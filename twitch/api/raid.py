import fs
import random
import utils

from cli import TagCLI
from requests import Session

from .channel_info import ChannelInfo
from .oauth import TwitchOAuth
from .streams import TwitchStreams

from ..websockets.irc import TwitchIRC


class TwitchRaid():
    session: Session
    cli: TagCLI
    oauth: TwitchOAuth
    streams: TwitchStreams
    irc: TwitchIRC

    last_raid_time = 0
    last_raided_channel = ''

    def __init__(self, session: Session, cli: TagCLI, oauth: TwitchOAuth, streams: TwitchStreams):
        self.session = session
        self.cli = cli
        self.oauth = oauth
        self.streams = streams
        self.last_raid_time = fs.readint('user_data/last_raid_time')

    def set_irc(self, irc: TwitchIRC):
        self.irc = irc

    def raid(self, channel_info: ChannelInfo):
        MIN_RAID_PERIOD = (100)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_raid_time + MIN_RAID_PERIOD) - current_time
        if time_remaining > 0:
            self.cli.print(f'next raid in {time_remaining} seconds')
            return True
        user_id = channel_info.user_id
        user_name = channel_info.user_name
        viewer_count = channel_info.viewer_count
        url = 'https://api.twitch.tv/helix/raids'
        params = {
            'from_broadcaster_id': self.oauth.broadcaster_id,
            'to_broadcaster_id': user_id,
        }
        with self.session.post(url, params=params) as r:
            if r.status_code in [409]:
                return True
            if r.status_code != 200:
                return False
        self.last_raided_channel = user_name
        self.last_raid_time = current_time
        fs.write('user_data/last_raid_time', str(self.last_raid_time))
        if r.status_code == 429:
            self.cli.print_err(r.content)
            return True
        self.cli.print(f'raiding {user_name} ({user_id=}, {viewer_count=})')
        self.irc.send_random_compliment(channel_info.user_login)
        return True

    def random(self):
        rand_channel_info: ChannelInfo
        MAX_TRIES = 3
        retry_cnt = 0
        while retry_cnt < MAX_TRIES:
            rand_channel_info = random.choice(self.streams.channels)
            if self.raid(rand_channel_info):
                break
            retry_cnt += 1
        is_success = (retry_cnt < MAX_TRIES)
        if not is_success:
            self.cli.print('No one wants to be raided.')
        return is_success
