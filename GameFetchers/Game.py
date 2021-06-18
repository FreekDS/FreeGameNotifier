import globals


class Game:
    def __init__(self, title, store_url, game_url, fetch_date, image, store_icon, store, description,
                 author):
        max_desc_size = globals.CONF_GENERAL.get('data').get('desc_size')

        description = description.replace('\n', '')
        if len(description) > max_desc_size:
            description = description[0:max_desc_size] + '...'

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
