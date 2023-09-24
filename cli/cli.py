from .colors import TextColor
from typing import overload

import msvcrt
import threading
import utils
from time import sleep


class CLI():
    instance = None

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
        self.mutex = threading.Lock()
        utils.clear_terminal()
        self.initialized = True

    def _get_next_color(self):
        try:
            color = next(self.color_iter)
        except:
            self.color_iter = iter(self.DEFAULT_COLORS)
            color = next(self.color_iter)
        return color

    def _io_handler(self, text: str, color: TextColor, io_function):
        if not color:
            color = self._get_next_color()
        result = io_function(f'{color}{text}')
        self.last_color = color
        return result

    def _print(self, text: str, color: TextColor):
        self._io_handler(text, color, print)

    def _input(self, text: str, color: TextColor):
        return self._io_handler(text, color, input)

    def print(self, text: str = '', color: TextColor = None):
        with self.mutex:
            self._print(text, color)

    def input(self, text: str = '', color: TextColor = None):
        while not msvcrt.kbhit():
            sleep(0.1)
        with self.mutex:
            msg = self._input(text, color)
        return msg
