from cli import *
from .command_base import CommandBase
from .dice import Dice
from .toggle_gif import ToggleGif


class CommandList():
    def __init__(self):
        self.cli = CLI()
        self.commands: list[CommandBase] = [
            Dice(),
            ToggleGif(),
        ]

    def execute(self, cmd: str) -> str:
        for command in self.commands:
            if not command.was_triggered(cmd):
                continue
            params = command.extract_params(cmd)
            return command.run(params)
        return 'no such command exists'
