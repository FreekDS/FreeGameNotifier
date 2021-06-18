import os
from discord.ext import commands
from dotenv import load_dotenv
from helpers import log
import globals

bot = commands.Bot(command_prefix='=')


# TODO: command to update prefix per guild (depends on persistent storage though)
# TODO: keep reddit post date in Game object for daily update
# TODO: add game release date?


@bot.event
async def on_ready():
    log(f"{bot.user} has joined {len(bot.guilds)} guilds")


if __name__ == '__main__':
    from Cogs import FGNCog

    load_dotenv()

    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

    globals.init(DROPBOX_TOKEN)

    bot.add_cog(FGNCog(bot))
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        FGNCog.clean()
        raise e
    finally:
        FGNCog.clean()
        globals.save_all()
