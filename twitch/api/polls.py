import os
from fs import FS
import random
import utils

from cli import TagCLI
from dataclasses import dataclass
from requests import Session

from .oauth import TwitchOAuth


@dataclass
class TwitchPolls():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth

    URL = 'https://api.twitch.tv/helix/polls'

    polls_files = []
    next_poll_time = 0

    def _get_random_poll_choices(self):
        if not self.polls_files:
            self.polls_files = os.listdir(FS.PREDICTIONS_PATH)
        poll_list_path = f'{FS.PREDICTIONS_PATH}{random.choice(self.polls_files)}'
        random_poll = random.choice(self.fs.read(poll_list_path)['predictions'])
        # rename predictions outcomes to poll choices
        random_poll['choices'] = random_poll.pop('outcomes')
        return random_poll

    def get_current_poll_id(self):
        result = ''
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
        }
        with self.session.get(self.URL, params=data) as r:
            try:
                result = r.json()['data'][0]['id']
            except:
                self.cli.print_err(r.content)
        return result

    def _can_create_poll(self, current_time) -> bool:
        return (current_time > self.next_poll_time)

    def create_poll(self):
        current_time = utils.get_current_time()
        if not self._can_create_poll(current_time):
            self.cli.print(f'next poll in {(self.next_poll_time - current_time)} seconds')
            return
        MIN_POLL_PERIOD = (15)  # seconds
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'duration': MIN_POLL_PERIOD,
        }
        data.update(self._get_random_poll_choices())
        with self.session.post(self.URL, json=data) as r:
            if r.status_code == 200:
                self.cli.print(f'starting a poll: {data["title"]}')
                self.next_poll_time = current_time + MIN_POLL_PERIOD + 1
            else:
                self.cli.print_err(r.content)
                self.end_current_poll()

    def end_current_poll(self):
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'id': self.get_current_poll_id(),
            'status': 'TERMINATED',
        }
        with self.session.patch(self.URL, json=data) as r:
            if r.status_code == 200:
                self.cli.print(f'manually terminated the poll')
            else:
                self.cli.print_err(r.content)
