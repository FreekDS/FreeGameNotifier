import globals
from .ScraperBase import SiteScraper


class MicrosoftStore(SiteScraper):

    @staticmethod
    def get_store_url():
        return "https://www.microsoft.com/"

    @staticmethod
    def get_store_name():
        return "Microsoft Store"

    def get_author(self):
        publisher = self.html.find('div', id='publisher')
        if publisher is None:
            return None
        author = publisher.find('span')
        return author.text if author else None

    @staticmethod
    def get_store_icon_url():
        return globals.CONF_GENERAL.get('icons').get('microsoft')

    def get_game_image(self):
        picture = self.html.find('picture', id='dynamicImage_image_picture')
        if picture is None:
            return None
        img = picture.find('img')
        return img['src']

    def get_description(self):
        desc = self.html.find('p', class_='pi-product-description-text')
        return desc.text if desc else None

    def get_title(self) -> str:
        title = self.html.find('h1', id='DynamicHeading_productTitle')
        return title.text if title else None

    def is_free(self) -> bool:
        price = self.html.find('span', class_='price-disclaimer')
        return 'Free' in price.text if price else False
