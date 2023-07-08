import random
from cli import CLI
import http_server_thread
from time import sleep
from twitch import Twitch

PRINT_TAG = 'APP'
cli = CLI()


def print(text: str):
    cli.print(f'[{PRINT_TAG}] {text}')


def loop(twitch:Twitch):
    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10
    while(True):
        channel_info = twitch.get_stream_channel_info()
        twitch.modify_channel_info(channel_info, True)
        twitch.update_channel_description(twitch.account.USER_NAME, True)
        twitch.shoutout(channel_info)
        twitch.raid_random()
        twitch.send_announcement()
        twitch.create_stream_schedule_segment()
        twitch.create_clip()
        sleep_time = MIN_SLEEP_TIME + (random.random() * MAX_SLEEP_DELTA)
        print(f'sleeping for {sleep_time:.2f} seconds')
        sleep(sleep_time)


def main():
    twitch = Twitch()
    if not twitch.load_account_info():
        return
    twitch.get_token()
    twitch.set_session_headers()
    twitch.get_broadcaster_id()
    twitch.start_websockets()
    twitch.subscribe_to_follow_events()
    twitch.subscribe_to_shoutout_received_events()
    http_server_thread.start()
    # twitch.get_channel_stream_key()
    # return
    twitch.get_streams()
    loop(twitch)


if __name__ == '__main__':
    main()
