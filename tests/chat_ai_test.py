from cli import TagCLI
from fs import FS
from twitch_chat_ai import TwitchChatAI
from twitch.api.bans import TwitchBans

from .test_base import TestBase


class ChatAI_Test(TestBase):
    name: str = 'ChatAI'

    def run(self):
        ban_trigger = TwitchBans.ban_trigger
        username = 'bobbyX'
        cnt = 1
        chat_ai = TwitchChatAI(TagCLI('TST'), FS(), ban_trigger, 2, 5)
        try:
            while True:
                message = input()
                ai_response = chat_ai.get_response(username.replace('X', str(cnt)), message)
                cnt += 1
                if cnt > chat_ai.contexts.maxlen:
                    cnt = 1
                print(ai_response, (ban_trigger in ai_response))
        except KeyboardInterrupt:
            chat_ai.save_contexts('chat_ai_contexts_test')
