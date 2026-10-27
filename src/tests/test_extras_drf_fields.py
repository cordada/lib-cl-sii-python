import unittest

import django.core.validators
import rest_framework  # noqa: F401
import rest_framework.fields

import cl_sii.dte.constants
from cl_sii.extras.drf_fields import DteFolioField


class RutFieldTest(unittest.TestCase):
    # TODO: implement!

    pass


class DteFolioFieldTest(unittest.TestCase):
    def test_is_integer_field(self) -> None:
        self.assertTrue(issubclass(DteFolioField, rest_framework.fields.IntegerField))

    def test_min_value_and_max_value(self) -> None:
        field = DteFolioField()

        self.assertEqual(cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE, field.min_value)
        self.assertEqual(cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE, field.max_value)

    def test_validators(self) -> None:
        field = DteFolioField()

        validator_limits = {
            type(validator): validator.limit_value
            for validator in field.validators
            if isinstance(validator, django.core.validators.BaseValidator)
        }
        self.assertEqual(
            {
                django.core.validators.MinValueValidator: (
                    cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE
                ),
                django.core.validators.MaxValueValidator: (
                    cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE
                ),
            },
            validator_limits,
        )

    def test_custom_min_value_and_max_value(self) -> None:
        field = DteFolioField(min_value=100, max_value=200)

        self.assertEqual(100, field.min_value)
        self.assertEqual(200, field.max_value)

    def test_run_validation_of_min_value(self) -> None:
        field = DteFolioField()

        value = field.run_validation(cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE)

        self.assertEqual(cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE, value)

    def test_run_validation_of_max_value(self) -> None:
        field = DteFolioField()

        value = field.run_validation(cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE)

        self.assertEqual(cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE, value)
