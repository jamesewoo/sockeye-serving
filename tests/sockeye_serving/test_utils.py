import pytest

from sockeye_serving import utils


@pytest.fixture
def my_str() -> str:
    return 'Hello, world!'


@pytest.fixture
def my_data(my_str: str) -> bytearray:
    return bytearray(my_str, encoding='utf-8')


@pytest.fixture
def my_args_file(tmp_path: str):
    p = tmp_path / 'args.txt'
    p.write_text('--abc def\n'
                 '--ab-bc  10\n'
                 '--de-fg\td_e_f\n'
                 '--g-h-i\n'
                 ' --f -1 ')
    return p


def test_decode_bytes(my_str, my_data):
    assert my_str == utils.decode_bytes(my_data)


def test_get_request(my_str):
    assert utils.get_request({'body': my_str}) == {'text': my_str}

    input = {'text': my_str}
    assert utils.get_request({'body': input}) == input

    input = {'text': my_str, 'constraints': ['abc']}
    assert utils.get_request({'body': input}) == input

    input = {'text': my_str, 'avoid': ['def']}
    assert utils.get_request({'body': input}) == input

    assert utils.get_request({'zzz': my_str}) is None
    assert utils.get_request({'zzz': {'text': my_str}}) is None
    assert utils.get_request({'body': {'zzz': my_str}}) is None


def test_get_file_data(my_str, my_data):
    assert utils.get_file_data({'body': my_data}) == my_data
    assert utils.get_file_data({'file': my_data}) == my_data
    assert utils.get_file_data({'data': my_data}) == my_data
    assert utils.get_file_data({'zzz': my_data}) is None
    assert utils.get_file_data({'body': 123}) is None


def test_read_sockeye_args(my_args_file):
    args = utils.read_sockeye_args(my_args_file)
    assert args == ['--abc', 'def', '--ab-bc', '10', '--de-fg', 'd_e_f', '--g-h-i', '--f', '-1']
