import telegram
import threading
import db


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
        self.frontends = [
            telegram.TelegramFrontend(self.__supporter_accepted_cb, self.__supporter_declined_cb)]

        self.requests = []

    def get_available_supporter(self, supporter_available_callback, conversation):
        request = SupportRequest(supporter_available_callback, conversation, str(conversation.get_id()),
                                 db.Supporter.get_all())
        self.requests.append(request)
        for frontend in self.frontends:
            frontend.get_available_supporter(conversation)

        def timeout():
            self.__supporter_accepted_cb(request.token, None)

        threading.Timer(5 * 60, timeout).start()

    def cancel_request(self, conversation):
        for request in self.requests[:]:
            if request.conversation == conversation:
                self.requests.remove(request)
                for frontend in self.frontends:
                    frontend.request_canceled(request)

    def __supporter_accepted_cb(self, token, supporter_phone):
        for request in self.requests:
            if request.token == token:
                self.requests.remove(request)
                request.callback(supporter_phone)
                for frontend in self.frontends:
                    frontend.call_delegated_to(supporter_phone, request.conversation)
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
