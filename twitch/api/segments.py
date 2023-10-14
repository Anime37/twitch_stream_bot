from datetime import time
import random
import utils

from cli import TagCLI
from fs import FS
from requests import Session
from word_utfer import TextUTFy

from .channel_info import ChannelInfo
from .oauth import TwitchOAuth


class TwitchSegments():
    session: Session
    cli: TagCLI
    fs: FS
    oauth: TwitchOAuth

    schedule_stream_start_time = 0
    scheduled_segments_counter = 0

    LAST_TIME_PATH = f'{FS.USER_DATA_PATH}last_segment_time'

    last_cursor = None

    def __init__(self, session: Session, cli: TagCLI, fs: FS, oauth: TwitchOAuth):
        self.session = session
        self.cli = cli
        self.fs = fs
        self.oauth = oauth
        self._init_last_segment_info()
        start_time = utils.get_rfc3339_time()
        self.start_weekday = utils.get_day_of_week_from_rfc3339(start_time)

    def _init_last_segment_info(self):
        last_segment_info = self.fs.read(self.LAST_TIME_PATH).split(' ')
        if len(last_segment_info) < 2:
            return
        self.schedule_stream_start_time = int(last_segment_info[0])
        self.scheduled_segments_counter = int(last_segment_info[1])

    def _get_stream_scheduled_segments_page(self, cursor=None):
        url = 'https://api.twitch.tv/helix/schedule'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'after': cursor,
        }
        with self.session.get(url, params=params) as r:
            return r.json()

    def get_all_stream_scheduled_segments(self):
        json_data = self._get_stream_scheduled_segments_page()
        cursor = json_data['pagination']['cursor']
        while cursor:
            json_data = self._get_stream_scheduled_segments_page(cursor)
            cursor = json_data['pagination']['cursor']
            for entry in json_data['data']['segments']:
                self.cli.print(entry['start_time'])

    def _store_last_segment_start_time(self):
        self.fs.write(self.LAST_TIME_PATH, f'{self.schedule_stream_start_time} {self.scheduled_segments_counter}')

    def _update_last_segment_info(self, add_to_counter: int):
        self.scheduled_segments_counter += add_to_counter
        self._store_last_segment_start_time()

    def _reset_last_segment_info(self):
        if self.scheduled_segments_counter > 0:
            self.scheduled_segments_counter = 0
            self.schedule_stream_start_time = 0
            self._store_last_segment_start_time()

    def create_stream_schedule_segment(self, channel_info: ChannelInfo, utfy: bool = False):
        MAX_TITLE_LEN = 140

        if utfy:
            title = TextUTFy(channel_info.title, 1, 2, False)[:MAX_TITLE_LEN]
        else:
            title = channel_info.title

        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id
        }
        duration = random.randint(30, 60)
        start_time = utils.get_rfc3339_time(self.schedule_stream_start_time)
        self.schedule_stream_start_time += duration
        start_weekday = utils.get_day_of_week_from_rfc3339(start_time)
        if self.schedule_stream_start_time > (24 * 60 * 7):
            self.schedule_stream_start_time = 60  # restart from day one + overlap protection
            self.last_cursor = None
        data = {
            'start_time': start_time,
            'timezone': 'America/New_York',
            'duration': duration,
            'is_recurring': True,
            'title': title,
        }
        with self.session.post(url, params=params, data=data) as r:
            if r.status_code == 200:
                self._update_last_segment_info(1)
                self.cli.print(f'creating a stream schedule {duration} minute segment at {start_time} ({start_weekday.name}) [{self.scheduled_segments_counter}]')
            elif r.status_code == 400:
                if (r.json()['message'] == "Segment cannot create overlapping segment"):
                    start_clocktime = utils.rfc3339_to_clocktime(start_time)
                    # TODO: fix overlap issues when going from one day to the next
                    if self.delete_scheduled_segments_from_start_time(start_weekday, start_clocktime, 10):
                        self.schedule_stream_start_time -= duration  # to not skip a segment
                else:
                    self.cli.print_err(r.content)
            else:
                self.cli.print_err(r.content)
        return (r.status_code == 200)

    def create_stream_schedule_segments(self, channel_info: ChannelInfo, utfy: bool = False, amount: int = 1):
        success_counter = 0
        fail_counter = 0
        while (success_counter < amount) and (fail_counter < 3):
            if self.create_stream_schedule_segment(channel_info, utfy):
                success_counter += 1
            else:
                fail_counter += 1

    def delete_stream_schedule_segment(self, id):
        url = 'https://api.twitch.tv/helix/schedule/segment'
        params = {
            'broadcaster_id': self.oauth.broadcaster_id,
            'id': id,
        }
        with self.session.delete(url, params=params) as r:
            if r.status_code not in [204, 404]:
                self.cli.print_err(r.content)
        return (r.status_code == 204)

    def _get_cursor_from_json(self, json_data: dict):
        try:
            cursor = json_data['pagination']['cursor']
        except:
            cursor = ''
        return cursor

    def _get_segments_entries_from_json(self, json_data: dict):
        try:
            data_entries = json_data['data']['segments']
        except:
            data_entries = []
        return data_entries

    def delete_all_scheduled_segments(self):
        finished = False
        total_deleted_cnt = 0
        while not finished:
            json_data = self._get_stream_scheduled_segments_page(self.last_cursor)
            data_entries = self._get_segments_entries_from_json(json_data)
            self.last_cursor = self._get_cursor_from_json(json_data)
            deleted_entries_cnt = 0
            for entry in data_entries:
                if not self.delete_stream_schedule_segment(entry['id']):
                    break
                deleted_entries_cnt += 1
            if deleted_entries_cnt > 0:
                total_deleted_cnt += deleted_entries_cnt
                self.cli.print(f'deleted scheduled stream segments: {total_deleted_cnt}/{self.scheduled_segments_counter}')
            finished = (deleted_entries_cnt == 0)
        self._reset_last_segment_info()

    def _check_weekday(self, entry: dict, start_weekday: utils.WeekDay):
        if not self.is_weekday_found:
            week_day = utils.get_day_of_week_from_rfc3339(entry['start_time'])
            self.is_weekday_found = (week_day == start_weekday)
        return self.is_weekday_found

    def _check_clocktime(self, entry: dict, start_clocktime: time):
        if not self.is_clocktime_found:
            found_start_clocktime = utils.rfc3339_to_clocktime(entry["start_time"])
            found_end_clocktime = utils.rfc3339_to_clocktime(entry["end_time"])
            self.is_clocktime_found = (found_start_clocktime <= start_clocktime <= found_end_clocktime)
        return self.is_clocktime_found

    def _is_starting_entry(self, entry: dict, start_weekday: utils.WeekDay, start_clocktime: time) -> bool:
        return self._check_weekday(entry, start_weekday) and self._check_clocktime(entry, start_clocktime)

    def delete_scheduled_segments_from_start_time(self, start_weekday: utils.WeekDay, start_clocktime: time, amount: int):
        FAIL_PROTECTION = 20

        finished = False
        deleting = False
        total_deleted_cnt = 0

        self.is_weekday_found = False
        self.is_clocktime_found = False

        self.cli.print(f'deleting {amount} segments')

        fail_cnt = 0

        while not finished and (fail_cnt < FAIL_PROTECTION):
            json_data = self._get_stream_scheduled_segments_page(self.last_cursor)
            data_entries = self._get_segments_entries_from_json(json_data)
            deleted_entries_cnt = 0
            for entry in data_entries:
                if not deleting:
                    deleting = self._is_starting_entry(entry, start_weekday, start_clocktime)
                    if not deleting:
                        continue
                if not self.delete_stream_schedule_segment(entry['id']):
                    finished = True
                    break
                deleted_entries_cnt += 1
                total_deleted_cnt += 1
                self._update_last_segment_info(-1)
                if total_deleted_cnt >= amount:
                    finished = True
                    break
            if not finished:
                self.last_cursor = self._get_cursor_from_json(json_data)
            fail_cnt += 1
        self.cli.print(f'deleted {total_deleted_cnt} scheduled stream segments')
        return finished
