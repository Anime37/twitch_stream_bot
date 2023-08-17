from threading import Event


class EventWrapper(Event):
    def __init__(self):
        super().__init__()

    def wait_and_clear(self, timeout=None):
        self.wait(timeout)
        self.clear()
