import os
import random
import threading
from cli import CLI
from time import sleep
from tts import TTSServerThread
from twitch import TwitchAPP

PRINT_TAG = 'APP'
cli = CLI()


def print(text: str):
    cli.print(f'[{PRINT_TAG}] {text}')


def start_twitch_threads(twitch: TwitchAPP):
    if not twitch.load_account_info():
        return
    twitch.get_token()
    twitch.set_session_headers()
    twitch.get_broadcaster_id()
    twitch.delete_all_eventsub_subscriptions()
    twitch.start_websockets()
    twitch.subscribe_to_follow_events()
    twitch.subscribe_to_shoutout_received_events()
    twitch.get_streams()
    twitch_api_thread = threading.Thread(target=twitch_api_loop, args=(twitch,))
    twitch_api_thread.start()


def twitch_api_loop(twitch: TwitchAPP):
    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10
    while True:
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


def chat_input(twitch: TwitchAPP):
    user_name = twitch.account.USER_NAME
    irc = twitch.websockets.irc
    while True:
        msg = cli.input(f'[{PRINT_TAG}] Enter message: ')
        update_chat = (msg and (msg[0] == '.'))
        if update_chat:
            msg = msg[1:]
        irc.send_chat(msg)
        if update_chat:
            irc.update_chat(user_name, msg)
            ai_response = irc.tts.ai.get_response(user_name, msg)
            irc.send_chat(ai_response)


def main():
    twitch = TwitchAPP()
    start_twitch_threads(twitch)
    TTSServerThread().start()
    try:
        chat_input(twitch)
    except KeyboardInterrupt:
        pass
    print('Shutting down...')
    os._exit(0)


if __name__ == '__main__':
    main()
