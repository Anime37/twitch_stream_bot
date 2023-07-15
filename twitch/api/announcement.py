from .shoutout import TwitchShoutout

import fs
import random
import utils


class TwitchAnnouncement(TwitchShoutout):
    last_announcement_time = 0

    def __init__(self):
        super().__init__()
        self.last_announcement_time = fs.readint('user_data/last_announcement_time')

    def send_announcement(self):
        MIN_ANNOUNCEMENT_PERIOD = (600)  # seconds
        current_time = utils.get_current_time()
        time_remaining = (self.last_announcement_time + MIN_ANNOUNCEMENT_PERIOD) - current_time
        if time_remaining > 0:
            self.print(f'next announcement in {time_remaining} seconds')
            return

        COLORS = [
            'blue',
            'green',
            'orange',
            'purple',
            'primary',
        ]
        url = 'https://api.twitch.tv/helix/chat/announcements'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'moderator_id': self.broadcaster_id,
        }
        data = {
            'message': utils.get_random_line(f'{self.MESSAGES_PATH}announcements.txt'),
            'color': random.choice(COLORS),
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.print('making an announcement!')
            else:
                self.print_err(r.content)
        self.last_announcement_time = current_time
        fs.write('user_data/last_announcement_time', str(self.last_announcement_time))
