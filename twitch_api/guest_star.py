from .x import X

import random


class TwitchGuestStar(X):
    def __init__(self):
        super().__init__()

    def create_guest_star_session(self):
        url = 'https://api.twitch.tv/helix/guest_star/session'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.post(url, params=params) as r:
            try:
                json_data = r.json()
                return json_data['data'][0]['id']
            except:
                self.print_err(r.content)

    def get_guest_star_session(self):
        url = 'https://api.twitch.tv/helix/guest_star/session'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'moderator_id': self.broadcaster_id,
        }
        with self.session.get(url, params=params) as r:
            try:
                json_data = r.json()
                if not json_data['data']:
                    return self.create_guest_star_session()
                return json_data['data'][0]['id']
            except:
                self.print_err(r.content)

    def send_guest_star_invite(self, stream_data):
        user_id = stream_data['user_id']
        user_name = stream_data['user_name']
        viewer_count = stream_data['viewer_count']
        self.print(f'inviting {user_name} ({user_id=}, {viewer_count=})')

        url = 'https://api.twitch.tv/helix/guest_star/invites'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'moderator_id': self.broadcaster_id,
            'session_id': self.get_guest_star_session(),
            'guest_id': user_id,
        }
        with self.session.post(url, params=params) as r:
            pass

    def send_guest_star_invite_random(self, data_entries):
        MAX_TRIES = 3
        retry_cnt = 0
        rand_idx = random.randrange(len(data_entries))
        rand_entry = data_entries[rand_idx]
        message = f'https://www.twitch.tv/popout/{self.account.USER_NAME}/guest-star'
        while not self.whisper(rand_entry['user_id'], message) and retry_cnt < MAX_TRIES:
            rand_idx = random.randrange(len(data_entries))
            rand_entry = data_entries[rand_idx]
            self.print(f"{rand_entry['user_name']} doesn't want to be whispered")
            retry_cnt += 1
        if retry_cnt >= MAX_TRIES:
            return
        self.send_guest_star_invite(rand_entry)
