import collections.abc
import re
from typing import List, Union

import globals


class NestedDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _deep_update(source, overrides):
        """
        https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        """
        for key, val in overrides.items():
            if isinstance(val, collections.abc.Mapping):
                tmp = NestedDict._deep_update(source.get(key, {}), val)
                source[key] = tmp
            elif isinstance(val, list):
                source[key] = (source.get(key, []) + val)
            else:
                source[key] = overrides[key]
        return source

    def deep_update(self, overrides) -> dict:
        return NestedDict._deep_update(self, overrides)

    def path_exists(self, path: List[str]) -> bool:
        source = self
        for key in path:
            if key in source:
                source = source[key]
            else:
                return False
        return True

    @staticmethod
    def build_from_path(path: List[str], value: Union[str, int, bool, list, dict]) -> dict:
        res = {path[-1]: value}
        for key in reversed(path[:-1]):
            res = {key: res}
        return res

    @staticmethod
    def from_dict(d: dict):
        return NestedDict(zip(list(d.keys()), list(d.values())))

    def to_dict(self) -> dict:
        return dict(zip(list(self.keys()), list(self.values())))

    def is_object(self, path: List[str]) -> bool:
        source = self
        for key in path:
            if key in source:
                source = source[key]
            else:
                return False
        return isinstance(source, list) or isinstance(source, dict)

    def delete_path(self, path, indexes: list or None = None):
        """
        https://stackoverflow.com/questions/63820322/delete-key-at-arbitrary-depth-in-nested-dictionary
        """
        source = self
        for key in path[:-1]:
            source = source[key]
        if isinstance(source[path[-1]], list):
            if indexes is not None:
                source[path[-1]] = [item for index, item in enumerate(source[path[-1]]) if index not in indexes]
            else:
                source[path[-1]] = list()
        else:
            del source[path[-1]]

    @staticmethod
    def parse_value(value: str, comprehend_list=True, forced_list_type=None):
        value = value.strip()
        if value in ['true', 'True']:
            return True
        elif value in ['false', 'False']:
            return False
        elif value.isnumeric():
            return int(value)
        elif re.match('\d+\.\d+', value):
            return float(value)
        elif value.startswith('[') and value.endswith(']') and comprehend_list:
            value = value.replace('[', '').replace(']', '')
            list_entries = value.split(',')
            value_result = list()
            for item in list_entries:
                parsed = NestedDict.parse_value(item)
                if forced_list_type:
                    if isinstance(parsed, forced_list_type):
                        value_result.append(parsed)
                else:
                    value_result.append(parsed)
            return value_result
        else:
            return NestedDict.insert_spaces(value)

    @staticmethod
    def insert_spaces(string):
        pattern = globals.CONF_GENERAL.get('space_placeholder')
        if not pattern:
            pattern = ' '
        return string.replace(pattern, ' ')
