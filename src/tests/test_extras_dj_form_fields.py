import unittest

import django.core.exceptions

from cl_sii.dte.constants import TipoDte
from cl_sii.extras.dj_form_fields import Rut, RutField, TipoDteField
from cl_sii.extras.dj_model_fields import TipoDteChoices


class RutFieldTest(unittest.TestCase):
    valid_rut_canonical: str
    valid_rut_instance: Rut
    valid_rut_verbose_leading_zero_lowercase: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.invalid_rut_canonical = '60803000K'
        cls.valid_rut_canonical = '60803000-K'
        cls.valid_rut_instance = Rut(cls.valid_rut_canonical)
        cls.valid_rut_canonical_with_invalid_dv = '60803000-0'
        cls.valid_rut_canonical_instance_with_invalid_dv = Rut(
            cls.valid_rut_canonical_with_invalid_dv
        )
        assert not cls.valid_rut_canonical_instance_with_invalid_dv.validate_dv()
        cls.valid_rut_verbose_leading_zero_lowercase = '060.803.000-k'

    def test_clean_value_of_invalid_canonical_str(self) -> None:
        rut_field = RutField()
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            rut_field.clean(self.invalid_rut_canonical)
        self.assertEqual(cm.exception.code, 'invalid')

    def test_clean_value_of_canonical_str(self) -> None:
        rut_field = RutField()
        cleaned_value = rut_field.clean(self.valid_rut_canonical)
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value.canonical, self.valid_rut_canonical)

    def test_clean_value_of_non_canonical_str(self) -> None:
        rut_field = RutField()
        cleaned_value = rut_field.clean(self.valid_rut_verbose_leading_zero_lowercase)
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value.canonical, self.valid_rut_canonical)

    def test_clean_value_of_Rut(self) -> None:
        rut_field = RutField()
        cleaned_value = rut_field.clean(self.valid_rut_instance)
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value.canonical, self.valid_rut_canonical)

    def test_clean_value_of_rut_str_with_invalid_dv_if_validated(self) -> None:
        rut_field = RutField(validate_dv=True)
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            rut_field.clean(self.valid_rut_canonical_with_invalid_dv)
        self.assertEqual(cm.exception.code, 'invalid_dv')

    def test_clean_value_of_rut_str_with_invalid_dv_if_not_validated(self) -> None:
        rut_field = RutField(validate_dv=False)
        cleaned_value = rut_field.clean(self.valid_rut_canonical_with_invalid_dv)
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value.canonical, self.valid_rut_canonical_with_invalid_dv)

    def test_clean_value_of_rut_instance_with_invalid_dv_if_validated(self) -> None:
        rut_field = RutField(validate_dv=True)
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            rut_field.clean(self.valid_rut_canonical_instance_with_invalid_dv)
        self.assertEqual(cm.exception.code, 'invalid_dv')

    def test_clean_value_of_rut_instance_with_invalid_dv_if_not_validated(self) -> None:
        rut_field = RutField(validate_dv=False)
        cleaned_value = rut_field.clean(self.valid_rut_canonical_instance_with_invalid_dv)
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value, self.valid_rut_canonical_instance_with_invalid_dv)

    def test_clean_of_empty_value_if_not_required(self) -> None:
        rut_field = RutField(required=False)
        for value in RutField.empty_values:
            cleaned_value = rut_field.clean(value)
            self.assertIsNone(cleaned_value)

    def test_clean_of_empty_value_if_required(self) -> None:
        rut_field = RutField()
        for value in RutField.empty_values:
            with self.assertRaises(django.core.exceptions.ValidationError) as cm:
                rut_field.clean(value)
            self.assertEqual(cm.exception.code, 'required')


class TipoDteFieldTest(unittest.TestCase):
    def test_choices(self) -> None:
        field = TipoDteField()

        self.assertEqual(TipoDteChoices.choices, field.choices)

    def test_clean(self) -> None:
        field = TipoDteField()
        test_items = ['33', 33, TipoDte.FACTURA_ELECTRONICA]

        for value in test_items:
            with self.subTest(value=value):
                self.assertIs(TipoDte.FACTURA_ELECTRONICA, field.clean(value))

    def test_prepare_value(self) -> None:
        field = TipoDteField()

        self.assertEqual(33, field.prepare_value(TipoDte.FACTURA_ELECTRONICA))
        self.assertEqual('33', field.prepare_value('33'))
        self.assertIsNone(field.prepare_value(None))

    def test_clean_empty_value_if_not_required(self) -> None:
        field = TipoDteField(required=False)

        self.assertIsNone(field.clean(''))

    def test_clean_invalid_value(self) -> None:
        field = TipoDteField()
        test_items = ['999', 'abc']

        for value in test_items:
            with self.subTest(value=value):
                with self.assertRaises(django.core.exceptions.ValidationError) as cm:
                    field.clean(value)

                self.assertEqual('invalid_choice', cm.exception.code)

    def test_custom_choices(self) -> None:
        choices = [(TipoDte.FACTURA_ELECTRONICA.value, 'Factura Electronica (33)')]
        field = TipoDteField(choices=choices)

        self.assertEqual(choices, field.choices)
        self.assertIs(TipoDte.FACTURA_ELECTRONICA, field.clean('33'))
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            field.clean('34')
        self.assertEqual('invalid_choice', cm.exception.code)
