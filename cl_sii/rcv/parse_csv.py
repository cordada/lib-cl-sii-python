"""
Parse RCV files (CSV)
=====================


"""
import csv
import logging
from datetime import date, datetime
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple

import marshmallow

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.extras import mm_fields
from cl_sii.libs import csv_utils, mm_utils, rows_processing, tz_utils
from cl_sii.rut import Rut
from .constants import RcEstadoContable, RcvKind
from .data_models import (
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RcvDetalleEntry,
    RvDetalleEntry,
)


logger = logging.getLogger(__name__)


RcvCsvFileParserType = Callable[
    [Rut, str, int, Optional[int]],
    Iterable[
        Tuple[
            Optional[RcvDetalleEntry],
            int,
            Dict[str, object],
            Dict[str, object],
        ],
    ],
]


def get_rcv_csv_file_parser(
    rcv_kind: RcvKind,
    estado_contable: Optional[RcEstadoContable],
) -> RcvCsvFileParserType:
    """
    Return a function that parses a CSV file of the given :class:`RcvKind` and
    :class:`RcEstadoContable`.

    :raises ValueError:
    :raises Exception: on unrecoverable errors
    """
    parse_func: RcvCsvFileParserType

    if rcv_kind == RcvKind.COMPRAS:
        if estado_contable is None:
            raise ValueError(
                "'estado_contable' must not be None when 'rcv_kind' is 'COMPRAS'.",
            )
        elif estado_contable == RcEstadoContable.REGISTRO:
            parse_func = parse_rcv_compra_registro_csv_file
        elif estado_contable == RcEstadoContable.NO_INCLUIR:
            parse_func = parse_rcv_compra_no_incluir_csv_file
        elif estado_contable == RcEstadoContable.RECLAMADO:
            parse_func = parse_rcv_compra_reclamado_csv_file
        elif estado_contable == RcEstadoContable.PENDIENTE:
            parse_func = parse_rcv_compra_pendiente_csv_file
        else:
            raise Exception(
                "Programming error. No handler for given 'estado_contable'.",
                estado_contable,
            )
    elif rcv_kind == RcvKind.VENTAS:
        if estado_contable is not None:
            raise ValueError("'estado_contable' must be None when 'rcv_kind' is 'VENTAS'.")
        parse_func = parse_rcv_venta_csv_file
    else:
        raise Exception("Programming error. No handler for given 'rcv_kind'.", rcv_kind)

    return parse_func


def parse_rcv_venta_csv_file(
    rut: Rut,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[RvDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RV ("Registro de Ventas") (CSV file).

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.

    schema_context = dict(
        emisor_rut=rut,
    )
    input_csv_row_schema = RcvVentaCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_docto'
        'Tipo Venta',
        'Rut cliente',  # 'receptor_rut'
        'Razon Social',  # 'receptor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Fecha Acuse Recibo',  # 'fecha_acuse_dt'
        'Fecha Reclamo',  # 'fecha_reclamo_dt'
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

    # note: mypy will complain about returned dataclass type mismatch (and it is right to do so)
    #   but we know from logic which subclass of 'RcvDetalleEntry' will be yielded.
    yield from _parse_rcv_csv_file(  # type: ignore
        input_csv_row_schema,
        expected_input_field_names,
        fields_to_remove_names,
        input_file_path,
        n_rows_offset,
        max_n_rows,
    )


def parse_rcv_compra_registro_csv_file(
    rut: Rut,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[RcRegistroDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC ("Registro de Compras") / "registro" (CSV file).

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.

    schema_context = dict(
        receptor_rut=rut,
    )
    input_csv_row_schema = RcvCompraRegistroCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_docto'
        'Tipo Compra',
        'RUT Proveedor',  # 'emisor_rut'
        'Razon Social',  # 'emisor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Fecha Acuse',  # 'fecha_acuse_dt'
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Total',  # 'monto_total'
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

    fields_to_remove_names = (
        'Nro',
        'Tipo Compra',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
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

    # note: mypy will complain about returned dataclass type mismatch (and it is right to do so)
    #   but we know from logic which subclass of 'RcvDetalleEntry' will be yielded.
    yield from _parse_rcv_csv_file(  # type: ignore
        input_csv_row_schema,
        expected_input_field_names,
        fields_to_remove_names,
        input_file_path,
        n_rows_offset,
        max_n_rows,
    )


def parse_rcv_compra_no_incluir_csv_file(
    rut: Rut,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[RcNoIncluirDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC ("Registro de Compras") / "no incluir" (CSV file).

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.

    schema_context = dict(
        receptor_rut=rut,
    )
    input_csv_row_schema = RcvCompraNoIncluirCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_docto'
        'Tipo Compra',
        'RUT Proveedor',  # 'emisor_rut'
        'Razon Social',  # 'emisor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Fecha Acuse',  # 'fecha_acuse_dt'
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Total',  # 'monto_total'
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    fields_to_remove_names = (
        'Nro',
        'Tipo Compra',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    # note: mypy will complain about returned dataclass type mismatch (and it is right to do so)
    #   but we know from logic which subclass of 'RcvDetalleEntry' will be yielded.
    yield from _parse_rcv_csv_file(  # type: ignore
        input_csv_row_schema,
        expected_input_field_names,
        fields_to_remove_names,
        input_file_path,
        n_rows_offset,
        max_n_rows,
    )


def parse_rcv_compra_reclamado_csv_file(
    rut: Rut,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[RcReclamadoDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC ("Registro de Compras") / "reclamado" (CSV file).

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.

    schema_context = dict(
        receptor_rut=rut,
    )
    input_csv_row_schema = RcvCompraReclamadoCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_docto'
        'Tipo Compra',
        'RUT Proveedor',  # 'emisor_rut'
        'Razon Social',  # 'emisor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Fecha Reclamo',  # 'fecha_reclamo_dt'
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Total',  # 'monto_total'
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    fields_to_remove_names = (
        'Nro',
        'Tipo Compra',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    # note: mypy will complain about returned dataclass type mismatch (and it is right to do so)
    #   but we know from logic which subclass of 'RcvDetalleEntry' will be yielded.
    yield from _parse_rcv_csv_file(  # type: ignore
        input_csv_row_schema,
        expected_input_field_names,
        fields_to_remove_names,
        input_file_path,
        n_rows_offset,
        max_n_rows,
    )


def parse_rcv_compra_pendiente_csv_file(
    rut: Rut,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Iterable[Tuple[Optional[RcPendienteDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC ("Registro de Compras") / "pendiente" (CSV file).

    """
    # warning: this looks like it would be executed before the iteration begins but it is not.

    schema_context = dict(
        receptor_rut=rut,
    )
    input_csv_row_schema = RcvCompraPendienteCsvRowSchema(context=schema_context)

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_docto'
        'Tipo Compra',
        'RUT Proveedor',  # 'emisor_rut'
        'Razon Social',  # 'emisor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Total',  # 'monto_total'
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    fields_to_remove_names = (
        'Nro',
        'Tipo Compra',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    # note: mypy will complain about returned dataclass type mismatch (and it is right to do so)
    #   but we know from logic which subclass of 'RcvDetalleEntry' will be yielded.
    yield from _parse_rcv_csv_file(  # type: ignore
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

    def to_detalle_entry(self, data: dict) -> RcvDetalleEntry:
        raise NotImplementedError


class RcvVentaCsvRowSchema(_RcvCsvRowSchemaBase):

    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_ACUSE_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_RECLAMO_DT_TZ = SII_OFFICIAL_TZ

    class Meta:
        strict = True

    ###########################################################################
    # basic fields
    ###########################################################################

    tipo_docto = mm_fields.RcvTipoDoctoField(
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

    ###########################################################################
    # extra fields: not included in the returned struct
    ###########################################################################

    fecha_recepcion_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        load_from='Fecha Recepcion',
    )
    fecha_acuse_dt = marshmallow.fields.DateTime(
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
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ
        )
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        if 'fecha_acuse_dt' in data and data['fecha_acuse_dt']:
            data['fecha_acuse_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_acuse_dt'], tz=self.FIELD_FECHA_ACUSE_DT_TZ
            )
        if 'fecha_reclamo_dt' in data and data['fecha_reclamo_dt']:
            data['fecha_reclamo_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_reclamo_dt'], tz=self.FIELD_FECHA_RECLAMO_DT_TZ
            )

        # Remove leading and trailing whitespace.
        data['receptor_razon_social'] = data['receptor_razon_social'].strip()

        return data

    def to_detalle_entry(self, data: dict) -> RvDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            tipo_docto = data['tipo_docto']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            receptor_razon_social: str = data['receptor_razon_social']  # type: ignore
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']  # type: ignore
            fecha_acuse_dt: Optional[datetime] = data['fecha_acuse_dt']  # type: ignore
            fecha_reclamo_dt: Optional[datetime] = data['fecha_reclamo_dt']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RvDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                receptor_razon_social=receptor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                fecha_acuse_dt=fecha_acuse_dt,
                fecha_reclamo_dt=fecha_reclamo_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraRegistroCsvRowSchema(_RcvCsvRowSchemaBase):

    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_ACUSE_DT_TZ = SII_OFFICIAL_TZ

    class Meta:
        strict = True

    ###########################################################################
    # basic fields
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
        load_from='RUT Proveedor',
    )
    tipo_docto = mm_fields.RcvTipoDoctoField(
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
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto Total',
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
        load_from='Razon Social',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    receptor_rut = mm_fields.RutField(
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
    fecha_acuse_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        allow_none=True,
        load_from='Fecha Acuse',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])

        # Fix missing/default values.
        if 'Fecha Acuse' in in_data:
            if in_data['Fecha Acuse'] == '':
                in_data['Fecha Acuse'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ
        )
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        if data['fecha_acuse_dt']:
            data['fecha_acuse_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_acuse_dt'], tz=self.FIELD_FECHA_ACUSE_DT_TZ
            )

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        # Remove leading and trailing whitespace.
        data['emisor_razon_social'] = data['emisor_razon_social'].strip()

        return data

    def to_detalle_entry(self, data: dict) -> RcRegistroDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            tipo_docto = data['tipo_docto']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']  # type: ignore
            fecha_acuse_dt: Optional[datetime] = data['fecha_acuse_dt']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcRegistroDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                fecha_acuse_dt=fecha_acuse_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraNoIncluirCsvRowSchema(RcvCompraRegistroCsvRowSchema):
    def to_detalle_entry(self, data: dict) -> RcNoIncluirDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            tipo_docto = data['tipo_docto']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']  # type: ignore
            fecha_acuse_dt: Optional[datetime] = data['fecha_acuse_dt']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcNoIncluirDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                fecha_acuse_dt=fecha_acuse_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraReclamadoCsvRowSchema(_RcvCsvRowSchemaBase):

    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_RECLAMO_DT_TZ = SII_OFFICIAL_TZ

    class Meta:
        strict = True

    ###########################################################################
    # basic fields
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
        load_from='RUT Proveedor',
    )
    tipo_docto = mm_fields.RcvTipoDoctoField(
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
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto Total',
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
        load_from='Razon Social',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    receptor_rut = mm_fields.RutField(
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
    fecha_reclamo_dt = marshmallow.fields.DateTime(
        # note: for some reason the rows with 'tipo_docto' equal to
        #   '<RcvTipoDocto.NOTA_CREDITO_ELECTRONICA: 61>' (and maybe others as well) do not
        #   have this field set (always? we do not know).
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
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])

        # Fix missing/default values.
        # note: for some reason the rows with 'tipo_docto' equal to
        #   '<RcvTipoDocto.NOTA_CREDITO_ELECTRONICA: 61>' (and maybe others as well) do not
        #   have this field set (always? we do not know).
        if 'Fecha Reclamo' in in_data:
            if in_data['Fecha Reclamo'] == '' or 'null' in in_data['Fecha Reclamo']:
                in_data['Fecha Reclamo'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ
        )
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        if data['fecha_reclamo_dt']:
            data['fecha_reclamo_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_reclamo_dt'], tz=self.FIELD_FECHA_RECLAMO_DT_TZ
            )

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        # Remove leading and trailing whitespace.
        data['emisor_razon_social'] = data['emisor_razon_social'].strip()

        return data

    def to_detalle_entry(self, data: dict) -> RcReclamadoDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            tipo_docto = data['tipo_docto']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']  # type: ignore
            fecha_reclamo_dt: Optional[datetime] = data['fecha_reclamo_dt']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcReclamadoDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                fecha_reclamo_dt=fecha_reclamo_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraPendienteCsvRowSchema(_RcvCsvRowSchemaBase):

    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_ACUSE_DT_TZ = SII_OFFICIAL_TZ

    class Meta:
        strict = True

    ###########################################################################
    # basic fields
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
        load_from='RUT Proveedor',
    )
    tipo_docto = mm_fields.RcvTipoDoctoField(
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
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto Total',
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
        load_from='Razon Social',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    receptor_rut = mm_fields.RutField(
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

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])

        # Fix missing/default values.
        if 'Fecha Acuse' in in_data:
            if in_data['Fecha Acuse'] == '':
                in_data['Fecha Acuse'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ
        )
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        # Remove leading and trailing whitespace.
        data['emisor_razon_social'] = data['emisor_razon_social'].strip()

        return data

    def to_detalle_entry(self, data: dict) -> RcPendienteDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            tipo_docto = data['tipo_docto']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcPendienteDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


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
) -> Iterable[Tuple[Optional[RcvDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC or RV (CSV file).

    Common implementation for the different alternatives that depend on the
    kind of RC and RV.

    """
    for field_to_remove_name in fields_to_remove_names:
        if field_to_remove_name not in expected_input_field_names:
            raise Exception(
                "Programming error: field to remove is not one of the expected ones.",
                field_to_remove_name,
            )

    _CSV_ROW_DICT_EXTRA_FIELDS_KEY = '_extra_csv_fields_data'

    fields_to_remove_names += (_CSV_ROW_DICT_EXTRA_FIELDS_KEY,)  # type: ignore

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
            entry: Optional[RcvDetalleEntry] = None
            row_errors: Dict[str, object] = {}
            conversion_error = None

            if not validation_errors:
                try:
                    entry = input_csv_row_schema.to_detalle_entry(deserialized_row_data)
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
