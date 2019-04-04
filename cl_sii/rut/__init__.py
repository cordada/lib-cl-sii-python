"""
Utilities for dealing with Chile's RUT ("Rol Único Tributario").

The terms RUT and RUN ("Rol Único Nacional") may be used interchangeably but
only when the holder is a natural person ("persona natural"); a legal person
("persona jurídica") does not have a RUN.

RUT "canonical format": no dots ('.'), with dash ('-'), uppercase K e.g.
``'76042235-5'``, ``'96874030-K'``.

"""
import itertools
import random

from . import constants


class Rut:

    """
    Representation of a RUT.

    It verifies that the input is syntactically valid and, optionally, that the
    "digito verificador" is correct.

    It does NOT check that the value is within boundaries deemed acceptable by
    the SII (although the regex used does implicitly impose some) nor that the
    RUT has actually been assigned to some person or entity.

    >>> Rut('96874030-K')
    Rut('96874030-K')>
    >>> str(Rut('96874030-K'))
    '96874030-K'
    >>> Rut('96874030-K').digits
    '96874030'
    >>> Rut('96874030-K').dv
    'K'
    >>> Rut('96874030-K').canonical
    '96874030-K'
    >>> Rut('96874030-K').verbose
    '96.874.030-K'
    >>> Rut('96874030-K').digits_with_dots
    '96.874.030'

    >>> Rut('77879240-0') == Rut('77.879.240-0')
    True
    >>> Rut('96874030-K') == Rut('9.68.7403.0-k')
    True

    """

    def __init__(self, value: str, validate_dv: bool = False) -> None:
        """
        Constructor.

        :param value: a string that represents a syntactically valid RUT
        :param validate_dv: whether to validate that the RUT's
            "digito verificador" is correct

        :raises ValueError:
        :raises TypeError:

        """
        invalid_rut_msg = "Syntactically invalid RUT."

        if isinstance(value, Rut):
            value = value.canonical
        if not isinstance(value, str):
            raise TypeError("Invalid type.")

        clean_value = Rut.clean_str(value)
        match_obj = constants.RUT_CANONICAL_STRICT_REGEX.match(clean_value)
        if match_obj is None:
            raise ValueError(invalid_rut_msg, value)

        match_groups = match_obj.groupdict()
        self._digits = match_groups['digits']
        self._dv = match_groups['dv']

        if validate_dv:
            if Rut.calc_dv(self._digits) != self._dv:
                raise ValueError("RUT's \"digito verificador\" is incorrect.", value)

    ############################################################################
    # properties
    ############################################################################

    @property
    def canonical(self) -> str:
        return f'{self._digits}-{self._dv}'

    @property
    def verbose(self) -> str:
        return f'{self.digits_with_dots}-{self._dv}'

    @property
    def digits(self) -> str:
        return self._digits

    @property
    def digits_with_dots(self) -> str:
        """Return RUT digits with a dot ('.') as thousands separator."""
        # > The ',' option signals the use of a comma for a thousands separator.
        #   https://docs.python.org/3/library/string.html#format-specification-mini-language
        return '{:,}'.format(int(self.digits)).replace(',', '.')

    @property
    def dv(self) -> str:
        return self._dv

    ############################################################################
    # magic methods
    ############################################################################

    def __str__(self) -> str:
        return self.canonical

    def __repr__(self) -> str:
        return f"Rut('{self.canonical}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rut):
            return self.canonical == other.canonical
        return False

    def __hash__(self) -> int:
        # Objects are hashable so they can be used in hashable collections.
        return hash(self.canonical)

    ############################################################################
    # class methods
    ############################################################################

    @classmethod
    def clean_str(cls, value: str) -> str:
        # note: unfortunately `value.strip('.')` does not remove all the occurrences of '.' in
        #   'value' (only the leading and trailing ones).
        return value.strip().replace('.', '').upper()

    @classmethod
    def calc_dv(cls, rut_digits: str) -> str:
        """
        Calculate the "digito verificador" of a RUT's digits.

        >>> Rut.calc_dv('60910000')
        '1'
        >>> Rut.calc_dv('76555835')
        '2'
        >>> Rut.calc_dv('76177907')
        '9'
        >>> Rut.calc_dv('76369187')
        'K'
        >>> Rut.calc_dv('77879240')
        '0'
        >>> Rut.calc_dv('96874030')
        'K'

        """
        if rut_digits.strip().isdigit() is False:
            raise ValueError("Must be a sequence of digits.")

        # Based on:
        #   https://gist.github.com/rbonvall/464824/4b07668b83ee45121345e4634ebce10dc6412ba3
        s = sum(
            d * f
            for d, f
            in zip(map(int, reversed(rut_digits)), itertools.cycle(range(2, 8)))
        )
        result_alg = 11 - (s % 11)
        return {10: 'K', 11: '0'}.get(result_alg, str(result_alg))

    @classmethod
    def random(cls) -> 'Rut':
        """
        Generate a random RUT.

        Value will be within proper boundaries and "digito verificador"
        will be calculated appropriately i.e. it is not random.

        """
        rut_digits = str(random.randint(
            constants.RUT_DIGITS_MIN_VALUE,
            constants.RUT_DIGITS_MAX_VALUE))
        rut_dv = Rut.calc_dv(rut_digits)
        return Rut(f'{rut_digits}-{rut_dv}')
