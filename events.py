from threading import Event


class EventWrapper(Event):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(EventWrapper, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if (self.initialized):
            return
        super().__init__()
        self.initialized = True

    def wait_and_clear(self, timeout=None):
        self.wait(timeout)
        self.clear()

    # def set(self):
    #     print('setting')
    #     super().set()
    #     print(self.is_set())

    # def clear(self):
    #     print('clearing')
    #     super().clear()
