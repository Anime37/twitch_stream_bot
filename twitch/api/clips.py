from cli import TagCLI
from dataclasses import dataclass
from requests import Session

from .oauth import TwitchOAuth


@dataclass
class TwitchClips():
    session: Session
    cli: TagCLI
    oauth: TwitchOAuth

    def create(self):
        url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id
        }
        with self.session.post(url, params=params) as r:
            try:
                id = r.json()['data'][0]['id']
                self.cli.print(f'creating a clip ({id=})')
            except:
                self.cli.print_err(r.content)
