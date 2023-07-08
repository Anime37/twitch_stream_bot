from dataclasses import dataclass
import websocket
import re
from cli import *
import threading


@dataclass
class PRIVMSG():
    sender: str
    user: str
    host: str
    target: str
    content: str


class IRC():
    PRINT_TAG = 'IRC'

    cli = CLI()
    mutex = threading.Lock()

    def __init__(self, channel, url, debug=False):
        if debug:
            websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.channel = channel

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def print_rx(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] << {text}', TextColor.YELLOW)

    def print_tx(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] >> {text}', TextColor.GREEN)

    def parse_privmsg(self, message):
        pattern = r'^:(?P<sender>[^!]+)!(?P<user>[^@]+)@(?P<host>[^ ]+) PRIVMSG (?P<target>[^ ]+) :(?P<content>.*)$'
        match = re.match(pattern, message)

        if not match:
            return None

        return PRIVMSG(
            match.group('sender'),
            match.group('user'),
            match.group('host'),
            match.group('target'),
            match.group('content')
        )

    def handle_privmsg(self, priv_msg: PRIVMSG):
        for field in priv_msg.__dataclass_fields__:
            value = getattr(priv_msg, field)
            self.print(f'{field}: {value}')

    def send_privmsg(self, channel, msg):
        with self.mutex:
            self.print_tx(f'PRIVMSG #{channel} :{msg}')
            self.ws.send(f'PRIVMSG #{channel} :{msg}')

    def on_message(self, ws, message: str):
        if 'PRIVMSG' in message:
            self.handle_privmsg(self.parse_privmsg(message))
        else:
            self.print_rx(f"Received message: {message}")

    def on_error(self, ws, error):
        self.print_err(f"Error occurred: {error}")

    def on_close(self, ws, status_code, close_msg):
        self.print_err(f"WebSocket connection closed ({status_code}: {close_msg})")

    def on_open(self, ws):
        self.print("WebSocket connection opened")

    def run(self):
        self.ws.run_forever()
