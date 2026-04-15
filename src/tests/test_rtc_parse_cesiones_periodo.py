import tempfile
import unittest
from collections import OrderedDict
from datetime import date, datetime

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte.constants import TipoDte
from cl_sii.libs.tz_utils import convert_naive_dt_to_tz_aware
from cl_sii.rtc.data_models_cesiones_periodo import CesionesPeriodoEntry
from cl_sii.rtc.parse_cesiones_periodo import (
    clean_cesiones_periodo_csv_file,
    parse_cesiones_periodo_csv_file,
)
from cl_sii.rut import Rut


_CESIONES_PERIODO_CSV_FILE_1 = (
    b'DATOS_CONSULTA; RUT=75320502-0;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=01032019;'
    b'HASTA_DDMMAAAA=31032019\r\n'
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;33;Factura Electronica;3608534;'
    b'2019-02-15;96628;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;ejecutivo@pobres.cl;super.ejecutivo@pobres.cl;muy@pobres.cl;'  # noqa: E501
    b'2019-03-07 13:31;96628;2019-04-16\r\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;33;Factura Electronica;3608460;'
    b'2019-02-11;256357;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl;super.ejecutivo@pobres.cl;'
    b'2019-03-07 13:32;256357;2019-04-12\r\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 09:27;703771;2019-07-05\r\n'
)
_CESIONES_PERIODO_CSV_FILE_2 = (
    b'DATOS_CONSULTA; RUT=75320502-0;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=01032019;'
    b'HASTA_DDMMAAAA=31032019\r\n'
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;1;Factura Electronica;3608460;'
    b'2019-02-11;1.0;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl;super.ejecutivo@pobres.cl;'
    b'2019-03-07 13:32;1.0;2019\r\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 09:27;703771;2019-07-05\r\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 23:00;703771;2019-07-05\r\n'
)
_CESIONES_PERIODO_CSV_FILE_3 = (
    'DATOS_CONSULTA; RUT=75320502-0;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=01032019;'
    'HASTA_DDMMAAAA=31032019\r\n'
    'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    '51532520-4;Cesión Vigente;75320502-0;null;1;Factura Electrónica;3608460;'
    '2019-02-11;1.0;51532520-4;MI CAÑOPITO SA;mi@campito.cl;96667560-8;'
    'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl;super.ejecutivo@pobres.cl;'
    '2019-03-07 13:32;1.0;2019\r\n'
).encode('iso-8859-1')
_CESIONES_PERIODO_CSV_FILE_4 = (
    'DATOS_CONSULTA; RUT=75320502-0;TIPO_CONSULTA=DEUDOR;DESDE_DDMMAAAA=01032019;'
    'HASTA_DDMMAAAA=31032019\r\n'
    'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\r\n'
    '51532520-4;Cesión Vigente;75320502-0;null;1;Factura Electrónica;3608460;'
    '2019-02-11;1.0;51532520-4;MI CAÑOPITO SA;mi@campito.cl;96667560-8;'
    'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl;super.ejecutivo@pobres.cl;'
    '2019-03-07 13:32;1.0;2019\r\n'
).encode('utf-16')

# - sorted
# - without the query params line
# - '\r\n' -> '\n'
# - replace with ',' the unescaped ';' character used in email fields when there are
#   multiple values.
_CESIONES_PERIODO_CSV_FILE_1_CLEANED = (
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;33;Factura Electronica;3608460;'
    b'2019-02-11;256357;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl,super.ejecutivo@pobres.cl;'
    b'2019-03-07 13:32;256357;2019-04-12\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;33;Factura Electronica;3608534;'
    b'2019-02-15;96628;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;ejecutivo@pobres.cl,super.ejecutivo@pobres.cl,muy@pobres.cl;'  # noqa: E501
    b'2019-03-07 13:31;96628;2019-04-16\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 09:27;703771;2019-07-05\n'
)
_CESIONES_PERIODO_CSV_FILE_2_CLEANED = (
    b'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    b'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    b'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\n'
    b'51532520-4;Cesion Vigente;75320502-0;null;1;Factura Electronica;3608460;'
    b'2019-02-11;1.0;51532520-4;MI CAMPITO SA;mi@campito.cl;96667560-8;'
    b'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl,super.ejecutivo@pobres.cl;'
    b'2019-03-07 13:32;1.0;2019\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 09:27;703771;2019-07-05\n'
    b'83564146-5;Cesion Vigente;75320502-0;null;33;Factura Electronica;1113465;'
    b'2019-03-07;703771;83564146-5;MOYA S A;paga@moya.xyz;96932010-K;'
    b'Ricky S.A.;whatever@ricky.cl;'
    b'2019-03-26 23:00;703771;2019-07-05\n'
)
_CESIONES_PERIODO_CSV_FILE_3_CLEANED = (
    'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\n'
    '51532520-4;Cesión Vigente;75320502-0;null;1;Factura Electrónica;3608460;'
    '2019-02-11;1.0;51532520-4;MI CAÑOPITO SA;mi@campito.cl;96667560-8;'
    'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl,super.ejecutivo@pobres.cl;'
    '2019-03-07 13:32;1.0;2019\n'
).encode('iso-8859-1')
_CESIONES_PERIODO_CSV_FILE_4_CLEANED = (
    'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;'
    'FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;'
    'RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO\n'
    '51532520-4;Cesión Vigente;75320502-0;null;1;Factura Electrónica;3608460;'
    '2019-02-11;1.0;51532520-4;MI CAÑOPITO SA;mi@campito.cl;96667560-8;'
    'POBRES SERVICIOS FINANCIEROS S.A.;un-poco@pobres.cl,super.ejecutivo@pobres.cl;'
    '2019-03-07 13:32;1.0;2019\n'
).encode('utf-16')


class FunctionsTest(unittest.TestCase):
    def test_clean_cesiones_periodo_csv_file_ok_1(self) -> None:
        input_file_content = _CESIONES_PERIODO_CSV_FILE_1
        expected_output_file_content = _CESIONES_PERIODO_CSV_FILE_1_CLEANED

        # note: for the output we need 'w+b' to be able to read and write data.
        with tempfile.NamedTemporaryFile(mode='w+b') as output_tmp_file:
            with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
                input_tmp_file.write(input_file_content)
                input_tmp_file.flush()
                clean_cesiones_periodo_csv_file(input_tmp_file.name, output_tmp_file.name)
            output_tmp_file.seek(0)
            output_file_content = output_tmp_file.read()
        self.assertEqual(output_file_content, expected_output_file_content)

    def test_clean_cesiones_periodo_csv_file_ok_2(self) -> None:
        input_file_content = _CESIONES_PERIODO_CSV_FILE_2
        expected_output_file_content = _CESIONES_PERIODO_CSV_FILE_2_CLEANED

        # note: for the output we need 'w+b' to be able to read and write data.
        with tempfile.NamedTemporaryFile(mode='w+b') as output_tmp_file:
            with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
                input_tmp_file.write(input_file_content)
                input_tmp_file.flush()
                clean_cesiones_periodo_csv_file(input_tmp_file.name, output_tmp_file.name)
            output_tmp_file.seek(0)
            output_file_content = output_tmp_file.read()
        self.assertEqual(output_file_content, expected_output_file_content)

    def test_clean_cesiones_periodo_csv_file_ok_3(self) -> None:
        input_file_content = _CESIONES_PERIODO_CSV_FILE_3
        expected_output_file_content = _CESIONES_PERIODO_CSV_FILE_3_CLEANED

        # note: for the output we need 'w+b' to be able to read and write data.
        with tempfile.NamedTemporaryFile(mode='w+b') as output_tmp_file:
            with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
                input_tmp_file.write(input_file_content)
                input_tmp_file.flush()
                clean_cesiones_periodo_csv_file(input_tmp_file.name, output_tmp_file.name)
            output_tmp_file.seek(0)
            output_file_content = output_tmp_file.read()
        self.assertEqual(output_file_content, expected_output_file_content)

    def test_clean_cesiones_periodo_csv_file_ok_4(self) -> None:
        input_file_content = _CESIONES_PERIODO_CSV_FILE_4
        expected_output_file_content = _CESIONES_PERIODO_CSV_FILE_4_CLEANED

        # note: for the output we need 'w+b' to be able to read and write data.
        with tempfile.NamedTemporaryFile(mode='w+b') as output_tmp_file:
            with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
                input_tmp_file.write(input_file_content)
                input_tmp_file.flush()
                clean_cesiones_periodo_csv_file(input_tmp_file.name, output_tmp_file.name)
            output_tmp_file.seek(0)
            output_file_content = output_tmp_file.read()
        self.assertEqual(output_file_content, expected_output_file_content)

    def test_clean_cesiones_periodo_csv_file_ok_1_twice(self) -> None:
        # Clean the file already cleaned up.
        input_file_content = _CESIONES_PERIODO_CSV_FILE_1_CLEANED
        expected_output_file_content = _CESIONES_PERIODO_CSV_FILE_1_CLEANED

        # note: for the output we need 'w+b' to be able to read and write data.
        with tempfile.NamedTemporaryFile(mode='w+b') as output_tmp_file:
            with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
                input_tmp_file.write(input_file_content)
                input_tmp_file.flush()
                clean_cesiones_periodo_csv_file(input_tmp_file.name, output_tmp_file.name)
            output_tmp_file.seek(0)
            output_file_content = output_tmp_file.read()
        self.assertEqual(output_file_content, expected_output_file_content)

    def test_parse_cesiones_periodo_csv_file_ok_1(self) -> None:
        with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
            input_tmp_file.write(_CESIONES_PERIODO_CSV_FILE_1_CLEANED)
            input_tmp_file.flush()

            results = list(parse_cesiones_periodo_csv_file(input_tmp_file.name, n_rows_offset=0))

        self.assertEqual(
            results,
            [
                (
                    CesionesPeriodoEntry(
                        dte_vendedor_rut=Rut('51532520-4'),
                        dte_deudor_rut=Rut('75320502-0'),
                        dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                        dte_folio=3608460,
                        dte_fecha_emision=date(2019, 2, 11),
                        dte_monto_total=256357,
                        cedente_rut=Rut('51532520-4'),
                        cedente_razon_social='MI CAMPITO SA',
                        cedente_email='mi@campito.cl',
                        cesionario_rut=Rut('96667560-8'),
                        cesionario_razon_social='POBRES SERVICIOS FINANCIEROS S.A.',
                        cesionario_emails='un-poco@pobres.cl,super.ejecutivo@pobres.cl',
                        deudor_email=None,
                        fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                            datetime(2019, 3, 7, 13, 32), tz=SII_OFFICIAL_TZ
                        ),
                        fecha_cesion=date(2019, 3, 7),
                        monto_cedido=256357,
                        fecha_ultimo_vencimiento=date(2019, 4, 12),
                        estado='Cesion Vigente',
                    ),
                    1,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '51532520-4'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '33'),
                            ('dte_folio', '3608460'),
                            ('dte_fecha_emision', '2019-02-11'),
                            ('dte_monto_total', '256357'),
                            ('cedente_rut', '51532520-4'),
                            ('cedente_razon_social', 'MI CAMPITO SA'),
                            ('cedente_email', 'mi@campito.cl'),
                            ('cesionario_rut', '96667560-8'),
                            ('cesionario_razon_social', 'POBRES SERVICIOS FINANCIEROS S.A.'),
                            ('cesionario_emails', 'un-poco@pobres.cl,super.ejecutivo@pobres.cl'),
                            ('fecha_cesion_dt', '2019-03-07 13:32'),
                            ('monto_cedido', '256357'),
                            ('fecha_ultimo_vencimiento', '2019-04-12'),
                            ('fecha_cesion', '2019-03-07 13:32'),
                        ]
                    ),
                    {},
                ),
                (
                    CesionesPeriodoEntry(
                        dte_vendedor_rut=Rut('51532520-4'),
                        dte_deudor_rut=Rut('75320502-0'),
                        dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                        dte_folio=3608534,
                        dte_fecha_emision=date(2019, 2, 15),
                        dte_monto_total=96628,
                        cedente_rut=Rut('51532520-4'),
                        cedente_razon_social='MI CAMPITO SA',
                        cedente_email='mi@campito.cl',
                        cesionario_rut=Rut('96667560-8'),
                        cesionario_razon_social='POBRES SERVICIOS FINANCIEROS S.A.',
                        cesionario_emails=(
                            'ejecutivo@pobres.cl,super.ejecutivo@pobres.cl,muy@pobres.cl'
                        ),
                        deudor_email=None,
                        fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                            datetime(2019, 3, 7, 13, 31), tz=SII_OFFICIAL_TZ
                        ),
                        fecha_cesion=date(2019, 3, 7),
                        monto_cedido=96628,
                        fecha_ultimo_vencimiento=date(2019, 4, 16),
                        estado='Cesion Vigente',
                    ),
                    2,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '51532520-4'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '33'),
                            ('dte_folio', '3608534'),
                            ('dte_fecha_emision', '2019-02-15'),
                            ('dte_monto_total', '96628'),
                            ('cedente_rut', '51532520-4'),
                            ('cedente_razon_social', 'MI CAMPITO SA'),
                            ('cedente_email', 'mi@campito.cl'),
                            ('cesionario_rut', '96667560-8'),
                            ('cesionario_razon_social', 'POBRES SERVICIOS FINANCIEROS S.A.'),
                            (
                                'cesionario_emails',
                                'ejecutivo@pobres.cl,super.ejecutivo@pobres.cl,muy@pobres.cl',
                            ),
                            ('fecha_cesion_dt', '2019-03-07 13:31'),
                            ('monto_cedido', '96628'),
                            ('fecha_ultimo_vencimiento', '2019-04-16'),
                            ('fecha_cesion', '2019-03-07 13:31'),
                        ]
                    ),
                    {},
                ),
                (
                    CesionesPeriodoEntry(
                        dte_vendedor_rut=Rut('83564146-5'),
                        dte_deudor_rut=Rut('75320502-0'),
                        dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                        dte_folio=1113465,
                        dte_fecha_emision=date(2019, 3, 7),
                        dte_monto_total=703771,
                        cedente_rut=Rut('83564146-5'),
                        cedente_razon_social='MOYA S A',
                        cedente_email='paga@moya.xyz',
                        cesionario_rut=Rut('96932010-K'),
                        cesionario_razon_social='Ricky S.A.',
                        cesionario_emails='whatever@ricky.cl',
                        deudor_email=None,
                        fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                            datetime(2019, 3, 26, 9, 27), tz=SII_OFFICIAL_TZ
                        ),
                        fecha_cesion=date(2019, 3, 26),
                        monto_cedido=703771,
                        fecha_ultimo_vencimiento=date(2019, 7, 5),
                        estado='Cesion Vigente',
                    ),
                    3,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '83564146-5'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '33'),
                            ('dte_folio', '1113465'),
                            ('dte_fecha_emision', '2019-03-07'),
                            ('dte_monto_total', '703771'),
                            ('cedente_rut', '83564146-5'),
                            ('cedente_razon_social', 'MOYA S A'),
                            ('cedente_email', 'paga@moya.xyz'),
                            ('cesionario_rut', '96932010-K'),
                            ('cesionario_razon_social', 'Ricky S.A.'),
                            ('cesionario_emails', 'whatever@ricky.cl'),
                            ('fecha_cesion_dt', '2019-03-26 09:27'),
                            ('monto_cedido', '703771'),
                            ('fecha_ultimo_vencimiento', '2019-07-05'),
                            ('fecha_cesion', '2019-03-26 09:27'),
                        ]
                    ),
                    {},
                ),
            ],
        )

    def test_parse_cesiones_periodo_csv_file_fail_1(self) -> None:
        with tempfile.NamedTemporaryFile(mode='wb') as input_tmp_file:
            input_tmp_file.write(_CESIONES_PERIODO_CSV_FILE_2_CLEANED)
            input_tmp_file.flush()

            results = list(parse_cesiones_periodo_csv_file(input_tmp_file.name, n_rows_offset=0))

        self.assertEqual(
            results,
            [
                (
                    None,
                    1,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '51532520-4'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '1'),
                            ('dte_folio', '3608460'),
                            ('dte_fecha_emision', '2019-02-11'),
                            ('dte_monto_total', '1.0'),
                            ('cedente_rut', '51532520-4'),
                            ('cedente_razon_social', 'MI CAMPITO SA'),
                            ('cedente_email', 'mi@campito.cl'),
                            ('cesionario_rut', '96667560-8'),
                            ('cesionario_razon_social', 'POBRES SERVICIOS FINANCIEROS S.A.'),
                            ('cesionario_emails', 'un-poco@pobres.cl,super.ejecutivo@pobres.cl'),
                            ('fecha_cesion_dt', '2019-03-07 13:32'),
                            ('monto_cedido', '1.0'),
                            ('fecha_ultimo_vencimiento', '2019'),
                            ('fecha_cesion', '2019-03-07 13:32'),
                        ]
                    ),
                    {
                        'validation': {
                            'dte_tipo_dte': ['Not a valid Tipo DTE.'],
                            'dte_monto_total': ['Not a valid integer.'],
                            'monto_cedido': ['Not a valid integer.'],
                            'fecha_ultimo_vencimiento': ['Not a valid date.'],
                        }
                    },
                ),
                (
                    CesionesPeriodoEntry(
                        dte_vendedor_rut=Rut('83564146-5'),
                        dte_deudor_rut=Rut('75320502-0'),
                        dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                        dte_folio=1113465,
                        dte_fecha_emision=date(2019, 3, 7),
                        dte_monto_total=703771,
                        cedente_rut=Rut('83564146-5'),
                        cedente_razon_social='MOYA S A',
                        cedente_email='paga@moya.xyz',
                        cesionario_rut=Rut('96932010-K'),
                        cesionario_razon_social='Ricky S.A.',
                        cesionario_emails='whatever@ricky.cl',
                        deudor_email=None,
                        fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                            datetime(2019, 3, 26, 9, 27), tz=SII_OFFICIAL_TZ
                        ),
                        fecha_cesion=date(2019, 3, 26),
                        monto_cedido=703771,
                        fecha_ultimo_vencimiento=date(2019, 7, 5),
                        estado='Cesion Vigente',
                    ),
                    2,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '83564146-5'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '33'),
                            ('dte_folio', '1113465'),
                            ('dte_fecha_emision', '2019-03-07'),
                            ('dte_monto_total', '703771'),
                            ('cedente_rut', '83564146-5'),
                            ('cedente_razon_social', 'MOYA S A'),
                            ('cedente_email', 'paga@moya.xyz'),
                            ('cesionario_rut', '96932010-K'),
                            ('cesionario_razon_social', 'Ricky S.A.'),
                            ('cesionario_emails', 'whatever@ricky.cl'),
                            ('fecha_cesion_dt', '2019-03-26 09:27'),
                            ('monto_cedido', '703771'),
                            ('fecha_ultimo_vencimiento', '2019-07-05'),
                            ('fecha_cesion', '2019-03-26 09:27'),
                        ]
                    ),
                    {},
                ),
                (
                    CesionesPeriodoEntry(
                        dte_vendedor_rut=Rut('83564146-5'),
                        dte_deudor_rut=Rut('75320502-0'),
                        dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                        dte_folio=1113465,
                        dte_fecha_emision=date(2019, 3, 7),
                        dte_monto_total=703771,
                        cedente_rut=Rut('83564146-5'),
                        cedente_razon_social='MOYA S A',
                        cedente_email='paga@moya.xyz',
                        cesionario_rut=Rut('96932010-K'),
                        cesionario_razon_social='Ricky S.A.',
                        cesionario_emails='whatever@ricky.cl',
                        deudor_email=None,
                        fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                            datetime(2019, 3, 26, 23, 00), tz=SII_OFFICIAL_TZ
                        ),
                        fecha_cesion=date(2019, 3, 26),
                        monto_cedido=703771,
                        fecha_ultimo_vencimiento=date(2019, 7, 5),
                        estado='Cesion Vigente',
                    ),
                    3,
                    OrderedDict(
                        [
                            ('dte_vendedor_rut', '83564146-5'),
                            ('estado', 'Cesion Vigente'),
                            ('dte_deudor_rut', '75320502-0'),
                            ('deudor_email', None),
                            ('dte_tipo_dte', '33'),
                            ('dte_folio', '1113465'),
                            ('dte_fecha_emision', '2019-03-07'),
                            ('dte_monto_total', '703771'),
                            ('cedente_rut', '83564146-5'),
                            ('cedente_razon_social', 'MOYA S A'),
                            ('cedente_email', 'paga@moya.xyz'),
                            ('cesionario_rut', '96932010-K'),
                            ('cesionario_razon_social', 'Ricky S.A.'),
                            ('cesionario_emails', 'whatever@ricky.cl'),
                            ('fecha_cesion_dt', '2019-03-26 23:00'),
                            ('monto_cedido', '703771'),
                            ('fecha_ultimo_vencimiento', '2019-07-05'),
                            ('fecha_cesion', '2019-03-26 23:00'),
                        ]
                    ),
                    {},
                ),
            ],
        )
