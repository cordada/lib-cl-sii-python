from __future__ import annotations

import dataclasses
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pydantic

from cl_sii.dte.data_models import DteNaturalKey, DteDataL1, DteDataL2
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.libs import tz_utils
from cl_sii.rtc.data_models import (
    CesionNaturalKey,
    CesionAltNaturalKey,
    CesionL0,
    CesionL1,
    CesionL2,
)
from cl_sii.rut import Rut


class CesionNaturalKeyTest(unittest.TestCase):
    """
    Tests for :class:`CesionNaturalKey`.
    """

    def _set_obj_1(self) -> None:
        obj_dte_natural_key = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

        obj = CesionNaturalKey(
            dte_key=obj_dte_natural_key,
            seq=32,
        )
        self.assertIsInstance(obj, CesionNaturalKey)

        self.obj_1 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            CesionNaturalKey()

    def test_str_and_repr(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = (
            "CesionNaturalKey("
            "dte_key=DteNaturalKey("
            "emisor_rut=Rut('76354771-K'),"
            " tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
            " folio=170"
            "),"
            " seq=32"
            ")"
        )
        self.assertEqual(str(obj), expected_output)
        self.assertEqual(repr(obj), expected_output)

    def test_as_dict(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = dict(
            dte_key=dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
        )
        self.assertEqual(obj.as_dict(), expected_output)

    def test_slug(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = '76354771-K--33--170--32'
        self.assertEqual(obj.slug, expected_output)

    def test_validate_dte_tipo_dte(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_error = {
            'loc': ('dte_key',),
            'msg': """('Value is not "cedible".', <TipoDteEnum.NOTA_CREDITO_ELECTRONICA: 61>)""",
            'type': 'value_error',
        }

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                dte_key=dataclasses.replace(
                    obj.dte_key,
                    tipo_dte=TipoDteEnum.NOTA_CREDITO_ELECTRONICA,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertIn(expected_validation_error, validation_errors)

    def test_validate_seq(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        test_values = [-1, 0, 41, 1000]

        for test_value in test_values:
            expected_validation_error = {
                'loc': ('seq',),
                'msg': f"""('Value is out of the valid range.', {test_value})""",
                'type': 'value_error',
            }

            with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
                dataclasses.replace(
                    obj,
                    seq=test_value,
                )

            validation_errors = assert_raises_cm.exception.errors()
            self.assertIn(expected_validation_error, validation_errors)


class CesionAltNaturalKeyTest(unittest.TestCase):
    """
    Tests for :class:`CesionAltNaturalKey`.
    """

    def _set_obj_1(self) -> None:
        obj_dte_natural_key = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

        obj = CesionAltNaturalKey(
            dte_key=obj_dte_natural_key,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57),
                tz=CesionAltNaturalKey.DATETIME_FIELDS_TZ,
            ),
        )
        self.assertIsInstance(obj, CesionAltNaturalKey)

        self.obj_1_dte_natural_key = obj_dte_natural_key
        self.obj_1 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            CesionAltNaturalKey()

    def test_str_and_repr(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = (
            "CesionAltNaturalKey("
            "dte_key=DteNaturalKey("
            "emisor_rut=Rut('76354771-K'),"
            " tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
            " folio=170"
            "),"
            " cedente_rut=Rut('76389992-6'),"
            " cesionario_rut=Rut('76598556-0'),"
            " fecha_cesion_dt=datetime.datetime("
            "2019, 4, 5, 12, 57,"
            " tzinfo=<DstTzInfo 'America/Santiago' -03-1 day, 21:00:00 DST>"
            ")"
            ")"
        )
        self.assertEqual(str(obj), expected_output)
        self.assertEqual(repr(obj), expected_output)

    def test_as_dict(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = dict(
            dte_key=dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=datetime.fromisoformat('2019-04-05T15:57+00:00'),
        )
        self.assertEqual(obj.as_dict(), expected_output)

    def test_slug(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = '76354771-K--33--170--76389992-6--76598556-0--2019-04-05T12:57-03:00'
        self.assertEqual(obj.slug, expected_output)

    def test_validate_dte_tipo_dte(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_error = {
            'loc': ('dte_key',),
            'msg': """('Value is not "cedible".', <TipoDteEnum.NOTA_CREDITO_ELECTRONICA: 61>)""",
            'type': 'value_error',
        }

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                dte_key=dataclasses.replace(
                    obj.dte_key,
                    tipo_dte=TipoDteEnum.NOTA_CREDITO_ELECTRONICA,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertIn(expected_validation_error, validation_errors)

    def test_validate_fecha_cesion_dt(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        # Test TZ-awareness:

        expected_validation_error = {
            'loc': ('fecha_cesion_dt',),
            'msg': 'Value must be a timezone-aware datetime object.',
            'type': 'value_error',
        }

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_cesion_dt=datetime(2019, 4, 5, 12, 57),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_error = {
            'loc': ('fecha_cesion_dt',),
            'msg':
                '('
                '''"Timezone of datetime value must be 'America/Santiago'.",'''
                ' datetime.datetime(2019, 4, 5, 12, 57, tzinfo=<UTC>)'
                ')',
            'type': 'value_error',
        }

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertIn(expected_validation_error, validation_errors)

        # Test value constraints:

        today_tz_aware = tz_utils.get_now_tz_aware().astimezone(
            CesionAltNaturalKey.DATETIME_FIELDS_TZ
        ).replace(microsecond=0)

        tomorrow_tz_aware = today_tz_aware + timedelta(days=1)

        expected_validation_error = {
            'loc': ('fecha_cesion_dt',),
            'msg':
                '('
                '''\'Value of "fecha_cesion_dt" must be before or equal to the current day.\','''
                f' {repr(tomorrow_tz_aware)},'
                f' {repr(today_tz_aware)}'
                ')',
            'type': 'value_error',
        }

        with patch('cl_sii.libs.tz_utils.get_now_tz_aware') as mock_get_now_tz_aware:
            with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
                mock_get_now_tz_aware.return_value = today_tz_aware
                dataclasses.replace(
                    obj,
                    fecha_cesion_dt=tomorrow_tz_aware,
                )
                mock_get_now_tz_aware.get_now_tz_aware.assert_called_once()

        validation_errors = assert_raises_cm.exception.errors()
        self.assertIn(expected_validation_error, validation_errors)

    def test_truncate_fecha_cesion_dt_to_minutes(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_fecha_cesion_dt = datetime.fromisoformat('2020-12-31T22:33-03:00')
        self.assertEqual(expected_fecha_cesion_dt.second, 0)
        self.assertEqual(expected_fecha_cesion_dt.microsecond, 0)

        obj_with_microseconds = dataclasses.replace(
            obj,
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2020, 12, 31, 22, 33, 44, 555555),
                tz=CesionAltNaturalKey.DATETIME_FIELDS_TZ,
            ),
        )
        obj_with_datetime_truncated = dataclasses.replace(
            obj,
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2020, 12, 31, 22, 33),
                tz=CesionAltNaturalKey.DATETIME_FIELDS_TZ,
            ),
        )
        self.assertEqual(obj_with_microseconds.fecha_cesion_dt, expected_fecha_cesion_dt)
        self.assertEqual(obj_with_datetime_truncated.fecha_cesion_dt, expected_fecha_cesion_dt)
        self.assertEqual(obj_with_microseconds, obj_with_datetime_truncated)


class CesionL0Test(unittest.TestCase):
    """
    Tests for :class:`CesionL0`.
    """

    def _set_obj_1(self) -> None:
        obj_dte_natural_key = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

        obj = CesionL0(
            dte_key=obj_dte_natural_key,
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL0.DATETIME_FIELDS_TZ,
            ),
        )
        self.assertIsInstance(obj, CesionL0)

        self.obj_1_dte_natural_key = obj_dte_natural_key
        self.obj_1 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            CesionL0()

    def test_str_and_repr(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = (
            "CesionL0("
            "dte_key=DteNaturalKey("
            "emisor_rut=Rut('76354771-K'),"
            " tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
            " folio=170"
            "),"
            " seq=32,"
            " cedente_rut=Rut('76389992-6'),"
            " cesionario_rut=Rut('76598556-0'),"
            " fecha_cesion_dt=datetime.datetime("
            "2019, 4, 5, 12, 57, 32,"
            " tzinfo=<DstTzInfo 'America/Santiago' -03-1 day, 21:00:00 DST>"
            ")"
            ")"
        )
        self.assertEqual(str(obj), expected_output)
        self.assertEqual(repr(obj), expected_output)

    def test_as_dict(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = dict(
            dte_key=dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=datetime.fromisoformat('2019-04-05T12:57:32-03:00'),
        )
        self.assertEqual(obj.as_dict(), expected_output)

    def test_slug(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = '76354771-K--33--170--76389992-6--76598556-0--2019-04-05T12:57-03:00'
        self.assertEqual(obj.slug, expected_output)

    def test_natural_key(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = CesionNaturalKey(
            dte_key=DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
        )
        self.assertEqual(obj.natural_key, expected_output)

        obj_without_seq = dataclasses.replace(
            obj,
            seq=None,
        )
        self.assertIsNone(obj_without_seq.natural_key)

    def test_alt_natural_key(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = CesionAltNaturalKey(
            dte_key=DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57),
                tz=CesionL0.DATETIME_FIELDS_TZ,
            ),
        )
        self.assertEqual(obj.alt_natural_key, expected_output)

        obj_without_seq = dataclasses.replace(
            obj,
            seq=None,
        )
        self.assertEqual(obj_without_seq.alt_natural_key, expected_output)

    def test_validate_dte_tipo_dte(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_errors = [
            {
                'loc': ('dte_key',),
                'msg':
                    """('Value is not "cedible".', <TipoDteEnum.NOTA_CREDITO_ELECTRONICA: 61>)""",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                dte_key=dataclasses.replace(
                    obj.dte_key,
                    tipo_dte=TipoDteEnum.NOTA_CREDITO_ELECTRONICA,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_seq(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        test_values = [-1, 0, 41, 1000]

        for test_value in test_values:
            expected_validation_errors = [
                {
                    'loc': ('seq',),
                    'msg': f"""('Value is out of the valid range.', {test_value})""",
                    'type': 'value_error',
                },
            ]

            with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
                dataclasses.replace(
                    obj,
                    seq=test_value,
                )

            validation_errors = assert_raises_cm.exception.errors()
            self.assertEqual(len(validation_errors), len(expected_validation_errors))
            for expected_validation_error in expected_validation_errors:
                self.assertIn(expected_validation_error, validation_errors)

    def test_validate_datetime_tz(self) -> None:
        self._set_obj_1()

        obj = self.obj_1

        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_cesion_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_cesion_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_cesion_dt',),
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
                obj,
                fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class CesionL1Test(CesionL0Test):
    """
    Tests for :class:`CesionL1`.
    """

    def _set_obj_1(self) -> None:
        obj_dte_natural_key = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

        obj = CesionL1(
            dte_key=obj_dte_natural_key,
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL1.DATETIME_FIELDS_TZ,
            ),
            monto_cedido=2996301,
            fecha_ultimo_vencimiento=date(2019, 5, 1),
            dte_fecha_emision=date(2019, 4, 1),
            dte_receptor_rut=Rut('96790240-3'),
            dte_monto_total=2996301,
        )
        self.assertIsInstance(obj, CesionL1)

        self.obj_1_dte_natural_key = obj_dte_natural_key
        self.obj_1 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            CesionL1()

    def test_str_and_repr(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = (
            "CesionL1("
            "dte_key=DteNaturalKey("
            "emisor_rut=Rut('76354771-K'),"
            " tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
            " folio=170"
            "),"
            " seq=32,"
            " cedente_rut=Rut('76389992-6'),"
            " cesionario_rut=Rut('76598556-0'),"
            " fecha_cesion_dt=datetime.datetime("
            "2019, 4, 5, 12, 57, 32,"
            " tzinfo=<DstTzInfo 'America/Santiago' -03-1 day, 21:00:00 DST>"
            "),"
            " monto_cedido=2996301,"
            " fecha_ultimo_vencimiento=datetime.date(2019, 5, 1),"
            " dte_fecha_emision=datetime.date(2019, 4, 1),"
            " dte_receptor_rut=Rut('96790240-3'),"
            " dte_monto_total=2996301"
            ")"
        )
        self.assertEqual(str(obj), expected_output)
        self.assertEqual(repr(obj), expected_output)

    def test_as_dict(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = dict(
            dte_key=dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=datetime.fromisoformat('2019-04-05T12:57:32-03:00'),
            monto_cedido=2996301,
            fecha_ultimo_vencimiento=date(2019, 5, 1),
            dte_fecha_emision=date(2019, 4, 1),
            dte_receptor_rut=Rut('96790240-3'),
            dte_monto_total=2996301,
        )
        self.assertEqual(obj.as_dict(), expected_output)

    def test_as_cesion_l0(self):
        self._set_obj_1()

        obj = self.obj_1
        expected_output = CesionL0(
            dte_key=DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL0.DATETIME_FIELDS_TZ,
            ),
        )
        self.assertEqual(obj.as_cesion_l0(), expected_output)

    def test_as_dte_data_l1(self):
        self._set_obj_1()

        obj = self.obj_1
        expected_output = DteDataL1(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
        )
        self.assertEqual(obj.as_dte_data_l1(), expected_output)

    def test_validate_monto_cedido(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        test_values = [-1, 10 ** 18 + 1]

        for test_value in test_values:
            expected_validation_errors = [
                {
                    'loc': ('monto_cedido',),
                    'msg': f"""('Value is out of the valid range.', {test_value})""",
                    'type': 'value_error',
                },
            ]

            with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
                dataclasses.replace(
                    obj,
                    monto_cedido=test_value,
                )

            validation_errors = assert_raises_cm.exception.errors()
            self.assertEqual(len(validation_errors), len(expected_validation_errors))
            for expected_validation_error in expected_validation_errors:
                self.assertIn(expected_validation_error, validation_errors)

    def test_validate_monto_cedido_does_not_exceed_dte_monto_total(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_errors = [
            {
                'loc': ('__root__',),
                'msg':
                    """('Value of "cesión" must be <= value of DTE.', 1000, 999)""",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                monto_cedido=1000,
                dte_monto_total=999,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_fecha_ultimo_vencimiento_is_not_before_dte_fecha_emision(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_errors = [
            {
                'loc': ('__root__',),
                'msg':
                    """('Value of "cesión" must be >= value of DTE.',"""
                    " datetime.date(2019, 5, 1), datetime.date(2019, 5, 2))",
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_ultimo_vencimiento=date(2019, 5, 1),
                dte_fecha_emision=date(2019, 5, 2),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)


class CesionL2Test(CesionL1Test):
    """
    Tests for :class:`CesionL2`.
    """

    def _set_obj_1(self) -> None:
        obj_dte_natural_key = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

        obj = CesionL2(
            dte_key=obj_dte_natural_key,
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL2.DATETIME_FIELDS_TZ,
            ),
            monto_cedido=2996301,
            fecha_ultimo_vencimiento=date(2019, 5, 1),
            dte_fecha_emision=date(2019, 4, 1),
            dte_receptor_rut=Rut('96790240-3'),
            dte_monto_total=2996301,
            fecha_firma_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL2.DATETIME_FIELDS_TZ,
            ),
            cedente_razon_social='ST CAPITAL S.A.',
            cesionario_razon_social='Fondo de Inversión Privado Deuda y Facturas',
            cedente_email='APrat@Financiaenlinea.com',
            cesionario_email='solicitudes@stcapital.cl',
            dte_emisor_razon_social='INGENIERIA ENACON SPA',
            dte_receptor_razon_social='MINERA LOS PELAMBRES',
            dte_deudor_email=None,
            cedente_declaracion_jurada=(
                'Se declara bajo juramento que ST CAPITAL S.A., RUT 76389992-6 ha puesto '
                'a disposicion del cesionario Fondo de Inversión Privado Deuda y Facturas, '
                'RUT 76598556-0, el documento validamente emitido al deudor MINERA LOS '
                'PELAMBRES, RUT 96790240-3.'
            ),
            dte_fecha_vencimiento=None,
            contacto_nombre='ST Capital Servicios Financieros',
            contacto_telefono=None,
            contacto_email='APrat@Financiaenlinea.com',
        )
        self.assertIsInstance(obj, CesionL2)

        self.obj_1_dte_natural_key = obj_dte_natural_key
        self.obj_1 = obj

    def test_create_new_empty_instance(self) -> None:
        with self.assertRaises(TypeError):
            CesionL2()

    def test_str_and_repr(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = (
            "CesionL2("
            "dte_key=DteNaturalKey("
            "emisor_rut=Rut('76354771-K'),"
            " tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>,"
            " folio=170"
            "),"
            " seq=32,"
            " cedente_rut=Rut('76389992-6'),"
            " cesionario_rut=Rut('76598556-0'),"
            " fecha_cesion_dt=datetime.datetime("
            "2019, 4, 5, 12, 57, 32,"
            " tzinfo=<DstTzInfo 'America/Santiago' -03-1 day, 21:00:00 DST>"
            "),"
            " monto_cedido=2996301,"
            " fecha_ultimo_vencimiento=datetime.date(2019, 5, 1),"
            " dte_fecha_emision=datetime.date(2019, 4, 1),"
            " dte_receptor_rut=Rut('96790240-3'),"
            " dte_monto_total=2996301,"
            " fecha_firma_dt=datetime.datetime("
            "2019, 4, 5, 12, 57, 32,"
            " tzinfo=<DstTzInfo 'America/Santiago' -03-1 day, 21:00:00 DST>"
            "),"
            " dte_fecha_vencimiento=None,"
            " contacto_nombre='ST Capital Servicios Financieros'"
            ")"
        )
        self.assertEqual(str(obj), expected_output)
        self.assertEqual(repr(obj), expected_output)

    def test_as_dict(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_output = dict(
            dte_key=dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=datetime.fromisoformat('2019-04-05T12:57:32-03:00'),
            monto_cedido=2996301,
            fecha_ultimo_vencimiento=date(2019, 5, 1),
            dte_fecha_emision=date(2019, 4, 1),
            dte_receptor_rut=Rut('96790240-3'),
            dte_monto_total=2996301,
            fecha_firma_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL2.DATETIME_FIELDS_TZ,
            ),
            cedente_razon_social='ST CAPITAL S.A.',
            cesionario_razon_social='Fondo de Inversión Privado Deuda y Facturas',
            cedente_email='APrat@Financiaenlinea.com',
            cesionario_email='solicitudes@stcapital.cl',
            dte_emisor_razon_social='INGENIERIA ENACON SPA',
            dte_receptor_razon_social='MINERA LOS PELAMBRES',
            dte_deudor_email=None,
            cedente_declaracion_jurada=(
                'Se declara bajo juramento que ST CAPITAL S.A., RUT 76389992-6 ha puesto '
                'a disposicion del cesionario Fondo de Inversión Privado Deuda y Facturas, '
                'RUT 76598556-0, el documento validamente emitido al deudor MINERA LOS '
                'PELAMBRES, RUT 96790240-3.'
            ),
            dte_fecha_vencimiento=None,
            contacto_nombre='ST Capital Servicios Financieros',
            contacto_telefono=None,
            contacto_email='APrat@Financiaenlinea.com',
        )
        self.assertEqual(obj.as_dict(), expected_output)

    def test_as_cesion_l1(self):
        self._set_obj_1()

        obj = self.obj_1
        expected_output = CesionL1(
            dte_key=DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ),
            seq=32,
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 4, 5, 12, 57, 32),
                tz=CesionL1.DATETIME_FIELDS_TZ,
            ),
            monto_cedido=2996301,
            fecha_ultimo_vencimiento=date(2019, 5, 1),
            dte_fecha_emision=date(2019, 4, 1),
            dte_receptor_rut=Rut('96790240-3'),
            dte_monto_total=2996301,
        )
        self.assertEqual(obj.as_cesion_l1(), expected_output)

    def test_as_dte_data_l2(self):
        self._set_obj_1()

        obj = self.obj_1
        expected_output = DteDataL2(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
        )
        self.assertEqual(obj.as_dte_data_l2(), expected_output)

    def test_validate_datetime_tz(self) -> None:
        super().test_validate_datetime_tz()

        obj = self.obj_1

        # Test TZ-awareness:

        expected_validation_errors = [
            {
                'loc': ('fecha_cesion_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
            {
                'loc': ('fecha_firma_dt',),
                'msg': 'Value must be a timezone-aware datetime object.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                fecha_cesion_dt=datetime(2019, 4, 5, 12, 57, 32),
                fecha_firma_dt=datetime(2019, 4, 5, 12, 57, 32),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

        # Test TZ-value:

        expected_validation_errors = [
            {
                'loc': ('fecha_cesion_dt',),
                'msg':
                    '('
                    '''"Timezone of datetime value must be 'America/Santiago'.",'''
                    ' datetime.datetime(2019, 4, 5, 12, 57, 32, tzinfo=<UTC>)'
                    ')',
                'type': 'value_error',
            },
            {
                'loc': ('fecha_firma_dt',),
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
                obj,
                fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
                fecha_firma_dt=tz_utils.convert_naive_dt_to_tz_aware(
                    dt=datetime(2019, 4, 5, 12, 57, 32),
                    tz=tz_utils.TZ_UTC,
                ),
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)

    def test_validate_contribuyente_razon_social(self) -> None:
        self._set_obj_1()

        obj = self.obj_1
        expected_validation_errors = [
            {
                'loc': ('cedente_razon_social',),
                'msg': 'ensure this value has at least 1 characters',
                'type': 'value_error.any_str.min_length',
                'ctx': {'limit_value': 1},
            },
            {
                'loc': ('cesionario_razon_social',),
                'msg': 'Value exceeds max allowed length.',
                'type': 'value_error',
            },
            {
                'loc': ('dte_emisor_razon_social',),
                'msg': 'ensure this value has at least 1 characters',
                'type': 'value_error.any_str.min_length',
                'ctx': {'limit_value': 1},
            },
            {
                'loc': ('dte_receptor_razon_social',),
                'msg': 'Value exceeds max allowed length.',
                'type': 'value_error',
            },
        ]

        with self.assertRaises(pydantic.ValidationError) as assert_raises_cm:
            dataclasses.replace(
                obj,
                cedente_razon_social='',
                cesionario_razon_social='C' * 101,
                dte_emisor_razon_social='',
                dte_receptor_razon_social='R' * 200,
            )

        validation_errors = assert_raises_cm.exception.errors()
        self.assertEqual(len(validation_errors), len(expected_validation_errors))
        for expected_validation_error in expected_validation_errors:
            self.assertIn(expected_validation_error, validation_errors)
