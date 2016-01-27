import pjsua as pj
from time import sleep
import threading
import _pjsua


class Conversation(object):
    def __init__(selfish, queue_call, account, conversation_graph, lib):
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
                following = selfish.conversation_graph.get_following_node(digits)
                if not selfish.current_node == following:
                    selfish.current_node = following
                    selfish.path.append(selfish.current_node)
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
                        if selfish.support_call is not None:
                            selfish.support_call.hangup()
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
                    selfish.lib.conf_disconnect(lib.player_get_slot(self.speech_player_id), self.call.info().conf_slot)
                    selfish.lib.player_destroy(self.speech_player_id)

                self.speech_player_id = selfish.lib.create_player(selfish.current_node.get_filename("de"))
                selfish.lib.conf_connect(lib.player_get_slot(self.speech_player_id), self.call.info().conf_slot)

                if selfish.current_node.id == -1:
                    print("Technischer Mitarbeiter")
                    # TODO: Support manager

                    sleep(5)
                    for i in range(100):
                        lib.conf_set_rx_level(lib.player_get_slot(self.music_player_id), 0.04 + i / 1000.0)
                        sleep(0.03)

        selfish.queue_call = queue_call
        selfish.path = []
        selfish.support_call = None
        selfish.account = account
        selfish.conversation_graph = conversation_graph
        selfish.current_node = conversation_graph.get_first_node(queue_call.info().remote_uri)
        selfish.lib = lib
        queue_call.set_callback(QueueCallback(queue_call))
        queue_call.answer(200, "Call accepted by bot.")
