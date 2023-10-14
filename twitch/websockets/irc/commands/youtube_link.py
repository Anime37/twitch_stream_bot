from .command_base import CommandBase


class YoutubeLink(CommandBase):
    trigger = 'youtube'
    help_description: str = 'link to my youtubz'

    def run(self, params: str) -> str:
        return 'https://www.youtube.com/@AnimeGIFfy'
