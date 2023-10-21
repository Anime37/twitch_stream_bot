from cli import TagCLI
from fs import FS
from twitch_chat_ai import TwitchChatAI
from twitch.api.bans import TwitchBans

from .itest import ITest


class ChatAI_Test(ITest):
    def __init__(self):
        super().__init__('ChatAI')

    def run(self):
        ban_trigger = TwitchBans.ban_trigger
        username = 'bobbybobbob'
        chat_ai = TwitchChatAI(TagCLI('TST'), FS(), ban_trigger)
        while True:
            message = input()
            ai_response = chat_ai.get_response(username, message)
            print(ai_response, (ban_trigger in ai_response))
