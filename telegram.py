import requests
import SimpleHTTPServer
import SocketServer
import socket
import threading
import json
import urllib


class TelegramComm():
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
                    return
                if self.talkCallback is not None and self.talkCallback(message['from']['id'], message['text']):
                    self.talkCallback = None

            def do_GET(s):
                s.send_response(200)
        self.talkCallback = None
        self.api_url = self.TELEGRAM_API_URL.format(botToken)
        self.userList = userList
        self.server = SocketServer.TCPServer(("0.0.0.0", localPort), TelegramWebhookHandler)
        self.server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        self.server.server_close()
