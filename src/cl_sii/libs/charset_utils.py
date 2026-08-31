import codecs
import unicodedata
from typing import Sequence, Tuple


_DEFAULT_FILE_ENCODING = 'utf-8'
"""Encoding assumed when there is no data to inspect."""

LOSSLESS_FALLBACK_ENCODING = 'latin-1'  # ISO-8859-1.
"""
Encoding that decodes any byte sequence without failing.

Handy as a last resort for reading a file whose encoding could not be determined reliably.
"""

_CANDIDATE_ENCODINGS: Sequence[str] = (
    'utf-8',
    # note: for text produced on Windows (the usual case for SII files), "cp1252" interprets the
    #   0x80-0x9F range correctly, unlike "latin-1".
    'cp1252',
    # note: "latin-1" decodes any byte sequence, so it guarantees a result.
    LOSSLESS_FALLBACK_ENCODING,
)
"""
Encodings tried, in order, until one of them decodes the data.

The files handled by this library contain Spanish text (Chilean documents), so this covers every
encoding they are known to come in. For that kind of text "cp1252" and "latin-1" are equivalent
anyway: they share the whole 0xA0-0xFF range, where the accented characters are.
"""

_BOMS: Sequence[Tuple[bytes, str]] = (
    # warning: order matters, the UTF-32 BOMs start with the UTF-16 ones.
    (codecs.BOM_UTF32_LE, 'utf-32'),
    (codecs.BOM_UTF32_BE, 'utf-32'),
    (codecs.BOM_UTF8, 'utf-8-sig'),
    (codecs.BOM_UTF16_LE, 'utf-16'),
    (codecs.BOM_UTF16_BE, 'utf-16'),
)
"""Byte order marks and the encoding each one implies."""

_DETECTION_SAMPLE_SIZE = 512 * 1024
"""Maximum number of bytes read from a file in order to detect its encoding."""


def clean_unicode(value: str) -> str:
    """
    Normalize and compose a unicode string.

    Handy when dealing with text that was transmitted/stored encoded
    in legacy encoding such as "Windows-1252".

    NFKC ("Normalization Form Compatibility Composition") will normalize
    characters that **may look different**, but are semantically the same
    as others.

    .. warning::
        NFKC was explicitly chosen over NFD, NFC and NFKD.

    .. seealso::
        https://docs.python.org/3/howto/unicode.html#comparing-strings

    .. seealso::
        https://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms

    .. seealso::
        https://www.fileformat.info/info/unicode/char/00c9/index.htm

    >>> clean_unicode('La \u00e9lite y\xa0la Vergüenza')
    'La élite y la Vergüenza'

    >>>> print('\u00c9', '\u0045\u0301')
    É É
    >>> '\u00c9' == 'É', '\u0045\u0301' == 'É'
    (True, False)
    >>> len('\u00c9'), len( '\u0045\u0301')
    (1, 2)
    >>> '\u00c9' == '\N{LATIN CAPITAL LETTER E WITH ACUTE}'
    True
    >>> '\u0045\u0301' == '\N{LATIN CAPITAL LETTER E}\N{COMBINING ACUTE ACCENT}'
    True
    >>> clean_unicode('\u0045\u0301') == 'É' == '\N{LATIN CAPITAL LETTER E WITH ACUTE}'
    True

    """
    return unicodedata.normalize('NFKC', value)


def detect_file_encoding(file_path: str) -> str:
    """
    Detect the encoding of the text file at ``file_path``.

    Only the first :data:`_DETECTION_SAMPLE_SIZE` bytes of the file are inspected, so the result is
    not guaranteed to decode the rest of the file: the caller must be prepared to handle a
    :class:`UnicodeDecodeError` while reading.

    .. seealso:: :func:`detect_encoding`

    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(_DETECTION_SAMPLE_SIZE)

    # note: 'read' returns fewer bytes than requested only at the end of the file.
    is_sample = len(raw_data) == _DETECTION_SAMPLE_SIZE

    return detect_encoding(raw_data, is_sample=is_sample)


def detect_encoding(raw_data: bytes, is_sample: bool = False) -> str:
    """
    Detect the encoding of ``raw_data``.

    Never raises: the last candidate is an encoding that decodes any byte sequence.

    :param is_sample:
        Whether ``raw_data`` is only the beginning of a larger byte sequence. If it is, an
        incomplete multi-byte character at the end of it is not considered a decoding error,
        because the rest of that character is in the part that was left out. In that case the
        returned encoding is guaranteed to decode the whole sequence, but not necessarily
        ``raw_data`` on its own.

    The encoding is chosen in layers:

    1. The byte order mark, if there is one.
    2. The first of :data:`_CANDIDATE_ENCODINGS` that decodes ``raw_data``. Pure ASCII is decoded
       by the first candidate, UTF-8.

    .. note::
        UTF-16 and UTF-32 are recognized only by their byte order mark. Without one they are
        indistinguishable from other encodings without a statistical guess, which is deliberately
        not made here: a wrong guess yields mojibake silently, whereas a file read with the wrong
        encoding fails loudly further down, when its CSV headers do not match.

    >>> detect_encoding('Cesión'.encode('utf-8'))
    'utf-8'

    """
    if not raw_data:
        return _DEFAULT_FILE_ENCODING

    for bom, bom_encoding in _BOMS:
        if raw_data.startswith(bom):
            return bom_encoding

    for encoding in _CANDIDATE_ENCODINGS:
        if _decodes_as(raw_data, encoding, is_sample):
            return encoding

    raise RuntimeError(
        "Programming error: none of the candidate encodings decoded the data.",
        _CANDIDATE_ENCODINGS,
    )


def _decodes_as(raw_data: bytes, encoding: str, is_sample: bool = False) -> bool:
    """
    Return whether ``raw_data`` can be decoded with ``encoding``.

    If ``is_sample`` is true, ``raw_data`` is only the beginning of a larger byte sequence, so an
    incomplete multi-byte character at the end of it is not considered an error.

    """
    decoder = codecs.getincrementaldecoder(encoding)()
    try:
        decoder.decode(raw_data, not is_sample)
    except UnicodeDecodeError:
        return False

    return True
