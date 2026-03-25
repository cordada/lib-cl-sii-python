import enum
import unittest
import unittest.mock
from typing import ClassVar

import django.core.exceptions
import django.db.models

import cl_sii.base.constants
import cl_sii.dte.constants
import cl_sii.extras.dj_model_fields
import cl_sii.rcv.constants
import cl_sii.rtc.constants
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


class TipoDocumentoFieldTestCase(unittest.TestCase):
    TipoDocumentoField: ClassVar[type[cl_sii.extras.dj_model_fields.TipoDocumentoField]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TipoDocumentoField = cl_sii.extras.dj_model_fields.TipoDocumentoField

    def test_is_field(self) -> None:
        self.assertTrue(issubclass(self.TipoDocumentoField, django.db.models.Field))

    def test_is_integer_field(self) -> None:
        self.assertTrue(issubclass(self.TipoDocumentoField, django.db.models.IntegerField))

    def test_choices(self) -> None:
        expected_choices = cl_sii.extras.dj_model_fields.TipoDocumentoChoices.choices
        field = self.TipoDocumentoField()
        self.assertEqual(expected_choices, field.choices)

    def test_custom_choices_are_not_overwritten(self) -> None:
        expected_choices = list(
            {
                tipo_doc.value: tipo_doc.name
                for tipo_doc in [
                    cl_sii.base.constants.TipoDocumento.BOLETA,
                    cl_sii.base.constants.TipoDocumento.BOLETA_ELECTRONICA,
                ]
            }.items()
        )
        field = self.TipoDocumentoField(
            choices=[
                (tipo_doc.value, tipo_doc.name)
                for tipo_doc in [
                    cl_sii.base.constants.TipoDocumento.BOLETA,
                    cl_sii.base.constants.TipoDocumento.BOLETA_ELECTRONICA,
                ]
            ]
        )
        self.assertEqual(expected_choices, field.choices)


class TipoDocumentoChoicesTestCase(unittest.TestCase):
    TipoDocumentoChoices: ClassVar[type[cl_sii.extras.dj_model_fields.TipoDocumentoChoices]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TipoDocumentoChoices = cl_sii.extras.dj_model_fields.TipoDocumentoChoices

    def test_is_enum(self) -> None:
        self.assertTrue(issubclass(self.TipoDocumentoChoices, enum.Enum))

    def test_is_choices(self) -> None:
        self.assertTrue(issubclass(self.TipoDocumentoChoices, django.db.models.Choices))

    def test_names(self) -> None:
        expected_names = [member.name for member in cl_sii.base.constants.TipoDocumento]
        self.assertEqual(expected_names, self.TipoDocumentoChoices.names)

    def test_values(self) -> None:
        expected_values = [member.value for member in cl_sii.base.constants.TipoDocumento]
        self.assertEqual(expected_values, self.TipoDocumentoChoices.values)

    def test_labels(self) -> None:
        for label in self.TipoDocumentoChoices.labels:
            self.assertIsInstance(label, str)

        self.assertEqual(
            len(cl_sii.base.constants.TipoDocumento), len(self.TipoDocumentoChoices.labels)
        )

    def test_choices(self) -> None:
        expected_choices = list(
            zip(self.TipoDocumentoChoices.values, self.TipoDocumentoChoices.labels)
        )
        self.assertEqual(expected_choices, self.TipoDocumentoChoices.choices)


class TipoDteFieldTestCase(unittest.TestCase):
    TipoDteField: ClassVar[type[cl_sii.extras.dj_model_fields.TipoDteField]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TipoDteField = cl_sii.extras.dj_model_fields.TipoDteField

    def test_is_field(self) -> None:
        self.assertTrue(issubclass(self.TipoDteField, django.db.models.Field))

    def test_is_integer_field(self) -> None:
        self.assertTrue(issubclass(self.TipoDteField, django.db.models.IntegerField))

    def test_choices(self) -> None:
        expected_choices = cl_sii.extras.dj_model_fields.TipoDteChoices.choices
        field = self.TipoDteField()
        self.assertEqual(expected_choices, field.choices)

    def test_custom_choices_are_not_overwritten(self) -> None:
        expected_choices = list(
            {
                tipo_dte.value: tipo_dte.name for tipo_dte in cl_sii.rtc.constants.TIPO_DTE_CEDIBLES
            }.items()
        )
        field = self.TipoDteField(
            choices=[
                (tipo_dte.value, tipo_dte.name)
                for tipo_dte in cl_sii.rtc.constants.TIPO_DTE_CEDIBLES
            ]
        )
        self.assertEqual(expected_choices, field.choices)


class TipoDteChoicesTestCase(unittest.TestCase):
    TipoDteChoices: ClassVar[type[cl_sii.extras.dj_model_fields.TipoDteChoices]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TipoDteChoices = cl_sii.extras.dj_model_fields.TipoDteChoices

    def test_is_enum(self) -> None:
        self.assertTrue(issubclass(self.TipoDteChoices, enum.Enum))

    def test_is_choices(self) -> None:
        self.assertTrue(issubclass(self.TipoDteChoices, django.db.models.Choices))

    def test_names(self) -> None:
        expected_names = [member.name for member in cl_sii.dte.constants.TipoDte]
        self.assertEqual(expected_names, self.TipoDteChoices.names)

    def test_values(self) -> None:
        expected_values = [member.value for member in cl_sii.dte.constants.TipoDte]
        self.assertEqual(expected_values, self.TipoDteChoices.values)

    def test_labels(self) -> None:
        for label in self.TipoDteChoices.labels:
            self.assertIsInstance(label, str)

        self.assertEqual(len(cl_sii.dte.constants.TipoDte), len(self.TipoDteChoices.labels))

    def test_choices(self) -> None:
        expected_choices = list(zip(self.TipoDteChoices.values, self.TipoDteChoices.labels))
        self.assertEqual(expected_choices, self.TipoDteChoices.choices)


class RcvTipoDoctoFieldTestCase(unittest.TestCase):
    RcvTipoDoctoField: ClassVar[type[cl_sii.extras.dj_model_fields.RcvTipoDoctoField]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcvTipoDoctoField = cl_sii.extras.dj_model_fields.RcvTipoDoctoField

    def test_is_field(self) -> None:
        self.assertTrue(issubclass(self.RcvTipoDoctoField, django.db.models.Field))

    def test_is_integer_field(self) -> None:
        self.assertTrue(issubclass(self.RcvTipoDoctoField, django.db.models.IntegerField))

    def test_choices(self) -> None:
        expected_choices = cl_sii.extras.dj_model_fields.RcvTipoDoctoChoices.choices
        field = self.RcvTipoDoctoField()
        self.assertEqual(expected_choices, field.choices)

    def test_custom_choices_are_not_overwritten(self) -> None:
        expected_choices = list(
            {
                tipo_doc.value: tipo_doc.name
                for tipo_doc in [
                    cl_sii.rcv.constants.RcvTipoDocto.NOTA_CREDITO,
                    cl_sii.rcv.constants.RcvTipoDocto.NOTA_CREDITO_ELECTRONICA,
                ]
            }.items()
        )
        field = self.RcvTipoDoctoField(
            choices=[
                (tipo_doc.value, tipo_doc.name)
                for tipo_doc in [
                    cl_sii.rcv.constants.RcvTipoDocto.NOTA_CREDITO,
                    cl_sii.rcv.constants.RcvTipoDocto.NOTA_CREDITO_ELECTRONICA,
                ]
            ]
        )
        self.assertEqual(expected_choices, field.choices)


class RcvTipoDoctoChoicesTestCase(unittest.TestCase):
    RcvTipoDoctoChoices: ClassVar[type[cl_sii.extras.dj_model_fields.RcvTipoDoctoChoices]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcvTipoDoctoChoices = cl_sii.extras.dj_model_fields.RcvTipoDoctoChoices

    def test_is_enum(self) -> None:
        self.assertTrue(issubclass(self.RcvTipoDoctoChoices, enum.Enum))

    def test_is_choices(self) -> None:
        self.assertTrue(issubclass(self.RcvTipoDoctoChoices, django.db.models.Choices))

    def test_names(self) -> None:
        expected_names = [member.name for member in cl_sii.rcv.constants.RcvTipoDocto]
        self.assertEqual(expected_names, self.RcvTipoDoctoChoices.names)

    def test_values(self) -> None:
        expected_values = [member.value for member in cl_sii.rcv.constants.RcvTipoDocto]
        self.assertEqual(expected_values, self.RcvTipoDoctoChoices.values)

    def test_labels(self) -> None:
        for label in self.RcvTipoDoctoChoices.labels:
            self.assertIsInstance(label, str)

        self.assertEqual(
            len(cl_sii.rcv.constants.RcvTipoDocto), len(self.RcvTipoDoctoChoices.labels)
        )

    def test_choices(self) -> None:
        expected_choices = list(
            zip(self.RcvTipoDoctoChoices.values, self.RcvTipoDoctoChoices.labels)
        )
        self.assertEqual(expected_choices, self.RcvTipoDoctoChoices.choices)
