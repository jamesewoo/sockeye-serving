import pytest
import serving.utils as utils


@pytest.fixture
def my_str():
    return 'Hello, world!'


@pytest.fixture
def my_data(my_str):
    return bytearray(my_str, encoding='utf-8')


def test_decode_bytes(my_str, my_data):
    assert my_str == utils.decode_bytes(my_data)


def test_get_text(my_str):
    assert utils.get_text({'body': my_str}) == my_str
    assert utils.get_text({'body': {'text': my_str}}) == my_str
    assert utils.get_text({'zzz': my_str}) is None
    assert utils.get_text({'body': {'zzz': my_str}}) is None


def test_get_file_data(my_str, my_data):
    assert utils.get_file_data({'body': my_data}) == my_data
    assert utils.get_file_data({'file': my_data}) == my_data
    assert utils.get_file_data({'data': my_data}) == my_data
    assert utils.get_file_data({'zzz': my_data}) is None
    assert utils.get_file_data({'body': 123}) is None
