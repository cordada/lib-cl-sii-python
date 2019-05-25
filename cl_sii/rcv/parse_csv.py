"""
Parse RCV files (CSV)
=====================


"""
import csv
from datetime import date
import logging
from typing import Dict, Iterable, Optional, Sequence, Tuple

import marshmallow
import marshmallow.fields
import marshmallow.validate

from cl_sii.dte.data_models import DteDataL2
from cl_sii.extras import mm_fields
from cl_sii.libs import csv_utils
from cl_sii.libs import mm_utils
from cl_sii.libs import rows_processing
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut


logger = logging.getLogger(__name__)


def parse_rcv_venta_csv_file(
    emisor_rut: Rut,
    emisor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[DteDataL2], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse DTE data objects from a RCV "Venta" file (CSV).

    """
    schema_context = dict(
        emisor_rut=emisor_rut,
        emisor_razon_social=emisor_razon_social,
    )
    input_csv_row_schema = RcvVentaCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_dte'
        'Tipo Venta',
        'Rut cliente',  # 'receptor_rut'
        'Razon Social',  # 'receptor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        # 'Fecha Acuse Recibo',  # 'fecha_acuse_recibo_dt'
        'Fecha Acuse Recibo',
        # 'Fecha Reclamo',  # 'fecha_reclamo_dt'
        'Fecha Reclamo',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA',
        'Monto total',  # 'monto_total'
        'IVA Retenido Total',
        'IVA Retenido Parcial',
        'IVA no retenido',
        'IVA propio',
        'IVA Terceros',
        'RUT Emisor Liquid. Factura',
        'Neto Comision Liquid. Factura',
        'Exento Comision Liquid. Factura',
        'IVA Comision Liquid. Factura',
        'IVA fuera de plazo',
        'Tipo Docto. Referencia',
        'Folio Docto. Referencia',
        'Num. Ident. Receptor Extranjero',
        'Nacionalidad Receptor Extranjero',
        'Credito empresa constructora',
        'Impto. Zona Franca (Ley 18211)',
        'Garantia Dep. Envases',
        'Indicador Venta sin Costo',
        'Indicador Servicio Periodico',
        'Monto No facturable',
        'Total Monto Periodo',
        'Venta Pasajes Transporte Nacional',
        'Venta Pasajes Transporte Internacional',
        'Numero Interno',
        'Codigo Sucursal',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Imp.',
        'Valor Otro Imp.',
        'Tasa Otro Imp.',
    )

    fields_to_remove_names = (
        'Nro',
        'Tipo Venta',
        'Fecha Acuse Recibo',
        'Fecha Reclamo',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA',
        'IVA Retenido Total',
        'IVA Retenido Parcial',
        'IVA no retenido',
        'IVA propio',
        'IVA Terceros',
        'RUT Emisor Liquid. Factura',
        'Neto Comision Liquid. Factura',
        'Exento Comision Liquid. Factura',
        'IVA Comision Liquid. Factura',
        'IVA fuera de plazo',
        'Tipo Docto. Referencia',
        'Folio Docto. Referencia',
        'Num. Ident. Receptor Extranjero',
        'Nacionalidad Receptor Extranjero',
        'Credito empresa constructora',
        'Impto. Zona Franca (Ley 18211)',
        'Garantia Dep. Envases',
        'Indicador Venta sin Costo',
        'Indicador Servicio Periodico',
        'Monto No facturable',
        'Total Monto Periodo',
        'Venta Pasajes Transporte Nacional',
        'Venta Pasajes Transporte Internacional',
        'Numero Interno',
        'Codigo Sucursal',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Imp.',
        'Valor Otro Imp.',
        'Tasa Otro Imp.',
    )

    yield from _parse_rcv_csv_file(
        input_csv_row_schema,
        expected_input_field_names,
        fields_to_remove_names,
        input_file_path,
        n_rows_offset,
        max_n_rows,
    )


###############################################################################
# schemas
###############################################################################

class _RcvCsvRowSchemaBase(marshmallow.Schema):

    @marshmallow.validates_schema(pass_original=True)
    def validate_schema(self, data: dict, original_data: dict) -> None:
        mm_utils.validate_no_unexpected_input_fields(self, data, original_data)

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    def to_dte_data_l2(self, data: dict) -> DteDataL2:
        # note: the data of some serializer fields may not be included in the returned struct.

        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            tipo_dte = data['tipo_dte']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            receptor_razon_social: str = data['receptor_razon_social']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            dte_data = DteDataL2(
                emisor_rut=emisor_rut,
                tipo_dte=tipo_dte,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                receptor_razon_social=receptor_razon_social,
                # fecha_vencimiento_date='',
                # firma_documento_dt='',
                # signature_value='',
                # signature_x509_cert_der='',
                # emisor_giro='',
                # emisor_email='',
                # receptor_email='',
            )
        except (TypeError, ValueError):
            raise

        return dte_data


class RcvVentaCsvRowSchema(_RcvCsvRowSchemaBase):

    FIELD_FECHA_RECEPCION_DT_TZ = DteDataL2.DATETIME_FIELDS_TZ
    FIELD_FECHA_ACUSE_RECIBO_DT_TZ = DteDataL2.DATETIME_FIELDS_TZ
    FIELD_FECHA_RECLAMO_DT_TZ = DteDataL2.DATETIME_FIELDS_TZ

    class Meta:
        strict = True

    ###########################################################################
    # basic fields
    ###########################################################################

    tipo_dte = mm_fields.TipoDteField(
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
    receptor_rut = mm_fields.RutField(
        required=True,
        load_from='Rut cliente',
    )
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto total',
    )
    receptor_razon_social = marshmallow.fields.String(
        required=True,
        load_from='Razon Social',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
    )

    ###########################################################################
    # extra fields: not included in the returned struct
    ###########################################################################

    fecha_recepcion_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        load_from='Fecha Recepcion',
    )
    fecha_acuse_recibo_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=False,
        allow_none=True,
        load_from='Fecha Acuse Recibo',
    )
    fecha_reclamo_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=False,
        allow_none=True,
        load_from='Fecha Reclamo',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('emisor_rut', self.context['emisor_rut'])
        in_data.setdefault('emisor_razon_social', self.context['emisor_razon_social'])

        # Fix missing/default values.
        if 'Fecha Acuse Recibo' in in_data:
            if in_data['Fecha Acuse Recibo'] == '':
                in_data['Fecha Acuse Recibo'] = None
        if 'Fecha Reclamo' in in_data:
            if in_data['Fecha Reclamo'] == '':
                in_data['Fecha Reclamo'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ)
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        if 'fecha_acuse_recibo_dt' in data and data['fecha_acuse_recibo_dt']:
            data['fecha_acuse_recibo_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_acuse_recibo_dt'], tz=self.FIELD_FECHA_ACUSE_RECIBO_DT_TZ)
        if 'fecha_reclamo_dt' in data and data['fecha_reclamo_dt']:
            data['fecha_reclamo_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_reclamo_dt'], tz=self.FIELD_FECHA_RECLAMO_DT_TZ)

        return data


###############################################################################
# helpers
###############################################################################

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


def _parse_rcv_csv_file(
    input_csv_row_schema: _RcvCsvRowSchemaBase,
    expected_input_field_names: Sequence[str],
    fields_to_remove_names: Sequence[str],
    input_file_path: str,
    n_rows_offset: int,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[DteDataL2], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse DTE data objects from a RCV file (CSV).

    Common implementation for the different kinds of RCV files (CSV).

    """
    for field_to_remove_name in fields_to_remove_names:
        if field_to_remove_name not in expected_input_field_names:
            raise Exception(
                "Programming error: field to remove is not one of the expected ones.",
                field_to_remove_name)

    _CSV_ROW_DICT_EXTRA_FIELDS_KEY = '_extra_csv_fields_data'

    fields_to_remove_names += (_CSV_ROW_DICT_EXTRA_FIELDS_KEY, )  # type: ignore

    input_data_enc = 'utf-8'
    # note:
    #   > If csvfile is a file object, it should be opened with newline=''
    #   https://docs.python.org/3/library/csv.html#csv.reader
    with open(input_file_path, mode='rt', encoding=input_data_enc, newline='') as input_f:
        # Create a CSV reader, with auto-detection of header names (first row).
        csv_reader = csv_utils.create_csv_dict_reader(
            input_f,
            csv_dialect=_RcvCsvDialect,
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
            logger.debug("Processing row %s. Content: %s", row_ix, repr(row_data))

            dte_data = None
            row_errors: Dict[str, object] = {}
            conversion_error = None

            if not validation_errors:
                try:
                    dte_data = input_csv_row_schema.to_dte_data_l2(deserialized_row_data)
                except Exception as exc:
                    conversion_error = str(exc)
                    logger.exception(
                        "Deserialized data to data model instance conversion failed "
                        "(probably a programming error).")

            # Instead of empty dicts, lists, str, etc, we want to have None.
            if validation_errors:
                row_errors['validation'] = validation_errors
            if conversion_error:
                row_errors['other'] = conversion_error

            yield dte_data, row_ix, row_data, row_errors
