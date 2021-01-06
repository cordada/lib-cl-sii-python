from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime

import pydantic

from cl_sii.dte.data_models import DteNaturalKey
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.libs import tz_utils
from cl_sii.rtc.data_models import (
    CesionNaturalKey,
    CesionAltNaturalKey,
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

    def test_validate_datetime_tz(self) -> None:
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
