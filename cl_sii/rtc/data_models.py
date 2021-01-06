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
from datetime import datetime
from typing import ClassVar, Mapping

import pydantic

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte import data_models as dte_data_models
from cl_sii.dte.constants import TipoDteEnum
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


def validate_cesion_dte_tipo_dte(value: TipoDteEnum) -> None:
    """
    Validate "tipo DTE" of the "cesión".

    :raises ValueError:
    """
    if value not in constants.TIPO_DTE_CEDIBLES:
        raise ValueError('Value is not "cedible".', value)


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type('Config', (), dict(
        arbitrary_types_allowed=True,
    ))
)
class CesionNaturalKey:
    """
    Natural key of a "cesión" of a DTE.

    The class instances are immutable.

    This group of fields uniquely identifies a "cesión".

    Example:

    >>> instance = CesionNaturalKey(
    ...     dte_data_models.DteNaturalKey(
    ...         Rut('60910000-1'), TipoDteEnum.FACTURA_ELECTRONICA, 2093465,
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
    config=type('Config', (), dict(
        arbitrary_types_allowed=True,
    ))
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
    ...         Rut('60910000-1'), TipoDteEnum.FACTURA_ELECTRONICA, 2093465,
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
