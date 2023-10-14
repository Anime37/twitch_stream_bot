from .command_base import CommandBase


class GithubLink(CommandBase):
    trigger = 'github'
    help_description: str = 'get the link to this project\'s GitHub'

    def run(self, params: str) -> str:
        return 'https://github.com/Anime37/twitch_stream_bot'

