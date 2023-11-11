from cli import TagCLI
from dataclasses import dataclass
from requests import Session

from fs import FS

from .channel_info import ChannelInfo

import random

@dataclass
class TwitchStreams():
    session: Session
    cli: TagCLI

    CONFIG_PATH = f'{FS.USER_CONFIG_PATH}streams.cfg'

    def __init__(self, session: Session, cli: TagCLI, fs: FS):
        self.session = session
        self.cli = cli
        self.fs = fs
        self._load_config()

    def _save_config(self):
        data_str = ''
        for range in self.page_ranges:
            data_str += f'{range[0]}-{range[1]}\n'
        data_str = data_str[:-1]
        self.fs.write(self.CONFIG_PATH, data_str)

    def _load_config(self):
        self.page_ranges = []
        config_ranges = self.fs.readlines(self.CONFIG_PATH)
        if not config_ranges:
            self._load_defaults()
            return
        for range in config_ranges:
            range = range.split('-')
            start = int(range[0])
            end = int(range[1])
            self.page_ranges.append([start, end])

    def _load_defaults(self):
        self.page_ranges = [
            [1, 5],
            [6, 20],
            [21, 50],
        ]
        self._save_config()

    def set_config(self, *config_ranges: str):
        if not config_ranges:
            self.cli.print_err(f'no arguments received')
            return
        new_ranges = []
        for range in config_ranges:
            if '-' not in range:
                self.cli.print_err(f'invalid argument ({range})')
                return
            range = range.split('-')
            if len(range) != 2:
                self.cli.print_err(f'invalid format ({range})')
                return
            start = int(range[0])
            end = int(range[1])
            new_ranges.append([start, end])
        self.page_ranges = new_ranges
        self.cli.print(f'set new stream page ranges: {self.page_ranges}')
        self._save_config()

    def _get_streams_page_number(self):
        try:
            page_range = next(self.page_range_iter)
        except:
            self.page_range_iter = iter(self.page_ranges)
            page_range = next(self.page_range_iter)
        return random.randint(*page_range)

    def _get_streams_page(self, page: int):
        self.cli.print(f'getting streams (page {page})')
        url = 'https://api.twitch.tv/helix/streams'
        params = {
            'first': 100,
            'after': ''
        }
        json_data = {}
        for _ in range(page):
            with self.session.get(url, params=params) as r:
                json_data = r.json()
            params['after'] = json_data['pagination']['cursor']
        return json_data['data']

    def get_streams(self):
        MAX_IDS = 5
        self.channels = []
        data_entries = self._get_streams_page(self._get_streams_page_number())
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

    def get_channel_info(self):
        channel_info: ChannelInfo
        try:
            channel_info = next(self.channel_info_iter)
        except StopIteration:
            self.get_streams()
            channel_info = next(self.channel_info_iter)
        return channel_info
