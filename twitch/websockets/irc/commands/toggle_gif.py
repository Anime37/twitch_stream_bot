import os
import random
from .command_base import CommandBase


class ToggleGif(CommandBase):
    trigger = 'togglegif'

    def _get_gif_filename(self, gifs, gif_name) -> str:
        if gif_name == 'random':
            return random.choice(gifs)
        for gif in gifs:
            if gif_name in gif:
                return gif
        return ''

    def _toggle_gif(self, gif_name: str) -> str:
        base_path = 'obs\gifs'
        gifs = os.listdir(base_path)
        gif_filename = self._get_gif_filename(gifs, gif_name)
        if not gif_filename:
            return 'no such gif exists!'
        src_path = f'{base_path}\{gif_filename}'
        is_off = (gif_filename[-4:] == '.off')
        output_path = src_path[:-4] if is_off else f'{src_path}.off'
        os.rename(src_path, output_path)
        result_str = 'on' if is_off else 'off'
        gif_name = gif_filename[:-4] if is_off else gif_filename
        return f'toggled {result_str} {gif_name}!'

    def run(self, params: str) -> str:
        if not params:
            return 'invalid params!'
        return self._toggle_gif(params)
