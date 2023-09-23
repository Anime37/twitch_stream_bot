import threading

from cli import TagCLI
from http.server import HTTPServer


class HTTPServerThread(HTTPServer, threading.Thread):
    def __init__(self, port, handler_class, tag='SRV'):
        self.cli = TagCLI(tag)
        server_address = ('', port)
        HTTPServer.__init__(self, server_address, handler_class)
        threading.Thread.__init__(self)

    def run(self):
        self.cli.print('starting HTTP server...')
        self.serve_forever()

    def stop(self):
        self.cli.print('stopping HTTP server...')
        self.shutdown()
        self.join()
