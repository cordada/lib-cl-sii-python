import unittest
from datetime import date

from cl_sii.rut import Rut  # noqa: F401

from cl_sii.dte.constants import TipoDteEnum  # noqa: F401
from cl_sii.dte.data_models import (  # noqa: F401
    DteDataL0, DteDataL1, DteDataL2, DteNaturalKey,
    validate_contribuyente_razon_social, validate_dte_folio, validate_dte_monto_total,
)


class DteNaturalKeyTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_nk_1 = DteNaturalKey(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteNaturalKey()'
        pass

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_nk_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            )
        )

    def test_slug(self) -> None:
        self.assertEqual(self.dte_nk_1.slug, '76354771-K--33--170')


class DteDataL0Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_l0_1 = DteDataL0(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
        )

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL0()'
        pass

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l0_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ))

    def test_natural_key(self) -> None:
        self.assertEqual(
            self.dte_l0_1.natural_key,
            DteNaturalKey(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
            ))


class DteDataL1Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_l1_1 = DteDataL1(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
        )

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL1()'
        pass

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l1_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
            ))


class DteDataL2Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.dte_l2_1 = DteDataL2(
            emisor_rut=Rut('76354771-K'),
            tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
            folio=170,
            fecha_emision_date=date(2019, 4, 1),
            receptor_rut=Rut('96790240-3'),
            monto_total=2996301,
            emisor_razon_social='INGENIERIA ENACON SPA',
            receptor_razon_social='MINERA LOS PELAMBRES',
            fecha_vencimiento_date=None,
        )

    def test_init_fail(self) -> None:
        # TODO: implement for 'DteDataL2()'
        pass

    def test_as_dict(self) -> None:
        self.assertDictEqual(
            self.dte_l2_1.as_dict(),
            dict(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
            ))


class FunctionsTest(unittest.TestCase):

    def test_validate_contribuyente_razon_social(self) -> None:
        # TODO: implement for 'validate_contribuyente_razon_social'
        pass

    def test_validate_dte_folio(self) -> None:
        # TODO: implement for 'validate_dte_folio'
        pass

    def test_validate_dte_monto_total(self) -> None:
        # TODO: implement for 'validate_dte_monto_total'
        pass
