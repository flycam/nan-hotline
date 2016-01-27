import pjsua as pj
from time import sleep
import threading
import _pjsua


class Conversation(object):
    def __init__(self, queue_call, account, conversation_graph, lib, supporter_manager):
        conv = self

        class QueueCallback(pj.CallCallback):
            def __init__(self, call):
                pj.CallCallback.__init__(self, call)
                self.account = account
                self.pin = None
                self.roomCall = None
                self.speech_player_id = None
                self.music_player_id = None

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

            def avail_callback(self, supporter):
                print "AVAIL called by " + str(supporter)

        self.queue_call = queue_call
        self.path = []
        self.support_call = None
        self.account = account
        self.conversation_graph = conversation_graph
        self.current_node = conversation_graph.get_first_node(queue_call.info().remote_uri)
        self.lib = lib
        self.id = 42
        self.supporter_manager = supporter_manager
        queue_call.set_callback(QueueCallback(queue_call))
        queue_call.answer(200, "Call accepted by bot.")

    def get_id(self):
        return self.id