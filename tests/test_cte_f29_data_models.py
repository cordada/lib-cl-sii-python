from __future__ import annotations

from typing import Sequence
from unittest import TestCase

from cl_sii.cte.f29 import data_models
from cl_sii.rcv.data_models import PeriodoTributario
from cl_sii.rut import Rut
from . import cte_f29_factories


class CteForm29Test(TestCase):
    """
    Tests for ``cte.f29.data_models.CteForm29``.
    """

    def test___str__(self) -> None:
        obj = cte_f29_factories.create_CteForm29(
            contribuyente_rut=Rut('1-9'),
            periodo_tributario=PeriodoTributario(year=2018, month=12),
            folio=1234567890,
        )
        expected_output = (
            "CteForm29("
            "contribuyente_rut=Rut('1-9'),"
            " periodo_tributario=PeriodoTributario(year=2018, month=12),"
            " folio=1234567890"
            ")"
        )
        self.assertEqual(str(obj), expected_output)

    def test___repr__(self) -> None:
        obj = cte_f29_factories.create_CteForm29(
            contribuyente_rut=Rut('1-9'),
            periodo_tributario=PeriodoTributario(year=2018, month=12),
            folio=1234567890,
        )
        expected_output = (
            "CteForm29("
            "contribuyente_rut=Rut('1-9'),"
            " periodo_tributario=PeriodoTributario(year=2018, month=12),"
            " folio=1234567890"
            ")"
        )
        self.assertEqual(repr(obj), expected_output)

    def test_code_field_mapping_class_attributes(self) -> None:
        obj = cte_f29_factories.create_CteForm29()
        for code, field_name in obj.CODE_FIELD_MAPPING.items():
            if obj.get_field_name(code) is not None:
                self.assertTrue(
                    hasattr(obj, field_name),
                    msg=(
                        f"Code '{code}' is associated to field '{field_name}',"
                        f" but class '{obj.__class__.__name__}'"
                        f" does not have that attribute."
                    ),
                )

    def test_code_field_mapping_value_uniqueness(self) -> None:
        obj = cte_f29_factories.create_CteForm29()

        code_field_names: Sequence[str] = [
            field_name
            for field_name in obj.CODE_FIELD_MAPPING.values()
            if field_name is not None
        ]
        unique_code_field_names = set(code_field_names)

        self.assertEqual(len(code_field_names), len(unique_code_field_names))

    def test_strict_codes(self) -> None:
        with self.assertRaises(KeyError):
            cte_f29_factories.create_CteForm29(
                _strict_codes=True,
                extra={
                    999888777666: 'whatever',
                },
            )

        with self.assertLogs('cl_sii.cte.f29.data_models', level='WARNING') as assert_logs_cm:
            cte_f29_factories.create_CteForm29(
                _strict_codes=False,
                extra={
                    123456: 42,
                    999888777666: 'whatever',
                },
            )
        self.assertEqual(len(assert_logs_cm.output), 1)
        self.assertIn(
            'invalid or unknown SII Form 29 codes: 123456, 999888777666',
            assert_logs_cm.output[0],
        )

    def test_get_field_name(self) -> None:
        # Test a valid code.
        self.assertEqual(data_models.CteForm29.get_field_name(7), 'folio')

        # Test invalid codes.
        with self.assertRaises(KeyError):
            data_models.CteForm29.get_field_name(999888777666, strict=True)

        self.assertIsNone(data_models.CteForm29.get_field_name(999888777666, strict=False))

        # Test invalid type.
        with self.assertRaises(TypeError):
            data_models.CteForm29.get_field_name('999888777666')  # type: ignore

    def test_natural_key(self) -> None:
        obj = cte_f29_factories.create_CteForm29(
            contribuyente_rut=Rut('1-9'),
            periodo_tributario=PeriodoTributario(year=2018, month=12),
            folio=1234567890,
        )
        expected_output = data_models.CteForm29NaturalKey(
            contribuyente_rut=Rut('1-9'),
            periodo_tributario=PeriodoTributario(year=2018, month=12),
            folio=1234567890,
        )
        self.assertEqual(obj.natural_key, expected_output)

    def test_get_all_codes(self) -> None:
        pass  # TODO: Implement for 'get_all_codes'.

    def test_as_codes_dict(self) -> None:
        pass  # TODO: Implement for 'as_codes_dict'.

    def test___getitem__(self) -> None:
        pass  # TODO: Implement for '__getitem__'.

    def test___iter__(self) -> None:
        pass  # TODO: Implement for '__iter__'.
