import base64
import dataclasses
import unittest
from datetime import date, datetime

from cl_sii.libs import encoding_utils
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut  # noqa: F401

from cl_sii.dte.constants import TipoDteEnum  # noqa: F401
from cl_sii.dte.data_models import (  # noqa: F401
    DteDataL0, DteDataL1, DteDataL2, DteNaturalKey,
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

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteNaturalKey()'
        pass

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

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL0()'
        pass

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

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL1()'
        pass

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

    def test_vendedor_rut_deudor_rut(self) -> None:
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

        self.assertEqual(dte_factura_venta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_venta_exenta.vendedor_rut, emisor_rut)
        self.assertEqual(dte_factura_compra.vendedor_rut, receptor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.vendedor_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concept \"vendedor\" does not apply for this 'tipo_dte'.", dte_nota_credito.tipo_dte))

        self.assertEqual(dte_factura_venta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_venta_exenta.deudor_rut, receptor_rut)
        self.assertEqual(dte_factura_compra.deudor_rut, emisor_rut)
        with self.assertRaises(ValueError) as cm:
            self.assertIsNone(dte_nota_credito.deudor_rut)
        self.assertEqual(
            cm.exception.args,
            ("Concept \"deudor\" does not apply for this 'tipo_dte'.", dte_nota_credito.tipo_dte))


class DteDataL2Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dte_1_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'))
        cls.dte_1_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der')

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

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL2()'
        pass

    def test_init_fail_regression_signature_value_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

        init_kwars = self.dte_l2_1.as_dict()
        init_kwars.update(dict(signature_value=bytes_value_with_x20))

        with self.assertRaises(ValueError) as cm:
            _ = DteDataL2(**init_kwars)
        self.assertEqual(
            cm.exception.args,
            ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        )

    def test_init_fail_regression_signature_cert_der_bytes_with_x20(self) -> None:
        bytes_value_with_x20_as_base64 = 'IN2pkDBxqDnGl4Pfvboi'
        bytes_value_with_x20 = b'\x20\xdd\xa9\x900q\xa89\xc6\x97\x83\xdf\xbd\xba"'

        self.assertEqual(b'\x20', b' ')
        self.assertEqual(
            bytes_value_with_x20,
            base64.b64decode(bytes_value_with_x20_as_base64, validate=True))

        init_kwars = self.dte_l2_1.as_dict()
        init_kwars.update(dict(signature_x509_cert_der=bytes_value_with_x20))

        with self.assertRaises(ValueError) as cm:
            _ = DteDataL2(**init_kwars)
        self.assertEqual(
            cm.exception.args,
            ('Value has leading or trailing whitespace characters.', bytes_value_with_x20)
        )

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


class FunctionsTest(unittest.TestCase):

    def test_validate_contribuyente_razon_social(self) -> None:
        # TODO: implement for 'validate_contribuyente_razon_social'
        pass

    def test_validate_dte_folio(self) -> None:
        # TODO: implement for 'validate_dte_folio'
        pass

    def test_validate_dte_monto_total(self) -> None:
        # TODO: implement for 'validate_dte_monto_total'
        pass

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

    def test_validate_correct_tz(self) -> None:
        # TODO: implement for 'validate_correct_tz'
        pass
