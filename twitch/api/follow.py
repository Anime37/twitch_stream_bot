from .channel_info import ChannelInfo


class TwitchFollow():
    def __init__(self):
        super().__init__()

    # WIP
    def follow(self, channel_info: ChannelInfo):
        url = 'https://gql.twitch.tv/gql'
        data = [{
                "operationName": "FollowButton_FollowUser",
                "variables": {
                    "input": {
                        "disableNotifications": False,
                        "targetID": f"39469972"
                    }
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "800e7346bdf7e5278a3c1d3f21b2b56e2639928f86815677a7126b093b2fdd08"
                    }
                }
                },
                {
                "operationName": "AvailableEmotesForChannel",
                "variables": {
                    "channelID": "39469972",
                    "withOwner": True
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "b9ce64d02e26c6fe9adbfb3991284224498b295542f9c5a51eacd3610e659cfb"
                    }
                }
                }]
        headers = self.session.headers
        headers['Client-Id'] = 'kimne78kx3ncx6brgo4mv6wki5h1ko'
        with self.session.post(url, json=data) as r:
            self.print_err(r.content)
