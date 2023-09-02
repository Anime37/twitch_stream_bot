from collections import deque
from cli import *
import fs
import openai
import random


class ChatAI():
    MESSAGE_DEQUE_LIMIT = 10
    CHARACTER_LIMIT = 400
    CONFIG = [
        f'you are a twitch streamer and you talk with different people, who can be identified by their chatter_name.',
        'you receive messages in "chatter_name:message" format.',
        'you remember people you are talking to by their chatter_name.'
        'you use bad grammar and lowercase.',
        'you mention chatter_name when responding.',
        'you are cheeky or insulting towards negative chatters.',
        'you never admit to being an AI or a chatbot.',
        f'you respond in one sentence, with a {CHARACTER_LIMIT} character limit.',
    ]
    CONFIG_MESSAGE = [{"role": "system", "content": ' '.join(CONFIG)}]
    message_deque = deque(maxlen=MESSAGE_DEQUE_LIMIT)

    def __init__(self):
        self.cli = CLI()
        openai.api_key = fs.read('user_data/openai_apikey')
        openai.organization = "org-WYxlMO9eJAwqVXE47qAZEQVV"

    def _generate_response(self, user_name, content, logging=False) -> str:
        output: str
        message = [{"role": "user", "content": f'{user_name}:{content}'}]
        try:
            responses = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.CONFIG_MESSAGE + list(self.message_deque) + message
            )
        except Exception as e:
            self.cli.print(e, TextColor.WHITE)
            return ''
        self.message_deque += message
        self.message_deque.append(responses['choices'][0]['message'])
        if logging:
            fs.write('ai_request.json', self.CONFIG_MESSAGE + list(self.message_deque))
            fs.write('ai_responses.json', responses)
        output = responses['choices'][0]['message']['content']
        output = output.replace('\n\n', '\n')
        output = output.replace(user_name, f'@{user_name}')
        return output[:self.CHARACTER_LIMIT].lower()

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
