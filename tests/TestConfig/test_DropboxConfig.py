import os
from copy import deepcopy

import pytest
from dotenv import load_dotenv

from Config import Config


@pytest.fixture
def my_config():
    load_dotenv()
    db_config = Config(os.getenv('DROPBOX_ACCESS_TOKEN'), conf_path='config-test.json')
    db_config.read_file()
    old_content = deepcopy(db_config.get_content())
    yield db_config

    # cleanup
    db_config.update_content(old_content)
    assert db_config.get_content() == old_content
    db_config.save(True)


def test_get_content(my_config):
    content = my_config.get_content()
    assert content == {'author': 'Freek De Sagher',
                       'data': {'desc_size': 250,
                                'refresh_rate': 3600,
                                'sources': ['square-enix-games.com',
                                            'store.steampowered.com',
                                            'epicgames.com',
                                            'microsoft.com']},
                       'icons': {
                           'epic': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg'
                                   '/882px-Epic_Games_logo.svg.png',
                           'free': 'https://cdn3.iconfinder.com/data/icons/basicolor-shopping-ecommerce/24'
                                   '/222_free_gift-512.png',
                           'microsoft': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Microsoft_Store'
                                        '.svg/1200px',
                           'square_enix': 'https://cdn-prod.scalefast.com/public/assets/themes/squareenix-store-v3'
                                          '/images/favicons/favicon-16x16.png',
                           'steam': 'https://upload.wikimedia.org/wikipedia/commons/f/f5/SteamLogo.png'},
                       'reddit': {'agent': 'Windows:com.freegamesnotifier:v1-0-0-alpha (by u/dzerk21 '
                                           'and u/Pas-Op-Nen-Bot)',
                                  'fetch_limit': 15,
                                  'subreddits': ['FreeGamesOnSteam', 'FreeGameStuff']},
                       'space_placeholder': '$',
                       'version': 'v1.0.0-alpha'}


def test_update_content(my_config):
    new_content = {
        'new': 'content',
        'ha': True
    }
    old_content = my_config.get_content()
    my_config.update_content(new_content)
    assert my_config.get_content() != old_content
    assert my_config.get_content() == new_content


def test_read_file(my_config):
    # read() is already called in fixture
    assert my_config.initialized
    assert my_config.get_content() is not None
    assert len(my_config.keys()) != 0
    assert my_config != dict()


def test_has_changed_on_set(my_config):
    assert not my_config.has_changed()
    my_config.set('version', 'a new version')
    assert my_config.has_changed()


def test_has_changed_on_update_content(my_config):
    assert not my_config.has_changed()
    my_config.update_content({'new_content': True, 'testing': 'yes'})
    assert my_config.has_changed()


def test_has_changed_on_del_existing_key(my_config):
    assert not my_config.has_changed()
    assert 'version' in my_config.keys()
    my_config.del_key('version')
    assert my_config.has_changed()


def test_has_changed_on_del_non_existing_key(my_config):
    assert not my_config.has_changed()
    assert 'versione' not in my_config.keys()
    my_config.del_key('versione')
    assert not my_config.has_changed()


@pytest.mark.parametrize('force', [True, False])
def test_has_changed_after_save(my_config, force):
    my_config.set('version', 'test')
    assert my_config.has_changed() is True
    my_config.save(force=force)
    assert my_config.has_changed() is False if not force else True


def test_save(my_config):
    new_content = {'new_content': True}
    old_content = my_config.get_content()
    my_config.update_content(new_content)
    assert my_config.get_content() == new_content
    my_config.save()
    my_config.read_file()
    assert my_config.get_content() != old_content
    assert my_config.get_content() == new_content


def test_get(my_config):
    assert my_config.get('version') == 'v1.0.0-alpha'
    assert my_config.get('author') == 'Freek De Sagher'
    assert len(my_config.get('data').get('sources')) == 4
    assert my_config.get('data').get('desc_size') == 250


def test_keys(my_config):
    assert len(my_config.keys()) != 0
    for k in ['version', 'author', 'reddit', 'data', 'icons', 'space_placeholder']:
        assert k in my_config.keys()


def test_set(my_config):
    original = 'Freek De Sagher'
    new = 'Jefke Van Den Abbeele'
    assert my_config.get('author') == original
    my_config.set('author', new)
    assert my_config.get('author') != original
    assert my_config.get('author') == new


def test_del_existing_key(my_config):
    assert 'version' in my_config.keys()
    assert my_config.del_key('version')
    assert 'version' not in my_config.keys()


def test_del_non_existing_key(my_config):
    assert 'versione' not in my_config.keys()
    assert not my_config.del_key('versione')
    assert 'versione' not in my_config.keys()


def test_as_json(my_config):
    my_config.update_content({'simple': 'json'})
    json = my_config.as_json()
    assert json == '{\n    "simple": "json"\n}'


def test_print_json(capsys, my_config):
    capsys.readouterr()
    my_config.update_content({'simple': 'json'})
    my_config.print_json()
    captured = capsys.readouterr()
    assert captured.out == '{\n    "simple": "json"\n}\n'
