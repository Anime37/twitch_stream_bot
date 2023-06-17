import dataclasses
import os
import random
from cli import CLI
from colors import *
import server
import requests
import twitch_irc
import utils
from events import EventWrapper
from time import sleep, time
import json
import fs


@dataclasses.dataclass
class Account():
    REDIRENT_URI: str = ''
    USER_NAME: str = ''
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''


@dataclasses.dataclass
class CategoryInfo():
    name: str
    id: str


class Twitch():
    USER_DATA_PATH = 'user_data/'
    ACCOUNT_PATH = f'{USER_DATA_PATH}account.json'
    SCOPES = [
        'channel:read:stream_key',
        'channel:manage:broadcast',
        'channel:manage:raids',
        'chat:read',
        'chat:edit',
        'clips:edit',
        'channel:manage:guest_star',
        'user:manage:whispers'
        # need affiliate
        # 'channel:manage:predictions',
        # 'channel:manage:polls'
    ]
    token = None
    broadcaster_id = None
    last_raid_time = 0
    last_whisper_time = 0
    # prediction_files = []

    def __init__(self):
        self.cli = CLI()
        self.SCOPES = ' '.join(self.SCOPES)
        self.session = requests.Session()
        self.load_stored_data()

    def load_stored_data(self):
        self.last_raid_time = int(fs.read('user_data/last_raid_time'))
        self.last_whisper_time = int(fs.read('user_data/last_whisper_time'))

    def save_account_info(self):
        fs.write(self.ACCOUNT_PATH, dataclasses.asdict(self.account))

    def load_account_info(self):
        self.account = Account()
        if not os.path.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.cli.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        self.account = Account(**fs.read(self.ACCOUNT_PATH))
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
        self.token = fs.read(TOKEN_PATH)
        if self.token:
            return

        base_url = 'https://id.twitch.tv/oauth2/authorize'
        params = {
            'response_type': 'token',
            'client_id': self.account.CLIENT_ID,
            'redirect_uri': self.account.REDIRENT_URI,
            'scope': self.SCOPES,
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
        fs.write(TOKEN_PATH, self.token)

    def set_session_headers(self):
        self.session.headers = {
            'Authorization': f'Bearer {self.token}',
            'Client-Id': self.account.CLIENT_ID,
            # 'Content-Type': 'application/json'
        }

    def get_broadcaster_id(self):
        self.cli.print('getting broadcaster_id')

        # Try loading existing broadcaster_id
        BROADCASTER_ID_PATH = f'{self.USER_DATA_PATH}broadcaster_id'
        self.broadcaster_id = fs.read(BROADCASTER_ID_PATH)
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
            fs.write(BROADCASTER_ID_PATH, self.broadcaster_id)
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
        MIN_RAID_PERIOD = (60) # 1 minutes
        current_time = int(time())
        if (self.last_raid_time and (self.last_raid_time + MIN_RAID_PERIOD) > current_time):
            delta = (self.last_whisper_time + MIN_RAID_PERIOD) - current_time
            self.cli.print(f'too soon for another raid ({delta} seconds left)')
            return True
        user_id = stream_data['user_id']
        user_name = stream_data['user_name']
        viewer_count = stream_data['viewer_count']
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
        fs.write('user_data/last_raid_time', str(self.last_raid_time))
        self.cli.print(f'raiding {user_name} ({user_id=}, {viewer_count=})')
        twitch_irc.send_random_compliment(user_name)
        return True

    def raid_random(self, data_entries):
        MAX_TRIES = 3
        retry_cnt = 0
        rand_idx = random.randrange(len(data_entries))
        rand_entry = data_entries[rand_idx]
        while not self.raid(rand_entry) and retry_cnt < MAX_TRIES:
            rand_user_id = rand_entry['user_id']
            rand_user_name = rand_entry['user_name']
            # self.cli.print(f'{rand_user_name} ({rand_user_id}) doenst want to be raided')
            rand_idx = random.randrange(len(data_entries))
            rand_entry = data_entries[rand_idx]
            retry_cnt += 1

    # def get_top_streams(self, params):
    #     pass

    # def get_mid_streams(self, params):
    #     pass

    # def get_low_streams(self, params):
    #     pass

    def get_streams(self):
        msg = 'getting streams'
        base_url = 'https://api.twitch.tv/helix/streams'
        params = {
            'first': 100,
            'after': ''
        }
        page_to_get = random.randint(5, 20)
        if (random.randint(0, 5) == 0):
            page_to_get = random.randint(3, 5)
        if (random.randint(0, 10) == 0):
            page_to_get = random.randint(1, 3)
        self.cli.print(f'{msg} (page {page_to_get})')
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

        # Raid a random stream
        self.raid_random(data_entries)
        # Invite a random streamer to a guest session
        self.send_guest_star_invite_random(data_entries)

        for entry in data_entries:
            if not entry['game_id']:
                continue
            category_info = CategoryInfo(entry['game_name'], entry['game_id'])
            if category_info not in self.categories:
                self.categories.append(category_info)
        total_ids = len(self.categories)
        if total_ids > 10:
            from_left = random.randint(0, 1)
            self.categories = self.categories[:10] if from_left else self.categories[-10:]
        self.category_iter = iter(self.categories)

    def get_stream_category(self):
        category: CategoryInfo
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
        msg = 'creating a clip'
        base_url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.post(base_url, params=params) as r:
            try:
                msg += f"\nclip_id={r.json()['data'][0]['id']}"
                self.cli.print(msg)
            except:
                self.cli.print(r.content, TextColor.WHITE)

    # def get_random_prediction_outcomes(self):
    #     PREDICTIONS_PATH = 'predictions/'
    #     if not self.prediction_files:
    #         self.prediction_files = os.listdir(PREDICTIONS_PATH)
    #     prediction_list_path = f'{PREDICTIONS_PATH}{random.choice(self.prediction_files)}'
    #     random_prediction = fs.read(prediction_list_path)
    #     return random_prediction

    # def create_prediction(self):
    #     base_url = 'https://api.twitch.tv/helix/predictions'
    #     base_url = 'https://api.twitch.tv/helix/polls'
    #     data = {
    #         "broadcaster_id": self.broadcaster_id,
    #         "duration": 300,
    #     }
    #     data.update(self.get_random_prediction_outcomes())
    #     with self.session.post(base_url, data=json.dumps(data)) as r:
    #         print(r.request.body)
    #         try:
    #             print(f"{r.json()}")
    #         except:
    #             print(r.content)

    def create_guest_star_session(self):
        base_url = 'https://api.twitch.tv/helix/guest_star/session'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.post(base_url, params=params) as r:
            try:
                json_data = r.json()
                return json_data['data'][0]['id']
            except:
                self.cli.print(r.content)

    def get_guest_star_session(self):
        base_url = 'https://api.twitch.tv/helix/guest_star/session'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'moderator_id': self.broadcaster_id,
        }
        with self.session.get(base_url, params=params) as r:
            try:
                json_data = r.json()
                if not json_data['data']:
                    return self.create_guest_star_session()
                return json_data['data'][0]['id']
            except:
                self.cli.print(r.content)

    def whisper(self, user_id, message):
        MIN_WHISPER_PERIOD = (60 * 40) # 40 minutes
        current_time = int(time())
        if (self.last_whisper_time and (self.last_whisper_time + MIN_WHISPER_PERIOD) > current_time):
            delta = (self.last_whisper_time + MIN_WHISPER_PERIOD) - current_time
            self.cli.print(f'too soon for another whisper ({delta} seconds left)')
            return True

        base_url = 'https://api.twitch.tv/helix/whispers'
        params = {
            'from_user_id': self.broadcaster_id,
            'to_user_id': user_id,
        }
        data = {
            'message': message
        }
        with self.session.post(base_url, params=params, data=data) as r:
            status_code = r.status_code

        if (status_code in [204, 429]):
            self.last_whisper_time = current_time
            fs.write('user_data/last_whisper_time', str(self.last_whisper_time))
            return True

        return False

    def send_guest_star_invite(self, stream_data):
        user_id = stream_data['user_id']
        user_name = stream_data['user_name']
        viewer_count = stream_data['viewer_count']
        self.cli.print(f'inviting {user_name} ({user_id=}, {viewer_count=})')

        base_url = 'https://api.twitch.tv/helix/guest_star/invites'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'moderator_id': self.broadcaster_id,
            'session_id': self.get_guest_star_session(),
            'guest_id': user_id,
        }
        with self.session.post(base_url, params=params) as r:
            pass

    def send_guest_star_invite_random(self, data_entries):
        MAX_TRIES = 3
        retry_cnt = 0
        rand_idx = random.randrange(len(data_entries))
        rand_entry = data_entries[rand_idx]
        message = 'https://www.twitch.tv/popout/nullptrrrrrrrrrrrrrrrrrrr/guest-star'
        while not self.whisper(rand_entry['user_id'], message) and retry_cnt < MAX_TRIES:
            rand_idx = random.randrange(len(data_entries))
            rand_entry = data_entries[rand_idx]
            self.cli.print(f"{rand_entry['user_name']} doesn't want to be whispered")
            retry_cnt += 1
        if retry_cnt >= MAX_TRIES:
            return
        self.send_guest_star_invite(rand_entry)
