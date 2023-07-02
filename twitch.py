import dataclasses
import os
import random
from cli import CLI
from colors import *
import auth_server_thread
import requests
import twitch_irc
import utils
from events import EventWrapper
from time import sleep, time
import json
import fs
from word_utfer import TextUTFy


@dataclasses.dataclass
class Account():
    REDIRENT_URI: str = ''
    USER_NAME: str = ''
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''


@dataclasses.dataclass
class ChannelInfo():
    name: str
    id: str
    tags: list
    title: str
    user_id: str
    user_name: str
    viewer_count: str
    user_login: str


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
        self.last_raid_time = fs.readint('user_data/last_raid_time')
        self.last_whisper_time = fs.readint('user_data/last_whisper_time')

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
        auth_server_thread.start()
        EventWrapper().wait_and_clear()
        EventWrapper().wait(5)
        auth_server_thread.stop()
        if EventWrapper().is_set():
            self.token = auth_server_thread.server.queue.get()
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

    def raid(self, channel_info: ChannelInfo):
        MIN_RAID_PERIOD = (100)  # seconds
        current_time = int(time())
        if (self.last_raid_time and ((self.last_raid_time + MIN_RAID_PERIOD) > current_time)):
            delta = (self.last_raid_time + MIN_RAID_PERIOD) - current_time
            self.cli.print(f'next raid in {delta} seconds')
            return True
        user_id = channel_info.user_id
        user_name = channel_info.user_name
        viewer_count = channel_info.viewer_count
        base_url = 'https://api.twitch.tv/helix/raids'
        params = {
            'from_broadcaster_id': self.broadcaster_id,
            'to_broadcaster_id': user_id,
        }
        self.cli.print(f'trying to raid {user_name}')
        with self.session.post(base_url, params=params) as r:
            # self.cli.print(r.content, TextColor.WHITE)
            if r.status_code in [409]:
                return True
            if r.status_code != 200:
                return False
        self.last_raid_time = current_time
        fs.write('user_data/last_raid_time', str(self.last_raid_time))
        if r.status_code == 429:
            self.cli.print(r.content, TextColor.WHITE)
            return True
        self.cli.print(f'raiding {user_name} ({user_id=}, {viewer_count=})')
        twitch_irc.send_random_compliment(channel_info.user_login)
        return True

    def raid_random(self):
        MAX_TRIES = 3
        retry_cnt = 0
        rand_idx = random.randrange(len(self.channels))
        rand_channel_info = self.channels[rand_idx]
        while (retry_cnt < MAX_TRIES) and (not self.raid(rand_channel_info)):
            # rand_user_id = rand_channel_info['user_id']
            # rand_user_name = rand_channel_info['user_name']
            # self.cli.print(f'{rand_user_name} ({rand_user_id}) doenst want to be raided')
            rand_idx = random.randrange(len(self.channels))
            rand_channel_info = self.channels[rand_idx]
            retry_cnt += 1
        if retry_cnt >= MAX_TRIES:
            self.cli.print('No one wants to be raided.')

    def get_top_streams(self):
        return random.randint(1, 3)

    def get_mid_streams(self):
        return random.randint(3, 5)

    def get_low_streams(self):
        return random.randint(5, 20)

    def streams_page_to_get(self):
        try:
            page_to_get = next(self.page_to_get_iter)()
        except:
            self.page_to_get_iter = iter(
                [self.get_low_streams]*4 +
                [self.get_mid_streams]*2 +
                [self.get_top_streams]*1
            )
            page_to_get = next(self.page_to_get_iter)()
        return page_to_get

    def get_streams(self):
        base_url = 'https://api.twitch.tv/helix/streams'
        params = {
            'first': 100,
            'after': ''
        }
        page_to_get = self.streams_page_to_get()
        self.cli.print(f'getting streams (page {page_to_get})')
        json_data = {}
        for _ in range(page_to_get):
            with self.session.get(base_url, params=params) as r:
                json_data = r.json()
            params['after'] = json_data['pagination']['cursor']
        data_entries = json_data['data']

        self.channels = []
        for entry in data_entries:
            if not entry['game_id']:
                continue
            channel_info = ChannelInfo(entry['game_name'], entry['game_id'], entry['tags'], entry['title'],
                                       entry['user_id'], entry['user_name'], entry['viewer_count'], entry['user_login'])
            if channel_info not in self.channels:
                self.channels.append(channel_info)
        total_ids = len(self.channels)
        if total_ids > 5:
            from_left = random.randint(0, 1)
            self.channels = self.channels[:5] if from_left else self.channels[-5:]
        self.channel_info_iter = iter(self.channels)

    def get_stream_channel_info(self):
        channel_info: ChannelInfo
        try:
            channel_info = next(self.channel_info_iter)
        except StopIteration:
            self.get_streams()
            channel_info = next(self.channel_info_iter)
        return channel_info

    def modify_channel_title(self, channel_info: ChannelInfo = None, title: str = None, utfy: bool = False):
        MAX_TITLE_LEN = 140
        MAX_TAG_LEN = 25

        if not channel_info:
            channel_info = self.get_stream_channel_info()
        if not title:
            title = channel_info.title
        if utfy:
            title = TextUTFy(title, 1, 2, False)[:MAX_TITLE_LEN]

        self.cli.print(
            f'changing title to {title}\n'
            f'changing tags to {channel_info.tags}\n'
            f'changing category to {channel_info.name} (id={channel_info.id})'
        )

        base_url = 'https://api.twitch.tv/helix/channels'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        data = {
            'title': title,
            'game_id': channel_info.id,
            'tags': utils.clamp_str_list(channel_info.tags, MAX_TAG_LEN),
        }
        with self.session.patch(base_url, params=params, data=data) as r:
            if r.status_code != 204:
                self.cli.print(r.content, TextColor.WHITE)

    def create_clip(self):
        base_url = 'https://api.twitch.tv/helix/clips'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.post(base_url, params=params) as r:
            try:
                id = r.json()['data'][0]['id']
                self.cli.print(f'creating a clip ({id=})')
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
    #             print(r.content, TextColor.WHITE)

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
                self.cli.print(r.content, TextColor.WHITE)

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
                self.cli.print(r.content, TextColor.WHITE)

    def whisper(self, user_id, message):
        MIN_WHISPER_PERIOD = (60 * 40)  # 40 minutes
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
        message = f'https://www.twitch.tv/popout/{self.account.USER_NAME}/guest-star'
        while not self.whisper(rand_entry['user_id'], message) and retry_cnt < MAX_TRIES:
            rand_idx = random.randrange(len(data_entries))
            rand_entry = data_entries[rand_idx]
            self.cli.print(f"{rand_entry['user_name']} doesn't want to be whispered")
            retry_cnt += 1
        if retry_cnt >= MAX_TRIES:
            return
        self.send_guest_star_invite(rand_entry)
