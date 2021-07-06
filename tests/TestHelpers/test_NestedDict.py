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
        'not-nested': True
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
    assert sample_dict.path_exists([])
    assert not sample_dict.path_exists(['nope'])
    assert not sample_dict.path_exists(['nope', 'njet'])


def test_deep_update():
    assert False


def test_build_from_path():
    assert False


def test_from_dict():
    assert False


def test_to_dict():
    assert False


def test_is_object():
    assert False


def test_delete_path():
    assert False


def test_parse_value():
    assert False


def test_insert_spaces():
    assert False
