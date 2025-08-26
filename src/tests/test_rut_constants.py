from __future__ import annotations

import unittest

from cl_sii.rut import constants


class RutDigitsConstantsTestCase(unittest.TestCase):
    def test_min_value(self) -> None:
        min_rut_digits = constants.RUT_DIGITS_MIN_VALUE

        self.assertLessEqual(min_rut_digits, constants.RUT_DIGITS_MAX_VALUE)

    def test_max_value(self) -> None:
        max_rut_digits = constants.RUT_DIGITS_MAX_VALUE

        self.assertGreaterEqual(max_rut_digits, constants.RUT_DIGITS_MIN_VALUE)

    def test_persona_juridica_min_value(self) -> None:
        min_rut_digits = constants.PERSONA_JURIDICA_MIN_RUT_DIGITS

        self.assertGreaterEqual(min_rut_digits, constants.RUT_DIGITS_MIN_VALUE)
        self.assertLessEqual(min_rut_digits, constants.RUT_DIGITS_MAX_VALUE)
