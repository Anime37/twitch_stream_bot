import auth_server_thread
import fs
import utils
import webbrowser

from requests import Session

from .logging import TwitchLogging
from .account import TwitchAccount


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
        'moderator:read:followers',
        'moderator:manage:shoutouts',
        'user:edit',
        'user:manage:whispers',
        # need affiliate
        'channel:manage:predictions',
        'channel:manage:polls'
    ]
    token = None
    broadcaster_id = None

    def __init__(self, session: Session, log: TwitchLogging):
        super().__init__(log)
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
        auth_server_thread.start()
        self.token = auth_server_thread.server.queue.get()
        auth_server_thread.stop()

    def get_token(self):
        self.log.print('getting token')

        # Try loading existing token
        TOKEN_PATH = f'{fs.USER_DATA_PATH}token'
        self.token = fs.read(TOKEN_PATH)
        if self.token:
            return
        # Otherwise, request and store new token
        self._request_token()
        fs.write(TOKEN_PATH, self.token)

    def get_broadcaster_id(self):
        self.log.print('getting broadcaster_id')

        # Try loading existing broadcaster_id
        BROADCASTER_ID_PATH = f'{fs.USER_DATA_PATH}broadcaster_id'
        self.broadcaster_id = fs.read(BROADCASTER_ID_PATH)
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
            fs.write(BROADCASTER_ID_PATH, self.broadcaster_id)
        except:
            self.log.print(json_data)

    def set_session_headers(self):
        self.session.headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
