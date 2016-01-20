import sys
import pjsua as pj
import _pjsua
import threading
from time import sleep


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
        call_cb = MyCallCallback(call, self.account)
        call.set_callback(call_cb)
        call.answer(200, "allet supa")


def make_call(uri, acc, doorin_id, to_disconnect_id, door_call):
    try:
        global lib
        # make a call
        print "Making call to", uri
        call = acc.make_call(uri)
        #call_cb = DoorConnectorCallCallback(call, doorin_id, to_disconnect_id, door_call)
        #call.set_callback(call_cb)
        return call
    except pj.Error, e:
        print "Error: " + str(e)
        return None


class MyCallCallback(pj.CallCallback):
    def __init__(self, call, account):
        pj.CallCallback.__init__(self, call)
        self.account = account
        self.pin = None
        self.roomCall = None

    def on_dtmf_digit(self, digits):
        print("DTMF:", digits)

    # Notification when call state has changed
    def on_state(self):
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            try:
                self.call.hangup()
            except pj.Error as e:
                print(e)
            print 'Current call is disconnected'

    # Notification when call's media state has changed.

    def on_media_state(self):
        def async(self):
            thread_desc = 0;
            err = _pjsua.thread_register("python worker", thread_desc)

            global lib
            if self.call.info().media_state == pj.MediaState.ACTIVE:
                # Connect the call to sound device
                call_slot = self.call.info().conf_slot
                print "Media is now active"
                player_id = lib.create_player("sounds/pausenmusik.wav", loop=True)
                lib.conf_connect(lib.player_get_slot(player_id), self.call.info().conf_slot)
                lib.conf_set_rx_level(lib.player_get_slot(player_id), .1)
                self.player_id = player_id
            else:
                print "Media is inactive"

        threading.Thread(target=async, args=(self,)).start()


lib = pj.Lib()

try:
    mcfg = pj.MediaConfig()
    mcfg.no_vad = True
    lib.init(log_cfg=pj.LogConfig(level=4, callback=log_cb), media_cfg=mcfg)
    lib.set_null_snd_dev()
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5080))
    lib.start()

    acc = lib.create_account(pj.AccountConfig("172.19.3.55", "620", "hallotel"))

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
        "(" + acc.info().reg_reason + ")"
    print "\nPress ENTER to quit"
    sys.stdin.readline()

    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
