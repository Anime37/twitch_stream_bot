from dataclasses import dataclass


@dataclass
class PRIVMSG():
    user_id: str
    sender: str
    content: str
