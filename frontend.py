class Frontend(object):
    def __init__(self, supporters, supporter_available_callback):
        self.supporters = supporters
        self.supporter_available_callback = supporter_available_callback

    def get_available_supporter(self, conversation):
        pass