import sys

import pjsua as pj
import _pjsua
import threading
from serverconfig import *
from telegram import TelegramComm
from config import *
from conversation import Conversation
from supporting import SupporterManager
import control_socket


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
    control_socket.ControlSocket(acc)
    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
        "(" + acc.info().reg_reason + ")"
    print "\nPress ENTER to quit"
    sys.stdin.readline()

    lib.destroy()
    supp_man.close()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
