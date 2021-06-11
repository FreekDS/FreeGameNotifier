import os
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f"{bot.user} has joined {len(bot.guilds)} guilds")


if __name__ == '__main__':
    # TODO: initialize COGS
    from FgnCog import FGNCog

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot.add_cog(FGNCog(bot))
    try:
        bot.run(TOKEN)
    except Exception as e:
        FGNCog.clean()
        raise e
    finally:
        FGNCog.clean()
