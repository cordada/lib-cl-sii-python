from __future__ import annotations

import dataclasses
import logging
from datetime import date, datetime
from typing import Optional

import cl_sii.dte.data_models
from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte.constants import TipoDte
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from . import data_models
from .constants import CESION_MONTO_CEDIDO_FIELD_MIN_VALUE, TIPO_DTE_CEDIBLES


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CesionesPeriodoEntry:
    """
    Entry of a list of "cesiones" in a period.

    In case of doubts about the concepts (particularly for "vendedor" and
    "deudor"), read the documentation of :mod:`cl_sii.dte.data_models`.
    """

    ###########################################################################
    # fields of DTE
    ###########################################################################

    # In case of doubts about the concepts (particularly for 'vendedor' and 'deudor'),
    #   see 'cl_sii.dte.data_models'.

    dte_vendedor_rut: Rut
    """
    RUT of the DTE's "vendedor".
    """

    dte_deudor_rut: Rut
    """
    RUT of the DTE's "deudor".
    """

    dte_tipo_dte: TipoDte
    """
    The DTE's "tipo DTE" (sighs).
    """

    dte_folio: int
    """
    The sequential number of the DTE of given kind issued by 'emisor_rut'.
    """

    dte_fecha_emision: date
    """
    Field 'fecha_emision' of the DTE.

    .. warning:: It may not match the **real date** on which the DTE was issued
        or received/processed by SII.
    """

    dte_monto_total: int
    """
    Total amount of the DTE.
    """

    ###########################################################################
    # fields of "cesion"
    ###########################################################################

    cedente_rut: Rut
    """
    RUT of the "cedente".
    """

    cedente_razon_social: str
    """
    "Razón social" (legal name) of the "cedente".
    """

    cedente_email: Optional[str]
    """
    Email address of the "cedente".
    """

    cesionario_rut: Rut
    """
    RUT of the "cesionario".
    """

    cesionario_razon_social: str
    """
    "Razón social" (legal name) of the "cesionario".
    """

    cesionario_emails: Optional[str]
    """
    Email address(es) of the "cesionario".
    """

    # note: this is not a field of the DTE even though 'dte_deudor_rut' is.
    deudor_email: Optional[str]
    """
    Email address of the "deudor".
    """

    fecha_cesion_dt: datetime
    """
    Datetime on which the "cesion" happened.

    Must be consistent with ``fecha_cesion`` (considering timezone).

    .. note:: This is the timestamp of when the "cesión"'s AEC was digitally
        signed, but truncated to the minute (AEC's timestamp has seconds,
        this one only has minutes).

    ..seealso:: Docstring of :attr:`data_models.CesionL0.fecha_cesion_dt`.
    """

    fecha_cesion: date
    """
    Date on which the "cesion" happened.

    Must be consistent with ``fecha_cesion_dt`` (considering timezone).
    """

    # TODO: find out if there is a valid case for which it can be different from 'dte_monto_total'.
    monto_cedido: int
    """
    Amount of the "cesion" ("monto del crédito cedido").
    """

    fecha_ultimo_vencimiento: date
    """
    "Fecha del último vencimiento del pago".

    Even though the DTE field ``fecha_vencimiento`` is optional, this field
    of the "cesión" is mandatory.
    """

    estado: str
    """
    "Estado" of the "cesion".
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        #######################################################################
        # fields of DTE
        #######################################################################

        if not isinstance(self.dte_vendedor_rut, Rut):
            raise TypeError("Inappropriate type of 'dte_vendedor_rut'.")

        if not isinstance(self.dte_deudor_rut, Rut):
            raise TypeError("Inappropriate type of 'dte_deudor_rut'.")

        if not isinstance(self.dte_tipo_dte, TipoDte):
            raise TypeError("Inappropriate type of 'dte_tipo_dte'.")
        if self.dte_tipo_dte not in TIPO_DTE_CEDIBLES:
            raise ValueError(
                "The \"tipo DTE\" in 'dte_tipo_dte' is not \"cedible\".",
                self.dte_tipo_dte,
            )

        if not isinstance(self.dte_folio, int):
            raise TypeError("Inappropriate type of 'dte_folio'.")
        if not self.dte_folio > 0:
            raise ValueError("Inappropriate value of 'dte_folio'.")

        if not isinstance(self.dte_fecha_emision, date):
            raise TypeError("Inappropriate type of 'dte_fecha_emision'.")

        # TODO: figure out validation rules of 'dte_monto_total'
        if not isinstance(self.dte_monto_total, int):
            raise TypeError("Inappropriate type of 'dte_monto_total'.")

        #######################################################################
        # fields of "cesion"
        #######################################################################

        if not isinstance(self.cedente_rut, Rut):
            raise TypeError("Inappropriate type of 'cedente_rut'.")

        if not isinstance(self.cedente_razon_social, str):
            raise TypeError("Inappropriate type of 'cedente_razon_social'.")
        cl_sii.dte.data_models.validate_contribuyente_razon_social(self.cedente_razon_social)

        if self.cedente_email is not None:
            if not isinstance(self.cedente_email, str):
                raise TypeError("Inappropriate type of 'cedente_email'.")
            cl_sii.dte.data_models.validate_clean_str(self.cedente_email)
            cl_sii.dte.data_models.validate_non_empty_str(self.cedente_email)

        if not isinstance(self.cesionario_rut, Rut):
            raise TypeError("Inappropriate type of 'cesionario_rut'.")

        if not isinstance(self.cesionario_razon_social, str):
            raise TypeError("Inappropriate type of 'cesionario_razon_social'.")
        cl_sii.dte.data_models.validate_contribuyente_razon_social(self.cesionario_razon_social)

        if self.cesionario_emails is not None:
            if not isinstance(self.cesionario_emails, str):
                raise TypeError("Inappropriate type of 'cesionario_emails'.")
            cl_sii.dte.data_models.validate_clean_str(self.cesionario_emails)
            cl_sii.dte.data_models.validate_non_empty_str(self.cesionario_emails)

        if self.deudor_email is not None:
            if not isinstance(self.deudor_email, str):
                raise TypeError("Inappropriate type of 'deudor_email'.")
            cl_sii.dte.data_models.validate_clean_str(self.deudor_email)
            cl_sii.dte.data_models.validate_non_empty_str(self.deudor_email)

        if not isinstance(self.fecha_cesion_dt, datetime):
            raise TypeError("Inappropriate type of 'fecha_cesion_dt'.")
        tz_utils.validate_dt_tz(self.fecha_cesion_dt, SII_OFFICIAL_TZ)

        if not isinstance(self.fecha_cesion, date):
            raise TypeError("Inappropriate type of 'fecha_cesion'.")
        if self.fecha_cesion_dt.date() != self.fecha_cesion:
            raise ValueError(
                "Date of 'fecha_cesion_dt' (considering timezone) does not match 'fecha_cesion'.",
                self.fecha_cesion_dt,
                self.fecha_cesion,
            )

        if not isinstance(self.monto_cedido, int):
            raise TypeError("Inappropriate type of 'monto_cedido'.")
        if not self.monto_cedido >= CESION_MONTO_CEDIDO_FIELD_MIN_VALUE:
            raise ValueError(
                f"Amount 'monto_cedido' must be >= {CESION_MONTO_CEDIDO_FIELD_MIN_VALUE}.",
                self.monto_cedido,
            )
        data_models.validate_cesion_and_dte_montos(
            cesion_value=self.monto_cedido,
            dte_value=self.dte_monto_total,
        )

        if not isinstance(self.fecha_ultimo_vencimiento, date):
            raise TypeError("Inappropriate type of 'fecha_ultimo_vencimiento'.")

        if not isinstance(self.estado, str):
            raise TypeError("Inappropriate type of 'estado'.")
        cl_sii.dte.data_models.validate_clean_str(self.estado)
        cl_sii.dte.data_models.validate_non_empty_str(self.estado)

    @property
    def monto_cedido_eq_dte_monto_total(self) -> bool:
        return self.monto_cedido == self.dte_monto_total

    def as_dte_data_l1(self) -> cl_sii.dte.data_models.DteDataL1:
        if self.dte_tipo_dte.emisor_is_vendedor:
            dte_emisor_rut = self.dte_vendedor_rut
            dte_receptor_rut = self.dte_deudor_rut
        elif self.dte_tipo_dte.receptor_is_vendedor:
            dte_emisor_rut = self.dte_deudor_rut
            dte_receptor_rut = self.dte_vendedor_rut
        else:
            raise ValueError(
                'Programming error: the "vendedor" is neither the "emisor" nor the "vendedor".',
                self,
            )

        try:
            dte_data = cl_sii.dte.data_models.DteDataL1(
                emisor_rut=dte_emisor_rut,
                tipo_dte=self.dte_tipo_dte,
                folio=self.dte_folio,
                fecha_emision_date=self.dte_fecha_emision,
                receptor_rut=dte_receptor_rut,
                monto_total=self.dte_monto_total,
            )
        except (TypeError, ValueError):
            raise

        return dte_data

    def as_cesion_l2(self) -> data_models.CesionL2:
        dte = self.as_dte_data_l1()

        return data_models.CesionL2(
            dte_key=dte.natural_key,
            seq=None,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
            monto_cedido=self.monto_cedido,
            dte_receptor_rut=dte.receptor_rut,
            dte_fecha_emision=dte.fecha_emision_date,
            dte_monto_total=dte.monto_total,
            fecha_ultimo_vencimiento=self.fecha_ultimo_vencimiento,
            cedente_razon_social=self.cedente_razon_social,
            cedente_email=self.cedente_email,
            cesionario_razon_social=self.cesionario_razon_social,
            cesionario_email=self.cesionario_emails,
        )
