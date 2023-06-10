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


@dataclasses.dataclass
class CategoryInfo():
    name:str
    id:str


class Twitch():
    USER_DATA_PATH = 'user_data/'
    ACCOUNT_PATH = f'{USER_DATA_PATH}account.json'
    token = None
    broadcaster_id = None
    last_raid_time = 0

    def __init__(self):
        self.cli = CLI()
        self.session = requests.Session()

    def save_account_info(self):
        with open(self.ACCOUNT_PATH, 'w') as f:
            json.dump(dataclasses.asdict(self.account), f, indent=2)

    def load_account_info(self):
        self.account = Account()
        if not os.path.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.cli.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        with open(self.ACCOUNT_PATH, 'r') as f:
            json_data = json.load(f)
            self.account = Account(**json_data)
        return self.validate_account_info()

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.cli.print(f'missing {field} value in {self.ACCOUNT_PATH}')
                return False
        return True

    def get_token(self):
        self.cli.print('getting token')

        # Try loading existing token
        TOKEN_PATH = f'{self.USER_DATA_PATH}token'
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as f:
                self.token = f.read()
        if self.token:
            return

        base_url = 'https://id.twitch.tv/oauth2/authorize'
        params = {
            'response_type': 'token',
            'client_id': self.account.CLIENT_ID,
            'redirect_uri': self.account.REDIRENT_URI,
            'scope': 'channel:read:stream_key channel:manage:broadcast channel:manage:raids chat:read chat:edit',
            'state': utils.get_random_string(32)
        }
        with self.session.get(base_url, params=params) as r:
            self.cli.print(r.url)
        server.start_server()
        EventWrapper().wait_and_clear()
        EventWrapper().wait(5)
        server.stop_server()
        if EventWrapper().is_set():
            self.token = server.server.queue.get()
            EventWrapper().clear()
        with open(TOKEN_PATH, 'w') as f:
            f.write(self.token)

    def set_session_headers(self):
        self.session.headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID
        }

    def get_broadcaster_id(self):
        self.cli.print('getting broadcaster_id')

        # Try loading existing broadcaster_id
        BROADCASTER_ID_PATH = f'{self.USER_DATA_PATH}broadcaster_id'
        if os.path.exists(BROADCASTER_ID_PATH):
            with open(BROADCASTER_ID_PATH, 'r') as f:
                self.broadcaster_id = f.read()
        if self.broadcaster_id:
            return

        base_url = 'https://api.twitch.tv/helix/users'
        params = {
            'login': f'{self.account.USER_NAME}'
        }
        with self.session.get(base_url, params=params) as r:
            json_data = r.json()
        try:
            self.broadcaster_id = json_data['data'][0]['id']
            with open(BROADCASTER_ID_PATH, 'w') as f:
                f.write(self.broadcaster_id)
        except:
            self.cli.print(json_data)

    def get_channel_info(self):
        self.cli.print('getting channel_info')

        base_url = 'https://api.twitch.tv'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(base_url, params=params) as r:
            self.cli.print(r.json())

    def get_channel_stream_key(self):
        self.cli.print('getting channel_stream_key')
        base_url = 'https://api.twitch.tv/helix/streams/key'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(base_url, params=params) as r:
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
        params = {
            'from_broadcaster_id': self.broadcaster_id,
            'to_broadcaster_id': user_id,
        }
        with self.session.post(base_url, params=params) as r:
            # self.cli.print(r.content)
            if r.status_code == 429:
                return True
            if r.status_code != 200:
                return False
        self.last_raid_time = current_time
        return True

    def get_top_streams(self, params):
        pass

    def get_mid_streams(self, params):
        pass

    def get_low_streams(self, params):
        pass

    def get_streams(self):
        self.cli.print(f'getting streams')
        base_url = 'https://api.twitch.tv/helix/streams'
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
            with self.session.get(base_url, params=params) as r:
                json_data = r.json()
            if (i % 11) == 10:
                sleep_time = 3 + (random.random() * 3)
                self.cli.print(f'sleeping for {sleep_time:.2f} seconds')
                sleep(sleep_time)
            params['after'] = json_data['pagination']['cursor']
        self.categories = []
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
            if not entry['game_id']:
                continue
            category_info = CategoryInfo(entry['game_name'], entry['game_id'])
            if category_info not in self.categories:
                self.categories.append(category_info)
        total_ids = len(self.categories)
        if total_ids > 10:
            from_left = random.randint(0,1)
            self.categories = self.categories[:10] if from_left else self.categories[-10:]
        self.category_iter = iter(self.categories)

    def get_stream_category(self):
        category:CategoryInfo
        try:
            category = next(self.category_iter)
        except StopIteration:
            self.get_streams()
            category = next(self.category_iter)
        return category

    def modify_channel_title(self, title, category=None):
        if not category:
            category = self.get_stream_category()

        self.cli.print(f'changing stream title to {title}')
        self.cli.print(f'changing category to {category.name} (id={category.id})')

        base_url = 'https://api.twitch.tv/helix/channels'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        data = {
            'title': title,
            'game_id': category.id
        }
        with self.session.patch(base_url, params=params, data=data) as r:
            pass

    def create_clip(self):
        pass
