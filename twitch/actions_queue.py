from __future__ import annotations

import utils

from cli import TagCLI
from queue import Queue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from twitch import TwitchAPP


class Action():
    def __init__(self, method: method, args: list = []):
        self.method = method
        self.args = args

    def __hash__(self):
        return hash((self.method, tuple(self.args)))

    def __eq__(self, other):
        return (isinstance(other, Action) and
                self.method == other.method and
                self.args == other.args)

    def run(self):
        self.method(*self.args)


class ActionList():
    def __init__(self):
        self.actions: list[Action] = []

    def add(self, method, args=[]):
        self.actions.append(Action(method, args))

    def __bool__(self):
        return bool(self.actions)

    def __iter__(self):
        return iter(self.actions)


class TwitchActionsQueue(Queue):
    app: TwitchAPP
    cli: TagCLI

    def __init__(self, app: TwitchAPP, maxsize: int = 0):
        super().__init__(maxsize)
        self.set = set()
        self.app = app
        self.cli = app.cli

    def _process_input(self, input: str):
        split_input = input.split(' ', maxsplit=1)
        action_name = split_input[0]
        if len(split_input) > 1:
            args = split_input[1].split(' ')
        else:
            args = []
        return action_name, args

    def add(self, input: str):
        action_name, args = self._process_input(input)
        action_list = ActionList()
        match(action_name):
            case 'eventsub_test':
                action_list.add(self.app.eventsub.subscribe_to_channel_update_events)
                action_list.add(self.app.eventsub.delete_channel_update_events)
            case 'reset':
                action_list.add(utils.restart_program)
            case 'whisper':
                action_list.add(self.app.whispers.random_response, args)
            case _:
                pass
        if not action_list:
            self.cli.print_err(f'no such queueable action: {action_name}')
            return
        if self.put(action_list):
            self.cli.print(f'queued up action: {action_name} | args: {args}')

    def put(self, actions: ActionList) -> bool:
        ret_val = False
        for action in actions:
            if self.full():
                self.cli.print_err(f'action queue is full')
                return ret_val
            if action in self.set:
                self.cli.print_err(f'action is already queued')
                return ret_val
            super().put(action)
            self.set.add(action)
            ret_val = True
        return ret_val

    def get_nowait(self) -> Action or None:
        action = super().get_nowait()
        self.set.remove(action)
        return action
