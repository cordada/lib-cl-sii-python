import unittest
import unittest.mock

import django.core.exceptions
import django.db.models

from cl_sii.extras.dj_model_fields import Rut, RutField


class RutFieldTest(unittest.TestCase):
    valid_rut_canonical: str
    valid_rut_instance: Rut
    valid_rut_canonical_with_invalid_dv: str
    valid_rut_canonical_instance_with_invalid_dv: Rut
    valid_rut_verbose_leading_zero_lowercase: str
    mock_model_instance: django.db.models.Model

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_rut_canonical = '60803000-K'
        cls.valid_rut_instance = Rut(cls.valid_rut_canonical)
        cls.valid_rut_canonical_with_invalid_dv = '60803000-0'
        cls.valid_rut_canonical_instance_with_invalid_dv = Rut(
            cls.valid_rut_canonical_with_invalid_dv
        )
        assert not cls.valid_rut_canonical_instance_with_invalid_dv.validate_dv()
        cls.valid_rut_verbose_leading_zero_lowercase = '060.803.000-k'
        cls.mock_model_instance = unittest.mock.create_autospec(
            django.db.models.Model, instance=True
        )

    def test_get_prep_value_of_canonical_str(self) -> None:
        prepared_value = RutField().get_prep_value(self.valid_rut_canonical)
        self.assertIsInstance(prepared_value, str)
        self.assertEqual(prepared_value, self.valid_rut_canonical)

    def test_get_prep_value_of_non_canonical_str(self) -> None:
        prepared_value = RutField().get_prep_value(self.valid_rut_verbose_leading_zero_lowercase)
        self.assertIsInstance(prepared_value, str)
        self.assertEqual(prepared_value, self.valid_rut_canonical)

    def test_get_prep_value_of_Rut(self) -> None:
        prepared_value = RutField().get_prep_value(self.valid_rut_instance)
        self.assertIsInstance(prepared_value, str)
        self.assertEqual(prepared_value, self.valid_rut_canonical)

    def test_get_prep_value_of_None(self) -> None:
        prepared_value = RutField().get_prep_value(None)
        self.assertIsNone(prepared_value)

    def test_clean_value_with_invalid_type(self) -> None:
        for value_with_invalid_type in [12345678, 12.34, [], {}, object()]:
            with self.subTest(value=value_with_invalid_type):
                rut_field = RutField()
                with self.assertRaises(django.core.exceptions.ValidationError) as cm:
                    rut_field.clean(value_with_invalid_type, self.mock_model_instance)
                self.assertEqual(cm.exception.code, 'invalid')

    def test_clean_value_of_rut_str_with_invalid_dv_if_validated(self) -> None:
        rut_field = RutField(validate_dv=True)
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            rut_field.clean(self.valid_rut_canonical_with_invalid_dv, self.mock_model_instance)
        self.assertEqual(cm.exception.code, 'invalid_dv')

    def test_clean_value_of_rut_str_with_invalid_dv_if_not_validated(self) -> None:
        rut_field = RutField(validate_dv=False)
        cleaned_value = rut_field.clean(
            self.valid_rut_canonical_with_invalid_dv, self.mock_model_instance
        )
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value.canonical, self.valid_rut_canonical_with_invalid_dv)

    def test_clean_value_of_rut_instance_with_valid_dv(self) -> None:
        for validate_dv in [True, False]:
            with self.subTest(validate_dv=validate_dv):
                rut_field = RutField(validate_dv=validate_dv)
                cleaned_value = rut_field.clean(self.valid_rut_instance, self.mock_model_instance)
                self.assertIsInstance(cleaned_value, Rut)
                self.assertEqual(cleaned_value, self.valid_rut_instance)

    def test_clean_value_of_rut_instance_with_invalid_dv_if_validated(self) -> None:
        rut_field = RutField(validate_dv=True)
        with self.assertRaises(django.core.exceptions.ValidationError) as cm:
            rut_field.clean(
                self.valid_rut_canonical_instance_with_invalid_dv, self.mock_model_instance
            )
        self.assertEqual(cm.exception.code, 'invalid_dv')

    def test_clean_value_of_rut_instance_with_invalid_dv_if_not_validated(self) -> None:
        rut_field = RutField(validate_dv=False)
        cleaned_value = rut_field.clean(
            self.valid_rut_canonical_instance_with_invalid_dv, self.mock_model_instance
        )
        self.assertIsInstance(cleaned_value, Rut)
        self.assertEqual(cleaned_value, self.valid_rut_canonical_instance_with_invalid_dv)

    def test_deconstruct_without_options(self) -> None:
        name, path, args, kwargs = RutField().deconstruct()
        self.assertEqual(path, 'cl_sii.extras.dj_model_fields.RutField')
        self.assertEqual(args, [])
        self.assertEqual(kwargs, {})

    def test_deconstruct_with_option_validate_dv_enabled(self) -> None:
        name, path, args, kwargs = RutField(validate_dv=True).deconstruct()
        self.assertEqual(args, [])
        self.assertEqual(kwargs, {'validate_dv': True})

    def test_deconstruct_with_option_validate_dv_disabled(self) -> None:
        name, path, args, kwargs = RutField(validate_dv=False).deconstruct()
        self.assertEqual(args, [])
        self.assertEqual(kwargs, {})
