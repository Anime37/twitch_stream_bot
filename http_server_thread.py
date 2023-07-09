import threading
from cli import CLI
from http.server import HTTPServer, SimpleHTTPRequestHandler

from colors import TextColor


PRINT_TAG = 'SRV'
cli = CLI()


def print(text: str):
    cli.print(f'[{PRINT_TAG}] {text}')


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        try:
            if 'chat.mp3' in args[0]:
                return
        except:
            pass
        print(args)


class HTTPServerThread(HTTPServer, threading.Thread):
    def __init__(self, port, handler_class=CustomHTTPRequestHandler):
        self.cli = CLI()
        server_address = ('', port)
        HTTPServer.__init__(self, server_address, handler_class)
        threading.Thread.__init__(self)

    def run(self):
        print('starting HTTP server...')
        self.serve_forever()

    def shutdown(self):
        print('stopping HTTP server...')
        super().shutdown()


def start():
    global http_server
    http_server = HTTPServerThread(7452)
    http_server.start()


def stop():
    global http_server
    http_server.shutdown()