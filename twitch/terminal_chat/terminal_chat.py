from cli import TagCLI
from twitch import TwitchAPP
from twitch.websockets.irc import PRIVMSG

from .actions_queue import TwitchActionsQueue


class TwitchTerminalChat():
    def __init__(self, app: TwitchAPP):
        self.app = app
        self.cli = app.cli
        self.irc = app.websockets.irc
        # self.actions_queue = TwitchActionsQueue(app)

    def _fake_privmsg(self, content: str):
        priv_msg = PRIVMSG(self.app.USER_NAME, '', '', '', content)
        self.irc.handle_privmsg(priv_msg)

    def _add_action_to_queue(self, action: str):
        match(action):
            case 'eventsub_test':
                self.app.actions_queue.put(self.app.eventsub.subscribe_to_channel_update_events)
                self.app.actions_queue.put(self.app.eventsub.delete_channel_update_events)

    def _handle_input(self, text: str):
        if not text:
            return
        self.irc.send_chat(text)
        match(text[0]):
            case '.':
                self._fake_privmsg(text[1:])
            case ',':
                self._add_action_to_queue(text[1:])
            case _:
                pass

    def loop(self):
        while True:
            text = self.cli.input('Enter message: ')
            self._handle_input(text)
