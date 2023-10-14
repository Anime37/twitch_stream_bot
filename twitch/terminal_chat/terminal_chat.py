from __future__ import annotations

import os
import sys

from cli import TagCLI
from twitch.websockets.irc import TwitchIRC, PRIVMSG

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from twitch import TwitchAPP


class TwitchTerminalChat():
    cli : TagCLI
    irc : TwitchIRC

    def __init__(self, app: TwitchAPP):
        self.app = app
        self.cli = app.cli
        self.irc = app.websockets.irc

    def _fake_privmsg(self, content: str):
        priv_msg = PRIVMSG('', self.app.USER_NAME, content)
        self.irc.handle_privmsg(priv_msg)

    def _handle_input(self, text: str):
        if not text:
            return
        self.irc.send_chat(text)
        if text[0] in ['.', ',', '!']:
            self._fake_privmsg(text)

    def loop(self):
        while True:
            text = self.cli.input('Enter message: ')
            self._handle_input(text)
