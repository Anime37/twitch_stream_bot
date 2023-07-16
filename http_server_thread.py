import threading
from cli import CLI
from http.server import HTTPServer


class HTTPServerThread(HTTPServer, threading.Thread):
    def __init__(self, port, handler_class, tag='SRV'):
        self.cli = CLI()
        self.PRINT_TAG = tag
        server_address = ('', port)
        HTTPServer.__init__(self, server_address, handler_class)
        threading.Thread.__init__(self)

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def run(self):
        self.print('starting HTTP server...')
        self.serve_forever()

    def shutdown(self):
        self.print('stopping HTTP server...')
        super().shutdown()
