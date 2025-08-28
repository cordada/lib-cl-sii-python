"""
Parse RCV files (CSV)
=====================


"""

import csv
import logging
from datetime import date, datetime
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple, TypeVar

import marshmallow

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.extras import mm_fields
from cl_sii.libs import csv_utils, mm_utils, rows_processing, tz_utils
from cl_sii.rut import Rut
from .constants import RcEstadoContable, RcTipoCompra, RcvKind, RvTipoVenta
from .data_models import (
    RcDetalleEntry,
    RcNoIncluirDetalleEntry,
    RcPendienteDetalleEntry,
    RcReclamadoDetalleEntry,
    RcRegistroDetalleEntry,
    RcvDetalleEntry,
    RvDetalleEntry,
)


logger = logging.getLogger(__name__)

RcvDetalleEntryType = TypeVar('RcvDetalleEntryType', bound=RcvDetalleEntry)

RcvCsvFileParserType = Callable[
    [Rut, str, int, Optional[int]],
    Iterable[
        Tuple[
            Optional[RcvDetalleEntryType],
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
    max_n_rows: Optional[int] = None,
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

    fields_to_remove_names = ('Nro',)

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
    max_n_rows: Optional[int] = None,
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

    fields_to_remove_names = ('Nro',)

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
    max_n_rows: Optional[int] = None,
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

    fields_to_remove_names = ('Nro',)

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
    max_n_rows: Optional[int] = None,
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

    fields_to_remove_names = ('Nro',)

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
    max_n_rows: Optional[int] = None,
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

    fields_to_remove_names = ('Nro',)

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
    def validate_schema(self, data: dict, original_data: dict, **kwargs: Any) -> None:
        mm_utils.validate_no_unexpected_input_fields(self, data, original_data)

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    def to_detalle_entry(self, data: dict) -> RcvDetalleEntry:
        raise NotImplementedError

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        # Get required field names from the schema
        required_fields = {
            field.data_key
            for name, field in self.fields.items()
            if field.required and field.allow_none is False
        }
        # Remove only required fields that are None or empty string
        for field in required_fields:
            if field in in_data.keys() and (
                in_data[field] is None or str(in_data[field]).strip() == ''
            ):
                del in_data[field]

        for name, field_item in self.fields.items():
            data_key = field_item.data_key
            if data_key is not None and data_key in in_data.keys():
                if in_data[data_key] == '' or (
                    isinstance(
                        field_item,
                        (
                            marshmallow.fields.Integer,
                            marshmallow.fields.Decimal,
                            marshmallow.fields.Float,
                            marshmallow.fields.Date,
                            marshmallow.fields.DateTime,
                            mm_fields.RutField,
                        ),
                    )
                    and in_data[data_key] == '-'
                ):
                    in_data[data_key] = None
        return in_data


class RcvVentaCsvRowSchema(_RcvCsvRowSchemaBase):
    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_ACUSE_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_RECLAMO_DT_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # basic fields
    ###########################################################################

    tipo_docto = mm_fields.RcvTipoDoctoField(
        required=True,
        data_key='Tipo Doc',
    )
    tipo_venta = marshmallow.fields.Enum(
        RvTipoVenta,
        required=True,
        data_key='Tipo Venta',
    )
    receptor_rut = mm_fields.RutField(
        required=True,
        data_key='Rut cliente',
    )
    receptor_razon_social = marshmallow.fields.String(
        required=True,
        data_key='Razon Social',
    )
    folio = marshmallow.fields.Integer(
        required=True,
        data_key='Folio',
    )
    fecha_emision_date = mm_utils.CustomMarshmallowDateField(
        format='%d/%m/%Y',  # e.g. '22/10/2018'
        required=True,
        data_key='Fecha Docto',
    )
    fecha_acuse_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=False,
        allow_none=True,
        data_key='Fecha Acuse Recibo',
    )
    fecha_recepcion_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        data_key='Fecha Recepcion',
    )
    fecha_reclamo_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=False,
        allow_none=True,
        data_key='Fecha Reclamo',
    )
    monto_exento = marshmallow.fields.Integer(
        required=True,
        data_key='Monto Exento',
    )
    monto_neto = marshmallow.fields.Integer(
        required=True,
        data_key='Monto Neto',
    )
    monto_iva = marshmallow.fields.Integer(
        required=True,
        data_key='Monto IVA',
    )
    monto_total = marshmallow.fields.Integer(
        required=True,
        data_key='Monto total',
    )
    iva_retenido_total = marshmallow.fields.Integer(
        required=True,
        data_key='IVA Retenido Total',
    )
    iva_retenido_parcial = marshmallow.fields.Integer(
        required=True,
        data_key='IVA Retenido Parcial',
    )
    iva_no_retenido = marshmallow.fields.Integer(
        required=True,
        data_key='IVA no retenido',
    )
    iva_propio = marshmallow.fields.Integer(
        required=True,
        data_key='IVA propio',
    )
    iva_terceros = marshmallow.fields.Integer(
        required=True,
        data_key='IVA Terceros',
    )
    liquidacion_factura_emisor_rut = mm_fields.RutField(
        required=False,
        allow_none=True,
        data_key='RUT Emisor Liquid. Factura',
    )
    neto_comision_liquidacion_factura = marshmallow.fields.Integer(
        required=True,
        data_key='Neto Comision Liquid. Factura',
    )
    exento_comision_liquidacion_factura = marshmallow.fields.Integer(
        required=True,
        data_key='Exento Comision Liquid. Factura',
    )
    iva_comision_liquidacion_factura = marshmallow.fields.Integer(
        required=True,
        data_key='IVA Comision Liquid. Factura',
    )
    iva_fuera_de_plazo = marshmallow.fields.Integer(
        required=True,
        data_key='IVA fuera de plazo',
    )
    tipo_documento_referencia = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Tipo Docto. Referencia',
    )
    folio_documento_referencia = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Folio Docto. Referencia',
    )
    num_ident_receptor_extranjero = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Num. Ident. Receptor Extranjero',
    )
    nacionalidad_receptor_extranjero = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Nacionalidad Receptor Extranjero',
    )
    credito_empresa_constructora = marshmallow.fields.Integer(
        required=True,
        data_key='Credito empresa constructora',
    )
    impuesto_zona_franca_ley_18211 = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Impto. Zona Franca (Ley 18211)',
    )
    garantia_dep_envases = marshmallow.fields.Integer(
        required=True,
        data_key='Garantia Dep. Envases',
    )
    indicador_venta_sin_costo = marshmallow.fields.Integer(
        required=True,
        data_key='Indicador Venta sin Costo',
    )
    indicador_servicio_periodico = marshmallow.fields.Integer(
        required=True,
        data_key='Indicador Servicio Periodico',
    )
    monto_no_facturable = marshmallow.fields.Integer(
        required=True,
        data_key='Monto No facturable',
    )
    total_monto_periodo = marshmallow.fields.Integer(
        required=True,
        data_key='Total Monto Periodo',
    )
    venta_pasajes_transporte_nacional = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Venta Pasajes Transporte Nacional',
    )
    venta_pasajes_transporte_internacional = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Venta Pasajes Transporte Internacional',
    )
    numero_interno = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Numero Interno',
    )
    codigo_sucursal = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Codigo Sucursal',
    )
    nce_o_nde_sobre_factura_de_compra = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='NCE o NDE sobre Fact. de Compra',
    )
    codigo_otro_imp = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Codigo Otro Imp.',
    )
    valor_otro_imp = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Valor Otro Imp.',
    )
    tasa_otro_imp = marshmallow.fields.Decimal(
        required=False,
        allow_none=True,
        data_key='Tasa Otro Imp.',
    )
    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        in_data = super().preprocess(in_data, **kwargs)
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('emisor_rut', self.context['emisor_rut'])

        # Set tipo_venta from string to enum value.
        if 'Tipo Venta' in in_data:
            if in_data['Tipo Venta'] == 'Del Giro':
                in_data['Tipo Venta'] = RvTipoVenta.DEL_GIRO.value
            elif in_data['Tipo Venta'] == 'Bienes Raíces':
                in_data['Tipo Venta'] = RvTipoVenta.BIENES_RAICES.value
            elif in_data['Tipo Venta'] == 'Activo Fijo':
                in_data['Tipo Venta'] = RvTipoVenta.ACTIVO_FIJO.value

        # Fix missing/default values.
        if 'Fecha Acuse Recibo' in in_data:
            if in_data['Fecha Acuse Recibo'] == '':
                in_data['Fecha Acuse Recibo'] = None
        if 'Fecha Reclamo' in in_data:
            if in_data['Fecha Reclamo'] == '':
                in_data['Fecha Reclamo'] = None
        if 'RUT Emisor Liquid. Factura' in in_data:
            if in_data['RUT Emisor Liquid. Factura'] in (None, '', '-'):
                in_data['RUT Emisor Liquid. Factura'] = None
        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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
            emisor_rut: Rut = data['emisor_rut']
            tipo_docto = data['tipo_docto']
            tipo_venta = data['tipo_venta']
            folio: int = data['folio']
            fecha_emision_date: date = data['fecha_emision_date']
            receptor_rut: Rut = data['receptor_rut']
            receptor_razon_social: str = data['receptor_razon_social']
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']
            fecha_acuse_dt: Optional[datetime] = data['fecha_acuse_dt']
            fecha_reclamo_dt: Optional[datetime] = data['fecha_reclamo_dt']
            monto_exento = data['monto_exento']
            monto_neto = data['monto_neto']
            monto_iva = data['monto_iva']
            monto_total: int = data['monto_total']
            iva_retenido_total = data['iva_retenido_total']
            iva_retenido_parcial = data['iva_retenido_parcial']
            iva_no_retenido = data['iva_no_retenido']
            iva_propio = data['iva_propio']
            iva_terceros = data['iva_terceros']
            liquidacion_factura_emisor_rut = data['liquidacion_factura_emisor_rut']
            neto_comision_liquidacion_factura = data['neto_comision_liquidacion_factura']
            exento_comision_liquidacion_factura = data['exento_comision_liquidacion_factura']
            iva_comision_liquidacion_factura = data['iva_comision_liquidacion_factura']
            iva_fuera_de_plazo = data['iva_fuera_de_plazo']
            tipo_documento_referencia = data['tipo_documento_referencia']
            folio_documento_referencia = data['folio_documento_referencia']
            num_ident_receptor_extranjero = data['num_ident_receptor_extranjero']
            nacionalidad_receptor_extranjero = data['nacionalidad_receptor_extranjero']
            credito_empresa_constructora = data['credito_empresa_constructora']
            impuesto_zona_franca_ley_18211 = data['impuesto_zona_franca_ley_18211']
            garantia_dep_envases = data['garantia_dep_envases']
            indicador_venta_sin_costo = data['indicador_venta_sin_costo']
            indicador_servicio_periodico = data['indicador_servicio_periodico']
            monto_no_facturable = data['monto_no_facturable']
            total_monto_periodo = data['total_monto_periodo']
            venta_pasajes_transporte_nacional = data['venta_pasajes_transporte_nacional']
            venta_pasajes_transporte_internacional = data['venta_pasajes_transporte_internacional']
            numero_interno = data['numero_interno']
            codigo_sucursal = data['codigo_sucursal']
            nce_o_nde_sobre_factura_de_compra = data['nce_o_nde_sobre_factura_de_compra']
            codigo_otro_imp = data['codigo_otro_imp']
            valor_otro_imp = data['valor_otro_imp']
            tasa_otro_imp = data['tasa_otro_imp']
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RvDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                tipo_venta=tipo_venta,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                receptor_razon_social=receptor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                fecha_acuse_dt=fecha_acuse_dt,
                fecha_reclamo_dt=fecha_reclamo_dt,
                monto_exento=monto_exento,
                monto_neto=monto_neto,
                monto_iva=monto_iva,
                monto_total=monto_total,
                iva_retenido_total=iva_retenido_total,
                iva_retenido_parcial=iva_retenido_parcial,
                iva_no_retenido=iva_no_retenido,
                iva_propio=iva_propio,
                iva_terceros=iva_terceros,
                liquidacion_factura_emisor_rut=liquidacion_factura_emisor_rut,
                neto_comision_liquidacion_factura=neto_comision_liquidacion_factura,
                exento_comision_liquidacion_factura=exento_comision_liquidacion_factura,
                iva_comision_liquidacion_factura=iva_comision_liquidacion_factura,
                iva_fuera_de_plazo=iva_fuera_de_plazo,
                tipo_documento_referencia=tipo_documento_referencia,
                folio_documento_referencia=folio_documento_referencia,
                num_ident_receptor_extranjero=num_ident_receptor_extranjero,
                nacionalidad_receptor_extranjero=nacionalidad_receptor_extranjero,
                credito_empresa_constructora=credito_empresa_constructora,
                impuesto_zona_franca_ley_18211=impuesto_zona_franca_ley_18211,
                garantia_dep_envases=garantia_dep_envases,
                indicador_venta_sin_costo=indicador_venta_sin_costo,
                indicador_servicio_periodico=indicador_servicio_periodico,
                monto_no_facturable=monto_no_facturable,
                total_monto_periodo=total_monto_periodo,
                venta_pasajes_transporte_nacional=venta_pasajes_transporte_nacional,
                venta_pasajes_transporte_internacional=venta_pasajes_transporte_internacional,
                numero_interno=numero_interno,
                codigo_sucursal=codigo_sucursal,
                nce_o_nde_sobre_factura_de_compra=nce_o_nde_sobre_factura_de_compra,
                codigo_otro_imp=codigo_otro_imp,
                valor_otro_imp=valor_otro_imp,
                tasa_otro_imp=tasa_otro_imp,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraCsvRowSchema(_RcvCsvRowSchemaBase):
    FIELD_FECHA_RECEPCION_DT_TZ = SII_OFFICIAL_TZ
    FIELD_FECHA_ACUSE_DT_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # Fields
    ###########################################################################

    emisor_rut = mm_fields.RutField(
        required=True,
        data_key='RUT Proveedor',
    )
    tipo_docto = mm_fields.RcvTipoDoctoField(
        required=True,
        data_key='Tipo Doc',
    )
    tipo_compra = marshmallow.fields.Enum(
        RcTipoCompra,
        required=True,
        data_key='Tipo Compra',
    )
    folio = marshmallow.fields.Integer(
        required=True,
        data_key='Folio',
    )
    fecha_emision_date = mm_utils.CustomMarshmallowDateField(
        format='%d/%m/%Y',  # e.g. '22/10/2018'
        required=True,
        data_key='Fecha Docto',
    )
    monto_total = marshmallow.fields.Integer(
        required=True,
        data_key='Monto Total',
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
        data_key='Razon Social',
    )
    receptor_rut = mm_fields.RutField(
        required=True,
    )
    fecha_recepcion_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',
        required=True,
        data_key='Fecha Recepcion',
    )
    monto_exento = marshmallow.fields.Integer(
        required=True,
        data_key='Monto Exento',
    )
    monto_neto = marshmallow.fields.Integer(
        required=True,
        data_key='Monto Neto',
    )
    monto_iva_recuperable = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Monto IVA Recuperable',
    )
    monto_iva_no_recuperable = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Monto Iva No Recuperable',
    )
    codigo_iva_no_rec = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Codigo IVA No Rec.',
    )
    monto_neto_activo_fijo = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Monto Neto Activo Fijo',
    )
    iva_activo_fijo = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='IVA Activo Fijo',
    )
    iva_uso_comun = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='IVA uso Comun',
    )
    impto_sin_derecho_a_credito = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Impto. Sin Derecho a Credito',
    )
    iva_no_retenido = marshmallow.fields.Integer(
        required=True,
        allow_none=True,
        data_key='IVA No Retenido',
    )
    nce_o_nde_sobre_factura_de_compra = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='NCE o NDE sobre Fact. de Compra',
    )
    codigo_otro_impuesto = marshmallow.fields.String(
        required=False,
        allow_none=True,
        data_key='Codigo Otro Impuesto',
    )
    valor_otro_impuesto = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Valor Otro Impuesto',
    )
    tasa_otro_impuesto = marshmallow.fields.Decimal(
        required=False,
        allow_none=True,
        data_key='Tasa Otro Impuesto',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    receptor_rut = mm_fields.RutField(
        required=True,
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        in_data = super().preprocess(in_data, **kwargs)
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])

        # Set tipo_compra from string to enum value.
        if 'Tipo Compra' in in_data:
            if in_data['Tipo Compra'] == 'Del Giro':
                in_data['Tipo Compra'] = RcTipoCompra.DEL_GIRO.value
            elif in_data['Tipo Compra'] == 'Supermercados':
                in_data['Tipo Compra'] = RcTipoCompra.SUPERMERCADOS.value
            elif in_data['Tipo Compra'] == 'Bienes Raíces':
                in_data['Tipo Compra'] = RcTipoCompra.BIENES_RAICES.value
            elif in_data['Tipo Compra'] == 'Activo Fijo':
                in_data['Tipo Compra'] = RcTipoCompra.ACTIVO_FIJO.value
            elif in_data['Tipo Compra'] == 'IVA Uso Común':
                in_data['Tipo Compra'] = RcTipoCompra.IVA_USO_COMUN.value
            elif in_data['Tipo Compra'] == 'IVA no Recuperable':
                in_data['Tipo Compra'] = RcTipoCompra.IVA_NO_RECUPERABLE.value
            elif in_data['Tipo Compra'] == 'No Corresp. Incluir':
                in_data['Tipo Compra'] = RcTipoCompra.NO_CORRESPONDE_INCLUIR.value

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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

    def to_detalle_entry(self, data: dict) -> RcDetalleEntry:
        raise NotImplementedError("Set Entry subclass in derived class.")


class RcvCompraRegistroCsvRowSchema(RcvCompraCsvRowSchema):
    ###########################################################################
    # Fields
    ###########################################################################

    fecha_acuse_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        allow_none=True,
        data_key='Fecha Acuse',
    )
    tabacos_puros = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Tabacos Puros',
    )
    tabacos_cigarrillos = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Tabacos Cigarrillos',
    )
    tabacos_elaborados = marshmallow.fields.Integer(
        required=False,
        allow_none=True,
        data_key='Tabacos Elaborados',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        in_data = super().preprocess(in_data, **kwargs)
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Fix missing/default values.
        if 'Fecha Acuse' in in_data:
            if in_data['Fecha Acuse'] == '':
                in_data['Fecha Acuse'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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
            emisor_rut: Rut = data['emisor_rut']
            tipo_docto = data['tipo_docto']
            folio: int = data['folio']
            tipo_compra: str = data['tipo_compra']
            fecha_emision_date: date = data['fecha_emision_date']
            receptor_rut: Rut = data['receptor_rut']
            monto_total: int = data['monto_total']
            emisor_razon_social: str = data['emisor_razon_social']
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']
            monto_exento: int = data['monto_exento']
            monto_neto: int = data['monto_neto']
            monto_iva_recuperable: Optional[int] = data.get('monto_iva_recuperable')
            monto_iva_no_recuperable: Optional[int] = data.get('monto_iva_no_recuperable')
            codigo_iva_no_rec: Optional[str] = data.get('codigo_iva_no_rec')
            monto_neto_activo_fijo: Optional[int] = data.get('monto_neto_activo_fijo')
            iva_activo_fijo: Optional[int] = data.get('iva_activo_fijo')
            iva_uso_comun: Optional[int] = data.get('iva_uso_comun')
            impto_sin_derecho_a_credito: Optional[int] = data.get('impto_sin_derecho_a_credito')
            iva_no_retenido: int = data['iva_no_retenido']
            nce_o_nde_sobre_factura_de_compra: Optional[str] = data.get(
                'nce_o_nde_sobre_factura_de_compra'
            )
            codigo_otro_impuesto: Optional[str] = data.get('codigo_otro_impuesto')
            valor_otro_impuesto: Optional[int] = data.get('valor_otro_impuesto')
            tasa_otro_impuesto: Optional[float] = data.get('tasa_otro_impuesto')
            fecha_acuse_dt: Optional[datetime] = data.get('fecha_acuse_dt')
            tabacos_puros: Optional[int] = data.get('tabacos_puros')
            tabacos_cigarrillos: Optional[int] = data.get('tabacos_cigarrillos')
            tabacos_elaborados: Optional[int] = data.get('tabacos_elaborados')
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcRegistroDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                tipo_compra=tipo_compra,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                monto_exento=monto_exento,
                monto_neto=monto_neto,
                monto_iva_recuperable=monto_iva_recuperable,
                monto_iva_no_recuperable=monto_iva_no_recuperable,
                codigo_iva_no_rec=codigo_iva_no_rec,
                monto_neto_activo_fijo=monto_neto_activo_fijo,
                iva_activo_fijo=iva_activo_fijo,
                iva_uso_comun=iva_uso_comun,
                impto_sin_derecho_a_credito=impto_sin_derecho_a_credito,
                iva_no_retenido=iva_no_retenido,
                nce_o_nde_sobre_factura_de_compra=nce_o_nde_sobre_factura_de_compra,
                codigo_otro_impuesto=codigo_otro_impuesto,
                valor_otro_impuesto=valor_otro_impuesto,
                tasa_otro_impuesto=tasa_otro_impuesto,
                fecha_acuse_dt=fecha_acuse_dt,
                tabacos_puros=tabacos_puros,
                tabacos_cigarrillos=tabacos_cigarrillos,
                tabacos_elaborados=tabacos_elaborados,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraNoIncluirCsvRowSchema(RcvCompraCsvRowSchema):
    ###########################################################################
    # Fields
    ###########################################################################

    fecha_acuse_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        allow_none=True,
        data_key='Fecha Acuse',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        in_data = super().preprocess(in_data, **kwargs)
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Fix missing/default values.
        if 'Fecha Acuse' in in_data:
            if in_data['Fecha Acuse'] == '':
                in_data['Fecha Acuse'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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

    def to_detalle_entry(self, data: dict) -> RcNoIncluirDetalleEntry:
        try:
            emisor_rut: Rut = data['emisor_rut']
            tipo_docto = data['tipo_docto']
            folio: int = data['folio']
            tipo_compra: str = data['tipo_compra']
            fecha_emision_date: date = data['fecha_emision_date']
            receptor_rut: Rut = data['receptor_rut']
            monto_total: int = data['monto_total']
            emisor_razon_social: str = data['emisor_razon_social']
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']
            monto_exento: int = data['monto_exento']
            monto_neto: int = data['monto_neto']
            monto_iva_recuperable: Optional[int] = data.get('monto_iva_recuperable')
            monto_iva_no_recuperable: Optional[int] = data.get('monto_iva_no_recuperable')
            codigo_iva_no_rec: Optional[str] = data.get('codigo_iva_no_rec')
            monto_neto_activo_fijo: Optional[int] = data.get('monto_neto_activo_fijo')
            iva_activo_fijo: Optional[int] = data.get('iva_activo_fijo')
            iva_uso_comun: Optional[int] = data.get('iva_uso_comun')
            impto_sin_derecho_a_credito: Optional[int] = data.get('impto_sin_derecho_a_credito')
            iva_no_retenido: int = data['iva_no_retenido']
            nce_o_nde_sobre_factura_de_compra: Optional[str] = data.get(
                'nce_o_nde_sobre_factura_de_compra'
            )
            codigo_otro_impuesto: Optional[str] = data.get('codigo_otro_impuesto')
            valor_otro_impuesto: Optional[int] = data.get('valor_otro_impuesto')
            tasa_otro_impuesto: Optional[float] = data.get('tasa_otro_impuesto')
            fecha_acuse_dt: Optional[datetime] = data.get('fecha_acuse_dt')
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcNoIncluirDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                tipo_compra=tipo_compra,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                monto_exento=monto_exento,
                monto_neto=monto_neto,
                monto_iva_recuperable=monto_iva_recuperable,
                monto_iva_no_recuperable=monto_iva_no_recuperable,
                codigo_iva_no_rec=codigo_iva_no_rec,
                monto_neto_activo_fijo=monto_neto_activo_fijo,
                iva_activo_fijo=iva_activo_fijo,
                iva_uso_comun=iva_uso_comun,
                impto_sin_derecho_a_credito=impto_sin_derecho_a_credito,
                iva_no_retenido=iva_no_retenido,
                nce_o_nde_sobre_factura_de_compra=nce_o_nde_sobre_factura_de_compra,
                codigo_otro_impuesto=codigo_otro_impuesto,
                valor_otro_impuesto=valor_otro_impuesto,
                tasa_otro_impuesto=tasa_otro_impuesto,
                fecha_acuse_dt=fecha_acuse_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraReclamadoCsvRowSchema(RcvCompraCsvRowSchema):
    FIELD_FECHA_RECLAMO_DT_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # extra fields: not included in the returned struct
    ###########################################################################

    fecha_reclamo_dt = marshmallow.fields.DateTime(
        # note: for some reason the rows with 'tipo_docto' equal to
        #   '<RcvTipoDocto.NOTA_CREDITO_ELECTRONICA: 61>' (and maybe others as well) do not
        #   have this field set (always? we do not know).
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=False,
        allow_none=True,
        data_key='Fecha Reclamo',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict, **kwargs: Any) -> dict:
        in_data = super().preprocess(in_data, **kwargs)

        # Fix missing/default values.
        # note: for some reason the rows with 'tipo_docto' equal to
        #   '<RcvTipoDocto.NOTA_CREDITO_ELECTRONICA: 61>' (and maybe others as well) do not
        #   have this field set (always? we do not know).
        if 'Fecha Reclamo' in in_data:
            if in_data['Fecha Reclamo'] == '' or 'null' in in_data['Fecha Reclamo']:
                in_data['Fecha Reclamo'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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
            emisor_rut: Rut = data['emisor_rut']
            tipo_docto = data['tipo_docto']
            folio: int = data['folio']
            tipo_compra: str = data['tipo_compra']
            fecha_emision_date: date = data['fecha_emision_date']
            receptor_rut: Rut = data['receptor_rut']
            monto_total: int = data['monto_total']
            emisor_razon_social: str = data['emisor_razon_social']
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']
            monto_exento: int = data['monto_exento']
            monto_neto: int = data['monto_neto']
            monto_iva_recuperable: Optional[int] = data.get('monto_iva_recuperable')
            monto_iva_no_recuperable: Optional[int] = data.get('monto_iva_no_recuperable')
            codigo_iva_no_rec: Optional[str] = data.get('codigo_iva_no_rec')
            monto_neto_activo_fijo: Optional[int] = data.get('monto_neto_activo_fijo')
            iva_activo_fijo: Optional[int] = data.get('iva_activo_fijo')
            iva_uso_comun: Optional[int] = data.get('iva_uso_comun')
            impto_sin_derecho_a_credito: Optional[int] = data.get('impto_sin_derecho_a_credito')
            iva_no_retenido: int = data['iva_no_retenido']
            nce_o_nde_sobre_factura_de_compra: Optional[str] = data.get(
                'nce_o_nde_sobre_factura_de_compra'
            )
            codigo_otro_impuesto: Optional[str] = data.get('codigo_otro_impuesto')
            valor_otro_impuesto: Optional[int] = data.get('valor_otro_impuesto')
            tasa_otro_impuesto: Optional[float] = data.get('tasa_otro_impuesto')
            fecha_reclamo_dt: Optional[datetime] = data.get('fecha_reclamo_dt')
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcReclamadoDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                tipo_compra=tipo_compra,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                monto_exento=monto_exento,
                monto_neto=monto_neto,
                monto_iva_recuperable=monto_iva_recuperable,
                monto_iva_no_recuperable=monto_iva_no_recuperable,
                codigo_iva_no_rec=codigo_iva_no_rec,
                monto_neto_activo_fijo=monto_neto_activo_fijo,
                iva_activo_fijo=iva_activo_fijo,
                iva_uso_comun=iva_uso_comun,
                impto_sin_derecho_a_credito=impto_sin_derecho_a_credito,
                iva_no_retenido=iva_no_retenido,
                nce_o_nde_sobre_factura_de_compra=nce_o_nde_sobre_factura_de_compra,
                codigo_otro_impuesto=codigo_otro_impuesto,
                valor_otro_impuesto=valor_otro_impuesto,
                tasa_otro_impuesto=tasa_otro_impuesto,
                fecha_reclamo_dt=fecha_reclamo_dt,
            )
        except (TypeError, ValueError):
            raise

        return detalle_entry


class RcvCompraPendienteCsvRowSchema(RcvCompraCsvRowSchema):
    @marshmallow.post_load
    def postprocess(self, data: dict, **kwargs: Any) -> dict:
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
            emisor_rut: Rut = data['emisor_rut']
            tipo_docto = data['tipo_docto']
            folio: int = data['folio']
            tipo_compra: str = data['tipo_compra']
            fecha_emision_date: date = data['fecha_emision_date']
            receptor_rut: Rut = data['receptor_rut']
            monto_total: int = data['monto_total']
            emisor_razon_social: str = data['emisor_razon_social']
            fecha_recepcion_dt: datetime = data['fecha_recepcion_dt']
            monto_exento: int = data['monto_exento']
            monto_neto: int = data['monto_neto']
            monto_iva_recuperable: Optional[int] = data.get('monto_iva_recuperable')
            monto_iva_no_recuperable: Optional[int] = data.get('monto_iva_no_recuperable')
            codigo_iva_no_rec: Optional[str] = data.get('codigo_iva_no_rec')
            monto_neto_activo_fijo: Optional[int] = data.get('monto_neto_activo_fijo')
            iva_activo_fijo: Optional[int] = data.get('iva_activo_fijo')
            iva_uso_comun: Optional[int] = data.get('iva_uso_comun')
            impto_sin_derecho_a_credito: Optional[int] = data.get('impto_sin_derecho_a_credito')
            iva_no_retenido: int = data['iva_no_retenido']
            nce_o_nde_sobre_factura_de_compra: Optional[str] = data.get(
                'nce_o_nde_sobre_factura_de_compra'
            )
            codigo_otro_impuesto: Optional[str] = data.get('codigo_otro_impuesto')
            valor_otro_impuesto: Optional[int] = data.get('valor_otro_impuesto')
            tasa_otro_impuesto: Optional[float] = data.get('tasa_otro_impuesto')
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            detalle_entry = RcPendienteDetalleEntry(
                emisor_rut=emisor_rut,
                tipo_docto=tipo_docto,
                folio=folio,
                tipo_compra=tipo_compra,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                fecha_recepcion_dt=fecha_recepcion_dt,
                monto_exento=monto_exento,
                monto_neto=monto_neto,
                monto_iva_recuperable=monto_iva_recuperable,
                monto_iva_no_recuperable=monto_iva_no_recuperable,
                codigo_iva_no_rec=codigo_iva_no_rec,
                monto_neto_activo_fijo=monto_neto_activo_fijo,
                iva_activo_fijo=iva_activo_fijo,
                iva_uso_comun=iva_uso_comun,
                impto_sin_derecho_a_credito=impto_sin_derecho_a_credito,
                iva_no_retenido=iva_no_retenido,
                nce_o_nde_sobre_factura_de_compra=nce_o_nde_sobre_factura_de_compra,
                codigo_otro_impuesto=codigo_otro_impuesto,
                valor_otro_impuesto=valor_otro_impuesto,
                tasa_otro_impuesto=tasa_otro_impuesto,
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
    max_n_rows: Optional[int] = None,
) -> Iterable[Tuple[Optional[RcvDetalleEntry], int, Dict[str, object], Dict[str, object]]]:
    """
    Parse entries from an RC or RV (CSV file).

    Common implementation for the different alternatives that depend on the
    kind of RC and RV.

    """
    for field_to_remove_name in fields_to_remove_names:
        if field_to_remove_name not in expected_input_field_names:
            raise Exception(
                "Programming error: field to remove is not one of the expected.",
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
                        "Deserialized row data conversion failed for row %d: %s",
                        row_ix,
                        conversion_error,
                        extra={'deserialized_row_data': deserialized_row_data},
                    )

            # Instead of empty dicts, lists, str, etc, we want to have None.
            if validation_errors:
                row_errors['validation'] = validation_errors
            if conversion_error:
                row_errors['conversion_errors'] = conversion_error

            yield entry, row_ix, row_data, row_errors
