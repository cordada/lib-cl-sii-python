import datetime
from unittest import TestCase

from cl_sii import rcv
from cl_sii import rut


class ProcessRcvCsvFileTests(TestCase):
    owner_rut: rut.Rut
    total_rows: int

    @classmethod
    def setUpClass(cls) -> None:
        cls.owner_rut = rut.Rut('6824160-K')
        cls.total_rows = 3233

    def test_ok(self) -> None:
        total_rows = 0

        with open('tests/test_data/rcv_csv/purchase_all_document_types.csv', mode='r') as f:
            # TODO: fix type
            rows_generator = rcv.process_rcv_csv_file(  # type: ignore
                f, self.owner_rut.canonical)
            for row in rows_generator:
                self.assertIn('receptor_rut', row)
                self.assertIsInstance(row['receptor_rut'], rut.Rut)
                self.assertTrue(self.owner_rut == row['receptor_rut'])

                self.assertIn('emisor_rut', row)
                self.assertIsInstance(row['emisor_rut'], rut.Rut)

                self.assertIn('tipo_dte', row)
                self.assertIsInstance(row['tipo_dte'], int)

                self.assertIn('folio', row)
                self.assertIsInstance(row['folio'], int)

                self.assertIn('monto_total', row)
                self.assertIsInstance(row['monto_total'], int)

                self.assertIn('fecha_recepcion_datetime', row)
                self.assertIsInstance(row['fecha_recepcion_datetime'], datetime.datetime)

                self.assertIn('fecha_emision_date', row)
                self.assertIsInstance(row['fecha_emision_date'], datetime.date)

                total_rows = total_rows + 1
        self.assertEqual(total_rows, self.total_rows)

    def test_max_data_row(self) -> None:
        with open('tests/test_data/rcv_csv/purchase_all_document_types.csv', mode='r') as f:
            # TODO: fix type
            rows_generator = rcv.process_rcv_csv_file(  # type: ignore
                f, self.owner_rut.canonical, max_data_rows=1)

            with self.assertRaisesRegex(Exception, r'Exceeded \'max_data_rows\' value: 1\.'):
                for _ in rows_generator:
                    continue

    def test_invalid_row(self) -> None:
        excepted_message = (
            r"Error deserializing row 1 of CSV file: "
            r"\('Validation errors during deserialization.', "
            r"{'Fecha Docto': \['Not a valid date\.'\]}\)"
        )

        with open('tests/test_data/rcv_csv/purchase_invalid_row.csv', mode='r') as f:
            # TODO: fix type
            rows_generator = rcv.process_rcv_csv_file(  # type: ignore
                f, self.owner_rut.canonical)

            with self.assertRaisesRegex(Exception, excepted_message):
                for _ in rows_generator:
                    continue

    def test_missing_row(self) -> None:
        expected_fields_name = [
            'Tipo Doc', 'Tipo Compra', 'RUT Proveedor', 'Razon Social', 'Folio', 'Fecha Docto',
            'Fecha Recepcion', 'Fecha Acuse', 'Monto Exento', 'Monto Neto', 'Monto IVA Recuperable',
            'Monto Iva No Recuperable', 'Codigo IVA No Rec.', 'Monto Total',
            'Monto Neto Activo Fijo', 'IVA Activo Fijo', 'IVA uso Comun',
            'Impto. Sin Derecho a Credito', 'IVA No Retenido', 'Tabacos Puros',
            'Tabacos Cigarrillos', 'Tabacos Elaborados', 'NCE o NDE sobre Fact. de Compra',
            'Codigo Otro Impuesto', 'Valor Otro Impuesto', 'Tasa Otro Impuesto'
        ]

        with open('tests/test_data/rcv_csv/purchase_missing_row.csv', mode='r') as f:
            # TODO: fix type
            rows_generator = rcv.process_rcv_csv_file(  # type: ignore
                f, self.owner_rut.canonical)

            with self.assertRaises(Exception) as context_manager:
                for _ in rows_generator:
                    continue

        exception = context_manager.exception
        self.assertEqual(len(exception.args), 2)
        message, fields_name = exception.args
        self.assertEqual(
            message,
            'CSV file field names do not match those expected, or their order.')
        self.assertListEqual(fields_name, expected_fields_name)

    def test_invalid_csv(self) -> None:
        with open('tests/test_data/rcv_csv/invalid.csv', mode='r') as f:
            # TODO: fix type
            rows_generator = rcv.process_rcv_csv_file(  # type: ignore
                f, self.owner_rut.canonical)

            with self.assertRaises(Exception) as context_manager:
                for _ in rows_generator:
                    continue

        exception = context_manager.exception
        self.assertEqual(len(exception.args), 2)
        message, fields_name = exception.args
        self.assertEqual(
            message,
            'CSV file field names do not match those expected, or their order.')
        expected_fields_name = ['I am not a CSV']
        self.assertListEqual(fields_name, expected_fields_name)
