from __future__ import annotations

import unittest
from typing import Sequence, Tuple

from cl_sii.dte.constants import TipoDte
from cl_sii.extras.dj_url_converters import RutConverter, TipoDteConverter
from cl_sii.rut import Rut


class RutConverterTest(unittest.TestCase):
    """
    Tests for :class:`RutConverter`.
    """

    def test_regex(self) -> None:
        for rut_str in (
            '60805000-0',
            '78773510-K',
            '123456-0',
            '123-6',
            '1-9',
            '6-K',
        ):
            self.assertRegex(rut_str, RutConverter.regex)

    def test_regex_matches_leading_zeroes(self) -> None:
        for rut_str in ('001-9', '000006-K', '0123456-0'):
            self.assertRegex(rut_str, RutConverter.regex)

    def test_regex_matches_uppercase_and_lowercase(self) -> None:
        self.assertRegex('6-K', RutConverter.regex)
        self.assertRegex('6-k', RutConverter.regex)

    def test_to_python(self) -> None:
        obj = RutConverter()

        test_values: Sequence[Tuple[str, Rut]] = [
            ('60805000-0', Rut('60805000-0')),
            ('78773510-K', Rut('78773510-K')),
            ('123456-0', Rut('123456-0')),
            ('1-9', Rut('1-9')),
            ('01-9', Rut('1-9')),
            ('6-k', Rut('6-K')),
        ]

        for string_test_value, python_test_value in test_values:
            self.assertEqual(obj.to_python(string_test_value), python_test_value)

    def test_to_url(self) -> None:
        obj = RutConverter()

        test_values: Sequence[Tuple[Rut, str]] = [
            (Rut('60805000-0'), '60805000-0'),
            (Rut('78773510-K'), '78773510-K'),
            (Rut('123456-0'), '123456-0'),
            (Rut('1-9'), '1-9'),
        ]

        for python_test_value, string_test_value in test_values:
            self.assertEqual(obj.to_url(python_test_value), string_test_value)


class TipoDteConverterTest(unittest.TestCase):
    """
    Tests for :class:`TipoDteConverter`.
    """

    def test_regex(self) -> None:
        for tipo_dte_str in (
            '33',
            '34',
            '43',
            '46',
            '52',
            '56',
            '61',
            '110',
        ):
            self.assertRegex(tipo_dte_str, TipoDteConverter.regex)

    def test_to_python(self) -> None:
        obj = TipoDteConverter()

        test_values: Sequence[Tuple[str, TipoDte]] = [
            ('33', TipoDte(33)),
            ('34', TipoDte(34)),
            ('43', TipoDte(43)),
            ('46', TipoDte(46)),
            ('52', TipoDte(52)),
            ('56', TipoDte(56)),
            ('61', TipoDte(61)),
            # warning: `110` is a valid value, but `TipoDte` doesn't support it yet.
            # ('110', TipoDte(110)),
        ]

        for string_test_value, python_test_value in test_values:
            self.assertEqual(obj.to_python(string_test_value), python_test_value)

    def test_to_url(self) -> None:
        obj = TipoDteConverter()

        test_values: Sequence[Tuple[TipoDte, str]] = [
            (TipoDte(33), '33'),
            (TipoDte(34), '34'),
            (TipoDte(43), '43'),
            (TipoDte(46), '46'),
            (TipoDte(52), '52'),
            (TipoDte(56), '56'),
            (TipoDte(61), '61'),
            # warning: `110` is a valid value, but `TipoDte` doesn't support it yet.
            # (TipoDte(110), '110'),
        ]

        for python_test_value, string_test_value in test_values:
            self.assertEqual(obj.to_url(python_test_value), string_test_value)
