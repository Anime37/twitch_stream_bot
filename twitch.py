import dataclasses
import json
import os
import random
from cli import CLI
from colors import *
import auth_server_thread
import requests
from twitch_websockets import TwitchWebSockets
import utils
from events import EventWrapper
from time import time
import fs
from word_utfer import TextUTFy
import webbrowser


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
    PRINT_TAG = 'API'
    USER_DATA_PATH = 'user_data/'
    ACCOUNT_PATH = f'{USER_DATA_PATH}account.json'
    SCOPES = [
        'channel:manage:broadcast',
        'channel:manage:guest_star',
        'channel:manage:raids',
        'channel:manage:schedule',
        'channel:read:stream_key',
        'channel:read:subscriptions',
        'chat:edit',
        'chat:read',
        'clips:edit',
        'moderator:manage:announcements',
        'moderator:read:followers',
        'moderator:manage:shoutouts',
        'user:edit',
        'user:manage:whispers',
        # need affiliate
        # 'channel:manage:predictions',
        # 'channel:manage:polls'
    ]
    token = None
    broadcaster_id = None
    last_raid_time = 0
    last_raided_channel = ''
    last_whisper_time = 0
    last_shoutout_time = 0
    last_shouted_out_channel = ''
    last_announcement_time = 0
    schedule_stream_start_time = 0
    scheduled_segments_counter = 0
    # prediction_files = []

    def __init__(self):
        self.cli = CLI()
        self.SCOPES = ' '.join(self.SCOPES)
        self.session = requests.Session()
        self.load_stored_data()

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def start_websockets(self):
        self.websockets = TwitchWebSockets(self.account.USER_NAME)
        self.websockets.start_all()

    def load_stored_data(self):
        self.last_raid_time = fs.readint('user_data/last_raid_time')
        self.last_whisper_time = fs.readint('user_data/last_whisper_time')
        self.last_shoutout_time = fs.readint('user_data/last_shoutout_time')
        self.last_announcement_time = fs.readint('user_data/last_announcement_time')

    def save_account_info(self):
        fs.write(self.ACCOUNT_PATH, dataclasses.asdict(self.account))

    def load_account_info(self):
        self.account = Account()
        if not os.path.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        self.account = Account(**fs.read(self.ACCOUNT_PATH))
        return self.validate_account_info()

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.print(f'missing {field} value in {self.ACCOUNT_PATH}')
                return False
        return True

    def get_token(self):
        self.print('getting token')

        # Try loading existing token
        TOKEN_PATH = f'{self.USER_DATA_PATH}token'
        self.token = fs.read(TOKEN_PATH)
        if self.token:
            return

        url = 'https://id.twitch.tv/oauth2/authorize'
        params = {
            'response_type': 'token',
            'client_id': self.account.CLIENT_ID,
            'redirect_uri': self.account.REDIRENT_URI,
            'scope': self.SCOPES,
            'state': utils.get_random_string(32)
        }
        with self.session.get(url, params=params) as r:
            webbrowser.open(r.url)
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
        self.print('getting broadcaster_id')

        # Try loading existing broadcaster_id
        BROADCASTER_ID_PATH = f'{self.USER_DATA_PATH}broadcaster_id'
        self.broadcaster_id = fs.read(BROADCASTER_ID_PATH)
        if self.broadcaster_id:
            return

        url = 'https://api.twitch.tv/helix/users'
        params = {
            'login': f'{self.account.USER_NAME}'
        }
        with self.session.get(url, params=params) as r:
            json_data = r.json()
        try:
            self.broadcaster_id = json_data['data'][0]['id']
            fs.write(BROADCASTER_ID_PATH, self.broadcaster_id)
        except:
            self.print(json_data)

    def get_channel_info(self):
        self.print('getting channel_info')

        url = 'https://api.twitch.tv'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(url, params=params) as r:
            self.print(r.json())

    def get_channel_stream_key(self):
        self.print('getting channel_stream_key')
        url = 'https://api.twitch.tv/helix/streams/key'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        with self.session.get(url, params=params) as r:
            json_data = r.json()
            try:
                self.stream_key = json_data['data'][0]['stream_key']
                self.print(self.stream_key)
            except:
                self.print(json_data)

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
        MAX_IDS = 5

        url = 'https://api.twitch.tv/helix/streams'
        params = {
            'first': 100,
            'after': ''
        }
        page_to_get = self.streams_page_to_get()
        self.print(f'getting streams (page {page_to_get})')
        json_data = {}
        for _ in range(page_to_get):
            with self.session.get(url, params=params) as r:
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
        if total_ids > MAX_IDS:
            from_left = random.randint(0, 1)
            self.channels = self.channels[:MAX_IDS] if from_left else self.channels[-MAX_IDS:]
        self.channel_info_iter = iter(self.channels)

    def get_stream_channel_info(self):
        channel_info: ChannelInfo
        try:
            channel_info = next(self.channel_info_iter)
        except StopIteration:
            self.get_streams()
            channel_info = next(self.channel_info_iter)
        return channel_info

    def modify_channel_info(self, channel_info: ChannelInfo, utfy: bool = False):
        MAX_TITLE_LEN = 140
        MAX_TAG_LEN = 25

        if utfy:
            title = TextUTFy(channel_info.title, 1, 2, False)[:MAX_TITLE_LEN]
        else:
            title = channel_info.title

        url = 'https://api.twitch.tv/helix/channels'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        data = {
            'title': title,
            'game_id': channel_info.id,
            'tags': utils.clamp_str_list(channel_info.tags, MAX_TAG_LEN),
        }
        with self.session.patch(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.print(
                    f'changing title to: {channel_info.title}\n'
                    f'[{self.PRINT_TAG}] changing tags to: {channel_info.tags}\n'
                    f'[{self.PRINT_TAG}] changing category to: {channel_info.name} (id={channel_info.id})'
                )
            else:
                self.print_err(r.content)

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

    # def get_random_prediction_outcomes(self):
    #     PREDICTIONS_PATH = 'predictions/'
    #     if not self.prediction_files:
    #         self.prediction_files = os.listdir(PREDICTIONS_PATH)
    #     prediction_list_path = f'{PREDICTIONS_PATH}{random.choice(self.prediction_files)}'
    #     random_prediction = fs.read(prediction_list_path)
    #     return random_prediction

    # def create_prediction(self):
    #     url = 'https://api.twitch.tv/helix/predictions'
    #     url = 'https://api.twitch.tv/helix/polls'
    #     data = {
    #         "broadcaster_id": self.broadcaster_id,
    #         "duration": 300,
    #     }
    #     data.update(self.get_random_prediction_outcomes())
    #     with self.session.post(url, data=json.dumps(data)) as r:
    #         self.print(r.request.body)
    #         try:
    #             self.print(f"{r.json()}")
    #         except:
    #             self.print_err(r.content)

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
            'message': utils.get_random_line('announcements.txt'),
            'color': random.choice(COLORS),
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.print('making an announcement!')
            else:
                self.print_err(r.content)
        self.last_announcement_time = current_time
        fs.write('user_data/last_announcement_time', str(self.last_announcement_time))

    def update_channel_description(self, description: str, utfy: bool = False):
        MAX_DESCRIPTION_LEN = 300
        url = 'https://api.twitch.tv/helix/users'
        if utfy:
            description = TextUTFy(description, 5, 10, False)[:MAX_DESCRIPTION_LEN]
        params = {
            'description': description
        }
        with self.session.put(url, params=params) as r:
            if r.status_code == 200:
                self.print(f'changing channel description')
            else:
                self.print_err(r.content)

    def get_stream_scheduled_segments_page(self, cursor=None):
        url = 'https://api.twitch.tv/helix/schedule'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'after': cursor,
        }
        with self.session.get(url, params=params) as r:
            return r.json()

    def get_all_stream_scheduled_segments(self):
        json_data = self.get_stream_scheduled_segments_page()
        cursor = json_data['pagination']['cursor']
        while cursor:
            json_data = self.get_stream_scheduled_segments_page(cursor)
            cursor = json_data['pagination']['cursor']
            for entry in json_data['data']['segments']:
                self.print(entry['start_time'])

    def create_stream_schedule_segment(self):
        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        duration = random.randint(30, 60)
        start_time = utils.get_rfc3339_time(self.schedule_stream_start_time)
        self.schedule_stream_start_time += duration
        data = {
            'start_time': start_time,
            'timezone': 'America/New_York',
            'duration': duration,
            'is_recurring': True,
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 200:
                self.scheduled_segments_counter += 1
                self.print(f'creating a stream schedule {duration} minute segment at {start_time} ({self.scheduled_segments_counter})')
            elif r.status_code == 400 and r.json()['message'] == 'Segment cannot create overlapping segment':
                self.delete_all_stream_schedule_segments()
            else:
                self.print_err(r.content)

    def delete_stream_schedule_segment(self, id):
        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'id': id,
        }
        with self.session.delete(url, params=params) as r:
            if r.status_code not in [204, 404]:
                self.print_err(r.content)
        return (r.status_code == 204)

    def _get_cursor_from_json(self, json_data: dict):
        try:
            cursor = json_data['pagination']['cursor']
        except:
            cursor = ''
        return cursor

    def delete_all_stream_schedule_segments(self):
        del_counter = 0
        self.print('deleting all scheduled stream segments...')
        json_data = self.get_stream_scheduled_segments_page()
        cursor = self._get_cursor_from_json(json_data)
        while cursor:
            json_data = self.get_stream_scheduled_segments_page(cursor)
            cursor = self._get_cursor_from_json(json_data)
            for entry in json_data['data']['segments']:
                if not self.delete_stream_schedule_segment(entry['id']):
                    cursor = ''
                    break
                del_counter += 1
            self.print(f'deleted scheduled stream segments: {del_counter}/{self.scheduled_segments_counter}')
        self.print(f'deleted all scheduled stream segments!')
        self.scheduled_segments_counter = 0

    def create_eventsub_subscription(self, type: str, version: str, conditions: dict):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        data = {
            'type': type,
            'version': version,
            'condition': conditions,
            'transport': {
                'method': 'websocket',
                'session_id': self.websockets.eventsub.session_id,
            },
        }
        headers = self.session.headers
        with self.session.post(url, json=data) as r:
            if r.status_code == 202:
                self.print(f'subscribed to {type} events')
            else:
                self.print(r.content)

    def subscribe_to_follow_events(self):
        self.create_eventsub_subscription(
            'channel.follow', '2',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )

    def subscribe_to_shoutout_create_events(self):
        self.create_eventsub_subscription(
            'channel.shoutout.create', '1',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )

    def subscribe_to_shoutout_received_events(self):
        self.create_eventsub_subscription(
            'channel.shoutout.receive', '1',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )
