import base64
import dataclasses
import unittest
from datetime import date, datetime

import pydantic

from cl_sii.libs import encoding_utils
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut  # noqa: F401

from cl_sii.dte.constants import (  # noqa: F401
    DTE_FOLIO_FIELD_MAX_VALUE,
    DTE_FOLIO_FIELD_MIN_VALUE,
    DTE_MONTO_TOTAL_FIELD_MAX_VALUE,
    DTE_MONTO_TOTAL_FIELD_MIN_VALUE,
    TipoDteEnum,
)
from cl_sii.dte.data_models import (  # noqa: F401
    DteDataL0, DteDataL1, DteDataL2, DteNaturalKey, DteXmlData,
    validate_contribuyente_razon_social, validate_dte_folio, validate_dte_monto_total,
)

from .utils import read_test_file_bytes


class DteNaturalKeyTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_nk_1 = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_validate_folio_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('folio',),
                'msg': "Value is out of the valid range for 'folio'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field folio
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_nk_1,
                folio=DTE_FOLIO_FIELD_MIN_VALUE - 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Validate the maximum value of the field folio
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_nk_1,
                folio=DTE_FOLIO_FIELD_MAX_VALUE + 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_nk_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            )
        )

    def test_slug(self) -> None:
        self.assertEqual(self.dte_nk_1.slug, '76354771-K--33--170')


class DteDataL0Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_l0_1 = DteDataL0(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l0_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ))

    def test_natural_key(self) -> None:
        self.assertEqual(
            self.dte_l0_1.natural_key,
            DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ))


class DteDataL1Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_l1_1 = DteDataL1(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
        )

    def test_is_ok_negative_monto_total_in_tipo_dte_liquidacion_factura(self) -> None:
        try:
            _ = dataclasses.replace(
                self.dte_l1_1,
                tipo_dte=TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA,
                monto_total=-1,
            )
        except pydantic.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

    def test_validate_monto_total_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('monto_total',),
                'msg': "Value is out of the valid range for 'monto_total'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field monto_total
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=DTE_MONTO_TOTAL_FIELD_MIN_VALUE - 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Validate the maximum value of the field monto_total
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=DTE_MONTO_TOTAL_FIELD_MAX_VALUE + 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Validate the minimum value of the field monto_total
        # for a tipo_dte FACTURA_ELECTRONICA
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l1_1,
                monto_total=-1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l1_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            ))

    def test_vendedor_rut_comprador_rut(self) -> None:
        emisor_rut = self.dte_l1_1.emisor_rut
        receptor_rut = self.dte_l1_1.receptor_rut
        dte_factura_venta = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA)
        dte_factura_venta_exenta = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDteEnum.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA)
        dte_factura_compra = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDteEnum.FACTURA_COMPRA_ELECTRONICA)
        dte_nota_credito = dataclasses.replace(
            self.dte_l1_1, tipo_dte=TipoDteEnum.NOTA_CREDITO_ELECTRONICA)

        # 'vendedor_rut'
        self.assertEqual(dte_factura_venta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_venta_exenta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_compra.vendedor_rut, receptor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.vendedor_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concept \"vendedor\" does not apply for this 'tipo_dte'.", dte_nota_credito.tipo_dte))

        # 'comprador_rut'
        self.assertEqual(dte_factura_venta.comprador_rut, receptor_rut)
        self.assertEqual(dte_factura_venta_exenta.comprador_rut, receptor_rut)
        self.assertEqual(dte_factura_compra.comprador_rut, emisor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.comprador_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concepts \"comprador\" and \"deudor\" do not apply for this 'tipo_dte'.",
             dte_nota_credito.tipo_dte))

        # 'deudor_rut'
        self.assertEqual(dte_factura_venta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_venta_exenta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_compra.deudor_rut, emisor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.deudor_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concepts \"comprador\" and \"deudor\" do not apply for this 'tipo_dte'.",
             dte_nota_credito.tipo_dte))


class DteDataL2Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_1_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'))
        cls.dte_1_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der')
        cls.dte_2_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-signature-value-base64.txt'))
        cls.dte_2_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der')

    def setUp(self) -> None:
        super().setUp()

        self.dte_l2_1 = DteDataL2(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=DteDataL2.DATETIME_FIELDS_TZ),
            signature_value=self.dte_1_xml_signature_value,
            signature_x509_cert_der=self.dte_1_xml_cert_der,
            emisor_giro='Ingenieria y Construccion',
            emisor_email='hello@example.com',
            receptor_email=None,
        )
        self.dte_l2_2 = DteDataL2(
            emisor_rut=Rut('60910000-1'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=2336600,
            fecha_emision_date=date(2019, 8, 8),
            receptor_rut=Rut('76555835-2'),
            monto_total=10642,
            emisor_razon_social='Universidad de Chile',
            receptor_razon_social='FYNPAL SPA',
            fecha_vencimiento_date=date(2019, 8, 8),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 9, 9, 41, 9),
                tz=DteDataL2.DATETIME_FIELDS_TZ),
            signature_value=self.dte_2_xml_signature_value,
            signature_x509_cert_der=self.dte_2_xml_cert_der,
            emisor_giro='Corporación Educacional y Servicios                 Profesionales',
            emisor_email=None,
            receptor_email=None,
        )

    def test_constants_match(self):
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
                'msg': "Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_receptor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': "Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                firma_documento_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg':
                    '('
                    '''"Timezone of datetime value must be 'America/Santiago'.",'''
                    ' datetime.datetime(2019, 4, 5, 12, 57, 32, tzinfo=<UTC>)'
                    ')',
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

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_init_fail_regression_signature_value_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

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
                'msg': 'Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                signature_value=b'',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_init_fail_regression_signature_cert_der_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

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
                'msg': 'Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                signature_x509_cert_der=b'',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "('Value has leading or trailing whitespace characters.', ' NASA ')",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_giro=' NASA ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg':
                    "("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_emisor_email@test.cl '"
                    ")",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_email=' fake_emisor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg':
                    "("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_receptor_email@test.cl '"
                    ")",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_email=' fake_receptor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_giro='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l2_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
            ))
        self.assertDictEqual(
            self.dte_l2_2.as_dict(),
            dict(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteDataL2.DATETIME_FIELDS_TZ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            ))

    def test_as_dte_data_l1(self) -> None:
        self.assertEqual(
            self.dte_l2_1.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            )
        )
        self.assertEqual(
            self.dte_l2_2.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
            )
        )


class DteXmlDataTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_1_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'))
        cls.dte_1_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der')
        cls.dte_2_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-signature-value-base64.txt'))
        cls.dte_2_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der')

    def setUp(self) -> None:
        super().setUp()

        self.dte_xml_data_1 = DteXmlData(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=DteXmlData.DATETIME_FIELDS_TZ),
            signature_value=self.dte_1_xml_signature_value,
            signature_x509_cert_der=self.dte_1_xml_cert_der,
            emisor_giro='Ingenieria y Construccion',
            emisor_email='hello@example.com',
            receptor_email=None,
        )
        self.dte_xml_data_2 = DteXmlData(
            emisor_rut=Rut('60910000-1'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=2336600,
            fecha_emision_date=date(2019, 8, 8),
            receptor_rut=Rut('76555835-2'),
            monto_total=10642,
            emisor_razon_social='Universidad de Chile',
            receptor_razon_social='FYNPAL SPA',
            fecha_vencimiento_date=date(2019, 8, 8),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 9, 9, 41, 9),
                tz=DteXmlData.DATETIME_FIELDS_TZ),
            signature_value=self.dte_2_xml_signature_value,
            signature_x509_cert_der=self.dte_2_xml_cert_der,
            emisor_giro='Corporación Educacional y Servicios                 Profesionales',
            emisor_email=None,
            receptor_email=None,
        )

    def test_constants_match(self):
        self.assertEqual(
            DteXmlData.DATETIME_FIELDS_TZ,
            DteDataL2.DATETIME_FIELDS_TZ,
        )

    def test_validate_emisor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_razon_social',),
                'msg': "Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_receptor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': "Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_emisor_razon_social_none(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_razon_social',),
                'msg': "none is not an allowed value",
                'type': 'type_error.none.not_allowed',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social=None,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_receptor_razon_social_none(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_razon_social',),
                'msg': "none is not an allowed value",
                'type': 'type_error.none.not_allowed',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social=None,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                firma_documento_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('firma_documento_dt',),
                'msg':
                    '('
                    '''"Timezone of datetime value must be 'America/Santiago'.",'''
                    ' datetime.datetime(2019, 4, 5, 12, 57, 32, tzinfo=<UTC>)'
                    ')',
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

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_init_fail_regression_signature_value_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

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
                'msg': 'Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                signature_value=b'',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_init_fail_regression_signature_cert_der_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

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
                'msg': 'Bytes value length is 0.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                signature_x509_cert_der=b'',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "('Value has leading or trailing whitespace characters.', ' NASA ')",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_giro=' NASA ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg':
                    "("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_emisor_email@test.cl '"
                    ")",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_email=' fake_emisor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_no_leading_or_trailing_whitespace_characters_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg':
                    "("
                    "'Value has leading or trailing whitespace characters.', "
                    "' fake_receptor_email@test.cl '"
                    ")",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_email=' fake_receptor_email@test.cl ',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_emisor_giro(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_giro',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_giro='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_emisor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('emisor_email',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_non_empty_stripped_str_receptor_email(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('receptor_email',),
                'msg': "String value length (stripped) is 0.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_email='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_xml_data_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteXmlData.DATETIME_FIELDS_TZ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
            ))
        self.assertDictEqual(
            self.dte_xml_data_2.as_dict(),
            dict(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteXmlData.DATETIME_FIELDS_TZ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            ))

    def test_as_dte_data_l1(self) -> None:
        self.assertEqual(
            self.dte_xml_data_1.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            )
        )
        self.assertEqual(
            self.dte_xml_data_2.as_dte_data_l1(),
            DteDataL1(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
            )
        )

    def test_as_dte_data_l2(self) -> None:
        self.assertEqual(
            self.dte_xml_data_1.as_dte_data_l2(),
            DteDataL2(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 1, 1, 36, 40),
                    tz=DteXmlData.DATETIME_FIELDS_TZ),
                signature_value=self.dte_1_xml_signature_value,
                signature_x509_cert_der=self.dte_1_xml_cert_der,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='hello@example.com',
                receptor_email=None,
            )
        )
        self.assertEqual(
            self.dte_xml_data_2.as_dte_data_l2(),
            DteDataL2(
                emisor_rut=Rut('60910000-1'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=2336600,
                fecha_emision_date=date(2019, 8, 8),
                receptor_rut=Rut('76555835-2'),
                monto_total=10642,
                emisor_razon_social='Universidad de Chile',
                receptor_razon_social='FYNPAL SPA',
                fecha_vencimiento_date=date(2019, 8, 8),
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 8, 9, 9, 41, 9),
                    tz=DteXmlData.DATETIME_FIELDS_TZ),
                signature_value=self.dte_2_xml_signature_value,
                signature_x509_cert_der=self.dte_2_xml_cert_der,
                emisor_giro='Corporación Educacional y Servicios                 Profesionales',
                emisor_email=None,
                receptor_email=None,
            )
        )


class FunctionsTest(unittest.TestCase):

    def test_validate_contribuyente_razon_social(self) -> None:
        # TODO: implement for 'validate_contribuyente_razon_social'
        pass

    def test_validate_dte_folio(self) -> None:
        # TODO: implement for 'validate_dte_folio'
        pass

    def test_validate_dte_monto_total_with_valid_values(self) -> None:
        # Test value '0':
        for tipo_dte in TipoDteEnum:
            try:
                validate_dte_monto_total(0, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test value '1':
        for tipo_dte in TipoDteEnum:
            try:
                validate_dte_monto_total(1, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test value '-1':
        for tipo_dte in TipoDteEnum:
            if tipo_dte == TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
                try:
                    validate_dte_monto_total(-1, tipo_dte)
                except ValueError as e:
                    self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test maximum value:
        for tipo_dte in TipoDteEnum:
            try:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MAX_VALUE, tipo_dte)
            except ValueError as e:
                self.fail('{exc_name} raised'.format(exc_name=type(e).__name__))

        # Test minimum value:
        for tipo_dte in TipoDteEnum:
            if tipo_dte == TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
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
        for tipo_dte in TipoDteEnum:
            with self.assertRaises(ValueError) as assert_raises_cm:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MAX_VALUE + 1, tipo_dte)
            self.assertEqual(str(assert_raises_cm.exception), expected_exc_msg)

        # Test value that is too small:
        for tipo_dte in TipoDteEnum:
            with self.assertRaises(ValueError) as assert_raises_cm:
                validate_dte_monto_total(DTE_MONTO_TOTAL_FIELD_MIN_VALUE - 1, tipo_dte)
            self.assertEqual(str(assert_raises_cm.exception), expected_exc_msg)

        # Test value that is negative:
        for tipo_dte in TipoDteEnum:
            if tipo_dte != TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
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
