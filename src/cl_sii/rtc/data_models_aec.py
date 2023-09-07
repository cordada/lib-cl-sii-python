"""
Data models for RTC AEC XML docs/files
======================================
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
from typing import ClassVar, Mapping, Optional, Sequence, Tuple

import pydantic

from cl_sii.base.constants import SII_OFFICIAL_TZ
from cl_sii.dte import data_models as dte_data_models
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut
from . import data_models


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
class CesionAecXml:
    """
    Data in XML element ``sii-dte:Cesion`` in an AEC XML doc.

    ..seealso::
        XML schema of ``{http://www.sii.cl/SiiDte}/Cesion`` in
        'data/ref/factura_electronica/schemas-xml/Cesion_v10.xsd' (c7adc5a2)

    ..note:: An AEC XML doc includes one or more ``Cesion`` XML elements.

    Excluded XML elements:

    * ``sii-dte:DocumentoCesion/sii-dte:OtrasCondiciones`` (0..1 occurrences)
    * ``ds:Signature`` (1..3 occurrences)
    """

    ###########################################################################
    # Constants
    ###########################################################################

    DATETIME_FIELDS_TZ: ClassVar[tz_utils.PytzTimezone] = SII_OFFICIAL_TZ

    ###########################################################################
    # Fields
    ###########################################################################

    dte: dte_data_models.DteDataL1
    """
    DTE of the "cesión".

    AEC doc XML elements:
    * '...//Cesion//DocumentoCesion//IdDTE//RUTEmisor'
    * '...//Cesion//DocumentoCesion//IdDTE//TipoDTE'
    * '...//Cesion//DocumentoCesion//IdDTE//Folio'
    * '...//Cesion//DocumentoCesion//IdDTE//FchEmis'
    * '...//Cesion//DocumentoCesion//IdDTE//RUTReceptor'
    * '...//Cesion//DocumentoCesion//IdDTE//MntTotal'

    RPETC email:
    * attachment / 'Documento Cedido' / (initial text before ' - Monto Total')
    * attachment / 'Documento Cedido' / 'Emisor'
    * attachment / 'Documento Cedido' / 'Receptor'
    * attachment / 'Documento Cedido' / 'Fecha Emision'
    """

    seq: int
    """
    Sequence number of the "cesión". Must be >= 1.

    AEC doc XML element: '..//Cesion//DocumentoCesion//SeqCesion'

    RPETC email: attachment / 'Cesion' / 'Seq'
    """

    cedente_rut: Rut
    """
    RUT of the "cedente".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cedente//RUT'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cesionario_rut: Rut
    """
    RUT of the "cesionario".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cesionario//RUT'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    monto_cesion: int
    """
    Amount of the "cesión".

    AEC doc XML element: '..//Cesion//DocumentoCesion//MontoCesion'

    RPETC email: attachment / 'Cesion' / 'Monto Cedido'
    """

    fecha_cesion_dt: datetime
    """
    Datetime of "cesión".

    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    > TimeStamp de la Cesion del DTE.

    AEC doc XML element: '..//Cesion//DocumentoCesion//TmstCesion'

    RPETC email: attachment / 'Cesion' / 'Fecha de la Cesion'
    """

    fecha_ultimo_vencimiento: date
    """
    Date of "Ultimo Vencimiento".

    e.g. `2019-04-28` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element: '..//Cesion//DocumentoCesion//UltimoVencimiento'

    RPETC email: attachment / 'Cesion' / 'Ultimo Vencimiento'
    """

    cedente_razon_social: str
    """
    "Razón social" (legal name) of the "cedente".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cedente//RazonSocial'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cedente_direccion: str = dataclasses.field(repr=False)
    """
    Address ("Dirección") of the "cedente".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cedente//Direccion'

    RPETC email: attachment / 'Cedente' / 'Direccion'
    """

    cedente_email: str = dataclasses.field(repr=False)
    """
    Email address of the "cedente".

    .. warning:: Value may be an invalid email address.

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cedente//eMail'

    RPETC email: attachment / 'Cedente' / 'eMail'
    """

    cedente_persona_autorizada_rut: Rut
    """
    "Persona Autorizada" by the "cedente" to "Firmar la Transferencia" (RUT).

    .. note:: It might be the "cedente" itself, a "persona natural", etc.

    First of the
    > Lista de Personas Autorizadas por el Cedente a Firmar la Transferencia

    AEC doc XML element (1..3 occurrences of 'RUTAutorizado'):
        '..//Cesion//DocumentoCesion//Cedente//RUTAutorizado//RUT'
    """

    cedente_persona_autorizada_nombre: Optional[str]
    """
    "Persona Autorizada" by the "cedente" to "Firmar la Transferencia" (name).

    .. note:: It might be the "cedente" itself, a "persona natural", etc. There is a
    contradiction regarding the element ``Nombre de la persona autorizada`` about what
    the technical documentation states and how it was implemented in the XML schema.
    Although the former defines the field as required, the XML schema does not set a
    minimum required length, so the field can be empty.

    First of the
    > Lista de Personas Autorizadas por el Cedente a Firmar la Transferencia

    AEC doc XML element (1..3 occurrences of 'RUTAutorizado'):
        '..//Cesion//DocumentoCesion//Cedente//RUTAutorizado//Nombre'

    .. seealso::
        https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/99b15aff252836e1ac311d243636aa3a9e6b89c6/src/docs/rtc/2013-02-11-formato-archivo-electronico-cesion.pdf
        https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/99b15aff252836e1ac311d243636aa3a9e6b89c6/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/SiiTypes_v10.xsd#L682-L689
    """

    cesionario_razon_social: str
    """
    "Razón social" (legal name) of the "cesionario".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cesionario//RazonSocial'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    cesionario_direccion: str = dataclasses.field(repr=False)
    """
    Address ("Dirección") of the "cesionario".

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cesionario//Direccion'

    RPETC email: attachment / 'Cesionario' / 'Direccion'
    """

    cesionario_email: str = dataclasses.field(repr=False)
    """
    Email address of the "cesionario".

    .. warning:: Value may be an invalid email address.

    AEC doc XML element: '..//Cesion//DocumentoCesion//Cesionario//eMail'

    RPETC email: attachment / 'Cesionario' / 'eMail'
    """

    dte_deudor_email: Optional[str] = dataclasses.field(default=None, repr=False)
    """
    Email address of the "deudor" of the DTE.

    .. warning:: Value may be an invalid email address.

    AEC doc XML element: '..//Cesion//DocumentoCesion//eMailDeudor'

    RPETC email: no.
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

    AEC doc XML element (optional): '..//Cesion//DocumentoCesion//Cedente//DeclaracionJurada'

    RPETC email: attachment / 'Cesion' / 'Declaracion Jurada'
    **but only whether "declaración jurada" was included or not**,
    not the "declaración jurada" itself.
    """

    @property
    def natural_key(self) -> data_models.CesionNaturalKey:
        return data_models.CesionNaturalKey(dte_key=self.dte.natural_key, seq=self.seq)

    @property
    def alt_natural_key(self) -> data_models.CesionAltNaturalKey:
        return data_models.CesionAltNaturalKey(
            dte_key=self.dte.natural_key,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
        )

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_cesion_l2(self) -> data_models.CesionL2:
        return data_models.CesionL2(
            dte_key=self.dte.natural_key,
            seq=self.seq,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
            monto_cedido=self.monto_cesion,
            dte_receptor_rut=self.dte.receptor_rut,
            dte_fecha_emision=self.dte.fecha_emision_date,
            dte_monto_total=self.dte.monto_total,
            fecha_ultimo_vencimiento=self.fecha_ultimo_vencimiento,
            cedente_razon_social=self.cedente_razon_social,
            cedente_email=self.cedente_email,
            cesionario_razon_social=self.cesionario_razon_social,
            cesionario_email=self.cesionario_email,
            dte_deudor_email=self.dte_deudor_email,
            cedente_declaracion_jurada=self.cedente_declaracion_jurada,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte')
    def validate_dte_tipo_dte(cls, v: object) -> object:
        if isinstance(v, dte_data_models.DteDataL0):
            data_models.validate_cesion_dte_tipo_dte(v.tipo_dte)
        return v

    @pydantic.validator('seq')
    def validate_seq(cls, v: object) -> object:
        if isinstance(v, int):
            data_models.validate_cesion_seq(v)
        return v

    @pydantic.validator('monto_cesion')
    def validate_monto_cesion(cls, v: object) -> object:
        if isinstance(v, int):
            data_models.validate_cesion_monto(v)
        return v

    @pydantic.validator(
        'cedente_razon_social',
        'cesionario_razon_social',
    )
    def validate_contribuyente_razon_social(cls, v: object) -> object:
        if isinstance(v, str):
            dte_data_models.validate_contribuyente_razon_social(v)
        return v

    @pydantic.validator('fecha_cesion_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_fecha_cesion_dt_is_consistent_with_dte(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        fecha_cesion_dt = values['fecha_cesion_dt']
        dte = values['dte']

        if isinstance(fecha_cesion_dt, datetime) and isinstance(dte, dte_data_models.DteDataL1):
            pass  # TODO: Validate value of 'fecha_cesion_dt' in relation to the DTE data.

        return values

    @pydantic.root_validator(skip_on_failure=True)
    def validate_monto_cesion_does_not_exceed_dte_monto_total(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        monto_cesion = values['monto_cesion']
        dte = values['dte']

        if isinstance(monto_cesion, int) and isinstance(dte, dte_data_models.DteDataL1):
            data_models.validate_cesion_and_dte_montos(
                cesion_value=monto_cesion,
                dte_value=dte.monto_total,
            )

        return values

    @pydantic.root_validator(skip_on_failure=True)
    def validate_fecha_ultimo_vencimiento_is_consistent_with_dte(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        fecha_ultimo_vencimiento = values['fecha_ultimo_vencimiento']
        dte = values['dte']

        if isinstance(fecha_ultimo_vencimiento, date) and isinstance(
            dte, dte_data_models.DteDataL1
        ):
            pass  # TODO: Validate value of 'fecha_ultimo_vencimiento' in relation to the DTE data.

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
class AecXml:
    """
    Data in a "cesión"'s AEC XML doc.

    ..seealso::
        XML schema of ``{http://www.sii.cl/SiiDte}/AEC`` in
        'data/ref/factura_electronica/schemas-xml/AEC_v10.xsd' (c7adc5a2)

    XML signatures
    --------------

    For now, all the XML signatures are excluded from this model.

    Inside the ``<AEC>`` XML element there are 3 XML signatures:

    1) 'sii-dte:AEC/ds:Signature'
      (over ``<DocumentoAEC>``)

    2) 'sii-dte:AEC/sii-dte:DocumentoAEC/sii-dte:Cesiones/sii-dte:DTECedido/
        ds:Signature'
      (over ``<DocumentoDTECedido>``)

    3) 'sii-dte:AEC/sii-dte:DocumentoAEC/sii-dte:Cesiones/sii-dte:DTECedido/
        sii-dte:DocumentoDTECedido/sii-dte:DTE/ds:Signature'
      (over ``<Documento>``)

    Plus 1, 2 or 3 per "cesión":

    'sii-dte:AEC/sii-dte:DocumentoAEC/sii-dte:Cesiones/sii-dte:Cesion/ds:Signature'
      (over ``<DocumentoCesion>``)
     Ref: data/ref/factura_electronica/schemas-xml/Cesion_v10.xsd#L222-L226 (c7adc5a2)

    Thus the minimum total number of XML signatures is 4.
    """

    ###########################################################################
    # Constants
    ###########################################################################

    DATETIME_FIELDS_TZ: ClassVar[tz_utils.PytzTimezone] = SII_OFFICIAL_TZ

    ###########################################################################
    # Fields
    ###########################################################################

    dte: dte_data_models.DteXmlData
    """
    DTE that was "cedido".

    AEC doc XML element: 'DocumentoAEC//Cesiones//DTECedido//DocumentoDTECedido//DTE'

    RPETC email: attachment / 'Documento Cedido'
    """

    cedente_rut: Rut
    """
    RUT of the "cedente".

    > RUT que Genera el Archivo de Transferencias.

    AEC doc XML element: 'DocumentoAEC//Caratula//RutCedente'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cesionario_rut: Rut
    """
    RUT of the "cesionario".

    > RUT a Quien Va Dirigido el Archivo de Transferencias.

    AEC doc XML element: 'DocumentoAEC//Caratula//RutCesionario'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    fecha_firma_dt: datetime
    """
    Datetime of 'Firma del Archivo de Transferencias'

    > Fecha y Hora de la Firma del Archivo de Transferencias.

    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element: 'DocumentoAEC//Caratula//TmstFirmaEnvio'

    RPETC email: attachment / 'Cesion' / 'Fecha de la Cesion'
    """

    signature_value: Optional[bytes] = dataclasses.field(repr=False)
    """
    AEC's digital signature's value (raw bytes, without base64 encoding).

    Signature is over AEC doc XML element: 'DocumentoAEC'

    AEC doc XML element: 'Signature/SignatureValue'
    """

    signature_x509_cert_der: Optional[bytes] = dataclasses.field(repr=False)
    """
    AEC's digital signature's DER-encoded X.509 certificate.

    Signature is over AEC doc XML element: 'DocumentoAEC'

    AEC doc XML element: 'Signature/KeyInfo/X509Data/X509Certificate'

    .. seealso::
        Functions :func:`cl_sii.libs.crypto_utils.load_der_x509_cert`
        and :func:`cl_sii.libs.crypto_utils.x509_cert_der_to_pem`.
    """

    cesiones: Sequence[CesionAecXml]
    """
    List of structs for ``sii-dte:Cesion`` XML elements.

    ..warning::
        The items MUST be ordered according to their ``seq``, starting with
        the first "cesión" of the DTE (i.e. with ``seq = 1``).
    """

    contacto_nombre: Optional[str] = None
    """
    Name of the contact person.

    > Persona de Contacto para aclarar dudas.

    AEC doc XML element: 'DocumentoAEC//Caratula//NmbContacto'

    RPETC email: none.
    """

    contacto_telefono: Optional[str] = None
    """
    Phone number of the contact person.

    > Telefono de Contacto.

    AEC doc XML element: 'DocumentoAEC//Caratula//FonoContacto'

    RPETC email: none.
    """

    contacto_email: Optional[str] = None
    """
    Email address of the contact person.

    > Correo Electronico de Contacto.

    .. warning:: Value may be an invalid email address.

    AEC doc XML element: 'DocumentoAEC//Caratula//MailContacto'

    RPETC email: none.
    """

    @property
    def _last_cesion(self) -> CesionAecXml:
        return self.cesiones[-1]

    @property
    def seq(self) -> int:
        """
        Sequence number of the "cesión". Must be >= 1.

        Value is not directly available from the XML element. It needs
        to be extracted from the latest ``<Cesion>`` in 'DocumentoAEC//Cesiones'.

        AEC doc XML element: no direct one.

        RPETC email: attachment / 'Cesion' / 'Seq'
        """
        return self._last_cesion.seq

    @property
    def monto_cesion(self) -> int:
        """
        Amount of the "cesión".

        Value is not directly available from the XML element. It needs
        to be extracted from the latest ``<Cesion>`` in 'DocumentoAEC//Cesiones'.

        AEC doc XML element: no direct one.

        RPETC email: attachment / 'Cesion' / 'Monto Cedido'
        """
        return self._last_cesion.monto_cesion

    @property
    def fecha_cesion_dt(self) -> datetime:
        return self._last_cesion.fecha_cesion_dt

    @property
    def fecha_ultimo_vencimiento(self) -> date:
        return self._last_cesion.fecha_ultimo_vencimiento

    @property
    def cedente_razon_social(self) -> str:
        return self._last_cesion.cedente_razon_social

    @property
    def cedente_direccion(self) -> str:
        return self._last_cesion.cedente_direccion

    @property
    def cedente_email(self) -> str:
        return self._last_cesion.cedente_email

    @property
    def cesionario_razon_social(self) -> str:
        return self._last_cesion.cesionario_razon_social

    @property
    def cesionario_direccion(self) -> str:
        return self._last_cesion.cesionario_direccion

    @property
    def cesionario_email(self) -> str:
        return self._last_cesion.cesionario_email

    @property
    def dte_emisor_email(self) -> str:
        raise NotImplementedError

    @property
    def dte_receptor_email(self) -> str:
        raise NotImplementedError

    @property
    def dte_deudor_email(self) -> Optional[str]:
        return self._last_cesion.dte_deudor_email

    @property
    def cedente_declaracion_jurada(self) -> Optional[str]:
        return self._last_cesion.cedente_declaracion_jurada

    @property
    def natural_key(self) -> data_models.CesionNaturalKey:
        return data_models.CesionNaturalKey(dte_key=self.dte.natural_key, seq=self.seq)

    @property
    def alt_natural_key(self) -> data_models.CesionAltNaturalKey:
        return data_models.CesionAltNaturalKey(
            dte_key=self.dte.natural_key,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
        )

    @property
    def slug(self) -> str:
        """
        Return a slug representation (that preserves uniquess) of the instance.
        """
        # Note: Based on 'cl_sii.dte.data_models.DteNaturalKey.slug'.
        return self.natural_key.slug

    ###########################################################################
    # Custom Methods
    ###########################################################################

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    def as_cesion_l2(self) -> data_models.CesionL2:
        return data_models.CesionL2(
            dte_key=self.dte.natural_key,
            seq=self.seq,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            fecha_cesion_dt=self.fecha_cesion_dt,
            monto_cedido=self.monto_cesion,
            fecha_firma_dt=self.fecha_firma_dt,
            dte_receptor_rut=self.dte.receptor_rut,
            dte_fecha_emision=self.dte.fecha_emision_date,
            dte_monto_total=self.dte.monto_total,
            fecha_ultimo_vencimiento=self.fecha_ultimo_vencimiento,
            cedente_razon_social=self.cedente_razon_social,
            cedente_email=self.cedente_email,
            cesionario_razon_social=self.cesionario_razon_social,
            cesionario_email=self.cesionario_email,
            dte_emisor_razon_social=self.dte.emisor_razon_social,
            # dte_emisor_email=None,
            dte_receptor_razon_social=self.dte.receptor_razon_social,
            # dte_receptor_email=None,
            dte_deudor_email=self.dte_deudor_email,
            cedente_declaracion_jurada=self.cedente_declaracion_jurada,
            dte_fecha_vencimiento=self.dte.fecha_vencimiento_date,
            contacto_nombre=self.contacto_nombre,
            contacto_telefono=self.contacto_telefono,
            contacto_email=self.contacto_email,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte')
    def validate_dte_tipo_dte(cls, v: object) -> object:
        if isinstance(v, dte_data_models.DteDataL0):
            data_models.validate_cesion_dte_tipo_dte(v.tipo_dte)
        return v

    @pydantic.validator('fecha_firma_dt')
    def validate_datetime_tz(cls, v: object) -> object:
        if isinstance(v, datetime):
            tz_utils.validate_dt_tz(v, cls.DATETIME_FIELDS_TZ)
        return v

    @pydantic.validator('cesiones')
    def validate_cesiones_min_items(cls, v: object) -> object:
        if isinstance(v, Sequence):
            if len(v) < 1:
                raise ValueError("must contain at least one item")
        return v

    @pydantic.validator('cesiones')
    def validate_cesiones_seq_order(cls, v: object) -> object:
        if isinstance(v, Sequence):
            for idx, cesion in enumerate(v, start=1):
                if cesion.seq != idx:
                    raise ValueError("items must be ordered according to their 'seq'")
        return v

    # Note: Even though this validation seems to make perfect sense, there are some
    # real cases of SII-approved AEC where this is not fulfilled.
    # We will keep this validation in case we need it in the future.
    # @pydantic.validator('cesiones')
    # def validate_cesiones_monto_cesion_must_not_increase(cls, v: object) -> object:
    #     if isinstance(v, Sequence):
    #         if len(v) >= 2:
    #             previous_cesion: Optional[CesionAecXml] = None
    #             for cesion in v:
    #                 if previous_cesion is not None:
    #                     if not (cesion.monto_cesion <= previous_cesion.monto_cesion):
    #                         raise ValueError(
    #                             "items must have a 'monto_cesion'"
    #                             " that does not exceed the previous item's 'monto_cesion'.",
    #                         )
    #                 previous_cesion = cesion

    #     return v

    @pydantic.root_validator(skip_on_failure=True)
    def validate_dte_matches_cesiones_dtes(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        dte = values['dte']
        cesiones = values['cesiones']

        if isinstance(dte, dte_data_models.DteXmlData) and isinstance(cesiones, Sequence):
            if cesiones:
                dte_l1 = dte.as_dte_data_l1()

                for cesion in cesiones:
                    assert isinstance(cesion, CesionAecXml)
                    if cesion.dte != dte_l1:
                        raise ValueError(
                            f"'dte' of {cesion.__class__.__name__} with {cesion.natural_key!r}"
                            f" must match {dte_l1.__class__.__name__} with {dte_l1.natural_key}.",
                        )

        return values

    @pydantic.root_validator(skip_on_failure=True)
    def validate_last_cesion_matches_some_fields(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        field_validations: Sequence[Tuple[str, str]] = [
            # (AecXml field, CesionAecXml field):
            # Even though it seems reasonable to expect that the date in `fecha_firma_dt`
            # in the AEC is later than the date in `fecha_cesion_dt`, we know of cases of
            # AEC approved by the SII in which this is not fulfilled, we observe cases
            # where the date in `fecha_firma_dt` was later or even before the date in
            # `fecha_cesion_dt` by a difference of up to 6 hours.
            # ('fecha_firma_dt', 'fecha_cesion_dt'),
            ('cedente_rut', 'cedente_rut'),
            ('cesionario_rut', 'cesionario_rut'),
        ]

        cesiones = values['cesiones']
        if isinstance(cesiones, Sequence):
            if cesiones:
                last_cesion = cesiones[-1]

                for self_field, last_cesion_field in field_validations:
                    self_value = values.get(self_field)
                    last_cesion_value = getattr(last_cesion, last_cesion_field)

                    if self_value != last_cesion_value:
                        raise ValueError(
                            f"{last_cesion_field!r} of last 'cesion' must match {self_field!r}:"
                            f" {last_cesion_value!r} != {self_value!r}.",
                        )

        return values

    @pydantic.root_validator
    def validate_signature_value_and_signature_x509_cert_der_may_only_be_none_together(
        cls,
        values: Mapping[str, object],
    ) -> Mapping[str, object]:
        signature_value = values.get('signature_value')
        signature_x509_cert_der = values.get('signature_x509_cert_der')

        if not (
            (signature_value is None and signature_x509_cert_der is None)
            or (signature_value is not None and signature_x509_cert_der is not None)
        ):
            raise TypeError(
                "'signature_value' and 'signature_x509_cert_der'"
                " must either both be None or both be not None."
            )

        return values
