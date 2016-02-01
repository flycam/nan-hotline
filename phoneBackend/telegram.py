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


class TelegramComm(object):
    TELEGRAM_API_URL = "https://api.telegram.org/bot{}/"

    def __init__(self, url, localPort, botToken, userList):
        class TelegramWebhookHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

            def do_POST(s):
                length = int(s.headers['Content-Length'])
                requ = s.rfile.read(length).decode('utf-8')
                print requ
                requ = json.loads(requ)
                s.send_response(200)
                message = requ['message']
                if message['text'] == "/botsnack":
                    self.sendRequest("sendMessage",
                                     {'chat_id': message['chat']['id'], 'text': '*knirps* *knirps* Yummy! Thank you!'})
                    return
                if not message['from']['id'] in userList:
                    self.sendRequest("sendMessage", {"chat_id": message['chat']['id'],
                                                     "text": "My mom told me not to talk to strangers."})
                    print str(message['from']['id']) + " not in userlist. "
                    return
                if self.talkCallback is not None and self.talkCallback(message['from']['id'], message['text']):
                    self.talkCallback = None

            def do_GET(s):
                s.send_response(200)

        self.talkCallback = None
        self.api_url = self.TELEGRAM_API_URL.format(botToken)
        self.userList = userList

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
        for user in self.userList:
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


class TelegramFrontend(Frontend):
    def __init__(self, supporters, supporter_available_callback, supporter_declined_cb):
        super(TelegramFrontend, self).__init__(supporters, supporter_available_callback, supporter_declined_cb)
        user_list = [s.telegram_id for s in supporters]
        self.telegram = TelegramComm("https://nan.uni-karlsruhe.de/janis", 8080, serverconfig.telegram_token,
                                     user_list)

    def get_available_supporter(self, conversation):
        for supporter in self.supporters:
            accept_commands = ["/accept_{}_{} <{}>".format(conversation.get_id(), p.id, p.sip_uri) for p in supporter.phones]

            message_text = "Incomming support request by " + conversation.queue_call.info().remote_uri + "\nPath: " + "->".join(
                [p.description for p in conversation.path]) + "\n" + '\n'.join(accept_commands) + "\n/decline_" + str(conversation.get_id())

            keyboard = [accept_commands, ['/decline_' + str(conversation.get_id()) + ""]]

            self.telegram.sendRequestWithKeyboard(supporter.telegram_id,
                                                  message_text,
                                                  {'keyboard': keyboard, "resize_keyboard": True, "one_time_keyboard": True},
                                                  self.__broadcast_callback)

    def call_delegated_to(self, supporter_phone, conversation):
        if supporter_phone is None:
            self.telegram.sendBroadcast("Call to {} declined.".format(conversation.queue_call.remote_uri))
            return
        self.telegram.sendBroadcast("Call {} delegated to {} (phone {})".format(conversation.queue_call.remote_uri, supporter_phone.supporter.name, supporter_phone.sip_uri))

    def __broadcast_callback(self, from_telegram_user, text):
        selected_supporter = None
        for supporter in self.supporters:
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