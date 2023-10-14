import random
from .command_base import CommandBase


class Dice(CommandBase):
    trigger = 'dice'
    help_description: str = 'roll a D20'

    def run(self, params: str) -> str:
        return f'you rolled a {random.randint(1, 20)}'
