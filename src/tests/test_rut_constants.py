from __future__ import annotations

import unittest
from typing import ClassVar

from cl_sii.rut import constants


class RutDigitsConstantsTestCase(unittest.TestCase):
    RUT_DIGITS_MIN_VALUE: ClassVar[int]
    RUT_DIGITS_MAX_VALUE: ClassVar[int]
    PERSONA_JURIDICA_MIN_RUT_DIGITS: ClassVar[int]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RUT_DIGITS_MIN_VALUE = constants.RUT_DIGITS_MIN_VALUE
        cls.RUT_DIGITS_MAX_VALUE = constants.RUT_DIGITS_MAX_VALUE
        cls.PERSONA_JURIDICA_MIN_RUT_DIGITS = constants.PERSONA_JURIDICA_MIN_RUT_DIGITS

    def test_min_value(self) -> None:
        min_rut_digits = self.RUT_DIGITS_MIN_VALUE

        self.assertLessEqual(min_rut_digits, self.RUT_DIGITS_MAX_VALUE)

    def test_max_value(self) -> None:
        max_rut_digits = self.RUT_DIGITS_MAX_VALUE

        self.assertGreaterEqual(max_rut_digits, self.RUT_DIGITS_MIN_VALUE)

    def test_persona_juridica_min_value(self) -> None:
        min_rut_digits = self.PERSONA_JURIDICA_MIN_RUT_DIGITS

        self.assertGreaterEqual(min_rut_digits, self.RUT_DIGITS_MIN_VALUE)
        self.assertLessEqual(min_rut_digits, self.RUT_DIGITS_MAX_VALUE)
