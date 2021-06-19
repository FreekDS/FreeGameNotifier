import globals
from .ScraperBase import SiteScraper


class Steam(SiteScraper):

    @staticmethod
    def get_store_url():
        return "https://store.steampowered.com/"

    @staticmethod
    def get_store_name():
        return "Steam"

    def get_author(self):
        devs = self.html.find('div', id='developers_list')
        return devs.text if devs else None

    def get_game_image(self):
        image = self.html.find('img', class_='game_header_image_full')
        return image['src'] if image else None

    def get_description(self):
        desc = self.html.find('div', class_='game_description_snippet')
        if desc:
            return desc.text.strip()
        else:
            return None

    @staticmethod
    def get_store_icon_url():
        return globals.CONF_GENERAL.get('icons').get('steam')

    def get_title(self) -> str:
        title = self.html.find('div', id='appHubAppName')
        if title is None:
            title = self.html.find('h2', class_='pageheader')
        return title.text if title else None

    def is_free(self) -> bool:
        discount_price = self.html.find('div', class_='discount_final_price')
        price = self.html.find('div', class_='game_purchase_price')

        options = [price.text] if price is not None else []
        if discount_price is not None:
            options.append(discount_price.text)

        for option in options:
            if option.strip() in ['0,--€', 'Free', 'Gratis', '$0.00']:
                return True
        return False
