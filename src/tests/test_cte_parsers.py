from __future__ import annotations

from unittest import TestCase

from cl_sii.cte import data_models, parsers
from .utils import read_test_file_str_utf8


class ParsersTest(TestCase):
    def test_parse_taxpayer_provided_info(self) -> None:
        html_content = read_test_file_str_utf8('test_data/sii-cte/cte_taxpayer_provided_info.html')

        with self.subTest("Parsing ok"):
            result = parsers.parse_taxpayer_provided_info(html_content)
            expected_obj = data_models.TaxpayerProvidedInfo(
                legal_representatives=[
                    data_models.LegalRepresentative(
                        name='DAVID USUARIO DE PRUEBA',
                        rut='76354771-K',
                        incorporation_date='20-09-2023',
                    ),
                    data_models.LegalRepresentative(
                        name='JAVIERA USUARIO DE PRUEBA',
                        rut='38855667-6',
                        incorporation_date='20-09-2023',
                    ),
                ],
                company_formation=[
                    data_models.LegalRepresentative(
                        name='JAVIERA USUARIO DE PRUEBA',
                        rut='38855667-6',
                        incorporation_date='20-09-2023',
                    ),
                    data_models.LegalRepresentative(
                        name='MARÍA USUARIO DE PRUEBA',
                        rut='34413183-k',
                        incorporation_date='23-02-2024',
                    ),
                ],
                participation_in_existing_companies=[],
            )
            self.assertEqual(result, expected_obj)

        with self.subTest("Parsing emtpy content"):
            with self.assertRaises(ValueError) as assert_raises_cm:
                parsers.parse_taxpayer_provided_info("")

            self.assertEqual(
                assert_raises_cm.exception.args,
                ("Could not find taxpayer information table in HTML",),
            )
