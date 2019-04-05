"""
SII RCV ("Registro de Compras y Ventas").

.. note::
    The RCV ("Registro de Compras y Ventas") is composed of 2 "registros":
    RC ("Registro de Compras") and RV ("Registro de Ventas").

.. seealso::
    http://www.sii.cl/preguntas_frecuentes/catastro/001_012_6971.htm

"""
import csv
import io
from typing import Callable

from . import parse


def process_rcv_csv_file(
    text_stream: io.TextIOBase,
    rcv_owner_rut: str,
    row_data_handler: Callable,
    max_data_rows: int = None,
) -> int:
    """
    Process a RCV CSV file.

    Processing steps:
    - Create a CSV reader, with auto-detection of header names (first row).
    - Instantiate an schema to parse and deserialize each row.
    - For each data row:
        - Using an appropriate schema, deserialize the raw data.
        - Apply ``row_data_handler`` to the deserialization output.

    :param text_stream: a file-like object, not necessarily a real file
    :param rcv_owner_rut: RCV file owner's RUT
    :param row_data_handler: function be called with parsed row data
    :param max_data_rows: max number of data rows to process (raise exception if exceeded);
        ``None`` means no limit
    :return: number of data rows processed

    """
    # TODO: convert to iterator. That way we do not need the 'row_data_handler' and we can also use
    #   the same function to retrieve the collection of deserialized rows.

    csv_reader = parse.create_rcv_csv_reader(text_stream, expected_fields_strict=True)
    schema = parse.RcvCsvRowSchema(context=dict(receptor_rut=rcv_owner_rut))

    try:
        for row_ix, row_data in enumerate(csv_reader, start=1):
            if max_data_rows is not None and row_ix > max_data_rows:
                # TODO: custom exception
                raise Exception("Exceeded 'max_data_rows' value: {}.".format(max_data_rows))

            try:
                deserialized_row_data = schema.deserialize_csv_row(row_data)
            except Exception as exc:
                exc_msg = "Error deserializing row {} of CSV file: {}".format(row_ix, exc)
                raise Exception(exc_msg) from exc
            try:
                row_data_handler(row_ix, deserialized_row_data)
            except Exception as exc:
                exc_msg = "Error in row_data_handler for row {} of CSV file: {}".format(row_ix, exc)
                raise Exception(exc_msg) from exc

        # The first row in the CSV file is not a data row; it is the headers row.
        rows_processed = csv_reader.line_num - 1
    except csv.Error as exc:
        exc_msg = "CSV error for line {} of CSV file: {}".format(csv_reader.line_num, exc)
        raise Exception(exc_msg) from exc

    return rows_processed
