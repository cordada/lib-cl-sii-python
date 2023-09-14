import base64
import binascii
from typing import Union


def clean_base64(value: Union[str, bytes]) -> bytes:
    """
    Force bytes and remove line breaks and spaces.

    Does not validate base64 format.

    :raises ValueError:
    :raises TypeError:

    """
    if isinstance(value, bytes):
        value_base64_bytes = value
    elif isinstance(value, str):
        try:
            value_base64_bytes = value.strip().encode(encoding='ascii', errors='strict')
        except UnicodeEncodeError as exc:
            raise ValueError("Only ASCII characters are accepted.", str(exc)) from exc
    else:
        raise TypeError("Value must be str or bytes.")

    # remove line breaks and spaces
    # warning: we may only remove characters that are not part of the standard base-64 alphabet
    #   (or any of its popular alternatives).
    value_base64_bytes_cleaned = (
        value_base64_bytes.replace(b'\n', b'')
        .replace(b'\r', b'')
        .replace(b'\t', b'')
        .replace(b' ', b'')
    )

    return value_base64_bytes_cleaned


def decode_base64_strict(value: Union[str, bytes]) -> bytes:
    """
    Strict conversion for str/bytes, tolerating only line breaks and spaces.

    :raises ValueError: non-base64 input or non-ASCII characters included

    """
    value_base64_bytes_cleaned = clean_base64(value)
    try:
        value_bytes = base64.b64decode(value_base64_bytes_cleaned, validate=True)
    except binascii.Error as exc:
        raise ValueError("Input is not a valid base64 value.", str(exc)) from exc
    return value_bytes


def validate_base64(value: Union[str, bytes]) -> None:
    """
    Validate that ``value`` is base64-encoded data.

    :raises ValueError:
    :raises TypeError:

    """
    decode_base64_strict(value)
