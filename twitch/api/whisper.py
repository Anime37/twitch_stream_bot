from random import choice
from fs import FS
import utils

from cli import TagCLI
from requests import Session

from .oauth import TwitchOAuth


class TwitchWhisper():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth

    def __init__(self, session: Session, cli: TagCLI, fs: FS, oauth: TwitchOAuth):
        self.session = session
        self.cli = cli
        self.fs = fs
        self.oauth = oauth

    def whisper(self, user_id: str, user_name: str, message: str):
        url = 'https://api.twitch.tv/helix/whispers'
        params = {
            'from_user_id': self.oauth.broadcaster_id,
            'to_user_id': user_id,
        }
        data = {
            'message': message
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.cli.print(f'>> WHISPER #{user_name}: {message}')
            else:
                self.cli.print_err(r.content)
        return (r.status_code == 204)

    def random_response(self, user_id: str, user_name: str):
        responses = ['yes', 'ok', 'sure']
        self.whisper(user_id, user_name, choice(responses))
