import unicodedata

import chardet


_DEFAULT_FILE_ENCODING = 'utf-8'


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
    with open(file_path, 'rb') as f:
        raw_data = f.read(512 * 1024)  # Read up to 512 KB
    result = chardet.detect(raw_data)

    encoding = result['encoding']
    if encoding is None or encoding == 'ascii':
        encoding = _DEFAULT_FILE_ENCODING
    return encoding
