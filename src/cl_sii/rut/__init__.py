"""
Utilities for dealing with Chile's RUT ("Rol Único Tributario").

The terms RUT and RUN ("Rol Único Nacional") may be used interchangeably but
only when the holder is a natural person ("persona natural"); a legal person
("persona jurídica") does not have a RUN.

RUT "canonical format": no dots ('.'), with dash ('-'), uppercase K e.g.
``'76042235-5'``, ``'96874030-K'``.

"""

from __future__ import annotations

import itertools
import random
import re
from typing import ClassVar

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

    INVALID_TYPE_ERROR_MESSAGE: ClassVar[str] = "Invalid type."
    """
    Error message used when the input type is not one of the accepted ones.
    """

    INVALID_RUT_ERROR_MESSAGE: ClassVar[str] = "Syntactically invalid RUT."
    """
    Error message used when the input is not a syntactically valid RUT.
    """

    INVALID_DV_ERROR_MESSAGE: ClassVar[str] = "RUT's \"digito verificador\" is incorrect."
    """
    Error message used when the RUT's "digito verificador" is incorrect.
    """

    def __init__(self, value: str | Rut, validate_dv: bool = False) -> None:
        """
        Constructor.

        :param value: a string that represents a syntactically valid RUT
        :param validate_dv: whether to validate that the RUT's
            "digito verificador" is correct

        :raises ValueError:
        :raises TypeError:

        """
        if isinstance(value, Rut):
            value = value.canonical
        if not isinstance(value, str):
            raise TypeError(self.INVALID_TYPE_ERROR_MESSAGE)

        clean_value = Rut.clean_str(value)
        match_obj = constants.RUT_CANONICAL_STRICT_REGEX.match(clean_value)
        if match_obj is None:
            raise ValueError(self.INVALID_RUT_ERROR_MESSAGE, value)

        match_groups = match_obj.groupdict()
        self._digits = match_groups['digits']
        self._dv = match_groups['dv']

        if validate_dv:
            self.validate_dv(raise_exception=True)

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

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Rut):
            return int(self.digits) < int(other.digits)
        else:
            return NotImplemented

    def __le__(self, other: object) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rut):
            return self.canonical == other.canonical
        return False

    def __hash__(self) -> int:
        # Objects are hashable so they can be used in hashable collections.
        return hash(self.canonical)

    ############################################################################
    # custom methods
    ############################################################################

    def validate_dv(self, raise_exception: bool = False) -> bool:
        """
        Whether the "digito verificador" of the RUT is correct.

        :param raise_exception: Whether to raise an exception if validation fails.
        :raises ValueError:
        """
        is_valid = self.calc_dv(self._digits) == self._dv
        if not is_valid and raise_exception:
            raise ValueError(self.INVALID_DV_ERROR_MESSAGE, self.canonical)
        return is_valid

    ############################################################################
    # class methods
    ############################################################################

    @classmethod
    def clean_str(cls, value: str) -> str:
        # note: unfortunately `value.strip('.')` does not remove all the occurrences of '.' in
        #   'value' (only the leading and trailing ones).
        clean_value = value.strip().replace('.', '').upper()
        # Remove leading zeros except if zero is the only digit, so we can accept the RUT '0-0'.
        leading_zero_free_value = re.sub(r'^0+(\d+)', r'\1', clean_value)
        return leading_zero_free_value

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
        s = sum(d * f for d, f in zip(map(int, reversed(rut_digits)), itertools.cycle(range(2, 8))))
        result_alg = 11 - (s % 11)
        return {10: 'K', 11: '0'}.get(result_alg, str(result_alg))

    @classmethod
    def random(cls) -> 'Rut':
        """
        Generate a random RUT.

        Value will be within proper boundaries and "digito verificador"
        will be calculated appropriately i.e. it is not random.

        """
        rut_digits = str(
            random.randint(
                constants.RUT_DIGITS_MIN_VALUE,
                constants.RUT_DIGITS_MAX_VALUE,
            )
        )
        rut_dv = Rut.calc_dv(rut_digits)
        return Rut(f'{rut_digits}-{rut_dv}')
