import codecs
import io
from typing import IO


# notes:
# - For streams and modes see 'io.open()'
# - Stream classes have a pretty strange 'typing'/ABC/inheritance/etc arrangement because,
#   among others, they are implemented in C.
# - Use `IO[X]` for arguments and `TextIO`/`BinaryIO` for return types (says GVR).
#   https://github.com/python/typing/issues/518#issuecomment-350903120


def with_mode_binary(stream: IO) -> bool:
    """
    Return whether ``stream`` is a binary stream (i.e. reads bytes).
    """
    result = False
    try:
        result = 'b' in stream.mode
    except AttributeError:
        if isinstance(stream, (io.RawIOBase, io.BufferedIOBase, io.BytesIO)):
            result = True

    return result


def with_mode_text(stream: IO) -> bool:
    """
    Return whether ``stream`` is a text stream (i.e. reads strings).
    """
    result = False
    try:
        result = 't' in stream.mode
    except AttributeError:
        if isinstance(stream, (io.TextIOBase, io.TextIOWrapper, io.StringIO)):
            result = True

    return result


def with_encoding_utf8(text_stream: IO[str]) -> bool:
    """
    Return whether ``text_stream`` is a text stream with encoding set to UTF-8.

    :raises TypeError: if ``text_stream`` is not a text stream

    """
    result = False

    if isinstance(text_stream, io.StringIO):
        # note: 'StringIO' saves (unicode) strings in memory and therefore doesn't have (or need)
        #   an encoding, which is fine.
        #   https://stackoverflow.com/questions/9368865/io-stringio-encoding-in-python3/9368909#9368909
        result = True
    else:
        try:
            text_stream_encoding: str = text_stream.encoding  # type: ignore
        except AttributeError as exc:
            raise TypeError("Value is not a text stream.") from exc
        if text_stream_encoding is None:
            # e.g. the strange case of `tempfile.SpooledTemporaryFile(mode='rt', encoding='utf-8')`
            pass
        else:
            try:
                text_stream_encoding_norm = codecs.lookup(text_stream_encoding).name
                result = text_stream_encoding_norm == 'utf-8'
            except LookupError:
                pass

    return result
