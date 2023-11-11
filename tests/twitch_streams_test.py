from requests import Session
from twitch.api.streams import TwitchStreams

from .twitch_oauth_test import TwitchOAuth_Test


class TwitchStreams_Test(TwitchOAuth_Test):
    name: str = 'streams'

    def __init__(self) -> None:
        super().__init__()
        self.streams = TwitchStreams(self.session, self.cli, self.fs)

    def run(self):
        if not self.setup():
            return
        page_to_get = int(input('which page of streams to get: '))
        streams = self.streams._get_streams_page(page_to_get)
        for entry in streams:
            user_name = entry['user_name']
            viewer_count = entry['viewer_count']
            self.cli.print(f'{user_name} | {viewer_count}')
