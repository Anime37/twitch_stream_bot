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

    def _get_top_streams(self):
        return random.randint(1, 5)

    def _get_mid_streams(self):
        return random.randint(6, 20)

    def _get_low_streams(self):
        return random.randint(21, 50)

    def _streams_page_to_get(self):
        try:
            page_to_get = next(self.page_to_get_iter)()
        except:
            self.page_to_get_iter = iter(
                [self._get_low_streams]*1 +
                [self._get_mid_streams]*1 +
                [self._get_top_streams]*1
            )
            page_to_get = next(self.page_to_get_iter)()
        return page_to_get

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
        data_entries = self._get_streams_page(self._streams_page_to_get())
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
