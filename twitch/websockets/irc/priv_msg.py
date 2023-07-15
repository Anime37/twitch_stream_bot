from dataclasses import dataclass


@dataclass
class PRIVMSG():
    sender: str
    user: str
    host: str
    target: str
    content: str
