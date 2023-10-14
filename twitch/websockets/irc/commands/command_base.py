class CommandBase():
    trigger: str = 'undefined'
    help_params: str = ''
    help_description: str = 'undefined'

    trigger_len: int

    def __init__(self):
        self.trigger_len = len(self.trigger)

    def was_triggered(self, cmd: str) -> bool:
        return (cmd[:self.trigger_len] == self.trigger)

    def extract_params(self, cmd: str) -> str:
        return cmd[self.trigger_len:].strip()

    def get_help_msg(self) -> str:
        return f'!{self.trigger} {self.help_params} - {self.help_description}'

    def run(self, params: str) -> str:
        return 'command not implemented'
