import base64
import dataclasses
import unittest
from datetime import date, datetime

import pydantic

from cl_sii.libs import encoding_utils
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut  # noqa: F401

from cl_sii.dte.constants import (  # noqa: F401
    DTE_MONTO_TOTAL_FIELD_MIN_VALUE, DTE_MONTO_TOTAL_FIELD_MAX_VALUE,
    TipoDteEnum,
)
from cl_sii.dte.data_models import (  # noqa: F401
    DteDataL0, DteDataL1, DteDataL2, DteNaturalKey, DteXmlData, DteXmlReferencia,
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

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL2()'
        pass

    def test_init_fail_razon_social_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                self.dte_l2_1,
                emisor_razon_social='',
            )
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                self.dte_l2_1,
                receptor_razon_social='',
            )
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

    def test_init_ok_razon_social_none(self) -> None:
        _ = dataclasses.replace(
            self.dte_l2_1,
            emisor_razon_social=None,
            receptor_razon_social=None,
        )

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


class DteXmlReferenciaTest(unittest.TestCase):
    """
    Tests for :class:`DteXmlReferencia`.
    """

    def _set_obj_1(self) -> None:
        obj = DteXmlReferencia(
            numero_linea_ref=1,
            tipo_documento_ref="801",
            folio_ref="4769807823",
            fecha_ref=date(2021, 4, 16)
        )
        self.assertIsInstance(obj, DteXmlReferencia)

        self.obj_1 = obj

    def _set_obj_2(self) -> None:
        obj = DteXmlReferencia(
            numero_linea_ref=2,
            tipo_documento_ref="HES",
            folio_ref="1001055906",
            fecha_ref=date(2021, 4, 16)
        )
        self.assertIsInstance(obj, DteXmlReferencia)

        self.obj_2 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            DteXmlReferencia()

    def test_init_fail_numero_linea_ref_out_of_range(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                numero_linea_ref=0,
            )
        self.assertEqual(
            cm.exception.args,
            ("Value 'numero_linea_ref' must be a value between 1 and 40", 0)
        )
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                numero_linea_ref=41,
            )
        self.assertEqual(
            cm.exception.args,
            ("Value 'numero_linea_ref' must be a value between 1 and 40", 41)
        )

    def test_init_fail_tipo_documento_ref_invalid(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                tipo_documento_ref="8001",
            )
        self.assertEqual(
            cm.exception.args,
            ("The length of 'tipo_documento_ref' must be a value between 1 and 3", "8001")
        )
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                tipo_documento_ref="2BAD",
            )
        self.assertEqual(
            cm.exception.args,
            ("The length of 'tipo_documento_ref' must be a value between 1 and 3", "2BAD")
        )

    def test_init_fail_ind_global_invalid(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                ind_global=2,
            )
        self.assertEqual(
            cm.exception.args,
            ("Only the value \"1\" is valid for the field 'ind_global'", 2)
        )

    def test_init_fail_folio_ref_empty(self) -> None:
        self._set_obj_2()

        obj = self.obj_2

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                folio_ref="",
            )
        self.assertEqual(
            cm.exception.args,
            ("The length of 'folio_ref' must be a value between 1 and 18", '')
        )

    def test_init_fail_fecha_ref_out_of_range(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                fecha_ref=date(2002, 7, 31),
            )
        self.assertEqual(
            cm.exception.args,
            (
                "The date 'fecha_ref' must be after 2002-08-01 and before 2050-12-31",
                date(2002, 7, 31)
            )
        )
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                fecha_ref=date(2051, 1, 1),
            )
        self.assertEqual(
            cm.exception.args,
            (
                "The date 'fecha_ref' must be after 2002-08-01 and before 2050-12-31",
                date(2051, 1, 1)
            )
        )

    def test_init_fail_razon_ref_too_long(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                obj,
                razon_ref=(
                    'Lorem ipsum dolor sit amet, consectetur adipiscing '
                    'elit. Sed metus magna, ultricies sit amet dolor sed'
                ),
            )
        self.assertEqual(
            cm.exception.args,
            (
                "The maximum length allowed for `razon_ref` is 90",
                'Lorem ipsum dolor sit amet, consectetur adipiscing '
                'elit. Sed metus magna, ultricies sit amet dolor sed'
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
        cls.dte_3_xml_signature_value = encoding_utils.decode_base64_strict(read_test_file_bytes(
            'test_data/sii-crypto/DTE--96670340-7--61--110616-signature-value-base64.txt'))
        cls.dte_3_xml_cert_der = read_test_file_bytes(
            'test_data/sii-crypto/DTE--96670340-7--61--110616-cert.der')

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
            referencias=None,
        )
        self.dte_xml_data_3 = DteXmlData(
            emisor_rut=Rut('96670340-7'),
            tipo_dte=TipoDteEnum.NOTA_CREDITO_ELECTRONICA,
            folio=110616,
            fecha_emision_date=date(2019, 8, 2),
            receptor_rut=Rut('81675600-6'),
            monto_total=57347078,
            emisor_razon_social='Bata Chile S.A.',
            receptor_razon_social='Comercializadora S.A',
            fecha_vencimiento_date=date(2019, 9, 1),
            firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 8, 5, 15, 20, 6),
                tz=DteXmlData.DATETIME_FIELDS_TZ),
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

    def test_constants_match(self):
        self.assertEqual(
            DteXmlData.DATETIME_FIELDS_TZ,
            DteDataL2.DATETIME_FIELDS_TZ,
        )

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteXmlData()'
        pass

    def test_init_fail_razon_social_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social='',
            )
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))
        with self.assertRaises(ValueError) as cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social='',
            )
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

    def test_init_fail_razon_social_none(self) -> None:
        with self.assertRaises(TypeError) as cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                emisor_razon_social=None,
            )
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'emisor_razon_social'.", ))
        with self.assertRaises(TypeError) as cm:
            dataclasses.replace(
                self.dte_xml_data_1,
                receptor_razon_social=None,
            )
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'receptor_razon_social'.", ))

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
                referencias=None,
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

    def test_validate_referencias_numero_linea_ref_order(self) -> None:
        obj = self.dte_xml_data_1

        expected_validation_errors = [
            {
                'loc': ('referencias',),
                'msg': "items must be ordered according to their 'numero_linea_ref'",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=list(reversed(obj.referencias)),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

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
                'loc': ('__root__',),
                'msg':
                    "Setting a 'rut_otro' is not a valid option for this 'tipo_dte':"
                    " 'tipo_dte' == <TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
                    " 'Referencia' number 1.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_referencias_rut_otro_is_consistent_with_emisor_rut(self) -> None:
        obj = self.dte_xml_data_2
        obj = dataclasses.replace(
            obj,
            tipo_dte=TipoDteEnum.FACTURA_COMPRA_ELECTRONICA,
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
                'loc': ('__root__',),
                'msg':
                    "'rut_otro' must be different from 'emisor_rut':"
                    " Rut('60910000-1') == Rut('60910000-1'),"
                    " 'Referencia' number 1.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_referencias_codigo_ref_is_consistent_with_tipo_dte(self) -> None:
        obj = self.dte_xml_data_3
        obj_referencia = dataclasses.replace(
            obj.referencias[0],
            codigo_ref=None,
        )

        expected_validation_errors = [
            {
                'loc': ('__root__',),
                'msg':
                    "'codigo_ref' is mandatory for this 'tipo_dte':"
                    " 'tipo_dte' == <TipoDteEnum.NOTA_CREDITO_ELECTRONICA: 61>,"
                    " 'Referencia' number 1.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                referencias=[obj_referencia],
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


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
