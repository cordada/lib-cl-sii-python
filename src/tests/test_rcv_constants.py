from __future__ import annotations

import unittest
from typing import ClassVar

from cl_sii.dte.constants import TipoDte
from cl_sii.rcv import constants


class RcvKindTest(unittest.TestCase):
    RcvKind: ClassVar[type[constants.RcvKind]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcvKind = constants.RcvKind

    def test_enum_member_value_types(self) -> None:
        expected_type = str
        for member in self.RcvKind:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_equal_names_and_values(self) -> None:
        for member in self.RcvKind:
            with self.subTest(name=member.name):
                self.assertEqual(member.value, member.name)

    def test_is_estado_contable_compatible(self) -> None:
        RcvKind = self.RcvKind
        RcEstadoContable = constants.RcEstadoContable

        self.assertTrue(RcvKind.VENTAS.is_estado_contable_compatible(None))
        self.assertTrue(RcvKind.COMPRAS.is_estado_contable_compatible(RcEstadoContable.REGISTRO))
        self.assertTrue(RcvKind.COMPRAS.is_estado_contable_compatible(RcEstadoContable.NO_INCLUIR))
        self.assertTrue(RcvKind.COMPRAS.is_estado_contable_compatible(RcEstadoContable.RECLAMADO))
        self.assertTrue(RcvKind.COMPRAS.is_estado_contable_compatible(RcEstadoContable.PENDIENTE))

        self.assertFalse(RcvKind.COMPRAS.is_estado_contable_compatible(None))
        self.assertFalse(RcvKind.VENTAS.is_estado_contable_compatible(RcEstadoContable.REGISTRO))
        self.assertFalse(RcvKind.VENTAS.is_estado_contable_compatible(RcEstadoContable.NO_INCLUIR))
        self.assertFalse(RcvKind.VENTAS.is_estado_contable_compatible(RcEstadoContable.RECLAMADO))
        self.assertFalse(RcvKind.VENTAS.is_estado_contable_compatible(RcEstadoContable.PENDIENTE))


class RcEstadoContableTest(unittest.TestCase):
    RcEstadoContable: ClassVar[type[constants.RcEstadoContable]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcEstadoContable = constants.RcEstadoContable

    def test_enum_member_value_types(self) -> None:
        expected_type = str
        for member in self.RcEstadoContable:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_equal_names_and_values(self) -> None:
        for member in self.RcEstadoContable:
            with self.subTest(name=member.name):
                self.assertEqual(member.value, member.name)


class RcTipoCompraTest(unittest.TestCase):
    RcTipoCompra: ClassVar[type[constants.RcTipoCompra]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcTipoCompra = constants.RcTipoCompra

    def test_enum_member_value_types(self) -> None:
        expected_type = str
        for member in self.RcTipoCompra:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_equal_names_and_values(self) -> None:
        for member in self.RcTipoCompra:
            with self.subTest(name=member.name):
                self.assertEqual(member.value, member.name)


class RcvTipoDoctoTest(unittest.TestCase):
    RcvTipoDocto: ClassVar[type[constants.RcvTipoDocto]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RcvTipoDocto = constants.RcvTipoDocto

    def test_enum_member_value_types(self) -> None:
        expected_type = int
        for member in self.RcvTipoDocto:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_are_also_integers(self) -> None:
        for member in self.RcvTipoDocto:
            with self.subTest(name=member.name):
                self.assertEqual(int(member.value), member)
                self.assertIsInstance(member, int)

    def test_of_some_member(self) -> None:
        value = self.RcvTipoDocto.FACTURA_ELECTRONICA

        self.assertEqual(value.name, 'FACTURA_ELECTRONICA')
        self.assertEqual(value.value, 33)

    def test_as_tipo_dte(self) -> None:
        self.assertEqual(
            self.RcvTipoDocto.FACTURA_ELECTRONICA.as_tipo_dte(),
            TipoDte.FACTURA_ELECTRONICA,
        )

        with self.assertRaises(ValueError) as cm:
            self.RcvTipoDocto.FACTURA.as_tipo_dte()
        self.assertEqual(
            cm.exception.args, ("There is no equivalent 'TipoDte' for 'RcvTipoDocto.FACTURA'.",)
        )


class RvTipoVentaTest(unittest.TestCase):
    RvTipoVenta: ClassVar[type[constants.RvTipoVenta]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.RvTipoVenta = constants.RvTipoVenta

    def test_enum_member_value_types(self) -> None:
        expected_type = str
        for member in self.RvTipoVenta:
            with self.subTest(name=member.name):
                self.assertIsInstance(member.value, expected_type)

    def test_enum_members_equal_names_and_values(self) -> None:
        for member in self.RvTipoVenta:
            with self.subTest(name=member.name):
                self.assertEqual(member.value, member.name)
