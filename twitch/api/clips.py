from dataclasses import dataclass
from requests import Session

from .logging import TwitchLogging
from .oauth import TwitchOAuth


@dataclass
class TwitchClips():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth

    def create(self):
        url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id
        }
        with self.session.post(url, params=params) as r:
            try:
                id = r.json()['data'][0]['id']
                self.log.print(f'creating a clip ({id=})')
            except:
                self.log.print_err(r.content)
