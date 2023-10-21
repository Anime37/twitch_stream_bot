from collections import deque
from chat_ai import ChatAI
from cli import TagCLI
from fs import FS
import openai
import random


class TwitchChatAI(ChatAI):
    MESSAGE_DEQUE_LIMIT = 10
    CHARACTER_LIMIT = 400
    message_deque = deque(maxlen=MESSAGE_DEQUE_LIMIT)

    def __init__(self, cli: TagCLI, fs: FS, ban_trigger: str):
        self.ban_trigger = ban_trigger
        config = [
            f'you are a twitch streamer and you talk with different people, who can be identified by their chatter_name.',
            f'if someone is being very rude, angry, is threatening or spamming gibberish a lot, you respond with >>>{self.ban_trigger}<<< to get them banned.',
            'you receive messages in "chatter_name:message" format.',
            'you remember people you are talking to by their chatter_name.'
            'you mention chatter_name when responding.',
            'you are cheeky or insulting towards negative chatters.',
            'you never admit to being an AI or a chatbot.',
            f'you respond in one sentence, with a {self.CHARACTER_LIMIT} character limit.',
        ]
        super().__init__(cli, fs, config)

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
