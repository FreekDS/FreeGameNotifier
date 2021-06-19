from Config import Config

CONF_GENERAL: Config
CONF_GUILDS: Config


def init(access_token):
    global CONF_GENERAL
    global CONF_GUILDS

    CONF_GENERAL = Config(access_token=access_token, conf_path='config-dev.json')
    CONF_GENERAL.read_file()

    # CONF_GUILDS = Config(conf_path='guilds.json')
    # CONF_GUILDS.read_file()


def save_all():
    global CONF_GENERAL
    global CONF_GUILDS
    CONF_GENERAL.save()
