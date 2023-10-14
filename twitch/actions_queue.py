from __future__ import annotations

import utils

from cli import TagCLI
from queue import Queue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from twitch import TwitchAPP


class TwitchActionsQueue(Queue):
    app: TwitchAPP
    cli: TagCLI

    def __init__(self, app: TwitchAPP, maxsize: int = 0):
        super().__init__(maxsize)
        self.app = app
        self.cli = app.cli

    def add(self, action: str):
        try:
            match(action):
                case 'eventsub_test':
                    self.put(self.app.eventsub.subscribe_to_channel_update_events)
                    self.put(self.app.eventsub.delete_channel_update_events)
                case 'reset':
                    self.put(utils.restart_program)
                case _:
                    raise Exception
        except:
            self.cli.print(f'no such queueable action: {action}')
        else:
            self.cli.print(f'queued up action: {action}')

    def put(self, func):
        super().put(func)
