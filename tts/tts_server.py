from .request_handler import TTSRequestHandler

from http_server_thread import HTTPServerThread


class TTSServerThread(HTTPServerThread):
    instance = None

    PRINT_TAG = 'TTS'

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(TTSServerThread, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, port=7452):
        if (self.initialized):
            return
        super().__init__(port, TTSRequestHandler, self.PRINT_TAG)
        self.initialized = True
