import random
from .command_base import CommandBase


class Dice(CommandBase):
    trigger = 'dice'

    def run(self, params: str) -> str:
        return f'you rolled a {random.randint(3, 18)}'
