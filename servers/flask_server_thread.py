import threading
import flask

from cli import TagCLI
from werkzeug.serving import make_server


class FlaskServerThread(threading.Thread):
    def __init__(self, template_dir = '', port: int = 7452, tag: str = 'SRV'):
        self.cli = TagCLI(tag)
        self.stop_event = threading.Event()
        threading.Thread.__init__(self, args=(self.stop_event,))
        self.app = flask.Flask('oauth_app', template_folder=f'{template_dir}\\templates')
        self.server = make_server('127.0.0.1', port, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def run(self):
        self.cli.print('starting server...')
        self.server.serve_forever()

    def stop(self):
        self.cli.print('stopping server')
        self.server.shutdown()
        self.join()
