from config import DESCRIPTION_SIZE


class Game:
    def __init__(self, title, store_url, game_url, fetch_date, image, store_icon, store, description,
                 author):
        description = description.replace('\n', '')
        if len(description) > DESCRIPTION_SIZE:
            description = description[0:DESCRIPTION_SIZE] + '...'

        self.store_url = store_url
        self.image = image
        self.store_icon = store_icon
        self.store = store
        self.description = description
        self.title = title
        self.game_url = game_url
        self.fetch_date = fetch_date
        self.author = author

    def __repr__(self):
        return f"Game({self.title}, {self.game_url})"