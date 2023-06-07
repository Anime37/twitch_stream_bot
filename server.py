import flask
import threading
from events import EventWrapper
from queue import Queue
from urllib.parse import parse_qs
from werkzeug.serving import make_server


app = flask.Flask('myapp')


class ServerThread(threading.Thread):
    port = 7452
    queue = Queue(1)

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', self.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server...')
        self.server.serve_forever()

    def shutdown(self):
        print('stopping server')
        self.server.shutdown()


@app.route('/')
def index():
    EventWrapper().set()
    return flask.render_template('index.html')


@app.route('/process')
def process_hash():
    url_hash_str = flask.request.args.get('hash')[1:]
    query_params = parse_qs(url_hash_str)
    url_hash = {key: value[0] for key, value in query_params.items()}
    server.queue.put(url_hash["access_token"])
    EventWrapper().set()
    return ""


def start_server():
    global server, app
    # App routes defined here
    server = ServerThread(app)
    server.start()
    print('server started')


def stop_server():
    global server
    server.shutdown()
