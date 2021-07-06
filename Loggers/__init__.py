from datetime import datetime


def log(message):
    print(f"[{datetime.now().strftime('%b %d %Y %H:%M:%S')}]: {message}")


__all__ = ['log']
