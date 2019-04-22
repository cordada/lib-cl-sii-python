import unittest
from datetime import date, datetime

from cl_sii.dte.data_models import DteDataL1, DteDataL2
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.libs import crypto_utils
from cl_sii.libs import encoding_utils
from cl_sii.libs import xml_utils
from cl_sii.rut import Rut

from cl_sii.rtc.data_models_aec import AecXmlCesionData, AecXmlData
from cl_sii.rtc.parse_aec import parse_aec_xml_data, validate_aec_xml

from .utils import read_test_file_bytes


_TEST_AEC_1_FILE_PATH = 'tests/test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml'
_TEST_AEC_2_FILE_PATH = 'tests/test_data/sii-rtc/AEC--76399752-9--33--25568--SEQ-1.xml'


class OthersTest(unittest.TestCase):

    def test_AEC_XML_SCHEMA_OBJ(self):
        pass


class FunctionsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.aec_1_xml_bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml')
        cls.aec_2_xml_bytes = read_test_file_bytes(
            'test_data/sii-rtc/AEC--76399752-9--33--25568--SEQ-1.xml')

        cls.aec_1_dte_cert_pem_bytes = encoding_utils.clean_base64(
            crypto_utils.remove_pem_cert_header_footer(
                read_test_file_bytes('test_data/sii-crypto/DTE--76354771-K--33--170-cert.pem')))
        cls.aec_2_dte_cert_pem_bytes = encoding_utils.clean_base64(
            crypto_utils.remove_pem_cert_header_footer(
                read_test_file_bytes('test_data/sii-crypto/DTE--76399752-9--33--25568-cert.pem')))

        cls.aec_1_dte_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76354771-K--33--170-signature-value-base64.txt'))
        cls.aec_2_dte_signature_value = encoding_utils.decode_base64_strict(
            read_test_file_bytes(
                'test_data/sii-crypto/DTE--76399752-9--33--25568-signature-value-base64.txt'))

    def test_validate_aec_xml_ok_1(self) -> None:
        with open(_TEST_AEC_1_FILE_PATH, mode='rb') as f:
            xml_doc_1 = xml_utils.parse_untrusted_xml(f.read())

        self.assertIsNone(validate_aec_xml(xml_doc_1))

    def test_validate_aec_xml_ok_2(self) -> None:
        with open(_TEST_AEC_2_FILE_PATH, mode='rb') as f:
            xml_doc_2 = xml_utils.parse_untrusted_xml(f.read())

        self.assertIsNone(validate_aec_xml(xml_doc_2))

    def test_validate_aec_xml_fail(self) -> None:
        # TODO: implement for 'validate_aec_xml'
        pass

    def test_parse_aec_xml_data_ok_1(self) -> None:
        # TODO: split in separate tests, with more coverage.

        xml_doc = xml_utils.parse_untrusted_xml(self.aec_1_xml_bytes)

        aec_xml = parse_aec_xml_data(xml_doc)

        expected = AecXmlData(
            dte=DteDataL2(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt_naive=datetime(2019, 4, 1, 1, 36, 40),
                signature_value=self.aec_1_dte_signature_value,
                signature_x509_cert_pem=self.aec_1_dte_cert_pem_bytes,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='ENACONLTDA@GMAIL.COM',
                receptor_email=None,
            ),
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_firma_dt_naive=datetime(2019, 4, 5, 12, 57, 32),
            cesiones=[
                AecXmlCesionData(
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
                    monto=2996301,
                    fecha_cesion_dt_naive=datetime(2019, 4, 1, 10, 22, 2),
                    ultimo_vencimiento_date=date(2019, 5, 1),
                    cedente_razon_social='SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA LIMITADA',
                    cedente_direccion='MERCED 753  16 ARBOLEDA DE QUIILOTA',
                    cedente_email='enaconltda@gmail.com',
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
                AecXmlCesionData(
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
                    monto=2996301,
                    fecha_cesion_dt_naive=datetime(2019, 4, 5, 12, 57, 32),
                    ultimo_vencimiento_date=date(2019, 5, 1),
                    cedente_razon_social='ST CAPITAL S.A.',
                    cedente_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cedente_email='APrat@Financiaenlinea.com',
                    cesionario_razon_social='Fondo de Inversión Privado Deuda y Facturas',
                    cesionario_direccion='Arrayan 2750 Oficina 703 Providencia',
                    cesionario_email='solicitudes@stcapital.cl',
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

        self.assertEqual(aec_xml, expected)

    def test_parse_aec_xml_data_ok_2(self) -> None:
        # TODO: split in separate tests, with more coverage.

        xml_doc = xml_utils.parse_untrusted_xml(self.aec_2_xml_bytes)

        aec_xml = parse_aec_xml_data(xml_doc)

        expected = AecXmlData(
            dte=DteDataL2(
                emisor_rut=Rut('76399752-9'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=25568,
                fecha_emision_date=date(2019, 3, 29),
                receptor_rut=Rut('96874030-K'),
                monto_total=230992,
                emisor_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                receptor_razon_social='EMPRESAS LA POLAR S.A.',
                fecha_vencimiento_date=None,
                firma_documento_dt_naive=datetime(2019, 3, 28, 13, 59, 52),
                signature_value=self.aec_2_dte_signature_value,
                signature_x509_cert_pem=self.aec_2_dte_cert_pem_bytes,
                emisor_giro='COMERCIALIZACION DE PRODUCTOS PARA EL HOGAR',
                emisor_email='ANGEL.PEZO@APCASESORIAS.CL',
                receptor_email=None,
            ),
            cedente_rut=Rut('76399752-9'),
            cesionario_rut=Rut('76389992-6'),
            fecha_firma_dt_naive=datetime(2019, 4, 4, 9, 9, 52),
            cesiones=[
                AecXmlCesionData(
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
                    monto=230992,
                    fecha_cesion_dt_naive=datetime(2019, 4, 4, 9, 9, 52),
                    ultimo_vencimiento_date=date(2019, 4, 28),
                    cedente_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                    cedente_direccion='LOS CIPRESES 2834',
                    cedente_email='camilo.perez@innovamobel.cl',
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
                        'lo establecido en la Ley N°19.983.')
                ),
            ],
            contacto_nombre=None,
            contacto_telefono=None,
            contacto_email='fynpal-app-notif-st-capital@fynpal.com',
        )

        self.assertEqual(aec_xml, expected)
