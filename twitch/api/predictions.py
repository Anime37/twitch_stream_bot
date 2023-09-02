import os
import fs
import random

from dataclasses import dataclass
from requests import Session

from .logging import TwitchLogging
from .oauth import TwitchOAuth


@dataclass
class TwitchPredictions():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth
    PREDICTIONS_PATH = f'{fs.USER_CONFIG_PATH}predictions/'

    def _get_random_prediction_outcomes(self):
        if not self.prediction_files:
            self.prediction_files = os.listdir(self.PREDICTIONS_PATH)
        prediction_list_path = f'{self.PREDICTIONS_PATH}{random.choice(self.prediction_files)}'
        random_prediction = fs.read(prediction_list_path)
        return random_prediction

    def create_prediction(self):
        url = 'https://api.twitch.tv/helix/predictions'
        url = 'https://api.twitch.tv/helix/polls'
        data = {
            "broadcaster_id": self.oauth.broadcaster_id,
            "duration": 300,
        }
        data.update(self._get_random_prediction_outcomes())
        with self.session.post(url, json=data) as r:
            self.log.print(r.request.body)
            try:
                self.log.print(f"{r.json()}")
            except:
                self.log.print_err(r.content)
