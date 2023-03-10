import unittest

from cl_sii.rtc.constants import TIPO_DTE_CEDIBLES


class TipoDteCediblesTest(unittest.TestCase):
    # For 'TIPO_DTE_CEDIBLES'

    def test_all_are_factura(self) -> None:
        for element in TIPO_DTE_CEDIBLES:
            self.assertTrue(element.is_factura)

    # TODO: implement test that check that the values correspond to those defined in
    #   XML type 'SiiDte:DTEFacturasType' in official schema 'SiiTypes_v10.xsd'.
