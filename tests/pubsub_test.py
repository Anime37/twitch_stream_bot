from twitch.websockets.pubsub import TwitchPubSub

from .itest import ITest


class PubSub_Test(ITest):
    name: str = 'PubSub'

    def run(self):
        pubsub = TwitchPubSub()
        pubsub.run()
