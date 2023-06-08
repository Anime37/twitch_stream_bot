import os
import random
import string


def get_random_string(length):
    letters = string.printable
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def clear_terminal():
    os.system('cls')
