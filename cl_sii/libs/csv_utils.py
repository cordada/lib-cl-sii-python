import csv
from typing import IO, Sequence, Type, Union


def create_csv_dict_reader(
    text_stream: IO[str],
    csv_dialect: Type[csv.Dialect],
    row_dict_extra_fields_key: Union[str, None] = None,
    expected_fields_strict: bool = True,
    expected_field_names: Sequence[str] = None,
) -> csv.DictReader:
    """
    Create a CSV dict reader with custom options.

    :param text_stream:
    :param row_dict_extra_fields_key:
        CSV row dict key under which the extra data in the row will be saved
    :param csv_dialect:
    :param expected_fields_strict:
    :param expected_field_names:
        (required if ``expected_field_names`` is True)
    :return: a CSV DictReader

    """
    csv_reader = csv.DictReader(
        text_stream,
        fieldnames=None,  # the values of the first row will be used as the fieldnames
        restkey=row_dict_extra_fields_key,
        dialect=csv_dialect,
    )

    if expected_fields_strict:
        if expected_field_names:
            if csv_reader.fieldnames is None:
                raise Exception(
                    "Programming error: when a 'csv.DictReader' instance is created with"
                    "'fieldnames=None', the attribute will be set to the values of the first row."
                )
            if tuple(csv_reader.fieldnames) != expected_field_names:
                raise ValueError(
                    "CSV file field names do not match those expected, or their order.",
                    csv_reader.fieldnames,
                )
        else:
            raise ValueError(
                "Param 'expected_field_names' is required if 'expected_fields_strict' is True."
            )

    return csv_reader
