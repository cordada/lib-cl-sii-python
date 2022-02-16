"""
DTE data models
===============

Concepts
--------

In the domain of a DTE, a:

* "Vendedor": is who sold goods or services to "deudor" in a
  transaction for which the DTE was issued.
  It *usually* corresponds to the DTE's "emisor", but not always.
* "Deudor": is who purchased goods or services from "vendedor" in a
  transaction for which the DTE was issued.
  It *usually* corresponds to the DTE's "receptor", but not always.

"""
import dataclasses
from datetime import date, datetime
from typing import Mapping, Optional

import pydantic

import cl_sii.contribuyente.constants
import cl_sii.rut.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from . import constants
from .constants import TipoDte


def validate_dte_folio(value: int) -> None:
    """
    Validate value for DTE field ``folio``.

    :raises ValueError:
    :raises TypeError:

    """
    if value < constants.DTE_FOLIO_FIELD_MIN_VALUE or value > constants.DTE_FOLIO_FIELD_MAX_VALUE:
        raise ValueError("Value is out of the valid range for 'folio'.")


def validate_dte_monto_total(value: int, tipo_dte: TipoDte) -> None:
    """
    Validate value for DTE field ``monto_total``.

    :raises ValueError:
    :raises TypeError:

    """
    if (
        value < constants.DTE_MONTO_TOTAL_FIELD_MIN_VALUE
        or value > constants.DTE_MONTO_TOTAL_FIELD_MAX_VALUE
    ):
        raise ValueError("Value is out of the valid range for 'monto_total'.")

    if value < 0 and tipo_dte != TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
        raise ValueError("Value is out of the valid range for 'monto_total'.")


def validate_contribuyente_razon_social(value: str) -> None:
    """
    Validate value for the "razón social" of a "contribuyente".

    :raises ValueError:
    :raises TypeError:

    """
    if len(value) > len(value.strip()):
        raise ValueError("Value must not have leading or trailing whitespace.")

    if len(value) < 1:
        raise ValueError("Value must not be empty.")

    if len(value) > cl_sii.contribuyente.constants.RAZON_SOCIAL_LONG_MAX_LENGTH:
        raise ValueError("Value exceeds max allowed length.")


def validate_clean_str(value: str) -> None:
    if len(value.strip()) != len(value):
        raise ValueError("Value has leading or trailing whitespace characters.", value)


def validate_non_empty_str(value: str) -> None:
    if len(value.strip()) == 0:
        raise ValueError("String value length (stripped) is 0.")


def validate_non_empty_bytes(value: bytes) -> None:
    # warning: do NOT strip a bytes value because "strip" implies an ASCII-encoded text,
    #   which may not be the case.
    # if len(value.strip()) == 0:
    if len(value) == 0:
        raise ValueError("Bytes value length is 0.")


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
class DteNaturalKey:

    """
    Natural key of a DTE.

    The class instances are immutable.

    This group of fields uniquely identifies a DTE.

    >>> instance = DteNaturalKey(Rut('60910000-1'), TipoDte.FACTURA_ELECTRONICA, 2093465)

    >>> str(instance)
    "DteNaturalKey(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDte.FACTURA_ELECTRONICA: 33>, folio=2093465)"
    >>> str(instance) == repr(instance)
    True
    >>> instance.slug
    '60910000-1--33--2093465'

    """

    emisor_rut: Rut
    """
    RUT of the "emisor" of the DTE.
    """

    tipo_dte: TipoDte
    """
    The kind of DTE.
    """

    folio: int
    """
    The sequential number of a DTE of given kind issued by 'emisor_rut'.
    """

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    @property
    def slug(self) -> str:
        """
        Return an slug representation (that preserves uniquess) of the instance.
        """
        # note: many alternatives were considered and discarded such as:
        #   f'{self.emisor_rut}-{self.tipo_dte}-{self.folio}'
        #   f'{self.emisor_rut}.{self.tipo_dte}.{self.folio}'
        #   f'{self.emisor_rut}/{self.tipo_dte}/{self.folio}'
        #   f'R-{self.emisor_rut}-T-{self.tipo_dte}-F-{self.folio}'
        #   f'rut-{self.emisor_rut}-tipo-{self.tipo_dte}-folio-{self.folio}'

        return f'{self.emisor_rut}--{self.tipo_dte}--{self.folio}'

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('folio')
    def validate_folio(cls, v: object) -> object:
        if isinstance(v, int):
            validate_dte_folio(v)
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
class DteDataL0(DteNaturalKey):

    """
    DTE data level 0.

    Its fields are enough to uniquely identify a DTE but nothing more.

    The class instances are immutable.

    >>> instance = DteDataL0(
    ...     Rut('60910000-1'), TipoDte.FACTURA_ELECTRONICA, 2093465, date(2018, 5, 7),
    ...     Rut('60910000-1'), 10403)

    >>> str(instance)
    "DteDataL0(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDte.FACTURA_ELECTRONICA: 33>, " \
    "folio=2093465)"
    >>> str(instance) == repr(instance)
    True
    >>> instance.slug
    '60910000-1--33--2093465'
    >>> instance.natural_key
    "DteNaturalKey(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDte.FACTURA_ELECTRONICA: 33>, folio=2093465)"

    """

    @property
    def natural_key(self) -> DteNaturalKey:
        return DteNaturalKey(emisor_rut=self.emisor_rut, tipo_dte=self.tipo_dte, folio=self.folio)


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
class DteDataL1(DteDataL0):

    """
    DTE data level 1.

    It is the minimal set of DTE data fields that are useful.
    For example, SII has an endpoint that confirms that a given DTE exists,
    and the data that it requires can be obtained from this struct.

    The class instances are immutable.

    >>> instance = DteDataL1(
    ...     Rut('60910000-1'), TipoDte.FACTURA_ELECTRONICA, 2093465, date(2018, 5, 7),
    ...     Rut('60910000-1'), 10403)

    >>> str(instance)
    "DteDataL1(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDte.FACTURA_ELECTRONICA: 33>, " \
    "folio=2093465, fecha_emision_date=datetime.date(2018, 5, 7), " \
    "receptor_rut=Rut('60910000-1'), monto_total=10403)"
    >>> str(instance) == repr(instance)
    True

    """

    fecha_emision_date: date
    """
    Field 'fecha_emision' of the DTE.

    .. warning:: It may not match the **real date** on which the DTE was issued
        or received/processed by SII.

    """

    receptor_rut: Rut
    """
    RUT of the "receptor" of the DTE.
    """

    monto_total: int
    """
    Total amount of the DTE.
    """

    ###########################################################################
    # properties
    ###########################################################################

    @property
    def vendedor_rut(self) -> Rut:
        """
        Return the RUT of the "vendedor" aka "proveedor" (supplier).

        :raises ValueError:
        """
        if self.tipo_dte.emisor_is_vendedor:
            result = self.emisor_rut
        elif self.tipo_dte.receptor_is_vendedor:
            result = self.receptor_rut
        else:
            raise ValueError(
                "Concept \"vendedor\" does not apply for this 'tipo_dte'.", self.tipo_dte
            )

        return result

    @property
    def comprador_rut(self) -> Rut:
        """
        Return the RUT of the "comprador" aka "cliente" (buyer).

        :raises ValueError:
        """
        if self.tipo_dte.emisor_is_vendedor:
            result = self.receptor_rut
        elif self.tipo_dte.receptor_is_vendedor:
            result = self.emisor_rut
        else:
            raise ValueError(
                "Concepts \"comprador\" and \"deudor\" do not apply for this 'tipo_dte'.",
                self.tipo_dte,
            )

        return result

    @property
    def deudor_rut(self) -> Rut:
        """
        Return the RUT of the "deudor" (same as the "comprador").

        :raises ValueError:
        """
        return self.comprador_rut

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('monto_total')
    def validate_monto_total(cls, v: object, values: Mapping[str, object]) -> object:
        tipo_dte = values.get('tipo_dte')

        if isinstance(v, int) and isinstance(tipo_dte, TipoDte):
            validate_dte_monto_total(v, tipo_dte=tipo_dte)

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
class DteDataL2(DteDataL1):

    """
    DTE data level 2.

    Very similar to :class:`DteXmlData` (and a lot of duplicated code,
    unfortunately).

    About fields
    - ``emisor_razon_social``: redundant but required by the DTE XML schema.
    - ``receptor_razon_social``: redundant but required by the DTE XML schema.
    - ``fecha_vencimiento`` (date): important for some business logic
      but it is not required by the DTE XML schema.

    The class instances are immutable.

    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # fields
    ###########################################################################

    emisor_razon_social: Optional[str]
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    receptor_razon_social: Optional[str]
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    fecha_vencimiento_date: Optional[date] = None
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    firma_documento_dt: Optional[datetime] = None
    """
    Datetime on which the "documento" was digitally signed.
    """

    signature_value: Optional[bytes] = None
    """
    DTE's digital signature's value (raw bytes, without base64 encoding).
    """

    signature_x509_cert_der: Optional[bytes] = None
    """
    DTE's digital signature's DER-encoded X.509 cert.

    .. seealso::
        Functions :func:`cl_sii.libs.crypto_utils.load_der_x509_cert`
        and :func:`cl_sii.libs.crypto_utils.x509_cert_der_to_pem`.
    """

    emisor_giro: Optional[str] = None
    """
    "Giro" of the "emisor" of the DTE.
    """

    emisor_email: Optional[str] = None
    """
    Email address of the "emisor" of the DTE.
    """

    receptor_email: Optional[str] = None
    """
    Email address of the "receptor" of the DTE.
    """

    def as_dte_data_l1(self) -> DteDataL1:
        return DteDataL1(
            emisor_rut=self.emisor_rut,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fecha_emision_date,
            receptor_rut=self.receptor_rut,
            monto_total=self.monto_total,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('emisor_razon_social', 'receptor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('firma_documento_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.validator('signature_value', 'signature_x509_cert_der')
    def validate_non_empty_bytes(cls, v: object) -> object:
        if isinstance(v, bytes):
            validate_non_empty_bytes(v)
        return v

    @pydantic.validator('emisor_giro', 'emisor_email', 'receptor_email')
    def validate_no_leading_or_trailing_whitespace_characters(cls, v: object) -> object:
        if isinstance(v, str):
            validate_clean_str(v)
        return v

    @pydantic.validator('emisor_giro', 'emisor_email', 'receptor_email')
    def validate_non_empty_stripped_str(cls, v: object) -> object:
        if isinstance(v, str):
            validate_non_empty_str(v)
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
class DteXmlData(DteDataL1):

    """
    DTE XML data.

    Very similar to :class:`DteDataL2` (and a lot of duplicated code,
    unfortunately).

    About fields
    - ``emisor_razon_social``: redundant but required by the DTE XML schema.
    - ``receptor_razon_social``: redundant but required by the DTE XML schema.
    - ``fecha_vencimiento`` (date): important for some business logic
      but it is not required by the DTE XML schema.

    The class instances are immutable.

    """

    ###########################################################################
    # constants
    ###########################################################################

    DATETIME_FIELDS_TZ = SII_OFFICIAL_TZ

    ###########################################################################
    # fields
    ###########################################################################

    emisor_razon_social: str
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    receptor_razon_social: str
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    fecha_vencimiento_date: Optional[date] = None
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    firma_documento_dt: Optional[datetime] = None
    """
    Datetime on which the "documento" was digitally signed.
    """

    signature_value: Optional[bytes] = None
    """
    DTE's digital signature's value (raw bytes, without base64 encoding).
    """

    signature_x509_cert_der: Optional[bytes] = None
    """
    DTE's digital signature's DER-encoded X.509 cert.

    .. seealso::
        Functions :func:`cl_sii.libs.crypto_utils.load_der_x509_cert`
        and :func:`cl_sii.libs.crypto_utils.x509_cert_der_to_pem`.
    """

    emisor_giro: Optional[str] = None
    """
    "Giro" of the "emisor" of the DTE.
    """

    emisor_email: Optional[str] = None
    """
    Email address of the "emisor" of the DTE.
    """

    receptor_email: Optional[str] = None
    """
    Email address of the "receptor" of the DTE.
    """

    def as_dte_data_l1(self) -> DteDataL1:
        return DteDataL1(
            emisor_rut=self.emisor_rut,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fecha_emision_date,
            receptor_rut=self.receptor_rut,
            monto_total=self.monto_total,
        )

    def as_dte_data_l2(self) -> DteDataL2:
        return DteDataL2(
            emisor_rut=self.emisor_rut,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fecha_emision_date,
            receptor_rut=self.receptor_rut,
            monto_total=self.monto_total,
            emisor_razon_social=self.emisor_razon_social,
            receptor_razon_social=self.receptor_razon_social,
            fecha_vencimiento_date=self.fecha_vencimiento_date,
            firma_documento_dt=self.firma_documento_dt,
            signature_value=self.signature_value,
            signature_x509_cert_der=self.signature_x509_cert_der,
            emisor_giro=self.emisor_giro,
            emisor_email=self.emisor_email,
            receptor_email=self.receptor_email,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('emisor_razon_social', 'receptor_razon_social')
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('firma_documento_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.validator('signature_value', 'signature_x509_cert_der')
    def validate_non_empty_bytes(cls, v: object) -> object:
        if isinstance(v, bytes):
            validate_non_empty_bytes(v)
        return v

    @pydantic.validator('emisor_giro', 'emisor_email', 'receptor_email')
    def validate_no_leading_or_trailing_whitespace_characters(cls, v: object) -> object:
        if isinstance(v, str):
            validate_clean_str(v)
        return v

    @pydantic.validator('emisor_giro', 'emisor_email', 'receptor_email')
    def validate_non_empty_stripped_str(cls, v: object) -> object:
        if isinstance(v, str):
            validate_non_empty_str(v)
        return v
