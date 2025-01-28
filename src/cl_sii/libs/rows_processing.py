import csv
import logging
from typing import Dict, Iterable, Optional, Sequence, Tuple

import marshmallow


logger = logging.getLogger(__name__)


class MaxRowsExceeded(RuntimeError):
    """
    The maximum number of rows has been exceeded.
    """


###############################################################################
# iterators
###############################################################################


def csv_rows_mm_deserialization_iterator(
    csv_reader: csv.DictReader,
    row_schema: marshmallow.Schema,
    n_rows_offset: int = 0,
    max_n_rows: Optional[int] = None,
    fields_to_remove_names: Optional[Sequence[str]] = None,
) -> Iterable[Tuple[int, Dict[str, object], Dict[str, object], dict]]:
    """
    Marshmallow deserialization iterator over CSV rows.

    Iterate over ``csv_reader``, deserialize each row using ``row_schema``
    and yield the data before and after deserialization, plus any
    validation/deserialization errors.

    .. note:: The CSV header row is omitted, obviously.

    :param csv_reader:
    :param row_schema:
        Marshmallow schema for deserializing each CSV row
    :param n_rows_offset:
        (optional) number of rows to skip (and not deserialize)
    :param max_n_rows:
        (optional) max number of rows to deserialize (raise exception
        if exceeded); ``None`` means no limit
    :param fields_to_remove_names:
        (optional) the name of each field that must be removed (if it exists)
        from the row
    :returns:
        yields a tuple of (``row_ix`` (1-based), ``row_data``,
        ``deserialized_row_data``, ``validation_errors``)
    :raises MaxRowsExceeded:
        number of data rows processed exceeded ``max_n_rows``
    :raises RuntimeError:
        on CSV error when iterating over ``csv_reader``

    """
    rows_iterator: Iterable[Dict[str, object]] = csv_reader
    iterator = rows_mm_deserialization_iterator(
        rows_iterator, row_schema, n_rows_offset, max_n_rows, fields_to_remove_names
    )

    try:
        # note: we chose not to use 'yield from' to be explicit about what we are yielding.
        for row_ix, row_data, deserialized_row_data, validation_errors in iterator:
            yield row_ix, row_data, deserialized_row_data, validation_errors
    except csv.Error as exc:
        exc_msg = f"CSV error for line {csv_reader.line_num} of CSV file."
        raise RuntimeError(exc_msg) from exc


def rows_mm_deserialization_iterator(
    rows_iterator: Iterable[Dict[str, object]],
    row_schema: marshmallow.Schema,
    n_rows_offset: int = 0,
    max_n_rows: Optional[int] = None,
    fields_to_remove_names: Optional[Sequence[str]] = None,
) -> Iterable[Tuple[int, Dict[str, object], Dict[str, object], dict]]:
    """
    Marshmallow deserialization iterator.

    Iterate over ``rows_iterator``, deserialize each row using ``row_schema``
    and yield the data before and after deserialization, plus any
    validation/deserialization errors.

    :param rows_iterator:
    :param row_schema:
        Marshmallow schema for deserializing each row
    :param n_rows_offset:
        (optional) number of rows to skip (and not deserialize)
    :param max_n_rows:
        (optional) max number of rows to deserialize (raise exception
        if exceeded); ``None`` means no limit
    :param fields_to_remove_names:
        (optional) the name of each field that must be removed (if it exists)
        from the row
    :returns:
        yields a tuple of (``row_ix`` (1-based), ``row_data``,
        ``deserialized_row_data``, ``validation_errors``)
    :raises MaxRowsExceeded:
        number of data rows processed exceeded ``max_n_rows``

    """
    if not n_rows_offset >= 0:
        raise ValueError("Param 'n_rows_offset' must be an integer >= 0.")

    fields_to_remove_names = fields_to_remove_names or ()

    for row_ix, row_data in enumerate(rows_iterator, start=1):
        if max_n_rows is not None and row_ix > max_n_rows + n_rows_offset:
            raise MaxRowsExceeded(f"Exceeded 'max_n_rows' limit: {max_n_rows}.")

        if row_ix <= n_rows_offset:
            continue

        for _field_name in fields_to_remove_names:
            row_data.pop(_field_name, None)

        try:
            deserialized_row_data: dict = row_schema.load(row_data)
            raised_validation_errors: dict = {}
        except marshmallow.ValidationError as exc:
            deserialized_row_data = {}
            raised_validation_errors = dict(exc.normalized_messages())

        validation_errors = raised_validation_errors

        yield row_ix, row_data, deserialized_row_data, validation_errors
