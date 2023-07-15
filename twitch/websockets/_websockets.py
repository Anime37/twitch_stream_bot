from .eventsub import TwitchEventSub
from .irc import TwitchIRC

import websocket
from cli import *


class TwitchWebSockets():
    instance = None
    started = False

    PRINT_TAG = 'WSS'
    cli = CLI()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def __init__(self, channel, debug=False):
        if self.initialized:
            return
        self.print('initializing websockets')
        if debug:
            websocket.enableTrace(True)
        self.init_sockets(channel)

    def init_sockets(self, channel):
        self.irc = TwitchIRC(channel)
        self.eventsub = TwitchEventSub()

    def start_all(self):
        if self.started:
            self.print_err('WebSockets already started')
            return
        self.irc.start()
        self.eventsub.start()
        self.started = True
