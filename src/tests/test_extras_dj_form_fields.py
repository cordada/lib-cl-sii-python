import unittest

import django.core.exceptions

from cl_sii.extras.dj_form_fields import Rut, RutField


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
