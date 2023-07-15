from .x import X


import os
import fs
import random


class TwitchPredictions(X):
    def __init__(self):
        super().__init__()

    def get_random_prediction_outcomes(self):
        PREDICTIONS_PATH = 'predictions/'
        if not self.prediction_files:
            self.prediction_files = os.listdir(PREDICTIONS_PATH)
        prediction_list_path = f'{PREDICTIONS_PATH}{random.choice(self.prediction_files)}'
        random_prediction = fs.read(prediction_list_path)
        return random_prediction

    def create_prediction(self):
        url = 'https://api.twitch.tv/helix/predictions'
        url = 'https://api.twitch.tv/helix/polls'
        data = {
            "broadcaster_id": self.broadcaster_id,
            "duration": 300,
        }
        data.update(self.get_random_prediction_outcomes())
        with self.session.post(url, json=data) as r:
            self.print(r.request.body)
            try:
                self.print(f"{r.json()}")
            except:
                self.print_err(r.content)
