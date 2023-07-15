from .channel import TwitchChannel
from .channel_info import ChannelInfo

import fs
import random
import utils


class TwitchRaid(TwitchChannel):
    last_raid_time = 0
    last_raided_channel = ''

    def __init__(self):
        super().__init__()
        self.last_raid_time = fs.readint('user_data/last_raid_time')

    def raid(self, channel_info: ChannelInfo):
        MIN_RAID_PERIOD = (100)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_raid_time + MIN_RAID_PERIOD) - current_time
        if time_remaining > 0:
            self.print(f'next raid in {time_remaining} seconds')
            return True
        user_id = channel_info.user_id
        user_name = channel_info.user_name
        viewer_count = channel_info.viewer_count
        url = 'https://api.twitch.tv/helix/raids'
        params = {
            'from_broadcaster_id': self.broadcaster_id,
            'to_broadcaster_id': user_id,
        }
        with self.session.post(url, params=params) as r:
            # self.print_err(r.content)
            if r.status_code in [409]:
                return True
            if r.status_code != 200:
                return False
        self.last_raided_channel = user_name
        self.last_raid_time = current_time
        fs.write('user_data/last_raid_time', str(self.last_raid_time))
        if r.status_code == 429:
            self.print_err(r.content)
            return True
        self.print(f'raiding {user_name} ({user_id=}, {viewer_count=})')
        self.websockets.irc.send_random_compliment(channel_info.user_login)
        return True

    def raid_random(self):
        rand_channel_info: ChannelInfo

        MAX_TRIES = 3
        retry_cnt = -1 # first loop always fails
        raid_user_name = self.last_shouted_out_channel
        while (self.last_shouted_out_channel == raid_user_name) or \
              ((retry_cnt < MAX_TRIES) and \
              (not self.raid(rand_channel_info))):
            rand_channel_info = random.choice(self.channels)
            raid_user_name = rand_channel_info.user_name
            retry_cnt += 1
        if retry_cnt >= MAX_TRIES:
            self.print('No one wants to be raided.')
