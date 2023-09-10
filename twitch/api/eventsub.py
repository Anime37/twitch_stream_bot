from dataclasses import dataclass
from requests import Session

from .logging import TwitchLogging
from .oauth import TwitchOAuth

from ..websockets.eventsub import TwitchEventSubWebSocket


@dataclass
class TwitchEventSub():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth

    active_subscriptions = {}

    def set_websocket(self, websocket: TwitchEventSubWebSocket):
        self.websocket = websocket

    def get_subscriptions(self):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        with self.session.get(url) as r:
            if r.status_code != 200:
                self.log.print_err(r.content)
                return None
        return r.json()

    def delete_subscription(self, id):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        params = {
            'id': id
        }
        with self.session.delete(url, params=params) as r:
            is_success = (r.status_code == 204)
            if not is_success:
                self.log.print_err(r.content)
        return is_success

    def delete_all_subscriptions(self):
        subscriptions_json = self.get_subscriptions()
        if not subscriptions_json:
            return
        total = subscriptions_json['total']
        del_counter = 0
        self.log.print(f'deleting eventsub subscriptions: {del_counter}/{total}')
        for entry in subscriptions_json['data']:
            del_counter += self.delete_subscription(entry['id'])
        self.log.print(f'deleted eventsub subscriptions: {del_counter}/{total}')

    def create_subscription(self, type: str, version: str, conditions: dict):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        data = {
            'type': type,
            'version': version,
            'condition': conditions,
            'transport': {
                'method': 'websocket',
                'session_id': self.websocket.session_id,
            },
        }
        with self.session.post(url, json=data) as r:
            if r.status_code == 202:
                self.active_subscriptions[type] = r.json()['data'][0]['id']
                self.log.print(f'subscribed to {type} events')
            # elif r.status_code == 429:
            #     self.log.print(r.headers)
            else:
                self.log.print_err(r.content)

    def subscribe_to_channel_update_events(self):
        self.create_subscription(
            'channel.update', '2',
            {
                "broadcaster_user_id": self.oauth.broadcaster_id,
                "moderator_user_id": self.oauth.broadcaster_id
            }
        )

    def delete_channel_update_events(self):
        type = 'channel.update'
        if type not in self.active_subscriptions:
            return
        if self.delete_subscription(self.active_subscriptions[type]):
            self.log.print('deleted channel.update eventsub subscription')

    def subscribe_to_follow_events(self):
        self.create_subscription(
            'channel.follow', '2',
            {
                "broadcaster_user_id": self.oauth.broadcaster_id,
                "moderator_user_id": self.oauth.broadcaster_id
            }
        )

    def subscribe_to_shoutout_create_events(self):
        self.create_subscription(
            'channel.shoutout.create', '1',
            {
                "broadcaster_user_id": self.oauth.broadcaster_id,
                "moderator_user_id": self.oauth.broadcaster_id
            }
        )

    def subscribe_to_shoutout_received_events(self):
        self.create_subscription(
            'channel.shoutout.receive', '1',
            {
                "broadcaster_user_id": self.oauth.broadcaster_id,
                "moderator_user_id": self.oauth.broadcaster_id
            }
        )
