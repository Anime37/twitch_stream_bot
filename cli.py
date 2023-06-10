import threading
from time import sleep
import utils


class TextColor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'  # Reset the text color


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
        self.last_color = TextColor.BLUE
        self.initialized = True

    def print(self, text):
        with self.mutex:
            self.history.append(text)
            if len(self.history) > self.HISTORY_LEN:
                self.history = self.history[-self.HISTORY_LEN:]
            utils.clear_terminal()
            for history_item in self.history:
                print(history_item)

    # overrides
    def print(self, text):
        new_color = TextColor.BLUE if (self.last_color == TextColor.RED) else TextColor.RED
        print(f'{new_color}{text}')
        self.last_color = new_color
