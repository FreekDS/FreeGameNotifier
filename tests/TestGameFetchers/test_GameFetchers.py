import pytest
import globals
import os
from dotenv import load_dotenv
from GameFetchers.GameFetchers import RedditFetcher


@pytest.fixture
def rf():
    if not globals.initialized:
        load_dotenv()
        globals.init(os.getenv('DROPBOX_ACCESS_TOKEN'), True)
    rf = RedditFetcher("FreeGamesOnSteam")
    yield rf


@pytest.mark.asyncio
async def test_reddit_fetcher(rf):
    """Test __repr__ function"""
    assert rf.__repr__() == "RedditFetcher('FreeGamesOnSteam')"


@pytest.mark.asyncio
async def test_subreddit(rf):
    subreddit = await rf.subreddit
    assert subreddit is not None
    assert subreddit.display_name == 'FreeGamesOnSteam'
