from .irc import TwitchIRC

import json
import threading
import websocket
from cli import *
from event_handler import EventHandler


class TwitchEventSubWebSocket(threading.Thread):
    instance = None

    PRINT_TAG = 'EVT'
    cli = CLI()
    mutex = threading.Lock()
    keepalive_counter = 0
    # KEEPALIVE_FREQUENCY = 10 + 5 # seconds (documented + safety)
    # NO_KEEPALIVE_FAIL_AMOUNT = 5 # how many to miss before reconnecting
    WELCOME_EVENT_NAME = 'evtsub_welcome'

    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, irc: TwitchIRC):
        threading.Thread.__init__(self)
        if self.initialized:
            return
        self.irc = irc
        self.event_handler = EventHandler()
        self.welcome_event = self.event_handler.create_event(self.WELCOME_EVENT_NAME)
        self.ws = websocket.WebSocketApp("wss://eventsub.wss.twitch.tv/ws",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.initialized = True

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_rx(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] << {text}', TextColor.MAGENTA)

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def session_welcome_handler(self, message: dict):
        self.session_id = message['payload']['session']['id']
        self.welcome_event.set()

    def notification_handler(self, message: dict):
        event_type = message['payload']['subscription']['type']
        event_payload = message['payload']['event']
        match(event_type):
            case 'channel.follow':
                user_name = event_payload['user_name']
                self.print_rx(f'a follow from {user_name}!')
                self.irc.send_thx_for_follow(user_name)
            case 'channel.shoutout.receive':
                user_name = event_payload['from_broadcaster_user_name']
                user_login = event_payload['from_broadcaster_user_login']
                viewer_count = event_payload['viewer_count']
                self.print_rx(f'a shoutout from {user_name} ({viewer_count=})!')
                self.irc.send_thx_for_shoutout(user_login, user_name, viewer_count)
                self.irc.send_thx_for_shoutout(self.irc.channel, user_name, viewer_count)
            case 'channel.shoutout.create':
                self.print_rx('created a shoutout')
            case 'channel.update':
                self.print_rx('updated channel properties')
            case _:
                self.print_rx(f'{message}')

    def on_message(self, ws, message: str):
        json_message = json.loads(message)
        message_type = json_message['metadata']['message_type']
        match(message_type):
            case 'session_keepalive':
                # self.keepalive_counter += 1
                # if (self.keepalive_counter % 30) == 0:
                #     self.print(f'EventSub is still alive')
                pass
            case 'notification':
                self.notification_handler(json_message)
            case 'session_welcome':
                self.session_welcome_handler(json_message)
            case _:
                self.print_err(json_message)

    def on_error(self, ws, error):
        self.print_err(f"Error occurred: {error}")

    def on_close(self, ws, status_code, close_msg):
        self.print_err(f"WebSocket connection closed ({status_code}: {close_msg})")

    def on_open(self, ws):
        self.print("WebSocket connection opened")

    def run(self):
        self.ws.run_forever(reconnect=3)

    def _wait_for_welcome(self):
        self.welcome_event.wait()

    def start(self):
        super().start()
        self._wait_for_welcome()
