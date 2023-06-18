import fs
import threading
import utils
from colors import TextColor
from irc import *
from time import time


class TwitchIRC(IRC, threading.Thread):
    COMM_TMO = 5
    last_receive_time = 0
    last_send_time = 0
    threat_format = "{}, if you don't stop spamming, I will {}"

    def __init__(self, channel):
        IRC.__init__(self, channel, 'wss://irc-ws.chat.twitch.tv:443')
        threading.Thread.__init__(self)

    def send_random_threat(self, priv_msg: PRIVMSG):
        self.send_privmsg(
            self.channel,
            self.threat_format.format(
                priv_msg.sender,
                utils.get_random_line('spam_threats.txt')
            )
        )

    def send_random_compliment(self, channel):
        self.send_privmsg(
            channel,
            utils.get_random_line('compliments.txt')
        )

    def update_chat(self, priv_msg: PRIVMSG):
        fs.write('chat.txt', f'{priv_msg.sender}:\n{priv_msg.content}')

    def handle_privmsg(self, priv_msg: PRIVMSG):
        self.cli.print(f'#{priv_msg.sender}: {priv_msg.content}', TextColor.YELLOW)
        current_time = int(time())
        if (self.last_receive_time and ((self.last_receive_time + self.COMM_TMO) > current_time)):
            if ((self.last_send_time + self.COMM_TMO) < current_time):
                self.send_random_threat(priv_msg)
                self.last_send_time = current_time
            return
        self.last_receive_time = current_time
        self.update_chat(priv_msg)

    def on_message(self, ws, message):
        if 'PRIVMSG' in message:
            self.handle_privmsg(self.parse_privmsg(message))
        elif 'PING' in message:
            self.cli.print('[IRC] Received PING, Sending PONG', TextColor.WHITE)
            self.ws.send('PONG :tmi.twitch.tv')
        elif f':{self.channel}.tmi.twitch.tv 353' in message:
            self.send_privmsg(self.channel, 'connected')

    def on_open(self, ws):
        super().on_open(ws)
        token = fs.read('user_data/token')
        ws.send('CAP REQ :twitch.tv/commands')
        ws.send(f'PASS oauth:{token}')
        ws.send(f'NICK {self.channel}')
        ws.send(f'JOIN #{self.channel}')

    def run(self):
        self.ws.run_forever()


def start(channel):
    global server
    server = TwitchIRC(channel)
    server.start()
    CLI().print('irc started')


def stop():
    global server
    server.ws.keep_running = False
    # print(server.name)
    # server.shutdown()
    server.join()
    CLI().print('irc stopped')


def send_random_compliment(channel):
    global server
    server.send_random_compliment(channel)
