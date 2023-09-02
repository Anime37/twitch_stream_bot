import os
import threading

from cli import CLI
from tts import TTSServerThread
from twitch import TwitchAPP


def _start_twitch_threads(twitch: TwitchAPP):
    if not twitch.setup():
        return
    twitch_api_thread = threading.Thread(target=twitch.api_loop)
    twitch_api_thread.start()


def start_threads(twitch: TwitchAPP):
    TTSServerThread().start()
    _start_twitch_threads(twitch)


def chat_input(twitch: TwitchAPP):
    PRINT_TAG = 'APP'
    USER_NAME = twitch.oauth.account.USER_NAME
    cli = CLI()
    irc = twitch.websockets.irc

    while True:
        msg = cli.input(f'[{PRINT_TAG}] Enter message: ')
        update_chat = (msg and (msg[0] == '.'))
        if update_chat:
            msg = msg[1:]
        irc.send_chat(msg)
        if update_chat:
            irc.update_chat(USER_NAME, msg)
            ai_response = irc.ai.get_response(USER_NAME, msg)
            irc.send_chat(ai_response)


def main():
    twitch = TwitchAPP()
    start_threads(twitch)
    try:
        chat_input(twitch)
    except KeyboardInterrupt:
        pass
    print('Shutting down...')
    os._exit(0)


if __name__ == '__main__':
    main()
