from gif_manager import GifManager

from .command_base import CommandBase


class ToggleGif(CommandBase):
    trigger = 'togglegif'
    help_params: str = '<gif_name>'
    help_description: str = 'toggle gifs on/off on the stream (guess gif names)'

    def __init__(self):
        super().__init__()
        self.gif_manager = GifManager()

    def run(self, params: str) -> str:
        if not params:
            return 'invalid params!'
        return self.gif_manager.find_and_toggle_gif(params)
