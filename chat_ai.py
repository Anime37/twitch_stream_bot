from collections import deque
from cli import TagCLI
from fs import FS
import openai
import random


class ChatAI():
    cli: TagCLI
    fs: FS

    CONFIG: list[str]
    CONFIG_MESSAGE: list[dict]

    def __init__(self, cli: TagCLI, fs: FS, config: list[str], max_queue_len: int = 10):
        self.cli = cli
        self.fs = fs
        self.CONFIG_MESSAGE = [{"role": "system", "content": ' '.join(config)}]
        self.message_deque = deque(maxlen=max_queue_len)
        openai.api_key = self.fs.read(f'{FS.USER_DATA_PATH}openai_apikey')
        openai.organization = "org-WYxlMO9eJAwqVXE47qAZEQVV"

    def _generate_response(self, user_name, content) -> str:
        output: str
        message = [{"role": "user", "content": f'{user_name}:{content}'}]
        try:
            responses = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.CONFIG_MESSAGE + list(self.message_deque) + message
            )
        except Exception as e:
            self.cli.print_err(e)
            return ''
        self.message_deque += message
        self.message_deque.append(responses['choices'][0]['message'])
        output = responses['choices'][0]['message']['content']
        output = output.replace('\n\n', '\n')
        output = output.replace(user_name, f'@{user_name}')
        return output
