import dataclasses
import os
import random
from cli import CLI
import server
import requests
import utils
from events import EventWrapper
from time import sleep, time
import json


@dataclasses.dataclass
class Account():
    REDIRENT_URI: str = ''
    USER_NAME: str = ''
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''


class Twitch():
    account_json_path = 'user_data/account.json'
    last_raid_time = 0

    def __init__(self):
        self.cli = CLI()
        self.session = requests.Session()

    def save_account_info(self):
        with open(self.account_json_path, 'w') as f:
            json.dump(dataclasses.asdict(self.account), f, indent=2)

    def load_account_info(self):
        self.account = Account()
        if not os.path.exists(self.account_json_path):
            self.save_account_info()
            self.cli.print(f'please fill out the account details in {self.account_json_path}')
            return False
        with open(self.account_json_path, 'r') as f:
            json_data = json.load(f)
            self.account = Account(**json_data)
        return True

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.cli.print(f'missing {field} value in {self.account_json_path}')
                return False
        return True

    def get_token(self):
        self.validate_account_info()
        self.cli.print('getting token')
        base_url = 'https://id.twitch.tv/oauth2/authorize'

        params = {
            'response_type': 'token',
            'client_id': self.account.CLIENT_ID,
            'redirect_uri': self.account.REDIRENT_URI,
            'scope': 'channel:read:stream_key channel:manage:broadcast channel:manage:raids',
            'state': utils.get_random_string(32)
        }
        # params_str = "&".join("%s=%s" % (k,v) for k,v in params.items())
        with self.session.get(base_url, params=params) as r:
            self.cli.print(r.url)
        server.start_server()
        EventWrapper().wait()
        EventWrapper().clear()
        EventWrapper().wait(5)
        if EventWrapper().is_set():
            self.token = server.server.queue.get()
            EventWrapper().clear()
        server.stop_server()

    def get_broadcaster_id(self):
        self.cli.print('getting broadcaster_id')
        base_url = 'https://api.twitch.tv/helix/users'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'login': f'{self.account.USER_NAME}'
        }
        with self.session.get(base_url, params=params, headers=headers) as r:
            json_data = r.json()
            try:
                self.broadcaster_id = json_data['data'][0]['id']
            except:
                self.cli.print(json_data)

    def get_channel_info(self):
        self.cli.print('getting channel_info')

        base_url = 'https://api.twitch.tv'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(base_url, params=params, headers=headers) as r:
            self.cli.print(r.json())

    def get_channel_stream_key(self):
        self.cli.print('getting channel_stream_key')
        base_url = 'https://api.twitch.tv/helix/streams/key'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(base_url, params=params, headers=headers) as r:
            json_data = r.json()
            try:
                self.stream_key = json_data['data'][0]['stream_key']
                self.cli.print(self.stream_key)
            except:
                self.cli.print(json_data)

    def raid(self, stream_data):
        current_time = int(time())
        if (self.last_raid_time and (self.last_raid_time + 60) > current_time):
            self.cli.print(f'too soon for another raid ({(self.last_raid_time + 60)} < {current_time})')
            return True
        user_id = stream_data['user_id']
        user_name = stream_data['user_name']
        viewer_count = stream_data['viewer_count']
        self.cli.print(f'raiding {user_name} ({user_id=}, {viewer_count=})')
        base_url = 'https://api.twitch.tv/helix/raids'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'from_broadcaster_id': self.broadcaster_id,
            'to_broadcaster_id': user_id,
        }
        with self.session.post(base_url, params=params, headers=headers) as r:
            self.cli.print(r.content)
            if r.status_code == 429:
                return True
            if r.status_code != 200:
                return False
        self.last_raid_time = current_time
        return True

    def get_streams(self):
        self.cli.print(f'getting streams')
        base_url = 'https://api.twitch.tv/helix/streams'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'first': 100,
            'after': ''
        }
        page_to_get = random.randint(5, 20)
        if (random.randint(0, 10) == 0):
            page_to_get = random.randint(3, 5)
        if (random.randint(0, 20) == 0):
            page_to_get = random.randint(1, 3)
        self.cli.print(f'getting page {page_to_get}')
        json_data = {}
        for i in range(page_to_get):
            with self.session.get(base_url, params=params, headers=headers) as r:
                json_data = r.json()
            if (i % 11) == 10:
                sleep_time = 3 + (random.random() * 3)
                self.cli.print(f'sleeping for {sleep_time:.2f} seconds')
                sleep(sleep_time)
            params['after'] = json_data['pagination']['cursor']
        self.game_ids = []
        data_entries = json_data['data']
        rand_idx = random.randrange(len(data_entries))
        rand_entry = data_entries[rand_idx]
        rand_user_id = rand_entry['user_id']
        rand_user_name = rand_entry['user_name']
        retry_cnt = 0
        while not self.raid(rand_entry) and retry_cnt < 3:
            self.cli.print(f'{rand_user_name} ({rand_user_id}) doenst want to be raided')
            rand_idx = random.randrange(len(data_entries))
            rand_entry = data_entries[rand_idx]
            rand_user_id = rand_entry['user_id']
            rand_user_name = rand_entry['user_name']
            retry_cnt += 1
        for entry in data_entries:
            game_id = entry['game_id']
            game_name = entry['game_name']
            if game_id not in self.game_ids:
                self.game_ids.append(game_id)
        total_ids = len(self.game_ids)
        if total_ids > 10:
            from_left = random.randint(0,1)
            self.game_ids = self.game_ids[:10] if from_left else self.game_ids[-10:]
        self.game_ids_iter = iter(self.game_ids)

    def modify_channel_title(self, title):
        try:
            game_id = next(self.game_ids_iter)
        except StopIteration:
            self.get_streams()
            game_id = next(self.game_ids_iter)
        self.cli.print(f'changing stream title to {title}')
        self.cli.print(f'changing game_id to {game_id}')
        base_url = 'https://api.twitch.tv/helix/channels'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        data = {
            'title': title,
            'game_id': game_id
        }
        with self.session.patch(base_url, params=params, headers=headers, data=data) as r:
            pass
