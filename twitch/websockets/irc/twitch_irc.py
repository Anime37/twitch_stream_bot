import threading
import utils

from chat_ai import ChatAI
from fs import FS
from tts import TTS

from .irc import *
from .commands.command_list import CommandList

from ...actions_queue import TwitchActionsQueue
from ...api.bans import TwitchBans


class TwitchIRC(IRC, threading.Thread):
    instance = None

    COMM_TMO = 5
    last_receive_time = 0
    last_send_time = 0
    threat_format = "{}, if you don't stop spamming, I will {}"
    last_follow_thx_time = 0
    followbot_counter = 0

    CHAT_OUTPUT_PATH = f'{FS.USER_DATA_PATH}chat/chat.txt'

    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, channel: str, actions_queue: TwitchActionsQueue, bans: TwitchBans):
        if self.initialized:
            return
        IRC.__init__(self, channel, 'wss://irc-ws.chat.twitch.tv:443')
        threading.Thread.__init__(self)
        self.fs = FS()
        self.init_tts()
        self.ai = ChatAI(self.cli, self.fs)
        self.commands = CommandList()
        self.actions_queue = actions_queue
        self.bans = bans
        self.initialized = True

    def init_tts(self):
        self.tts = TTS(self.fs)
        self.tts.set_voices('Japanese')

    def send_random_threat(self, priv_msg: PRIVMSG):
        self.send_privmsg(
            self.channel,
            self.threat_format.format(
                priv_msg.sender,
                utils.get_random_line(f'{FS.MESSAGES_PATH}spam_threats.txt')
            )
        )

    def send_random_compliment(self, channel):
        self.send_privmsg(
            channel,
            utils.get_random_line(f'{FS.MESSAGES_PATH}compliments.txt')
        )

    def _is_followbotting(self):
        MIN_THX_PERIOD = (2)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_follow_thx_time + MIN_THX_PERIOD) - current_time
        is_followbotting = time_remaining > 0
        if is_followbotting:
            self.followbot_counter += 1
        else:
            self.last_follow_thx_time = current_time
            self.followbot_counter = 0
        return is_followbotting

    def _followbotting_response(self, user_name):
        FOLLOWBOT_DETECTION_COUNT = (5)
        if self.followbot_counter == FOLLOWBOT_DETECTION_COUNT:
            self.send_privmsg(
                self.channel,
                self.ai.generate_followbot_response(user_name)
            )

    def _handle_followbotting(self, user_name):
        if not self._is_followbotting():
            return False
        self._followbotting_response(user_name)
        return True

    def send_thx_for_follow(self, user_name):
        if self._handle_followbotting(user_name):
            return
        ai_response = self.ai.generate_follow_thx(user_name)
        self._send_and_update_tts(self.channel, ai_response)

    def send_thx_for_shoutout(self, user_login, user_name, viewer_count):
        ai_response = self.ai.generate_shoutout_thx(user_name, viewer_count)
        self._send_and_update_tts(user_login, ai_response)

    def _send_and_update_tts(self, user_login: str, message: str):
        self.send_privmsg(user_login, message)
        self._update_tts(message)

    def _save_chat_message(self, sender: str, msg: str):
        self.fs.write(self.CHAT_OUTPUT_PATH, f'[{utils.get_current_timestamp()}]\n{sender}:\n{msg}')

    def _update_tts(self, msg: str):
        self.tts.save_to_file(msg, 'chat.mp3')

    def update_chat(self, sender: str, msg: str):
        self._save_chat_message(sender, msg)
        self._update_tts(msg)

    def _handle_chat_message(self, priv_msg: PRIVMSG):
        if (priv_msg.sender == self.channel) and (priv_msg.content[0] != '.'):
            return
        ai_response = self.ai.get_response(priv_msg.sender, priv_msg.content)
        if priv_msg.user_id and ('!timeout!' in ai_response):
            self.bans.ban_user(priv_msg.user_id, priv_msg.sender)
        else:
            self.update_chat(priv_msg.sender, priv_msg.content)
        self.send_chat(ai_response)

    def _handle_chat_command(self, priv_msg: PRIVMSG):
        results = self.commands.execute(priv_msg.content[1:])
        if len(results) > 1:
            results = [f'@{priv_msg.sender}'] + results
        else:
            results[0] = f'@{priv_msg.sender}, {results[0]}'
        for result in results:
            self.send_chat(result)

    def _handle_chat_admin(self, priv_msg: PRIVMSG):
        if (priv_msg.sender != self.channel):
            return
        self.actions_queue.add(priv_msg.content[1:].strip())

    def _spam_handler(self, priv_msg: PRIVMSG) -> bool:
        current_time = utils.get_current_time()
        if (self.last_receive_time and ((self.last_receive_time + self.COMM_TMO) > current_time)):
            if ((self.last_send_time + self.COMM_TMO) < current_time):
                self.send_random_threat(priv_msg)
                self.last_send_time = current_time
            return True
        self.last_receive_time = current_time
        return False

    def handle_privmsg(self, priv_msg: PRIVMSG):
        self.print_rx(f'#{priv_msg.sender}: {priv_msg.content}')
        if self._spam_handler(priv_msg):
            return
        match(priv_msg.content[0]):
            case '!':
                self._handle_chat_command(priv_msg)
            case ',':
                self._handle_chat_admin(priv_msg)
            case _:
                self._handle_chat_message(priv_msg)

    def on_message(self, ws, message):
        if 'PRIVMSG' in message:
            self.handle_privmsg(self.parse_privmsg(message))
        elif 'JOIN' in message:
            channel = message.split('\n')[0].split('#')[1].strip()
            self.print_rx(f'joined {channel}')
            if channel == self.channel:
                self.send_privmsg(self.channel, 'connected')
        elif 'PING' in message:
            self.print_rx('PING')
            self.print_tx('PONG')
            self._send('PONG :tmi.twitch.tv')
        # elif 'ROOMSTATE' in message:
        #     self.print_rx(f'{message}')
        # else:
        #     self.print_rx(f'{message}')

    def authenticate(self):
        token = self.fs.read(FS.TWITCH_TOKEN_PATH)
        self._send('CAP REQ :twitch.tv/commands twitch.tv/tags')
        self._send(f'PASS oauth:{token}')
        self._send(f'NICK {self.channel}')

    def on_open(self, ws):
        super().on_open(ws)
        self.authenticate()
        self.join_channel(self.channel)

    def run(self):
        self.ws.run_forever(reconnect=3)

    def stop(self):
        self.ws.keep_running = False
        self.join()
