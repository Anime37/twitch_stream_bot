import os
import random

from cli import *


class GifManager():
    instance = None

    BASE_PATH = 'obs\gifs'

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(GifManager, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if (self.initialized):
            return
        self.initialized = True

    def _get_gif_filename(self, gifs, gif_name) -> str:
        if gif_name == 'random':
            return random.choice(gifs)
        for gif in gifs:
            if gif_name in gif:
                return gif
        return ''

    def _get_gif_list(self):
        return os.listdir(self.BASE_PATH)

    def _get_current_gif_state(self, gif_filename: str) -> bool:
        return (gif_filename[-4:] != '.off')

    def _state_to_string(self, is_on: bool) -> str:
        return 'on' if is_on else 'off'

    def _toggle_gif(self, gif_filename: str, new_state: bool) -> str:
        def _change_file_name(src_path: str, is_on: bool):
            output_path = src_path[:-4] if is_on else f'{src_path}.off'
            os.rename(src_path, output_path)

        def _get_new_file_name(gif_filename, is_on):
            return gif_filename[:-4] if is_on else gif_filename

        result_str = self._state_to_string(new_state)
        src_path = f'{self.BASE_PATH}\{gif_filename}'
        _change_file_name(src_path, new_state)
        gif_name = _get_new_file_name(gif_filename, new_state)
        return f'toggled {result_str} {gif_name}!'

    def find_and_toggle_gif(self, gif_name: str) -> str:
        gifs = self._get_gif_list()
        gif_filename = self._get_gif_filename(gifs, gif_name)
        if not gif_filename:
            return 'no such gif exists!'
        new_state = not self._get_current_gif_state(gif_filename)
        return self._toggle_gif(gif_filename, new_state)

    def toggle_all_gifs(self, new_state: bool):
        gifs = self._get_gif_list()
        for gif in gifs:
            if new_state == self._get_current_gif_state(gif):
                continue
            self._toggle_gif(gif, new_state)
        return f'toggled all gifs {self._state_to_string(new_state)}'
