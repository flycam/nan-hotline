import sys

import pjsua as pj
import _pjsua
import threading
from serverconfig import *
from telegram import TelegramComm
from config import *
from conversation import Conversation
from supporting import SupporterManager


def log_cb(level, str, len):
    print str,


class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_incoming_call(self, call):
        global graph
        global lib
        global supp_man
        Conversation(call, self.account, graph, lib, supp_man)


def make_call(callcallback, uri, acc, to_disconnect_id, door_call):
    try:
        thread_desc = 0;
        err = _pjsua.thread_register("python call worker" + uri, thread_desc)
        global lib
        # make a call
        print "Making call to", uri
        call = acc.make_call(uri)
        call_cb = DoorConnectorCallCallback(call, to_disconnect_id, door_call)
        call.set_callback(call_cb)
        callcallback.makecallCall = call
    except pj.Error, e:
        print "Error: " + str(e)
        return None


class DoorConnectorCallCallback(pj.CallCallback):
    def __init__(self, call, to_disconnect_id, door_call):
        pj.CallCallback.__init__(self, call)
        # self.doorin_id = doorin_id
        self.to_disconnect_id = to_disconnect_id
        self.door_call = door_call

    # Notification when call state has changed
    def on_state(self):
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            try:
                if self.door_call.info().state == pj.CallState.CONFIRMED:
                    self.door_call.hangup()
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
            # lib.conf_disconnect(lib.player_get_slot(self.to_disconnect_id), self.doorin_id)
            self.call.transfer_to_call(self.door_call)


lib = pj.Lib()

graph = CommunicationGraph("config")
supp_man = SupporterManager()
try:
    mcfg = pj.MediaConfig()
    mcfg.no_vad = True
    lib.init(log_cfg=pj.LogConfig(level=4, callback=log_cb), media_cfg=mcfg)
    lib.set_null_snd_dev()
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5080))
    lib.start()

    acc = lib.create_account(pj.AccountConfig(sip_registrar, sip_account, sip_pw))

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
        "(" + acc.info().reg_reason + ")"
    print "\nPress ENTER to quit"
    sys.stdin.readline()

    lib.destroy()
    #tcomm.close()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
