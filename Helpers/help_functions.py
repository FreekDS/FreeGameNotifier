from datetime import datetime
import globals


def log(message):
    print(f"[{datetime.now().strftime('%b %d %Y %H:%M:%S')}]: {message}")


def insert_spaces(string):
    pattern = globals.CONF_GENERAL.get('space_placeholder')
    if not pattern:
        pattern = ' '
    return string.replace(pattern, ' ')


# TODO some date time related functions to convert to hours and stuff might be useful here
