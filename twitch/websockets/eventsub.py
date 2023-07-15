from .irc import TwitchIRC

import json
import threading
import websocket
from cli import *
from events import EventWrapper


class TwitchEventSub(threading.Thread):
    PRINT_TAG = 'EVT'
    cli = CLI()
    mutex = threading.Lock()
    keepalive_counter = 0
    # KEEPALIVE_FREQUENCY = 10 + 5 # seconds (documented + safety)
    # NO_KEEPALIVE_FAIL_AMOUNT = 5 # how many to miss before reconnecting

    def __init__(self, debug=False):
        threading.Thread.__init__(self)
        if debug:
            websocket.enableTrace(True)
        self.irc = TwitchIRC()
        self.ws = websocket.WebSocketApp("wss://eventsub.wss.twitch.tv/ws",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_rx(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] << {text}', TextColor.MAGENTA)

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def session_welcome_handler(self, message: dict):
        self.session_id = message['payload']['session']['id']
        EventWrapper().set()

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
                started_at = event_payload['started_at']
                self.print_rx(f'a shoutout from {user_name} ({viewer_count=})!')
                self.irc.send_privmsg(
                    user_login,
                    f'THANKS FOR A SHOUTOUT AT {started_at}!\n'
                    f'{viewer_count} VIEWERS??? VERY NICE!!!\n'
                    'WHATS YOUR FAVORITE ANIME??? MINE IS NEO GENETICS EVENGALIST...'
                )
            case 'channel.shoutout.create':
                self.print_rx(f'created a shoutout')
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

    def start(self):
        super().start()
        EventWrapper().wait_and_clear()