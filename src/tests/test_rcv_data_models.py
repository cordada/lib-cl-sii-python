import dataclasses
import unittest
from datetime import date, datetime

import pydantic

import cl_sii.dte.constants
import cl_sii.dte.data_models
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rcv.constants import RcvTipoDocto
from cl_sii.rcv.data_models import (
    DocumentoReferencia,
    PeriodoTributario,
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RcvDetalleEntry,
    RvDetalleEntry,
)
from cl_sii.rut import Rut


class PeriodoTributarioTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.periodo_tributario_1 = PeriodoTributario(
            year=2019,
            month=4,
        )

    def test_validate_year_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('year',),
                'msg': "Value error, Value is out of the valid range for 'year'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field year
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                year=1899,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_month_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('month',),
                'msg': "Value error, Value is out of the valid range for 'month'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field month
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                month=0,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)

        # Validate the maximum value of the field month
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                month=13,
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)


class RcvDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rcv_detalle_entry_1 = RcvDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            monto_total=2996301,
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcvDetalleEntry.DATETIME_FIELDS_TZ,
            ),
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
                self.rcv_detalle_entry_1,
                folio=cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE - 1,
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
                self.rcv_detalle_entry_1,
                folio=cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE + 1,
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
                'loc': ('fecha_recepcion_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rcv_detalle_entry_1,
                fecha_recepcion_dt=datetime(2019, 4, 5, 12, 57, 32),
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
                'loc': ('fecha_recepcion_dt',),
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
                self.rcv_detalle_entry_1,
                fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
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


class RvDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rv_detalle_entry_1 = RvDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            tipo_venta='Del Giro',
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            cliente_rut=Rut('96790240-3'),
            cliente_razon_social='MINERA LOS PELAMBRES',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            monto_exento=0,
            monto_neto=1000000,
            monto_iva=190000,
            monto_total=1190000,
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
            indicador_venta_sin_costo=0,
            indicador_servicio_periodico=0,
            monto_no_facturable=0,
            total_monto_periodo=0,
            venta_pasajes_transporte_nacional=None,
            venta_pasajes_transporte_internacional=None,
            numero_interno=None,
            codigo_sucursal=None,
            nce_o_nde_sobre_factura_de_compra=None,
            otros_impuestos=None,
        )

    def test_constants_match(self) -> None:
        self.assertEqual(
            RvDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
        )

    def test_validate_cliente_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('cliente_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rv_detalle_entry_1,
                cliente_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(validation_errors, expected_validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # fecha_acuse_dt
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_acuse_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rv_detalle_entry_1,
                fecha_acuse_dt=datetime(2019, 4, 5, 12, 57, 32),
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
                'loc': ('fecha_acuse_dt',),
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
                self.rv_detalle_entry_1,
                fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
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

        # fecha_reclamo_dt
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_reclamo_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rv_detalle_entry_1,
                fecha_reclamo_dt=datetime(2019, 4, 5, 12, 57, 32),
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
                'loc': ('fecha_reclamo_dt',),
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
                self.rv_detalle_entry_1,
                fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
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

    def test_get_documento_referencia_dte_natural_keys(self) -> None:
        rv_detalle_entry = self.rv_detalle_entry_1

        # Detalle Entry that does not reference another documento:

        self.assertIsNone(rv_detalle_entry.documento_referencias)
        self.assertIsNone(rv_detalle_entry.get_documento_referencia_dte_natural_keys())

        # Detalle Entry that references a DTE:

        rv_detalle_entry_with_doc_ref = dataclasses.replace(
            rv_detalle_entry,
            tipo_docto=RcvTipoDocto.NOTA_CREDITO_ELECTRONICA,
            folio=12345,
            documento_referencias=[
                DocumentoReferencia(
                    tipo_documento_referencia=RcvTipoDocto.FACTURA_ELECTRONICA,
                    folio_documento_referencia=170,
                )
            ],
        )
        self.assertEqual(
            cl_sii.dte.data_models.DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDte.NOTA_CREDITO_ELECTRONICA,
                folio=12345,
            ),
            rv_detalle_entry_with_doc_ref.as_dte_data_l2().natural_key,
        )

        expected_doc_ref_dte_natural_key = [
            cl_sii.dte.data_models.DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,
                folio=170,
            )
        ]
        actual_doc_ref_dte_natural_key = (
            rv_detalle_entry_with_doc_ref.get_documento_referencia_dte_natural_keys()
        )

        self.assertEqual(expected_doc_ref_dte_natural_key, actual_doc_ref_dte_natural_key)

        # Detalle Entry that references a documento that is a valid DTE
        # but not a valid RCV Tipo de Documento:

        rv_detalle_entry_with_non_rcv_doc_ref = dataclasses.replace(
            rv_detalle_entry,
            documento_referencias=[
                DocumentoReferencia(
                    tipo_documento_referencia=cl_sii.dte.constants.TipoDte.GUIA_DESPACHO_ELECTRONICA,  # noqa: E501
                    folio_documento_referencia=12345,
                )
            ],
        )
        with self.assertRaisesRegex(ValueError, r'^52 is not a valid RcvTipoDocto$'):
            RcvTipoDocto(
                rv_detalle_entry_with_non_rcv_doc_ref.documento_referencias[0]['tipo_documento_referencia']  # type: ignore[index] # noqa: E501
            )

        expected_doc_ref_dte_natural_key = [
            cl_sii.dte.data_models.DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=cl_sii.dte.constants.TipoDte.GUIA_DESPACHO_ELECTRONICA,
                folio=12345,
            )
        ]
        actual_doc_ref_dte_natural_key = (
            rv_detalle_entry_with_non_rcv_doc_ref.get_documento_referencia_dte_natural_keys()
        )

        self.assertEqual(expected_doc_ref_dte_natural_key, actual_doc_ref_dte_natural_key)

        # Detalle Entry that references a documento with an invalid folio value (0):

        rv_detalle_entry_with_invalid_folio = dataclasses.replace(
            rv_detalle_entry,
            documento_referencias=[
                DocumentoReferencia(
                    tipo_documento_referencia=cl_sii.dte.constants.TipoDte.FACTURA_ELECTRONICA,  # noqa: E501
                    folio_documento_referencia=0,
                )
            ],
        )
        self.assertIsNone(
            rv_detalle_entry_with_invalid_folio.get_documento_referencia_dte_natural_keys()
        )


class RcRegistroDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rc_registro_detalle_entry_1 = RcRegistroDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            tipo_compra='Del Giro',
            fecha_emision_date=date(2019, 4, 1),
            proveedor_rut=Rut('96790240-3'),
            monto_total=2996301,
            proveedor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcRegistroDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RcRegistroDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            monto_exento=0,
            monto_neto=0,
            monto_iva_recuperable=0,
            monto_iva_no_recuperable=0,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=0,
            iva_activo_fijo=0,
            iva_uso_comun=0,
            impto_sin_derecho_a_credito=0,
            iva_no_retenido=None,
            tabacos_puros=0,
            tabacos_cigarrillos=0,
            tabacos_elaborados=0,
            nce_o_nde_sobre_factura_de_compra=None,
            otros_impuestos=None,
        )

    def test_constants_match(self) -> None:
        self.assertEqual(
            RcRegistroDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
        )

    def test_validate_proveedor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('proveedor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_registro_detalle_entry_1,
                proveedor_razon_social='',
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
                'loc': ('fecha_acuse_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_registro_detalle_entry_1,
                fecha_acuse_dt=datetime(2019, 4, 5, 12, 57, 32),
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
                'loc': ('fecha_acuse_dt',),
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
                self.rc_registro_detalle_entry_1,
                fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
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


class RcNoIncluirDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rc_no_incluir_detalle_entry_1 = RcNoIncluirDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            tipo_compra='Del Giro',
            fecha_emision_date=date(2019, 4, 1),
            proveedor_rut=Rut('96790240-3'),
            monto_total=2996301,
            proveedor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=SII_OFFICIAL_TZ,
            ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=SII_OFFICIAL_TZ,
            ),
            monto_exento=0,
            monto_neto=0,
            monto_iva_recuperable=0,
            monto_iva_no_recuperable=0,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=0,
            iva_activo_fijo=0,
            iva_uso_comun=0,
            impto_sin_derecho_a_credito=0,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra=None,
            otros_impuestos=None,
        )


class RcReclamadoDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rc_reclamado_detalle_entry_1 = RcReclamadoDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            tipo_compra='Del Giro',
            fecha_emision_date=date(2019, 4, 1),
            proveedor_rut=Rut('96790240-3'),
            monto_total=2996301,
            proveedor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ,
            ),
            monto_exento=0,
            monto_neto=0,
            monto_iva_recuperable=0,
            monto_iva_no_recuperable=0,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=0,
            iva_activo_fijo=0,
            iva_uso_comun=0,
            impto_sin_derecho_a_credito=0,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra=None,
            otros_impuestos=None,
        )

    def test_constants_match(self) -> None:
        self.assertEqual(
            RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
        )

    def test_validate_proveedor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('proveedor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_reclamado_detalle_entry_1,
                proveedor_razon_social='',
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
                'loc': ('fecha_reclamo_dt',),
                'msg': 'Value error, Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_reclamado_detalle_entry_1,
                fecha_reclamo_dt=datetime(2019, 4, 5, 12, 57, 32),
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
                'loc': ('fecha_reclamo_dt',),
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
                self.rc_reclamado_detalle_entry_1,
                fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
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


class RcPendienteDetalleEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.rc_pendiente_detalle_entry_1 = RcPendienteDetalleEntry(
            contribuyente_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            tipo_compra='Del Giro',
            fecha_emision_date=date(2019, 4, 1),
            proveedor_rut=Rut('96790240-3'),
            monto_total=2996301,
            proveedor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=SII_OFFICIAL_TZ,
            ),
            monto_exento=0,
            monto_neto=0,
            monto_iva_recuperable=0,
            monto_iva_no_recuperable=0,
            codigo_iva_no_rec=None,
            monto_neto_activo_fijo=0,
            iva_activo_fijo=0,
            iva_uso_comun=0,
            impto_sin_derecho_a_credito=0,
            iva_no_retenido=0,
            nce_o_nde_sobre_factura_de_compra=None,
            otros_impuestos=None,
        )

    def test_validate_proveedor_razon_social_empty(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('proveedor_razon_social',),
                'msg': "Value error, Value must not be empty.",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_pendiente_detalle_entry_1,
                proveedor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors(
            include_context=False,
            include_input=False,
            include_url=False,
        )
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        self.assertEqual(validation_errors, expected_validation_errors)
