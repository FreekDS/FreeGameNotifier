import discord
from discord.channel import DMChannel
from discord.embeds import Embed
from discord.ext import commands
from discord.ext.commands import has_permissions

import globals
from Utils import NestedDict


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
    @commands.is_owner()
    async def force_reload(self, ctx):
        globals.CONF_GENERAL.read_file()
        await ctx.send("✅ Reloaded configuration")

    @commands.command('force-save', aliases=['fs'])
    @commands.is_owner()
    async def force_save(self, ctx):
        globals.CONF_GENERAL.save(force=True)
        globals.CONF_GUILDS.save(force=True)
        await ctx.send("✅ Forced save of configuration")

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
                await ctx.send('❌ Specified key path does not exist')
                return
            value = value.split('=', 1)[-1]
            value = NestedDict.parse_value(value)
            value = [value]
            diff = NestedDict.build_from_path(keys, value)
            original.deep_update(diff)

        elif str(value).startswith('/r'):  # Remove from list
            if not original.path_exists(keys):
                await ctx.send('❌ Specified key path does not exist')
                return
            if not original.is_object(keys):
                await ctx.send('❌ Can only remove indices from a list')
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
                await ctx.send('❌ Specified key path does not exist')
                return
            original.delete_path(keys)

        elif str(value).startswith('/new'):  # Add a new key to a nested dictionary
            # Parse value
            value = keys[-1]
            diff = NestedDict.build_from_path(keys[:-1], NestedDict.parse_value(value))
            original.deep_update(diff)

        else:  # Generic update in nested dictionary
            if not original.path_exists(keys):
                await ctx.send('❌ Specified key path does not exist')
                return
            if original.is_object(keys):
                await ctx.send('❌ Cannot update objects that easily, use /new, /add or /r to alter objects')
                return
            diff = NestedDict.build_from_path(keys, NestedDict.parse_value(value))
            original.deep_update(diff)

        globals.CONF_GENERAL.update_content(original.to_dict())
        await ctx.invoke(self.bot.get_command('show-config'))

    @commands.command(name='guild-prefixes', aliases=['gps'])
    @commands.is_owner()
    async def show_guild_prefixes(self, ctx):
        guilds_json = globals.CONF_GUILDS.as_json()
        await ctx.send(f"```json\n{guilds_json}```")

    @commands.command(name='update-prefix', aliases=['up'])
    @commands.is_owner()
    async def update_prefix(self, ctx, guild_id, prefix):
        globals.CONF_GUILDS.set(guild_id, prefix, True)
        await ctx.send(f'✅ Updated {guild_id} prefix to {prefix}')

    @commands.command(name='delete-prefix', aliases=['delp'])
    @commands.is_owner()
    async def clear_prefix(self, ctx, guild_id):
        if globals.CONF_GUILDS.del_key(guild_id):
            await ctx.send(f'✅ Deleted guild {guild_id} prefix')
            return
        await ctx.send(f'❌ No such guild in config "{guild_id}"')

    @commands.command(name='fgn-prefix', aliases=['prefix'])
    @has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix):
        if isinstance(ctx.channel, DMChannel):
            await ctx.send('❌ Can only be executed from within a guild!')
            return
        globals.CONF_GUILDS.set(str(ctx.guild.id), prefix, True)
        await ctx.send(f'✅ Updated prefix to "{prefix}"')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Prefix recovery service
        if isinstance(message.channel, DMChannel):
            if message.content.lower().startswith('prefix '):
                guild_name = message.content.split('prefix ')[-1]
                guild_name = guild_name.strip()
                if not guild_name:
                    await message.channel.send('please provide a guild name after \'prefix\'')
                    return
                guild = discord.utils.get(self.bot.guilds, name=guild_name)
                if guild is None:
                    await message.channel.send(f'❌ Could not find a guild with the name \'{guild_name}\'')
                    return
                prefix = globals.CONF_GUILDS.get(str(guild.id))
                if prefix is None:
                    prefix = globals.CONF_GUILDS.get('default')
                await message.channel.send(f"✅ prefix for {guild_name} is '{prefix}'")
            elif not message.content.lower().startswith('='):
                await message.channel.send(f"Recover your prefix by sending 'prefix *guild_name*'")

    @commands.command(name='guild-id', aliases=['gid'])
    @commands.is_owner()
    async def get_guild_id_by_name(self, ctx, name):
        guild = discord.utils.get(self.bot.guilds, name=name)
        if guild is not None:
            await ctx.send(f'✅ Guild ID is {guild.id}')
        else:
            await ctx.send(f"❌ No such guild {name}")

    @commands.command(name='admin-help', aliases=['ahelp'], help=globals.get_help('admin-help'))
    @commands.is_owner()
    async def admin_help(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            return
        e = Embed(title="Admin command usage", description="This is mainly for configuration management",
                  color=discord.Color.red())
        e.add_field(name='edit-config (ec)',
                    value=f"A couple of use cases exist for edit-config\n\n"
                          f"**edit existing value**: ec key1 [key2, key3...] new_value\n\t"
                          f"this does only work for values, not for lists or objects\n"
                          f"**delete key**: ec key1 [key2, key3...] /del\n"
                          f"*add new key*: ec key1 [key2, key3...] /new\n"
                          f"**remove item from list**: ec key1 [key2, key3...] /r=index_type\n\t"
                          f"index_type can be 'all', a single index or a list of indices given in Python list format "
                          f"(no spaces are allowed)\n "
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
        e.add_field(name='guild-prefixes (gps)', value=f"Show the guild prefixes", inline=False)
        e.add_field(name='update-prefixes *guild_id* *prefix* (up)', value=f"Update the prefix for any guild",
                    inline=False)
        e.add_field(name='delete-prefix *guild_id* (delp)', value=f"Delete the prefix for a guild", inline=False)
        await ctx.send(embed=e)
