import unittest

from cl_sii.dte.constants import TipoDte  # noqa: F401
from cl_sii.rcv import constants  # noqa: F401
from cl_sii.rcv.constants import RcEstadoContable, RcvKind, RcvTipoDocto  # noqa: F401


class RcvKindTest(unittest.TestCase):

    def test_members(self):
        self.assertSetEqual(
            {x for x in RcvKind},
            {
                RcvKind.COMPRAS,
                RcvKind.VENTAS,
            }
        )

    def test_values_type(self):
        self.assertSetEqual(
            {type(x.value) for x in RcvKind},
            {str}
        )

    def test_is_estado_contable_compatible(self):
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

    def test_members(self):
        self.assertSetEqual(
            {x for x in RcEstadoContable},
            {
                RcEstadoContable.REGISTRO,
                RcEstadoContable.NO_INCLUIR,
                RcEstadoContable.RECLAMADO,
                RcEstadoContable.PENDIENTE,
            }
        )

    def test_values_type(self):
        self.assertSetEqual(
            {type(x.value) for x in RcEstadoContable},
            {str}
        )


class RcvTipoDoctoTest(unittest.TestCase):

    def test_members(self):
        self.assertSetEqual(
            {x for x in RcvTipoDocto},
            {
                RcvTipoDocto.FACTURA_INICIO,
                RcvTipoDocto.FACTURA,
                RcvTipoDocto.FACTURA_ELECTRONICA,
                RcvTipoDocto.FACTURA_NO_AFECTA_O_EXENTA,
                RcvTipoDocto.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA,
                RcvTipoDocto.FACTURA_COMPRA,
                RcvTipoDocto.FACTURA_COMPRA_ELECTRONICA,
                RcvTipoDocto.FACTURA_EXPORTACION,
                RcvTipoDocto.FACTURA_EXPORTACION_ELECTRONICA,

                RcvTipoDocto.NOTA_DEBITO,
                RcvTipoDocto.NOTA_DEBITO_ELECTRONICA,
                RcvTipoDocto.NOTA_CREDITO,
                RcvTipoDocto.NOTA_CREDITO_ELECTRONICA,
                RcvTipoDocto.NOTA_DEBITO_EXPORTACION,
                RcvTipoDocto.NOTA_DEBITO_EXPORTACION_ELECTRONICA,
                RcvTipoDocto.NOTA_CREDITO_EXPORTACION,
                RcvTipoDocto.NOTA_CREDITO_EXPORTACION_ELECTRONICA,

                RcvTipoDocto.LIQUIDACION_FACTURA,
                RcvTipoDocto.LIQUIDACION_FACTURA_ELECTRONICA,

                RcvTipoDocto.TOTAL_OP_DEL_MES_BOLETA_AFECTA,
                RcvTipoDocto.TOTAL_OP_DEL_MES_BOLETA_EXENTA,
                RcvTipoDocto.TOTAL_OP_DEL_MES_BOLETA_EXENTA_ELECTR,
                RcvTipoDocto.TOTAL_OP_DEL_MES_BOLETA_ELECTR,

                RcvTipoDocto.TIPO_47,
                RcvTipoDocto.TIPO_48,
                RcvTipoDocto.TIPO_102,
                RcvTipoDocto.TIPO_103,
                RcvTipoDocto.TIPO_105,
                RcvTipoDocto.TIPO_108,
                RcvTipoDocto.TIPO_109,
                RcvTipoDocto.TIPO_901,
                RcvTipoDocto.TIPO_902,
                RcvTipoDocto.TIPO_903,
                RcvTipoDocto.TIPO_904,
                RcvTipoDocto.TIPO_905,
                RcvTipoDocto.TIPO_906,
                RcvTipoDocto.TIPO_907,
                RcvTipoDocto.TIPO_909,
                RcvTipoDocto.TIPO_910,
                RcvTipoDocto.TIPO_911,
                RcvTipoDocto.TIPO_914,
                RcvTipoDocto.TIPO_919,
                RcvTipoDocto.TIPO_920,
                RcvTipoDocto.TIPO_922,
                RcvTipoDocto.TIPO_924,
            }
        )

    def test_values_type(self):
        self.assertSetEqual(
            {type(x.value) for x in RcvTipoDocto},
            {int}
        )

    def test_of_some_member(self):
        value = RcvTipoDocto.FACTURA_ELECTRONICA

        self.assertEqual(value.name, 'FACTURA_ELECTRONICA')
        self.assertEqual(value.value, 33)

    def test_as_tipo_dte(self):
        self.assertEqual(
            RcvTipoDocto.FACTURA_ELECTRONICA.as_tipo_dte(),
            TipoDte.FACTURA_ELECTRONICA)

        with self.assertRaises(ValueError) as cm:
            RcvTipoDocto.FACTURA.as_tipo_dte()
        self.assertEqual(
            cm.exception.args,
            ("There is no equivalent 'TipoDte' for 'RcvTipoDocto.FACTURA'.", ))
