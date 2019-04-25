import os


_TESTS_DIR_PATH = os.path.dirname(__file__)


def read_test_file_bytes(path: str) -> bytes:
    filepath = os.path.join(
        _TESTS_DIR_PATH,
        path,
    )
    with open(filepath, mode='rb') as file:
        content = file.read()

    return content


def read_test_file_str_ascii(path: str) -> str:
    filepath = os.path.join(
        _TESTS_DIR_PATH,
        path,
    )
    with open(filepath, mode='rt', encoding='ascii') as file:
        content = file.read()

    return content


def read_test_file_str_utf8(path: str) -> str:
    filepath = os.path.join(
        _TESTS_DIR_PATH,
        path,
    )
    with open(filepath, mode='rt', encoding='utf8') as file:
        content = file.read()

    return content
