from abc import ABC, abstractmethod
from io import TextIOWrapper


class FSExtensionHandler(ABC):
    file_extension: str

    def is_extension(self, filepath: str):
        return filepath.endswith(self.file_extension)

    @abstractmethod
    def read(self, f: TextIOWrapper):
        pass

    @abstractmethod
    def write(self, f: TextIOWrapper, data):
        pass

    def readlines(self, f: TextIOWrapper) -> list[str]:
        return [line.strip() for line in f.readlines()]
