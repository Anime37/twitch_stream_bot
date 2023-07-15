from twitch_api.channel_info import ChannelInfo
from twitch_api.raid import TwitchRaid

import fs
import utils


class TwitchShoutout(TwitchRaid):
    last_shoutout_time = 0
    last_shouted_out_channel = ''

    def __init__(self):
        super().__init__()
        self.last_shoutout_time = fs.readint('user_data/last_shoutout_time')

    def shoutout(self, channel_info: ChannelInfo):
        MIN_SHOUTOUT_PERIOD = (150)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_shoutout_time + MIN_SHOUTOUT_PERIOD) - current_time
        if time_remaining > 0:
            self.print(f'next shoutout in {time_remaining} seconds')
            return
        user_name = channel_info.user_name
        if self.last_raided_channel == user_name:
            return
        url = 'https://api.twitch.tv/helix/chat/shoutouts'
        params = {
            'from_broadcaster_id': self.broadcaster_id,
            'to_broadcaster_id': channel_info.user_id,
            'moderator_id': self.broadcaster_id,
        }
        user_id = channel_info.user_id
        viewer_count = channel_info.viewer_count
        with self.session.post(url, params=params) as r:
            if r.status_code == 204:
                self.print(f'shouting out {user_name} ({user_id=}, {viewer_count=})')
            else:
                self.print_err(r.content)
        self.last_shoutout_time = current_time
        self.last_shouted_out_channel = user_name
        fs.write('user_data/last_shoutout_time', str(self.last_shoutout_time))
        self.websockets.irc.send_random_compliment(channel_info.user_login)
