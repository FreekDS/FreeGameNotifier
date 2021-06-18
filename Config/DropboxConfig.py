from functools import wraps

import dropbox
import dropbox.exceptions
import dropbox.files
import json
from helpers import log


def init_required(func):
    @wraps(func)
    def wrapper(*args):
        if args[0].initialized:
            return func(*args)
        else:
            log("Config manager is not initialized, initialize first by calling read_file()!")

    return wrapper


class Config:
    DBX = None

    def __init__(self, access_token=None, conf_path='config.json'):
        if Config.DBX is None:
            if not access_token:
                raise AttributeError("Please provide an access token")
            try:
                Config.DBX = dropbox.Dropbox(access_token)
            except dropbox.exceptions.AuthError as e:
                raise e
        self.content = dict()
        self.conf_path = conf_path
        self.initialized = False
        self._changed = False

    def read_file(self):
        try:
            md, resp = Config.DBX.files_download(f'/{self.conf_path}')
            self.content = json.loads(resp.content)
            self.initialized = True
            log(f"/{self.conf_path} loaded from DropBox!")
        except dropbox.exceptions.ApiError as e:
            print(e)
        pass

    @init_required
    def has_changed(self):
        return self._changed

    @init_required
    def save(self):
        if self.has_changed():
            content = json.dumps(self.content, indent=4).encode()
            try:
                res = Config.DBX.files_upload(content, f"/{self.conf_path}", dropbox.files.WriteMode.overwrite)
                self._changed = False
                print(res)
            except dropbox.exceptions.ApiError as e:
                log(f"Error {e}")

    @init_required
    def get(self, key):
        return self.content.get(key)

    @init_required
    def keys(self):
        return self.content.keys()

    @init_required
    def set(self, key, value):
        if key not in self.content:
            log("No such key in configuration...")
            return False
        self.content[key] = value
        self._changed = True
        return True

    def print_json(self, indent=4):
        print(json.dumps(self.content, indent=indent))
