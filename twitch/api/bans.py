from collections import defaultdict
from cli import TagCLI
from dataclasses import dataclass
from requests import Session

from .oauth import TwitchOAuth


@dataclass
class TwitchBans():
    session: Session
    cli: TagCLI
    oauth: TwitchOAuth

    multipliers = defaultdict(list)

    def _get_multiplier(self, user_id: str):
        try:
            self.multipliers[user_id] += 1
        except:
            self.multipliers[user_id] = 1
        return self.multipliers[user_id]

    def ban_user(self, user_id: str, user_name: str):
        url = 'https://api.twitch.tv/helix/moderation/bans'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'moderator_id': self.oauth.broadcaster_id,
        }
        body = {
            'data': {
                'user_id': user_id,
                'duration': 30 * self._get_multiplier(user_id),
                'reason': 'relax ;)',
            }
        }
        print(body)
        with self.session.post(url, params=params, json=body) as r:
            if r.status_code == 200:
                self.cli.print(f'banned {user_name}')
            else:
                self.cli.print_err(r.content)
