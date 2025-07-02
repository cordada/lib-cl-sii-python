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

from __future__ import annotations

import dataclasses
import logging
import random
from datetime import date, datetime
from typing import Mapping, Optional, Sequence

import pydantic
from typing_extensions import Self

import cl_sii.contribuyente.constants
import cl_sii.rut.constants
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from . import constants
from .constants import CodigoReferencia, TipoDte


logger = logging.getLogger(__name__)


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


VALIDATION_CONTEXT_TRUST_INPUT: str = 'trust_input'
"""
Key for the validation context to indicate that the input data is trusted.
"""


def is_input_trusted_according_to_validation_context(
    validation_context: Optional[Mapping[str, object]],
) -> bool:
    """
    Return whether the input data is trusted according to the validation context.

    :param validation_context:
        The validation context of a Pydantic model.
        Get it from ``pydantic.ValidationInfo.context``.

    Example for data classes:

    >>> dte_xml_data_instance_kwargs: Mapping[str, object] = dict(
    ...     emisor_rut=Rut('60910000-1'),  # ...
    ... )
    >>> dte_xml_data_adapter = pydantic.TypeAdapter(DteXmlData)
    >>> dte_xml_data_instance: DteXmlData = dte_xml_data_adapter.validate_python(
    ...     dte_xml_data_instance_kwargs,
    ...     context={VALIDATION_CONTEXT_TRUST_INPUT: True}
    ... )
    """
    if validation_context is None:
        return False
    else:
        return validation_context.get(VALIDATION_CONTEXT_TRUST_INPUT) is True


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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

    @pydantic.field_validator('folio')
    @classmethod
    def validate_folio(cls, v: object) -> object:
        if isinstance(v, int):
            validate_dte_folio(v)
        return v

    ############################################################################
    # class methods
    ############################################################################

    @classmethod
    def random(
        cls,
        emisor_rut: Optional[Rut] = None,
        tipo_dte: TipoDte | Sequence[TipoDte] = tuple(TipoDte),
        folio: int | tuple[int, int] = (
            constants.DTE_FOLIO_FIELD_MIN_VALUE,
            constants.DTE_FOLIO_FIELD_MAX_VALUE,
        ),
    ) -> Self:
        """
        Generate random DTE natural key within valid ranges.

        :param emisor_rut: RUT of the "emisor" of the DTE. If `None`, a random RUT is generated.
        :param tipo_dte: The kind of DTE. If a sequence is provided, a random one is chosen.
        :param folio: The sequential number of the DTE. If a 2-tuple of integers is provided,
            a random one is chosen within the range defined by the tuple.
        """
        if emisor_rut is None:
            emisor_rut = Rut.random()
        if isinstance(tipo_dte, Sequence):
            tipo_dte = random.choice(tipo_dte)
        if isinstance(folio, tuple):
            folio = random.randint(*folio)
        return cls(emisor_rut, tipo_dte, folio)


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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

    @pydantic.field_validator('monto_total')
    @classmethod
    def validate_monto_total(cls, v: object, info: pydantic.ValidationInfo) -> object:
        tipo_dte = info.data['tipo_dte']

        if isinstance(v, int) and isinstance(tipo_dte, TipoDte):
            validate_dte_monto_total(v, tipo_dte=tipo_dte)

        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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

    @pydantic.field_validator('emisor_razon_social', 'receptor_razon_social')
    @classmethod
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            validate_contribuyente_razon_social(v)
        return v

    @pydantic.field_validator('firma_documento_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.field_validator('signature_value', 'signature_x509_cert_der')
    @classmethod
    def validate_non_empty_bytes(cls, v: object) -> object:
        if isinstance(v, bytes):
            validate_non_empty_bytes(v)
        return v

    @pydantic.field_validator('emisor_giro', 'emisor_email', 'receptor_email')
    @classmethod
    def validate_no_leading_or_trailing_whitespace_characters(cls, v: object) -> object:
        if isinstance(v, str):
            validate_clean_str(v)
        return v

    @pydantic.field_validator('emisor_giro', 'emisor_email', 'receptor_email')
    @classmethod
    def validate_non_empty_stripped_str(cls, v: object) -> object:
        if isinstance(v, str):
            validate_non_empty_str(v)
        return v


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    ),
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
        This field accepts any of the elements of the class:`TipoDocumento` or
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

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('numero_linea_ref')
    @classmethod
    def validate_numero_linea_ref(cls, value: int) -> int:
        if (
            constants.DTE_REFERENCIA_LINE_NUMBER_MIN_VALUE
            <= value
            <= constants.DTE_REFERENCIA_LINE_NUMBER_MAX_VALUE
        ):
            return value

        raise ValueError(
            "Value 'numero_linea_ref' must be a value between "
            f"{constants.DTE_REFERENCIA_LINE_NUMBER_MIN_VALUE} and "
            f"{constants.DTE_REFERENCIA_LINE_NUMBER_MAX_VALUE}",
            value,
        )

    @pydantic.field_validator('tipo_documento_ref')
    @classmethod
    def validate_tipo_documento_ref(cls, value: str) -> str:
        if 1 <= len(value) <= 3:
            return value

        raise ValueError(
            "The length of 'tipo_documento_ref' must be a value between 1 and 3", value
        )

    @pydantic.field_validator('ind_global')
    @classmethod
    def validate_ind_global(cls, value: int | None) -> int | None:
        if value and value != 1:
            raise ValueError("Only the value '1' is valid for the field 'ind_global'", value)
        return value

    @pydantic.field_validator('folio_ref')
    @classmethod
    def validate_folio_ref(cls, value: str) -> str:
        if (
            constants.DTE_REFERENCIA_FOLIO_MIN_LENGTH
            <= len(value)
            <= constants.DTE_REFERENCIA_FOLIO_MAX_LENGTH
        ):
            return value

        raise ValueError(
            "The length of 'folio_ref' must be a value between "
            f"{constants.DTE_REFERENCIA_FOLIO_MIN_LENGTH} and "
            f"{constants.DTE_REFERENCIA_FOLIO_MAX_LENGTH}",
            value,
        )

    @pydantic.field_validator('fecha_ref')
    @classmethod
    def validate_fecha_ref(cls, value: date) -> date:
        if (
            value < constants.DTE_REFERENCIA_FECHA_NOT_BEFORE
            or value > constants.DTE_REFERENCIA_FECHA_NOT_AFTER
        ):
            raise ValueError(
                "The date 'fecha_ref' must be after "
                f"{constants.DTE_REFERENCIA_FECHA_NOT_BEFORE} and before "
                f"{constants.DTE_REFERENCIA_FECHA_NOT_AFTER}",
                value,
            )

        return value

    @pydantic.field_validator('razon_ref')
    @classmethod
    def validate_razon_ref(cls, value: str | None) -> str | None:
        if value and len(value) > constants.DTE_REFERENCIA_RAZON_MAX_LENGTH:
            raise ValueError(
                "The maximum length allowed for `razon_ref` is "
                f"{constants.DTE_REFERENCIA_RAZON_MAX_LENGTH}",
                value,
            )

        return value


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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

    referencias: Optional[Sequence[DteXmlReferencia]] = None
    """
    List of structs for ``Referencia`` XML elements.

    ..warning::
        The items MUST be ordered according to their ``numero_linea_ref``.
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

    @pydantic.field_validator('emisor_razon_social', 'receptor_razon_social')
    @classmethod
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            validate_contribuyente_razon_social(v)
        return v

    @pydantic.field_validator('firma_documento_dt')
    @classmethod
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.field_validator('signature_value', 'signature_x509_cert_der')
    @classmethod
    def validate_non_empty_bytes(cls, v: object) -> object:
        if isinstance(v, bytes):
            validate_non_empty_bytes(v)
        return v

    @pydantic.field_validator('emisor_giro', 'emisor_email', 'receptor_email')
    @classmethod
    def validate_no_leading_or_trailing_whitespace_characters(cls, v: object) -> object:
        if isinstance(v, str):
            validate_clean_str(v)
        return v

    @pydantic.field_validator('emisor_giro', 'emisor_email', 'receptor_email')
    @classmethod
    def validate_non_empty_stripped_str(cls, v: object) -> object:
        if isinstance(v, str):
            validate_non_empty_str(v)
        return v

    @pydantic.field_validator('referencias')
    @classmethod
    def validate_referencias_numero_linea_ref_order(cls, v: object) -> object:
        if isinstance(v, Sequence):
            numero_linea_refs = [referencia.numero_linea_ref for referencia in v]
            if numero_linea_refs != sorted(numero_linea_refs):
                raise ValueError(
                    "items must be ordered according to their 'numero_linea_ref'. "
                    f"All numero_linea_refs: "
                    f"{', '.join(str(num_linea_ref) for num_linea_ref in numero_linea_refs)}"
                )
        return v

    @pydantic.model_validator(mode='after')
    def validate_referencias_rut_otro_is_consistent_with_tipo_dte(
        self, info: pydantic.ValidationInfo
    ) -> Self:
        referencias = self.referencias
        tipo_dte = self.tipo_dte

        if (
            isinstance(referencias, Sequence)
            and isinstance(tipo_dte, TipoDte)
            and tipo_dte not in constants.DTE_REFERENCIA_RUTOTR_TIPO_DOC_SET
        ):
            for referencia in referencias:
                if referencia.rut_otro:
                    message: str = (
                        f"Setting a 'rut_otro' is not a valid option for this 'tipo_dte':"
                        f" 'tipo_dte' == {tipo_dte!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}."
                    )
                    if is_input_trusted_according_to_validation_context(info.context):
                        logger.warning('Validation failed but input is trusted: %s', message)
                    else:
                        raise ValueError(message)

        return self

    @pydantic.model_validator(mode='after')
    def validate_referencias_rut_otro_is_consistent_with_emisor_rut(
        self, info: pydantic.ValidationInfo
    ) -> Self:
        referencias = self.referencias
        emisor_rut = self.emisor_rut

        if isinstance(referencias, Sequence) and isinstance(emisor_rut, Rut):
            for referencia in referencias:
                if referencia.rut_otro and referencia.rut_otro == emisor_rut:
                    message: str = (
                        f"'rut_otro' must be different from 'emisor_rut':"
                        f" {referencia.rut_otro!r} == {emisor_rut!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}."
                    )
                    if is_input_trusted_according_to_validation_context(info.context):
                        logger.warning('Validation failed but input is trusted: %s', message)
                    else:
                        raise ValueError(message)

        return self

    @pydantic.model_validator(mode='after')
    def validate_referencias_codigo_ref_is_consistent_with_tipo_dte(self) -> Self:
        referencias = self.referencias
        tipo_dte = self.tipo_dte

        if (
            isinstance(referencias, Sequence)
            and isinstance(tipo_dte, TipoDte)
            and tipo_dte in constants.DTE_REFERENCIA_CODREF_TIPO_DOC_MANDATORY_SET
        ):
            for referencia in referencias:
                if not referencia.codigo_ref:
                    raise ValueError(
                        f"'codigo_ref' is mandatory for this 'tipo_dte':"
                        f" 'tipo_dte' == {tipo_dte!r},"
                        f" 'Referencia' number {referencia.numero_linea_ref}.",
                    )

        return self


DTE_XML_DATA_PYDANTIC_TYPE_ADAPTER = pydantic.TypeAdapter(DteXmlData)
