import unittest

from cl_sii.rcv.parse_csv import (  # noqa: F401
    RcvCompraNoIncluirCsvRowSchema, RcvCompraPendienteCsvRowSchema,
    RcvCompraReclamadoCsvRowSchema, RcvCompraRegistroCsvRowSchema,
    RcvVentaCsvRowSchema,
    parse_rcv_compra_no_incluir_csv_file, parse_rcv_compra_pendiente_csv_file,
    parse_rcv_compra_reclamado_csv_file, parse_rcv_compra_registro_csv_file,
    parse_rcv_venta_csv_file,
    _parse_rcv_csv_file,
)
from cl_sii.rut import Rut


class RcvVentaCsvRowSchemaTest(unittest.TestCase):

    # TODO: implement for 'RcvVentaCsvRowSchema'.
    pass


class RcvCompraRegistroCsvRowSchemaTest(unittest.TestCase):

    # TODO: implement for 'RcvCompraRegistroCsvRowSchema'.
    pass


class RcvCompraNoIncluirCsvRowSchemaTest(unittest.TestCase):

    # TODO: implement for 'RcvCompraNoIncluirCsvRowSchema'.
    pass


class RcvCompraReclamadoCsvRowSchemaTest(unittest.TestCase):

    # TODO: implement for 'RcvCompraReclamadoCsvRowSchema'.
    pass


class RcvCompraPendienteCsvRowSchemaTest(unittest.TestCase):

    # TODO: implement for 'RcvCompraPendienteCsvRowSchema'.
    pass


class FunctionsTest(unittest.TestCase):

    def test_parse_rcv_venta_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_venta_csv_file'.
        pass

    def test_fail_parse_rcv_venta_csv_file_bad_razon_social(self) -> None:
        other_kwargs = dict(rut=Rut('1-9'), input_file_path='x')

        with self.assertRaises(TypeError) as cm:
            next(parse_rcv_venta_csv_file(razon_social=1, **other_kwargs))
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'razon_social'.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_venta_csv_file(razon_social='', **other_kwargs))
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_venta_csv_file(razon_social=' a ', **other_kwargs))
        self.assertEqual(
            cm.exception.args,
            ("Value must not have leading or trailing whitespace.", ))

    def test_parse_rcv_compra_registro_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_registro_csv_file'.
        pass

    def test_fail_parse_rcv_compra_registro_csv_file_bad_razon_social(self) -> None:
        other_kwargs = dict(rut=Rut('1-9'), input_file_path='x')

        with self.assertRaises(TypeError) as cm:
            next(parse_rcv_compra_registro_csv_file(razon_social=1, **other_kwargs))
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'razon_social'.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_registro_csv_file(razon_social='', **other_kwargs))
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_registro_csv_file(razon_social=' a ', **other_kwargs))
        self.assertEqual(
            cm.exception.args,
            ("Value must not have leading or trailing whitespace.", ))

    def test_parse_rcv_compra_no_incluir_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_no_incluir_csv_file'.
        pass

    def test_fail_parse_rcv_compra_no_incluir_csv_file_bad_razon_social(self) -> None:
        other_kwargs = dict(rut=Rut('1-9'), input_file_path='x')

        with self.assertRaises(TypeError) as cm:
            next(parse_rcv_compra_no_incluir_csv_file(razon_social=1, **other_kwargs))
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'razon_social'.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_no_incluir_csv_file(razon_social='', **other_kwargs))
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_no_incluir_csv_file(razon_social=' a ', **other_kwargs))
        self.assertEqual(
            cm.exception.args,
            ("Value must not have leading or trailing whitespace.", ))

    def test_parse_rcv_compra_reclamado_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_reclamado_csv_file'.
        pass

    def test_fail_parse_rcv_compra_reclamado_csv_file_bad_razon_social(self) -> None:
        other_kwargs = dict(rut=Rut('1-9'), input_file_path='x')

        with self.assertRaises(TypeError) as cm:
            next(parse_rcv_compra_reclamado_csv_file(razon_social=1, **other_kwargs))
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'razon_social'.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_reclamado_csv_file(razon_social='', **other_kwargs))
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_reclamado_csv_file(razon_social=' a ', **other_kwargs))
        self.assertEqual(
            cm.exception.args,
            ("Value must not have leading or trailing whitespace.", ))

    def test_parse_rcv_compra_pendiente_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_pendiente_csv_file'.
        pass

    def test_fail_parse_rcv_compra_pendiente_csv_file_bad_razon_social(self) -> None:
        other_kwargs = dict(rut=Rut('1-9'), input_file_path='x')

        with self.assertRaises(TypeError) as cm:
            next(parse_rcv_compra_pendiente_csv_file(razon_social=1, **other_kwargs))
        self.assertEqual(cm.exception.args, ("Inappropriate type of 'razon_social'.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_pendiente_csv_file(razon_social='', **other_kwargs))
        self.assertEqual(cm.exception.args, ("Value must not be empty.", ))

        with self.assertRaises(ValueError) as cm:
            next(parse_rcv_compra_pendiente_csv_file(razon_social=' a ', **other_kwargs))
        self.assertEqual(
            cm.exception.args,
            ("Value must not have leading or trailing whitespace.", ))

    def test__parse_rcv_csv_file(self) -> None:
        # TODO: implement for '_parse_rcv_csv_file'.
        pass
