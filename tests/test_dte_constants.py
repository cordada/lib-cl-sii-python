import unittest

from cl_sii.dte import constants  # noqa: F401
from cl_sii.dte.constants import TipoDte


class TipoDteTest(unittest.TestCase):
    def test_members(self) -> None:
        self.assertSetEqual(
            {x for x in TipoDte},
            {
                TipoDte.FACTURA_ELECTRONICA,
                TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA,
                TipoDte.LIQUIDACION_FACTURA_ELECTRONICA,
                TipoDte.FACTURA_COMPRA_ELECTRONICA,
                TipoDte.GUIA_DESPACHO_ELECTRONICA,
                TipoDte.NOTA_DEBITO_ELECTRONICA,
                TipoDte.NOTA_CREDITO_ELECTRONICA,
            },
        )

    def test_FACTURA_ELECTRONICA(self) -> None:
        value = TipoDte.FACTURA_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertEqual(result, expected)

    def test_FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA(self) -> None:
        value = TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertTrue(result is expected)

    def test_LIQUIDACION_FACTURA_ELECTRONICA(self) -> None:
        value = TipoDte.LIQUIDACION_FACTURA_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertEqual(result, expected)

    def test_FACTURA_COMPRA_ELECTRONICA(self) -> None:
        value = TipoDte.FACTURA_COMPRA_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertTrue(result is expected)

    def test_GUIA_DESPACHO_ELECTRONICA(self) -> None:
        value = TipoDte.GUIA_DESPACHO_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertTrue(result is expected)

    def test_NOTA_DEBITO_ELECTRONICA(self) -> None:
        value = TipoDte.NOTA_DEBITO_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertTrue(result is expected)

    def test_NOTA_CREDITO_ELECTRONICA(self) -> None:
        value = TipoDte.NOTA_CREDITO_ELECTRONICA

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

        for (result, expected) in assertions:
            self.assertTrue(result is expected)
