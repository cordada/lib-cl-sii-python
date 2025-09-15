from __future__ import annotations

import unittest
from typing import ClassVar

from cl_sii.dte import constants


class TipoDteTest(unittest.TestCase):
    TipoDte: ClassVar[type[constants.TipoDte]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TipoDte = constants.TipoDte

    def test_enum_member_value_types(self) -> None:
        expected_type = int
        for member in self.TipoDte:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_are_also_integers(self) -> None:
        for member in self.TipoDte:
            with self.subTest(name=member.name):
                self.assertEqual(int(member.value), member)
                self.assertIsInstance(member, int)

    def test_FACTURA_ELECTRONICA(self) -> None:
        value = self.TipoDte.FACTURA_ELECTRONICA

        self.assertEqual(value.name, 'FACTURA_ELECTRONICA')
        self.assertEqual(value.value, 33)

        assertions = [
            (value.is_factura, True),
            (value.is_factura_venta, True),
            (value.is_factura_compra, False),
            (value.is_nota, False),
            (value.emisor_is_vendedor, True),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertEqual(result, expected)

    def test_FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA(self) -> None:
        value = self.TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA

        self.assertEqual(value.name, 'FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA')
        self.assertEqual(value.value, 34)

        assertions = [
            (value.is_factura, True),
            (value.is_factura_venta, True),
            (value.is_factura_compra, False),
            (value.is_nota, False),
            (value.emisor_is_vendedor, True),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertTrue(result is expected)

    def test_LIQUIDACION_FACTURA_ELECTRONICA(self) -> None:
        value = self.TipoDte.LIQUIDACION_FACTURA_ELECTRONICA

        self.assertEqual(value.name, 'LIQUIDACION_FACTURA_ELECTRONICA')
        self.assertEqual(value.value, 43)

        assertions = [
            (value.is_factura, True),
            (value.is_factura_venta, True),
            (value.is_factura_compra, False),
            (value.is_nota, False),
            (value.emisor_is_vendedor, True),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertEqual(result, expected)

    def test_FACTURA_COMPRA_ELECTRONICA(self) -> None:
        value = self.TipoDte.FACTURA_COMPRA_ELECTRONICA

        self.assertEqual(value.name, 'FACTURA_COMPRA_ELECTRONICA')
        self.assertEqual(value.value, 46)

        assertions = [
            (value.is_factura, True),
            (value.is_factura_venta, False),
            (value.is_factura_compra, True),
            (value.is_nota, False),
            (value.emisor_is_vendedor, False),
            (value.receptor_is_vendedor, True),
        ]

        for result, expected in assertions:
            self.assertTrue(result is expected)

    def test_GUIA_DESPACHO_ELECTRONICA(self) -> None:
        value = self.TipoDte.GUIA_DESPACHO_ELECTRONICA

        self.assertEqual(value.name, 'GUIA_DESPACHO_ELECTRONICA')
        self.assertEqual(value.value, 52)

        assertions = [
            (value.is_factura, False),
            (value.is_factura_venta, False),
            (value.is_factura_compra, False),
            (value.is_nota, False),
            (value.emisor_is_vendedor, False),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertTrue(result is expected)

    def test_NOTA_DEBITO_ELECTRONICA(self) -> None:
        value = self.TipoDte.NOTA_DEBITO_ELECTRONICA

        self.assertEqual(value.name, 'NOTA_DEBITO_ELECTRONICA')
        self.assertEqual(value.value, 56)

        assertions = [
            (value.is_factura, False),
            (value.is_factura_venta, False),
            (value.is_factura_compra, False),
            (value.is_nota, True),
            (value.emisor_is_vendedor, False),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertTrue(result is expected)

    def test_NOTA_CREDITO_ELECTRONICA(self) -> None:
        value = self.TipoDte.NOTA_CREDITO_ELECTRONICA

        self.assertEqual(value.name, 'NOTA_CREDITO_ELECTRONICA')
        self.assertEqual(value.value, 61)

        assertions = [
            (value.is_factura, False),
            (value.is_factura_venta, False),
            (value.is_factura_compra, False),
            (value.is_nota, True),
            (value.emisor_is_vendedor, False),
            (value.receptor_is_vendedor, False),
        ]

        for result, expected in assertions:
            self.assertTrue(result is expected)
