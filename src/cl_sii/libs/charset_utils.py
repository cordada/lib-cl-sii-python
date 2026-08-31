import codecs
import logging
import unicodedata
from typing import Optional, Sequence, Tuple

import chardet


logger = logging.getLogger(__name__)


_DEFAULT_FILE_ENCODING = 'utf-8'
"""Encoding assumed when there is no data to inspect."""

LOSSLESS_FALLBACK_ENCODING = 'latin-1'
"""
Encoding that decodes any byte sequence without failing.

Handy as a last resort for reading a file whose encoding could not be determined reliably.
"""

_FALLBACK_ENCODINGS: Sequence[str] = (
    'utf-8',
    # note: for text produced on Windows (the usual case for SII files), "cp1252" interprets the
    #   0x80-0x9F range correctly, unlike "latin-1".
    'cp1252',
    LOSSLESS_FALLBACK_ENCODING,
)
"""Candidates tried, in order, when there is no usable charset detection result."""

_BLOCKED_DETECTED_ENCODINGS = frozenset(
    # note: only the CJK encodings that the charset detector can actually return are listed. The
    #   ones it may return but Python does not know ("EUC-TW", "ISO-2022-CN") are discarded anyway
    #   because they can not be looked up.
    codecs.lookup(encoding).name
    for encoding in (
        'big5',
        'cp932',
        'cp949',
        'euc_jp',
        'euc_kr',
        'gb2312',
        'hz',
        'iso2022_jp',
        'iso2022_kr',
        'johab',
        'shift_jis',
    )
)
"""
Multi-byte CJK encodings, which are never a legitimate detection result here.

The files handled by this library contain Spanish text (Chilean documents). A CJK encoding is
always a false positive of the charset detector caused by a handful of non-ASCII bytes in an
otherwise ASCII file, and honoring it results in a :class:`UnicodeDecodeError` or in mojibake.
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

    return detect_encoding(raw_data)


def detect_encoding(raw_data: bytes) -> str:
    """
    Detect the encoding of ``raw_data``.

    Never raises: the last candidate is an encoding that decodes any byte sequence.

    The encoding is chosen in layers:

    1. The byte order mark, if there is one.
    2. UTF-8, if ``raw_data`` is valid UTF-8 (which includes pure ASCII).
    3. The result of the charset detector, but only if it is not one of
       :data:`_BLOCKED_DETECTED_ENCODINGS` and it actually decodes ``raw_data``.
    4. The first of :data:`_FALLBACK_ENCODINGS` that decodes ``raw_data``.

    .. note::
        The detector's confidence value is deliberately ignored: for the files handled by this
        library it discriminates in the wrong direction (correct "ISO-8859-1" results come with a
        confidence of ~0.66, while false positive CJK results come with a much higher one).

    >>> detect_encoding('Cesión'.encode('utf-8'))
    'utf-8'

    """
    if not raw_data:
        return _DEFAULT_FILE_ENCODING

    for bom, bom_encoding in _BOMS:
        if raw_data.startswith(bom):
            return bom_encoding

    # note: valid UTF-8 is strong evidence by itself, and much more reliable than the statistical
    #   detector, which for short texts tends to report some legacy 8-bit encoding that decodes the
    #   data into mojibake instead of failing.
    #   Null bytes are the exception: they are valid UTF-8 but they mean the data is most likely
    #   UTF-16/UTF-32 without a BOM, which only the detector can tell apart.
    if b'\x00' not in raw_data and _decodes_as(raw_data, 'utf-8'):
        return 'utf-8'

    detected_encoding = _get_detected_encoding(raw_data)
    if detected_encoding is not None:
        return detected_encoding

    for encoding in _FALLBACK_ENCODINGS:
        if _decodes_as(raw_data, encoding):
            return encoding

    raise Exception(
        "Programming error: none of the fallback encodings decoded the data.",
        _FALLBACK_ENCODINGS,
    )


def _get_detected_encoding(raw_data: bytes) -> Optional[str]:
    """
    Return the charset detector's result for ``raw_data``, if it is usable.

    :returns: the detected encoding, or ``None`` if there is none or it is not usable.

    """
    detected_encoding = chardet.detect(raw_data)['encoding']
    if detected_encoding is None:
        return None

    try:
        normalized_encoding = codecs.lookup(detected_encoding).name
    except LookupError:
        logger.warning("Detected encoding is unknown to Python: %s", detected_encoding)
        return None

    if normalized_encoding in _BLOCKED_DETECTED_ENCODINGS:
        logger.warning(
            "Ignoring detected encoding because it is not plausible for this kind of data: %s",
            detected_encoding,
        )
        return None

    if not _decodes_as(raw_data, normalized_encoding):
        logger.warning(
            "Ignoring detected encoding because it does not decode the data: %s",
            detected_encoding,
        )
        return None

    return normalized_encoding


def _decodes_as(raw_data: bytes, encoding: str) -> bool:
    """
    Return whether ``raw_data`` can be decoded with ``encoding``.

    ``raw_data`` may be a truncated sample of a larger byte sequence, so an incomplete multi-byte
    character at the end of it is not considered an error.

    """
    decoder = codecs.getincrementaldecoder(encoding)()
    try:
        decoder.decode(raw_data, False)
    except UnicodeDecodeError:
        return False

    return True
