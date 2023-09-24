from fs import FS
import random
import utils

from cli import TagCLI
from requests import Session

from .oauth import TwitchOAuth


class TwitchAnnouncement():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth

    LAST_TIME_PATH = f'{FS.USER_DATA_PATH}last_announcement_time'

    last_announcement_time = 0

    def __init__(self, session: Session, cli: TagCLI, fs: FS, oauth: TwitchOAuth):
        self.session = session
        self.cli = cli
        self.fs = fs
        self.oauth = oauth
        self.last_announcement_time = fs.readint(self.LAST_TIME_PATH)

    def send(self):
        MIN_ANNOUNCEMENT_PERIOD = (600)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_announcement_time + MIN_ANNOUNCEMENT_PERIOD) - current_time
        if time_remaining > 0:
            self.cli.print(f'next announcement in {time_remaining} seconds')
            return

        COLORS = [
            'blue',
            'green',
            'orange',
            'purple',
            'primary',
        ]
        url = 'https://api.twitch.tv/helix/chat/announcements'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'moderator_id': self.oauth.broadcaster_id,
        }
        data = {
            'message': utils.get_random_line(f'{FS.MESSAGES_PATH}announcements.txt'),
            'color': random.choice(COLORS),
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.cli.print('making an announcement!')
            else:
                self.cli.print_err(r.content)
        self.last_announcement_time = current_time
        self.fs.write(self.LAST_TIME_PATH, str(self.last_announcement_time))
