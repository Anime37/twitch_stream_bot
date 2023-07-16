from .colors import TextColor

import msvcrt
import threading
import utils
from time import sleep


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

    def get_next_color(self):
        try:
            color = next(self.color_iter)
        except:
            self.color_iter = iter(self.DEFAULT_COLORS)
            color = next(self.color_iter)
        return color

    def print(self, text, new_color=None):
        with self.mutex:
            if not new_color:
                new_color = self.get_next_color()
            print(f'{new_color}{text}')
            self.last_color = new_color

    def input(self, input_text=''):
        while not msvcrt.kbhit():
            sleep(0.1)
        with self.mutex:
            msg = input(input_text)
        return msg
