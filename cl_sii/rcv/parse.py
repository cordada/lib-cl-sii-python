import csv
import io
from collections import OrderedDict

import marshmallow
import marshmallow.fields
import marshmallow.validate

from cl_sii.extras import mm_fields
from cl_sii.libs import mm_utils
from cl_sii.libs import tz_utils


_CSV_ROW_DICT_EXTRA_FIELDS_KEY = None
"""CSV row dict key under which the extra data in the row will be saved."""

_RCV_CSV_EXPECTED_FIELD_NAMES = (
    'Nro',
    'Tipo Doc',
    'Tipo Compra',
    'RUT Proveedor',
    'Razon Social',
    'Folio',
    'Fecha Docto',
    'Fecha Recepcion',
    'Fecha Acuse',
    'Monto Exento',
    'Monto Neto',
    'Monto IVA Recuperable',
    'Monto Iva No Recuperable',
    'Codigo IVA No Rec.',
    'Monto Total',
    'Monto Neto Activo Fijo',
    'IVA Activo Fijo',
    'IVA uso Comun',
    'Impto. Sin Derecho a Credito',
    'IVA No Retenido',
    'Tabacos Puros',
    'Tabacos Cigarrillos',
    'Tabacos Elaborados',
    'NCE o NDE sobre Fact. de Compra',
    'Codigo Otro Impuesto',
    'Valor Otro Impuesto',
    'Tasa Otro Impuesto',
)
_RCV_CSV_DIALECT_KEY = 'sii_rcv'


class _RcvCsvDialect(csv.Dialect):

    """
    CSV dialect of RCV CSV files.

    The properties of this dialect were determined with the help of
    :class:`csv.Sniffer`.

    >>> import gzip
    >>> filename = 'SII-download-RCV-file-http-body-response.csv.gz'
    >>> with gzip.open(filename, 'rt', encoding='utf-8') as f:
    ...     dialect = csv.Sniffer().sniff(f.read(50 * 1024))

    """

    delimiter = ';'
    quotechar = '"'
    escapechar = None
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect(_RCV_CSV_DIALECT_KEY, _RcvCsvDialect)


class RcvCsvRowSchema(marshmallow.Schema):

    EXPECTED_INPUT_FIELDS = tuple(_RCV_CSV_EXPECTED_FIELD_NAMES) + (_CSV_ROW_DICT_EXTRA_FIELDS_KEY, )  # type: ignore  # noqa: E501
    FIELD_FECHA_RECEPCION_DATETIME_TZ = tz_utils.TIMEZONE_CL_SANTIAGO

    class Meta:
        strict = True

    emisor_rut = mm_fields.RutField(
        required=True,
        load_from='RUT Proveedor',
    )
    tipo_dte = marshmallow.fields.Integer(
        required=True,
        load_from='Tipo Doc',
    )
    folio = marshmallow.fields.Integer(
        required=True,
        load_from='Folio',
    )
    fecha_emision_date = mm_utils.CustomMarshmallowDateField(
        format='%d/%m/%Y',  # e.g. '22/10/2018'
        required=True,
        load_from='Fecha Docto',
    )
    fecha_recepcion_datetime = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        load_from='Fecha Recepcion',
    )
    # note: this field value is set using data passed in the schema context.
    receptor_rut = mm_fields.RutField(
        required=True,
    )
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto Total',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_datetime'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_datetime'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_datetime'], tz=self.FIELD_FECHA_RECEPCION_DATETIME_TZ)
        # >>> data['fecha_recepcion_datetime'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_datetime'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `datetime_obj.astimezone(pytz.timezone('some timezone'))`

        return data

    @marshmallow.validates_schema(pass_original=True)
    def validate_schema(self, data: dict, original_data: dict) -> None:
        # Fail validation if there was an unexpected input field.
        unexpected_input_fields = (
            set(original_data)
            - set(self.fields)
            - set(self.EXPECTED_INPUT_FIELDS)
        )
        if unexpected_input_fields:
            raise marshmallow.ValidationError(
                'Unexpected input field', field_names=list(unexpected_input_fields))

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    ###########################################################################
    # non-marshmallow-related methods
    ###########################################################################

    def deserialize_csv_row(self, row: OrderedDict) -> dict:
        try:
            result = self.load(row)  # type: marshmallow.UnmarshalResult
        except marshmallow.ValidationError as exc:
            exc_msg = "Validation errors during deserialization."
            validation_error_msgs = dict(exc.normalized_messages())
            raise ValueError(exc_msg, validation_error_msgs) from exc

        result_data = result.data  # type: dict
        result_errors = result.errors  # type: dict
        if result_errors:
            raise Exception("Deserialization errors: %s", result_errors)
        return result_data


def create_rcv_csv_reader(
    text_stream: io.TextIOBase,
    expected_fields_strict: bool = True,
) -> csv.DictReader:
    # note: mypy wrongly complains: it does not accept 'fieldnames' to be None but that value
    #   is completely acceptable, and it even is the default!
    #   > error: Argument "fieldnames" to "DictReader" has incompatible type "None"; expected
    #   > "Sequence[str]"
    csv_reader = csv.DictReader(  # type: ignore
        text_stream,
        fieldnames=None,  # the values of the first row will be used as the fieldnames
        restkey=_CSV_ROW_DICT_EXTRA_FIELDS_KEY,
        dialect=_RCV_CSV_DIALECT_KEY,
    )
    if expected_fields_strict and tuple(csv_reader.fieldnames) != _RCV_CSV_EXPECTED_FIELD_NAMES:
        raise Exception(
            "CSV file field names do not match those expected, or their order.",
            csv_reader.fieldnames)

    return csv_reader
