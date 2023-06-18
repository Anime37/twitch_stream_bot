import random
import utils
import twitch_irc
from cli import CLI
from time import sleep
from twitch import Twitch
from word_utfer import TextUTFy


def loop(twitch:Twitch):
    cli = CLI()
    BASE_WORD = twitch.account.USER_NAME
    OFFSET = 3
    SPACES = ' ' * OFFSET
    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10
    word = ''
    utfed_word = ''
    while(True):
        word = utils.get_random_string(3) + SPACES + BASE_WORD + SPACES + utils.get_random_string(3)
        utfed_word = TextUTFy(word, 1, 5, False)
        twitch.modify_channel_title(utfed_word)
        twitch.create_clip()
        sleep_time = MIN_SLEEP_TIME + (random.random() * MAX_SLEEP_DELTA)
        cli.print(f'sleeping for {sleep_time:.2f} seconds')
        sleep(sleep_time)


def main():
    twitch = Twitch()
    if not twitch.load_account_info():
        return
    twitch.get_token()
    twitch.set_session_headers()
    twitch.get_broadcaster_id()
    twitch_irc.start(twitch.account.USER_NAME)
    # twitch.get_channel_stream_key()
    twitch.get_streams()
    loop(twitch)


if __name__ == '__main__':
    main()
