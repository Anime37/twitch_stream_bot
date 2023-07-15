from .segments import TwitchSegments


class TwitchClips(TwitchSegments):
    def __init__(self):
        super().__init__()

    def create_clip(self):
        url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.post(url, params=params) as r:
            try:
                id = r.json()['data'][0]['id']
                self.print(f'creating a clip ({id=})')
            except:
                self.print_err(r.content)
