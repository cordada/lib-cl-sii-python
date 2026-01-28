from __future__ import annotations

import datetime
import unittest
from collections.abc import Iterable, Iterator
from decimal import Decimal
from typing import Callable, Optional
from unittest import mock

import cl_sii.rcv.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs.tz_utils import convert_naive_dt_to_tz_aware
from cl_sii.rcv.data_models import (
    DocumentoReferencia,
    OtrosImpuestos,
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
    _parse_rv_documento_referencias,
    _RcvCompraCsvRowContext,
    _RcvCompraCsvRowSchemaContext,
    _RcvVentaCsvRowContext,
    _RcvVentaCsvRowSchemaContext,
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
        schema_context: _RcvVentaCsvRowContext = {
            'contribuyente_rut': Rut('1-9'),
        }
        input_csv_row_schema = RcvVentaCsvRowSchema()

        raw_data = {
            'Tipo Doc': '33',
            'Tipo Venta': 'Del Giro',
            'Rut cliente': '12345678-5',
            'Razon Social': 'Fake Customer S.A.',
            'Folio': '506',
            'Fecha Docto': '04/06/2019',
            'Fecha Recepcion': '18/06/2019 17:01:06',
            'Fecha Acuse Recibo': '',
            'Fecha Reclamo': '',
            'Monto Exento': '0',
            'Monto Neto': '1750181',
            'Monto IVA': '332534',
            'Monto total': '2082715',
            'IVA Retenido Total': '0',
            'IVA Retenido Parcial': '0',
            'IVA no retenido': '0',
            'IVA propio': '0',
            'IVA Terceros': '0',
            'RUT Emisor Liquid. Factura': '',
            'Neto Comision Liquid. Factura': '0',
            'Exento Comision Liquid. Factura': '0',
            'IVA Comision Liquid. Factura': '0',
            'IVA fuera de plazo': '0',
            'Documento Referencias': None,
            'Num. Ident. Receptor Extranjero': '',
            'Nacionalidad Receptor Extranjero': '',
            'Credito empresa constructora': '0',
            'Impto. Zona Franca (Ley 18211)': '',
            'Garantia Dep. Envases': '0',
            'Indicador Venta sin Costo': '2',
            'Indicador Servicio Periodico': '0',
            'Monto No facturable': '0',
            'Total Monto Periodo': '0',
            'Venta Pasajes Transporte Nacional': '',
            'Venta Pasajes Transporte Internacional': '',
            'Numero Interno': '',
            'Codigo Sucursal': '0',
            'NCE o NDE sobre Fact. de Compra': '',
            'Otros Impuestos': [
                {
                    'codigo_otro_impuesto': '',
                    'valor_otro_impuesto': '',
                    'tasa_otro_impuesto': '',
                }
            ],
        }

        with _RcvVentaCsvRowSchemaContext(schema_context):
            deserialized_data = input_csv_row_schema.load(raw_data)

        result = input_csv_row_schema.to_detalle_entry(deserialized_data)
        expected_result = RvDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=506,
            fecha_emision_date=datetime.date(2019, 6, 4),
            cliente_rut=Rut('12345678-5'),
            monto_total=2082715,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 6, 18, 17, 1, 6), tz=SII_OFFICIAL_TZ
            ),
            tipo_venta='DEL_GIRO',
            cliente_razon_social='Fake Customer S.A.',
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
            documento_referencias=None,
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
            otros_impuestos=None,
        )

        self.assertEqual(result, expected_result)


class RcvCompraRegistroCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_registro_row(self) -> None:
        schema_context: _RcvCompraCsvRowContext = {
            'contribuyente_rut': Rut('1-9'),
        }
        input_csv_row_schema = RcvCompraRegistroCsvRowSchema()

        raw_data = {
            'Tipo Doc': '33',
            'Tipo Compra': 'Del Giro',
            'RUT Proveedor': '12345678-5',
            'Razon Social': 'Fake Seller S.A.',
            'Folio': '23084',
            'Fecha Docto': '21/06/2019',
            'Fecha Recepcion': '24/06/2019 09:55:53',
            'Fecha Acuse': '30/06/2019 09:55:53',
            'Monto Exento': '0',
            'Monto Neto': '240169',
            'Monto IVA Recuperable': '45632',
            'Monto Iva No Recuperable': '',
            'Codigo IVA No Rec.': '',
            'Monto Total': '285801',
            'Monto Neto Activo Fijo': '',
            'IVA Activo Fijo': '',
            'IVA uso Comun': '',
            'Impto. Sin Derecho a Credito': '',
            'IVA No Retenido': '0',
            'Tabacos Puros': '',
            'Tabacos Cigarrillos': '',
            'Tabacos Elaborados': '',
            'NCE o NDE sobre Fact. de Compra': '0',
            'Codigo Otro Impuesto': '',
            'Valor Otro Impuesto': '',
            'Tasa Otro Impuesto': '',
        }

        with _RcvCompraCsvRowSchemaContext(schema_context):
            deserialized_data = input_csv_row_schema.load(raw_data)

        result = input_csv_row_schema.to_detalle_entry(deserialized_data)
        expected_result = RcRegistroDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=23084,
            fecha_emision_date=datetime.date(2019, 6, 21),
            proveedor_rut=Rut('12345678-5'),
            monto_total=285801,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 6, 24, 9, 55, 53),
                tz=SII_OFFICIAL_TZ,
            ),
            tipo_compra='DEL_GIRO',
            proveedor_razon_social='Fake Seller S.A.',
            monto_exento=0,
            monto_neto=240169,
            monto_iva_recuperable=45632,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            otros_impuestos=None,
            fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 6, 30, 9, 55, 53), tz=SII_OFFICIAL_TZ
            ),
            tabacos_puros=None,
            tabacos_cigarrillos=None,
            tabacos_elaborados=None,
        )
        self.assertEqual(result, expected_result)


class RcvCompraNoIncluirCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_no_incluir_row(self) -> None:
        schema_context: _RcvCompraCsvRowContext = {
            'contribuyente_rut': Rut('1-9'),
        }
        input_csv_row_schema = RcvCompraNoIncluirCsvRowSchema()

        raw_data = {
            'Tipo Doc': '33',
            'Tipo Compra': 'No Corresp. Incluir',
            'RUT Proveedor': '12345678-5',
            'Razon Social': 'Fake Seller S.A.',
            'Folio': '19000035',
            'Fecha Docto': '13/12/2019',
            'Fecha Recepcion': '14/12/2019 15:56:27',
            'Fecha Acuse': '',
            'Monto Exento': '0',
            'Monto Neto': '87699',
            'Monto IVA Recuperable': '',
            'Monto Iva No Recuperable': '16663',
            'Codigo IVA No Rec.': '9',
            'Monto Total': '104362',
            'Monto Neto Activo Fijo': '',
            'IVA Activo Fijo': '',
            'IVA uso Comun': '',
            'Impto. Sin Derecho a Credito': '',
            'IVA No Retenido': '0',
            'NCE o NDE sobre Fact. de Compra': '0',
            'Codigo Otro Impuesto': '23',
            'Valor Otro Impuesto': '1200',
            'Tasa Otro Impuesto': '31.5',
        }

        with _RcvCompraCsvRowSchemaContext(schema_context):
            deserialized_data = input_csv_row_schema.load(raw_data)

        result = input_csv_row_schema.to_detalle_entry(deserialized_data)
        expected_result = RcNoIncluirDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=19000035,
            fecha_emision_date=datetime.date(2019, 12, 13),
            proveedor_rut=Rut('12345678-5'),
            monto_total=104362,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 12, 14, 15, 56, 27), tz=SII_OFFICIAL_TZ
            ),
            tipo_compra='NO_CORRESPONDE_INCLUIR',
            proveedor_razon_social='Fake Seller S.A.',
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
            otros_impuestos=None,
            fecha_acuse_dt=None,
        )

        self.assertEqual(result, expected_result)


class RcvCompraReclamadoCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_reclamado_row(self) -> None:
        schema_context: _RcvCompraCsvRowContext = {
            'contribuyente_rut': Rut('1-9'),
        }
        input_csv_row_schema = RcvCompraReclamadoCsvRowSchema()

        raw_data = {
            'Tipo Doc': '33',
            'Tipo Compra': 'Del Giro',
            'RUT Proveedor': '12345678-5',
            'Razon Social': 'Fake Seller S.A.',
            'Folio': '1000055',
            'Fecha Docto': '05/06/2019',
            'Fecha Recepcion': '05/06/2019 21:58:49',
            'Fecha Reclamo': '12/06/2019 09:47:23',
            'Monto Exento': '0',
            'Monto Neto': '970894',
            'Monto IVA Recuperable': '184470',
            'Monto Iva No Recuperable': '',
            'Codigo IVA No Rec.': '',
            'Monto Total': '1155364',
            'Monto Neto Activo Fijo': '',
            'IVA Activo Fijo': '',
            'IVA uso Comun': '',
            'Impto. Sin Derecho a Credito': '',
            'IVA No Retenido': '0',
            'NCE o NDE sobre Fact. de Compra': '0',
            'Codigo Otro Impuesto': '',
            'Valor Otro Impuesto': '',
            'Tasa Otro Impuesto': '',
        }

        with _RcvCompraCsvRowSchemaContext(schema_context):
            deserialized_data = input_csv_row_schema.load(raw_data)

        result = input_csv_row_schema.to_detalle_entry(deserialized_data)
        expected_result = RcReclamadoDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=1000055,
            fecha_emision_date=datetime.date(2019, 6, 5),
            proveedor_rut=Rut('12345678-5'),
            monto_total=1155364,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 6, 5, 21, 58, 49), tz=SII_OFFICIAL_TZ
            ),
            tipo_compra='DEL_GIRO',
            proveedor_razon_social='Fake Seller S.A.',
            monto_exento=0,
            monto_neto=970894,
            monto_iva_recuperable=184470,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            otros_impuestos=None,
            fecha_reclamo_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 6, 12, 9, 47, 23), tz=SII_OFFICIAL_TZ
            ),
        )

        self.assertEqual(result, expected_result)


class RcvCompraPendienteCsvRowSchemaTest(unittest.TestCase):
    def test_parse_rcv_compra_pendiente_row(self) -> None:
        schema_context: _RcvCompraCsvRowContext = {
            'contribuyente_rut': Rut('1-9'),
        }
        input_csv_row_schema = RcvCompraPendienteCsvRowSchema()

        raw_data = {
            'Tipo Doc': '33',
            'Tipo Compra': 'Del Giro',
            'RUT Proveedor': '12345678-5',
            'Razon Social': 'Fake Seller S.A.',
            'Folio': '9800042',
            'Fecha Docto': '28/06/2019',
            'Fecha Recepcion': '01/07/2019 13:21:32',
            'Monto Exento': '0',
            'Monto Neto': '41838',
            'Monto IVA Recuperable': '7949',
            'Monto Iva No Recuperable': '',
            'Codigo IVA No Rec.': '',
            'Monto Total': '49787',
            'Monto Neto Activo Fijo': '',
            'IVA Activo Fijo': '',
            'IVA uso Comun': '',
            'Impto. Sin Derecho a Credito': '',
            'IVA No Retenido': '0',
            'NCE o NDE sobre Fact. de Compra': '0',
            'Codigo Otro Impuesto': '',
            'Valor Otro Impuesto': '',
            'Tasa Otro Impuesto': '',
        }

        with _RcvCompraCsvRowSchemaContext(schema_context):
            deserialized_data = input_csv_row_schema.load(raw_data)

        result = input_csv_row_schema.to_detalle_entry(deserialized_data)
        expected_result = RcPendienteDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=9800042,
            fecha_emision_date=datetime.date(2019, 6, 28),
            proveedor_rut=Rut('12345678-5'),
            monto_total=49787,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                datetime.datetime(2019, 7, 1, 13, 21, 32), tz=SII_OFFICIAL_TZ
            ),
            tipo_compra='DEL_GIRO',
            proveedor_razon_social='Fake Seller S.A.',
            monto_exento=0,
            monto_neto=41838,
            monto_iva_recuperable=7949,
            monto_iva_no_recuperable=None,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=None,
            iva_activo_fijo=None,
            iva_uso_comun=None,
            impto_sin_derecho_a_credito=None,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra='0',
            otros_impuestos=None,
        )

        self.assertEqual(result, expected_result)


class FunctionsTest(unittest.TestCase):
    maxDiff = None

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
        assert isinstance(items, Iterable) and isinstance(items, Iterator)

        expected_entry_struct = RvDetalleEntry(
            contribuyente_rut=Rut('1-9'),
            tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=506,
            fecha_emision_date=datetime.date(2019, 6, 4),
            cliente_rut=Rut('12345678-5'),
            monto_total=2082715,
            fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                dt=datetime.datetime(2019, 6, 18, 17, 1, 6),
                tz=SII_OFFICIAL_TZ,
            ),
            tipo_venta='DEL_GIRO',
            cliente_razon_social='Fake Company S.A.',
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
            documento_referencias=None,
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
            otros_impuestos=None,
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
        assert isinstance(items, Iterable) and isinstance(items, Iterator)

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.cliente_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.cliente_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def test_parse_rcv_venta_csv_file_missing_required_fields(self) -> None:
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
        assert isinstance(items, Iterable) and isinstance(items, Iterator)

        items_list = list(items)

        expected_entries_list: list[
            tuple[Optional[RvDetalleEntry], int, dict[str, object], dict[str, object]]
        ]
        expected_entries_list = [
            (
                None,
                1,
                {
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '12345678-5',
                    'Razon Social': 'Fake Company S.A. ',
                    'Folio': '506',
                    'Fecha Docto': '04/06/2019',
                    'Fecha Acuse Recibo': None,
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1750181',
                    'Monto IVA': '332534',
                    'Monto total': '2082715',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {
                    'validation': {
                        'Tipo Doc': ['Missing data for required field.'],
                        'Fecha Recepcion': ['Missing data for required field.'],
                    }
                },
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=508,
                    fecha_emision_date=datetime.date(2019, 6, 28),
                    monto_total=2629420,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 7, 1, 13, 49, 42),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    cliente_rut=Rut('12345678-5'),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='Fake Company S.A.',
                    fecha_acuse_dt=None,
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=2209597,
                    monto_iva=419823,
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
                    documento_referencias=None,
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
                    otros_impuestos=None,
                ),
                2,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '12345678-5',
                    'Razon Social': '  Fake Company S.A.',
                    'Folio': '508',
                    'Fecha Docto': '28/06/2019',
                    'Fecha Recepcion': '01/07/2019 13:49:42',
                    'Fecha Acuse Recibo': None,
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '2209597',
                    'Monto IVA': '419823',
                    'Monto total': '2629420',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA,
                    folio=88,
                    fecha_emision_date=datetime.date(2017, 8, 4),
                    monto_total=18939225,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2017, 9, 13, 10, 18, 59),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    cliente_rut=Rut('4954153-8'),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='Faker Company',
                    fecha_acuse_dt=None,
                    fecha_reclamo_dt=None,
                    monto_exento=None,
                    monto_neto=15915315,
                    monto_iva=3023910,
                    iva_retenido_total=None,
                    iva_retenido_parcial=None,
                    iva_no_retenido=None,
                    iva_propio=None,
                    iva_terceros=None,
                    liquidacion_factura_emisor_rut=None,
                    neto_comision_liquidacion_factura=None,
                    exento_comision_liquidacion_factura=None,
                    iva_comision_liquidacion_factura=None,
                    iva_fuera_de_plazo=None,
                    documento_referencias=None,
                    num_ident_receptor_extranjero=None,
                    nacionalidad_receptor_extranjero=None,
                    credito_empresa_constructora=None,
                    impuesto_zona_franca_ley_18211=None,
                    garantia_dep_envases=None,
                    indicador_venta_sin_costo=None,
                    indicador_servicio_periodico=None,
                    monto_no_facturable=None,
                    total_monto_periodo=None,
                    venta_pasajes_transporte_nacional=None,
                    venta_pasajes_transporte_internacional=None,
                    numero_interno=None,
                    codigo_sucursal=None,
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=None,
                ),
                3,
                {
                    'Codigo Sucursal': None,
                    'Credito empresa constructora': None,
                    'Documento Referencias': None,
                    'Exento Comision Liquid. Factura': None,
                    'Fecha Acuse Recibo': None,
                    'Fecha Docto': '04/08/2017',
                    'Fecha Recepcion': '13/09/2017 10:18:59',
                    'Fecha Reclamo': None,
                    'Folio': '88',
                    'Garantia Dep. Envases': None,
                    'IVA Comision Liquid. Factura': None,
                    'IVA Retenido Parcial': None,
                    'IVA Retenido Total': None,
                    'IVA Terceros': None,
                    'IVA fuera de plazo': None,
                    'IVA no retenido': None,
                    'IVA propio': None,
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Indicador Servicio Periodico': None,
                    'Indicador Venta sin Costo': None,
                    'Monto Exento': None,
                    'Monto IVA': '3023910',
                    'Monto Neto': '15915315',
                    'Monto No facturable': None,
                    'Monto total': '18939225',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Neto Comision Liquid. Factura': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Numero Interno': None,
                    'Otros Impuestos': None,
                    'RUT Emisor Liquid. Factura': None,
                    'Razon Social': 'Faker Company',
                    'Rut cliente': '4954153-8',
                    'Tipo Doc': '30',
                    'Tipo Venta': 'DEL_GIRO',
                    'Total Monto Periodo': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Venta Pasajes Transporte Nacional': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
        ]
        self.assertEqual(items_list, expected_entries_list)

    def _test_parse_rcv_compra_csv_file_proveedor_rz_leading_trailing_whitespace(
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
        assert isinstance(items, Iterable) and isinstance(items, Iterator)

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.proveedor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.proveedor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def test_parse_rcv_venta_csv_file_conversion_error(self) -> None:
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
                max_n_rows=2,
            )
            assert isinstance(items, Iterable) and isinstance(items, Iterator)
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

    def test_parse_rcv_venta_csv_file_empty_otros_impuestos_rows(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-extra-empty-impuestos-rows.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
        )
        items_list = list(items)
        expected_entries_list: list[
            tuple[Optional[RvDetalleEntry], int, dict[str, object], dict[str, object]]
        ]
        expected_entries_list = [
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=6541,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('54213736-3'),
                    monto_total=9565862,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 9),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='CHILE SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=7217280,
                    monto_iva=1371283,
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
                    documento_referencias=None,
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='27',
                            valor_otro_impuesto=275904,
                            tasa_otro_impuesto=Decimal('10'),
                        ),
                        OtrosImpuestos(
                            codigo_otro_impuesto='271',
                            valor_otro_impuesto=701395,
                            tasa_otro_impuesto=Decimal('18'),
                        ),
                    ],
                ),
                1,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '54213736-3',
                    'Razon Social': 'CHILE SPA',
                    'Folio': '6541',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:09:00',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '7217280',
                    'Monto IVA': '1371283',
                    'Monto total': '9565862',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '27',
                            'valor_otro_impuesto': '275904',
                            'tasa_otro_impuesto': '10',
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': '701395',
                            'tasa_otro_impuesto': '18',
                        },
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=9874,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('42509414-9'),
                    monto_total=13136156,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 9, 53, 17),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='COMERCIAL SPA',
                    fecha_acuse_dt=None,
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=8879040,
                    monto_iva=1687018,
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
                    documento_referencias=None,
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='24',
                            valor_otro_impuesto=2570098,
                            tasa_otro_impuesto=Decimal('31.5'),
                        )
                    ],
                ),
                3,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '42509414-9',
                    'Razon Social': 'COMERCIAL SPA',
                    'Folio': '9874',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 09:53:17',
                    'Fecha Acuse Recibo': None,
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '8879040',
                    'Monto IVA': '1687018',
                    'Monto total': '13136156',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '2570098',
                            'tasa_otro_impuesto': '31.5',
                        }
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=3210,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('68840666-8'),
                    monto_total=30471437,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 58, 51),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='TEXAS SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=20522880,
                    monto_iva=3899347,
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
                    documento_referencias=None,
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='24',
                            valor_otro_impuesto=6049210,
                            tasa_otro_impuesto=Decimal('31.5'),
                        )
                    ],
                ),
                4,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '68840666-8',
                    'Razon Social': 'TEXAS SPA',
                    'Folio': '3210',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:58:51',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '20522880',
                    'Monto IVA': '3899347',
                    'Monto total': '30471437',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '6049210',
                            'tasa_otro_impuesto': '31.5',
                        }
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA,  # noqa: E501
                    folio=3210,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('68840666-8'),
                    monto_total=30471437,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 58, 51),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='TEXAS SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=9999,
                    monto_iva=3899347,
                    iva_retenido_total=2020,
                    iva_retenido_parcial=None,
                    iva_no_retenido=0,
                    iva_propio=0,
                    iva_terceros=0,
                    liquidacion_factura_emisor_rut=None,
                    neto_comision_liquidacion_factura=0,
                    exento_comision_liquidacion_factura=0,
                    iva_comision_liquidacion_factura=0,
                    iva_fuera_de_plazo=0,
                    documento_referencias=None,
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='24',
                            valor_otro_impuesto=6049210,
                            tasa_otro_impuesto=Decimal('31.5'),
                        )
                    ],
                ),
                5,
                {
                    'Tipo Doc': '34',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '68840666-8',
                    'Razon Social': 'TEXAS SPA',
                    'Folio': '3210',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:58:51',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '9999',
                    'Monto IVA': '3899347',
                    'Monto total': '30471437',
                    'IVA Retenido Total': '2020',
                    'IVA Retenido Parcial': None,
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '6049210',
                            'tasa_otro_impuesto': '31.5',
                        }
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=3210,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('54213736-3'),
                    monto_total=30471437,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 58, 51),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='THE COMPANY SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=9999,
                    monto_iva=3899347,
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
                    documento_referencias=None,
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='24',
                            valor_otro_impuesto=6049210,
                            tasa_otro_impuesto=Decimal('31.5'),
                        ),
                        OtrosImpuestos(
                            codigo_otro_impuesto='271',
                            valor_otro_impuesto=701395,
                            tasa_otro_impuesto=Decimal('18'),
                        ),
                    ],
                ),
                6,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '54213736-3',
                    'Razon Social': 'THE COMPANY SPA',
                    'Folio': '3210',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:58:51',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '9999',
                    'Monto IVA': '3899347',
                    'Monto total': '30471437',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': None,
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '6049210',
                            'tasa_otro_impuesto': '31.5',
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': '701395',
                            'tasa_otro_impuesto': '18',
                        },
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
        ]
        self.assertEqual(items_list, expected_entries_list)

    def test_parse_rcv_venta_csv_file_multiple_dte_referencias(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-multiple-dte-referencias.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
        )
        items_list = list(items)

        expected_entries_list: list[
            tuple[Optional[RvDetalleEntry], int, dict[str, object], dict[str, object]]
        ]
        expected_entries_list = [
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=506,
                    fecha_emision_date=datetime.date(2019, 6, 4),
                    cliente_rut=Rut('12345678-5'),
                    monto_total=2082715,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 6, 18, 17, 1, 6),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='Fake Company S.A.',
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
                    documento_referencias=None,
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
                    otros_impuestos=None,
                ),
                1,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '12345678-5',
                    'Razon Social': 'Fake Company S.A. ',
                    'Folio': '506',
                    'Fecha Docto': '04/06/2019',
                    'Fecha Recepcion': '18/06/2019 17:01:06',
                    'Fecha Acuse Recibo': None,
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1750181',
                    'Monto IVA': '332534',
                    'Monto total': '2082715',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Documento Referencias': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=14239,
                    fecha_emision_date=datetime.date(2025, 12, 9),
                    cliente_rut=Rut('77697060-3'),
                    monto_total=658284,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 12, 9, 8, 50, 45),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='DIRECT LTDA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 12, 10, 13, 14, 17),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=553180,
                    monto_iva=105104,
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
                    documento_referencias=[
                        DocumentoReferencia(
                            tipo_documento_referencia=52,
                            folio_documento_referencia=10370,
                        ),
                        DocumentoReferencia(
                            tipo_documento_referencia=52,
                            folio_documento_referencia=10371,
                        ),
                    ],
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
                    otros_impuestos=None,
                ),
                2,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '77697060-3',
                    'Razon Social': 'DIRECT LTDA',
                    'Folio': '14239',
                    'Fecha Docto': '09/12/2025',
                    'Fecha Recepcion': '09/12/2025 08:50:45',
                    'Fecha Acuse Recibo': '10/12/2025 13:14:17',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '553180',
                    'Monto IVA': '105104',
                    'Monto total': '658284',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Documento Referencias': [
                        {
                            'tipo_documento_referencia': 52,
                            'folio_documento_referencia': 10370,
                        },
                        {
                            'tipo_documento_referencia': 52,
                            'folio_documento_referencia': 10371,
                        },
                    ],
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=3210,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    cliente_rut=Rut('54213736-3'),
                    monto_total=30471437,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 58, 51),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='THE COMPANY SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=9999,
                    monto_iva=3899347,
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
                    documento_referencias=[
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=200,
                        ),
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=300,
                        ),
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=400,
                        ),
                    ],
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': 6049210,
                            'tasa_otro_impuesto': Decimal('31.5'),
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': 701395,
                            'tasa_otro_impuesto': Decimal('18'),
                        },
                    ],
                ),
                3,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '54213736-3',
                    'Razon Social': 'THE COMPANY SPA',
                    'Folio': '3210',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:58:51',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '9999',
                    'Monto IVA': '3899347',
                    'Monto total': '30471437',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Documento Referencias': [
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 200,
                        },
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 300,
                        },
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 400,
                        },
                    ],
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '6049210',
                            'tasa_otro_impuesto': '31.5',
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': '701395',
                            'tasa_otro_impuesto': '18',
                        },
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
        ]
        self.assertEqual(items_list, expected_entries_list)

    def test_parse_rcv_venta_csv_file_validation_errors(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-validation-errors.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
        )
        items_list = list(items)
        expected_entries_list: list[
            tuple[Optional[RvDetalleEntry], int, dict[str, object], dict[str, object]]
        ]
        expected_entries_list = [
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=3210,
                    fecha_emision_date=datetime.date(2025, 9, 1),
                    monto_total=30471437,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 1, 10, 58, 51),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    cliente_rut=Rut('54213736-3'),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='THE COMPANY SPA',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2025, 9, 8, 14, 15, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=9999,
                    monto_iva=3899347,
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
                    documento_referencias=[
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=200,
                        ),
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=300,
                        ),
                        DocumentoReferencia(
                            tipo_documento_referencia=33,
                            folio_documento_referencia=400,
                        ),
                    ],
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
                    codigo_sucursal='12354',
                    nce_o_nde_sobre_factura_de_compra=None,
                    otros_impuestos=[
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': 6049210,
                            'tasa_otro_impuesto': Decimal('31.5'),
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': 701395,
                            'tasa_otro_impuesto': Decimal('18'),
                        },
                    ],
                ),
                1,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '54213736-3',
                    'Razon Social': 'THE COMPANY SPA',
                    'Folio': '3210',
                    'Fecha Docto': '01/09/2025',
                    'Fecha Recepcion': '01/09/2025 10:58:51',
                    'Fecha Acuse Recibo': '08/09/2025 14:15:23',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '9999',
                    'Monto IVA': '3899347',
                    'Monto total': '30471437',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '12354',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '24',
                            'valor_otro_impuesto': '6049210',
                            'tasa_otro_impuesto': '31.5',
                        },
                        {
                            'codigo_otro_impuesto': '271',
                            'valor_otro_impuesto': '701395',
                            'tasa_otro_impuesto': '18',
                        },
                    ],
                    'Documento Referencias': [
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 200,
                        },
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 300,
                        },
                        {
                            'tipo_documento_referencia': 33,
                            'folio_documento_referencia': 400,
                        },
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RvDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=14395,
                    fecha_emision_date=datetime.date(2026, 1, 7),
                    monto_total=1959157,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2026, 1, 7, 13, 18, 20),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    cliente_rut=Rut('81859341-4'),
                    tipo_venta='DEL_GIRO',
                    cliente_razon_social='POLAR S.A.',
                    fecha_acuse_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2026, 1, 8, 15, 48, 9),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    fecha_reclamo_dt=None,
                    monto_exento=0,
                    monto_neto=1646350,
                    monto_iva=312807,
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
                    documento_referencias=[
                        DocumentoReferencia(
                            folio_documento_referencia=10489,
                            tipo_documento_referencia=52,
                        )
                    ],
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
                    otros_impuestos=None,
                ),
                3,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '81859341-4',
                    'Razon Social': 'POLAR S.A.',
                    'Folio': '14395',
                    'Fecha Docto': '07/01/2026',
                    'Fecha Recepcion': '07/01/2026 13:18:20',
                    'Fecha Acuse Recibo': '08/01/2026 15:48:09',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1646350',
                    'Monto IVA': '312807',
                    'Monto total': '1959157',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Documento Referencias': [
                        {
                            'tipo_documento_referencia': 52,
                            'folio_documento_referencia': 10489,
                        }
                    ],
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                None,
                4,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '81859341-4',
                    'Razon Social': 'POLAR S.A.',
                    'Folio': '14396',
                    'Fecha Docto': '07/01/2026',
                    'Fecha Recepcion': '07/01/2026 13:18:20',
                    'Fecha Acuse Recibo': '08/01/2026 15:48:09',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1646350',
                    'Monto IVA': '312807',
                    'Monto total': '1959157',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {
                    'validation': {
                        "Documento Referencias": (
                            "Both 'tipo_documento_referencia' (52) and"
                            " 'folio_documento_referencia' () must be provided."
                        )
                    }
                },
            ),
            (
                None,
                5,
                {
                    'Tipo Doc': '33',
                    'Tipo Venta': 'DEL_GIRO',
                    'Rut cliente': '81859341-4',
                    'Razon Social': 'POLAR S.A.',
                    'Folio': '14397',
                    'Fecha Docto': '07/01/2026',
                    'Fecha Recepcion': '07/01/2026 13:18:20',
                    'Fecha Acuse Recibo': '08/01/2026 15:48:09',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1646350',
                    'Monto IVA': '312807',
                    'Monto total': '1959157',
                    'IVA Retenido Total': '0',
                    'IVA Retenido Parcial': '0',
                    'IVA no retenido': '0',
                    'IVA propio': '0',
                    'IVA Terceros': '0',
                    'RUT Emisor Liquid. Factura': None,
                    'Neto Comision Liquid. Factura': '0',
                    'Exento Comision Liquid. Factura': '0',
                    'IVA Comision Liquid. Factura': '0',
                    'IVA fuera de plazo': '0',
                    'Num. Ident. Receptor Extranjero': None,
                    'Nacionalidad Receptor Extranjero': None,
                    'Credito empresa constructora': '0',
                    'Impto. Zona Franca (Ley 18211)': None,
                    'Garantia Dep. Envases': '0',
                    'Indicador Venta sin Costo': '2',
                    'Indicador Servicio Periodico': '0',
                    'Monto No facturable': '0',
                    'Total Monto Periodo': '0',
                    'Venta Pasajes Transporte Nacional': None,
                    'Venta Pasajes Transporte Internacional': None,
                    'Numero Interno': None,
                    'Codigo Sucursal': '0',
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {
                    'validation': {
                        "Documento Referencias": (
                            "Invalid 'folio_documento_referencia': (1057539-304-SE26)."
                        )
                    }
                },
            ),
        ]
        self.assertEqual(items_list, expected_entries_list)

    def test_parse_rcv_compra_registro_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_registro_csv_file'.
        pass

    def test_parse_rcv_compra_registro_csv_file_proveedor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_proveedor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_registro_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-registro-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_no_incluir_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_no_incluir_csv_file'.
        pass

    def test_parse_rcv_compra_no_incluir_csv_file_proveedor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_proveedor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_no_incluir_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-no_incluir-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_reclamado_csv_file(self) -> None:
        rcv_file_path = get_test_file_path('test_data/sii-rcv/RCV-compra-reclamado.csv')

        items = parse_rcv_compra_reclamado_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )
        result = list(items)

        # Expected output: list of RcReclamadoDetalleEntry instances matching the CSV
        expected_result = [
            (
                RcReclamadoDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=1000055,
                    fecha_emision_date=datetime.date(2019, 6, 5),
                    proveedor_rut=Rut('12345678-5'),
                    monto_total=1155364,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 6, 5, 21, 58, 49),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_compra='DEL_GIRO',
                    proveedor_razon_social='Fake Company S.A.',
                    monto_exento=0,
                    monto_neto=970894,
                    monto_iva_recuperable=184470,
                    monto_iva_no_recuperable=None,
                    codigo_iva_no_rec=None,
                    monto_neto_activo_fijo=None,
                    iva_activo_fijo=None,
                    iva_uso_comun=None,
                    impto_sin_derecho_a_credito=None,
                    iva_no_retenido=0,
                    nce_o_nde_sobre_factura_de_compra='0',
                    otros_impuestos=[
                        OtrosImpuestos(
                            codigo_otro_impuesto='23',
                            valor_otro_impuesto=12000,
                            tasa_otro_impuesto=Decimal('2.967999999'),
                        )
                    ],
                    fecha_reclamo_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 6, 12, 9, 47, 23),
                        tz=SII_OFFICIAL_TZ,
                    ),
                ),
                1,
                {
                    'Tipo Doc': '33',
                    'Tipo Compra': 'DEL_GIRO',
                    'RUT Proveedor': '12345678-5',
                    'Razon Social': 'Fake Company S.A. ',
                    'Folio': '1000055',
                    'Fecha Docto': '05/06/2019',
                    'Fecha Recepcion': '05/06/2019 21:58:49',
                    'Fecha Reclamo': '12/06/2019 09:47:23',
                    'Monto Exento': '0',
                    'Monto Neto': '970894',
                    'Monto IVA Recuperable': '184470',
                    'Monto Iva No Recuperable': None,
                    'Codigo IVA No Rec.': None,
                    'Monto Total': '1155364',
                    'Monto Neto Activo Fijo': None,
                    'IVA Activo Fijo': None,
                    'IVA uso Comun': None,
                    'Impto. Sin Derecho a Credito': None,
                    'IVA No Retenido': '0',
                    'NCE o NDE sobre Fact. de Compra': '0',
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': '23',
                            'valor_otro_impuesto': '12000',
                            'tasa_otro_impuesto': '2.967999999',
                        },
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RcReclamadoDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.NOTA_CREDITO_ELECTRONICA,
                    folio=70013,
                    fecha_emision_date=datetime.date(2019, 6, 24),
                    proveedor_rut=Rut('12345678-5'),
                    monto_total=1966880,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 6, 24, 15, 24, 41),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_compra='DEL_GIRO',
                    proveedor_razon_social='Fake Company S.A.',
                    monto_exento=0,
                    monto_neto=1652840,
                    monto_iva_recuperable=314040,
                    monto_iva_no_recuperable=None,
                    codigo_iva_no_rec=None,
                    monto_neto_activo_fijo=None,
                    iva_activo_fijo=None,
                    iva_uso_comun=None,
                    impto_sin_derecho_a_credito=None,
                    iva_no_retenido=0,
                    nce_o_nde_sobre_factura_de_compra='0',
                    otros_impuestos=None,
                    fecha_reclamo_dt=None,
                ),
                2,
                {
                    'Tipo Doc': '61',
                    'Tipo Compra': 'DEL_GIRO',
                    'RUT Proveedor': '12345678-5',
                    'Razon Social': '  Fake Company S.A.',
                    'Folio': '70013',
                    'Fecha Docto': '24/06/2019',
                    'Fecha Recepcion': '24/06/2019 15:24:41',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '1652840',
                    'Monto IVA Recuperable': '314040',
                    'Monto Iva No Recuperable': None,
                    'Codigo IVA No Rec.': None,
                    'Monto Total': '1966880',
                    'Monto Neto Activo Fijo': None,
                    'IVA Activo Fijo': None,
                    'IVA uso Comun': None,
                    'Impto. Sin Derecho a Credito': None,
                    'IVA No Retenido': '0',
                    'NCE o NDE sobre Fact. de Compra': '0',
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                RcReclamadoDetalleEntry(
                    contribuyente_rut=Rut('1-9'),
                    tipo_docto=cl_sii.rcv.constants.RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio=789456,
                    fecha_emision_date=datetime.date(2019, 6, 5),
                    proveedor_rut=Rut('76354771-K'),
                    monto_total=1155364,
                    fecha_recepcion_dt=convert_naive_dt_to_tz_aware(
                        dt=datetime.datetime(2019, 6, 5, 21, 58, 49),
                        tz=SII_OFFICIAL_TZ,
                    ),
                    tipo_compra='DEL_GIRO',
                    proveedor_razon_social='Fake Company S.A.',
                    monto_exento=0,
                    monto_neto=970894,
                    monto_iva_recuperable=184470,
                    monto_iva_no_recuperable=None,
                    codigo_iva_no_rec=None,
                    monto_neto_activo_fijo=None,
                    iva_activo_fijo=None,
                    iva_uso_comun=None,
                    impto_sin_derecho_a_credito=None,
                    iva_no_retenido=0,
                    nce_o_nde_sobre_factura_de_compra='0',
                    otros_impuestos=None,
                    fecha_reclamo_dt=None,
                ),
                3,
                {
                    'Tipo Doc': '33',
                    'Tipo Compra': 'DEL_GIRO',
                    'RUT Proveedor': '76354771-K',
                    'Razon Social': 'Fake Company S.A. ',
                    'Folio': '789456',
                    'Fecha Docto': '05/06/2019',
                    'Fecha Recepcion': '05/06/2019 21:58:49',
                    'Fecha Reclamo': None,
                    'Monto Exento': '0',
                    'Monto Neto': '970894',
                    'Monto IVA Recuperable': '184470',
                    'Monto Iva No Recuperable': None,
                    'Codigo IVA No Rec.': None,
                    'Monto Total': '1155364',
                    'Monto Neto Activo Fijo': None,
                    'IVA Activo Fijo': None,
                    'IVA uso Comun': None,
                    'Impto. Sin Derecho a Credito': None,
                    'IVA No Retenido': '0',
                    'NCE o NDE sobre Fact. de Compra': '0',
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {},
            ),
            (
                None,
                4,
                {
                    'Tipo Doc': '33',
                    'Tipo Compra': 'DEL_GIRO',
                    'RUT Proveedor': 'INVALID-RUT',
                    'Razon Social': 'Fake Company S.A.',
                    'Folio': 'notanumber',
                    'Fecha Docto': 'invalid-date',
                    'Fecha Recepcion': 'invalid-datetime',
                    'Fecha Reclamo': 'invalid-datetime',
                    'Monto Exento': 'notanumber',
                    'Monto Neto': 'notanumber',
                    'Monto IVA Recuperable': 'notanumber',
                    'Monto Iva No Recuperable': 'notanumber',
                    'Codigo IVA No Rec.': 'notanumber',
                    'Monto Total': 'notanumber',
                    'Monto Neto Activo Fijo': 'notanumber',
                    'IVA Activo Fijo': 'notanumber',
                    'IVA uso Comun': 'notanumber',
                    'Impto. Sin Derecho a Credito': 'notanumber',
                    'IVA No Retenido': 'notanumber',
                    'NCE o NDE sobre Fact. de Compra': 'notanumber',
                    'Otros Impuestos': [
                        {
                            'codigo_otro_impuesto': 'notanumber',
                            'tasa_otro_impuesto': 'notanumber',
                            'valor_otro_impuesto': 'notanumber',
                        }
                    ],
                    'contribuyente_rut': Rut('1-9'),
                },
                {
                    'validation': {
                        'RUT Proveedor': ['Not a syntactically valid RUT.'],
                        'Folio': ['Not a valid integer.'],
                        'Fecha Docto': ['Not a valid date.'],
                        'Monto Total': ['Not a valid integer.'],
                        'Fecha Recepcion': ['Not a valid datetime.'],
                        'Monto Exento': ['Not a valid integer.'],
                        'Monto Neto': ['Not a valid integer.'],
                        'Monto IVA Recuperable': ['Not a valid integer.'],
                        'Monto Iva No Recuperable': ['Not a valid integer.'],
                        'Monto Neto Activo Fijo': ['Not a valid integer.'],
                        'IVA Activo Fijo': ['Not a valid integer.'],
                        'IVA uso Comun': ['Not a valid integer.'],
                        'Impto. Sin Derecho a Credito': ['Not a valid integer.'],
                        'IVA No Retenido': ['Not a valid integer.'],
                        'Fecha Reclamo': ['Not a valid datetime.'],
                    }
                },
            ),
            (
                None,
                5,
                {
                    'Fecha Reclamo': None,
                    'Monto IVA Recuperable': None,
                    'Monto Iva No Recuperable': None,
                    'Codigo IVA No Rec.': None,
                    'Monto Neto Activo Fijo': None,
                    'IVA Activo Fijo': None,
                    'IVA uso Comun': None,
                    'Impto. Sin Derecho a Credito': None,
                    'IVA No Retenido': None,
                    'NCE o NDE sobre Fact. de Compra': None,
                    'Otros Impuestos': None,
                    'contribuyente_rut': Rut('1-9'),
                },
                {
                    'validation': {
                        'RUT Proveedor': ['Missing data for required field.'],
                        'Tipo Doc': ['Missing data for required field.'],
                        'Tipo Compra': ['Missing data for required field.'],
                        'Folio': ['Missing data for required field.'],
                        'Fecha Docto': ['Missing data for required field.'],
                        'Monto Total': ['Missing data for required field.'],
                        'Razon Social': ['Missing data for required field.'],
                        'Fecha Recepcion': ['Missing data for required field.'],
                        'Monto Exento': ['Missing data for required field.'],
                        'Monto Neto': ['Missing data for required field.'],
                    }
                },
            ),
        ]
        self.assertEqual(result, expected_result)

    def test_parse_rcv_compra_reclamado_csv_file_proveedor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_proveedor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_reclamado_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-reclamado-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_pendiente_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_pendiente_csv_file'.
        pass

    def test_parse_rcv_compra_pendiente_csv_file_proveedor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_proveedor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_pendiente_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-pendiente-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test__parse_rcv_csv_file(self) -> None:
        # TODO: implement for '_parse_rcv_csv_file'.
        pass

    def test_get_rcv_csv_file_parser_returns_correct_parser(self) -> None:
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
            get_rcv_csv_file_parser(RcvKind.COMPRAS, DummyEstadoContable())  # type: ignore[arg-type] # noqa: E501

        # Test unknown rcv_kind
        class DummyRcvKind:
            pass

        with self.assertRaises(Exception):
            get_rcv_csv_file_parser(DummyRcvKind(), None)  # type: ignore[arg-type]

    def test__parse_rv_documento_referencias(self) -> None:
        """Test _parse_rv_documento_referencias function with all possible scenarios."""

        # Test case 1: Both parameters are None - should return None
        with self.subTest("Both None"):
            result = _parse_rv_documento_referencias(None, None)
            self.assertIsNone(result)

        # Test case 2: Both parameters are empty strings - should return None
        with self.subTest("Mixed empty values"):
            result = _parse_rv_documento_referencias("0", "")
            self.assertIsNone(result)

        # Test case 3: Only tipo provided (folio empty) - should raise ValueError
        with self.subTest("Only tipo provided"):
            with self.assertRaises(ValueError) as cm:
                _parse_rv_documento_referencias("33", None)
            self.assertIn("Both 'tipo_documento_referencia'", str(cm.exception))

            with self.assertRaises(ValueError):
                _parse_rv_documento_referencias(33, "")

            with self.assertRaises(ValueError):
                _parse_rv_documento_referencias("33", "0")

        # Test case 4: Only folio provided (tipo empty) - should raise ValueError
        with self.subTest("Only folio provided"):
            with self.assertRaises(ValueError) as cm:
                _parse_rv_documento_referencias(None, "12345")
            self.assertIn("Both 'tipo_documento_referencia'", str(cm.exception))

            with self.assertRaises(ValueError):
                _parse_rv_documento_referencias("", "12345")

            with self.assertRaises(ValueError):
                _parse_rv_documento_referencias("0", "12345")

        # Test case 5: Valid single folio with string tipo
        with self.subTest("Valid single folio - string tipo"):
            result = _parse_rv_documento_referencias("33", "12345")
            expected = [
                {
                    'tipo_documento_referencia': 33,
                    'folio_documento_referencia': 12345,
                }
            ]
            self.assertEqual(result, expected)

        # Test case 6: Valid single folio with integer tipo
        with self.subTest("Valid single folio - integer tipo"):
            result = _parse_rv_documento_referencias(52, "67890")
            expected = [
                {
                    'tipo_documento_referencia': 52,
                    'folio_documento_referencia': 67890,
                }
            ]
            self.assertEqual(result, expected)

        # Test case 7: Valid multiple folios - three folios
        with self.subTest("Valid three folios"):
            result = _parse_rv_documento_referencias("33", "200-300-400")
            expected = [
                {
                    'tipo_documento_referencia': 33,
                    'folio_documento_referencia': 200,
                },
                {
                    'tipo_documento_referencia': 33,
                    'folio_documento_referencia': 300,
                },
                {
                    'tipo_documento_referencia': 33,
                    'folio_documento_referencia': 400,
                },
            ]
            self.assertEqual(result, expected)

        # Test case 8: Invalid folio - non-numeric
        with self.subTest("Invalid folio - non-numeric"):
            with self.assertRaises(ValueError) as cm:
                _parse_rv_documento_referencias("33", "abc")
            self.assertIn("Invalid 'folio_documento_referencia'", str(cm.exception))

        # Test case 9: Non-string folio parameter (should work for integer)
        with self.subTest("Non-string folio"):
            result = _parse_rv_documento_referencias("33", 12345)  # type: ignore[arg-type]
            expected = [
                {
                    'tipo_documento_referencia': 33,
                    'folio_documento_referencia': 12345,
                }
            ]
            self.assertEqual(result, expected)
