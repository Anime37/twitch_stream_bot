import abc

from dataclasses import dataclass


@dataclass
class ITest(metaclass=abc.ABCMeta):
    name: str

    def run():
        pass
