from twitch import TwitchAPP


class TwitchActionsQueue():
    def __init__(self, app: TwitchAPP):
        self.app = app

    def add(self, action: str):
        match(action):
            case 'eventsub_test':
                self.app.actions_queue.put(self.app.eventsub.subscribe_to_channel_update_events)
                self.app.actions_queue.put(self.app.eventsub.delete_channel_update_events)
