import urllib.request
from abc import abstractmethod
from urllib.request import Request
from bs4 import BeautifulSoup
from config import MICROSOFT_ICON, EPIC_ICON, STEAM_ICON, SQUARE_ENIX_ICON

__all__ = ['still_free', 'get_html', 'get_title', 'html_get']


class SiteScraper:

    @staticmethod
    def generate_html(url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        req.add_header('Cookie', "HAS_ACCEPTED_AGE_GATE_ONCE=true")
        html = urllib.request.urlopen(req).read().decode('utf-8')
        return BeautifulSoup(html, 'html.parser')

    def __init__(self, html):
        self.html = html

    @staticmethod
    @abstractmethod
    def get_store_name():
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_store_url():
        raise NotImplementedError()

    @abstractmethod
    def get_title(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def is_free(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_author(self):
        raise NotImplemented()

    @staticmethod
    @abstractmethod
    def get_store_icon_url():
        raise NotImplemented()

    @abstractmethod
    def get_game_image(self):
        raise NotImplemented()

    @abstractmethod
    def get_description(self):
        raise NotImplemented()

    def __call__(self, *args, **kwargs):
        return self.is_free()


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
        return STEAM_ICON

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
        return MICROSOFT_ICON

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


def get_html(full_url):
    return SiteScraper.generate_html(full_url)


def still_free(html):
    websites = [Steam(html), EpicGames(html), SquareEnix(html), MicrosoftStore(html)]
    return any(free_site() for free_site in websites)


def get_title(html):
    websites = [Steam(html), EpicGames(html), SquareEnix(html), MicrosoftStore(html)]
    for s in websites:
        title = s.get_title()
        if title:
            return title
    return None


def html_get(html, what):
    what = f"get_{what}"
    websites = [Steam(html), EpicGames(html), SquareEnix(html), MicrosoftStore(html)]
    for s in websites:
        if s.get_title() is not None:
            method = getattr(s, what)
            if method is None:
                raise AttributeError(f"Unknown attribute, no method '{what}'")
            result = method()
            if result is not None:
                result = result.replace('\r', '')
                result = result.replace('\t', '')
                return result.strip()
    return ""


if __name__ == '__main__':
    # Todo write proper tests maybe

    # url_ms = "https://web.archive.org/web/20210610134429if_/https://www.microsoft.com/en-us/p/Tell-Me-Why-Chapters-1" \
    #          "-3/9NF83PRZK6K3?wa=wsignin1.0 "
    # print(still_free(url_ms))
    #
    # url_steam = "https://web.archive.org/web/20210610135133/https://store.steampowered.com/sub/588737/"
    # print(still_free(url_steam))

    url_epic = "https://web.archive.org/web/20210610155350/https://www.epicgames.com/store/en-US/p/genshin-impact"
    url_epic = 'https://www.epicgames.com/store/en-US/p/genshin-impact'
    html = get_html(url_epic)
    d = EpicGames(html).get_description()
    print(EpicGames(html).get_description())

    # url_steam = "https://store.steampowered.com/app/613900/Museum_of_Other_Realities/"
    # html = get_html(url_steam)
    # desc = Steam(html).get_description()
    # print(Steam(html).get_description())
