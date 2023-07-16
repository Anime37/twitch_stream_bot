from http.server import SimpleHTTPRequestHandler

from cli import *


class TTSRequestHandler(SimpleHTTPRequestHandler):
    PRINT_TAG = 'TTS'
    cli = CLI()

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def log_message(self, format, *args):
        try:
            if 'chat.mp3' in args[0]:
                return
        except:
            pass
        self.print(args)
