import globals
import discord

from discord.channel import DMChannel
from discord.embeds import Embed
from discord.ext import commands
from Helpers import NestedDict


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
                'use /r=index or /r=all or /r=[index1,index2]...\n'
                'In case of adding a value, use /new as final keyword\n"'
                'In case of removing a key, use /del as final keyword')
            return
        value = args[-1]
        keys = list(args[:-1])

        original: NestedDict = NestedDict.from_dict(globals.CONF_GENERAL.get_content())

        if str(value).startswith('/a'):  # Append to list
            if not original.path_exists(keys):
                await ctx.send('Specified key path does not exist')
                return
            value = value.split('=', 1)[-1]
            value = NestedDict.parse_value(value)
            value = [value]
            diff = NestedDict.build_from_path(keys, value)
            original.deep_update(diff)

        elif str(value).startswith('/r'):  # Remove from list
            if not original.path_exists(keys):
                await ctx.send('Specified key path does not exist')
                return
            if not original.is_object(keys):
                await ctx.send('Can only remove indices from a list')
                return
            value = value.split('=', 1)[-1]
            value = value.replace(' ', '')
            if value == 'all':
                value = None
            else:
                parsed = NestedDict.parse_value(value, forced_list_type=int)
                if isinstance(parsed, list):
                    value = parsed
                else:
                    value = [parsed]
            original.delete_path(keys, indexes=value)

        elif str(value).startswith('/del'):  # Delete entire key from nested dictionary
            if not original.path_exists(keys):
                await ctx.send('Specified key path does not exist')
                return
            original.delete_path(keys)

        elif str(value).startswith('/new'):  # Add a new key to a nested dictionary
            # Parse value
            value = keys[-1]
            diff = NestedDict.build_from_path(keys[:-1], NestedDict.parse_value(value))
            original.deep_update(diff)

        else:  # Generic update in nested dictionary
            if not original.path_exists(keys):
                await ctx.send('Specified key path does not exist')
                return
            if original.is_object(keys):
                await ctx.send('Cannot update objects that easily, use /new, /add or /r to alter objects')
                return
            diff = NestedDict.build_from_path(keys, NestedDict.parse_value(value))
            original.deep_update(diff)

        globals.CONF_GENERAL.update_content(original.to_dict())
        await ctx.invoke(self.bot.get_command('show-config'))

    @commands.command(name='admin-help', aliases=['ahelp'])
    @commands.is_owner()
    async def admin_help(self, ctx):
        e = Embed(title="Admin command usage", description="This is mainly for configuration management",
                  color=discord.Color.red())
        e.add_field(name='edit-config (ec)',
                    value=f"A couple of use cases exist for edit-config\n\n"
                          f"**edit existing value**: ec key1 [key2, key3...] new_value\n\t"
                          f"this does only work for values, not for lists or objects\n"
                          f"**delete key**: ec key1 [key2, key3...] /del\n"
                          f"*add new key*: ec key1 [key2, key3...] /new\n"
                          f"**remove item from list**: ec key1 [key2, key3...] /r=index_type\n\t"
                          f"index_type can be 'all', a single index or a list of indices given in Python list format (no spaces are allowed)\n"
                          f"**append value to list**: ec key1 [key2, key3...] /a=value\n\t"
                          f"the value can be a list, string, boolean, integer or a float\n\n"
                          f"Note: to use spaces, use the space placeholder. See the config for the placeholder\n",
                    inline=False)
        e.add_field(name='force-save (fs)',
                    value=f"Force save the configuration file to DropBox", inline=False)
        e.add_field(name='force-reload (fr)',
                    value='Force reload the configuration file from DropBox', inline=False)
        e.add_field(name='show-config (sc)',
                    value='Show the configuration file', inline=False)
        await ctx.send(embed=e)
