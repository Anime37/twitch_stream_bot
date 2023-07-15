from .clips import TwitchClips


class TwitchEventSub(TwitchClips):
    def __init__(self):
        super().__init__()

    def get_eventsub_subscriptions(self):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        with self.session.get(url) as r:
            if r.status_code != 200:
                self.print_err(r.content)
                return None
        return r.json()

    def delete_eventsub_subscription(self, id):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        params = {
            'id': id
        }
        with self.session.delete(url, params=params) as r:
            is_success = (r.status_code == 204)
            if not is_success:
                self.print_err(r.content)
        return is_success

    def delete_all_eventsub_subscriptions(self):
        subscriptions_json = self.get_eventsub_subscriptions()
        if not subscriptions_json:
            return
        total = subscriptions_json['total']
        del_counter = 0
        self.print(f'deleting eventsub subscriptions: {del_counter}/{total}')
        for entry in subscriptions_json['data']:
            del_counter += self.delete_eventsub_subscription(entry['id'])
        self.print(f'deleted eventsub subscriptions: {del_counter}/{total}')

    def create_eventsub_subscription(self, type: str, version: str, conditions: dict):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        data = {
            'type': type,
            'version': version,
            'condition': conditions,
            'transport': {
                'method': 'websocket',
                'session_id': self.websockets.eventsub.session_id,
            },
        }
        headers = self.session.headers
        with self.session.post(url, json=data) as r:
            if r.status_code == 202:
                self.print(f'subscribed to {type} events')
            # elif r.status_code == 429:
            #     self.print(r.headers)
            else:
                self.print_err(r.content)

    def subscribe_to_follow_events(self):
        self.create_eventsub_subscription(
            'channel.follow', '2',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )

    def subscribe_to_shoutout_create_events(self):
        self.create_eventsub_subscription(
            'channel.shoutout.create', '1',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )

    def subscribe_to_shoutout_received_events(self):
        self.create_eventsub_subscription(
            'channel.shoutout.receive', '1',
            {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id": self.broadcaster_id
            }
        )
