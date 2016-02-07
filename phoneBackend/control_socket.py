import SimpleHTTPServer
import SocketServer
import threading
from distutils.command.config import config

import db
import threading
import pjsua as pj
import _pjsua


class ControlSocket(object):
    def __init__(self, account):
        self.account = account
        control_socket = self

        class ControlHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
            def do_POST(self):
                print self.path
                length = int(self.headers['Content-Length'])
                requ = self.rfile.read(length).decode('utf-8')
                if self.path == "/proxy":
                    parts = requ.split('&')
                    case = int(parts[0])
                    supporter_phone = int(parts[1])
                    target_uri = parts[2]
                    ProxyCoversation(case, supporter_phone, target_uri)

                self.send_response(200)

            def do_GET(self):
                self.send_response(200)

        class MyTCPSocketServer(SocketServer.TCPServer):
            allow_reuse_address = True

        self.server = MyTCPSocketServer(("127.0.0.1", 9000), ControlHandler)
        threading.Thread(target=self.server.serve_forever).start()

        class ProxyCoversation(object):

            def __init__(self, case, supporter_phone, target_uri):
                self.supporter_phone = db.SupporterPhone.get_by_id(supporter_phone)
                self.case = case
                self.target_uri = target_uri
                proxy_conversation = self

                class ProxyCCB(pj.CallCallback):
                    def __init__(self, call, queue_callback):
                        pj.CallCallback.__init__(self, call)
                        self.queue_callback = queue_callback

                    # Notification when call state has changed
                    def on_state(self):
                        print "Call with", self.call.info().remote_uri,
                        print "is", self.call.info().state_text,
                        print "last code =", self.call.info().last_code,
                        print "(" + self.call.info().last_reason + ")"

                        if self.call.info().state == pj.CallState.DISCONNECTED:
                            try:
                                if self.queue_callback.call.info().state == pj.CallState.CONFIRMED:
                                    self.queue_callback.call.hangup()
                            except pj.Error as e:
                                print(e)
                            except ReferenceError as e:
                                print(e)

                        if self.call.info().state == pj.CallState.CONFIRMED:
                            self.proceed()

                    # Notification when call's media state has changed.

                    def on_media_state(self):
                        if self.call.info().media_state == pj.MediaState.ACTIVE:
                            self.proceed()

                    def proceed(self):
                        if self.call.info().state == pj.CallState.CONFIRMED and self.call.info().media_state == pj.MediaState.ACTIVE:
                            #self.queue_callback.stop_music()
                            self.call.transfer_to_call(self.queue_callback.call)

                class SupporterCCB(pj.CallCallback):
                    def __init__(self, call):
                        pj.CallCallback.__init__(self, call)
                        self.proxy_call = None

                    # Notification when call state has changed
                    def on_state(self):
                        print "Call with", self.call.info().remote_uri,
                        print "is", self.call.info().state_text,
                        print "last code =", self.call.info().last_code,
                        print "(" + self.call.info().last_reason + ")"

                        if self.call.info().state == pj.CallState.DISCONNECTED:
                            try:
                                if self.proxy_call is not None:
                                    self.proxy_call.hangup()
                            except pj.Error as e:
                                print(e)
                            except ReferenceError as e:
                                print(e)

                        if self.call.info().state == pj.CallState.CONFIRMED:
                            self.proceed()

                    # Notification when call's media state has changed.

                    def on_media_state(self):
                        if self.call.info().media_state == pj.MediaState.ACTIVE:
                            self.proceed()

                    def proceed(self):
                        if self.call.info().state == pj.CallState.CONFIRMED and self.call.info().media_state == pj.MediaState.ACTIVE:
                            def async():
                                try:
                                    thread_desc = 0;
                                    err = _pjsua.thread_register("python call worker" + proxy_conversation.target_uri, thread_desc)
                                    # make a call
                                    print "Making call to", proxy_conversation.target_uri
                                    call = control_socket.account.make_call(str(proxy_conversation.target_uri))
                                    call_cb = ProxyCCB(call, self)
                                    call.set_callback(call_cb)
                                    self.proxy_call = call
                                except pj.Error, e:
                                    print "Error: " + str(e)

                            threading.Thread(target=async).start()

                def async():
                    try:
                        thread_desc = 0;
                        err = _pjsua.thread_register("python call worker" + self.supporter_phone.sip_uri, thread_desc)
                        # make a call
                        print "Making call to", self.supporter_phone.sip_uri
                        call = control_socket.account.make_call(self.supporter_phone.sip_uri)
                        call_cb = SupporterCCB(call)
                        call.set_callback(call_cb)
                    except pj.Error, e:
                        print "Error: " + str(e)

                threading.Thread(target=async).start()
