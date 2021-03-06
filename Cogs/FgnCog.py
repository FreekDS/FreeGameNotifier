import asyncio

from discord import Embed, Colour
from discord.channel import DMChannel
from discord.ext import commands, tasks
from discord.ext.commands import Context as CmdCtx

import globals
from GameFetchers.GameFetchers import GameFetcher, RedditFetcher, CombinationFetcher, Game
from Helpers import log


class FGNCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_source: GameFetcher = CombinationFetcher(
            *[RedditFetcher(sr) for sr in globals.CONF_GENERAL.get('reddit').get('subreddits')]
        )
        self.guild_daily_channels = {}

    @commands.command(name='free-games', aliases=['fg'], help=globals.get_help('free-games'))
    async def show_free_games(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            await ctx.message.delete()
        if self.data_source.update_required():
            msg = await ctx.send("Updating data.... (might take ~1 minute)")
        else:
            msg = None
        games = await self.data_source.get_free_games()
        if msg:
            await msg.delete()
        for game in games:
            await ctx.send(embed=self.create_embed(game))

    @commands.command(name='free-today', aliases=['ft'], help=globals.get_help('free-today'))
    async def free_today(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            await ctx.message.delete()
        today = self.data_source.get_daily_cached()
        if not today:
            await ctx.send("No new free games today, try again later!")
            return
        for g in self.data_source.get_daily_cached():
            await ctx.send(embed=self.create_embed(g))

    @commands.command(name='ping', help=globals.get_help('ping'))
    async def pong(self, ctx: CmdCtx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000, 4)}ms")

    @commands.command(name='setup', help=globals.get_help('setup'))
    async def setup_daily(self, ctx: CmdCtx):
        if isinstance(ctx.channel, DMChannel):
            await ctx.send('❌ Can only be used in server channels')
            return
        await ctx.message.delete()
        self.guild_daily_channels[ctx.guild.id] = ctx.channel
        if not self.daily_update.is_running():
            self.daily_update.start()
        await ctx.send('✅ New free games will be posted here!')

    @commands.command(name='toggle-loop', aliases=['tl'], help=globals.get_help('toggle-loop'))
    @commands.is_owner()
    async def toggle_daily_update(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            await ctx.message.delete()
        if isinstance(ctx.channel, DMChannel):
            if self.daily_update.is_running():
                self.daily_update.cancel()
                await ctx.send("Stopped loop!")
            else:
                self.daily_update.start()
                await ctx.send("Started loop!")

    @commands.command(name='force-update', aliases=['fu'], help=globals.get_help('force-update'))
    @commands.is_owner()
    async def force_update(self, ctx):
        if not isinstance(ctx.channel, DMChannel):
            await ctx.message.delete()
        await self.data_source.get_free_games(True)
        await ctx.send("✅ Updated cache")

    @commands.command(name='broadcast', aliases=['bc', 'broodkast'], help=globals.get_help('broadcast'))
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
        if game.image.startswith('http') or game.image.startswith('https'):
            embed.set_image(url=game.image)
        else:
            print("hmm?")
        embed.set_footer(icon_url=globals.CONF_GENERAL.get('icons').get('free'), text="It's free real estate!!")
        return embed

    def cog_unload(self):
        self.daily_update.cancel()
        FGNCog.clean()

    @staticmethod
    def clean():
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.close()
        asyncio.run(RedditFetcher.clean())

    @tasks.loop(hours=24)
    async def daily_update(self):
        log("Daily update started!")
        games = await self.data_source.daily_update()
        for channel in self.guild_daily_channels.values():
            for game in games:
                await channel.send(embed=self.create_embed(game))
            if not games:
                await channel.send('No new games today')
