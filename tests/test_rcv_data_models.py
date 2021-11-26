import dataclasses
import unittest
from datetime import date, datetime

import pydantic

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rcv.constants import RcvTipoDocto
from cl_sii.rcv.data_models import (
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RvDetalleEntry
)
from cl_sii.rut import Rut


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
