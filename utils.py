from enum import Enum, auto
import os
import random
import string
import sys
from time import time
import datetime


fake_time = datetime.datetime(2099, 1, 1, 0, 0, 0)

class WeekDay(Enum):
    Monday = 0
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()
    Saturday = auto()
    Sunday = auto()


def get_random_string(length):
    letters = string.printable
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def clear_terminal():
    os.system('cls')


def get_random_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        random_line = random.choice(lines)
        return random_line.strip()


def clamp_str(text, char_limit):
    encoded_text = text.encode()[:char_limit]  # Clamp the encoded text to a maximum of 25 bytes
    while len(encoded_text) > 0:
        try:
            encoded_text.decode()
            break
        except UnicodeDecodeError:
            encoded_text = encoded_text[:-1]
    return encoded_text.decode()  # Decode the clamped encoded text


def clamp_str_list(str_list, char_limit):
    if not str_list:
        return str_list
    return [clamp_str(entry, char_limit) for entry in str_list]


def get_current_time():
    return int(time())


def get_current_timestamp():
    return datetime.datetime.now().replace(microsecond=0)


def get_rfc3339_time(minute_offset: int = 0):
    duration = datetime.timedelta(minutes=minute_offset)
    offset_time = fake_time + duration
    return offset_time.isoformat("T") + "Z"


def rfc3339_to_offset(iso_str: str):
    return datetime.datetime.fromisoformat(iso_str.rstrip("Z"))

def get_day_of_week_from_rfc3339(iso_str: str) -> WeekDay:
    dt = datetime.datetime.fromisoformat(iso_str.rstrip("Z"))
    return WeekDay(dt.weekday())

def rfc3339_to_clocktime(iso_str: str) -> datetime.time:
    return rfc3339_to_offset(iso_str).time()

def restart_program():
    os.execvp(sys.executable, [sys.executable] + sys.argv)
