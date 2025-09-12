from __future__ import annotations

from datetime import date
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

    def test_parse_taxpayer_data(self) -> None:
        html_content = read_test_file_str_utf8('test_data/sii-cte/cte_empty_f29.html')
        with self.subTest("Parsing ok"):
            result = parsers.parse_taxpayer_data(html_content)
            expected_obj = data_models.TaxpayerData(
                start_of_activities_date=date(2023, 11, 15),
                economic_activities=(
                    "SERVICIOS DE ASESORIA Y CONSULTORIA EN MATERIA DE ADMINISTRACION DE EMPRESAS "
                    "Y OTROS SERVICIOS DE ASESORIA ADMINISTRATIVA Y DE NEGOCIOS N.C.P.\n"
                    "ACTIVIDADES DE OTRAS ORGANIZACIONES EMPRESARIALES N.C.P.\n"
                    "OTRAS ACTIVIDADES DE SERVICIOS PERSONALES N.C.P."
                ),
                tax_category="Primera categoría",
                address="AV REAL, LAS CONDES",
                branches=[],
                last_filed_documents=[
                    data_models.LastFiledDocument(
                        name="FACTURA ELECTRONICA", date=date(2025, 7, 24)
                    ),
                    data_models.LastFiledDocument(
                        name="FACTURA NO AFECTA O EXENTA ELECTRONICA", date=date(2025, 7, 17)
                    ),
                    data_models.LastFiledDocument(
                        name="GUIA DESPACHO ELECTRONICA", date=date(2025, 5, 14)
                    ),
                    data_models.LastFiledDocument(
                        name="NOTA CREDITO ELECTRONICA", date=date(2025, 7, 18)
                    ),
                ],
                tax_observations="No tiene observaciones.",
            )
            self.assertEqual(result, expected_obj)

        with self.subTest("Parsing empty content"):
            with self.assertRaises(ValueError) as assert_raises_cm:
                parsers.parse_taxpayer_data("")
            self.assertEqual(
                assert_raises_cm.exception.args,
                ("Could not find 'Datos del Contribuyente' table in HTML",),
            )

        with self.subTest("Parsing content with empty table"):
            html_content = read_test_file_str_utf8('test_data/sii-cte/cte_empty_table.html')
            result = parsers.parse_taxpayer_data(html_content)
            expected_obj = data_models.TaxpayerData(
                start_of_activities_date=None,
                economic_activities="",
                tax_category="",
                address="",
                branches=[],
                last_filed_documents=[],
                tax_observations=None,
            )
            self.assertEqual(result, expected_obj)
