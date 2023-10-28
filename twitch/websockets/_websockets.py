from .eventsub import TwitchEventSubWebSocket
from .irc import TwitchIRC
from .pubsub import TwitchPubSub

from ..actions_queue import TwitchActionsQueue
from ..api.oauth import TwitchOAuth


class TwitchWebSockets():
    instance = None
    started = False

    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, oauth: TwitchOAuth, actions_queue: TwitchActionsQueue, bans):
        if self.initialized:
            return
        self.irc = TwitchIRC(oauth.account.USER_NAME, actions_queue, bans)
        self.eventsub = TwitchEventSubWebSocket(self.irc)
        self.pubsub = TwitchPubSub(actions_queue)
        self.initialized = True

    def start_all(self):
        self.irc.start()
        self.eventsub.start()
        self.pubsub.start()
        self.started = True
