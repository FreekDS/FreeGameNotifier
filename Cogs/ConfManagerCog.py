import globals
import re
import collections.abc

from discord.channel import DMChannel
from discord.ext import commands


def deep_update(source, overrides):
    """
    https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for key, val in overrides.items():
        if isinstance(val, collections.abc.Mapping):
            tmp = deep_update(source.get(key, {}), val)
            source[key] = tmp
        elif isinstance(val, list):
            source[key] = (source.get(key, []) + val)
        else:
            source[key] = overrides[key]
    return source


def path_exists(source, path):
    for key in path:
        if key in source:
            source = source[key]
        else:
            return False
    return True


def build_dict_from_path(path: list, value):
    res = {path[-1]: value}
    for key in reversed(path[:-1]):
        res = {key: res}
    return res


def is_object(source, path: list):
    for key in path:
        if key in source:
            source = source[key]
        else:
            return False
    return isinstance(source, list) or isinstance(source, dict)


def delete_path(source, path, indexes: list or None = None):
    """
    https://stackoverflow.com/questions/63820322/delete-key-at-arbitrary-depth-in-nested-dictionary
    """
    for key in path[:-1]:
        source = source[key]
    if isinstance(source[path[-1]], list):
        if indexes is not None:
            source[path[-1]] = [item for index, item in enumerate(source[path[-1]]) if index not in indexes]
        else:
            source[path[-1]] = list()
    else:
        del source[path[-1]]


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
            parsed = parse_value(item)
            if forced_list_type:
                if isinstance(parsed, forced_list_type):
                    value_result.append(parsed)
            else:
                value_result.append(parsed)
        return value_result
    else:
        return value


class ConfManagerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command('show-config', aliases=['sc'])
    @commands.is_owner()
    async def display_config(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            return
        conf_str = globals.CONF_GENERAL.as_json()
        await ctx.send(f"```json\n{conf_str}\n```")

    @commands.command('force-reload', aliases=['fr'])
    async def force_reload(self, ctx):
        globals.CONF_GENERAL.read_file()
        await ctx.send("Reloaded configuration")

    @commands.command('force-save', aliases=['fs'])
    async def force_save(self, ctx):
        globals.CONF_GENERAL.save(force=True)
        await ctx.send("Forced save of configuration")

    @commands.command('edit-config', aliases=['ec'])
    @commands.is_owner()
    async def edit_config(self, ctx, *args):
        if len(args) < 2:
            await ctx.send(
                'Usage: key [subkeys] value\nIn case of list, append to it using /a=new_value\n\tTo remove just '
                'use /r=index or /r=all or /r=index1,index2...\n'
                'In case of adding a value, use /new as final keyword\n"'
                'In case of removing a key, use /del as final keyword')
            return
        value = args[-1]
        keys = list(args[:-1])

        # TODO check for cleanup :)

        original = globals.CONF_GENERAL.get_content()

        if str(value).startswith('/a'):  # Append to list
            if not path_exists(original, keys):
                await ctx.send('Specified key path does not exist')
                return
            value = value.split('=', 1)[-1]
            value = parse_value(value)
            value = [value]
            diff = build_dict_from_path(keys, value)
            deep_update(original, diff)

        elif str(value).startswith('/r'):  # Remove from list
            if not path_exists(original, keys):
                await ctx.send('Specified key path does not exist')
                return
            if not is_object(original, keys):
                await ctx.send('Can only remove indices from a list')
                return
            value = value.split('=', 1)[-1]
            value = value.replace(' ', '')
            if value == 'all':
                value = None
            else:
                parsed = parse_value(value, forced_list_type=int)
                if isinstance(parsed, list):
                    value = parsed
                else:
                    value = [parsed]
            delete_path(original, keys, indexes=value)

        elif str(value).startswith('/del'):  # Delete entire key from nested dictionary
            if not path_exists(original, keys):
                await ctx.send('Specified key path does not exist')
                return
            delete_path(original, keys)

        elif str(value).startswith('/new'):  # Add a new key to a nested dictionary
            # Parse value
            value = keys[-1]
            diff = build_dict_from_path(keys[:-1], parse_value(value))
            deep_update(original, diff)

        else:  # Generic update in nested dictionary
            if not path_exists(original, keys):
                await ctx.send('Specified key path does not exist')
                return
            if is_object(original, list(keys)):
                await ctx.send('Cannot update objects that easily, use /new, /add or /r to alter objects')
                return
            diff = build_dict_from_path(keys, parse_value(value))
            deep_update(original, diff)

        globals.CONF_GENERAL.update_content(original)
        await ctx.invoke(self.bot.get_command('show-config'))


if __name__ == '__main__':
    source = {
        'test': 1,
        'geen_test': 2,
        'lijsten': {
            'hondjes': {
                'staarten': "neen",
                'hoofd': True
            }
        }
    }

    override = {
        'test': 69
    }

    delete_path(source, ['lijsten', 'hondjes', 'staarten'])

    print(source)
