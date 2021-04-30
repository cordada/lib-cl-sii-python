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
from typing import Mapping, Optional, Sequence

import pydantic

import cl_sii.contribuyente.constants
import cl_sii.rut.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut

from . import constants
from .constants import CodigoReferencia, TipoDteEnum


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


def validate_dte_monto_total(value: int, tipo_dte: TipoDteEnum) -> None:
    """
    Validate value for DTE field ``monto_total``.

    :raises ValueError:
    :raises TypeError:

    """
    # note: mypy gets confused and complains about "Unsupported operand types for >/<".
    if (value < constants.DTE_MONTO_TOTAL_FIELD_MIN_VALUE  # type: ignore
            or value > constants.DTE_MONTO_TOTAL_FIELD_MAX_VALUE):  # type: ignore
        raise ValueError("Value is out of the valid range for 'monto_total'.")

    if value < 0 and tipo_dte != TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
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

        validate_dte_monto_total(self.monto_total, self.tipo_dte)

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
                "Concept \"vendedor\" does not apply for this 'tipo_dte'.", self.tipo_dte)

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
                self.tipo_dte)

        return result

    @property
    def deudor_rut(self) -> Rut:
        """
        Return the RUT of the "deudor" (same as the "comprador").

        :raises ValueError:
        """
        return self.comprador_rut


@dataclasses.dataclass(frozen=True)
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

    emisor_razon_social: Optional[str] = dc_field()
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    receptor_razon_social: Optional[str] = dc_field()
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    fecha_vencimiento_date: Optional[date] = dc_field(default=None)
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    firma_documento_dt: Optional[datetime] = dc_field(default=None)
    """
    Datetime on which the "documento" was digitally signed.
    """

    signature_value: Optional[bytes] = dc_field(default=None)
    """
    DTE's digital signature's value (raw bytes, without base64 encoding).
    """

    signature_x509_cert_der: Optional[bytes] = dc_field(default=None)
    """
    DTE's digital signature's DER-encoded X.509 cert.

    .. seealso::
        Functions :func:`cl_sii.libs.crypto_utils.load_der_x509_cert`
        and :func:`cl_sii.libs.crypto_utils.x509_cert_der_to_pem`.
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

        if self.emisor_razon_social is not None:
            if not isinstance(self.emisor_razon_social, str):
                raise TypeError("Inappropriate type of 'emisor_razon_social'.")
            validate_contribuyente_razon_social(self.emisor_razon_social)

        if self.receptor_razon_social is not None:
            if not isinstance(self.receptor_razon_social, str):
                raise TypeError("Inappropriate type of 'receptor_razon_social'.")
            validate_contribuyente_razon_social(self.receptor_razon_social)

        if self.fecha_vencimiento_date is not None:
            if not isinstance(self.fecha_vencimiento_date, date):
                raise TypeError("Inappropriate type of 'fecha_vencimiento_date'.")

        if self.firma_documento_dt is not None:
            if not isinstance(self.firma_documento_dt, datetime):
                raise TypeError("Inappropriate type of 'firma_documento_dt'.")
            tz_utils.validate_dt_tz(self.firma_documento_dt, self.DATETIME_FIELDS_TZ)

        if self.signature_value is not None:
            if not isinstance(self.signature_value, bytes):
                raise TypeError("Inappropriate type of 'signature_value'.")
            # warning: do NOT strip a bytes value because "strip" implies an ASCII-encoded text,
            #   which in this case it is not.
            validate_non_empty_bytes(self.signature_value)

        if self.signature_x509_cert_der is not None:
            if not isinstance(self.signature_x509_cert_der, bytes):
                raise TypeError("Inappropriate type of 'signature_x509_cert_der'.")
            # warning: do NOT strip a bytes value because "strip" implies an ASCII-encoded text,
            #   which in this case it is not.
            validate_non_empty_bytes(self.signature_x509_cert_der)

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

    def as_dte_data_l1(self) -> DteDataL1:
        return DteDataL1(
            emisor_rut=self.emisor_rut,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fecha_emision_date,
            receptor_rut=self.receptor_rut,
            monto_total=self.monto_total)


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type('Config', (), dict(
        arbitrary_types_allowed=True,
    ))
)
class DteXmlReferencia:
    """
    Data in XML element ``Referencia`` in an DTE XML doc.

    > Identificacion de otros documentos Referenciados por Documento

    DTE doc XML element: 'Documento//Referencia'

    .. note:: An XML DTE document includes none or up to 40 "Referencia" elements.

    .. seealso::
        XML schema of ``{http://www.sii.cl/SiiDte}/DTE/Documento/Referencia`` in 'DTE_v10.xsd' at
        https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/dte/README.md

    """

    ###########################################################################
    # Fields
    ###########################################################################

    numero_linea_ref: int
    """
    Sequential line  number of the "referencia". Must be an integer between 1 and 40 inclusive

    > Numero Secuencial de Linea de Referencia

    DTE doc XML element: '..//Documento//Referencia//NroLinRef'
    """

    tipo_documento_ref: str
    """
    Kind of the document of "Referencia". Length must be >= 1 and <= 3

    > Tipo de Documento de Referencia

    DTE doc XML element: '..//Documento//Referencia//TpoDocRef'

    .. note::
        This field accepts any of the elements of the class:`TipoDocumentoEnum` or
        an alphanumeric to refer to non-tax documents (in this case, validation does not apply)
    """

    folio_ref: str
    """
    The folio of the document referred to.

    > Identificación del documento de referencia.

    DTE doc XML element: '..//Documento//Referencia//FolioRef'
    """

    fecha_ref: date
    """
    The 'fecha_emision' of the document referred to.

    > Fecha del documento de referencia

    DTE doc XML element: '..//Documento//Referencia//FchRef'
    """

    ind_global: Optional[int] = None
    """
    Whether a set of documents of the same kind is referenced.

    > Documento afecta a un número de más de 20 documentos del mismo `tipo_documento_ref`
    > Se explicita la razón en `Razón Referencia`

    DTE doc XML element: '..//Documento//Referencia//IndGlobal'
    """

    rut_otro: Optional[Rut] = None
    """
    The RUT of the "emisor" of the document referred to.

    > RUT otro contribuyente

    DTE doc XML element: '..//Documento//Referencia//RUTOtr'

    .. note::
        > Sólo si el documento de referencia es de tipo tributario y fue emitido
        > por otro contribuyente
    """

    codigo_ref: Optional[CodigoReferencia] = None
    """
    The type of use for the reference

    > Tipo de Uso de la Referencia

    DTE doc XML element: '..//Documento//Referencia//CodRef'
    """

    razon_ref: Optional[str] = None
    """
    The reason the document is being referenced

    > Razon Explicita por la que se Referencia el Documento

    DTE doc XML element: '..//Documento//Referencia//RazonRef'
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """

        if (
            self.numero_linea_ref < constants.DTE_REFERENCIA_LINE_NUMBER_MIN_VALUE
            or self.numero_linea_ref > constants.DTE_REFERENCIA_LINE_NUMBER_MAX_VALUE
        ):
            raise ValueError(
                "Value 'numero_linea_ref' must be a value between "
                f"{constants.DTE_REFERENCIA_LINE_NUMBER_MIN_VALUE} and "
                f"{constants.DTE_REFERENCIA_LINE_NUMBER_MAX_VALUE}",
                self.numero_linea_ref)

        if len(self.tipo_documento_ref) < 1 or len(self.tipo_documento_ref) > 3:
            raise ValueError(
                "The length of 'tipo_documento_ref' must be a value between 1 and 3",
                self.tipo_documento_ref)

        if self.ind_global and self.ind_global != 1:
            raise ValueError(
                "Only the value \"1\" is valid for the field 'ind_global'",
                self.ind_global)

        if (
                len(self.folio_ref) < constants.DTE_REFERENCIA_FOLIO_MIN_LENGTH
                or len(self.folio_ref) > constants.DTE_REFERENCIA_FOLIO_MAX_LENGTH
        ):
            raise ValueError(
                "The length of 'folio_ref' must be a value between "
                f"{constants.DTE_REFERENCIA_FOLIO_MIN_LENGTH} and "
                f"{constants.DTE_REFERENCIA_FOLIO_MAX_LENGTH}",
                self.folio_ref)

        if (
            self.fecha_ref < constants.DTE_REFERENCIA_FECHA_NOT_BEFORE
            or self.fecha_ref > constants.DTE_REFERENCIA_FECHA_NOT_AFTER
        ):
            raise ValueError(
                "The date 'fecha_ref' must be after "
                f"{constants.DTE_REFERENCIA_FECHA_NOT_BEFORE} and before "
                f"{constants.DTE_REFERENCIA_FECHA_NOT_AFTER}",
                self.fecha_ref)

        if self.razon_ref and len(self.razon_ref) > constants.DTE_REFERENCIA_RAZON_MAX_LENGTH:
            raise ValueError(
                "The maximum length allowed for `razon_ref` is "
                f"{constants.DTE_REFERENCIA_RAZON_MAX_LENGTH}",
                self.razon_ref)


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=type('Config', (), dict(
        arbitrary_types_allowed=True,
    ))
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

    referencias: Optional[Sequence[DteXmlReferencia]] = None
    """
    List of structs for ``Referencia`` XML elements.

    ..warning::
        The items MUST be ordered according to their ``numero_linea_ref``.
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

        if self.firma_documento_dt is not None:
            if not isinstance(self.firma_documento_dt, datetime):
                raise TypeError("Inappropriate type of 'firma_documento_dt'.")
            tz_utils.validate_dt_tz(self.firma_documento_dt, self.DATETIME_FIELDS_TZ)

        if self.signature_value is not None:
            if not isinstance(self.signature_value, bytes):
                raise TypeError("Inappropriate type of 'signature_value'.")
            # warning: do NOT strip a bytes value because "strip" implies an ASCII-encoded text,
            #   which in this case it is not.
            validate_non_empty_bytes(self.signature_value)

        if self.signature_x509_cert_der is not None:
            if not isinstance(self.signature_x509_cert_der, bytes):
                raise TypeError("Inappropriate type of 'signature_x509_cert_der'.")
            # warning: do NOT strip a bytes value because "strip" implies an ASCII-encoded text,
            #   which in this case it is not.
            validate_non_empty_bytes(self.signature_x509_cert_der)

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

    def as_dte_data_l1(self) -> DteDataL1:
        return DteDataL1(
            emisor_rut=self.emisor_rut,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fecha_emision_date,
            receptor_rut=self.receptor_rut,
            monto_total=self.monto_total)

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

    @pydantic.validator('referencias')
    def validate_referencias_numero_linea_ref_order(cls, v: object) -> object:
        if isinstance(v, Sequence):
            for idx, referencia in enumerate(v, start=1):
                if referencia.numero_linea_ref != idx:
                    raise ValueError("items must be ordered according to their 'numero_linea_ref'")
        return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_referencias_rut_otro_is_consistent_with_tipo_dte(
        cls, values: Mapping[str, object],
    ) -> Mapping[str, object]:
        referencias = values['referencias']
        tipo_dte = values['tipo_dte']

        if (
            isinstance(referencias, Sequence)
            and isinstance(tipo_dte, TipoDteEnum)
            and tipo_dte not in constants.DTE_REFERENCIA_RUTOTR_TIPO_DOC_SET
        ):
            for referencia in referencias:
                if referencia.rut_otro:
                    raise ValueError(
                        f"Setting a 'rut_otro' is not a valid option for this 'tipo_dte':"
                        f" 'tipo_dte' == {tipo_dte!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}.",
                    )

        return values

    @pydantic.root_validator(skip_on_failure=True)
    def validate_referencias_rut_otro_is_consistent_with_emisor_rut(
        cls, values: Mapping[str, object],
    ) -> Mapping[str, object]:
        referencias = values['referencias']
        emisor_rut = values['emisor_rut']

        if (
            isinstance(referencias, Sequence)
            and isinstance(emisor_rut, Rut)
        ):
            for referencia in referencias:
                if referencia.rut_otro and referencia.rut_otro == emisor_rut:
                    raise ValueError(
                        f"'rut_otro' must be different from 'emisor_rut':"
                        f" {referencia.rut_otro!r} == {emisor_rut!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}.",
                    )

        return values

    @pydantic.root_validator(skip_on_failure=True)
    def validate_referencias_codigo_ref_is_consistent_with_tipo_dte(
        cls, values: Mapping[str, object],
    ) -> Mapping[str, object]:
        referencias = values['referencias']
        tipo_dte = values['tipo_dte']

        if (
            isinstance(referencias, Sequence)
            and isinstance(tipo_dte, TipoDteEnum)
            and tipo_dte in constants.DTE_REFERENCIA_CODREF_TIPO_DOC_MANDATORY_SET
        ):
            for referencia in referencias:
                if not referencia.codigo_ref:
                    raise ValueError(
                        f"'codigo_ref' is mandatory for this 'tipo_dte':"
                        f" 'tipo_dte' == {tipo_dte!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}.",
                    )

        return values
