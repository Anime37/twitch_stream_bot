from dataclasses import dataclass

from requests import Session

from cli import TagCLI
from fs import FS

from .oauth import TwitchOAuth


@dataclass
class TwitchClips():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth
    last_clip_id: str = ''

    def create(self):
        url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id
        }
        with self.session.post(url, params=params) as r:
            try:
                id = r.json()['data'][0]['id']
                self.cli.print(f'created a clip ({id=})')
                if self.last_clip_id:
                    self.fs.write(f'{FS.USER_DATA_PATH}last_clip_id.txt', self.last_clip_id)
                self.last_clip_id = id
            except:
                self.cli.print_err(r.content)
