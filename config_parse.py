import configparser
import os


def parse_config(filename='config.ini'):
    result = {}
    path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(path):
        raise FileNotFoundError('No config file found!')
    cp = configparser.ConfigParser()
    cp.read(path)
    for k, v in cp.items('APP'):
        if v.isdigit() or v.isdecimal():
            result[k] = int(v)
        else:
            result[k] = v
    return result
