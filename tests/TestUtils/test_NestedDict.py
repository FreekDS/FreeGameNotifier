import copy

import pytest

from Utils import NestedDict


@pytest.fixture
def sample_dict():
    d = {
        'nested1': {
            'field1': 1,
            'field2': True,
            'field3': 'yep'
        },
        'nested2': {
            'nested2-1': {
                'field1': 1,
                'field2': True,
                'field3': 'yep'
            }
        },
        'not-nested': True,
        'list': [1, 2, 3]
    }
    return NestedDict.from_dict(d)


def test_path_exists(sample_dict):
    assert sample_dict.path_exists(['nested1', 'field1'])
    assert sample_dict.path_exists(['nested1', 'field2'])
    assert sample_dict.path_exists(['nested1', 'field3'])
    assert sample_dict.path_exists(['nested2', 'nested2-1', 'field1'])
    assert sample_dict.path_exists(['nested2', 'nested2-1', 'field2'])
    assert sample_dict.path_exists(['nested2', 'nested2-1', 'field3'])
    assert sample_dict.path_exists(['not-nested'])
    assert sample_dict.path_exists(['list'])
    assert sample_dict.path_exists([])
    assert not sample_dict.path_exists(['nope'])
    assert not sample_dict.path_exists(['nope', 'njet'])


def test_deep_update(sample_dict: NestedDict):
    sample_dict.deep_update({
        'nested2': {
            'nested2-1': {
                'field1': 'changed'
            }
        }
    })
    assert not sample_dict.get('nested2').get('nested2-1').get('field1') == 1
    assert sample_dict.get('nested2').get('nested2-1').get('field1') == 'changed'

    sample_dict.deep_update({
        'nested1': {
            'new_field': 'new'
        }
    })

    assert sample_dict.path_exists(['nested1', 'new_field'])
    assert sample_dict.get('nested1').get('new_field') == 'new'

    sample_dict.deep_update({
        'nested1': True
    })

    assert sample_dict.get('nested1') is True

    old = copy.deepcopy(sample_dict)
    sample_dict.deep_update({})
    assert sample_dict == old


def test_build_from_path():
    new_dict = NestedDict.build_from_path([], 'nothing')
    assert new_dict == dict()

    new_dict = NestedDict.build_from_path(['simple'], True)
    assert new_dict == {'simple': True}

    new_dict = NestedDict.build_from_path(['simple'], 10.2)
    assert new_dict == {'simple': 10.2}

    new_dict = NestedDict.build_from_path(['simple'], 'yes')
    assert new_dict == {'simple': 'yes'}

    new_dict = NestedDict.build_from_path(['simple'], 10)
    assert new_dict == {'simple': 10}

    new_dict = NestedDict.build_from_path(['simple'], {'yese': True})
    assert new_dict == {'simple': {'yese': True}}

    new_dict = NestedDict.build_from_path(['depth1', 'depth2', 'depth3'], 'that\'s deep!')
    assert new_dict == {'depth1': {'depth2': {'depth3': 'that\'s deep!'}}}


def test_from_dict():
    a_dict = {
        'yep': 1,
        'yes': True,
        'deep': {
            'deeper': {
                'deepest': 5
            }
        }
    }
    nested = NestedDict.from_dict(a_dict)
    assert nested.get('yep') == a_dict.get('yep')
    assert nested.get('yes') == a_dict.get('yes')
    assert nested.get('deep').get('deeper').get('deepest') == a_dict.get('deep').get('deeper').get('deepest')


def test_to_dict(sample_dict):
    d = {
        'nested1': {
            'field1': 1,
            'field2': True,
            'field3': 'yep'
        },
        'nested2': {
            'nested2-1': {
                'field1': 1,
                'field2': True,
                'field3': 'yep'
            }
        },
        'not-nested': True,
        'list': [1, 2, 3]
    }
    assert d == sample_dict.to_dict()


def test_is_object(sample_dict):
    assert sample_dict.is_object(['nested1'])
    assert sample_dict.is_object(['nested2'])
    assert sample_dict.is_object(['nested2', 'nested2-1'])
    assert sample_dict.is_object(['list'])
    assert not sample_dict.is_object(['not-nested'])
    assert not sample_dict.is_object(['nested1', 'field1'])


def test_delete_path(sample_dict):
    old = copy.deepcopy(sample_dict)
    sample_dict.delete_path(['doesnt', 'exist'])
    assert sample_dict == old

    sample_dict.delete_path([])
    assert sample_dict == old

    sample_dict.delete_path(['not-nested'])
    assert sample_dict != old
    assert not sample_dict.path_exists(['not-nested'])
    assert sample_dict.get('not-nested') is None

    sample_dict.delete_path(['nested1', 'field1'])
    assert not sample_dict.path_exists(['nested1', 'field1'])
    assert sample_dict.get('nested1').get('field1') is None

    sample_dict.delete_path(['nested2', 'nested2-1'])
    assert not sample_dict.path_exists(['nested2', 'nested2-1'])

    sample_dict.delete_path(['list'], indexes=[1])
    assert sample_dict.path_exists(['list'])
    assert sample_dict.get('list') == [1, 3]

    sample_dict.delete_path(['list'])
    assert not sample_dict.path_exists(['list'])
    assert sample_dict.get('list') is None


def test_parse_value():
    import globals
    from dotenv import load_dotenv
    import os

    if not globals.initialized:
        load_dotenv()
        globals.init(os.getenv('DROPBOX_ACCESS_TOKEN'), True)

    assert NestedDict.parse_value('true') is True
    assert NestedDict.parse_value('True') is True
    assert NestedDict.parse_value('false') is False
    assert NestedDict.parse_value('False') is False

    assert NestedDict.parse_value('1235') == 1235
    assert NestedDict.parse_value('-10') == -10
    assert NestedDict.parse_value('0') == 0

    assert NestedDict.parse_value('-0.45') == -0.45
    assert NestedDict.parse_value('0.0') == 0.0
    assert isinstance(NestedDict.parse_value('0.0'), float)
    assert NestedDict.parse_value('1.2') == 1.2
    assert NestedDict.parse_value('1.0') == 1.0
    assert isinstance(NestedDict.parse_value('1.0'), float)

    assert isinstance(NestedDict.parse_value('[1,2,3]', comprehend_list=False), str)
    assert NestedDict.parse_value('[1,2,3]', comprehend_list=False) == '[1,2,3]'

    assert isinstance(NestedDict.parse_value('[1,2,3]'), list)
    assert NestedDict.parse_value('[1,2,3]') == [1, 2, 3]
    assert NestedDict.parse_value("[1, 2.3, True, false, yep]") == [1, 2.3, True, False, 'yep']

    assert NestedDict.parse_value("[1, 2.3, True, false, yep]", forced_list_type=bool) == [True, False]
