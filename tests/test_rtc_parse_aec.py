from __future__ import annotations

import unittest
from datetime import date, datetime

from cl_sii.dte.data_models import DteDataL1, DteXmlData
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.dte.parse import DTE_XMLNS
from cl_sii.libs import encoding_utils
from cl_sii.libs import tz_utils
from cl_sii.libs import xml_utils
from cl_sii.rut import Rut

from cl_sii.rtc.data_models_aec import CesionAecXml, AecXml
from cl_sii.rtc.parse_aec import AEC_XML_SCHEMA_OBJ, parse_aec_xml, validate_aec_xml

from .utils import read_test_file_bytes


class AecXmlSchemaTest(unittest.TestCase):
    """
    Tests for AEC XML schema.
    """

    @unittest.skip("TODO: Implement for 'AEC_XML_SCHEMA_OBJ'.")
    def test_AEC_XML_SCHEMA_OBJ(self):
        self.assertIsNotNone(AEC_XML_SCHEMA_OBJ)


class AecXmlValidatorTest(unittest.TestCase):
    """
    Tests for :func:`validate_aec_xml`.
    """

    def _set_obj_1(self) -> None:
        aec_xml_bytes: bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml',
        )

        self.aec_1_xml_bytes = aec_xml_bytes

    def _set_obj_2(self) -> None:
        aec_xml_bytes: bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76399752-9--33--25568--SEQ-1.xml',
        )

        self.aec_2_xml_bytes = aec_xml_bytes

    def test_validate_aec_xml_ok_1(self) -> None:
        self._set_obj_1()

        aec_xml_bytes = self.aec_1_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(aec_xml_bytes)
        try:
            validate_aec_xml(xml_doc)
        except xml_utils.XmlSchemaDocValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        expected_xml_root_tag = '{%s}AEC' % DTE_XMLNS
        self.assertEqual(xml_doc.getroottree().getroot().tag, expected_xml_root_tag)

    def test_validate_aec_xml_ok_2(self) -> None:
        self._set_obj_2()

        aec_xml_bytes = self.aec_2_xml_bytes
        xml_doc = xml_utils.parse_untrusted_xml(aec_xml_bytes)
        try:
            validate_aec_xml(xml_doc)
        except xml_utils.XmlSchemaDocValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        expected_xml_root_tag = '{%s}AEC' % DTE_XMLNS
        self.assertEqual(xml_doc.getroottree().getroot().tag, expected_xml_root_tag)

    @unittest.skip("TODO: Implement for 'validate_aec_xml'.")
    def test_validate_aec_xml_fail(self) -> None:
        self.assertIsNotNone(validate_aec_xml)


class AecXmlParserTest(unittest.TestCase):
    """
    Tests for :func:`parse_aec_xml`.
    """

    def _set_obj_1(self) -> None:
        aec_xml_bytes: bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml',
        )

        aec_signature_value: bytes = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/AEC--76354771-K--33--170--SEQ-2-signature-value-base64.txt',
            ),
        )

        aec_cert_der_bytes: bytes = read_test_file_bytes(
            'test_data/sii-crypto/AEC--76354771-K--33--170--SEQ-2-cert.der',
        )

        aec_dte_cert_der_bytes: bytes = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der',
        )

        aec_dte_signature_value: bytes = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt',
            ),
        )

        self.aec_1_xml_bytes = aec_xml_bytes
        self.aec_1_signature_value = aec_signature_value
        self.aec_1_cert_der_bytes = aec_cert_der_bytes
        self.aec_1_dte_cert_der_bytes = aec_dte_cert_der_bytes
        self.aec_1_dte_signature_value = aec_dte_signature_value

    def _set_obj_2(self) -> None:
        aec_xml_bytes: bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76399752-9--33--25568--SEQ-1.xml',
        )

        aec_signature_value: bytes = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/AEC--76399752-9--33--25568--SEQ-1-signature-value-base64.txt',
            ),
        )

        aec_cert_der_bytes: bytes = read_test_file_bytes(
            'test_data/sii-crypto/AEC--76399752-9--33--25568--SEQ-1-cert.der',
        )

        aec_dte_cert_der_bytes: bytes = read_test_file_bytes(
            'test_data/sii-crypto/DTE--76399752-9--33--25568-cert.der',
        )

        aec_dte_signature_value: bytes = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76399752-9--33--25568-signature-value-base64.txt',
            ),
        )

        self.aec_2_xml_bytes = aec_xml_bytes
        self.aec_2_signature_value = aec_signature_value
        self.aec_2_cert_der_bytes = aec_cert_der_bytes
        self.aec_2_dte_cert_der_bytes = aec_dte_cert_der_bytes
        self.aec_2_dte_signature_value = aec_dte_signature_value

    def test_parse_aec_xml_ok_1(self) -> None:
        self._set_obj_1()

        aec_xml_bytes = self.aec_1_xml_bytes
        aec_signature_value = self.aec_1_signature_value
        aec_cert_der_bytes = self.aec_1_cert_der_bytes
        aec_dte_signature_value = self.aec_1_dte_signature_value
        aec_dte_cert_der_bytes = self.aec_1_dte_cert_der_bytes
        expected_output = AecXml(
            dte=DteXmlData(
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
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=aec_dte_signature_value,
                signature_x509_cert_der=aec_dte_cert_der_bytes,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='ENACONLTDA@GMAIL.COM',
                receptor_email=None,
            ),
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_firma_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=AecXml.DATETIME_FIELDS_TZ,
            ),
            signature_value=aec_signature_value,
            signature_x509_cert_der=aec_cert_der_bytes,
            cesiones=[
                CesionAecXml(
                    dte=DteDataL1(
                        emisor_rut=Rut('76354771-K'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=170,
                        fecha_emision_date=date(2019, 4, 1),
                        receptor_rut=Rut('96790240-3'),
                        monto_total=2996301,
                    ),
                    seq=1,
                    cedente_rut=Rut('76354771-K'),
                    cesionario_rut=Rut('76389992-6'),
                    monto_cesion=2996301,
                    fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                        dt=datetime(2019, 4, 1, 10, 22, 2),
                        tz=CesionAecXml.DATETIME_FIELDS_TZ,
                    ),
                    fecha_ultimo_vencimiento=date(2019, 5, 1),
                    cedente_razon_social='SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA LIMITADA',
                    cedente_direccion='MERCED 753  16 ARBOLEDA DE QUIILOTA',
                    cedente_email='enaconltda@gmail.com',
                    cedente_persona_autorizada_rut=Rut('76354771-K'),
                    cedente_persona_autorizada_nombre='SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA LIM',
                    cesionario_razon_social='ST CAPITAL S.A.',
                    cesionario_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cesionario_email='fynpal-app-notif-st-capital@fynpal.com',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA '
                        'LIMITADA, RUT 76354771-K ha puesto a disposición del cesionario ST '
                        'CAPITAL S.A., RUT 76389992-6, el o los documentos donde constan los '
                        'recibos de las mercaderías entregadas o servicios prestados, entregados '
                        'por parte del deudor de la factura MINERA LOS PELAMBRES, RUT 96790240-3, '
                        'deacuerdo a lo establecido en la Ley N°19.983.'
                    ),
                ),
                CesionAecXml(
                    dte=DteDataL1(
                        emisor_rut=Rut('76354771-K'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=170,
                        fecha_emision_date=date(2019, 4, 1),
                        receptor_rut=Rut('96790240-3'),
                        monto_total=2996301,
                    ),
                    seq=2,
                    cedente_rut=Rut('76389992-6'),
                    cesionario_rut=Rut('76598556-0'),
                    monto_cesion=2996301,
                    fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                        dt=datetime(2019, 4, 5, 12, 57, 32),
                        tz=CesionAecXml.DATETIME_FIELDS_TZ,
                    ),
                    fecha_ultimo_vencimiento=date(2019, 5, 1),
                    cedente_razon_social='ST CAPITAL S.A.',
                    cedente_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cedente_email='APrat@Financiaenlinea.com',
                    cesionario_razon_social='Fondo de Inversión Privado Deuda y Facturas',
                    cesionario_direccion='Arrayan 2750 Oficina 703 Providencia',
                    cesionario_email='solicitudes@stcapital.cl',
                    cedente_persona_autorizada_rut=Rut('16360379-9'),
                    cedente_persona_autorizada_nombre='ANDRES  PRATS VIAL',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que ST CAPITAL S.A., RUT 76389992-6 ha puesto '
                        'a disposicion del cesionario Fondo de Inversión Privado Deuda y Facturas, '
                        'RUT 76598556-0, el documento validamente emitido al deudor MINERA LOS '
                        'PELAMBRES, RUT 96790240-3.'
                    ),
                ),
            ],
            contacto_nombre='ST Capital Servicios Financieros',
            contacto_telefono=None,
            contacto_email='APrat@Financiaenlinea.com',
        )

        xml_doc = xml_utils.parse_untrusted_xml(aec_xml_bytes)
        aec_xml = parse_aec_xml(xml_doc)
        self.assertEqual(aec_xml, expected_output)

    def test_parse_aec_xml_ok_2(self) -> None:
        self._set_obj_2()

        aec_xml_bytes = self.aec_2_xml_bytes
        aec_signature_value = self.aec_2_signature_value
        aec_cert_der_bytes = self.aec_2_cert_der_bytes
        aec_dte_signature_value = self.aec_2_dte_signature_value
        aec_dte_cert_der_bytes = self.aec_2_dte_cert_der_bytes
        expected_output = AecXml(
            dte=DteXmlData(
                emisor_rut=Rut('76399752-9'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=25568,
                fecha_emision_date=date(2019, 3, 29),
                receptor_rut=Rut('96874030-K'),
                monto_total=230992,
                emisor_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                receptor_razon_social='EMPRESAS LA POLAR S.A.',
                fecha_vencimiento_date=None,
                firma_documento_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 3, 28, 13, 59, 52),
                    tz=DteXmlData.DATETIME_FIELDS_TZ,
                ),
                signature_value=aec_dte_signature_value,
                signature_x509_cert_der=aec_dte_cert_der_bytes,
                emisor_giro='COMERCIALIZACION DE PRODUCTOS PARA EL HOGAR',
                emisor_email='ANGEL.PEZO@APCASESORIAS.CL',
                receptor_email=None,
            ),
            cedente_rut=Rut('76399752-9'),
            cesionario_rut=Rut('76389992-6'),
            fecha_firma_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 4, 9, 9, 52),
                tz=AecXml.DATETIME_FIELDS_TZ,
            ),
            signature_value=aec_signature_value,
            signature_x509_cert_der=aec_cert_der_bytes,
            cesiones=[
                CesionAecXml(
                    dte=DteDataL1(
                        emisor_rut=Rut('76399752-9'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=25568,
                        fecha_emision_date=date(2019, 3, 29),
                        receptor_rut=Rut('96874030-K'),
                        monto_total=230992,
                    ),
                    seq=1,
                    cedente_rut=Rut('76399752-9'),
                    cesionario_rut=Rut('76389992-6'),
                    monto_cesion=230992,
                    fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                        dt=datetime(2019, 4, 4, 9, 9, 52),
                        tz=CesionAecXml.DATETIME_FIELDS_TZ,
                    ),
                    fecha_ultimo_vencimiento=date(2019, 4, 28),
                    cedente_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                    cedente_direccion='LOS CIPRESES 2834',
                    cedente_email='camilo.perez@innovamobel.cl',
                    cedente_persona_autorizada_rut=Rut('76399752-9'),
                    cedente_persona_autorizada_nombre='COMERCIALIZADORA INNOVA MOBEL SPA',
                    cesionario_razon_social='ST CAPITAL S.A.',
                    cesionario_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cesionario_email='fynpal-app-notif-st-capital@fynpal.com',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que COMERCIALIZADORA INNOVA MOBEL SPA, RUT '
                        '76399752-9 ha puesto a disposición del cesionario ST CAPITAL S.A., RUT '
                        '76389992-6, el o los documentos donde constan los recibos de las '
                        'mercaderías entregadas o servicios prestados, entregados por parte del '
                        'deudor de la factura EMPRESAS LA POLAR S.A., RUT 96874030-K, deacuerdo a '
                        'lo establecido en la Ley N°19.983.'
                    ),
                ),
            ],
            contacto_nombre=None,
            contacto_telefono=None,
            contacto_email='fynpal-app-notif-st-capital@fynpal.com',
        )

        xml_doc = xml_utils.parse_untrusted_xml(aec_xml_bytes)
        aec_xml = parse_aec_xml(xml_doc)
        self.assertEqual(aec_xml, expected_output)
