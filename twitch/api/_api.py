from .eventsub import TwitchEventSub
from ..websockets import TwitchWebSockets


class TwitchAPI(TwitchEventSub):
    def __init__(self):
        super().__init__()

    def start_websockets(self):
        self.websockets = TwitchWebSockets(self.account.USER_NAME)
        self.websockets.start_all()
