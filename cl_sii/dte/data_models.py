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
from dataclasses import field as dc_field
from datetime import date, datetime
from typing import Mapping, Optional

import cl_sii.contribuyente.constants
import cl_sii.rut.constants
from cl_sii.libs import encoding_utils
from cl_sii.rut import Rut

from . import constants
from .constants import TipoDteEnum


def validate_dte_folio(value: int) -> None:
    """
    Validate value for DTE field ``folio``.

    :raises ValueError:
    :raises TypeError:

    """
    # note: mypy gets confused and complains about "Unsupported operand types for >/<".
    if (value < constants.DTE_FOLIO_FIELD_MIN_VALUE  # type: ignore
            or value > constants.DTE_FOLIO_FIELD_MAX_VALUE):  # type: ignore
        raise ValueError("Value is out of the valid range for 'folio'.")


def validate_dte_monto_total(value: int) -> None:
    """
    Validate value for DTE field ``monto_total``.

    :raises ValueError:
    :raises TypeError:

    """
    # note: mypy gets confused and complains about "Unsupported operand types for >/<".
    if (value < constants.DTE_MONTO_TOTAL_FIELD_MIN_VALUE  # type: ignore
            or value > constants.DTE_MONTO_TOTAL_FIELD_MAX_VALUE):  # type: ignore
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


def validate_clean_bytes(value: bytes) -> None:
    if len(value.strip()) != len(value):
        raise ValueError("Value has leading or trailing whitespace characters.", value)


def validate_non_empty_str(value: str) -> None:
    if len(value.strip()) == 0:
        raise ValueError("String value length (stripped) is 0.")


def validate_non_empty_bytes(value: bytes) -> None:
    if len(value.strip()) == 0:
        raise ValueError("Bytes value length (stripped) is 0.")


@dataclasses.dataclass(frozen=True)
class DteNaturalKey:

    """
    Natural key of a DTE.

    The class instances are immutable.

    This group of fields uniquely identifies a DTE.

    >>> instance = DteNaturalKey(Rut('60910000-1'), TipoDteEnum.FACTURA_ELECTRONICA, 2093465)

    >>> str(instance)
    "DteNaturalKey(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>, folio=2093465)"
    >>> str(instance) == repr(instance)
    True
    >>> instance.slug
    '60910000-1--33--2093465'

    """

    emisor_rut: Rut = dc_field()
    """
    RUT of the "emisor" of the DTE.
    """

    tipo_dte: TipoDteEnum = dc_field()
    """
    The kind of DTE.
    """

    folio: int = dc_field()
    """
    The sequential number of a DTE of given kind issued by 'emisor_rut'.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """

        if not isinstance(self.emisor_rut, Rut):
            raise TypeError("Inappropriate type of 'emisor_rut'.")

        if not isinstance(self.tipo_dte, TipoDteEnum):
            raise TypeError("Inappropriate type of 'tipo_dte'.")

        if not isinstance(self.folio, int):
            raise TypeError("Inappropriate type of 'folio'.")

        validate_dte_folio(self.folio)

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


@dataclasses.dataclass(frozen=True)
class DteDataL0(DteNaturalKey):

    """
    DTE data level 0.

    Its fields are enough to uniquely identify a DTE but nothing more.

    The class instances are immutable.

    >>> instance = DteDataL0(
    ...     Rut('60910000-1'), TipoDteEnum.FACTURA_ELECTRONICA, 2093465, date(2018, 5, 7),
    ...     Rut('60910000-1'), 10403)

    >>> str(instance)
    "DteDataL0(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>, " \
    "folio=2093465)"
    >>> str(instance) == repr(instance)
    True
    >>> instance.slug
    '60910000-1--33--2093465'
    >>> instance.natural_key
    "DteNaturalKey(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>, folio=2093465)"

    """

    @property
    def natural_key(self) -> DteNaturalKey:
        return DteNaturalKey(emisor_rut=self.emisor_rut, tipo_dte=self.tipo_dte, folio=self.folio)


@dataclasses.dataclass(frozen=True)
class DteDataL1(DteDataL0):

    """
    DTE data level 1.

    It is the minimal set of DTE data fields that are useful.
    For example, SII has an endpoint that confirms that a given DTE exists,
    and the data that it requires can be obtained from this struct.

    The class instances are immutable.

    >>> instance = DteDataL1(
    ...     Rut('60910000-1'), TipoDteEnum.FACTURA_ELECTRONICA, 2093465, date(2018, 5, 7),
    ...     Rut('60910000-1'), 10403)

    >>> str(instance)
    "DteDataL1(" \
    "emisor_rut=Rut('60910000-1'), tipo_dte=<TipoDteEnum.FACTURA_ELECTRONICA: 33>, " \
    "folio=2093465, fecha_emision_date=datetime.date(2018, 5, 7), " \
    "receptor_rut=Rut('60910000-1'), monto_total=10403)"
    >>> str(instance) == repr(instance)
    True

    """

    fecha_emision_date: date = dc_field()
    """
    Field 'fecha_emision' of the DTE.

    .. warning:: It may not match the **real date** on which the DTE was issued
        or received/processed by SII.

    """

    receptor_rut: Rut = dc_field()
    """
    RUT of the "receptor" of the DTE.
    """

    monto_total: int = dc_field()
    """
    Total amount of the DTE.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        super().__post_init__()

        if not isinstance(self.fecha_emision_date, date):
            raise TypeError("Inappropriate type of 'fecha_emision_date'.")

        if not isinstance(self.receptor_rut, Rut):
            raise TypeError("Inappropriate type of 'receptor_rut'.")

        if not isinstance(self.monto_total, int):
            raise TypeError("Inappropriate type of 'monto_total'.")

        validate_dte_monto_total(self.monto_total)

    @property
    def vendedor_rut(self) -> Rut:
        """
        Return the RUT of the "vendedor".

        :raises ValueError:
        """
        if self.tipo_dte.emisor_is_vendedor:
            result = self.emisor_rut
        elif self.tipo_dte.receptor_is_vendedor:
            result = self.receptor_rut
        else:
            raise ValueError(
                "Concept \"vendedor\" does not apply for this 'tipo_dte'.", self.tipo_dte)

        return result

    @property
    def deudor_rut(self) -> Rut:
        """
        Return the RUT of the "deudor".

        :raises ValueError:
        """
        if self.tipo_dte.emisor_is_vendedor:
            result = self.receptor_rut
        elif self.tipo_dte.receptor_is_vendedor:
            result = self.emisor_rut
        else:
            raise ValueError(
                "Concept \"deudor\" does not apply for this 'tipo_dte'.", self.tipo_dte)

        return result


@dataclasses.dataclass(frozen=True)
class DteDataL2(DteDataL1):

    """
    DTE data level 2.

    About fields
    - ``emisor_razon_social``: redundant but required by the DTE XML schema.
    - ``receptor_razon_social``: redundant but required by the DTE XML schema.
    - ``fecha_vencimiento`` (date): important for some business logic
      but it is not required by the DTE XML schema.

    The class instances are immutable.

    """

    emisor_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    receptor_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    fecha_vencimiento_date: Optional[date] = dc_field(default=None)
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    firma_documento_dt_naive: Optional[datetime] = dc_field(default=None)
    """
    Datetime on which the "documento" was digitally signed.
    """

    signature_value: Optional[bytes] = dc_field(default=None)
    """
    DTE's digital signature's value (raw bytes, without base64 encoding).
    """

    signature_x509_cert_pem: Optional[bytes] = dc_field(default=None)
    """
    DTE's digital signature's PEM-encoded X.509 cert.

    PEM-encoded implies base64-encoded.
    """

    emisor_giro: Optional[str] = dc_field(default=None)
    """
    "Giro" of the "emisor" of the DTE.
    """

    emisor_email: Optional[str] = dc_field(default=None)
    """
    Email address of the "emisor" of the DTE.
    """

    receptor_email: Optional[str] = dc_field(default=None)
    """
    Email address of the "receptor" of the DTE.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        super().__post_init__()

        if not isinstance(self.emisor_razon_social, str):
            raise TypeError("Inappropriate type of 'emisor_razon_social'.")
        validate_contribuyente_razon_social(self.emisor_razon_social)

        if not isinstance(self.receptor_razon_social, str):
            raise TypeError("Inappropriate type of 'receptor_razon_social'.")
        validate_contribuyente_razon_social(self.receptor_razon_social)

        if self.fecha_vencimiento_date is not None:
            if not isinstance(self.fecha_vencimiento_date, date):
                raise TypeError("Inappropriate type of 'fecha_vencimiento_date'.")

        if self.firma_documento_dt_naive is not None:
            if not isinstance(self.firma_documento_dt_naive, datetime):
                raise TypeError("Inappropriate type of 'firma_documento_dt_naive'.")

        if self.signature_value is not None:
            if not isinstance(self.signature_value, bytes):
                raise TypeError("Inappropriate type of 'signature_value'.")
            validate_clean_bytes(self.signature_value)
            validate_non_empty_bytes(self.signature_value)

        if self.signature_x509_cert_pem is not None:
            if not isinstance(self.signature_x509_cert_pem, bytes):
                raise TypeError("Inappropriate type of 'signature_x509_cert_pem'.")
            validate_clean_bytes(self.signature_x509_cert_pem)
            validate_non_empty_bytes(self.signature_x509_cert_pem)
            encoding_utils.validate_base64(self.signature_x509_cert_pem)

        if self.emisor_giro is not None:
            if not isinstance(self.emisor_giro, str):
                raise TypeError("Inappropriate type of 'emisor_giro'.")
            validate_clean_str(self.emisor_giro)
            validate_non_empty_str(self.emisor_giro)

        if self.emisor_email is not None:
            if not isinstance(self.emisor_email, str):
                raise TypeError("Inappropriate type of 'emisor_email'.")
            validate_clean_str(self.emisor_email)
            validate_non_empty_str(self.emisor_email)

        if self.receptor_email is not None:
            if not isinstance(self.receptor_email, str):
                raise TypeError("Inappropriate type of 'receptor_email'.")
            validate_clean_str(self.receptor_email)
            validate_non_empty_str(self.receptor_email)
