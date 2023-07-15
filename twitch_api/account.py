from .account_info import AccountInfo
from .base import TwitchBase

import dataclasses
import fs
import os


class TwitchAccount(TwitchBase):
    def __init__(self):
        super().__init__()
        self.ACCOUNT_PATH = f'{self.USER_DATA_PATH}account.json'

    def save_account_info(self):
        fs.write(self.ACCOUNT_PATH, dataclasses.asdict(self.account))

    def load_account_info(self):
        self.account = AccountInfo()
        if not os.path.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        self.account = AccountInfo(**fs.read(self.ACCOUNT_PATH))
        return self.validate_account_info()

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.print(f'missing {field} value in {self.ACCOUNT_PATH}')
                return False
        return True
