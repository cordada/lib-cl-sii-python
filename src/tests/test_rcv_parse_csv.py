import unittest
from typing import Callable
from unittest import mock

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

    def test_parse_rcv_venta_csv_file_missing_required_fields(self):
        # This CSV should have a required field (e.g., 'Folio') as an empty string
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-missing-required-fields.csv',
        )

        items = parse_rcv_venta_csv_file(
            rut=Rut('1-9'),
            input_file_path=rcv_file_path,
            n_rows_offset=0,
            max_n_rows=None,
        )

        entry_struct, row_ix, row_data, row_parsing_errors = next(items)
        self.assertIsNone(entry_struct)
        self.assertIn('validation', row_parsing_errors)
        self.assertIn('Fecha Recepcion', row_parsing_errors['validation'])
        self.assertIn('Tipo Doc', row_parsing_errors['validation'])
        self.assertEqual(
            row_parsing_errors['validation']['Fecha Recepcion'],
            ['Missing data for required field.'],
        )

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

    def test_parse_rcv_venta_csv_file_conversion_error(self):
        rcv_file_path = get_test_file_path(
            'test_data/sii-rcv/RCV-venta-rz_leading_trailing_whitespace.csv',
        )

        # Patch the to_detalle_entry method to raise an exception
        with (
            self.assertLogs('cl_sii.rcv', level='ERROR') as assert_logs_cm,
            mock.patch.object(
                RcvVentaCsvRowSchema,
                'to_detalle_entry',
                side_effect=ValueError('Mocked conversion error'),
            ),
        ):
            items = parse_rcv_venta_csv_file(
                rut=Rut('1-9'),
                input_file_path=rcv_file_path,
                n_rows_offset=0,
                max_n_rows=1,
            )
            entry_struct, row_ix, row_data, row_parsing_errors = next(items)
            self.assertIsNone(entry_struct)
            self.assertIn('conversion_errors', row_parsing_errors)
            self.assertIn('Mocked conversion error', row_parsing_errors['conversion_errors'])
            self.assertRegex(
                assert_logs_cm.output[0],
                (
                    'ERROR:cl_sii.rcv.parse_csv:'
                    'Deserialized row data conversion failed for row 1: Mocked conversion error'
                ),
            )

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
