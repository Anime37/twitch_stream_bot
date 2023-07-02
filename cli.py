import threading
import utils
from colors import TextColor


class CLI():
    instance = None
    HISTORY_LEN = 10
    DEFAULT_COLORS = [
        TextColor.RED,
        TextColor.BLUE,
    ]

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
        utils.clear_terminal()
        self.initialized = True

    def print(self, text):
        with self.mutex:
            self.history.append(text)
            if len(self.history) > self.HISTORY_LEN:
                self.history = self.history[-self.HISTORY_LEN:]
            for history_item in self.history:
                print(history_item)

    def get_next_color(self):
        try:
            color = next(self.color_iter)
        except:
            self.color_iter = iter(self.DEFAULT_COLORS)
            color = next(self.color_iter)
        return color

    # overrides
    def print(self, text, new_color=None):
        with self.mutex:
            if not new_color:
                new_color = self.get_next_color()
            print(f'{new_color}{text}')
            self.last_color = new_color
