from requests import Session
from twitch.api.oauth import TwitchOAuth

from .test_base import TestBase


class TwitchOAuth_Test(TestBase):
    def __init__(self) -> None:
        super().__init__()
        self.session = Session()
        self.oauth = TwitchOAuth(self.session, self.cli, self.fs)

    def setup(self) -> bool:
        if not self.oauth.load_account_info():
            return False
        self.oauth.get_token()
        self.oauth.set_session_headers()
        self.oauth.get_broadcaster_id()
        return True

    def run(self):
        if not self.setup():
            return
