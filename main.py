import utils
import random
from time import sleep
from twitch import Twitch
from word_utfer import TextUTFy


def loop(twitch):
    offset = 3
    while(True):
        base_word = 'nullptr'
        spaces = ' ' * offset
        word = utils.get_random_string(3) + spaces + base_word + spaces + utils.get_random_string(3)
        utfed_word = TextUTFy(word, 1, 5, False)
        twitch.modify_channel_title(utfed_word)
        sleep_time = 10 + (random.random() * 10)
        print(f'sleeping for {sleep_time:.2f} seconds')
        sleep(sleep_time)


def main():
    twitch = Twitch()
    if not (twitch.load_account_info() and twitch.validate_account_info()):
        return
    twitch.get_token()
    twitch.get_broadcaster_id()
    # twitch.get_channel_stream_key()
    twitch.get_streams()
    loop(twitch)


if __name__ == '__main__':
    main()
