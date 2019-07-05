import unittest

import django.db.models  # noqa: F401

from cl_sii.extras.dj_model_fields import Rut, RutField


class RutFieldTest(unittest.TestCase):
    valid_rut_canonical: str
    valid_rut_instance: Rut

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_rut_canonical = '60803000-K'
        cls.valid_rut_instance = Rut(cls.valid_rut_canonical)

    def test_get_prep_value_of_Rut(self) -> None:
        prepared_value = RutField().get_prep_value(self.valid_rut_instance)
        self.assertIsInstance(prepared_value, str)
        self.assertEqual(prepared_value, self.valid_rut_canonical)

    def test_get_prep_value_of_None(self) -> None:
        prepared_value = RutField().get_prep_value(None)
        self.assertIsNone(prepared_value)
