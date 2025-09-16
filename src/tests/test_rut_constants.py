from __future__ import annotations

import re
import unittest
from typing import ClassVar, Pattern

import jsonschema

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


class RutRegexConstantsTestCase(unittest.TestCase):
    RUT_CANONICAL_STRICT_REGEX: ClassVar[Pattern[str]]
    RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX: ClassVar[Pattern[str]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RUT_CANONICAL_STRICT_REGEX = constants.RUT_CANONICAL_STRICT_REGEX
        cls.RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX = (
            constants.RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX
        )

    def test_json_schema_regex_is_python_regex_without_named_groups(self) -> None:
        # %% -----Arrange-----

        python_regex = self.RUT_CANONICAL_STRICT_REGEX
        python_regex_without_named_groups = re.compile(
            re.sub(
                pattern=r'\?P<\w+>',
                repl='',
                string=python_regex.pattern,
            )
        )
        expected = python_regex_without_named_groups

        # %% -----Act-----

        actual = self.RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX

        # %% -----Assert-----

        self.assertEqual(expected, actual)

        # %% -----

    def test_json_schema_regex_is_valid_schema(self) -> None:
        # %% -----Arrange-----

        schema = {
            "type": "string",
            "pattern": self.RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX.pattern,
        }
        valid_test_values = [
            '0-0',
            '1-9',
            '6-K',
            '78773510-K',
        ]
        invalid_test_values = [
            '6K',
            '6-k',
            '78773510-k',
            '78.773.510-K',
            78773510,
            1.9,
            None,
        ]

        # %% -----Act & Assert-----

        for test_value in valid_test_values:
            with self.subTest(test_value=test_value):
                try:
                    jsonschema.validate(instance=test_value, schema=schema)
                except jsonschema.exceptions.ValidationError as exc:
                    self.fail(f'{exc.__class__.__name__} raised')

        for invalid_test_value in invalid_test_values:
            with self.subTest(test_value=invalid_test_value):
                with self.assertRaises(jsonschema.exceptions.ValidationError):
                    jsonschema.validate(instance=invalid_test_value, schema=schema)

        # %% -----
