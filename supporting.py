import json
import telegram
import threading


class Supporter(object):
    def __init__(self, name, telegram_id, sip_id):
        self.name = str(name)
        self.telegram_id = telegram_id
        self.sip_id = str(sip_id)


class SupportRequest(object):
    def __init__(self, callback, conversation, token, supporters):
        self.callback = callback
        self.conversation = conversation
        self.token = token
        self.supporter_declined = {}
        for supporter in supporters:
            self.supporter_declined[supporter] = False


class SupporterManager(object):
    def __init__(self):
        supporters_dict = json.load(open('supporters', 'r'))
        self.supporters = [Supporter(**args) for args in supporters_dict]
        self.frontends = [
            telegram.TelegramFrontend(self.supporters, self.__supporter_accepted_cb, self.__supporter_declined_cb)]

        self.requests = []

    def get_available_supporter(self, supporter_available_callback, conversation):
        request = SupportRequest(supporter_available_callback, conversation, str(conversation.get_id()),
                                 self.supporters)
        self.requests.append(request)
        for frontend in self.frontends:
            frontend.get_available_supporter(conversation)

        def timeout():
            self.__supporter_accepted_cb(request.token, None)

        threading.Timer(5 * 60, timeout).start()

    def __supporter_accepted_cb(self, token, supporter):
        for request in self.requests:
            if request.token == token:
                self.requests.remove(request)
                request.callback(supporter)
                for frontend in self.frontends:
                    frontend.call_delegated_to(supporter, request.conversation)
                return
        print("Got available supporter for not (anymore) existing request")

    def __supporter_declined_cb(self, token, supporter):
        for request in self.requests:
            if request.token == token:
                request.supporter_declined[supporter] = True

                if all(request.supporter_declined.values()):
                    self.__supporter_accepted_cb(token, None)

    def close(self):
        for frontend in self.frontends:
            frontend.close()
