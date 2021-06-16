from config import EPIC_ICON
from .ScraperBase import SiteScraper


class EpicGames(SiteScraper):

    @staticmethod
    def get_store_url():
        return "https://www.epicgames.com"

    @staticmethod
    def get_store_name():
        return "Epic Games Store"

    def get_author(self):
        div = self.html.find('div', attrs={'data-component': 'Metadata'})
        if div is None:
            return None
        spans = div.find_all('span')
        if len(spans) == 2:
            return spans[-1].text
        else:
            return None

    @staticmethod
    def get_store_icon_url():
        return EPIC_ICON

    def get_game_image(self):
        picture_div = self.html.find('div', attrs={'data-testid': 'picture', 'data-component': 'Picture'})
        if picture_div is None:
            return None
        img = picture_div.find('img')
        return img['src'] if img else None

    def get_description(self):
        div = self.html.find('div', attrs={'data-component': 'LineClamp'})
        if div is None:
            div2 = self.html.find('div', attrs={'data-component': 'AboutSectionLayout'})
            return div2.text if div2 else None
        text = div.find('div')
        return text.text if text else None

    def get_title(self) -> str:
        title_parent = self.html.find('div', attrs={'data-component': 'PDPTitleHeader'})
        return title_parent.next.text if title_parent else None

    def is_free(self) -> bool:
        aside = self.html.find('aside')
        if aside is None:
            return False
        some_elements = aside.find_all('span', attrs={'data-component': 'Message'})
        for el in some_elements:
            if 'Free' in el.text:
                return True
        return False
