from . import CLI, TextColor


class TagCLI():
    def __init__(self, tag):
        self.cli = CLI()
        self.PRINT_TAG = tag

    def print(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}')

    def print_list(self, lines: list):
        self.cli.print_list({self.PRINT_TAG}, lines)

    def print_err(self, text: str):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', TextColor.WHITE)

    def input(self, text: str) -> str:
        return self.cli.input(f'[{self.PRINT_TAG}] {text}')
