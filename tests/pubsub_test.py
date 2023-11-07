from twitch.websockets.pubsub import TwitchPubSub

from .test_base import TestBase


class PubSub_Test(TestBase):
    name: str = 'PubSub'

    def run(self):
        pubsub = TwitchPubSub(None)
        pubsub.run()
