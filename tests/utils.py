import json
import os
from typing import Mapping


_TESTS_DIR_PATH = os.path.dirname(__file__)


def get_test_file_path(path: str) -> str:
    filepath = os.path.join(
        _TESTS_DIR_PATH,
        path,
    )
    return filepath


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


def read_test_file_json_dict(path: str) -> Mapping[str, object]:
    filepath = os.path.join(
        _TESTS_DIR_PATH,
        path,
    )
    with open(filepath, mode='rb') as file:
        content = json.load(file)

    if isinstance(content, Mapping):
        return content
    else:
        raise TypeError(
            f"Expected JSON file content to be a 'Mapping', not a '{content.__class__.__name__}'.",
        )
