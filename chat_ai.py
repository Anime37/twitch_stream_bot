import threading
from collections import deque

import openai

from cli import TagCLI
from fs import FS


class ChatAI():
    cli: TagCLI
    fs: FS

    CONFIG: list[str]
    CONFIG_MESSAGE: list[dict]

    def __init__(self, cli: TagCLI, fs: FS, max_contexts: int = 5, max_context_len: int = 20):
        self.cli = cli
        self.fs = fs
        self.load_config()
        self.contexts = deque(maxlen=max_contexts)
        self.MAX_CONTEXT_LEN = max_context_len
        openai.api_key = self.fs.read(f'{FS.USER_DATA_PATH}openai_apikey')
        openai.organization = "org-WYxlMO9eJAwqVXE47qAZEQVV"
        self.mutex = threading.Lock()

    def _get_config(self):
        return [f'you are a chat ai.']

    def load_config(self):
        self.CONFIG_MESSAGE = [{"role": "system", "content": ' '.join(self._get_config())}]

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
        self.mutex.acquire()
        self._update_context(context_name, message)
        try:
            responses = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.CONFIG_MESSAGE + list(self._get_conversation(context_name))
            )
        except Exception as e:
            self.cli.print_err(e)
            return ''
        self._update_context(context_name, responses['choices'][0]['message'].to_dict())
        self.mutex.release()
        output = responses['choices'][0]['message']['content']
        output = output.replace('\n\n', '\n')
        output = output.replace(context_name, f'@{context_name}')
        return output

    def save_contexts(self, filename: str = 'chat_ai_contexts'):
        self.cli.print('saving contexts')
        CONTEXTS_PATH = f'{FS.USER_DATA_PATH}{filename}.txt'
        output_str = ''
        self.mutex.acquire()
        for context in self.contexts:
            (context_name, conversation_list), = context.items()
            conversation = [f"{entry['role']}: {entry['content']}" for entry in list(conversation_list)]
            output_str += f'{context_name}:\n'
            for entry in conversation:
                output_str += f'{entry}\n'
            output_str += '\n'
        self.mutex.release()
        self.fs.write(CONTEXTS_PATH, output_str)
