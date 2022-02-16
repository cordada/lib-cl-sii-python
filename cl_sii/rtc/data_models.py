"""
Data models for RTC
===================

In this domain we care about the data of transactions that consist in:
a "cesión" of a DTE, by a "cedente" to a "cesionario".

Natural key of a cesion
-----------------------

Each transaction can be uniquely identified by the group of fields defined in
:class:`CesionNaturalKey`. However, because of SII's inconsistent systems
implementations, there are several information sources *where the "cesión"'s
sequence number is not available*. Thus the usefulness of that class is
limited, unlike :class:`cl_sii.dte.data_models.DteNaturalKey` for a DTE.
In some cases, the alternative natural key :class:`CesionAltNaturalKey` may
be used as a workaround when the sequence number is not available.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
from typing import Any, ClassVar, Mapping, Optional

import pydantic

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte import data_models as dte_data_models
from cl_sii.dte.constants import TipoDte
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from . import constants


def validate_cesion_seq(value: int) -> None:
    """
    Validate value for sequence number of a "cesión".

    :raises ValueError:
    """
    if (
        value < constants.CESION_SEQUENCE_NUMBER_MIN_VALUE
        or value > constants.CESION_SEQUENCE_NUMBER_MAX_VALUE
    ):
        raise ValueError("Value is out of the valid range.", value)


def validate_cesion_monto(value: int) -> None:
    """
    Validate amount of the "cesión".

    :raises ValueError:
    """
    if (
        value < constants.CESION_MONTO_CEDIDO_FIELD_MIN_VALUE
        or value > constants.CESION_MONTO_CEDIDO_FIELD_MAX_VALUE
    ):
        raise ValueError("Value is out of the valid range.", value)


def validate_cesion_dte_tipo_dte(value: TipoDte) -> None:
    """
    Validate "tipo DTE" of the "cesión".

    :raises ValueError:
    """
    if value not in constants.TIPO_DTE_CEDIBLES:
        raise ValueError('Value is not "cedible".', value)


def validate_cesion_and_dte_montos(cesion_value: int, dte_value: int) -> None:
    """
    Validate amounts of the "cesión" and its associated DTE.

    :raises ValueError:
    """
    if not (cesion_value <= dte_value):
        raise ValueError('Value of "cesión" must be <= value of DTE.', cesion_value, dte_value)


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
class CesionNaturalKey:
    """
    Natural key of a "cesión" of a DTE.

    The class instances are immutable.

    This group of fields uniquely identifies a "cesión".

    Example:

    >>> instance = CesionNaturalKey(
    ...     dte_data_models.DteNaturalKey(
    ...         Rut('60910000-1'), TipoDte.FACTURA_ELECTRONICA, 2093465,
    ...     ),
    ...     1,
    ... )
    """

    ###########################################################################
    # Fields
    ###########################################################################

    dte_key: dte_data_models.DteNaturalKey
    """
    Natural key of the "cesión"'s DTE.
    """

    seq: int
    """
    Sequence number of the "cesión". Must be >= 1.
    """

    @property
    def slug(self) -> str:
        """
        Return an slug representation (that preserves uniquess) of the instance.
        """
        # Note: Based on 'cl_sii.dte.data_models.DteNaturalKey.slug'.
        return f'{self.dte_key.slug}--{self.seq}'

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte_key')
    def validate_dte_tipo_dte(cls, v: object) -> object:
        if isinstance(v, dte_data_models.DteNaturalKey):
            validate_cesion_dte_tipo_dte(v.tipo_dte)
        return v

    @pydantic.validator('seq')
    def validate_seq(cls, v: object) -> object:
        if isinstance(v, int):
            validate_cesion_seq(v)
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
class CesionAltNaturalKey:
    """
    Alternative natural key of a "cesión" of a DTE.

    Useful when the sequence number is unavailable, such as in "cesiones periodo".

    The class instances are immutable.

    .. warning::
        It is assumed that it is impossible to "ceder" a given DTE by a given "cedente" to a given
        "cesionario" more than once in a particular instant (``fecha_cesion_dt``).

    Example:

    >>> instance = CesionAltNaturalKey(
    ...     dte_data_models.DteNaturalKey(
    ...         Rut('60910000-1'), TipoDte.FACTURA_ELECTRONICA, 2093465,
    ...     ),
    ...     Rut('76389992-6'),
    ...     Rut('76598556-0'),
    ...     datetime.fromisoformat('2019-04-05T12:57:32-03:00'),
    ... )
    """

    ###########################################################################
    # Constants
    ###########################################################################

    DATETIME_FIELDS_TZ: ClassVar[tz_utils.PytzTimezone] = SII_OFFICIAL_TZ

    ###########################################################################
    # Fields
    ###########################################################################

    dte_key: dte_data_models.DteNaturalKey
    """
    Natural key of the "cesión"'s DTE.
    """

    cedente_rut: Rut
    """
    RUT of the "cedente".
    """

    cesionario_rut: Rut
    """
    RUT of the "cesionario".
    """

    fecha_cesion_dt: datetime
    """
    Date and time when the "cesión" happened.

    .. warning:: The value will always be truncated to the minute, even if the
        original value has seconds. This has to be done because this field is
        part of a key and in some data sources the timestamp has seconds and in
        others it has not (e.g. AEC and Cesión Periodo).
    """

    @property
    def slug(self) -> str:
        """
        Return a slug representation (that preserves uniquess) of the instance.
        """
        # Note: Based on 'cl_sii.dte.data_models.DteNaturalKey.slug'.

        _fecha_cesion_dt = self.fecha_cesion_dt.astimezone(self.DATETIME_FIELDS_TZ)
        fecha_cesion_dt: str = _fecha_cesion_dt.isoformat(timespec='minutes')

        return f'{self.dte_key.slug}--{self.cedente_rut}--{self.cesionario_rut}--{fecha_cesion_dt}'

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte_key')
    def validate_dte_tipo_dte(cls, v: object) -> object:
        if isinstance(v, dte_data_models.DteNaturalKey):
            validate_cesion_dte_tipo_dte(v.tipo_dte)
        return v

    @pydantic.validator('fecha_cesion_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.validator('fecha_cesion_dt')
    def truncate_fecha_cesion_dt_to_minutes(cls, v: object) -> object:
        if isinstance(v, datetime):
            if v.second != 0:
                v = v.replace(second=0)
            if v.microsecond != 0:
                v = v.replace(microsecond=0)
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
class CesionL0:
    """
    Data of a "cesión" (level 0).

    Its fields are enough to uniquely identify a "cesión" but nothing more.

    The class instances are immutable.
    """

    ###########################################################################
    # Constants
    ###########################################################################

    DATETIME_FIELDS_TZ: ClassVar[tz_utils.PytzTimezone] = SII_OFFICIAL_TZ

    ###########################################################################
    # Fields
    ###########################################################################

    dte_key: dte_data_models.DteNaturalKey
    """
    Natural key of the "cesión"'s DTE.
    """

    seq: Optional[int]
    """
    Sequence number of the "cesión". Must be >= 1.
    """

    cedente_rut: Rut
    """
    RUT of the "cedente".
    """

    cesionario_rut: Rut
    """
    RUT of the "cesionario".
    """

    fecha_cesion_dt: datetime
    """
    Date and time when the "cesión" happened.

    .. note::
        - This is the timestamp of when the "cesión"'s AEC was digitally signed
          (AEC XML document XPath: ``/AEC/DocumentoAEC/Caratula/TmstFirmaEnvio``).
        - Same timestamp as the last ``Cesion`` element of AEC XPath
          ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/TmstCesion``.
        - Same timestamp as RPETC email's ``Cesion`` / ``Fecha de la Cesion``.
        - NOT the same timestamp as RPETC email's ``Fecha de Recepcion``.
        - Almost the same timestamp as "Cesiones Periodo"'s ``FCH_CESION``,
          (AEC's has seconds, "Cesiones Periodo"'s is truncated to the minute).
        - Same timestamp as the "Registro AoR DTE" event ``DTE Cedido``.
        - The above statements were empirically verified for
          ``CesionNaturalKey(dte_key=DteNaturalKey(Rut('99***140-4'), 33, 3105), seq=2)``.

    .. warning:: The timestamp is generated by the signer of the AEC so it
        cannot be fully trusted. It is not clear how much validation is
        performed by the SII. A more trustworthy value is the RPETC email's
        ``Fecha de Recepcion``, which is generated by the SII, but most of the
        time only the "fecha cesión" will be available.
    """

    @property
    def natural_key(self) -> Optional[CesionNaturalKey]:
        if self.seq is not None:
            return CesionNaturalKey(
                dte_key=self.dte_key,
                seq=self.seq,
            )
        else:
            return None

    @property
    def alt_natural_key(self) -> CesionAltNaturalKey:
        return CesionAltNaturalKey(
            dte_key=self.dte_key,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
        )

    @property
    def slug(self) -> str:
        """
        Return an slug representation (that preserves uniquess) of the instance.
        """
        # Note: Based on 'cl_sii.dte.data_models.DteNaturalKey.slug'.
        return self.alt_natural_key.slug

    @property
    def dte_emisor_rut(self) -> Rut:
        return self.dte_key.emisor_rut

    @property
    def dte_tipo_dte(self) -> TipoDte:
        return self.dte_key.tipo_dte

    @property
    def dte_folio(self) -> int:
        return self.dte_key.folio

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte_key')
    def validate_dte_tipo_dte(cls, v: object) -> object:
        if isinstance(v, dte_data_models.DteNaturalKey):
            validate_cesion_dte_tipo_dte(v.tipo_dte)
        return v

    @pydantic.validator('seq')
    def validate_seq(cls, v: object) -> object:
        if isinstance(v, int):
            validate_cesion_seq(v)
        return v

    @pydantic.validator('fecha_cesion_dt')
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
class CesionL1(CesionL0):
    """
    Data of a "cesión" (level 1).

    It is the minimal set of "cesión" data fields that are useful.
    TODO: Explain why these fields were chosen as "minimal".

    The class instances are immutable.
    """

    ###########################################################################
    # Fields
    ###########################################################################

    monto_cedido: int
    """
    Amount of the "cesión".
    """

    fecha_ultimo_vencimiento: date
    """
    Date of "Ultimo Vencimiento".
    """

    dte_fecha_emision: date
    """
    Field 'fecha_emision' of the DTE.

    .. warning:: It may not match the **real date** on which the DTE was issued
        or received/processed by SII.
    """

    dte_receptor_rut: Rut
    """
    RUT of the "receptor" of the DTE.
    """

    dte_monto_total: int
    """
    Total amount of the DTE.
    """

    @property
    def dte_vendedor_rut(self) -> Rut:
        """
        Return the RUT of the DTE's "vendedor".

        :raises ValueError:
        """
        return self.as_dte_data_l1().vendedor_rut

    @property
    def dte_deudor_rut(self) -> Rut:
        """
        Return the RUT of the DTE's "deudor".

        :raises ValueError:
        """
        return self.as_dte_data_l1().deudor_rut

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_cesion_l0(self) -> CesionL0:
        return CesionL0(
            dte_key=self.dte_key,
            seq=self.seq,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
        )

    def as_dte_data_l1(self) -> dte_data_models.DteDataL1:
        return dte_data_models.DteDataL1(
            emisor_rut=self.dte_key.emisor_rut,
            tipo_dte=self.dte_key.tipo_dte,
            folio=self.dte_key.folio,
            fecha_emision_date=self.dte_fecha_emision,
            receptor_rut=self.dte_receptor_rut,
            monto_total=self.dte_monto_total,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    # TODO: Validate value of 'fecha_cesion_dt' in relation to the DTE data.

    @pydantic.validator('monto_cedido')
    def validate_monto_cedido(cls, v: object) -> object:
        if isinstance(v, int):
            validate_cesion_monto(v)
        return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_monto_cedido_does_not_exceed_dte_monto_total(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        monto_cedido = values['monto_cedido']
        dte_monto_total = values['dte_monto_total']

        if isinstance(monto_cedido, int) and isinstance(dte_monto_total, int):
            validate_cesion_and_dte_montos(cesion_value=monto_cedido, dte_value=dte_monto_total)

        return values


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type(
        'Config',
        (),
        dict(
            anystr_strip_whitespace=True,
            arbitrary_types_allowed=True,
            min_anystr_length=1,
        ),
    ),
)
class CesionL2(CesionL1):
    """
    Data of a "cesión" (level 2).

    The class instances are immutable.
    """

    ###########################################################################
    # Fields
    ###########################################################################

    fecha_firma_dt: Optional[datetime] = None
    """
    Datetime of 'Firma del Archivo de Transferencias'

    .. warning:: It is not equal to the datetime on which the SII received/processed the "cesión".
    """

    cedente_razon_social: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    "Razón social" (legal name) of the "cedente".
    """

    cesionario_razon_social: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    "Razón social" (legal name) of the "cesionario".
    """

    cedente_email: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Email address of the "cedente".

    .. warning:: Value may be an invalid email address.
    """

    cesionario_email: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Email address of the "cesionario".

    .. warning:: Value may be an invalid email address.
    """

    dte_emisor_razon_social: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    # dte_emisor_email: str
    # """
    # Email address of the "emisor" of the DTE.
    #
    # .. warning:: Value may be an invalid email address.
    # """

    dte_receptor_razon_social: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    # dte_receptor_email: str
    # """
    # Email address of the "receptor" of the DTE.
    #
    # .. warning:: Value may be an invalid email address.
    # """

    dte_deudor_email: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Email address of the "deudor" of the DTE.

    .. warning:: Value may be an invalid email address.
    """

    cedente_declaracion_jurada: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    "Declaración Jurada" by the "cedente".

    > Declaracion Jurada de Disponibilidad de Documentacion No Electronica.

    .. note::
        The RUT and "razón social" of the "deudor" of the DTE are included
        in the text. However, this field is optional.

    Example:
        "Se declara bajo juramento que
        COMERCIALIZADORA INNOVA MOBEL SPA, RUT 76399752-9
        ha puesto a disposición del cesionario
        ST CAPITAL S.A., RUT 76389992-6,
        el o los documentos donde constan los recibos de las mercaderías
        entregadas o servicios prestados, entregados por parte del deudor
        de la factura
        EMPRESAS LA POLAR S.A., RUT 96874030-K,
        deacuerdo a lo establecido en la Ley N°19.983."
    """

    dte_fecha_vencimiento: Optional[date] = None
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    contacto_nombre: Optional[str] = None
    """
    Name of the contact person.

    > Persona de Contacto para aclarar dudas.
    """

    contacto_telefono: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Phone number of the contact person.
    """

    contacto_email: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Email address of the contact person.
    """

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_cesion_l1(self) -> CesionL1:
        return CesionL1(
            dte_key=self.dte_key,
            seq=self.seq,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
            monto_cedido=self.monto_cedido,
            fecha_ultimo_vencimiento=self.fecha_ultimo_vencimiento,
            dte_fecha_emision=self.dte_fecha_emision,
            dte_receptor_rut=self.dte_receptor_rut,
            dte_monto_total=self.dte_monto_total,
        )

    def as_dte_data_l2(self) -> dte_data_models.DteDataL2:
        return dte_data_models.DteDataL2(
            emisor_rut=self.dte_key.emisor_rut,
            tipo_dte=self.dte_key.tipo_dte,
            folio=self.dte_key.folio,
            fecha_emision_date=self.dte_fecha_emision,
            receptor_rut=self.dte_receptor_rut,
            monto_total=self.dte_monto_total,
            emisor_razon_social=self.dte_emisor_razon_social,
            receptor_razon_social=self.dte_receptor_razon_social,
            fecha_vencimiento_date=self.dte_fecha_vencimiento,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    # TODO: Validate value of 'fecha_firma_dt' in relation to the DTE data.

    # TODO: Validate value of 'fecha_ultimo_vencimiento' in relation to the DTE data.

    @pydantic.validator(
        'fecha_cesion_dt',
        'fecha_firma_dt',
    )
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.validator(
        'cedente_razon_social',
        'cesionario_razon_social',
        'dte_emisor_razon_social',
        'dte_receptor_razon_social',
    )
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            dte_data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_dte_data_l2(cls, values: Mapping[str, Any]) -> Mapping[str, object]:
        dte_key = values['dte_key']
        try:
            # Note: Delegate some validation to 'dte_data_models.DteDataL2'.
            _ = dte_data_models.DteDataL2(
                emisor_rut=dte_key.emisor_rut if dte_key is not None else None,
                tipo_dte=dte_key.tipo_dte if dte_key is not None else None,
                folio=dte_key.folio if dte_key is not None else None,
                fecha_emision_date=values['dte_fecha_emision'],  # type: ignore[arg-type]
                receptor_rut=values['dte_receptor_rut'],  # type: ignore[arg-type]
                monto_total=values['dte_monto_total'],  # type: ignore[arg-type]
                emisor_razon_social=values['dte_emisor_razon_social'],
                receptor_razon_social=values['dte_receptor_razon_social'],
                fecha_vencimiento_date=values['dte_fecha_vencimiento'],
            )
        except (TypeError, ValueError):
            raise

        return values
