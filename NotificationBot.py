import os

from discord.ext import commands
from dotenv import load_dotenv

import globals
from Helpers import log


def determine_prefix(_, message):
    try:
        g_id = str(message.guild.id)
        prefix = globals.CONF_GUILDS.get(g_id)
        return prefix if prefix else globals.CONF_GUILDS.get('default')
    except Exception:
        default = globals.CONF_GUILDS.get('default')
        return default if default else '!'


bot = commands.Bot(command_prefix=determine_prefix)


# TODO: keep reddit post date in Game object for daily update
# TODO: add game release date?


@bot.event
async def on_ready():
    log(f"{bot.user} has joined {len(bot.guilds)} guilds")


@bot.event
async def on_guild_remove(guild):
    globals.CONF_GENERAL.del_key(guild.id)
    globals.CONF_GENERAL.save()


if __name__ == '__main__':

    load_dotenv()

    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

    is_development = os.getenv('DEV', None) is not None
    globals.init(DROPBOX_TOKEN, is_development)

    from Cogs import FGNCog, ConfManagerCog, HelpCog

    bot.remove_command('help')  # Remove default help command
    bot.add_cog(FGNCog(bot))
    bot.add_cog(ConfManagerCog(bot))
    bot.add_cog(HelpCog(bot))
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        FGNCog.clean()
        raise e
    finally:
        FGNCog.clean()
        globals.save_all()
