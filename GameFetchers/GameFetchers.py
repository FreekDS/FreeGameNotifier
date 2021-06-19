from abc import abstractmethod
from datetime import datetime, timedelta
from typing import List

import asyncpraw
import os
import globals
from WebScrapers import *
from Helpers import log
from .Game import Game


class GameFetcher:

    def __init__(self):
        self.cache: List[Game] = list()
        self.last_update = None
        self.daily_cache: List[Game] = list()
        self.last_daily_update = None

    @abstractmethod
    async def get_free_games(self, force=False) -> List[Game]:
        raise NotImplementedError()

    @abstractmethod
    async def clean(self, *args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def allowed_source(full_url: str) -> bool:
        for allowed in globals.CONF_GENERAL.get('data').get('sources'):
            if allowed in full_url:
                return True
        return False

    def get_daily_cached(self):
        return self.daily_cache

    async def daily_update(self):
        new_list = await self.get_free_games(True)

        def filter_not_free(g: Game):
            html = get_html(g.game_url)
            if still_free(html):
                return True
            return False

        def filter_outdated(g: Game):
            fetched_time = g.fetch_date
            seconds = (datetime.now() - fetched_time).total_seconds()
            minutes = seconds / 60
            return minutes / 60 <= 24

        self.daily_cache = list(filter(filter_outdated, self.daily_cache))
        self.daily_cache = list(filter(filter_not_free, self.daily_cache))
        cached_titles = [g.title for g in self.daily_cache]

        for game in new_list:
            title = game.title
            if title not in cached_titles:
                cached_titles.append(title)
                self.daily_cache.append(game)
        log("Updated daily cache!")
        return self.daily_cache

    def daily_update_required(self):
        if self.last_daily_update is None:
            return True
        duration: timedelta = (datetime.now() - self.last_update)
        minutes = duration.total_seconds() / 60
        return minutes / 60 >= 24

    def update_required(self):
        if self.last_update is None:
            return True
        elapsed_minutes = (datetime.now() - self.last_update).total_seconds() / 60
        return elapsed_minutes >= globals.CONF_GENERAL.get('data').get('refresh_rate')


class RedditFetcher(GameFetcher):
    REDDIT_INSTANCE = None

    @property
    def reddit(self):
        if RedditFetcher.REDDIT_INSTANCE is None:
            RedditFetcher.REDDIT_INSTANCE = asyncpraw.Reddit(
                client_id=os.getenv('REDDIT_ID'),
                client_secret=os.getenv('REDDIT_SECRET'),
                user_agent=globals.CONF_GENERAL.get('reddit').get('agent')
            )
        return RedditFetcher.REDDIT_INSTANCE

    def __init__(self, subreddit: str):
        super().__init__()
        self.subreddit_name = subreddit
        self._subreddit = None

    def __repr__(self):
        return f"RedditFetcher('{self.subreddit_name}')"

    @staticmethod
    async def clean(*args, **kwargs):
        if RedditFetcher.REDDIT_INSTANCE is not None:
            await RedditFetcher.REDDIT_INSTANCE.close()

    async def __aexit__(self, *args):
        await self.clean()

    @property
    async def subreddit(self):
        if self._subreddit is None:
            self._subreddit = await self.reddit.subreddit(self.subreddit_name)
        return self._subreddit

    async def get_free_games(self, force=False):
        if self.update_required() or force:
            free = []
            s_reddit = await self.subreddit
            async for s in s_reddit.hot(limit=globals.CONF_GENERAL.get('reddit').get('fetch_limit')):
                url = s.url
                if s.stickied or not self.allowed_source(url):
                    continue
                website_body = get_html(url)
                if still_free(website_body):
                    free.append(Game(
                        title=html_get(website_body, 'title'),
                        game_url=url,
                        fetch_date=datetime.now(),
                        author=html_get(website_body, 'author'),
                        description=html_get(website_body, 'description'),
                        image=html_get(website_body, 'game_image'),
                        store=html_get(website_body, 'store_name'),
                        store_icon=html_get(website_body, 'store_icon_url'),
                        store_url=html_get(website_body, 'store_url'),

                    ))
                    # TODO: get post date of reddit post, for daily update, posts cannot be older than 1 day
            self.last_update = datetime.now()
            self.cache = free
            log(f"Updated {self} cache!")
        return self.cache


class CombinationFetcher(GameFetcher):

    def __init__(self, *fetchers):
        super().__init__()
        self.fetchers: List[GameFetcher] = list(fetchers)

    async def get_free_games(self, force=False):
        all_games = dict()
        for fetcher in self.fetchers:
            fetched_games = await fetcher.get_free_games(force)
            for game in fetched_games:
                title = game.title
                if title not in all_games:
                    all_games[title] = game
        self.cache = all_games.values()
        if self.update_required() or force:
            self.last_update = datetime.now()
        return self.cache

    @staticmethod
    async def clean(*args, **kwargs):
        pass
