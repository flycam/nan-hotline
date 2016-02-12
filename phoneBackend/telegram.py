import requests
import SimpleHTTPServer
import SocketServer
import socket
import threading
import json
import urllib
from frontend import Frontend
import serverconfig
import re
import db


class TelegramComm(object):
    TELEGRAM_API_URL = "https://api.telegram.org/bot{}/"

    def __init__(self, url, localPort, botToken):
        class TelegramWebhookHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

            def do_POST(s):
                length = int(s.headers['Content-Length'])
                requ = s.rfile.read(length).decode('utf-8')
                print requ
                requ = json.loads(requ)
                s.send_response(200)
                message = requ['message']
                userList = self.get_user_list()
                if message['text'] == "/botsnack":
                    self.sendRequest("sendMessage",
                                     {'chat_id': message['chat']['id'], 'text': '*knirps* *knirps* Yummy! Thank you!'})
                    return
                if not message['from']['id'] in userList:
                    self.sendRequest("sendMessage", {"chat_id": message['chat']['id'],
                                                     "text": "My mom told me not to talk to strangers."})
                    print str(message['from']['id']) + " not in userlist. "
                    return
                user = userList[message['from']['id']]
                if message['text'].startswith("/call"):
                    reg = re.compile(r'^/call[ _]([0-9]+)(:?[ _]([0-9]+))?$')
                    match = reg.match(message['text'])
                    if match is None:
                        self.sendRequest("sendMessage", {"chat_id": message['chat']['id'],
                                                         "text": "Ehmm.. What?"})
                        return
                    else:
                        phone_number = match.group(1)
                        phone_id = match.group(2)
                        if phone_id is None:
                            self.sendRequest("sendMessage", {"chat_id": message['chat']['id'],
                                                             "text": "Select your phone id: \n" + "\n".join(
                                                                 ["/call_{}_{}".format(phone_number, p.id) for p in
                                                                  user.phones])})
                        else:
                            # TODO: implement
                            self.sendRequest("sendMessage", {"chat_id": message['chat']['id'],
                                                             "text": "Ok, let's go.. So, ehm. Could you come again a bit later? I'm quite busy here at the moment... And I don't want to serve your request anyway."})
                    return

                if self.talkCallback is not None and self.talkCallback(message['from']['id'], message['text']):
                    self.talkCallback = None

            def do_GET(s):
                s.send_response(200)

        self.talkCallback = None
        self.api_url = self.TELEGRAM_API_URL.format(botToken)

        class MyTCPSocketServer(SocketServer.TCPServer):
            allow_reuse_address = True

        self.server = MyTCPSocketServer(("0.0.0.0", localPort), TelegramWebhookHandler)
        threading.Thread(target=self.server.serve_forever).start()
        if not requests.post(self.api_url + "setWebhook", data={"url": url}).json()['ok']:
            raise RuntimeError("Couldn't set webHook!")

    def sendRequest(self, command, data):
        res = requests.post(self.api_url + command, json=data).json()
        print self.api_url + command + " data: " + str(data)
        if not res['ok']:
            raise RuntimeError("Couldn't execute command! (" + res["description"] + ")")

    def sendBroadcast(self, message, keyboardMarkup=None, callback=None):
        if keyboardMarkup is None:
            keyboardMarkup = {"hide_keyboard": True}
        if callback is not None:
            self.talkCallback = callback
        for user in self.get_user_list():
            self.sendRequest("sendMessage",
                             {'chat_id': str(user), 'text': message, 'reply_markup': keyboardMarkup})

    def sendRequestWithKeyboard(self, user, message, keyboardMarkup=None, callback=None):
        if keyboardMarkup is None:
            keyboardMarkup = {"hide_keyboard": True}
        if callback is not None:
            self.talkCallback = callback
        self.sendRequest("sendMessage",
                         {'chat_id': str(user), 'text': message, 'reply_markup': keyboardMarkup})

    def close(self):
        self.server.shutdown()

    def get_user_list(self):
        supporters = db.Supporter.get_all()
        user_list = {}
        for s in supporters:
            user_list[s.telegram_id] = s
        return user_list


class TelegramFrontend(Frontend):
    def __init__(self, supporter_available_callback, supporter_declined_cb):
        super(TelegramFrontend, self).__init__(supporter_available_callback, supporter_declined_cb)
        self.telegram = TelegramComm("https://nan.uni-karlsruhe.de/janis", 8080, serverconfig.telegram_token)

    def get_available_supporter(self, conversation):
        for supporter in db.Supporter.get_all():
            accept_commands = ["/accept_{}_{} <{}>".format(conversation.get_id(), p.id, p.sip_uri) for p in
                               supporter.phones]

            message_text = "Incomming support request by " + conversation.queue_call.info().remote_uri + "\nPath: " + "->".join(
                [p.description for p in conversation.path]) + "\n" + '\n'.join(accept_commands) + "\n/decline_" + str(
                conversation.get_id())

            keyboard = [accept_commands, ['/decline_' + str(conversation.get_id()) + ""]]

            self.telegram.sendRequestWithKeyboard(supporter.telegram_id,
                                                  message_text,
                                                  {'keyboard': keyboard, "resize_keyboard": True,
                                                   "one_time_keyboard": True},
                                                  self.__broadcast_callback)

    def call_delegated_to(self, supporter_phone, conversation):
        if supporter_phone is None:
            self.telegram.sendBroadcast("Call to {} declined.".format(conversation.queue_call.remote_uri))
            return
        self.telegram.sendBroadcast("Call {} delegated to {} (phone {})".format(conversation.queue_call.remote_uri,
                                                                                supporter_phone.supporter.name,
                                                                                supporter_phone.sip_uri))

    def request_canceled(self, request):
        self.telegram.sendBroadcast("Call request {} canceled".format(request.conversation.queue_call.remote_uri))

    def __broadcast_callback(self, from_telegram_user, text):
        selected_supporter = None
        for supporter in db.Supporter.get_all():
            if supporter.telegram_id == from_telegram_user:
                selected_supporter = supporter
        if selected_supporter is None:
            print("Got reply from unknown supporter telegram_id={}".format(from_telegram_user))
            return

        if "/accept" in text:
            rex = re.compile(r'/accept_([0-9]*)_([0-9]*)')
            m = rex.match(text)
            if m is None:
                print("Supporter reply has invalid format (accept)")
                return
            token = m.groups()[0]
            supporterPhoneId = m.groups()[1]

            selectedPhone = None
            for phone in selected_supporter.phones:
                try:
                    phoneIdInt = int(supporterPhoneId)
                except ValueError:
                    print("Got invalid phone id {}".format(supporterPhoneId))
                    return
                if phone.id == phoneIdInt:
                    selectedPhone = phone
            if selectedPhone is None:
                print("Got reply for unknown phone id {}".format(supporterPhoneId))
                return

            self.supporter_available_callback(token, selectedPhone)
        elif "/decline" in text:
            rex = re.compile(r'/decline_(.*)')
            m = rex.match(text)
            if m is None:
                print("Supporter reply has invalid format (decline)")
                return
            token = m.groups()[0]

            self.supporter_declined_callback(token, selected_supporter)

    def close(self):
        self.telegram.close()
