from .eventsub import TwitchEventSub

from twitch_websockets import TwitchWebSockets


class Twitch(TwitchEventSub):
    def __init__(self):
        super().__init__()

    def start_websockets(self):
        self.websockets = TwitchWebSockets(self.account.USER_NAME)
        self.websockets.start_all()
