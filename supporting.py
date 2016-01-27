import json
import telegram
import codecs


class Supporter(object):
    def __init__(self, name, telegram_id, sip_id):
        self.name = str(name)
        self.telegram_id = telegram_id
        self.sip_id = str(sip_id)


class SupportRequest(object):
    def __init__(self, callback, conversation, token):
        self.callback = callback
        self.conversation = conversation
        self.token = token


class SupporterManager(object):
    def __init__(self):
        supporters_dict = json.load(open('supporters', 'r'))
        self.supporters = [Supporter(**args) for args in supporters_dict]
        self.frontends = [telegram.TelegramFrontend(self.supporters, self.__callback)]

        self.requests = []

    def get_available_supporter(self, supporter_available_callback, conversation):
        self.requests.append(SupportRequest(supporter_available_callback, conversation, str(conversation.get_id())))
        for frontend in self.frontends:
            frontend.get_available_supporter(conversation)

    def __callback(self, token, supporter):
        for request in self.requests:
            if request.token == token:
                request.callback(supporter)
                self.requests.remove(request)
                return
        print("Got available supporter for not (anymore) existing request")