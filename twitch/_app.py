from .api import TwitchAPI
from .websockets import TwitchWebSockets


class TwitchAPP(TwitchAPI):
    def __init__(self):
        super().__init__()

    def start_websockets(self):
        self.websockets = TwitchWebSockets(self.account.USER_NAME)
        self.websockets.start_all()
