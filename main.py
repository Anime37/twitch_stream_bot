import os
import threading

from cli import TagCLI
from gif_manager import GifManager
from tts import TTSServerThread
from twitch import *


cli = TagCLI('APP')


def toggle_on_all_gifs():
    result = GifManager().toggle_all_gifs(True)
    cli.print(result)


def _start_twitch_threads(twitch: TwitchAPP):
    if not twitch.setup():
        return
    twitch_api_thread = threading.Thread(target=twitch.api_loop)
    twitch_api_thread.start()


def start_threads(twitch: TwitchAPP):
    TTSServerThread().start()
    _start_twitch_threads(twitch)


def main():
    toggle_on_all_gifs()
    twitch = TwitchAPP(cli)
    start_threads(twitch)
    try:
        TwitchTerminalChat(twitch).loop()
    except KeyboardInterrupt:
        cli.print('Shutting down...')
    os._exit(0)


if __name__ == '__main__':
    main()
