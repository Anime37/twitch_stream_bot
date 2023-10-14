from cli import *

from .command_base import CommandBase
from .dice import Dice
from .github_link import GithubLink
from .toggle_gif import ToggleGif
from .youtube_link import YoutubeLink


class CommandList():
    def __init__(self):
        self.cli = CLI()
        self.commands: list[CommandBase] = [
            Dice(),
            ToggleGif(),
            GithubLink(),
            YoutubeLink(),
        ]

    def _get_help(self):
        help_messages = []
        for command in self.commands:
            help_messages.append(command.get_help_msg())
        return help_messages

    def execute(self, cmd: str) -> list[str]:
        if 'help' in cmd:
            return self._get_help()
        for command in self.commands:
            if not command.was_triggered(cmd):
                continue
            params = command.extract_params(cmd)
            return [command.run(params)] # maybe possiblity to return list from run?
        return ['no such command exists']
