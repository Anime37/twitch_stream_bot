from . import CLI, TextColor


class TagCLI():
    def __init__(self, tag: str):
        self.cli = CLI()
        self.PRINT_TAG = tag

    def print(self, text: str, color: TextColor = None):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', color)

    def print_list(self, lines: list, color: TextColor = None):
        with self.cli.mutex:
            if not color:
                color = self.cli._get_next_color()
            for line in lines:
                self.cli._print(f'[{self.PRINT_TAG}] {line}', color)

    def print_err(self, text: str, color: TextColor = TextColor.WHITE):
        self.cli.print(f'[{self.PRINT_TAG}] {text}', color)

    def input(self, text: str = '', color: TextColor = None) -> str:
        return self.cli.input(f'[{self.PRINT_TAG}] {text}', color)
