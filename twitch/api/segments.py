from .announcement import TwitchAnnouncement

import random
import utils


class TwitchSegments(TwitchAnnouncement):
    schedule_stream_start_time = 0
    scheduled_segments_counter = 0

    def __init__(self):
        super().__init__()

    def get_stream_scheduled_segments_page(self, cursor=None):
        url = 'https://api.twitch.tv/helix/schedule'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'after': cursor,
        }
        with self.session.get(url, params=params) as r:
            return r.json()

    def get_all_stream_scheduled_segments(self):
        json_data = self.get_stream_scheduled_segments_page()
        cursor = json_data['pagination']['cursor']
        while cursor:
            json_data = self.get_stream_scheduled_segments_page(cursor)
            cursor = json_data['pagination']['cursor']
            for entry in json_data['data']['segments']:
                self.print(entry['start_time'])

    def create_stream_schedule_segment(self):
        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.broadcaster_id
        }
        duration = random.randint(30, 60)
        start_time = utils.get_rfc3339_time(self.schedule_stream_start_time)
        self.schedule_stream_start_time += duration
        data = {
            'start_time': start_time,
            'timezone': 'America/New_York',
            'duration': duration,
            'is_recurring': True,
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 200:
                self.scheduled_segments_counter += 1
                self.print(f'creating a stream schedule {duration} minute segment at {start_time} ({self.scheduled_segments_counter})')
            elif r.status_code == 400 and r.json()['message'] == 'Segment cannot create overlapping segment':
                self.delete_all_stream_schedule_segments()
            else:
                self.print_err(r.content)

    def delete_stream_schedule_segment(self, id):
        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.broadcaster_id,
            'id': id,
        }
        with self.session.delete(url, params=params) as r:
            if r.status_code not in [204, 404]:
                self.print_err(r.content)
        return (r.status_code == 204)

    def _get_cursor_from_json(self, json_data: dict):
        try:
            cursor = json_data['pagination']['cursor']
        except:
            cursor = ''
        return cursor

    def delete_all_stream_schedule_segments(self):
        del_counter = 0
        self.print('deleting all scheduled stream segments...')
        json_data = self.get_stream_scheduled_segments_page()
        cursor = self._get_cursor_from_json(json_data)
        while cursor:
            json_data = self.get_stream_scheduled_segments_page(cursor)
            try:
                data_entries = json_data['data']['segments']
            except:
                break
            if self.scheduled_segments_counter == 0:
                self.scheduled_segments_counter = 'x'
            cursor = self._get_cursor_from_json(json_data)
            for entry in data_entries:
                if not self.delete_stream_schedule_segment(entry['id']):
                    cursor = ''
                    break
                del_counter += 1
            self.print(f'deleted scheduled stream segments: {del_counter}/{self.scheduled_segments_counter}')
        self.print(f'deleted all scheduled stream segments!')
        self.scheduled_segments_counter = 0
