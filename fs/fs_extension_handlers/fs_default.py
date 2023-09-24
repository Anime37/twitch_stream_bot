from . import FSExtensionHandler


class FSDefaultHandler(FSExtensionHandler):
    file_extension = ''

    def read(self, f):
        return f.read()

    def write(self, f, data):
        f.write(data)
