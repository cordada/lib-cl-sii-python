import unittest

import django.db.models  # noqa: F401

from cl_sii.extras.dj_model_fields import Rut, RutField


class RutFieldTest(unittest.TestCase):
    valid_rut_canonical: str
    valid_rut_instance: Rut
    valid_rut_verbose_leading_zero_lowercase: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_rut_canonical = '60803000-K'
        cls.valid_rut_instance = Rut(cls.valid_rut_canonical)
        cls.valid_rut_verbose_leading_zero_lowercase = '060.803.000-k'

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
