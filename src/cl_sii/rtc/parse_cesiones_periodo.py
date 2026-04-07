"""
Parse RTC files (CSV)
=====================

Example:

>>> import pathlib
>>> input_file_path = pathlib.Path('CESIONES_76389992-6_1_01062019_01072019.txt'):
>>> output_file_path = input_file_path.with_suffix('.cleaned.txt')
>>> clean_cesiones_periodo_csv_file(str(input_file_path), str(output_file_path))
>>> g = parse_cesiones_periodo_csv_file(input_file_path=str(output_file_path))
>>> row_ix = 0
>>> for entry_struct, row_ix, row_data, row_parsing_errors in g:
...     if entry_struct is None or row_parsing_errors:
...         print(f"Error for '{output_file_path}':")
...     print(entry_struct, row_ix, row_data, row_parsing_errors)

"""

import csv
import logging
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple, TypedDict

import marshmallow
import marshmallow.experimental.context

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.extras import mm_fields
from cl_sii.libs import csv_utils, mm_utils, rows_processing, tz_utils
from cl_sii.libs.charset_utils import detect_file_encoding
from cl_sii.rtc import data_models_cesiones_periodo
from cl_sii.rut import Rut


logger = logging.getLogger(__name__)


_CESIONES_PERIODO_CSV_HEADERS_LINE = 'VENDEDOR;ESTADO_CESION;DEUDOR;MAIL_DEUDOR;TIPO_DOC;NOMBRE_DOC;FOLIO_DOC;FCH_EMIS_DTE;MNT_TOTAL;CEDENTE;RZ_CEDENTE;MAIL_CEDENTE;CESIONARIO;RZ_CESIONARIO;MAIL_CESIONARIO;FCH_CESION;MNT_CESION;FCH_VENCIMIENTO'  # noqa: E501
_CESIONES_PERIODO_CSV_HEADERS_N = 1 + _CESIONES_PERIODO_CSV_HEADERS_LINE.count(';')
assert _CESIONES_PERIODO_CSV_HEADERS_N == 18


def parse_cesiones_periodo_csv_file(
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: Optional[int] = None,
) -> Iterable[
    Tuple[
        Optional[data_models_cesiones_periodo.CesionesPeriodoEntry],
        int,
        Dict[str, object],
        Dict[str, object],
    ]
]:
    """
    Parse entries from the list of "cesiones" in a period (CSV file).

    The original text file must be cleaned up with
    :func:`clean_cesiones_periodo_csv_file` before parsing.

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.
    input_csv_row_schema_class = CesionesPeriodoCsvRowSchema
    input_file_encoding = detect_file_encoding(input_file_path)
    csv_headers_n = _CESIONES_PERIODO_CSV_HEADERS_N
    csv_headers_line = _CESIONES_PERIODO_CSV_HEADERS_LINE

    expected_input_field_names = (
        'VENDEDOR',  # 'dte_vendedor_rut'
        'ESTADO_CESION',  # 'estado'
        'DEUDOR',  # 'dte_deudor_rut'
        'MAIL_DEUDOR',  # 'deudor_email'
        'TIPO_DOC',  # 'dte_tipo_dte'
        'NOMBRE_DOC',
        'FOLIO_DOC',  # 'dte_folio'
        'FCH_EMIS_DTE',  # 'dte_fecha_emision'
        'MNT_TOTAL',  # 'dte_monto_total'
        'CEDENTE',  # 'cedente_rut'
        'RZ_CEDENTE',  # 'cedente_razon_social'
        'MAIL_CEDENTE',  # 'cedente_email'
        'CESIONARIO',  # 'cesionario_rut'
        'RZ_CESIONARIO',  # 'cesionario_razon_social'
        'MAIL_CESIONARIO',  # 'cesionario_emails'
        'FCH_CESION',  # 'fecha_cesion_dt'
        'MNT_CESION',  # 'monto_cedido'
        'FCH_VENCIMIENTO',  # 'fecha_ultimo_vencimiento'
    )
    fields_to_remove_names = (
        # note: value is redundant with 'TIPO_DOC'
        'NOMBRE_DOC',
    )
    fields_names_map: Dict[str, str] = {
        'VENDEDOR': 'dte_vendedor_rut',
        'ESTADO_CESION': 'estado',
        'DEUDOR': 'dte_deudor_rut',
        'MAIL_DEUDOR': 'deudor_email',
        'TIPO_DOC': 'dte_tipo_dte',
        'FOLIO_DOC': 'dte_folio',
        'FCH_EMIS_DTE': 'dte_fecha_emision',
        'MNT_TOTAL': 'dte_monto_total',
        'CEDENTE': 'cedente_rut',
        'RZ_CEDENTE': 'cedente_razon_social',
        'MAIL_CEDENTE': 'cedente_email',
        'CESIONARIO': 'cesionario_rut',
        'RZ_CESIONARIO': 'cesionario_razon_social',
        'MAIL_CESIONARIO': 'cesionario_emails',
        'FCH_CESION': 'fecha_cesion_dt',
        'MNT_CESION': 'monto_cedido',
        'FCH_VENCIMIENTO': 'fecha_ultimo_vencimiento',
    }

    assert len(expected_input_field_names) == csv_headers_n
    assert ';'.join(expected_input_field_names) == csv_headers_line

    # Assert that all map keys exist in 'expected_input_field_names'.
    assert set(fields_names_map.keys()).issubset(set(expected_input_field_names))
    # Assert that all map values are unique.
    assert len(set(fields_names_map.values())) == len(fields_names_map)
    # Assert that all map values corresponds to a field name of the 'input_csv_row_schema'.
    schema_declared_fields_names = set(input_csv_row_schema_class._declared_fields.keys())
    assert set(fields_names_map.values()).issubset(schema_declared_fields_names)

    schema_context: _CesionesPeriodoCsvRowContext = {
        'fields_names_map': fields_names_map,
    }
    input_csv_row_schema = input_csv_row_schema_class()

    with _CesionesPeriodoCsvRowSchemaContext(schema_context):
        yield from _parse_cesiones_periodo_csv_file(
            input_csv_row_schema,
            expected_input_field_names,
            fields_to_remove_names,
            input_file_path,
            input_file_encoding,
            n_rows_offset,
            max_n_rows,
        )


def clean_cesiones_periodo_csv_file(
    input_file_path: str,
    output_file_path: str,
) -> Tuple[Optional[str], int]:
    """
    Clean CSV file of "cesiones" in a period.

    * Sort all lines except the first two (query params; CSV headers).
    * Remove the first line (query params), if it exists.
    * Change newlines to ``\n``.
    * Replace with ``,`` the unescaped ``;`` character used in email fields
      when there are multiple values.

    >>> clean_cesiones_periodo_csv_file('CESIONES_76389992-6_1_01062019_01072019.txt', 'output.txt')
    ('RUT=76389992-6;TIPO_CONSULTA=CEDENTE;DESDE_DDMMAAAA=01062019;HASTA_DDMMAAAA=01072019',
     1700)

    :return: query params and number of "cesiones"

    """

    def _clean_line(original: str) -> str:
        # Merge consecutive fields that look like they are email addresses (e.g. have the '@' char),
        #   setting a ',' as separator.
        #   e.g. convert this:
        #       'whatever;x@a.com;y@b.cl;2019'
        #   to:
        #       'whatever;x@a.com,y@b.cl;2019'
        last_match_ix = None
        fields_values = original.split(';')
        new_fields_values = []

        for field_ix, field_value in enumerate(fields_values):
            if '@' in field_value:
                if last_match_ix is not None and field_ix == last_match_ix + 1:
                    new_fields_values[-1] += f',{field_value}'
                else:
                    new_fields_values.append(field_value)
                last_match_ix = field_ix
            else:
                new_fields_values.append(field_value)

        modified = ';'.join(new_fields_values)

        return modified

    def _line_needs_cleaning(original_line: str) -> bool:
        # The line needs to be cleaned if it does not have the expected number of columns.
        return original_line.count(';') != _CESIONES_PERIODO_CSV_HEADERS_N - 1

    file_encoding = detect_file_encoding(input_file_path)
    output_new_line_str = '\n'

    # note: reading text with `newline=None` means line endings will be autodetected
    #   (both '\n' and '\r\n' work), and the output of `readline()` includes '\n'
    #   (in Linux at least) at the end.
    with open(input_file_path, mode='rt', encoding=file_encoding, newline=None) as input_f:
        query_params: Optional[str] = None
        # e.g. 'DATOS_CONSULTA; RUT=76389992-6;TIPO_CONSULTA=CEDENTE;DESDE_DDMMAAAA=01062019;HASTA_DDMMAAAA=01072019'  # noqa: E501
        query_params_line = input_f.readline().upper().strip()
        csv_headers_line = None

        if query_params_line.startswith('DATOS_CONSULTA;'):
            query_params = query_params_line.partition('DATOS_CONSULTA;')[2].strip()
        elif query_params_line == _CESIONES_PERIODO_CSV_HEADERS_LINE:
            csv_headers_line = query_params_line
        else:
            # TODO: use a new custom exception for this kind of cases.
            raise Exception(
                "First line is not the query params line ('DATOS_CONSULTA;'...) "
                "nor the expected CSV headers line ('%s...'): %s",
                _CESIONES_PERIODO_CSV_HEADERS_LINE[:30],
                query_params_line,
            )

        if csv_headers_line is None:
            csv_headers_line = input_f.readline().upper().strip()
            if not csv_headers_line == _CESIONES_PERIODO_CSV_HEADERS_LINE:
                # TODO: use a new custom exception for this kind of cases.
                raise Exception(
                    "CSV headers line does not match what is expected ('%s...'): %s",
                    _CESIONES_PERIODO_CSV_HEADERS_LINE[:30],
                    csv_headers_line,
                )

        sorted_lines = sorted(input_f)
        n_sorted_lines = len(sorted_lines)
        sorted_clean_lines = []
        for line in sorted_lines:
            sorted_clean_lines.append(_clean_line(line) if _line_needs_cleaning(line) else line)

        with open(output_file_path, mode='wt', encoding=file_encoding, newline=None) as output_f:
            output_f.writelines(
                [
                    csv_headers_line + output_new_line_str,
                ]
            )
            output_f.writelines(sorted_clean_lines)

    return query_params, n_sorted_lines


###############################################################################
# schemas
###############################################################################


class _CesionesPeriodoCsvRowContext(TypedDict):
    fields_names_map: Mapping[str, str]


_CesionesPeriodoCsvRowSchemaContext = marshmallow.experimental.context.Context[
    _CesionesPeriodoCsvRowContext
]


class CesionesPeriodoCsvRowSchema(marshmallow.Schema):
    FIELD_FECHA_CESION_DT_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # fields of DTE
    ###########################################################################

    dte_vendedor_rut = mm_fields.RutField(
        required=True,
    )
    dte_deudor_rut = mm_fields.RutField(
        required=True,
    )
    dte_tipo_dte = mm_fields.TipoDteField(
        required=True,
    )
    dte_folio = marshmallow.fields.Integer(
        required=True,
    )
    dte_fecha_emision = mm_utils.CustomMarshmallowDateField(
        format='%Y-%m-%d',  # e.g. '2018-11-19'
        required=True,
    )
    dte_monto_total = marshmallow.fields.Integer(
        required=True,
    )

    ###########################################################################
    # fields of "cesion"
    ###########################################################################

    cedente_rut = mm_fields.RutField(
        required=True,
    )
    cedente_razon_social = marshmallow.fields.String(
        required=True,
    )
    cedente_email = marshmallow.fields.String(
        allow_none=True,
        load_default=None,
    )
    cesionario_rut = mm_fields.RutField(
        required=True,
    )
    cesionario_razon_social = marshmallow.fields.String(
        required=True,
    )
    cesionario_emails = marshmallow.fields.String(
        allow_none=True,
        load_default=None,
    )
    # note: this is not a field of the DTE even though 'dte_deudor_rut' is.
    deudor_email = marshmallow.fields.String(
        allow_none=True,
        load_default=None,
    )
    fecha_cesion_dt = marshmallow.fields.DateTime(
        # warning: input does not include seconds
        format='%Y-%m-%d %H:%M',  # e.g. '2019-06-13 14:31'
        required=True,
    )
    # note: parsed directly from a copy of the input 'fecha_cesion_dt'.
    fecha_cesion = mm_utils.CustomMarshmallowDateField(
        # note: even though the time is parsed, it will be discarded.
        format='%Y-%m-%d %H:%M',  # e.g. '2019-06-13 14:31'
        required=True,
    )
    monto_cedido = marshmallow.fields.Integer(
        required=True,
    )
    fecha_ultimo_vencimiento = mm_utils.CustomMarshmallowDateField(
        format='%Y-%m-%d',  # e.g. '2018-11-19'
        required=True,
    )

    estado = marshmallow.fields.String(
        required=True,
    )

    @marshmallow.validates_schema(pass_original=True)
    def validate_schema(self, data: dict, original_data: dict, **kwargs: Any) -> None:
        mm_utils.validate_no_unexpected_input_fields(self, data, original_data)

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Rename fields according to the map defined in 'fields_names_map'.
        fields_names_map: Mapping[str, str] = _CesionesPeriodoCsvRowSchemaContext.get()[
            'fields_names_map'
        ]
        for original_field_name, new_field_name in fields_names_map.items():
            if original_field_name in in_data:
                in_data[new_field_name] = in_data.pop(original_field_name)

        # Copy values.
        if 'fecha_cesion' not in in_data and 'fecha_cesion_dt' in in_data:
            in_data['fecha_cesion'] = in_data['fecha_cesion_dt']

        # Fix some values.
        if 'cedente_email' in in_data:
            if in_data['cedente_email'] in ('', 'null'):
                in_data['cedente_email'] = None
        if 'cesionario_emails' in in_data:
            if in_data['cesionario_emails'] in ('', 'null'):
                in_data['cesionario_emails'] = None
        if 'deudor_email' in in_data:
            if in_data['deudor_email'] in ('', 'null'):
                in_data['deudor_email'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
        # >>> data['fecha_cesion_dt'].isoformat()
        # '2019-02-26T22:24:00'
        data['fecha_cesion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_cesion_dt'], tz=self.FIELD_FECHA_CESION_DT_TZ
        )
        # >>> data['fecha_cesion_dt'].isoformat()
        # '2019-02-26T22:24:00-03:00'
        # >>> data['fecha_cesion_dt'].astimezone(pytz.UTC).isoformat()
        # '2019-02-27T01:24:00+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        return data

    def as_data_model(self, data: dict) -> data_models_cesiones_periodo.CesionesPeriodoEntry:
        try:
            dte_vendedor_rut: Rut = data['dte_vendedor_rut']
            dte_deudor_rut: Rut = data['dte_deudor_rut']
            dte_tipo_dte = data['dte_tipo_dte']
            dte_folio: int = data['dte_folio']
            dte_fecha_emision: date = data['dte_fecha_emision']
            dte_monto_total: int = data['dte_monto_total']

            cedente_rut: Rut = data['cedente_rut']
            cedente_razon_social: str = data['cedente_razon_social']
            cedente_email: Optional[str] = data['cedente_email']
            cesionario_rut: Rut = data['cesionario_rut']
            cesionario_razon_social: str = data['cesionario_razon_social']
            cesionario_emails: Optional[str] = data['cesionario_emails']
            deudor_email: Optional[str] = data['deudor_email']

            fecha_cesion_dt: datetime = data['fecha_cesion_dt']
            fecha_cesion: datetime = data['fecha_cesion']
            monto_cedido: int = data['monto_cedido']
            fecha_ultimo_vencimiento: date = data['fecha_ultimo_vencimiento']
            estado: str = data['estado']
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = data_models_cesiones_periodo.CesionesPeriodoEntry(
                dte_vendedor_rut=dte_vendedor_rut,
                dte_deudor_rut=dte_deudor_rut,
                dte_tipo_dte=dte_tipo_dte,
                dte_folio=dte_folio,
                dte_fecha_emision=dte_fecha_emision,
                dte_monto_total=dte_monto_total,
                cedente_rut=cedente_rut,
                cedente_razon_social=cedente_razon_social,
                cedente_email=cedente_email,
                cesionario_rut=cesionario_rut,
                cesionario_razon_social=cesionario_razon_social,
                cesionario_emails=cesionario_emails,
                deudor_email=deudor_email,
                fecha_cesion_dt=fecha_cesion_dt,
                fecha_cesion=fecha_cesion,
                monto_cedido=monto_cedido,
                fecha_ultimo_vencimiento=fecha_ultimo_vencimiento,
                estado=estado,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


###############################################################################
# helpers
###############################################################################


class _CesionesPeriodoCsvDialect(csv.Dialect):
    """
    CSV dialect of "cesiones" in a period CSV files.

    The properties of this dialect were determined with the help of
    :class:`csv.Sniffer`.

    >>> filename = 'CESIONES_76389992-6_1_01062019_01072019.txt'
    >>> with open(filename, 'rt', encoding='utf-8') as f:
    ...     dialect = csv.Sniffer().sniff(f.read(50 * 1024))

    """

    delimiter = ';'
    quotechar = '"'
    escapechar = None
    doublequote = False
    skipinitialspace = False
    # note: the original file uses '\r\n' for new lines but we replace them with '\n'
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL


def _parse_cesiones_periodo_csv_file(
    input_csv_row_schema: CesionesPeriodoCsvRowSchema,
    expected_input_field_names: Sequence[str],
    fields_to_remove_names: Sequence[str],
    input_file_path: str,
    input_file_encoding: str,
    n_rows_offset: int,
    max_n_rows: Optional[int] = None,
) -> Iterable[
    Tuple[
        Optional[data_models_cesiones_periodo.CesionesPeriodoEntry],
        int,
        Dict[str, object],
        Dict[str, object],
    ]
]:
    """
    Parse entries from the list of "cesiones" in a period (CSV file).

    """
    for field_to_remove_name in fields_to_remove_names:
        if field_to_remove_name not in expected_input_field_names:
            raise Exception(
                "Programming error: field to remove is not one of the expected ones.",
                field_to_remove_name,
            )

    _CSV_ROW_DICT_EXTRA_FIELDS_KEY = '_extra_csv_fields_data'

    fields_to_remove_names += (_CSV_ROW_DICT_EXTRA_FIELDS_KEY,)  # type: ignore

    # note:
    #   > If csvfile is a file object, it should be opened with newline=''
    #   https://docs.python.org/3/library/csv.html#csv.reader
    with open(input_file_path, mode='rt', encoding=input_file_encoding, newline='') as input_f:
        # Create a CSV reader, with auto-detection of header names (first row).
        csv_reader = csv_utils.create_csv_dict_reader(
            input_f,
            csv_dialect=_CesionesPeriodoCsvDialect,
            row_dict_extra_fields_key=_CSV_ROW_DICT_EXTRA_FIELDS_KEY,
            expected_fields_strict=True,
            expected_field_names=expected_input_field_names,
        )

        g = rows_processing.csv_rows_mm_deserialization_iterator(
            csv_reader,
            row_schema=input_csv_row_schema,
            n_rows_offset=n_rows_offset,
            max_n_rows=max_n_rows,
            fields_to_remove_names=fields_to_remove_names,
        )

        for row_ix, row_data, deserialized_row_data, validation_errors in g:
            entry: Optional[data_models_cesiones_periodo.CesionesPeriodoEntry] = None
            row_errors: Dict[str, object] = {}
            conversion_error = None

            if not validation_errors:
                try:
                    entry = input_csv_row_schema.as_data_model(deserialized_row_data)
                except Exception as exc:
                    conversion_error = str(exc)
                    logger.exception(
                        "Deserialized data to data model instance conversion failed "
                        "(probably a programming error)."
                    )

            # Instead of empty dicts, lists, str, etc, we want to have None.
            if validation_errors:
                row_errors['validation'] = validation_errors
            if conversion_error:
                row_errors['other'] = conversion_error

            yield entry, row_ix, row_data, row_errors
