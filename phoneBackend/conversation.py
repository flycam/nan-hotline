import pjsua as pj
from time import sleep
import threading
import _pjsua
import random
import db


class Conversation(object):
    def __init__(self, queue_call, account, conversation_graph, lib, supporter_manager):
        conv = self

        class SupporterCallback(pj.CallCallback):
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
                    self.queue_callback.stop_music()
                    self.call.transfer_to_call(self.queue_callback.call)

        class QueueCallback(pj.CallCallback):
            def __init__(self, call):
                pj.CallCallback.__init__(self, call)
                self.account = account
                self.pin = None
                self.roomCall = None
                self.speech_player_id = None
                self.music_player_id = None
                call.remote_uri = call.info().remote_uri

            def on_dtmf_digit(self, digits):
                print("DTMF:", digits)
                following = conv.current_node.get_following_node(digits)
                if not conv.current_node == following:
                    conv.current_node = following
                    conv.path.append(conv.current_node)
                    self.play_node()

            # Notification when call state has changed
            def on_state(self):
                print "Call with", self.call.info().remote_uri,
                print "is", self.call.info().state_text,
                print "last code =", self.call.info().last_code,
                print "(" + self.call.info().last_reason + ")"

                if self.call.info().state == pj.CallState.DISCONNECTED:
                    conv.supporter_manager.cancel_request(conv)
                    try:
                        self.call.hangup()
                    except pj.Error as e:
                        print(e)
                    print 'Current call is disconnected'
                    try:
                        if conv.support_call is not None:
                            conv.support_call.hangup()
                    except pj.Error as e:
                        print(e)

            def on_media_state(self):
                def async():
                    thread_desc = 0;
                    err = _pjsua.thread_register("python worker", thread_desc)

                    if self.call.info().media_state == pj.MediaState.ACTIVE:
                        # Connect the call to sound device
                        call_slot = self.call.info().conf_slot
                        print "Media is now active"
                        self.music_player_id = lib.create_player("sounds/pausenmusik.wav", loop=True)
                        lib.conf_connect(lib.player_get_slot(self.music_player_id), call_slot)
                        lib.conf_set_rx_level(lib.player_get_slot(self.music_player_id), 0.04)

                        self.play_node()

                    else:
                        print "Media is inactive"

                threading.Thread(target=async).start()

            def play_node(self):
                def async():
                    thread_desc = 0;
                    err = _pjsua.thread_register("python worker callback node "+ str(conv.current_node.id) + str(conv.get_id()), thread_desc)
                    if self.speech_player_id is not None:
                        conv.lib.conf_disconnect(lib.player_get_slot(self.speech_player_id), self.call.info().conf_slot)
                        conv.lib.player_destroy(self.speech_player_id)

                    self.speech_player_id = conv.lib.create_player(conv.current_node.get_filename("de"))
                    conv.lib.conf_connect(lib.player_get_slot(self.speech_player_id), self.call.info().conf_slot)

                    if conv.current_node.id == -1:
                        print("Technischer Mitarbeiter")
                        conv.supporter_manager.get_available_supporter(self.avail_callback, conv)

                        sleep(5)
                        for i in range(100):
                            lib.conf_set_rx_level(lib.player_get_slot(self.music_player_id), 0.04 + i / 1000.0)
                            sleep(0.03)
                    elif conv.current_node.id == -2:
                        print("Kein technischer Mitarbeiter")
                        sleep(8)
                        self.call.hangup()
                threading.Thread(target=async).start()

            def stop_music(self):
                lib.conf_disconnect(lib.player_get_slot(self.music_player_id), self.call.info().conf_slot)
                lib.player_destroy(self.music_player_id)

            def avail_callback(self, supporter_phone):
                if not self.call.is_valid():
                    print("AVAIL for call that is not valid anymore")
                    return

                def async():
                    thread_desc = 0;
                    err = _pjsua.thread_register("python worker callback timeout "+ str(conv.get_id()), thread_desc)
                    print "AVAIL called by supporter phone {}".format(supporter_phone)
                    db.create_conversation(supporter_phone, self.call.info().remote_uri, "->".join([n.description for n in conv.path]))
                    if supporter_phone is not None:
                        self.make_call(supporter_phone.sip_uri)
                    else:
                        conv.current_node = conv.conversation_graph.getNodeById(-2)
                        conv.path.append(conv.current_node)
                        self.play_node()

                threading.Thread(target=async).start()

            def make_call(self, uri):
                def async():
                    try:
                        thread_desc = 0;
                        err = _pjsua.thread_register("python call worker" + uri, thread_desc)
                        # make a call
                        print "Making call to", uri
                        call = conv.account.make_call(uri)
                        call_cb = SupporterCallback(call, self)
                        call.set_callback(call_cb)
                        conv.support_call = call
                    except pj.Error, e:
                        print "Error: " + str(e)
                threading.Thread(target=async).start()

        self.queue_call = queue_call
        self.path = []
        self.support_call = None
        self.account = account
        self.conversation_graph = conversation_graph
        self.current_node = conversation_graph.get_first_node(queue_call.info().remote_uri)
        self.lib = lib
        self.id = random.randint(0, 500000)
        self.supporter_manager = supporter_manager
        queue_call.set_callback(QueueCallback(queue_call))
        queue_call.answer(200, "Call accepted by bot.")

    def get_id(self):
        return self.id
