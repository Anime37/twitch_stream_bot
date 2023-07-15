import requests
from cli import *


class TwitchBase():
    PRINT_TAG = 'API'
    USER_DATA_PATH = 'user_data/'
    MESSAGES_PATH = f'{USER_DATA_PATH}config/messages/'


    def __init__(self):
        self.cli = CLI()
        self.session = requests.Session()

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)
