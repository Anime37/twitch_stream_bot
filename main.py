import random
import twitch_irc
from cli import CLI
import http_server_thread
from time import sleep
from twitch import Twitch


def loop(twitch:Twitch):
    cli = CLI()
    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10
    while(True):
        channel_info = twitch.get_stream_channel_info()
        twitch.modify_channel_title(channel_info, True)
        twitch.shoutout(channel_info)
        twitch.raid_random()
        twitch.create_clip()
        sleep_time = MIN_SLEEP_TIME + (random.random() * MAX_SLEEP_DELTA)
        cli.print(f'sleeping for {sleep_time:.2f} seconds')
        sleep(sleep_time)


def main():
    twitch = Twitch()
    if not twitch.load_account_info():
        return
    twitch.get_token()
    http_server_thread.start()
    twitch.set_session_headers()
    twitch.get_broadcaster_id()
    twitch_irc.start(twitch.account.USER_NAME)
    # twitch.get_channel_stream_key()
    # return
    twitch.get_streams()
    loop(twitch)


if __name__ == '__main__':
    main()
