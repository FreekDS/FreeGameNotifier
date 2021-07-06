from datetime import datetime

from GameFetchers.Game import Game


def test_game():
    game = Game(
        "title",
        "http://www.store.com",
        "http://www.game.com",
        datetime.now(),
        "http://image.com/image.png",
        "http://store_icon.com/png",
        "Game Store!",
        "Fun game to play and stuff",
        "Author: jefke van den abbeele"
    )
    rep = game.__repr__()
    assert rep == 'Game(title, http://www.game.com)'
