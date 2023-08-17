from event_wrapper import EventWrapper

from cli import *


class EventHandler():
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(EventHandler, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if (self.initialized):
            return
        self.cli = CLI()
        self.events: dict[str, EventWrapper] = {}
        self.initialized = True

    def create_event(self, key_name: str):
        if not (key_name in self.events):
            self.events[key_name] = EventWrapper()
        return self.events[key_name]

    def get_event(self, key_name: str):
        return self.create_event(key_name)

    def delete_event(self, key_name: str):
        self.events.pop(key_name)
