from cli import *


class TwitchLogging():
    PRINT_TAG = 'API'

    def __init__(self):
        self.cli = CLI()

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_list(self, lines: list):
        self.cli.print_list({self.PRINT_TAG}, lines)

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)
