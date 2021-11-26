import dataclasses
import unittest
from datetime import date, datetime

import pydantic

import cl_sii.dte.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rcv.constants import RcvTipoDocto
from cl_sii.rcv.data_models import (
    PeriodoTributario,
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RcvDetalleEntry,
    RvDetalleEntry
)
from cl_sii.rut import Rut


class PeriodoTributarioTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.periodo_tributario_1 = PeriodoTributario(
            year=2019,
            month=4
        )

    def test_validate_year_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('year',),
                'msg': "Value is out of the valid range for 'year'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field year
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                year=1899,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_month_range(self) -> None:
        expected_validation_errors = [
            {
                'loc': ('month',),
                'msg': "Value is out of the valid range for 'month'.",
                'type': 'value_error',
            },
        ]

        # Validate the minimum value of the field month
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                month=0,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Validate the maximum value of the field month
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.periodo_tributario_1,
                month=13,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class RcvDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rcv_detalle_entry_1 = RcvDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcvDetalleEntry.DATETIME_FIELDS_TZ),
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
                self.rcv_detalle_entry_1,
                folio=cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE - 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Validate the maximum value of the field folio
        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rcv_detalle_entry_1,
                folio=cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE + 1,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_recepcion_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rcv_detalle_entry_1,
                fecha_recepcion_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_recepcion_dt',),
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
                self.rcv_detalle_entry_1,
                fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class RvDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rv_detalle_entry_1 = RvDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ),
            fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RvDetalleEntry.DATETIME_FIELDS_TZ),
        )

    def test_constants_match(self):
        self.assertEqual(
            RvDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
        )

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
                self.rv_detalle_entry_1,
                receptor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # fecha_acuse_dt
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_acuse_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rv_detalle_entry_1,
                fecha_acuse_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_acuse_dt',),
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
                self.rv_detalle_entry_1,
                fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # fecha_reclamo_dt
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_reclamo_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rv_detalle_entry_1,
                fecha_reclamo_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_reclamo_dt',),
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
                self.rv_detalle_entry_1,
                fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class RcRegistroDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rc_registro_detalle_entry_1 = RcRegistroDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcRegistroDetalleEntry.DATETIME_FIELDS_TZ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RcRegistroDetalleEntry.DATETIME_FIELDS_TZ),
        )

    def test_constants_match(self):
        self.assertEqual(
            RcRegistroDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
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
                self.rc_registro_detalle_entry_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_acuse_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_registro_detalle_entry_1,
                fecha_acuse_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_acuse_dt',),
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
                self.rc_registro_detalle_entry_1,
                fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class RcNoIncluirDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rc_no_incluir_detalle_entry_1 = RcNoIncluirDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=SII_OFFICIAL_TZ),
            fecha_acuse_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=SII_OFFICIAL_TZ),
        )


class RcReclamadoDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rc_reclamado_detalle_entry_1 = RcReclamadoDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ),
            fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 8, 10, 21, 18),
                tz=RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ),
        )

    def test_constants_match(self):
        self.assertEqual(
            RcReclamadoDetalleEntry.DATETIME_FIELDS_TZ,
            RcvDetalleEntry.DATETIME_FIELDS_TZ,
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
                self.rc_reclamado_detalle_entry_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_reclamo_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                self.rc_reclamado_detalle_entry_1,
                fecha_reclamo_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_reclamo_dt',),
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
                self.rc_reclamado_detalle_entry_1,
                fecha_reclamo_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class RcPendienteDetalleEntryTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.rc_pendiente_detalle_entry_1 = RcPendienteDetalleEntry(
            emisor_rut=Rut('76354771-K'),
            tipo_docto=RcvTipoDocto.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            fecha_recepcion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 1, 1, 36, 40),
                tz=SII_OFFICIAL_TZ),
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
                self.rc_pendiente_detalle_entry_1,
                emisor_razon_social='',
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)
