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
