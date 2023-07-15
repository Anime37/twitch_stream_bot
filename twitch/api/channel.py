from .channel_info import ChannelInfo
from .streams import TwitchStreams

import utils
from word_utfer import TextUTFy


class TwitchChannel(TwitchStreams):
    def __init__(self):
        super().__init__()

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
