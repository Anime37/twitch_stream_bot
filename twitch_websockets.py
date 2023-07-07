import websocket
from cli import CLI
from twitch_eventsub import TwitchEventSub
from twitch_irc import TwitchIRC


class TwitchWebSockets():
    instance = None

    started = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, channel, debug=False):
        if self.initialized:
            return
        self.cli = CLI()
        self.cli.print('initializing websockets')
        if debug:
            websocket.enableTrace(True)
        self.init_sockets(channel)

    def init_sockets(self, channel):
        self.irc = TwitchIRC(channel)
        self.eventsub = TwitchEventSub()

    def start_all(self):
        if self.started:
            self.cli.print('WebSockets already started')
            return
        self.irc.start()
        self.eventsub.start()
        self.started = True
