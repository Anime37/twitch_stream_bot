import dataclasses


@dataclasses.dataclass
class AccountInfo():
    REDIRENT_URI: str = ''
    USER_NAME: str = ''
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''

