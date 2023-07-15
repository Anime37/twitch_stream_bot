from .x import X

import fs
import utils


class Twitch(X):
    last_whisper_time = 0

    def __init__(self):
        super().__init__()
        self.last_whisper_time = fs.readint('user_data/last_whisper_time')

    def whisper(self, user_id, message):
        MIN_WHISPER_PERIOD = (60 * 40)  # 40 minutes
        current_time = utils.get_current_time()
        time_remaining = (self.last_whisper_time + MIN_WHISPER_PERIOD) - current_time
        if time_remaining > 0:
            self.print(f'too soon for another whisper ({time_remaining} seconds left)')
            return True

        url = 'https://api.twitch.tv/helix/whispers'
        params = {
            'from_user_id': self.broadcaster_id,
            'to_user_id': user_id,
        }
        data = {
            'message': message
        }
        with self.session.post(url, params=params, data=data) as r:
            status_code = r.status_code

        if (status_code in [204, 429]):
            self.last_whisper_time = current_time
            fs.write('user_data/last_whisper_time', str(self.last_whisper_time))
            return True

        return False
