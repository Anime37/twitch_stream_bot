import dataclasses
import fs
import os

from .account_info import AccountInfo
from .logging import TwitchLogging


@dataclasses.dataclass
class TwitchAccount():
    log: TwitchLogging

    ACCOUNT_PATH = f'{fs.USER_DATA_PATH}account.json'

    def save_account_info(self):
        fs.write(self.ACCOUNT_PATH, dataclasses.asdict(self.account))

    def load_account_info(self):
        self.account = AccountInfo()
        if not os.path.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.log.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        self.account = AccountInfo(**fs.read(self.ACCOUNT_PATH))
        return self.validate_account_info()

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.log.print(f'missing {field} value in {self.ACCOUNT_PATH}')
                return False
        return True
