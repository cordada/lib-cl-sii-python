"""
RCV data models
===============


"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import ClassVar, Optional

import pydantic
from typing_extensions import Self

import cl_sii.dte.data_models
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from .constants import RcEstadoContable, RcvKind, RcvTipoDocto


logger = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass(frozen=True)
class PeriodoTributario:
    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # fields
    ###########################################################################

    year: int
    month: int

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('year')
    @classmethod
    def validate_year(cls, v: object) -> object:
        if isinstance(v, int) and v < 1900:
            # 1900 si an arbitrary number but it more useful than checking not < 1.
            raise ValueError("Value is out of the valid range for 'year'.")
        return v

    @pydantic.field_validator('month')
    @classmethod
    def validate_month(cls, v: object) -> object:
        if isinstance(v, int):
            if v < 1 or v > 12:
                raise ValueError("Value is out of the valid range for 'month'.")
        return v

    ###########################################################################
    # dunder/magic methods
    ###########################################################################

    def __str__(self) -> str:
        # 'YYYY-MM' e.g. '2018-03'
        return f"{self.year}-{self.month:02d}"

    def __lt__(self, other: PeriodoTributario) -> bool:
        return self.as_date() < other.as_date()

    def __le__(self, other: PeriodoTributario) -> bool:
        return self.as_date() <= other.as_date()

    ###########################################################################
    # custom methods
    ###########################################################################

    @property
    def is_in_the_future(self) -> bool:
        return self.as_datetime() > tz_utils.get_now_tz_aware()

    @classmethod
    def from_date(cls, value: date) -> PeriodoTributario:
        return PeriodoTributario(year=value.year, month=value.month)

    @classmethod
    def from_datetime(cls, value: datetime) -> PeriodoTributario:
        value_naive = tz_utils.convert_tz_aware_dt_to_naive(value, cls.DATETIME_FIELDS_TZ)
        return cls.from_date(value_naive.date())

    def as_date(self) -> date:
        return date(self.year, self.month, day=1)

    def as_datetime(self) -> datetime:
        # note: timezone-aware
        return tz_utils.convert_naive_dt_to_tz_aware(
            datetime(self.year, self.month, day=1, hour=0, minute=0, second=0),
            self.DATETIME_FIELDS_TZ,
        )


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcvDetalleEntry:
    """
    Entry of the "detalle" of an RCV.
    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    RCV_KIND: ClassVar[Optional[RcvKind]] = None
    RC_ESTADO_CONTABLE: ClassVar[Optional[RcEstadoContable]] = None

    ###########################################################################
    # fields
    ###########################################################################

    emisor_rut: Rut
    """
    RUT of the "emisor" of the "documento".
    """

    tipo_docto: RcvTipoDocto
    """
    The kind of "documento".
    """

    folio: int
    """
    The sequential number of a "documento".
    """

    # TODO: docstring
    fecha_emision_date: date

    # TODO: docstring
    # TODO: can it be None? What happens for those "tipo docto" that do not have a receptor?
    receptor_rut: Rut

    monto_total: int
    """
    Total amount of the "documento".
    """

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_recepcion_dt: datetime

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('folio')
    @classmethod
    def validate_folio(cls, v: object) -> object:
        if isinstance(v, int):
            cl_sii.dte.data_models.validate_dte_folio(v)
        return v

    @pydantic.field_validator('fecha_recepcion_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.model_validator(mode='after')
    def validate_rcv_kind_is_consistent_with_rc_estado_contable(self) -> Self:
        rcv_kind = self.RCV_KIND
        rc_estado_contable = self.RC_ESTADO_CONTABLE

        if isinstance(rcv_kind, RcvKind):
            if rcv_kind == RcvKind.COMPRAS:
                if rc_estado_contable is None:
                    raise ValueError(
                        "'RC_ESTADO_CONTABLE' must not be None when 'RCV_KIND' is 'COMPRAS'."
                    )
            elif rcv_kind == RcvKind.VENTAS:
                if rc_estado_contable is not None:
                    raise ValueError(
                        "'RC_ESTADO_CONTABLE' must be None when 'RCV_KIND' is 'VENTAS'."
                    )

        return self

    @property
    def is_dte(self) -> bool:
        try:
            self.tipo_docto.as_tipo_dte()
        except ValueError:
            return False
        return True

    def as_dte_data_l2(self) -> cl_sii.dte.data_models.DteDataL2:
        try:
            tipo_dte = self.tipo_docto.as_tipo_dte()

            emisor_razon_social = getattr(self, 'emisor_razon_social', None)
            receptor_razon_social = getattr(self, 'receptor_razon_social', None)

            dte_data = cl_sii.dte.data_models.DteDataL2(
                emisor_rut=self.emisor_rut,
                tipo_dte=tipo_dte,
                folio=self.folio,
                fecha_emision_date=self.fecha_emision_date,
                receptor_rut=self.receptor_rut,
                monto_total=self.monto_total,
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


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RvDetalleEntry(RcvDetalleEntry):
    """
    Entry of the "detalle" of an RV ("Registro de Ventas").
    """

    ###########################################################################
    # constants
    ###########################################################################

    RCV_KIND: ClassVar[RcvKind] = RcvKind.VENTAS

    tipo_venta: str
    """
    Tipo Venta
    """

    receptor_razon_social: str
    """
    Razon Social
    """

    fecha_acuse_dt: Optional[datetime]
    """
    Fecha Acuse Recibo (must be timezone aware)
    """

    fecha_reclamo_dt: Optional[datetime]
    """
    Fecha Reclamo (must be timezone aware)
    """

    monto_exento: int
    """
    Monto Exento
    """

    monto_neto: int
    """
    Monto Neto
    """

    monto_iva: int
    """
    Monto IVA
    """

    iva_retenido_total: int
    """
    IVA Retenido Total
    """

    iva_retenido_parcial: int
    """
    IVA Retenido Parcial
    """

    iva_no_retenido: int
    """
    IVA no retenido
    """

    iva_propio: int
    """
    IVA propio
    """

    iva_terceros: int
    """
    IVA Terceros
    """

    liquidacion_factura_emisor_rut: Optional[Rut]
    """
    RUT Emisor Liquid. Factura
    """

    neto_comision_liquidacion_factura: int
    """
    Neto Comision Liquid. Factura
    """

    exento_comision_liquidacion_factura: int
    """
    Exento Comision Liquid. Factura
    """

    iva_comision_liquidacion_factura: int
    """
    IVA Comision Liquid. Factura
    """

    iva_fuera_de_plazo: int
    """
    IVA fuera de plazo
    """

    tipo_documento_referencia: Optional[int]
    """
    Tipo Docto. Referencia
    """

    folio_documento_referencia: Optional[int]
    """
    Folio Docto. Referencia
    """

    num_ident_receptor_extranjero: Optional[str]
    """
    Num. Ident. Receptor Extranjero
    """

    nacionalidad_receptor_extranjero: Optional[str]
    """
    Nacionalidad Receptor Extranjero
    """

    credito_empresa_constructora: int
    """
    Credito empresa constructora
    """

    impuesto_zona_franca_ley_18211: Optional[int]
    """
    Impto. Zona Franca (Ley 18211)
    """

    garantia_dep_envases: int
    """
    Garantia Dep. Envases
    """

    indicador_venta_sin_costo: int
    """
    Indicador Venta sin Costo
    """

    indicador_servicio_periodico: int
    """
    Indicador Servicio Periodico
    """

    monto_no_facturable: int
    """
    Monto No facturable
    """

    total_monto_periodo: int
    """
    Total Monto Periodo
    """

    venta_pasajes_transporte_nacional: Optional[int]
    """
    Venta Pasajes Transporte Nacional
    """

    venta_pasajes_transporte_internacional: Optional[int]
    """
    Venta Pasajes Transporte Internacional
    """

    numero_interno: Optional[str]
    """
    Numero Interno
    """

    codigo_sucursal: Optional[str]
    """
    Codigo Sucursal
    """

    nce_o_nde_sobre_factura_de_compra: Optional[str]
    """
    NCE o NDE sobre Fact. de Compra
    """

    codigo_otro_imp: Optional[str]
    """
    Codigo Otro Imp.
    """

    valor_otro_imp: Optional[int]
    """
    Valor Otro Imp.
    """

    tasa_otro_imp: Optional[float]
    """
    Tasa Otro Imp.
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('receptor_razon_social')
    @classmethod
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.field_validator('fecha_acuse_dt', 'fecha_reclamo_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcDetalleEntry(RcvDetalleEntry):
    """
    Base class for entries of the "detalle" of an RC ("Registro de Compras").
    Contains all common fields from RcvCompraCsvRowSchema.
    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    RCV_KIND = RcvKind.COMPRAS

    ###########################################################################
    # fields - all common fields from RcvCompraCsvRowSchema
    ###########################################################################

    tipo_compra: str
    """
    Tipo Compra
    """

    emisor_razon_social: str
    """
    "Razón social" (legal name) of the "emisor" of the "documento".
    """

    monto_exento: int
    """
    Monto Exento
    """

    monto_neto: int
    """
    Monto Neto
    """

    monto_iva_recuperable: Optional[int]
    """
    Monto IVA Recuperable
    """

    monto_iva_no_recuperable: Optional[int]
    """
    Monto Iva No Recuperable
    """

    codigo_iva_no_rec: Optional[str]
    """
    Codigo IVA No Rec.
    """

    monto_neto_activo_fijo: Optional[int]
    """
    Monto Neto Activo Fijo
    """

    iva_activo_fijo: Optional[int]
    """
    IVA Activo Fijo
    """

    iva_uso_comun: Optional[int]
    """
    IVA uso Comun
    """

    impto_sin_derecho_a_credito: Optional[int]
    """
    Impto. Sin Derecho a Credito
    """

    iva_no_retenido: int
    """
    IVA No Retenido
    """

    nce_o_nde_sobre_factura_de_compra: Optional[str]
    """
    NCE o NDE sobre Fact. de Compra
    """

    codigo_otro_impuesto: Optional[str]
    """
    Codigo Otro Impuesto
    """

    valor_otro_impuesto: Optional[int]
    """
    Valor Otro Impuesto
    """

    tasa_otro_impuesto: Optional[float]
    """
    Tasa Otro Impuesto
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('emisor_razon_social')
    @classmethod
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcRegistroDetalleEntry(RcDetalleEntry):
    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "registro".
    """

    ###########################################################################
    # constants
    ###########################################################################

    RC_ESTADO_CONTABLE: ClassVar[RcEstadoContable] = RcEstadoContable.REGISTRO

    ###########################################################################
    # Unique fields
    ###########################################################################

    fecha_acuse_dt: Optional[datetime]
    """
    Fecha Acuse (must be timezone aware)
    """

    tabacos_puros: Optional[int]
    """
    Tabacos Puros
    """

    tabacos_cigarrillos: Optional[int]
    """
    Tabacos Cigarrillos
    """

    tabacos_elaborados: Optional[int]
    """
    Tabacos Elaborados
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('fecha_acuse_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcNoIncluirDetalleEntry(RcDetalleEntry):
    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "no incluir".
    """

    ###########################################################################
    # constants
    ###########################################################################

    RC_ESTADO_CONTABLE: ClassVar[RcEstadoContable] = RcEstadoContable.NO_INCLUIR

    ###########################################################################
    # Unique fields
    ###########################################################################

    fecha_acuse_dt: Optional[datetime]
    """
    Fecha Acuse (must be timezone aware)
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('fecha_acuse_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcReclamadoDetalleEntry(RcDetalleEntry):
    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "reclamado".
    """

    ###########################################################################
    # constants
    ###########################################################################

    RC_ESTADO_CONTABLE: ClassVar[RcEstadoContable] = RcEstadoContable.RECLAMADO

    ###########################################################################
    # Unique fields
    ###########################################################################

    fecha_reclamo_dt: Optional[datetime]
    """
    Fecha Reclamo (must be timezone aware)
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('fecha_reclamo_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
)
class RcPendienteDetalleEntry(RcDetalleEntry):
    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "pendiente".
    """

    ###########################################################################
    # constants
    ###########################################################################

    RC_ESTADO_CONTABLE: ClassVar[RcEstadoContable] = RcEstadoContable.PENDIENTE

    # No unique fields for pendiente - it only has common fields from RcDetalleEntry
