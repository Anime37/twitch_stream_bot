from .irc import *

import fs
import threading
import utils
from tts import TTS


class TwitchIRC(IRC, threading.Thread):
    instance = None

    MESSAGES_PATH = 'user_data/config/messages/'
    COMM_TMO = 5
    last_receive_time = 0
    last_send_time = 0
    threat_format = "{}, if you don't stop spamming, I will {}"

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, channel='', debug=False):
        if self.initialized:
            return
        IRC.__init__(self, channel, 'wss://irc-ws.chat.twitch.tv:443', debug)
        threading.Thread.__init__(self)
        self.init_tts()
        self.initialized = True

    def init_tts(self):
        self.tts = TTS()
        self.tts.set_voices('Japanese')

    def send_random_threat(self, priv_msg: PRIVMSG):
        self.send_privmsg(
            self.channel,
            self.threat_format.format(
                priv_msg.sender,
                utils.get_random_line(f'{self.MESSAGES_PATH}spam_threats.txt')
            )
        )

    def send_random_compliment(self, channel):
        self.send_privmsg(
            channel,
            utils.get_random_line(f'{self.MESSAGES_PATH}compliments.txt')
        )

    def send_thx_for_follow(self, user_name):
        self.send_privmsg(
            self.channel,
            self.tts.ai.generate_follow_thx(user_name)
        )

    def send_thx_for_shoutout(self, channel):
        self.send_privmsg(
            channel,
            self.tts.ai.generate_shoutout_thx(channel)
        )

    def _save_chat_message(self, sender: str, msg: str):
        OUTPUT_PATH = 'user_data/chat/chat.txt'
        fs.write(OUTPUT_PATH, f'{sender}:\n{msg}')

    def update_chat(self, sender: str, msg: str):
        self._save_chat_message(sender, msg)
        self.tts.save_to_file(msg, 'chat.mp3')

    def handle_privmsg(self, priv_msg: PRIVMSG):
        self.print_rx(f'#{priv_msg.sender}: {priv_msg.content}')
        if (priv_msg.sender == self.channel) and priv_msg.content[0] != '!':
            return
        current_time = utils.get_current_time()
        if (self.last_receive_time and ((self.last_receive_time + self.COMM_TMO) > current_time)):
            if ((self.last_send_time + self.COMM_TMO) < current_time):
                self.send_random_threat(priv_msg)
                self.last_send_time = current_time
            return
        self.last_receive_time = current_time
        self.update_chat(priv_msg.sender, priv_msg.content)
        ai_response = self.tts.ai.get_response(priv_msg.sender, priv_msg.content)
        self.send_chat(ai_response)

    def on_message(self, ws, message):
        if 'PRIVMSG' in message:
            self.handle_privmsg(self.parse_privmsg(message))
        elif 'JOIN' in message:
            channel = message.split('\n')[0].split('#')[1].strip()
            self.print_rx(f'joined {channel}')
            if channel == self.channel:
                self.send_privmsg(self.channel, 'connected')
            elif self.JOIN_CHANNELS:
                self.join_event.set()
        elif 'PING' in message:
            self.print_rx('PING')
            self.print_tx('PONG')
            self._send('PONG :tmi.twitch.tv')
        # elif 'ROOMSTATE' in message:
        #     self.print_rx(f'{message}')
        # else:
        #     self.print_rx(f'{message}')

    def authenticate(self):
        token = fs.read('user_data/token_bot')
        self._send('CAP REQ :twitch.tv/commands')
        self._send(f'PASS oauth:{token}')
        self._send(f'NICK {self.channel}')

    def on_open(self, ws):
        super().on_open(ws)
        self.authenticate()
        self.join_channel(self.channel)

    def run(self):
        self.ws.run_forever(reconnect=3)

    def shutdown(self):
        self.ws.keep_running = False
        self.join()
