from config import SQUARE_ENIX_ICON
from .ScraperBase import SiteScraper


class SquareEnix(SiteScraper):

    @staticmethod
    def get_store_url():
        return "https://store.na.square-enix-games.com"

    @staticmethod
    def get_store_name():
        return "Square Enix"

    def get_author(self):
        return "Square Enix"

    @staticmethod
    def get_store_icon_url():
        return SQUARE_ENIX_ICON

    def get_game_image(self):
        figure = self.html.find('figure', class_='product-boxshot-container')
        if not figure:
            return None
        figure = figure.find('img')
        if not figure:
            return None
        src_set = figure['data-srcset']
        return src_set.split()[0]

    def get_description(self):
        desc = self.html.find('div', class_='short-description')
        return desc.text if desc else None

    def get_title(self) -> str:
        title = self.html.find('h1', class_='product-title')
        return title.text if title else None

    def is_free(self) -> bool:
        price = self.html.find('span', class_='price')
        return '$0.00' in price.text if price else False
