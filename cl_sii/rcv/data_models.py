"""
RCV data models
===============


"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import ClassVar, Mapping, Optional

import pydantic

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

    @pydantic.validator('year')
    def validate_year(cls, v: object) -> object:
        if isinstance(v, int) and v < 1900:
            # 1900 si an arbitrary number but it more useful than checking not < 1.
            raise ValueError("Value is out of the valid range for 'year'.")
        return v

    @pydantic.validator('month')
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
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
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

    @pydantic.validator('folio')
    def validate_folio(cls, v: object) -> object:
        if isinstance(v, int):
            cl_sii.dte.data_models.validate_dte_folio(v)
        return v

    @pydantic.validator('fecha_recepcion_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_rcv_kind_is_consistent_with_rc_estado_contable(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        rcv_kind = values.get('RCV_KIND')
        rc_estado_contable = values.get('RC_ESTADO_CONTABLE')

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

        return values

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
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
    ),
)
class RvDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RV ("Registro de Ventas").
    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    RCV_KIND = RcvKind.VENTAS
    RC_ESTADO_CONTABLE = None

    # TODO: docstring
    # TODO: can it be None? What happens for those "tipo docto" that do not have a receptor?
    receptor_razon_social: str

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_acuse_dt: Optional[datetime]

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_reclamo_dt: Optional[datetime]

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('receptor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('fecha_acuse_dt', 'fecha_reclamo_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
    ),
)
class RcRegistroDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "registro".
    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.REGISTRO

    emisor_razon_social: str
    """
    "Razón social" (legal name) of the "emisor" of the "documento".
    """

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_acuse_dt: Optional[datetime]

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('emisor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('fecha_acuse_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
    ),
)
class RcNoIncluirDetalleEntry(RcRegistroDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "no incluir".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.NO_INCLUIR


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
    ),
)
class RcReclamadoDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "reclamado".
    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # fields
    ###########################################################################

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.RECLAMADO

    emisor_razon_social: str
    """
    "Razón social" (legal name) of the "emisor" of the "documento".
    """

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_reclamo_dt: Optional[datetime]

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('emisor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('fecha_reclamo_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type(
        'Config',
        (),
        dict(
            arbitrary_types_allowed=True,
        ),
    ),
)
class RcPendienteDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "pendiente".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.PENDIENTE

    emisor_razon_social: str
    """
    "Razón social" (legal name) of the "emisor" of the "documento".
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('emisor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            cl_sii.dte.data_models.validate_contribuyente_razon_social(v)
        return v
