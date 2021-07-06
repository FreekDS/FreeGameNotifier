from .EpicScraper import EpicGames
from .MicrosoftScraper import MicrosoftStore
from .ScraperBase import SiteScraper
from .SquareEnixScraper import SquareEnix
from .SteamScraper import Steam

__all__ = ['still_free', 'get_html', 'html_get']


def get_html(full_url):
    return SiteScraper.generate_html(full_url)


def still_free(html):
    websites = [Steam(html), EpicGames(html), SquareEnix(html), MicrosoftStore(html)]
    return any(free_site() for free_site in websites)


def html_get(html, what):
    what = f"get_{what}"
    websites = [Steam(html), EpicGames(html), SquareEnix(html), MicrosoftStore(html)]
    for s in websites:
        if s.get_title() is not None:
            method = getattr(s, what)
            if method is None:
                raise AttributeError(f"Unknown attribute, no method 'get_{what}'")
            result = method()
            if result is not None:
                result = result.replace('\r', '')
                result = result.replace('\t', '')
                return result.strip()
    return ""


if __name__ == '__main__':
    # Todo write proper tests maybe

    # url_ms = "https://web.archive.org/web/20210610134429if_/https://www.microsoft.com/en-us/p/Tell-Me-Why-Chapters
    # -1" \ "-3/9NF83PRZK6K3?wa=wsignin1.0 " print(still_free(url_ms))
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
