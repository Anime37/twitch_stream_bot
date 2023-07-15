import dataclasses


@dataclasses.dataclass
class ChannelInfo():
    name: str
    id: str
    tags: list
    title: str
    user_id: str
    user_name: str
    viewer_count: str
    user_login: str
