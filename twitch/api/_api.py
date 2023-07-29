from .eventsub import TwitchEventSub


class TwitchAPI(TwitchEventSub):
    def __init__(self):
        super().__init__()
