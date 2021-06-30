import urllib.request
from abc import abstractmethod
from urllib.request import Request

from bs4 import BeautifulSoup


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
