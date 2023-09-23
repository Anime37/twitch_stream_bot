import os
import flask

from queue import Queue
from urllib.parse import parse_qs

from servers import FlaskServerThread


class OAuthServer(FlaskServerThread):
    queue = Queue(1)

    def __init__(self, port: int = 7452, tag: str = 'OTH'):
        templates_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(templates_dir, port, tag)
        self._add_flask_url_rules()

    def _add_flask_url_rules(self):
        self.app.add_url_rule('/', view_func=self.index)
        self.app.add_url_rule('/process', view_func=self.process_hash)

    def index(self):
        return flask.render_template('index.html')

    def process_hash(self):
        url_hash_str = flask.request.args.get('hash')[1:]
        query_params = parse_qs(url_hash_str)
        url_hash = {key: value[0] for key, value in query_params.items()}
        self.queue.put(url_hash["access_token"])
        return ""
