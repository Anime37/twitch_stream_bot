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

    def __init__(self, cli: TagCLI, fs: FS, config: list[str], max_contexts: int = 5, max_context_len: int = 20):
        self.cli = cli
        self.fs = fs
        self.CONFIG_MESSAGE = [{"role": "system", "content": ' '.join(config)}]
        self.contexts = deque(maxlen=max_contexts)
        self.MAX_CONTEXT_LEN = max_context_len
        openai.api_key = self.fs.read(f'{FS.USER_DATA_PATH}openai_apikey')
        openai.organization = "org-WYxlMO9eJAwqVXE47qAZEQVV"

    def _get_conversation(self, context_name: str):
        for context in self.contexts:
            if next(iter(context)) == context_name:
                return context[context_name]
        return []

    def _add_context(self, context_name: str):
        conversation = deque(maxlen=self.MAX_CONTEXT_LEN)
        self.contexts.append({context_name: conversation})
        return conversation

    def _update_context(self, context_name, message):
        conversation = self._get_conversation(context_name)
        if not conversation:
            conversation = self._add_context(context_name)
        conversation.append(message)

    def _generate_response(self, context_name, content) -> str:
        output: str
        message = {"role": "user", "content": f'{context_name}:{content}'}
        self._update_context(context_name, message)
        try:
            responses = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.CONFIG_MESSAGE + list(self._get_conversation(context_name))
            )
        except Exception as e:
            self.cli.print_err(e)
            return ''
        self._update_context(context_name, responses['choices'][0]['message'])
        output = responses['choices'][0]['message']['content']
        output = output.replace('\n\n', '\n')
        output = output.replace(context_name, f'@{context_name}')
        return output
