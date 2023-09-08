import os
import fs
import random
import utils

from dataclasses import dataclass
from requests import Session

from .logging import TwitchLogging
from .oauth import TwitchOAuth


@dataclass
class TwitchPolls():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth

    POLLS_PATH = f'{fs.MESSAGES_PATH}predictions/'
    URL = 'https://api.twitch.tv/helix/polls'

    polls_files = []
    next_poll_time = 0

    def _get_random_poll_choices(self):
        if not self.polls_files:
            self.polls_files = os.listdir(self.POLLS_PATH)
        poll_list_path = f'{self.POLLS_PATH}{random.choice(self.polls_files)}'
        random_poll = random.choice(fs.read(poll_list_path)['predictions'])
        # rename predictions outcomes to poll choices
        random_poll['choices'] = random_poll.pop('outcomes')
        return random_poll

    def get_current_poll(self):
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
        }
        with self.session.get(self.URL, params=data) as r:
            try:
                self.log.print(r.json()['data'][0])
            except:
                self.log.print_err(r.content)

    def _can_create_poll(self, current_time) -> bool:
        return (current_time > self.next_poll_time)

    def create_poll(self):
        current_time = utils.get_current_time()
        if not self._can_create_poll(current_time):
            self.log.print(f'next poll in {(self.next_poll_time - current_time)} seconds')
            return
        MIN_POLL_PERIOD = (15)  # seconds
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'duration': MIN_POLL_PERIOD,
        }
        data.update(self._get_random_poll_choices())
        with self.session.post(self.URL, json=data) as r:
            if r.status_code != 200:
                self.log.print_err(r.content)
                return
            self.log.print(f'starting a poll: {data["title"]}')
            self.next_poll_time = current_time + MIN_POLL_PERIOD + 1

    def _can_end_poll(self) -> bool:
        self.get_current_poll()
        return True

    def end_current_poll(self):
        if not self._can_end_poll():
            return
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'id': self.current_poll.id,
            'status': self.current_poll.result_status,
            'winning_outcome_id': self.current_poll.winning_outcome_id,
        }
        with self.session.patch(self.URL, json=data) as r:
            try:
                self.current_poll.reset()
            except:
                self.log.print_err(r.content)
