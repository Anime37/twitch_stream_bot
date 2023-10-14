import random
import utils

from cli import TagCLI
from time import sleep
from twitch.actions_queue import TwitchActionsQueue

from .api import TwitchAPI
from .websockets import TwitchWebSockets


class TwitchAPP(TwitchAPI):
    cli: TagCLI
    actions_queue: TwitchActionsQueue

    MIN_SLEEP_TIME = 10
    MAX_SLEEP_DELTA = 10

    def __init__(self, cli: TagCLI):
        super().__init__()
        self.cli = cli
        self.actions_queue = TwitchActionsQueue(self, 5)

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

    def _sleep(self, secs: float):
        if secs <= 0:
            self.cli.print(f'skipping sleep ({secs:.2f})')
            return
        self.cli.print(f'sleeping for {secs:.2f} seconds')
        sleep(secs)

    def _run_api_actions(self):
        channel_info = self.streams.get_channel_info()
        self.channel.modify_info(channel_info, True)
        self.channel.update_description(self.USER_NAME, True)
        self.shoutout.shoutout(channel_info) or self.raid.random()
        self.announcements.send()
        self.polls.create_poll()
        self.predictions.create_prediction()
        self.segments.create_stream_schedule_segment()
        self.clips.create()

    def _run_queued_actions(self):
        if self.actions_queue.empty():
            return
        self.actions_queue.get_nowait()()

    def _run_actions(self):
        self._run_api_actions()
        self._run_queued_actions()

    def api_loop(self):
        while True:
            start_time = utils.get_current_time()
            self._run_actions()
            time_spent = utils.get_current_time() - start_time
            sleep_secs = self.MIN_SLEEP_TIME + (random.random() * self.MAX_SLEEP_DELTA) - time_spent
            self._sleep(sleep_secs)
