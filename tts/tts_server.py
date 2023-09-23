from servers import HTTPServerThread

from .request_handler import TTSRequestHandler


class TTSServerThread(HTTPServerThread):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(TTSServerThread, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self, port=7452, tag: str = 'TTS'):
        if (self.initialized):
            return
        super().__init__(port, TTSRequestHandler, tag)
        self.initialized = True
