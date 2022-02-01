from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Mapping
from unittest import TestCase

from cl_sii.cte.f29 import data_models, parse_datos_obj
from cl_sii.rcv.data_models import PeriodoTributario
from cl_sii.rut import Rut
from .utils import read_test_file_json_dict


class FunctionsTest(TestCase):
    def test_full(self) -> None:
        datos_obj: Mapping[str, Any] = read_test_file_json_dict(
            'test_data/sii-cte/f29/cte--61002000-3--f29-6600000016-datos-obj-fake.json',
        )
        obj = parse_datos_obj.parse_sii_cte_f29_datos_obj(datos_obj=datos_obj)

        self.assertIsInstance(obj, data_models.CteForm29)
        self.assertEqual(obj.contribuyente_rut, Rut('61002000-3'))
        self.assertEqual(obj.periodo_tributario, PeriodoTributario(year=2017, month=7))
        self.assertEqual(obj.folio, 6600000016)

        expected_codes_dict = {
            1: "SERVICIO DE REGISTRO CIVIL E IDENTIFICACION",
            3: Rut('61002000-3'),
            6: "HUERFANOS 1570",
            7: 6600000016,
            8: "SANTIAGO",
            15: PeriodoTributario(year=2017, month=7),
            30: 723122062,
            48: 1409603,
            60: 70,
            89: 0,
            77: 11429763,
            91: 1536269,
            92: 0,
            93: 224400,
            94: 1603589,
            151: 126666,
            315: datetime.date(2017, 8, 28),
            502: 6588397,
            503: 9,
            504: 17037344,
            511: 980816,
            519: 30,
            520: 1481178,
            527: 2,
            528: 512805,
            537: 18018160,
            538: 6588397,
            547: 1536269,
            562: 17296416,
            584: 10,
            595: 1536269,
            761: 1,
            762: 12443,
            795: 157080,
            915: datetime.date(2017, 10, 31),
            922: "013-2015"
        }
        self.assertEqual(obj.as_codes_dict(include_none=False), expected_codes_dict)

        expected_dict = {
            "contribuyente_rut": Rut('61002000-3'),
            "periodo_tributario": PeriodoTributario(year=2017, month=7),
            "folio": 6600000016,
            "apellido_paterno_o_razon_social": "SERVICIO DE REGISTRO CIVIL E IDENTIFICACION",
            "apellido_materno": None,
            "nombres": None,
            "calle_direccion": "HUERFANOS 1570",
            "numero_direccion": None,
            "comuna_direccion": "SANTIAGO",
            "telefono": None,
            "correo_electronico": None,
            "representante_legal_rut": None,
            "extra": {
                30: 723122062,
                48: 1409603,
                77: 11429763,
                89: 0,
                92: 0,
                93: 224400,
                151: 126666,
                502: 6588397,
                503: 9,
                504: 17037344,
                511: 980816,
                519: 30,
                520: 1481178,
                527: 2,
                528: 512805,
                537: 18018160,
                538: 6588397,
                547: 1536269,
                562: 17296416,
                584: 10,
                595: 1536269,
                761: 1,
                762: 12443,
                795: 157080
            },
            "total_a_pagar_en_plazo_legal": 1536269,
            "total_a_pagar_con_recargo": 1603589,
            "pct_condonacion": 70,
            "num_res_condonacion": "013-2015",
            "fecha_condonacion": datetime.date(2017, 10, 31),
            "tipo_declaracion": "Primitiva",
            "banco": "Banco del Patito Amarillo",
            "medio_pago": "PEL",
            "fecha_presentacion": datetime.date(2017, 8, 28),
        }
        self.assertEqual(dict(obj), expected_dict)

    def test_full_2(self) -> None:
        datos_obj: Mapping[str, Any] = read_test_file_json_dict(
            'test_data/sii-cte/f29/cte--6286736-1--f29-6700000056-datos-obj-fake.json',
        )
        obj = parse_datos_obj.parse_sii_cte_f29_datos_obj(
            datos_obj=datos_obj,
            campo_deserializer=parse_datos_obj.cte_f29_datos_obj_campo_best_effort_deserializer,
        )

        self.assertIsInstance(obj, data_models.CteForm29)
        self.assertEqual(obj.contribuyente_rut, Rut('6286736-1'))
        self.assertEqual(obj.periodo_tributario, PeriodoTributario(year=2018, month=12))
        self.assertEqual(obj.folio, 6700000056)

        expected_codes_dict = {
            1: "BONVALLET",
            2: "GODOY",
            3: Rut('6286736-1'),
            5: "EDWARD GUILLERMO",
            6: "GRECIA 2001",
            7: 6700000056,
            8: "MELIPILLA",
            9: '0',
            15: PeriodoTributario(year=2018, month=12),
            48: 22633,
            55: "E.BONVALLET@EXAMPLE.COM",
            62: 32875,
            77: 584976,
            91: 503286,
            115: Decimal('0.25'),
            142: 13000000,
            151: 447778,
            315: datetime.date(2019, 1, 22),
            502: 28500,
            503: 1,
            511: 613476,
            519: 37,
            520: 613476,
            521: 2365382,
            537: 613476,
            538: 28500,
            547: 503286,
            562: 518660,
            563: 13150000,
            564: 27,
            584: 11,
            586: 1,
            595: 503286,
            596: 0,
            9906: "22/01/2019",
        }
        self.assertEqual(obj.as_codes_dict(include_none=False), expected_codes_dict)

        expected_dict = {
            "contribuyente_rut": Rut('6286736-1'),
            "periodo_tributario": PeriodoTributario(year=2018, month=12),
            "folio": 6700000056,
            "apellido_paterno_o_razon_social": "BONVALLET",
            "apellido_materno": "GODOY",
            "nombres": "EDWARD GUILLERMO",
            "calle_direccion": "GRECIA 2001",
            "numero_direccion": None,
            "comuna_direccion": "MELIPILLA",
            "telefono": "0",
            "correo_electronico": "E.BONVALLET@EXAMPLE.COM",
            "representante_legal_rut": None,
            "extra": {
                48: 22633,
                62: 32875,
                77: 584976,
                115: Decimal('0.25'),
                142: 13000000,
                151: 447778,
                502: 28500,
                503: 1,
                511: 613476,
                519: 37,
                520: 613476,
                521: 2365382,
                537: 613476,
                538: 28500,
                547: 503286,
                562: 518660,
                563: 13150000,
                564: 27,
                584: 11,
                586: 1,
                595: 503286,
                596: 0,
                9906: "22/01/2019",
            },
            "total_a_pagar_en_plazo_legal": 503286,
            "total_a_pagar_con_recargo": None,
            "pct_condonacion": None,
            "num_res_condonacion": None,
            "fecha_condonacion": None,
            "tipo_declaracion": "Rectificatoria con Giro",
            "banco": "",
            "medio_pago": "",
            "fecha_presentacion": datetime.date(2019, 1, 22),
        }
        self.assertEqual(dict(obj), expected_dict)
