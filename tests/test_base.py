import abc

from cli import TagCLI
from fs import FS


class TestBase(metaclass=abc.ABCMeta):
    name: str

    def __init__(self):
        self.cli = TagCLI('TST')
        self.fs = FS()

    def run():
        pass
