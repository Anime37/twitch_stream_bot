import threading
from time import sleep
import utils


class CLI():
    instance = None
    HISTORY_LEN = 10

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(CLI, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if (self.initialized):
            return
        self.history = []
        self.mutex = threading.Lock()
        self.initialized = True

    def print(self, text):
        with self.mutex:
            self.history.append(text)
            if len(self.history) > self.HISTORY_LEN:
                self.history = self.history[-self.HISTORY_LEN:]
            utils.clear_terminal()
            for history_item in self.history:
                print(history_item)
