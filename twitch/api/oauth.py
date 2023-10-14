from fs import FS
import utils
import webbrowser

from cli import TagCLI
from requests import Session

from .account import TwitchAccount

from ..oauth_server.oauth_server import OAuthServer


class TwitchOAuth(TwitchAccount):
    session: Session

    SCOPES = [
        'channel:manage:broadcast',
        'channel:manage:guest_star',
        'channel:manage:raids',
        'channel:manage:schedule',
        'channel:read:stream_key',
        'channel:read:subscriptions',
        'chat:edit',
        'chat:read',
        'clips:edit',
        'moderator:manage:announcements',
        'moderator:manage:banned_users',
        'moderator:manage:shoutouts',
        'moderator:read:followers',
        'user:edit',
        'user:manage:whispers',
        # need affiliate
        'channel:manage:predictions',
        'channel:manage:polls'
    ]
    token = None
    broadcaster_id = None

    def __init__(self, session: Session, cli: TagCLI, fs: FS):
        super().__init__(cli, fs)
        self.session = session
        self.SCOPES = ' '.join(self.SCOPES)

    def _request_token(self):
        url = 'https://id.twitch.tv/oauth2/authorize'
        params = {
            'response_type': 'token',
            'client_id': self.account.CLIENT_ID,
            'redirect_uri': self.account.REDIRENT_URI,
            'scope': self.SCOPES,
            'state': utils.get_random_string(32)
        }
        with self.session.get(url, params=params) as r:
            webbrowser.open(r.url)
        oauth_server = OAuthServer()
        oauth_server.start()
        self.token = oauth_server.queue.get()
        oauth_server.stop()

    def get_token(self):
        self.cli.print('getting token')

        # Try loading existing token
        self.token = self.fs.read(FS.TWITCH_TOKEN_PATH)
        if self.token:
            return
        # Otherwise, request and store new token
        self._request_token()
        self.fs.write(FS.TWITCH_TOKEN_PATH, self.token)

    def get_broadcaster_id(self):
        self.cli.print('getting broadcaster_id')

        # Try loading existing broadcaster_id
        BROADCASTER_ID_PATH = f'{FS.USER_DATA_PATH}broadcaster_id'
        self.broadcaster_id = self.fs.read(BROADCASTER_ID_PATH)
        if self.broadcaster_id:
            return

        url = 'https://api.twitch.tv/helix/users'
        params = {
            'login': f'{self.account.USER_NAME}'
        }
        with self.session.get(url, params=params) as r:
            json_data = r.json()
        try:
            self.broadcaster_id = json_data['data'][0]['id']
            self.fs.write(BROADCASTER_ID_PATH, self.broadcaster_id)
        except:
            self.cli.print(json_data)

    def set_session_headers(self):
        self.session.headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
