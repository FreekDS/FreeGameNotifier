from discord import Embed, Colour
from discord.ext import commands

import globals
from NotificationBot import determine_prefix


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', help=globals.get_help('help'))
    async def help(self, ctx):
        prefix = determine_prefix(None, ctx.message)
        version = globals.CONF_GENERAL.get('version')

        embed = Embed(title="Commands", color=Colour.dark_gold(),
                      description=f'Use this bot to discover new free games!\nprefix: {prefix}')

        for command in self.bot.walk_commands():
            if not command.hidden and command.help is not None:
                for check in command.checks:
                    if not await check(ctx):
                        break
                else:
                    aliases = str()
                    for a in command.aliases[:-1]:
                        aliases += a + ', '
                    aliases += command.aliases[-1] if command.aliases else ''
                    c_name = f"{command.name} {'(' + aliases + ')' if aliases else ''}"
                    embed.add_field(name=c_name, value=command.help, inline=False)

        embed.set_footer(text=f'Version {version}')

        await ctx.send(embed=embed)
