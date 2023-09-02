import random

from time import sleep

from .api import TwitchAPI
from .websockets import TwitchWebSockets


class TwitchAPP(TwitchAPI):
    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10

    def _setup_oauth(self) -> bool:
        if not self.oauth.load_account_info():
            return False
        self.oauth.get_token()
        self.oauth.set_session_headers()
        self.oauth.get_broadcaster_id()
        self.USER_NAME = self.oauth.account.USER_NAME
        return True

    def _start_websockets(self):
        self.websockets = TwitchWebSockets(self.oauth.account.USER_NAME)
        self.websockets.start_all()

    def _set_websocket_references(self):
        self.eventsub.set_websocket(self.websockets.eventsub)
        self.raid.set_irc(self.websockets.irc)
        self.shoutout.set_irc(self.websockets.irc)

    def _setup_eventsub(self):
        self.eventsub.delete_all_subscriptions()
        self.eventsub.subscribe_to_follow_events()
        self.eventsub.subscribe_to_shoutout_received_events()

    def setup(self) -> bool:
        if not self._setup_oauth():
            return False
        self._start_websockets()
        self._set_websocket_references()
        self._setup_eventsub()
        self.streams.get_streams()
        return True

    def api_loop(self):
        while True:
            channel_info = self.streams.get_channel_info()
            self.channel.modify_info(channel_info, True)
            self.channel.update_description(self.USER_NAME, True)
            self.shoutout.shoutout(channel_info) or self.raid.random()
            self.announcements.send()
            self.predictions.create_prediction()
            self.segments.create_stream_schedule_segment()
            self.clips.create()
            sleep_time = self.MIN_SLEEP_TIME + (random.random() * self.MAX_SLEEP_DELTA)
            print(f'sleeping for {sleep_time:.2f} seconds')
            sleep(sleep_time)
