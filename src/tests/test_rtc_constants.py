from __future__ import annotations

import unittest
from typing import ClassVar

from cl_sii.dte.constants import TipoDte
from cl_sii.rtc import constants


class TipoDteCediblesTest(unittest.TestCase):
    """
    Tests for `TIPO_DTE_CEDIBLES`.
    """

    TIPO_DTE_CEDIBLES: ClassVar[frozenset[TipoDte]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TIPO_DTE_CEDIBLES = constants.TIPO_DTE_CEDIBLES

    def test_all_are_factura(self) -> None:
        for element in self.TIPO_DTE_CEDIBLES:
            with self.subTest(name=element.name):
                self.assertTrue(element.is_factura)

    # TODO: implement test that check that the values correspond to those defined in
    #   XML type 'SiiDte:DTEFacturasType' in official schema 'SiiTypes_v10.xsd'.
