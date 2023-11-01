import os
import threading

from .fs_extension_handlers import *


class FS():
    instance = None

    USER_DATA_PATH = 'user_data/'
    TWITCH_TOKEN_PATH = f'{USER_DATA_PATH}twitch_token'
    USER_CONFIG_PATH = f'{USER_DATA_PATH}config/'
    MESSAGES_PATH = f'{USER_CONFIG_PATH}messages/'
    PREDICTIONS_PATH = f'{MESSAGES_PATH}predictions/'

    mutex: threading.Lock
    extension_handlers: list[FSExtensionHandler]

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(FS, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if (self.initialized):
            return
        self.mutex = threading.Lock()
        self.default_handler = FSDefaultHandler()
        self.extension_handlers = [
            FSJsonHandler(),
            # DEFAULT HAS TO BE AT THE END
            self.default_handler
        ]
        self.initialized = True

    def _get_extension_handler(self, filepath: str):
        for handler in self.extension_handlers:
            if handler.is_extension(filepath):
                break
        return handler

    def exists(self, filepath: str):
        return os.path.exists(filepath)

    def _read(self, filepath: str, read_method: callable):
        if not self.exists(filepath):
            return ''
        with self.mutex:
            with open(filepath, 'r', encoding='utf-8') as f:
                return read_method(f)

    def read(self, filepath: str):
        handler = self._get_extension_handler(filepath)
        return self._read(filepath, handler.read)

    def readlines(self, filepath: str) -> list[str]:
        return self._read(filepath, self.default_handler.readlines)

    def readint(self, filepath: str):
        str_val = self._read(filepath, self.default_handler.read)
        try:
            return int(str_val)
        except:
            return 0

    def write(self, filepath: str, data):
        handler = self._get_extension_handler(filepath)
        with self.mutex:
            with open(filepath, 'w', encoding='utf-8') as f:
                handler.write(f, data)
