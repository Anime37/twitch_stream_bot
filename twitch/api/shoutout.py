from fs import FS
import utils

from cli import TagCLI
from requests import Session

from .channel_info import ChannelInfo
from .oauth import TwitchOAuth

from ..websockets.irc import TwitchIRC


class TwitchShoutout():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth

    irc: TwitchIRC

    LAST_TIME_PATH = f'{FS.USER_DATA_PATH}last_shoutout_time'

    last_shoutout_time = 0
    last_shouted_out_channel = ''

    def __init__(self, session: Session, cli: TagCLI, fs: FS, oauth: TwitchOAuth):
        self.session = session
        self.cli = cli
        self.fs = fs
        self.oauth = oauth
        self.last_shoutout_time = self.fs.readint(self.LAST_TIME_PATH)

    def set_irc(self, irc: TwitchIRC):
        self.irc = irc

    def shoutout(self, channel_info: ChannelInfo):
        MIN_SHOUTOUT_PERIOD = (150)  # seconds
        is_success = False
        current_time = utils.get_current_time()
        time_remaining = (self.last_shoutout_time + MIN_SHOUTOUT_PERIOD) - current_time
        if time_remaining > 0:
            self.cli.print(f'next shoutout in {time_remaining} seconds')
            return is_success
        user_name = channel_info.user_name
        url = 'https://api.twitch.tv/helix/chat/shoutouts'
        params = {
            'from_broadcaster_id': self.oauth.broadcaster_id,
            'to_broadcaster_id': channel_info.user_id,
            'moderator_id': self.oauth.broadcaster_id,
        }
        user_id = channel_info.user_id
        viewer_count = channel_info.viewer_count
        with self.session.post(url, params=params) as r:
            is_success = (r.status_code == 204)
        if is_success:
            self.cli.print(f'shouting out {user_name} ({user_id=}, {viewer_count=})')
            self.irc.send_random_compliment(channel_info.user_login)
        else:
            self.cli.print_err(r.content)
        self.last_shoutout_time = current_time
        self.last_shouted_out_channel = user_name
        self.fs.write(self.LAST_TIME_PATH, str(self.last_shoutout_time))
        return is_success
