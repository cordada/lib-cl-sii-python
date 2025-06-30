import base64
import dataclasses
import unittest
from datetime import date, datetime
from typing import Mapping

import pydantic

from cl_sii.dte.constants import (
    DTE_FOLIO_FIELD_MAX_VALUE,
    DTE_FOLIO_FIELD_MIN_VALUE,
    DTE_MONTO_TOTAL_FIELD_MAX_VALUE,
    DTE_MONTO_TOTAL_FIELD_MIN_VALUE,
    TipoDte,
)
from cl_sii.dte.data_models import (  # noqa: F401
    DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER,
    VALIDATION_CONTEXT_TRUST_INPUT,
    DteDataL0,
    DteDataL1,
    DteDataL2,
    DteNaturalKey,
    DteXmlData,
    DteXmlReferencia,
    validate_contribuyente_razon_social,
    validate_dte_folio,
    validate_dte_monto_total,
)
from cl_sii.libs import encoding_utils, tz_utils
from cl_sii.rut import Rut
from .utils import read_test_file_bytes


class DteNaturalKeyTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.dte_nk_1 = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_validate_folio_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('folio',),
                'msg': "Value error, Value is out of the valid range for 'folio'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field folio
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_nk_1,
                folio=DTE_FOLIO_FIELD_MIN_VALUE - 1,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Validate the maximum value of the field folio
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_nk_1,
                folio=DTE_FOLIO_FIELD_MAX_VALUE + 1,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_nk_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
            ),
        )

    def test_slug(self) -> None:
        self.assertEqual(self.dte_nk_1.slug, '76354771-K--33--170')

    def test_random(self) -> None:
        # Test that random() returns a DteNaturalKey instance
        random_dte_nk = DteNaturalKey.random()
        self.assertIsInstance(random_dte_nk, DteNaturalKey)

        # Test with default parameters -
        #   tipo_dte should be randomly selected from all TipoDte values
        random_dte_nk_default = DteNaturalKey.random()
        self.assertIsInstance(random_dte_nk_default.tipo_dte, TipoDte)
        self.assertIn(random_dte_nk_default.tipo_dte, TipoDte)

        # Test that each call to random() returns different values
        random_dte_nk_1 = DteNaturalKey.random()
        random_dte_nk_2 = DteNaturalKey.random()
        self.assertNotEqual(random_dte_nk_1, random_dte_nk_2)

        # Test that the generated folio values are within valid ranges
        self.assertGreaterEqual(random_dte_nk.folio, DTE_FOLIO_FIELD_MIN_VALUE)
        self.assertLessEqual(random_dte_nk.folio, DTE_FOLIO_FIELD_MAX_VALUE)

        # Test that emisor_rut is a valid Rut instance
        self.assertIsInstance(random_dte_nk.emisor_rut, Rut)

        # Test that tipo_dte is a valid TipoDte enum value
        self.assertIsInstance(random_dte_nk.tipo_dte, TipoDte)
        self.assertIn(random_dte_nk.tipo_dte, TipoDte)

        # Test with custom parameters
        custom_rut = Rut('12345678-9')
        custom_tipo = TipoDte.NOTA_CREDITO_ELECTRONICA
        custom_folio = 12345

        custom_dte_nk = DteNaturalKey.random(
            emisor_rut=custom_rut, tipo_dte=custom_tipo, folio=custom_folio
        )

        self.assertEqual(custom_dte_nk.emisor_rut, custom_rut)
        self.assertEqual(custom_dte_nk.tipo_dte, custom_tipo)
        self.assertEqual(custom_dte_nk.folio, custom_folio)

        # Test with specific tipo_dte (single value, not sequence)
        specific_tipo = TipoDte.FACTURA_ELECTRONICA
        specific_dte_nk = DteNaturalKey.random(tipo_dte=specific_tipo)
        self.assertEqual(specific_dte_nk.tipo_dte, specific_tipo)

        # Test with partial custom parameters
        partial_custom = DteNaturalKey.random(emisor_rut=custom_rut)
        self.assertEqual(partial_custom.emisor_rut, custom_rut)
        self.assertIsInstance(partial_custom.tipo_dte, TipoDte)
        self.assertGreaterEqual(partial_custom.folio, DTE_FOLIO_FIELD_MIN_VALUE)
        self.assertLessEqual(partial_custom.folio, DTE_FOLIO_FIELD_MAX_VALUE)

        # Test that multiple calls generate different combinations
        generated_combinations = set()
        for _ in range(10):
            dte_nk = DteNaturalKey.random()
            combination = (dte_nk.emisor_rut, dte_nk.tipo_dte, dte_nk.folio)
            generated_combinations.add(combination)

        # Should generate mostly unique combinations (allow some duplicates due to randomness)
        self.assertGreater(len(generated_combinations), 1)


class DteDataL0Test(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.dte_l0_1 = DteDataL0(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l0_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
            ),
        )

    def test_natural_key(self) -> None:
        self.assertEqual(
            self.dte_l0_1.natural_key,
            DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
            ),
        )


class DteDataL1Test(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.dte_l1_1 = DteDataL1(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
        )

    def test_is_ok_negative_monto_total_in_tipo_dte_liquidacion_factura(self) -> None:
        try:
            _ = dataclasses.replace(
                self.dte_l1_1,
                tipo_dte=TipoDte.LIQUIDACION_FACTURA_ELECTRONICA,
                monto_total=-1,
            )
        except pydantic.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

    def test_validate_monto_total_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('monto_total',),
                'msg': "Value error, Value is out of the valid range for 'monto_total'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field monto_total
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=DTE_MONTO_TOTAL_FIELD_MIN_VALUE - 1,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Validate the maximum value of the field monto_total
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=DTE_MONTO_TOTAL_FIELD_MAX_VALUE + 1,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Validate the minimum value of the field monto_total
        # for a tipo_dte FACTURA_ELECTRONICA
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=-1,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l1_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            ),
        )

    def test_vendedor_rut_comprador_rut(self) -> None:
        emisor_rut = self.dte_l1_1.emisor_rut
        receptor_rut = self.dte_l1_1.receptor_rut
        dte_factura_venta = dataclasses.replace(self.dte_l1_1, tipo_dte=TipoDte.FACTURA_ELECTRONICA)
        dte_factura_venta_exenta = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA
        )
        dte_factura_compra = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA
        )
        dte_nota_credito = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDte.NOTA_CREDITO_ELECTRONICA
        )

        # 'vendedor_rut'
        self.assertEqual(dte_factura_venta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_venta_exenta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_compra.vendedor_rut, receptor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.vendedor_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concept \"vendedor\" does not apply for this 'tipo_dte'.", dte_nota_credito.tipo_dte),
        )

        # 'comprador_rut'
        self.assertEqual(dte_factura_venta.comprador_rut, receptor_rut)
        self.assertEqual(dte_factura_venta_exenta.comprador_rut, receptor_rut)
        self.assertEqual(dte_factura_compra.comprador_rut, emisor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.comprador_rut)
        self.assertEqual(
            cm.exception.args,
            (
                "Concepts \"comprador\" and \"deudor\" do not apply for this 'tipo_dte'.",
                dte_nota_credito.tipo_dte,
            ),
        )

        # 'deudor_rut'
        self.assertEqual(dte_factura_venta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_venta_exenta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_compra.deudor_rut, emisor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.deudor_rut)
        self.assertEqual(
            cm.exception.args,
            (
                "Concepts \"comprador\" and \"deudor\" do not apply for this 'tipo_dte'.",
                dte_nota_credito.tipo_dte,
            ),
        )


class DteDataL2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_1_xml_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'
            )
        )
        cls.dte_1_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )
        cls.dte_2_xml_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--60910000-1--33--2336600-signature-value-base64.txt'
            )
        )
        cls.dte_2_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der'
        )

    def setUp(self) -> None:
        super().setUp()

        self.dte_l2_1 = DteDataL2(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=DteDataL2.DATETIME_FIELDS_TZ,
            ),
            signature_value=self.dte_1_xml_signature_value,
            signature_x509_cert_der=self.dte_1_xml_cert_der,
            emisor_giro='Ingenieria y Construccion',
            emisor_email='hello@example.com',
            receptor_email=None,
        )
        self.dte_l2_2 = DteDataL2(
            emisor_rut=Rut('60910000-1'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=2336600,
            fecha_emision_date=date(2019, 8, 8),
            receptor_rut=Rut('76555835-2'),
            monto_total=10642,
            emisor_razon_social='Universidad de Chile',
            receptor_razon_social='FYNPAL SPA',
            fecha_vencimiento_date=date(2019, 8, 8),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 9, 9, 41, 9),
                tz=DteDataL2.DATETIME_FIELDS_TZ,
            ),
            signature_value=self.dte_2_xml_signature_value,
            signature_x509_cert_der=self.dte_2_xml_cert_der,
            emisor_giro='Corporación Educacional y Servicios                 Profesionales',
            emisor_email=None,
            receptor_email=None,
        )

    def test_constants_match(self) -> None:
        self.assertEqual(
            DteXmlData.DATETIME_FIELDS_TZ,
            DteDataL2.DATETIME_FIELDS_TZ,
        )

    def test_ok_razon_social_none(self) -> None:
        try:
            _ = dataclasses.replace(
                self.dte_l2_1,
                emisor_razon_social=None,
                receptor_razon_social=None,
            )
        except pydantic.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

    def test_validate_emisor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_receptor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                firma_documento_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': (
                    'Value error, ('
                    '''"Timezone of datetime value must be 'America/Santiago'.",'''
                    ' datetime.datetime(2019, 4, 5, 12, 57, 32, tzinfo=<UTC>)'
                    ')'
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_init_fail_regression_signature_value_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True),
        )

        init_kwars = self.dte_l2_1.as_dict()
        init_kwars.update(dict(signature_value=bytes_value_with_x20))

        # with self.assertRaises(ValueError) as cm:
        #     _ = DteDataL2(**init_kwars)
        # self.assertEqual(
        #     cm.exception.args,
        #     ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        # )
        _ = DteDataL2(**init_kwars)

    def test_validate_non_empty_bytes_signature_value(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('signature_value',),
                'msg': 'Value error, Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                signature_value=b'',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_init_fail_regression_signature_cert_der_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True),
        )

        init_kwars = self.dte_l2_1.as_dict()
        init_kwars.update(dict(signature_x509_cert_der=bytes_value_with_x20))

        # with self.assertRaises(ValueError) as cm:
        #     _ = DteDataL2(**init_kwars)
        # self.assertEqual(
        #     cm.exception.args,
        #     ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        # )
        _ = DteDataL2(**init_kwars)

    def test_validate_non_empty_bytes_signature_x509_cert_der(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('signature_x509_cert_der',),
                'msg': 'Value error, Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                signature_x509_cert_der=b'',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': (
                    "Value error, "
                    "('Value has leading or trailing whitespace characters.', ' NASA ')"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_giro=' NASA ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': (
                    "Value error, "
                    "("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_emisor_email@test.cl '"
                    ")"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_email=' fake_emisor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': (
                    "Value error, ("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_receptor_email@test.cl '"
                    ")"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_email=' fake_receptor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_giro='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l2_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteDataL2.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
            ),
        )
        self.assertDictEqual(
            self.dte_l2_2.as_dict(),
            dict(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteDataL2.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            ),
        )

    def test_as_dte_data_l1(self) -> None:
        self.assertEqual(
            self.dte_l2_1.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            ),
        )
        self.assertEqual(
            self.dte_l2_2.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
            ),
        )


class DteXmlReferenciaTest(unittest.TestCase):
    """
    Tests for :class:`DteXmlReferencia`.
    """

    def _set_obj_1(self) -> None:
        obj = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="4769807823",
            fecha_ref=date(2021, 4, 16),
        )
        self.assertIsInstance(obj, DteXmlReferencia)

        self.obj_1 = obj

    def _set_obj_2(self) -> None:
        obj = DteXmlReferencia(
            numero_linea_ref=2,
            tipo_documento_ref="HES",
            folio_ref="1001055906",
            fecha_ref=date(2021, 4, 16),
        )
        self.assertIsInstance(obj, DteXmlReferencia)

        self.obj_2 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            DteXmlReferencia()

    def test_init_fail_numero_linea_ref_out_of_range(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                numero_linea_ref=0,
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('numero_linea_ref',),
                    'msg': (
                        'Value error, '
                        '("Value \'numero_linea_ref\' must be a value between 1 and 40", 0)'
                    ),
                    'type': 'value_error',
                }
            ],
        )
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                numero_linea_ref=41,
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('numero_linea_ref',),
                    'msg': (
                        'Value error, '
                        '("Value \'numero_linea_ref\' must be a value between 1 and 40", 41)'
                    ),
                    'type': 'value_error',
                }
            ],
        )

    def test_init_fail_tipo_documento_ref_invalid(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                tipo_documento_ref="8001",
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('tipo_documento_ref',),
                    'msg': 'Value error, ("The length of \'tipo_documento_ref\' must be a '
                    'value between 1 and 3", \'8001\')',
                    'type': 'value_error',
                }
            ],
        )
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                tipo_documento_ref="2BAD",
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('tipo_documento_ref',),
                    'msg': 'Value error, ("The length of \'tipo_documento_ref\' must be a value '
                    'between 1 and 3", \'2BAD\')',
                    'type': 'value_error',
                },
            ],
        )

    def test_init_fail_ind_global_invalid(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                ind_global=2,
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('ind_global',),
                    'msg': (
                        'Value error, '
                        '("Only the value \'1\' is valid for the field \'ind_global\'", 2)'
                    ),
                    'type': 'value_error',
                }
            ],
        )

    def test_init_fail_folio_ref_empty(self) -> None:
        self._set_obj_2()

        obj = self.obj_2

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                folio_ref="",
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('folio_ref',),
                    'msg': (
                        'Value error, '
                        '("The length of \'folio_ref\' must be a value between 1 and 18", \'\')'
                    ),
                    'type': 'value_error',
                }
            ],
        )

    def test_init_fail_fecha_ref_out_of_range(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_ref=date(2002, 7, 31),
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('fecha_ref',),
                    'msg': 'Value error, ("The date \'fecha_ref\' must be after 2002-08-01 and '
                    'before 2050-12-31", datetime.date(2002, 7, 31))',
                    'type': 'value_error',
                }
            ],
        )
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_ref=date(2051, 1, 1),
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('fecha_ref',),
                    'msg': (
                        'Value error, ('
                        '"The date \'fecha_ref\' must be after 2002-08-01 and '
                        'before 2050-12-31", datetime.date(2051, 1, 1))'
                    ),
                    'type': 'value_error',
                },
            ],
        )

    def test_init_fail_razon_ref_too_long(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                razon_ref=(
                    'Lorem ipsum dolor sit amet, consectetur adipiscing '
                    'elit. Sed metus magna, ultricies sit amet dolor sed'
                ),
            )
        self.assertEqual(
            assert_raises_cm.exception.errors(
                include_context=False,
                include_input=False,
                include_url=False,
            ),
            [
                {
                    'loc': ('razon_ref',),
                    'msg': (
                        "Value error, "
                        "('The maximum length allowed for `razon_ref` is 90', "
                        "'Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                        "Sed metus magna, ultricies sit amet dolor sed')"
                    ),
                    'type': 'value_error',
                }
            ],
        )


class DteXmlDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_1_xml_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'
            )
        )
        cls.dte_1_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )
        cls.dte_2_xml_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--60910000-1--33--2336600-signature-value-base64.txt'
            )
        )
        cls.dte_2_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der'
        )
        cls.dte_3_xml_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--96670340-7--61--110616-signature-value-base64.txt'
            )
        )
        cls.dte_3_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--96670340-7--61--110616-cert.der'
        )

    def setUp(self) -> None:
        super().setUp()

        self.dte_xml_data_1 = DteXmlData(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=DteXmlData.DATETIME_FIELDS_TZ,
            ),
            signature_value=self.dte_1_xml_signature_value,
            signature_x509_cert_der=self.dte_1_xml_cert_der,
            emisor_giro='Ingenieria y Construccion',
            emisor_email='hello@example.com',
            receptor_email=None,
            referencias=[
                DteXmlReferencia(
                    numero_linea_ref=1,
                    tipo_documento_ref='801',
                    folio_ref='638370',
                    fecha_ref=date(2019, 3, 28),
                    ind_global=None,
                    rut_otro=None,
                    codigo_ref=None,
                    razon_ref=None,
                ),
                DteXmlReferencia(
                    numero_linea_ref=2,
                    tipo_documento_ref='HES',
                    folio_ref='1001055906',
                    fecha_ref=date(2019, 3, 28),
                    ind_global=None,
                    rut_otro=None,
                    codigo_ref=None,
                    razon_ref=None,
                ),
            ],
        )
        self.dte_xml_data_2 = DteXmlData(
            emisor_rut=Rut('60910000-1'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=2336600,
            fecha_emision_date=date(2019, 8, 8),
            receptor_rut=Rut('76555835-2'),
            monto_total=10642,
            emisor_razon_social='Universidad de Chile',
            receptor_razon_social='FYNPAL SPA',
            fecha_vencimiento_date=date(2019, 8, 8),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 9, 9, 41, 9),
                tz=DteXmlData.DATETIME_FIELDS_TZ,
            ),
            signature_value=self.dte_2_xml_signature_value,
            signature_x509_cert_der=self.dte_2_xml_cert_der,
            emisor_giro='Corporación Educacional y Servicios                 Profesionales',
            emisor_email=None,
            receptor_email=None,
            referencias=None,
        )
        self.dte_xml_data_3 = DteXmlData(
            emisor_rut=Rut('96670340-7'),
            tipo_dte=TipoDte.NOTA_CREDITO_ELECTRONICA,
            folio=110616,
            fecha_emision_date=date(2019, 8, 2),
            receptor_rut=Rut('81675600-6'),
            monto_total=57347078,
            emisor_razon_social='Bata Chile S.A.',
            receptor_razon_social='Comercializadora S.A',
            fecha_vencimiento_date=date(2019, 9, 1),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 5, 15, 20, 6), tz=DteXmlData.DATETIME_FIELDS_TZ
            ),
            signature_value=self.dte_3_xml_signature_value,
            signature_x509_cert_der=self.dte_3_xml_cert_der,
            emisor_giro='Venta de calzado, accesorios y prendas de vestir',
            emisor_email=None,
            receptor_email=None,
            referencias=[
                DteXmlReferencia(
                    numero_linea_ref=1,
                    tipo_documento_ref='33',
                    folio_ref='115885',
                    fecha_ref=date(2019, 8, 2),
                    ind_global=None,
                    rut_otro=None,
                    codigo_ref=3,
                    razon_ref='Comision venta corner Hites',
                ),
            ],
        )

    def test_constants_match(self) -> None:
        self.assertEqual(
            DteXmlData.DATETIME_FIELDS_TZ,
            DteDataL2.DATETIME_FIELDS_TZ,
        )

    def test_validate_emisor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_receptor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_emisor_razon_social_none(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_razon_social',),
                'msg': 'Input should be a valid string',
                'type': 'string_type',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social=None,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_receptor_razon_social_none(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': 'Input should be a valid string',
                'type': 'string_type',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social=None,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:
        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                firma_documento_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': (
                    'Value error, ('
                    '''"Timezone of datetime value must be 'America/Santiago'.",'''
                    ' datetime.datetime(2019, 4, 5, 12, 57, 32, tzinfo=<UTC>)'
                    ')'
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_init_fail_regression_signature_value_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True),
        )

        init_kwars = self.dte_xml_data_1.as_dict()
        init_kwars.update(dict(signature_value=bytes_value_with_x20))

        # with self.assertRaises(ValueError) as cm:
        #     _ = DteXmlData(**init_kwars)
        # self.assertEqual(
        #     cm.exception.args,
        #     ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        # )
        _ = DteXmlData(**init_kwars)

    def test_validate_non_empty_bytes_signature_value(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('signature_value',),
                'msg': 'Value error, Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                signature_value=b'',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_init_fail_regression_signature_cert_der_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True),
        )

        init_kwars = self.dte_xml_data_1.as_dict()
        init_kwars.update(dict(signature_x509_cert_der=bytes_value_with_x20))

        # with self.assertRaises(ValueError) as cm:
        #     _ = DteXmlData(**init_kwars)
        # self.assertEqual(
        #     cm.exception.args,
        #     ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        # )
        _ = DteXmlData(**init_kwars)

    def test_validate_non_empty_bytes_signature_x509_cert_der(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('signature_x509_cert_der',),
                'msg': 'Value error, Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                signature_x509_cert_der=b'',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': (
                    "Value error, "
                    "('Value has leading or trailing whitespace characters.', ' NASA ')"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_giro=' NASA ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': (
                    "Value error, ("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_emisor_email@test.cl '"
                    ")"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_email=' fake_emisor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': (
                    "Value error, ("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_receptor_email@test.cl '"
                    ")"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_email=' fake_receptor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_giro='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_non_empty_stripped_str_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': "Value error, String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_xml_data_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
                referencias=[
                    dict(
                        numero_linea_ref=1,
                        tipo_documento_ref='801',
                        ind_global=None,
                        folio_ref='638370',
                        rut_otro=None,
                        fecha_ref=date(2019, 3, 28),
                        codigo_ref=None,
                        razon_ref=None,
                    ),
                    dict(
                        numero_linea_ref=2,
                        tipo_documento_ref='HES',
                        ind_global=None,
                        folio_ref='1001055906',
                        rut_otro=None,
                        fecha_ref=date(2019, 3, 28),
                        codigo_ref=None,
                        razon_ref=None,
                    ),
                ],
            ),
        )
        self.assertDictEqual(
            self.dte_xml_data_2.as_dict(),
            dict(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
                referencias=None,
            ),
        )

    def test_as_dte_data_l1(self) -> None:
        self.assertEqual(
            self.dte_xml_data_1.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            ),
        )
        self.assertEqual(
            self.dte_xml_data_2.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
            ),
        )

    def test_as_dte_data_l2(self) -> None:
        self.assertEqual(
            self.dte_xml_data_1.as_dte_data_l2(),
            DteDataL2(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
            ),
        )
        self.assertEqual(
            self.dte_xml_data_2.as_dte_data_l2(),
            DteDataL2(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            ),
        )

    def test_validate_referencias_numero_linea_ref_order(self) -> None:
        obj = self.dte_xml_data_1

        expected_validation_errors = [
            {
                'loc': ('referencias',),
                'msg': (
                    "Value error, items must be ordered according to their 'numero_linea_ref'. "
                    "All numero_linea_refs: 2, 1"
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=list(reversed(obj.referencias)),
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_referencias_rut_otro_is_consistent_with_tipo_dte(self) -> None:
        obj = self.dte_xml_data_2
        obj_referencia = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="1",
            fecha_ref=date(2019, 3, 28),
            ind_global=None,
            rut_otro=Rut('76354771-K'),
            codigo_ref=None,
            razon_ref=None,
        )

        expected_validation_errors = [
            {
                'loc': (),
                'msg': (
                    "Value error, "
                    "Setting a 'rut_otro' is not a valid option for this 'tipo_dte':"
                    " 'tipo_dte' == <TipoDte.FACTURA_ELECTRONICA: 33>,"
                    " 'Referencia' number 1."
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_referencias_rut_otro_is_consistent_with_tipo_dte_for_trusted_input(
        self,
    ) -> None:
        obj = self.dte_xml_data_2
        obj_referencia = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="1",
            fecha_ref=date(2019, 3, 28),
            ind_global=None,
            rut_otro=Rut('76354771-K'),
            codigo_ref=None,
            razon_ref=None,
        )

        expected_log_msg = (
            "Validation failed but input is trusted: "
            "Setting a 'rut_otro' is not a valid option for this 'tipo_dte':"
            " 'tipo_dte' == <TipoDte.FACTURA_ELECTRONICA: 33>,"
            " 'Referencia' number 1."
        )

        invalid_but_trusted_obj: Mapping[str, object] = {
            **DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER.dump_python(obj),
            **dict(
                referencias=[obj_referencia],
            ),
        }
        validation_context = {VALIDATION_CONTEXT_TRUST_INPUT: True}

        try:
            with self.assertLogs('cl_sii.dte.data_models', level='WARNING') as assert_logs_cm:
                DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER.validate_python(
                    invalid_but_trusted_obj, context=validation_context
                )
        except pydantic.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        self.assertEqual(assert_logs_cm.records[0].getMessage(), expected_log_msg)

    def test_validate_referencias_rut_otro_is_consistent_with_emisor_rut(self) -> None:
        obj = self.dte_xml_data_2
        obj = dataclasses.replace(
            obj,
            tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
        )
        obj_referencia = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="1",
            fecha_ref=date(2019, 3, 28),
            ind_global=None,
            rut_otro=Rut('60910000-1'),
            codigo_ref=None,
            razon_ref=None,
        )

        expected_validation_errors = [
            {
                'loc': (),
                'msg': (
                    "Value error, "
                    "'rut_otro' must be different from 'emisor_rut':"
                    " Rut('60910000-1') == Rut('60910000-1'),"
                    " 'Referencia' number 1."
                ),
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_referencias_rut_otro_is_consistent_with_emisor_rut_for_trusted_input(
        self,
    ) -> None:
        obj = self.dte_xml_data_2
        obj = dataclasses.replace(
            obj,
            tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
        )
        obj_referencia = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="1",
            fecha_ref=date(2019, 3, 28),
            ind_global=None,
            rut_otro=Rut('60910000-1'),
            codigo_ref=None,
            razon_ref=None,
        )

        expected_log_msg = (
            "Validation failed but input is trusted: "
            "'rut_otro' must be different from 'emisor_rut':"
            " Rut('60910000-1') == Rut('60910000-1'),"
            " 'Referencia' number 1."
        )

        invalid_but_trusted_obj: Mapping[str, object] = {
            **DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER.dump_python(obj),
            **dict(
                referencias=[obj_referencia],
            ),
        }
        validation_context = {VALIDATION_CONTEXT_TRUST_INPUT: True}

        try:
            with self.assertLogs('cl_sii.dte.data_models', level='WARNING') as assert_logs_cm:
                DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER.validate_python(
                    invalid_but_trusted_obj, context=validation_context
                )
        except pydantic.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        self.assertEqual(assert_logs_cm.records[0].getMessage(), expected_log_msg)

    def test_validate_referencias_codigo_ref_is_consistent_with_tipo_dte(self) -> None:
        obj = self.dte_xml_data_3
        obj_referencia = dataclasses.replace(
            obj.referencias[0],
            codigo_ref=None,
        )

        expected_validation_errors = [
            {
                'loc': (),
                'msg': "Value error, 'codigo_ref' is mandatory for this 'tipo_dte':"
                " 'tipo_dte' == <TipoDte.NOTA_CREDITO_ELECTRONICA: 61>,"
                " 'Referencia' number 1.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)


class FunctionsTest(unittest.TestCase):
    def test_validate_contribuyente_razon_social(self) -> None:
        # TODO: implement for 'validate_contribuyente_razon_social'
        pass

    def test_validate_dte_folio(self) -> None:
        # TODO: implement for 'validate_dte_folio'
        pass

    def test_validate_dte_monto_total_with_valid_values(self) -> None:
        # Test value '0':
        for tipo_dte in TipoDte:
            try:
                validate_dte_monto_total(0, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test value '1':
        for tipo_dte in TipoDte:
            try:
                validate_dte_monto_total(1, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test value '-1':
        for tipo_dte in TipoDte:
            if tipo_dte == TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
                try:
                    validate_dte_monto_total(-1, tipo_dte)
                except ValueError as e:
                    self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test maximum value:
        for tipo_dte in TipoDte:
            try:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MAX_VALUE, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test minimum value:
        for tipo_dte in TipoDte:
            if tipo_dte == TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
                dte_monto_total_field_min_value = DTE_MONTO_TOTAL_FIELD_MIN_VALUE
            else:
                dte_monto_total_field_min_value = 0

            try:
                validate_dte_monto_total(dte_monto_total_field_min_value, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

    def test_validate_dte_monto_total_with_invalid_values(self) -> None:
        expected_exc_msg = "Value is out of the valid range for 'monto_total'."

        # Test value that is too large:
        for tipo_dte in TipoDte:
            with self.assertRaises(ValueError) as assert_raises_cm:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MAX_VALUE + 1, tipo_dte)
            self.assertEqual(str(assert_raises_cm.exception), expected_exc_msg)

        # Test value that is too small:
        for tipo_dte in TipoDte:
            with self.assertRaises(ValueError) as assert_raises_cm:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MIN_VALUE - 1, tipo_dte)
            self.assertEqual(str(assert_raises_cm.exception), expected_exc_msg)

        # Test value that is negative:
        for tipo_dte in TipoDte:
            if tipo_dte != TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
                with self.assertRaises(ValueError) as assert_raises_cm:
                    validate_dte_monto_total(-1, tipo_dte)
                self.assertEqual(str(assert_raises_cm.exception), expected_exc_msg)

    def test_validate_clean_str(self) -> None:
        # TODO: implement for 'validate_clean_str'
        pass

    def test_validate_clean_bytes(self) -> None:
        # TODO: implement for 'validate_clean_bytes'
        pass

    def test_validate_non_empty_str(self) -> None:
        # TODO: implement for 'validate_non_empty_str'
        pass

    def test_validate_non_empty_bytes(self) -> None:
        # TODO: implement for 'validate_non_empty_bytes'
        pass
