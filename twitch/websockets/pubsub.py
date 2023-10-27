import json
import threading
import websocket

from cli import TagCLI, TextColor
from fs.fs import FS


class TwitchPubSub(threading.Thread):
    instance = None

    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if self.initialized:
            return
        threading.Thread.__init__(self)
        self.cli = TagCLI('PSB')
        self.ws = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.initialized = True

    def print_rx(self, text: str):
        self.cli.print(f'<< {text}', TextColor.CYAN)

    def _send(self, msg: dict):
        try:
            self.ws.send(json.dumps(msg))
        except:
            self.cli.print_err('socket is closed!')

    def _response_handler(self, msg_json: dict):
        error = msg_json['error']
        if error:
            self.cli.print(f'authentication error: {error}')
        else:
            self.cli.print('authentication successful')

    def _whisper_handler(self, message: dict):
        message_data = json.loads(message['data'])
        body = message_data['body']
        display_name = message_data['tags']['display_name']
        self.print_rx(f'{display_name}: {body}')

    def _message_handler(self, msg_json: dict):
        message = json.loads(msg_json['data']['message'])
        match(message['type']):
            case 'whisper_received':
                self._whisper_handler(message)
            case _:
                self.cli.print(message)

    def on_message(self, ws, msg: str):
        msg_json = json.loads(msg)
        match(msg_json['type']):
            case 'RESPONSE':
                self._response_handler(msg_json)
            case 'MESSAGE':
                self._message_handler(msg_json)
            case _:
                self.cli.print(msg_json)

    def on_error(self, ws, error):
        self.cli.print_err(f"Error occurred: {error}")

    def on_close(self, ws, status_code, close_msg):
        self.cli.print_err(
            f"WebSocket connection closed ({status_code}: {close_msg})")

    def on_open(self, ws):
        self.cli.print("WebSocket connection opened")
        self.fs = FS()
        broadcaster_id = self.fs.read(f'{FS.USER_DATA_PATH}broadcaster_id')
        msg = {
            "type": "LISTEN",
            "nonce": "u23f4b834u8324fub39",
            "data": {
                "topics": [f'whispers.{broadcaster_id}'],
                "auth_token": f'{self.fs.read(FS.TWITCH_TOKEN_PATH)}'
            }
        }
        self._send(msg)

    def run(self):
        self.ws.run_forever(reconnect=3)
