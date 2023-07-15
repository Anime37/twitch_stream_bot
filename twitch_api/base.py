import dataclasses
import json
import os

import requests
from cli import CLI
from colors import *


class TwitchBase():
    PRINT_TAG = 'API'
    USER_DATA_PATH = 'user_data/'

    def __init__(self):
        self.cli = CLI()
        self.session = requests.Session()

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)
