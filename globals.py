import os

from Config import Config

CONF_GENERAL: Config
CONF_GUILDS: Config

initialized = False

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

HELP: dict


def get_help(name: str) -> str:
    global HELP
    return HELP.get(name, '')


def init(access_token, is_development):
    global CONF_GENERAL
    global CONF_GUILDS
    global HELP
    global initialized

    version = '-dev' if is_development else ''

    CONF_GENERAL = Config(access_token=access_token, conf_path=f'config{version}.json')
    CONF_GENERAL.read_file()

    CONF_GUILDS = Config(conf_path=f'guilds{version}.json')
    CONF_GUILDS.read_file()

    with open(f'{ROOT_DIR}/texts/help.txt', encoding='utf-8') as h_file:
        HELP = dict()
        lines = h_file.readlines()
        for line in lines:
            if line.strip().startswith('#') or '\n' == line:
                continue
            [key, value] = line.split('=')
            HELP[key.strip()] = value.strip()

    initialized = True


def save_all():
    global CONF_GENERAL
    global CONF_GUILDS
    CONF_GENERAL.save()
