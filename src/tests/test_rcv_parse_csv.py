import datetime
import unittest
from typing import Callable
from unittest import mock

import cl_sii.rcv.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs.tz_utils import convert_naive_dt_to_tz_aware
from cl_sii.rcv.data_models import (
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RvDetalleEntry,
)
from cl_sii.rcv.parse_csv import (  # noqa: F401
    RcvCompraNoIncluirCsvRowSchema,
    RcvCompraPendienteCsvRowSchema,
    RcvCompraReclamadoCsvRowSchema,
    RcvCompraRegistroCsvRowSchema,
    RcvVentaCsvRowSchema,
    _parse_rcv_csv_file,
    parse_rcv_compra_no_incluir_csv_file,
    parse_rcv_compra_pendiente_csv_file,
    parse_rcv_compra_reclamado_csv_file,
    parse_rcv_compra_registro_csv_file,
    parse_rcv_venta_csv_file,
)
from cl_sii.rut import Rut
from .utils import get_test_file_path


class RcvVentaCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_ventas_row(self) -> None:
        schema_context = dict(
            emisor_rut=Rut('1-9'),
        )
        input_csv_row_schema = RcvVentaCsvRowSchema(context=schema_context)

        data = {
            'tipo_docto': cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            'tipo_venta': cl_sii.rcv.constants.RvTipoVenta.DEL_GIRO,
            'receptor_rut': Rut('12345678-5'),
            'receptor_razon_social': 'Fake Company S.A.',
            'folio': 506,
            'fecha_emision_date': datetime.date(2019, 6, 4),
            'fecha_acuse_dt': None,
            'fecha_recepcion_dt': datetime.datetime(2019, 6, 18, 17, 1, 6, tzinfo=SII_OFFICIAL_TZ),
            'fecha_reclamo_dt': None,
            'monto_exento': 0,
            'monto_neto': 1750181,
            'monto_iva': 332534,
            'monto_total': 2082715,
            'iva_retenido_total': 0,
            'iva_retenido_parcial': 0,
            'iva_no_retenido': 0,
            'iva_propio': 0,
            'iva_terceros': 0,
            'liquidacion_factura_emisor_rut': None,
            'neto_comision_liquidacion_factura': 0,
            'exento_comision_liquidacion_factura': 0,
            'iva_comision_liquidacion_factura': 0,
            'iva_fuera_de_plazo': 0,
            'tipo_documento_referencia': None,
            'folio_documento_referencia': None,
            'num_ident_receptor_extranjero': '',
            'nacionalidad_receptor_extranjero': '',
            'credito_empresa_constructora': 0,
            'impuesto_zona_franca_ley_18211': None,
            'garantia_dep_envases': 0,
            'indicador_venta_sin_costo': 2,
            'indicador_servicio_periodico': 0,
            'monto_no_facturable': 0,
            'total_monto_periodo': 0,
            'venta_pasajes_transporte_nacional': None,
            'venta_pasajes_transporte_internacional': None,
            'numero_interno': '',
            'codigo_sucursal': '0',
            'nce_o_nde_sobre_factura_de_compra': '',
            'codigo_otro_imp': '',
            'valor_otro_imp': None,
            'tasa_otro_imp': None,
            'emisor_rut': Rut('1-9'),
        }

        result = input_csv_row_schema.to_detalle_entry(data)
        expected_result = RvDetalleEntry(
            emisor_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=506,
            fecha_emision_date=datetime.date(2019, 6, 4),
            receptor_rut=Rut('12345678-5'),
            monto_total=2082715,
            fecha_recepcion_dt=datetime.datetime(2019, 6, 18, 17, 1, 6, tzinfo=SII_OFFICIAL_TZ),
            tipo_venta='DEL_GIRO',
            receptor_razon_social='Fake Company S.A.',
            fecha_acuse_dt=None,
            fecha_reclamo_dt=None,
            monto_exento=0,
            monto_neto=1750181,
            monto_iva=332534,
            iva_retenido_total=0,
            iva_retenido_parcial=0,
            iva_no_retenido=0,
            iva_propio=0,
            iva_terceros=0,
            liquidacion_factura_emisor_rut=None,
            neto_comision_liquidacion_factura=0,
            exento_comision_liquidacion_factura=0,
            iva_comision_liquidacion_factura=0,
            iva_fuera_de_plazo=0,
            tipo_documento_referencia=None,
            folio_documento_referencia=None,
            num_ident_receptor_extranjero='',
            nacionalidad_receptor_extranjero='',
            credito_empresa_constructora=0,
            impuesto_zona_franca_ley_18211=None,
            garantia_dep_envases=0,
            indicador_venta_sin_costo=2,
            indicador_servicio_periodico=0,
            monto_no_facturable=0,
            total_monto_periodo=0,
            venta_pasajes_transporte_nacional=None,
            venta_pasajes_transporte_internacional=None,
            numero_interno='',
            codigo_sucursal='0',
            nce_o_nde_sobre_factura_de_compra='',
            codigo_otro_imp='',
            valor_otro_imp=None,
            tasa_otro_imp=None,
        )

        self.assertEqual(result, expected_result)


class RcvCompraRegistroCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_registro_row(self) -> None:
        schema_context = dict(
            emisor_rut=Rut('1-9'),
        )
        input_csv_row_schema = RcvCompraRegistroCsvRowSchema(context=schema_context)

        data = {
            'emisor_rut': Rut('12345678-5'),
            'tipo_docto': cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            'tipo_compra': cl_sii.rcv.constants.RcTipoCompra.DEL_GIRO,
            'folio': 23084,
            'fecha_emision_date': datetime.date(2019, 6, 21),
            'monto_total': 285801,
            'emisor_razon_social': 'Fake Company S.A.',
            'receptor_rut': Rut('1-9'),
            'fecha_recepcion_dt': datetime.datetime(2019, 6, 24, 9, 55, 53, tzinfo=SII_OFFICIAL_TZ),
            'monto_exento': 0,
            'monto_neto': 240169,
            'monto_iva_recuperable': 45632,
            'monto_iva_no_recuperable': None,
            'codigo_iva_no_rec': '',
            'monto_neto_activo_fijo': None,
            'iva_activo_fijo': None,
            'iva_uso_comun': None,
            'impto_sin_derecho_a_credito': None,
            'iva_no_retenido': 0,
            'nce_o_nde_sobre_factura_de_compra': '0',
            'codigo_otro_impuesto': '',
            'valor_otro_impuesto': None,
            'tasa_otro_impuesto': None,
            'fecha_acuse_dt': datetime.datetime(2019, 6, 30, 9, 55, 53, tzinfo=SII_OFFICIAL_TZ),
            'tabacos_puros': None,
            'tabacos_cigarrillos': None,
            'tabacos_elaborados': None,
        }

        result = input_csv_row_schema.to_detalle_entry(data)
        expected_result = RcRegistroDetalleEntry(
            emisor_rut=Rut('12345678-5'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=23084,
            fecha_emision_date=datetime.date(2019, 6, 21),
            receptor_rut=Rut('1-9'),
            monto_total=285801,
            fecha_recepcion_dt=datetime.datetime(2019, 6, 24, 9, 55, 53, tzinfo=SII_OFFICIAL_TZ),
            tipo_compra='DEL_GIRO',
            emisor_razon_social='Fake Company S.A.',
            monto_exento=0,
            monto_neto=240169,
            monto_iva_recuperable=45632,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec='',
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            codigo_otro_impuesto='',
            valor_otro_impuesto=None,
            tasa_otro_impuesto=None,
            fecha_acuse_dt=datetime.datetime(2019, 6, 30, 9, 55, 53, tzinfo=SII_OFFICIAL_TZ),
            tabacos_puros=None,
            tabacos_cigarrillos=None,
            tabacos_elaborados=None,
        )
        self.assertEqual(result, expected_result)


class RcvCompraNoIncluirCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_no_incluir_row(self) -> None:
        schema_context = dict(
            emisor_rut=Rut('1-9'),
        )
        input_csv_row_schema = RcvCompraNoIncluirCsvRowSchema(context=schema_context)

        data = {
            'emisor_rut': Rut('12345678-5'),
            'tipo_docto': cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            'tipo_compra': cl_sii.rcv.constants.RcTipoCompra.NO_CORRESPONDE_INCLUIR,
            'folio': 19000035,
            'fecha_emision_date': datetime.date(2019, 12, 13),
            'monto_total': 104362,
            'emisor_razon_social': 'Fake Company S.A.',
            'receptor_rut': Rut('1-9'),
            'fecha_recepcion_dt': datetime.datetime(
                2019, 12, 14, 15, 56, 27, tzinfo=SII_OFFICIAL_TZ
            ),
            'monto_exento': 0,
            'monto_neto': 87699,
            'monto_iva_recuperable': None,
            'monto_iva_no_recuperable': 16663,
            'codigo_iva_no_rec': '9',
            'monto_neto_activo_fijo': None,
            'iva_activo_fijo': None,
            'iva_uso_comun': None,
            'impto_sin_derecho_a_credito': None,
            'iva_no_retenido': 0,
            'nce_o_nde_sobre_factura_de_compra': '0',
            'codigo_otro_impuesto': '',
            'valor_otro_impuesto': None,
            'tasa_otro_impuesto': None,
            'fecha_acuse_dt': None,
        }

        result = input_csv_row_schema.to_detalle_entry(data)
        expected_result = RcNoIncluirDetalleEntry(
            emisor_rut=Rut('12345678-5'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=19000035,
            fecha_emision_date=datetime.date(2019, 12, 13),
            receptor_rut=Rut('1-9'),
            monto_total=104362,
            fecha_recepcion_dt=datetime.datetime(2019, 12, 14, 15, 56, 27, tzinfo=SII_OFFICIAL_TZ),
            tipo_compra='NO_CORRESPONDE_INCLUIR',
            emisor_razon_social='Fake Company S.A.',
            monto_exento=0,
            monto_neto=87699,
            monto_iva_recuperable=None,
            monto_iva_no_recuperable=16663,
            codigo_iva_no_rec='9',
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            codigo_otro_impuesto='',
            valor_otro_impuesto=None,
            tasa_otro_impuesto=None,
            fecha_acuse_dt=None,
        )

        self.assertEqual(result, expected_result)


class RcvCompraReclamadoCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_reclamado_row(self) -> None:
        schema_context = dict(
            emisor_rut=Rut('1-9'),
        )
        input_csv_row_schema = RcvCompraReclamadoCsvRowSchema(context=schema_context)

        data = {
            'emisor_rut': Rut('12345678-5'),
            'tipo_docto': cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            'tipo_compra': cl_sii.rcv.constants.RcTipoCompra.DEL_GIRO,
            'folio': 1000055,
            'fecha_emision_date': datetime.date(2019, 6, 5),
            'monto_total': 1155364,
            'emisor_razon_social': 'Fake Company S.A.',
            'receptor_rut': Rut('1-9'),
            'fecha_recepcion_dt': datetime.datetime(2019, 6, 5, 21, 58, 49, tzinfo=SII_OFFICIAL_TZ),
            'monto_exento': 0,
            'monto_neto': 970894,
            'monto_iva_recuperable': 184470,
            'monto_iva_no_recuperable': None,
            'codigo_iva_no_rec': '',
            'monto_neto_activo_fijo': None,
            'iva_activo_fijo': None,
            'iva_uso_comun': None,
            'impto_sin_derecho_a_credito': None,
            'iva_no_retenido': 0,
            'nce_o_nde_sobre_factura_de_compra': '0',
            'codigo_otro_impuesto': '',
            'valor_otro_impuesto': None,
            'tasa_otro_impuesto': None,
            'fecha_reclamo_dt': datetime.datetime(2019, 6, 12, 9, 47, 23, tzinfo=SII_OFFICIAL_TZ),
        }

        result = input_csv_row_schema.to_detalle_entry(data)
        expected_result = RcReclamadoDetalleEntry(
            emisor_rut=Rut('12345678-5'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=1000055,
            fecha_emision_date=datetime.date(2019, 6, 5),
            receptor_rut=Rut('1-9'),
            monto_total=1155364,
            fecha_recepcion_dt=datetime.datetime(2019, 6, 5, 21, 58, 49, tzinfo=SII_OFFICIAL_TZ),
            tipo_compra='DEL_GIRO',
            emisor_razon_social='Fake Company S.A.',
            monto_exento=0,
            monto_neto=970894,
            monto_iva_recuperable=184470,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec='',
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            codigo_otro_impuesto='',
            valor_otro_impuesto=None,
            tasa_otro_impuesto=None,
            fecha_reclamo_dt=datetime.datetime(2019, 6, 12, 9, 47, 23, tzinfo=SII_OFFICIAL_TZ),
        )

        self.assertEqual(result, expected_result)


class RcvCompraPendienteCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_pendiente_row(self) -> None:
        schema_context = dict(
            emisor_rut=Rut('1-9'),
        )
        input_csv_row_schema = RcvCompraPendienteCsvRowSchema(context=schema_context)

        data = {
            'emisor_rut': Rut('12345678-5'),
            'tipo_docto': cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            'tipo_compra': cl_sii.rcv.constants.RcTipoCompra.DEL_GIRO,
            'folio': 9800042,
            'fecha_emision_date': datetime.date(2019, 6, 28),
            'monto_total': 49787,
            'emisor_razon_social': 'Fake Company S.A.',
            'receptor_rut': Rut('1-9'),
            'fecha_recepcion_dt': datetime.datetime(2019, 7, 1, 13, 21, 32, tzinfo=SII_OFFICIAL_TZ),
            'monto_exento': 0,
            'monto_neto': 41838,
            'monto_iva_recuperable': 7949,
            'monto_iva_no_recuperable': None,
            'codigo_iva_no_rec': '',
            'monto_neto_activo_fijo': None,
            'iva_activo_fijo': None,
            'iva_uso_comun': None,
            'impto_sin_derecho_a_credito': None,
            'iva_no_retenido': 0,
            'nce_o_nde_sobre_factura_de_compra': '0',
            'codigo_otro_impuesto': '',
            'valor_otro_impuesto': None,
            'tasa_otro_impuesto': None,
        }

        result = input_csv_row_schema.to_detalle_entry(data)
        expected_result = RcPendienteDetalleEntry(
            emisor_rut=Rut('12345678-5'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=9800042,
            fecha_emision_date=datetime.date(2019, 6, 28),
            receptor_rut=Rut('1-9'),
            monto_total=49787,
            fecha_recepcion_dt=datetime.datetime(2019, 7, 1, 13, 21, 32, tzinfo=SII_OFFICIAL_TZ),
            tipo_compra='DEL_GIRO',
            emisor_razon_social='Fake Company S.A.',
            monto_exento=0,
            monto_neto=41838,
            monto_iva_recuperable=7949,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec='',
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            codigo_otro_impuesto='',
            valor_otro_impuesto=None,
            tasa_otro_impuesto=None,
        )

        self.assertEqual(result, expected_result)


class FunctionsTest(unittest.TestCase):
    def test_parse_rcv_venta_csv_file(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-rz_leading_trailing_whitespace.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        expected_entry_struct = RvDetalleEntry(
            emisor_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=506,
            fecha_emision_date=datetime.date(2019, 6, 4),
            receptor_rut=Rut('12345678-5'),
            monto_total=2082715,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                dt=datetime.datetime(2019, 6, 18, 17, 1, 6),
                tz=SII_OFFICIAL_TZ,
            ),
            tipo_venta='DEL_GIRO',
            receptor_razon_social='Fake Company S.A.',
            fecha_acuse_dt=None,
            fecha_reclamo_dt=None,
            monto_exento=0,
            monto_neto=1750181,
            monto_iva=332534,
            iva_retenido_total=0,
            iva_retenido_parcial=0,
            iva_no_retenido=0,
            iva_propio=0,
            iva_terceros=0,
            liquidacion_factura_emisor_rut=None,
            neto_comision_liquidacion_factura=0,
            exento_comision_liquidacion_factura=0,
            iva_comision_liquidacion_factura=0,
            iva_fuera_de_plazo=0,
            tipo_documento_referencia=None,
            folio_documento_referencia=None,
            num_ident_receptor_extranjero=None,
            nacionalidad_receptor_extranjero=None,
            credito_empresa_constructora=0,
            impuesto_zona_franca_ley_18211=None,
            garantia_dep_envases=0,
            indicador_venta_sin_costo=2,
            indicador_servicio_periodico=0,
            monto_no_facturable=0,
            total_monto_periodo=0,
            venta_pasajes_transporte_nacional=None,
            venta_pasajes_transporte_internacional=None,
            numero_interno=None,
            codigo_sucursal='0',
            nce_o_nde_sobre_factura_de_compra=None,
            codigo_otro_imp=None,
            valor_otro_imp=None,
            tasa_otro_imp=None,
        )
        # First row:
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_ix, 1)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct, expected_entry_struct)

    def test_parse_rcv_venta_csv_file_receptor_rz_leading_trailing_whitespace(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-rz_leading_trailing_whitespace.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.receptor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.receptor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def test_parse_rcv_venta_csv_file_missing_required_fields(self):
        # This CSV should have a required field (e.g., 'Folio') as an empty string
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-missing-required-fields.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertIsNone(entry_struct)
        self.assertIn('validation', row_parsing_errors)
        self.assertIn('Fecha Recepcion', row_parsing_errors['validation'])
        self.assertIn('Tipo Doc', row_parsing_errors['validation'])
        self.assertEqual(
            row_parsing_errors['validation']['Fecha Recepcion'],
            ['Missing data for required field.'],
        )

    def _test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
        parse_rcv_compra_csv_file_function: Callable,
        rcv_file_path: str,
    ) -> None:
        rcv_file_path = get_test_file_path(rcv_file_path)

        items = parse_rcv_compra_csv_file_function(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.emisor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.emisor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def test_parse_rcv_venta_csv_file_conversion_error(self):
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-rz_leading_trailing_whitespace.csv',
        )

        # Patch the to_detalle_entry method to raise an exception
        with (
            self.assertLogs('cl_sii.rcv', level='ERROR') as assert_logs_cm,
            mock.patch.object(
                RcvVentaCsvRowSchema,
                'to_detalle_entry',
                side_effect=ValueError('Mocked conversion error'),
            ),
        ):
            items = parse_rcv_venta_csv_file(
                rut=Rut('1-9'),
                input_file_path=rcv_file_path,
                n_rows_offset=0,
                max_n_rows=1,
            )
            entry_struct, row_ix, row_data, row_parsing_errors = next(items)
            self.assertIsNone(entry_struct)
            self.assertIn('conversion_errors', row_parsing_errors)
            self.assertIn('Mocked conversion error', row_parsing_errors['conversion_errors'])
            self.assertRegex(
                assert_logs_cm.output[0],
                (
                    'ERROR:cl_sii.rcv.parse_csv:'
                    'Deserialized row data conversion failed for row 1: Mocked conversion error'
                ),
            )

    def test_parse_rcv_compra_registro_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_registro_csv_file'.
        pass

    def test_parse_rcv_compra_registro_csv_file_emisor_rz_leading_trailing_whitespace(self) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_registro_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-registro-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_no_incluir_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_no_incluir_csv_file'.
        pass

    def test_parse_rcv_compra_no_incluir_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_no_incluir_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-no_incluir-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_reclamado_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_reclamado_csv_file'.
        pass

    def test_parse_rcv_compra_reclamado_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_reclamado_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-reclamado-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_pendiente_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_pendiente_csv_file'.
        pass

    def test_parse_rcv_compra_pendiente_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_pendiente_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-pendiente-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test__parse_rcv_csv_file(self) -> None:
        # TODO: implement for '_parse_rcv_csv_file'.
        pass

    def test_get_rcv_csv_file_parser_returns_correct_parser(self):
        from cl_sii.rcv.constants import RcEstadoContable, RcvKind
        from cl_sii.rcv.parse_csv import (
            get_rcv_csv_file_parser,
            parse_rcv_compra_no_incluir_csv_file,
            parse_rcv_compra_pendiente_csv_file,
            parse_rcv_compra_reclamado_csv_file,
            parse_rcv_compra_registro_csv_file,
            parse_rcv_venta_csv_file,
        )

        # VENTAS: estado_contable must be None
        parser = get_rcv_csv_file_parser(RcvKind.VENTAS, None)
        self.assertIs(parser, parse_rcv_venta_csv_file)
        with self.assertRaises(ValueError):
            get_rcv_csv_file_parser(RcvKind.VENTAS, RcEstadoContable.REGISTRO)

        # COMPRAS: estado_contable must not be None
        self.assertIs(
            get_rcv_csv_file_parser(RcvKind.COMPRAS, RcEstadoContable.REGISTRO),
            parse_rcv_compra_registro_csv_file,
        )
        self.assertIs(
            get_rcv_csv_file_parser(RcvKind.COMPRAS, RcEstadoContable.NO_INCLUIR),
            parse_rcv_compra_no_incluir_csv_file,
        )
        self.assertIs(
            get_rcv_csv_file_parser(RcvKind.COMPRAS, RcEstadoContable.RECLAMADO),
            parse_rcv_compra_reclamado_csv_file,
        )
        self.assertIs(
            get_rcv_csv_file_parser(RcvKind.COMPRAS, RcEstadoContable.PENDIENTE),
            parse_rcv_compra_pendiente_csv_file,
        )
        with self.assertRaises(ValueError):
            get_rcv_csv_file_parser(RcvKind.COMPRAS, None)

        # Test unknown estado_contable
        class DummyEstadoContable:
            pass

        with self.assertRaises(Exception):
            get_rcv_csv_file_parser(RcvKind.COMPRAS, DummyEstadoContable())

        # Test unknown rcv_kind
        class DummyRcvKind:
            pass

        with self.assertRaises(Exception):
            get_rcv_csv_file_parser(DummyRcvKind(), None)
