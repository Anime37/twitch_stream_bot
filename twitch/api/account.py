import dataclasses
from fs import FS
import os

from cli import TagCLI

from .account_info import AccountInfo


@dataclasses.dataclass
class TwitchAccount():
    cli: TagCLI
    fs: FS

    ACCOUNT_PATH = f'{FS.USER_DATA_PATH}account.json'

    def save_account_info(self):
        self.fs.write(self.ACCOUNT_PATH, dataclasses.asdict(self.account))

    def load_account_info(self):
        self.account = AccountInfo()
        if not self.fs.exists(self.ACCOUNT_PATH):
            self.save_account_info()
            self.cli.print(f'please fill out the account details in {self.ACCOUNT_PATH}')
            return False
        self.account = AccountInfo(**self.fs.read(self.ACCOUNT_PATH))
        return self.validate_account_info()

    def validate_account_info(self):
        for field in self.account.__dataclass_fields__:
            value = getattr(self.account, field)
            if not value:
                self.cli.print(f'missing {field} value in {self.ACCOUNT_PATH}')
                return False
        return True
