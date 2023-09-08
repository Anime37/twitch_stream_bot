import os
import fs
import random
import utils

from dataclasses import dataclass
from requests import Session

from .logging import TwitchLogging
from .oauth import TwitchOAuth


@dataclass
class PredictionInfo():
    id: str = ''
    current_status: str = ''
    result_status: str = ''
    winning_outcome_id: str = ''

    def reset(self):
        self.__init__()


@dataclass
class TwitchPredictions():
    session: Session
    log: TwitchLogging
    oauth: TwitchOAuth

    PREDICTIONS_PATH = f'{fs.MESSAGES_PATH}predictions/'
    URL = 'https://api.twitch.tv/helix/predictions'

    prediction_files = []
    current_prediction = PredictionInfo()
    next_prediction_time = 0

    def _get_random_prediction_outcomes(self):
        if not self.prediction_files:
            self.prediction_files = os.listdir(self.PREDICTIONS_PATH)
        prediction_list_path = f'{self.PREDICTIONS_PATH}{random.choice(self.prediction_files)}'
        random_prediction = random.choice(fs.read(prediction_list_path)['predictions'])
        return random_prediction

    def _determine_outcome_result_status(self):
        if self.current_prediction.winning_outcome_id:
            self.current_prediction.result_status = 'RESOLVED'
        else:
            self.current_prediction.result_status = 'CANCELED'

    def _determine_winning_outcome_id(self, json_data: dict):
        if self.current_prediction.current_status != 'LOCKED':
            return False
        max_voters = 0
        for outcome in json_data['outcomes']:
            voters = outcome['users']
            if voters > max_voters:
                self.current_prediction.winning_outcome_id = outcome['id']
                max_voters = voters
        return True

    def _store_current_prediction_state(self, json_data: dict):
        self.current_prediction.id = json_data['id']
        self.current_prediction.current_status = json_data['status']
        if self._determine_winning_outcome_id(json_data):
            self._determine_outcome_result_status()

    def get_current_prediction(self):
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
        }
        with self.session.get(self.URL, params=data) as r:
            try:
                self._store_current_prediction_state(r.json()['data'][0])
            except:
                self.log.print_err(r.content)

    def _can_create_prediction(self, current_time):
        if (current_time <= self.next_prediction_time):
            return False
        self.end_current_prediction()
        return (self.current_prediction.id == '')

    def create_prediction(self):
        current_time = utils.get_current_time()
        if not self._can_create_prediction(current_time):
            self.log.print(f'next prediction in {(self.next_prediction_time - current_time)} seconds')
            return
        MIN_PREDICTION_PERIOD = (30)  # seconds
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'prediction_window': MIN_PREDICTION_PERIOD,
        }
        data.update(self._get_random_prediction_outcomes())
        with self.session.post(self.URL, json=data) as r:
            if r.status_code != 200:
                self.log.print_err(r.content)
                return
            self.current_prediction.id = r.json()['data'][0]['id']
            self.log.print(f'starting a prediction: {data["title"]}')
            self.next_prediction_time = current_time + MIN_PREDICTION_PERIOD + 1

    def _can_end_prediction(self) -> bool:
        self.get_current_prediction()
        return (self.current_prediction.result_status != '')

    def end_current_prediction(self):
        if not self._can_end_prediction():
            self.current_prediction.reset()
            return
        data = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'id': self.current_prediction.id,
            'status': self.current_prediction.result_status,
            'winning_outcome_id': self.current_prediction.winning_outcome_id,
        }
        with self.session.patch(self.URL, json=data) as r:
            try:
                self.current_prediction.reset()
            except:
                self.log.print_err(r.content)
