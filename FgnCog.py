import asyncio

from discord import Embed, Colour

from GameFetchers import GameFetcher, RedditFetcher, CombinationFetcher, Game
from discord.ext import commands, tasks
from discord.channel import DMChannel
from discord.ext.commands import Context as CmdCtx
from config import SUBREDDITS, FREE_ICON


class FGNCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_source: GameFetcher = CombinationFetcher(
            *[RedditFetcher(sr) for sr in SUBREDDITS]
        )
        self.guild_daily_channels = {}

    @commands.command(name='free-games', aliases=['fg'])
    async def show_free_games(self, ctx):
        if self.data_source.update_required():
            msg = await ctx.send("Updating data.... (might take ~1 minute)")
        else:
            msg = None
        games = await self.data_source.get_free_games()
        if msg:
            await msg.delete()
        for game in games:
            await ctx.send(embed=self.create_embed(game))

    @commands.command(name='free-today', aliases=['ft'])
    async def free_today(self, ctx):
        today = self.data_source.get_daily_cached()
        if not today:
            await ctx.send("No new free games today, try again later!")
            return
        for g in self.data_source.get_daily_cached():
            await ctx.send(embed=self.create_embed(g))

    @commands.command(name='ping')
    async def pong(self, ctx: CmdCtx):
        embed = Embed(
            colour=Colour.from_rgb(255, 1, 255),
            description='This is the description :)',
            title='Een gratis spelletje!',
            url='http://google.com'
        )
        embed.set_author(name="Jefke", url="https://youtube.com",
                         icon_url="https://www.suunto.com/contentassets/d74dd2dd8ae040b9b73fd9ae62f0c7f1/icon-success.png")
        embed.set_footer(text="met voetjes uiteraard",
                         icon_url="https://www.suunto.com/contentassets/d74dd2dd8ae040b9b73fd9ae62f0c7f1/icon-success.png")

        embed.add_field(name="een veld", value="een hondje", inline=False)
        embed.add_field(name="een ander veld", value="een poesje", inline=True)
        embed.set_thumbnail(
            url="https://geryaal.nl/wp-content/upload_folders/geryaal.nl/2018/07/wat-is-een-thumbnail.jpg")
        embed.set_image(url="https://geryaal.nl/wp-content/upload_folders/geryaal.nl/2018/07/wat-is-een-thumbnail.jpg")

        await ctx.send(embed=embed)

    @commands.command(name='setup')
    async def setup_daily(self, ctx: CmdCtx):
        self.guild_daily_channels[ctx.guild] = ctx.channel
        if not self.daily_update.is_running():
            self.daily_update.start()

    @commands.command(name='toggle-loop', aliases=['tl'])
    @commands.is_owner()
    async def toggle_daily_update(self, ctx):
        if isinstance(ctx.channel, DMChannel):
            if self.daily_update.is_running():
                self.daily_update.cancel()
                await ctx.send("Stopped loop!")
            else:
                self.daily_update.start()
                await ctx.send("Started loop!")

    @commands.command(name='force-update', aliases=['fu'])
    @commands.is_owner()
    async def force_update(self, ctx):
        await self.data_source.daily_update()
        await ctx.send("Updated cache")

    @commands.command(name='broadcast', aliases=['bc', 'broodkast'])
    @commands.is_owner()
    async def broadcast(self, _, message):
        for channel in self.guild_daily_channels.values():
            await channel.send(f"[ADMIN]: {message}")

    @staticmethod
    def create_embed(game: Game):
        embed = Embed(
            title=game.title,
            description=game.description,
            url=game.game_url,
            colour=Colour.random()
        )
        embed.set_author(name=game.store, icon_url=game.store_icon, url=game.store_url)
        embed.add_field(name='Author', value=game.author)
        embed.set_image(url=game.image)
        embed.set_footer(icon_url=FREE_ICON, text="It's free real estate!!")
        return embed

    def cog_unload(self):
        self.daily_update.cancel()
        FGNCog.clean()

    @staticmethod
    def clean():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(RedditFetcher.clean())

    @tasks.loop(hours=24)
    async def daily_update(self):
        games = await self.data_source.daily_update()
        for channel in self.guild_daily_channels.values():
            for game in games:
                await channel.send(embed=self.create_embed(game))
