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

"""
from __future__ import annotations

import dataclasses
from dataclasses import field as dc_field
from datetime import date, datetime
from typing import Mapping, Optional

from cl_sii.dte import data_models as dte_data_models
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.rut import Rut


def validate_cesion_seq(value: int) -> None:
    """
    Validate value for sequence number of a "cesión".

    :raises ValueError:

    """
    if value < 1:
        raise ValueError("Value is out of the valid range.", value)


def validate_cesion_monto(value: int) -> None:
    """
    Validate amount of the "cesión".

    :raises ValueError:

    """
    if value < 0:
        raise ValueError("Value is out of the valid range.", value)


def validate_clean_str(value: str) -> None:
    if len(value.strip()) != len(value):
        raise ValueError("Value has leading or trailing whitespace characters.", value)


def validate_non_empty_str(value: str) -> None:
    if len(value.strip()) == 0:
        raise ValueError("String (stripped) length is 0.")


@dataclasses.dataclass(frozen=True)
class CesionNaturalKey:

    """
    Natural key of a "cesión" of a DTE.

    The class instances are immutable.

    """

    dte_key: dte_data_models.DteNaturalKey = dc_field()
    """
    Natural key of the "cesión"'s DTE.
    """

    seq: int = dc_field()
    """
    Sequence number of the "cesión". Must be >= 1.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        if not isinstance(self.dte_key, dte_data_models.DteNaturalKey):
            raise TypeError("Inappropriate type of 'dte_key'.")
        if not isinstance(self.seq, int):
            raise TypeError("Inappropriate type of 'seq'.")

        validate_cesion_seq(self.seq)

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    @property
    def slug(self) -> str:
        """
        Return an slug representation (that preserves uniquess) of the instance.
        """
        # note: based on 'cl_sii.dte.data_models.DteNaturalKey.slug'

        return f'{self.dte_key.slug}--{self.seq}'


@dataclasses.dataclass(frozen=True)
class CesionDataL0(CesionNaturalKey):

    """
    Data of a "cesión" (level 0).

    """

    cedente_rut: Rut = dc_field()
    """
    RUT of the "cedente".
    """

    cesionario_rut: Rut = dc_field()
    """
    RUT of the "cesionario".
    """

    # TODO: find out validation rules with regard to previous "cesión"s or DTE's amounts.
    monto: int = dc_field()
    """
    Amount of the "cesión".
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        super().__post_init__()

        # TODO: validate value of 'fecha_cesion_dt_naive', in relation to the DTE data.

        if not isinstance(self.cedente_rut, Rut):
            raise TypeError("Inappropriate type of 'cedente_rut'.")
        if not isinstance(self.cesionario_rut, Rut):
            raise TypeError("Inappropriate type of 'cesionario_rut'.")
        if not isinstance(self.monto, int):
            raise TypeError("Inappropriate type of 'monto'.")

        validate_cesion_monto(self.monto)

    @property
    def dte_emisor_rut(self) -> Rut:
        return self.dte_key.emisor_rut

    @property
    def dte_tipo_dte(self) -> TipoDteEnum:
        return self.dte_key.tipo_dte

    @property
    def dte_folio(self) -> int:
        return self.dte_key.folio


@dataclasses.dataclass(frozen=True)
class CesionDataL1(CesionDataL0):

    """
    Data of a "cesión" (level 1).

    """

    fecha_firma_dt_naive: datetime = dc_field()
    """
    Datetime of 'Firma del Archivo de Transferencias'

    .. warning::
        It is not equal to the datetime on which the SII received/processed
        the "cesión".

    """

    dte_receptor_rut: Rut = dc_field()
    """
    RUT of the "receptor" of the DTE.
    """

    dte_fecha_emision_date: date = dc_field()
    """
    Field 'fecha_emision' of the DTE.

    .. warning:: It may not match the **real date** on which the DTE was issued
        or received/processed by SII.

    """

    dte_monto_total: int = dc_field()
    """
    Total amount of the DTE.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        super().__post_init__()

        # TODO: validate value of 'fecha_firma_dt_naive', in relation to the DTE data.

        if not isinstance(self.fecha_firma_dt_naive, datetime):
            raise TypeError("Inappropriate type of 'fecha_firma_dt_naive'.")
        if not isinstance(self.dte_receptor_rut, Rut):
            raise TypeError("Inappropriate type of 'dte_receptor_rut'.")
        if not isinstance(self.dte_fecha_emision_date, date):
            raise TypeError("Inappropriate type of 'dte_fecha_emision_date'.")
        if not isinstance(self.dte_monto_total, int):
            raise TypeError("Inappropriate type of 'dte_monto_total'.")

    @property
    def dte_vendedor_rut(self) -> Rut:
        """
        Return the RUT of the DTE's "vendedor".

        :raises ValueError:
        """
        return self.get_dte_data_l1().vendedor_rut

    @property
    def dte_deudor_rut(self) -> Rut:
        """
        Return the RUT of the DTE's "deudor".

        :raises ValueError:
        """
        return self.get_dte_data_l1().deudor_rut

    def get_dte_data_l1(self) -> dte_data_models.DteDataL1:
        return dte_data_models.DteDataL1(
            emisor_rut=self.dte_key.emisor_rut,
            tipo_dte=self.dte_key.tipo_dte,
            folio=self.dte_key.folio,
            fecha_emision_date=self.dte_fecha_emision_date,
            receptor_rut=self.dte_receptor_rut,
            monto_total=self.dte_monto_total,
        )


@dataclasses.dataclass(frozen=True)
class CesionDataL2(CesionDataL1):

    """
    Data of a "cesión" (level 2).

    """

    ultimo_vencimiento_date: date = dc_field()
    """
    Date of "Ultimo Vencimiento".
    """

    cedente_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "cedente".
    """

    cedente_email: str = dc_field()
    """
    Email address of the "cedente".

    .. warning:: Value may be an invalid email address.
    """

    cesionario_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "cesionario".
    """

    cesionario_email: str = dc_field()
    """
    Email address of the "cesionario".

    .. warning:: Value may be an invalid email address.
    """

    dte_emisor_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "emisor" of the DTE.
    """

    # dte_emisor_email: str = dc_field()
    # """
    # Email address of the "emisor" of the DTE.
    #
    # .. warning:: Value may be an invalid email address.
    # """

    dte_receptor_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "receptor" of the DTE.
    """

    # dte_receptor_email: str = dc_field()
    # """
    # Email address of the "receptor" of the DTE.
    #
    # .. warning:: Value may be an invalid email address.
    # """

    dte_deudor_email: Optional[str] = dc_field(default=None)
    """
    Email address of the "deudor" of the DTE.

    .. warning:: Value may be an invalid email address.
    """

    cedente_declaracion_jurada: Optional[str] = dc_field(default=None)
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

    dte_fecha_vencimiento_date: Optional[date] = dc_field(default=None)
    """
    "Fecha de vencimiento (pago)" of the DTE.
    """

    contacto_nombre: Optional[str] = dc_field(default=None)
    """
    Name of the contact person.

    > Persona de Contacto para aclarar dudas.
    """

    contacto_telefono: Optional[str] = dc_field(default=None)
    """
    Phone number of the contact person.
    """

    contacto_email: Optional[str] = dc_field(default=None)
    """
    Email address of the contact person.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        super().__post_init__()

        # note: delegate some validation to 'dte_data_models.DteDataL2'.
        _ = self.get_dte_data_l2()

        # TODO: validate value of 'ultimo_vencimiento_date', in relation to the DTE data.

        if not isinstance(self.ultimo_vencimiento_date, date):
            raise TypeError("Inappropriate type of 'ultimo_vencimiento_date'.")

        if not isinstance(self.cedente_razon_social, str):
            raise TypeError("Inappropriate type of 'cedente_razon_social'.")
        validate_clean_str(self.cedente_razon_social)
        validate_non_empty_str(self.cedente_razon_social)

        if not isinstance(self.cedente_email, str):
            raise TypeError("Inappropriate type of 'cedente_email'.")
        validate_clean_str(self.cedente_email)
        validate_non_empty_str(self.cedente_email)

        if not isinstance(self.cesionario_razon_social, str):
            raise TypeError("Inappropriate type of 'cesionario_razon_social'.")
        validate_clean_str(self.cesionario_razon_social)
        validate_non_empty_str(self.cesionario_razon_social)

        if not isinstance(self.cesionario_email, str):
            raise TypeError("Inappropriate type of 'cesionario_email'.")
        validate_clean_str(self.cesionario_email)
        validate_non_empty_str(self.cesionario_email)

        if not isinstance(self.dte_emisor_razon_social, str):
            raise TypeError("Inappropriate type of 'dte_emisor_razon_social'.")
        validate_clean_str(self.dte_emisor_razon_social)
        validate_non_empty_str(self.dte_emisor_razon_social)

        # if not isinstance(self.dte_emisor_email, str):
        #     raise TypeError("Inappropriate type of 'dte_emisor_email'.")
        # validate_clean_str(self.dte_emisor_email)
        # validate_non_empty_str(self.dte_emisor_email)

        if not isinstance(self.dte_receptor_razon_social, str):
            raise TypeError("Inappropriate type of 'dte_receptor_razon_social'.")
        validate_clean_str(self.dte_receptor_razon_social)
        validate_non_empty_str(self.dte_receptor_razon_social)

        # if not isinstance(self.dte_receptor_email, str):
        #     raise TypeError("Inappropriate type of 'dte_receptor_email'.")
        # validate_clean_str(self.dte_receptor_email)
        # validate_non_empty_str(self.dte_receptor_email)

        if self.dte_deudor_email is not None:
            if not isinstance(self.dte_deudor_email, str):
                raise TypeError("Inappropriate type of 'dte_deudor_email'.")
            validate_clean_str(self.dte_deudor_email)
            validate_non_empty_str(self.dte_deudor_email)
        if self.cedente_declaracion_jurada is not None:
            if not isinstance(self.cedente_declaracion_jurada, str):
                raise TypeError("Inappropriate type of 'cedente_declaracion_jurada'.")
            # validate_clean_str(self.cedente_declaracion_jurada)
            validate_non_empty_str(self.cedente_declaracion_jurada)

        if self.contacto_nombre is not None:
            if not isinstance(self.contacto_nombre, str):
                raise TypeError("Inappropriate type of 'contacto_nombre'.")
            validate_clean_str(self.contacto_nombre)
            validate_non_empty_str(self.contacto_nombre)

        if self.contacto_telefono is not None:
            if not isinstance(self.contacto_telefono, str):
                raise TypeError("Inappropriate type of 'contacto_telefono'.")
            validate_clean_str(self.contacto_telefono)
            validate_non_empty_str(self.contacto_telefono)

        if self.contacto_email is not None:
            if not isinstance(self.contacto_email, str):
                raise TypeError("Inappropriate type of 'contacto_email'.")
            validate_clean_str(self.contacto_email)
            validate_non_empty_str(self.contacto_email)

        dte_data_models.validate_contribuyente_razon_social(self.cedente_razon_social)
        dte_data_models.validate_contribuyente_razon_social(self.cesionario_razon_social)
        dte_data_models.validate_contribuyente_razon_social(self.dte_emisor_razon_social)
        dte_data_models.validate_contribuyente_razon_social(self.dte_receptor_razon_social)

    def get_dte_data_l2(self) -> dte_data_models.DteDataL2:
        return dte_data_models.DteDataL2(
            emisor_rut=self.dte_key.emisor_rut,
            tipo_dte=self.dte_key.tipo_dte,
            folio=self.dte_key.folio,
            fecha_emision_date=self.dte_fecha_emision_date,
            receptor_rut=self.dte_receptor_rut,
            monto_total=self.dte_monto_total,
            emisor_razon_social=self.dte_emisor_razon_social,
            receptor_razon_social=self.dte_receptor_razon_social,
            fecha_vencimiento_date=self.dte_fecha_vencimiento_date,
        )
