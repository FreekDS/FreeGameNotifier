import os
from discord.ext import commands
from dotenv import load_dotenv
from Helpers import log
import globals

bot = commands.Bot(command_prefix='=')

# TODO: custom help command
# TODO: command to update prefix per guild (depends on persistent storage though)
# TODO: keep reddit post date in Game object for daily update
# TODO: add game release date?


@bot.event
async def on_ready():
    log(f"{bot.user} has joined {len(bot.guilds)} guilds")


if __name__ == '__main__':
    from Cogs import FGNCog, ConfManagerCog

    load_dotenv()

    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

    is_development = os.getenv('DEV', None) is not None

    globals.init(DROPBOX_TOKEN, is_development)

    bot.add_cog(FGNCog(bot))
    bot.add_cog(ConfManagerCog(bot))
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        FGNCog.clean()
        raise e
    finally:
        FGNCog.clean()
        globals.save_all()
