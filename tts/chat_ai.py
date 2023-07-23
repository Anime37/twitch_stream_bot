from collections import deque
import fs
import openai


class ChatAI():
    MESSAGE_DEQUE_LIMIT = 50
    CHARACTER_LIMIT = 400
    CONFIG = 'you are a twitch streamer, who responds to positivity with positivity and negativity with negativity. ' \
             'received messages are in <user_name>:<message> format ' \
             'remember who you are talking to by <user_name> ' \
             'no capitalizations and poor grammar. ' \
             f'one sentence, {CHARACTER_LIMIT} character limit responses.'
    CONFIG_MESSAGE = [{"role": "system", "content": CONFIG}]
    message_deque = deque(maxlen=MESSAGE_DEQUE_LIMIT)

    def __init__(self):
        openai.api_key = fs.read('user_data/openai_apikey')
        openai.organization = "org-WYxlMO9eJAwqVXE47qAZEQVV"

    def _generate_response(self, user_name, content, logging=True) -> str:
        output: str
        message = [{"role": "user", "content": f'{user_name}:{content}'}]
        try:
            responses = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.CONFIG_MESSAGE + list(self.message_deque) + message
            )
        except:
            return ''
        self.message_deque += message
        self.message_deque.append(responses['choices'][0]['message'])
        if logging:
            fs.write('ai_output.json', responses)
        output = responses['choices'][0]['message']['content']
        output = output.replace('\n\n', '\n') \
                       .replace(user_name, f'@{user_name}') \
                       .replace(':', ',')
        return output[:self.CHARACTER_LIMIT]

    def get_response(self, user_name, message) -> str:
        response = self._generate_response(user_name, message)
        return response

    def generate_follow_thx(self, user_name):
        return self._generate_response(user_name, 'i followed your channel, thank me and suggest a random obscure anime')

    def generate_shoutout_thx(self, user_name):
        return self._generate_response(user_name, 'i shouted out your channel, suggest me a random obscure anime')
