import utils

from cli import TagCLI
from dataclasses import dataclass
from requests import Session
from word_utfer import TextUTFy

from .channel_info import ChannelInfo
from .oauth import TwitchOAuth


@dataclass
class TwitchChannel():
    session: Session
    cli: TagCLI
    oauth: TwitchOAuth

    def modify_info(self, channel_info: ChannelInfo, utfy: bool = False):
        MAX_TITLE_LEN = 140
        MAX_TAG_LEN = 25

        if utfy:
            title = TextUTFy(channel_info.title, 1, 2, False)[:MAX_TITLE_LEN]
        else:
            title = channel_info.title

        url = 'https://api.twitch.tv/helix/channels'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id
        }
        data = {
            'title': title,
            'game_id': channel_info.id,
            'tags': utils.clamp_str_list(channel_info.tags, MAX_TAG_LEN),
        }
        with self.session.patch(url, params=params, data=data) as r:
            if r.status_code == 204:
                self.cli.print_list(
                    [f'changing title to: {channel_info.title}',
                     f'changing tags to: {channel_info.tags}',
                     f'changing category to: {channel_info.name} (id={channel_info.id})']
                )
            else:
                self.cli.print_err(r.content)

    def update_description(self, description: str, utfy: bool = False):
        MAX_DESCRIPTION_LEN = 300
        url = 'https://api.twitch.tv/helix/users'
        if utfy:
            description = TextUTFy(description, 5, 10, False)[:MAX_DESCRIPTION_LEN]
        params = {
            'description': description
        }
        with self.session.put(url, params=params) as r:
            if r.status_code == 200:
                self.cli.print(f'changing channel description')
            else:
                self.cli.print_err(r.content)
