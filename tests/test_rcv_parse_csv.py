import unittest
from typing import Callable

from cl_sii.rcv.parse_csv import (  # noqa: F401
    RcvCompraNoIncluirCsvRowSchema,
    RcvCompraPendienteCsvRowSchema,
    RcvCompraReclamadoCsvRowSchema,
    RcvCompraRegistroCsvRowSchema,
    RcvVentaCsvRowSchema,
    _parse_rcv_csv_file,
    parse_rcv_compra_no_incluir_csv_file,
    parse_rcv_compra_pendiente_csv_file,
    parse_rcv_compra_reclamado_csv_file,
    parse_rcv_compra_registro_csv_file,
    parse_rcv_venta_csv_file,
)
from cl_sii.rut import Rut
from .utils import get_test_file_path


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

    def test_parse_rcv_venta_csv_file_receptor_rz_leading_trailing_whitespace(self) -> None:
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-rz_leading_trailing_whitespace.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.receptor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.receptor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def _test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
        parse_rcv_compra_csv_file_function: Callable,
        rcv_file_path: str,
    ) -> None:
        rcv_file_path = get_test_file_path(rcv_file_path)

        items = parse_rcv_compra_csv_file_function(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        # Test trailing whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], 'Fake Company S.A. ')
        self.assertEqual(entry_struct.emisor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

        # Test leading whitespace
        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertEqual(row_data['Razon Social'], '  Fake Company S.A.')
        self.assertEqual(entry_struct.emisor_razon_social, 'Fake Company S.A.')
        self.assertEqual(len(row_parsing_errors), 0)

    def test_parse_rcv_compra_registro_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_registro_csv_file'.
        pass

    def test_parse_rcv_compra_registro_csv_file_emisor_rz_leading_trailing_whitespace(self) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_registro_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-registro-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_no_incluir_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_no_incluir_csv_file'.
        pass

    def test_parse_rcv_compra_no_incluir_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_no_incluir_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-no_incluir-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_reclamado_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_reclamado_csv_file'.
        pass

    def test_parse_rcv_compra_reclamado_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_reclamado_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-reclamado-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test_parse_rcv_compra_pendiente_csv_file(self) -> None:
        # TODO: implement for 'parse_rcv_compra_pendiente_csv_file'.
        pass

    def test_parse_rcv_compra_pendiente_csv_file_emisor_rz_leading_trailing_whitespace(
        self,
    ) -> None:
        self._test_parse_rcv_compra_csv_file_emisor_rz_leading_trailing_whitespace(
            parse_rcv_compra_csv_file_function=parse_rcv_compra_pendiente_csv_file,
            rcv_file_path=(
                'test_data/sii-rcv/RCV-compra-pendiente-rz_leading_trailing_whitespace.csv'
            ),
        )

    def test__parse_rcv_csv_file(self) -> None:
        # TODO: implement for '_parse_rcv_csv_file'.
        pass
