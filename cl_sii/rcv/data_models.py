"""
RCV data models
===============


"""
from __future__ import annotations

import dataclasses
import logging
from dataclasses import field as dc_field
from datetime import date, datetime
from typing import Optional

import cl_sii.dte.data_models
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut

from .constants import RcEstadoContable, RcvKind, RcvTipoDocto


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class PeriodoTributario:

    year: int = dc_field()
    month: int = dc_field()

    def __post_init__(self) -> None:
        if not isinstance(self.year, int):
            raise TypeError("Inappropriate type of 'year'.")
        if self.year < 1900:  # arbitrary number but it more useful than checking not < 1.
            raise ValueError("Value is out of the valid range for 'year'.")

        if not isinstance(self.month, int):
            raise TypeError("Inappropriate type of 'month'.")
        if self.month < 1 or self.month > 12:
            raise ValueError("Value is out of the valid range for 'month'.")

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
        value_naive = tz_utils.convert_tz_aware_dt_to_naive(value, SII_OFFICIAL_TZ)
        return cls.from_date(value_naive.date())

    def as_date(self) -> date:
        return date(self.year, self.month, day=1)

    def as_datetime(self) -> datetime:
        # note: timezone-aware
        return tz_utils.convert_naive_dt_to_tz_aware(
            datetime(self.year, self.month, day=1, hour=0, minute=0, second=0),
            SII_OFFICIAL_TZ)


@dataclasses.dataclass(frozen=True)
class RcvDetalleEntry:

    """
    Entry of the "detalle" of an RCV.
    """

    ###########################################################################
    # constants
    ###########################################################################

    # note: as of Python 3.7.3 we can not do something like `RCV_KIND: Optional[RcvKind] = None`
    #   because 'dataclasses' gets confused and assumes that that class attribute is a dataclass
    #   field (it is not), and this error is triggered:
    #   > TypeError: non-default argument 'my_dc_field' follows default argument

    RCV_KIND = None  # type: Optional[RcvKind]
    RC_ESTADO_CONTABLE = None  # type: Optional[RcEstadoContable]

    ###########################################################################
    # fields
    ###########################################################################

    emisor_rut: Rut = dc_field()
    """
    RUT of the "emisor" of the "documento".
    """

    tipo_docto: RcvTipoDocto = dc_field()
    """
    The kind of "documento".
    """

    folio: int = dc_field()
    """
    The sequential number of a "documento".
    """

    # TODO: docstring
    fecha_emision_date: date = dc_field()

    # TODO: docstring
    # TODO: can it be None? What happens for those "tipo docto" that do not have a receptor?
    receptor_rut: Rut = dc_field()

    monto_total: int = dc_field()
    """
    Total amount of the "documento".
    """

    emisor_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "emisor" of the "documento".
    """

    # TODO: docstring
    # TODO: can it be None? What happens for those "tipo docto" that do not have a receptor?
    receptor_razon_social: str = dc_field()

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_recepcion_dt: datetime = dc_field()

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        if self.RCV_KIND == RcvKind.COMPRAS:
            if self.RC_ESTADO_CONTABLE is None:
                raise ValueError(
                    "'RC_ESTADO_CONTABLE' must not be None when 'RCV_KIND' is 'COMPRAS'.")
        elif self.RCV_KIND == RcvKind.VENTAS:
            if self.RC_ESTADO_CONTABLE is not None:
                raise ValueError(
                    "'RC_ESTADO_CONTABLE' must be None when 'RCV_KIND' is 'VENTAS'.")

        if not isinstance(self.emisor_rut, Rut):
            raise TypeError("Inappropriate type of 'emisor_rut'.")

        if not isinstance(self.tipo_docto, RcvTipoDocto):
            raise TypeError("Inappropriate type of 'tipo_docto'.")

        if not isinstance(self.folio, int):
            raise TypeError("Inappropriate type of 'folio'.")
        if not self.folio > 0:
            raise ValueError("Inappropriate value of 'folio'.")

        if not isinstance(self.fecha_emision_date, date):
            raise TypeError("Inappropriate type of 'fecha_emision_date'.")

        if not isinstance(self.receptor_rut, Rut):
            raise TypeError("Inappropriate type of 'receptor_rut'.")

        # TODO: figure out validation rules of 'monto_total'
        if not isinstance(self.monto_total, int):
            raise TypeError("Inappropriate type of 'monto_total'.")

        if not isinstance(self.emisor_razon_social, str):
            raise TypeError("Inappropriate type of 'emisor_razon_social'.")
        cl_sii.dte.data_models.validate_contribuyente_razon_social(self.emisor_razon_social)

        if not isinstance(self.receptor_razon_social, str):
            raise TypeError("Inappropriate type of 'receptor_razon_social'.")
        cl_sii.dte.data_models.validate_contribuyente_razon_social(self.receptor_razon_social)

        if not isinstance(self.fecha_recepcion_dt, datetime):
            raise TypeError("Inappropriate type of 'fecha_recepcion_dt'.")
        tz_utils.validate_dt_tz(self.fecha_recepcion_dt, SII_OFFICIAL_TZ)

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

            dte_data = cl_sii.dte.data_models.DteDataL2(
                emisor_rut=self.emisor_rut,
                tipo_dte=tipo_dte,
                folio=self.folio,
                fecha_emision_date=self.fecha_emision_date,
                receptor_rut=self.receptor_rut,
                monto_total=self.monto_total,
                emisor_razon_social=self.emisor_razon_social,
                receptor_razon_social=self.receptor_razon_social,
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


@dataclasses.dataclass(frozen=True)
class RvDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RV ("Registro de Ventas").
    """

    RCV_KIND = RcvKind.VENTAS
    RC_ESTADO_CONTABLE = None

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_acuse_dt: Optional[datetime] = dc_field()

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_reclamo_dt: Optional[datetime] = dc_field()

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.fecha_acuse_dt is not None:
            if not isinstance(self.fecha_acuse_dt, datetime):
                raise TypeError("Inappropriate type of 'fecha_acuse_dt'.")
            tz_utils.validate_dt_tz(self.fecha_acuse_dt, SII_OFFICIAL_TZ)

        if self.fecha_reclamo_dt is not None:
            if not isinstance(self.fecha_reclamo_dt, datetime):
                raise TypeError("Inappropriate type of 'fecha_reclamo_dt'.")
            tz_utils.validate_dt_tz(self.fecha_reclamo_dt, SII_OFFICIAL_TZ)


@dataclasses.dataclass(frozen=True)
class RcRegistroDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "registro".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.REGISTRO

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_acuse_dt: Optional[datetime] = dc_field()

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.fecha_acuse_dt is not None:
            if not isinstance(self.fecha_acuse_dt, datetime):
                raise TypeError("Inappropriate type of 'fecha_acuse_dt'.")
            tz_utils.validate_dt_tz(self.fecha_acuse_dt, SII_OFFICIAL_TZ)


@dataclasses.dataclass(frozen=True)
class RcNoIncluirDetalleEntry(RcRegistroDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "no incluir".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.NO_INCLUIR


@dataclasses.dataclass(frozen=True)
class RcReclamadoDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "reclamado".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.RECLAMADO

    # TODO: docstring
    # note: must be timezone-aware.
    fecha_reclamo_dt: Optional[datetime] = dc_field()

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.fecha_reclamo_dt is not None:
            if not isinstance(self.fecha_reclamo_dt, datetime):
                raise TypeError("Inappropriate type of 'fecha_reclamo_dt'.")
            tz_utils.validate_dt_tz(self.fecha_reclamo_dt, SII_OFFICIAL_TZ)


@dataclasses.dataclass(frozen=True)
class RcPendienteDetalleEntry(RcvDetalleEntry):

    """
    Entry of the "detalle" of an RC ("Registro de Compras") / "pendiente".
    """

    RCV_KIND = RcvKind.COMPRAS
    RC_ESTADO_CONTABLE = RcEstadoContable.PENDIENTE
