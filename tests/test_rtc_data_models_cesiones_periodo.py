from __future__ import annotations

import unittest
from datetime import date, datetime

import cl_sii.dte.data_models
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte.constants import TipoDte
from cl_sii.libs import tz_utils
from cl_sii.libs.tz_utils import convert_naive_dt_to_tz_aware
from cl_sii.rtc.data_models import CesionL2
from cl_sii.rtc.data_models_cesiones_periodo import CesionesPeriodoEntry
from cl_sii.rut import Rut


class CesionesPeriodoEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.valid_kwargs = dict(
            dte_vendedor_rut=Rut('51532520-4'),
            dte_deudor_rut=Rut('75320502-0'),
            dte_tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            dte_folio=3608460,
            dte_fecha_emision=date(2019, 2, 11),
            dte_monto_total=256357,
            cedente_rut=Rut('51532520-4'),
            cedente_razon_social='MI CAMPITO SA',
            cedente_email='mi@campito.cl',
            cesionario_rut=Rut('96667560-8'),
            cesionario_razon_social='POBRES SERVICIOS FINANCIEROS S.A.',
            cesionario_emails='un-poco@pobres.cl,super.ejecutivo@pobres.cl',
            deudor_email=None,
            fecha_cesion_dt=convert_naive_dt_to_tz_aware(
                datetime(2019, 3, 7, 13, 32), tz=SII_OFFICIAL_TZ),
            fecha_cesion=date(2019, 3, 7),
            monto_cedido=256357,
            fecha_ultimo_vencimiento=date(2019, 4, 12),
            estado='Cesion Vigente',
        )

    def test_init_ok_1(self) -> None:
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        self.assertTrue(obj.monto_cedido_eq_dte_monto_total)

    def test_init_ok_2(self) -> None:
        self.valid_kwargs.update(dict(
            monto_cedido=self.valid_kwargs['dte_monto_total'] - 1,
        ))
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        self.assertFalse(obj.monto_cedido_eq_dte_monto_total)

    def test_init_error_monto_cedido_1(self) -> None:
        self.valid_kwargs.update(dict(
            monto_cedido=-1,
        ))
        with self.assertRaises(ValueError) as cm:
            CesionesPeriodoEntry(**self.valid_kwargs)
        self.assertEqual(
            cm.exception.args,
            ("Amount 'monto_cedido' must be >= 0.", -1))

    def test_init_error_monto_cedido_2(self) -> None:
        self.valid_kwargs.update(dict(
            monto_cedido=self.valid_kwargs['dte_monto_total'] + 1,
        ))
        with self.assertRaises(ValueError) as cm:
            CesionesPeriodoEntry(**self.valid_kwargs)
        self.assertEqual(
            cm.exception.args,
            ('Value of "cesión" must be <= value of DTE.', 256358, 256357))

    def test_init_error_dte_tipo_dte_1(self) -> None:
        self.valid_kwargs.update(dict(
            dte_tipo_dte=TipoDte.NOTA_CREDITO_ELECTRONICA,
        ))
        with self.assertRaises(ValueError) as cm:
            CesionesPeriodoEntry(**self.valid_kwargs)
        self.assertEqual(
            cm.exception.args,
            ("The \"tipo DTE\" in 'dte_tipo_dte' is not \"cedible\".",
             TipoDte.NOTA_CREDITO_ELECTRONICA))

    def test_as_dte_data_l1_ok_1(self) -> None:
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        dte_obj = cl_sii.dte.data_models.DteDataL1(
            emisor_rut=Rut('51532520-4'),
            tipo_dte=TipoDte.FACTURA_ELECTRONICA,
            folio=3608460,
            receptor_rut=Rut('75320502-0'),
            fecha_emision_date=date(2019, 2, 11),
            monto_total=256357,
        )

        self.assertEqual(obj.as_dte_data_l1(), dte_obj)
        self.assertEqual(dte_obj.emisor_rut, obj.dte_vendedor_rut)
        self.assertEqual(dte_obj.vendedor_rut, obj.dte_vendedor_rut)
        self.assertEqual(dte_obj.receptor_rut, obj.dte_deudor_rut)
        self.assertEqual(dte_obj.comprador_rut, obj.dte_deudor_rut)

    def test_as_dte_data_l1_ok_2(self) -> None:
        self.valid_kwargs.update(dict(
            dte_tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
        ))
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        dte_obj = cl_sii.dte.data_models.DteDataL1(
            emisor_rut=Rut('75320502-0'),
            tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
            folio=3608460,
            receptor_rut=Rut('51532520-4'),
            fecha_emision_date=date(2019, 2, 11),
            monto_total=256357,
        )

        self.assertEqual(obj.as_dte_data_l1(), dte_obj)
        self.assertEqual(dte_obj.receptor_rut, obj.dte_vendedor_rut)
        self.assertEqual(dte_obj.vendedor_rut, obj.dte_vendedor_rut)
        self.assertEqual(dte_obj.emisor_rut, obj.dte_deudor_rut)
        self.assertEqual(dte_obj.comprador_rut, obj.dte_deudor_rut)

    def test_as_cesion_l2_ok_1(self) -> None:
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        expected_output = CesionL2(
            dte_key=cl_sii.dte.data_models.DteNaturalKey(
                emisor_rut=Rut('51532520-4'),
                tipo_dte=TipoDte.FACTURA_ELECTRONICA,
                folio=3608460,
            ),
            seq=None,
            cedente_rut=Rut('51532520-4'),
            cesionario_rut=Rut('96667560-8'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 3, 7, 13, 32),
                tz=CesionL2.DATETIME_FIELDS_TZ,
            ),
            monto_cedido=256357,
            dte_receptor_rut=Rut('75320502-0'),
            dte_fecha_emision=date(2019, 2, 11),
            dte_monto_total=256357,
            fecha_ultimo_vencimiento=date(2019, 4, 12),
            cedente_razon_social='MI CAMPITO SA',
            cedente_email='mi@campito.cl',
            cesionario_razon_social='POBRES SERVICIOS FINANCIEROS S.A.',
            cesionario_email='un-poco@pobres.cl,super.ejecutivo@pobres.cl',
        )
        obj_cesion_l2 = obj.as_cesion_l2()
        self.assertEqual(obj_cesion_l2, expected_output)

        self.assertIsNone(obj_cesion_l2.natural_key)
        self.assertEqual(obj_cesion_l2.alt_natural_key.dte_key.emisor_rut, obj.dte_vendedor_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.cedente_rut, obj.cedente_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.cesionario_rut, obj.cesionario_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.fecha_cesion_dt, obj.fecha_cesion_dt)

        self.assertEqual(obj_cesion_l2.dte_receptor_rut, obj.dte_deudor_rut)

    def test_as_cesion_l2_ok_2(self) -> None:
        self.valid_kwargs.update(dict(
            dte_tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
        ))
        obj = CesionesPeriodoEntry(**self.valid_kwargs)
        expected_output = CesionL2(
            dte_key=cl_sii.dte.data_models.DteNaturalKey(
                emisor_rut=Rut('75320502-0'),
                tipo_dte=TipoDte.FACTURA_COMPRA_ELECTRONICA,
                folio=3608460,
            ),
            seq=None,
            cedente_rut=Rut('51532520-4'),
            cesionario_rut=Rut('96667560-8'),
            fecha_cesion_dt=tz_utils.convert_naive_dt_to_tz_aware(
                dt=datetime(2019, 3, 7, 13, 32),
                tz=CesionL2.DATETIME_FIELDS_TZ,
            ),
            monto_cedido=256357,
            dte_receptor_rut=Rut('51532520-4'),
            dte_fecha_emision=date(2019, 2, 11),
            dte_monto_total=256357,
            fecha_ultimo_vencimiento=date(2019, 4, 12),
            cedente_razon_social='MI CAMPITO SA',
            cedente_email='mi@campito.cl',
            cesionario_razon_social='POBRES SERVICIOS FINANCIEROS S.A.',
            cesionario_email='un-poco@pobres.cl,super.ejecutivo@pobres.cl',
        )
        obj_cesion_l2 = obj.as_cesion_l2()
        self.assertEqual(obj_cesion_l2, expected_output)

        self.assertIsNone(obj_cesion_l2.natural_key)
        self.assertEqual(obj_cesion_l2.alt_natural_key.dte_key.emisor_rut, obj.dte_deudor_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.cedente_rut, obj.cedente_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.cesionario_rut, obj.cesionario_rut)
        self.assertEqual(obj_cesion_l2.alt_natural_key.fecha_cesion_dt, obj.fecha_cesion_dt)

        self.assertEqual(obj_cesion_l2.dte_receptor_rut, obj.dte_vendedor_rut)
