class CommandBase():
    trigger: str
    trigger_len: int

    def __init__(self):
        self.trigger_len = len(self.trigger)

    def was_triggered(self, cmd: str) -> bool:
        return (cmd[:self.trigger_len] == self.trigger)

    def extract_params(self, cmd: str) -> str:
        return cmd[self.trigger_len:].strip()

    def run(self, params: str) -> str:
        return 'command not implemented'
