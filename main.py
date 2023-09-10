from dataclasses import dataclass
import os
import threading

from cli import CLI
from gif_manager import GifManager
from tts import TTSServerThread
from twitch import TwitchAPP
from twitch.websockets.irc.priv_msg import PRIVMSG


cli = CLI()
PRINT_TAG = 'APP'


def print(text: str):
    cli.print(f'[{PRINT_TAG}] {text}')


def input(text: str):
    return cli.input(f'[{PRINT_TAG}] {text}')


def toggle_on_all_gifs():
    result = GifManager().toggle_all_gifs(True)
    print(result)


def _start_twitch_threads(twitch: TwitchAPP):
    if not twitch.setup():
        return
    twitch_api_thread = threading.Thread(target=twitch.api_loop)
    twitch_api_thread.start()


def start_threads(twitch: TwitchAPP):
    TTSServerThread().start()
    _start_twitch_threads(twitch)


class TwitchChat():
    def __init__(self, app: TwitchAPP):
        self.app = app
        self.irc = app.websockets.irc

    def _fake_privmsg(self, content: str):
        priv_msg = PRIVMSG(self.app.USER_NAME, '', '', '', content)
        self.irc.handle_privmsg(priv_msg)

    def _add_action_to_queue(self, action: str):
        match(action):
            case 'eventsub_test':
                self.app.actions_queue.put(self.app.eventsub.subscribe_to_channel_update_events)
                self.app.actions_queue.put(self.app.eventsub.delete_channel_update_events)

    def _handle_input(self, text: str):
        if not text:
            return
        self.irc.send_chat(text)
        match(text[0]):
            case '.':
                self._fake_privmsg(text[1:])
            case ',':
                self._add_action_to_queue(text[1:])
            case _:
                pass

    def loop(self):
        while True:
            text = input('Enter message: ')
            self._handle_input(text)


def main():
    toggle_on_all_gifs()
    twitch = TwitchAPP()
    start_threads(twitch)
    try:
        TwitchChat(twitch).loop()
    except KeyboardInterrupt:
        pass
    print('Shutting down...')
    os._exit(0)


if __name__ == '__main__':
    main()
