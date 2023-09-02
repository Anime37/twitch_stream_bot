import fs
import utils

from requests import Session

from .channel_info import ChannelInfo
from .logging import TwitchLogging
from .oauth import TwitchOAuth

from ..websockets.irc import TwitchIRC


class TwitchShoutout():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth

    irc: TwitchIRC

    last_shoutout_time = 0
    last_shouted_out_channel = ''

    def __init__(self, session: Session, log: TwitchLogging, oauth: TwitchOAuth):
        self.session = session
        self.log = log
        self.oauth = oauth
        self.last_shoutout_time = fs.readint('user_data/last_shoutout_time')

    def set_irc(self, irc: TwitchIRC):
        self.irc = irc

    def shoutout(self, channel_info: ChannelInfo):
        MIN_SHOUTOUT_PERIOD = (150)  # seconds
        is_success = False
        current_time = utils.get_current_time()
        time_remaining = (self.last_shoutout_time + MIN_SHOUTOUT_PERIOD) - current_time
        if time_remaining > 0:
            self.log.print(f'next shoutout in {time_remaining} seconds')
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
            self.log.print(f'shouting out {user_name} ({user_id=}, {viewer_count=})')
            self.irc.send_random_compliment(channel_info.user_login)
        else:
            self.log.print_err(r.content)
        self.last_shoutout_time = current_time
        self.last_shouted_out_channel = user_name
        fs.write('user_data/last_shoutout_time', str(self.last_shoutout_time))
        return is_success
