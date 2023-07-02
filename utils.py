import os
import random
import string


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
