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
        self.extension_handlers = [
            FSJsonHandler(),
            # DEFAULT HAS TO BE AT THE END
            FSDefaultHandler()
        ]
        self.initialized = True

    def _get_extension_handler(self, filepath: str):
        for handler in self.extension_handlers:
            if handler.is_extension(filepath):
                break
        return handler

    def exists(self, filepath: str):
        return os.path.exists(filepath)

    def read(self, filepath: str):
        if not self.exists(filepath):
            return ''
        handler = self._get_extension_handler(filepath)
        with self.mutex:
            with open(filepath, 'r', encoding='utf-8') as f:
                return handler.read(f)

    def readint(self, filepath: str):
        str_val = self.read(filepath)
        try:
            return int(str_val)
        except:
            return 0

    def write(self, filepath: str, data):
        handler = self._get_extension_handler(filepath)
        with self.mutex:
            with open(filepath, 'w', encoding='utf-8') as f:
                handler.write(f, data)
