import json
import os
import threading

USER_DATA_PATH = 'user_data/'
USER_CONFIG_PATH = f'{USER_DATA_PATH}config/'
MESSAGES_PATH = f'{USER_CONFIG_PATH}messages/'

mutex = threading.Lock()


# START: REFACTOR THIS SHIT (SPLIT INTO FILES AND MAKE A LIBRARY)

def write_def(f, data):
    f.write(data)


def write_json(f, data):
    json.dump(data, f, indent=2)


def read_def(f):
    return f.read()


def read_json(f):
    return json.load(f)

# END: REFACTOR THIS SHIT (SPLIT INTO FILES AND MAKE A LIBRARY)


func_map = {
    # '.ext': (read_method, write_method)
    '.json' : (read_json, write_json),
    # DEFAULT HAS TO BE AT THE END
    ''      : (read_def, write_def),
}


def get_func_tuple(filepath: str):
    for extension, func_tuple in func_map.items():
        if filepath.endswith(extension):
            break
    return func_tuple


def read(filepath: str):
    if not os.path.exists(filepath):
        return ''
    func = get_func_tuple(filepath)[0]
    with mutex:
        with open(filepath, 'r', encoding='utf-8') as f:
            return func(f)


def readint(filepath: str):
    str_val = read(filepath)
    try:
        return int(str_val)
    except:
        return 0


def write(filepath: str, data):
    func = get_func_tuple(filepath)[1]
    with mutex:
        with open(filepath, 'w', encoding='utf-8') as f:
            func(f, data)
