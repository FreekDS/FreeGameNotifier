from functools import wraps

import dropbox
import dropbox.exceptions
import dropbox.files
import json
from Helpers import log


def init_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0].initialized:
            return func(*args, **kwargs)
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
        self._content = dict()
        self.conf_path = conf_path
        self.initialized = False
        self._changed = False

    @init_required
    def get_content(self):
        return self._content

    @init_required
    def update_content(self, content):
        self._content = content
        self._changed = True

    def read_file(self):
        try:
            md, resp = Config.DBX.files_download(f'/{self.conf_path}')
            self._content = json.loads(resp.content)
            self.initialized = True
            log(f"/{self.conf_path} loaded from DropBox!")
        except dropbox.exceptions.ApiError as e:
            print(e)
        pass

    @init_required
    def has_changed(self):
        return self._changed

    @init_required
    def save(self, force=False):
        if self.has_changed() or force:
            content = json.dumps(self._content, indent=4).encode()
            try:
                res = Config.DBX.files_upload(content, f"/{self.conf_path}", dropbox.files.WriteMode.overwrite)
                self._changed = False if not force else self._changed
                if force:
                    log(f"Saved configuration file forcefully!")
                else:
                    log("Saved configuration file!")
            except dropbox.exceptions.ApiError as e:
                log(f"Error saving configuration file {e}")

    @init_required
    def get(self, key):
        return self._content.get(key)

    @init_required
    def keys(self):
        return self._content.keys()

    @init_required
    def set(self, key, value):
        if key not in self._content:
            log("No such key in configuration...")
            return False
        self._content[key] = value
        self._changed = True
        return True

    def as_json(self, indent=4):
        return json.dumps(self._content, indent=indent)

    def print_json(self, indent=4):
        print(self.as_json(indent))
