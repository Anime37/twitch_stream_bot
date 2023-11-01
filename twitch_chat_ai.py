from collections import deque
from chat_ai import ChatAI
from cli import TagCLI
from fs import FS
import random


class TwitchChatAI(ChatAI):
    CHARACTER_LIMIT = 400

    def __init__(self, cli: TagCLI, fs: FS, ban_trigger: str, max_contexts: int = 5, max_context_len: int = 20):
        self.ban_trigger = ban_trigger
        super().__init__(cli, fs, max_contexts, max_context_len)

    def _get_config(self):
        CONFIG_PATH = f'{FS.USER_CONFIG_PATH}chat_ai.cfg'
        config = self.fs.readlines(CONFIG_PATH)
        config += [
            'you receive messages in "chatter_name:message" format.',
            f'if someone is being very rude, angry, is threatening or spamming gibberish, warn them to stop, but',
            f'if they continue 3 times in the row, you respond with >>>{self.ban_trigger}<<< to get them banned.',
            f'if they are saying slurs, you respond with >>>{self.ban_trigger}<<< to get them banned.',
            f'you respond in one sentence, with a {self.CHARACTER_LIMIT} character limit.',
        ]
        return config

    def _generate_response(self, user_name, content) -> str:
        return super()._generate_response(user_name, content)[:self.CHARACTER_LIMIT]

    def get_response(self, user_name, message) -> str:
        response = self._generate_response(user_name, message)
        return response

    def generate_follow_thx(self, user_name):
        random_year = random.randint(1980, 2023)
        message = f'i followed your channel \
suggest me a random obscure anime, that came out in {random_year}'
        return self._generate_response(user_name, message)

    def generate_followbot_response(self, user_name):
        reasons = [
            'lol',
            'you gonna get banned lol',
            'coz im a weirdo',
        ]
        return self._generate_response(user_name, f'i am followbotting your channel, {random.choice(reasons)}')

    def generate_shoutout_thx(self, user_name, viewer_count):
        random_year = random.randint(1980, 2023)
        message = f'i shouted out your channel to {viewer_count} viewers, \
suggest me a random obscure anime, that came out in {random_year}'
        return self._generate_response(user_name, message)
