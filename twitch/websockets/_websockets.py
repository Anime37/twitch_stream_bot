from .eventsub import TwitchEventSubWebSocket
from .irc import TwitchIRC

from ..actions_queue import TwitchActionsQueue


class TwitchWebSockets():
    instance = None
    started = False

    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, channel: str, actions_queue: TwitchActionsQueue, bans):
        if self.initialized:
            return
        self.irc = TwitchIRC(channel, actions_queue, bans)
        self.eventsub = TwitchEventSubWebSocket(self.irc)
        self.initialized = True

    def start_all(self):
        self.irc.start()
        self.eventsub.start()
        self.started = True
