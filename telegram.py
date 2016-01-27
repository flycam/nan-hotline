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
                    print message['from']['id'] + " not in userlist. "
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

    def close(self):
        self.server.shutdown()


class TelegramFrontend(Frontend):
    def __init__(self, supporters, supporter_available_callback):
        super(TelegramFrontend, self).__init__(supporters, supporter_available_callback)
        user_list = [s.telegram_id for s in supporters]
        self.telegram = TelegramComm("https://nan.uni-karlsruhe.de/janis", 8080, serverconfig.telegram_token,
                                     user_list)

    def get_available_supporter(self, conversation):
        self.telegram.sendBroadcast(
            "Incomming support request by " + conversation.call.info().remote_uri + "\nPath: " + "->".join(
                conversation.path),
            {'keyboard': [["Accept call [" + conversation.get_id() + "]"],
                          ['Decline call [' + conversation.get_id()] + "]"], "resize_keyboard": True,
             "one_time_keyboard": True}, self.__broadcast_callback)

    def __broadcast_callback(self, from_telegram_user, text):
        if "Accept call " in text:
            selected_supporter = None
            for supporter in self.supporters:
                if supporter.telegram_id == from_telegram_user:
                    selected_supporter = supporter
            if selected_supporter is None:
                print("Got reply from unknown supporter telegram_id={}".format(from_telegram_user))
                return

            rex = re.compile(r'Accept call \[([^\]])*\]')
            m = rex.match(text)
            if m is None:
                print("Supporter reply has invalid format")
                return
            token = m.groups()[0]

            self.supporter_available_callback(token, selected_supporter)