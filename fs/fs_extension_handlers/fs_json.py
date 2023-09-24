import json

from . import FSExtensionHandler


class FSJsonHandler(FSExtensionHandler):
    file_extension = '.json'

    def read(self, f):
        return json.load(f)

    def write(self, f, data):
        json.dump(data, f, indent=2)
