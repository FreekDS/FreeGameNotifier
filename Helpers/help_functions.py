from datetime import datetime


def log(message):
    print(f"[{datetime.now().strftime('%b %d %Y %H:%M:%S')}]: {message}")


# TODO some date time related functions to convert to hours and stuff might be useful here
