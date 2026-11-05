import unittest

import django.core.validators
import rest_framework  # noqa: F401
import rest_framework.exceptions
import rest_framework.fields

import cl_sii.dte.constants
from cl_sii.dte.constants import TipoDte
from cl_sii.extras.dj_model_fields import TipoDteChoices
from cl_sii.extras.drf_fields import DteFolioField, TipoDteField


class RutFieldTest(unittest.TestCase):
    # TODO: implement!

    pass


class TipoDteFieldTest(unittest.TestCase):
    error_messages = {'invalid_choice': 'Invalid choice.'}

    def test_is_choice_field(self) -> None:
        self.assertTrue(issubclass(TipoDteField, rest_framework.fields.ChoiceField))

    def test_choices(self) -> None:
        field = TipoDteField()

        self.assertEqual(dict(TipoDteChoices.choices), field.choices)

    def test_to_internal_value(self) -> None:
        field = TipoDteField()
        test_items = ['33', 33, TipoDte.FACTURA_ELECTRONICA]

        for value in test_items:
            with self.subTest(value=value):
                self.assertIs(TipoDte.FACTURA_ELECTRONICA, field.to_internal_value(value))

    def test_to_internal_value_of_invalid_value(self) -> None:
        field = TipoDteField(error_messages=self.error_messages)
        test_items = [999, '999', 'abc', '', ' 33 ', 33.0, True, None]

        for value in test_items:
            with self.subTest(value=value):
                with self.assertRaises(rest_framework.exceptions.ValidationError) as cm:
                    field.to_internal_value(value)

                self.assertEqual(['invalid_choice'], cm.exception.get_codes())

    def test_to_representation(self) -> None:
        field = TipoDteField()
        test_items = [TipoDte.FACTURA_ELECTRONICA, 33]

        for value in test_items:
            with self.subTest(value=value):
                representation = field.to_representation(value)

                self.assertIs(int, type(representation))
                self.assertEqual(33, representation)

    def test_custom_choices(self) -> None:
        choices = [(TipoDte.FACTURA_ELECTRONICA.value, 'Factura Electronica (33)')]
        field = TipoDteField(choices=choices, error_messages=self.error_messages)

        self.assertEqual(dict(choices), field.choices)
        self.assertIs(TipoDte.FACTURA_ELECTRONICA, field.to_internal_value('33'))
        with self.assertRaises(rest_framework.exceptions.ValidationError) as cm:
            field.to_internal_value('34')
        self.assertEqual(['invalid_choice'], cm.exception.get_codes())

    def test_custom_choice_not_in_tipo_dte(self) -> None:
        field = TipoDteField(
            choices=[(999, 'Unknown (999)')],
            error_messages=self.error_messages,
        )

        with self.assertRaises(rest_framework.exceptions.ValidationError) as cm:
            field.to_internal_value(999)
        self.assertEqual(['invalid_choice'], cm.exception.get_codes())


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
