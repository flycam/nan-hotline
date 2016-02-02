class Frontend(object):
    def __init__(self, supporters, supporter_available_callback, supporter_declined_callback):
        self.supporters = supporters
        self.supporter_available_callback = supporter_available_callback
        self.supporter_declined_callback = supporter_declined_callback

    def get_available_supporter(self, conversation):
        pass

    def call_delegated_to(self, supporter_phone, conversation):
        pass

    def request_canceled(self, request):
        pass

    def close(self):
        pass