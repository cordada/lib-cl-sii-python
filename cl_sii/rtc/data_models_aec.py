"""
Data models for RTC AEC XML docs/files
======================================

"""
from __future__ import annotations

import dataclasses
from dataclasses import field as dc_field
from datetime import date, datetime
from typing import Mapping, Optional, Sequence

from cl_sii.dte import data_models as dte_data_models
from cl_sii.rut import Rut

from . import data_models
from .data_models import validate_clean_str, validate_non_empty_str


@dataclasses.dataclass(frozen=True)
class AecXmlData:

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

    # TODO: after we implement a proper DTE XML data model, use that instead.
    dte: dte_data_models.DteDataL2 = dc_field()
    """
    DTE that was "cedido".

    AEC doc XML element:
        'DocumentoAEC//Cesiones//DTECedido//DocumentoDTECedido//DTE'

    RPETC email: attachment / 'Documento Cedido'
    """

    cedente_rut: Rut = dc_field()
    """
    RUT of the "cedente".

    > RUT que Genera el Archivo de Transferencias.

    AEC doc XML element:
        'DocumentoAEC//Caratula//RutCedente'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cesionario_rut: Rut = dc_field()
    """
    RUT of the "cesionario".

    > RUT a Quien Va Dirigido el Archivo de Transferencias.

    AEC doc XML element:
        'DocumentoAEC//Caratula//RutCesionario'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    fecha_firma_dt_naive: datetime = dc_field()
    """
    Datetime of 'Firma del Archivo de Transferencias'

    > Fecha y Hora de la Firma del Archivo de Transferencias.

    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element:
        'DocumentoAEC//Caratula//TmstFirmaEnvio'

    RPETC email: attachment / 'Cesion' / 'Fecha de la Cesion'
    """

    cesiones: Sequence[AecXmlCesionData] = dc_field()
    """
    List of structs for ``sii-dte:Cesion`` XML elements.

    ..warning::
        The items MUST be ordered according to their ``seq``, starting with
        the first "cesión" of the DTE (i.e. with ``seq = 1``).

    """

    contacto_nombre: Optional[str] = dc_field(default=None)
    """
    Name of the contact person.

    > Persona de Contacto para aclarar dudas.

    AEC doc XML element:
        'DocumentoAEC//Caratula//NmbContacto'

    RPETC email: none.
    """

    contacto_telefono: Optional[str] = dc_field(default=None)
    """
    Phone number of the contact person.

    > Telefono de Contacto.

    AEC doc XML element:
        'DocumentoAEC//Caratula//FonoContacto'

    RPETC email: none.
    """

    contacto_email: Optional[str] = dc_field(default=None)
    """
    Email address of the contact person.

    > Correo Electronico de Contacto.

    .. warning:: Value may be an invalid email address.

    AEC doc XML element:
        'DocumentoAEC//Caratula//MailContacto'

    RPETC email: none.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        if not isinstance(self.cedente_rut, Rut):
            raise TypeError("Inappropriate type of 'cedente_rut'.")
        if not isinstance(self.cesionario_rut, Rut):
            raise TypeError("Inappropriate type of 'cesionario_rut'.")
        if not isinstance(self.fecha_firma_dt_naive, datetime):
            raise TypeError("Inappropriate type of 'fecha_firma_dt_naive'.")

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

        self._validate_cesiones()

    @property
    def _last_cesion(self) -> AecXmlCesionData:
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
    def monto(self) -> int:
        """
        Amount of the "cesión".

        Value is not directly available from the XML element. It needs
        to be extracted from the latest ``<Cesion>`` in 'DocumentoAEC//Cesiones'.

        AEC doc XML element: no direct one.

        RPETC email: attachment / 'Cesion' / 'Monto Cedido'
        """
        return self._last_cesion.monto

    @property
    def natural_key(self) -> data_models.CesionNaturalKey:
        return data_models.CesionNaturalKey(dte_key=self.dte.natural_key, seq=self.seq)

    @property
    def slug(self) -> str:
        """
        Return an slug representation (that preserves uniquess) of the instance.
        """
        # note: based on 'cl_sii.dte.data_models.DteNaturalKey.slug'

        return f'{self.dte.slug}--{self.seq}'

    def as_dict(self) -> Mapping[str, object]:
        return dataclasses.asdict(self)

    def _validate_cesiones(self) -> None:
        # TODO: validate that
        #   - 'fecha_firma_dt_naive' matches the last cesion's 'fecha_cesion_dt_naive'.
        #   - 'cedente_rut' matches the last cesion's 'cedente_rut'.
        #   - 'cesionario_rut' matches the last cesion's 'cesionario_rut'.
        #   - Each 'AecXmlCesionData.dte' must match the 'AecXmlData.dte'.

        if len(self.cesiones) == 0:
            raise ValueError("'cesiones' must be a non-empty list of 'AecXmlCesionData'.")

        for ix, cesion in enumerate(self.cesiones, start=1):
            if not isinstance(cesion, AecXmlCesionData):
                raise TypeError("Inappropriate type of item in 'cesiones'.")
            if cesion.seq != ix:
                raise ValueError(
                    "The items in 'cesiones' must be ordered according to their 'seq'.")

    @property
    def ultimo_vencimiento_date(self) -> date:
        return self._last_cesion.ultimo_vencimiento_date

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

    def get_cesion_l2(self) -> data_models.CesionDataL2:
        return data_models.CesionDataL2(
            dte_key=self.dte.natural_key,
            seq=self.seq,
            cedente_rut=self.cedente_rut,
            cesionario_rut=self.cesionario_rut,
            monto=self.monto,
            fecha_firma_dt_naive=self.fecha_firma_dt_naive,
            dte_receptor_rut=self.dte.receptor_rut,
            dte_fecha_emision_date=self.dte.fecha_emision_date,
            dte_monto_total=self.dte.monto_total,
            ultimo_vencimiento_date=self.ultimo_vencimiento_date,
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
            dte_fecha_vencimiento_date=self.dte.fecha_vencimiento_date,
            contacto_nombre=self.contacto_nombre,
            contacto_telefono=self.contacto_telefono,
            contacto_email=self.contacto_email,
        )


@dataclasses.dataclass(frozen=True)
class AecXmlCesionData:

    """
    Data in XML element ``sii-dte:Cesion`` in an AEC XML doc.

    ..seealso::
        XML schema of ``{http://www.sii.cl/SiiDte}/Cesion`` in
        'data/ref/factura_electronica/schemas-xml/Cesion_v10.xsd' (c7adc5a2)

    ..note:: An AEC XML doc includes one or more ``Cesion`` XML elements.

    Excluded XML elements:

    * ``sii-dte:DocumentoCesion/sii-dte:OtrasCondiciones`` (0..1 occurrences)
    * ``sii-dte:DocumentoCesion/sii-dte:Cedente/sii-dte:RUTAutorizado`` (1..3 occurrences)
    * ``ds:Signature`` (1..3 occurrences)

    """

    dte: dte_data_models.DteDataL1 = dc_field()
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

    seq: int = dc_field()
    """
    Sequence number of the "cesión". Must be >= 1.

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//SeqCesion'

    RPETC email: attachment / 'Cesion' / 'Seq'
    """

    cedente_rut: Rut = dc_field()
    """
    RUT of the "cedente".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cedente//RUT'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cesionario_rut: Rut = dc_field()
    """
    RUT of the "cesionario".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cesionario//RUT'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    monto: int = dc_field()
    """
    Amount of the "cesión".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//MontoCesion'

    RPETC email: attachment / 'Cesion' / 'Monto Cedido'
    """

    fecha_cesion_dt_naive: datetime = dc_field()
    """
    Datetime of "cesión".

    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    > TimeStamp de la Cesion del DTE.

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//TmstCesion'

    RPETC email: attachment / 'Cesion' / 'Fecha de la Cesion'
    """

    ultimo_vencimiento_date: date = dc_field()
    """
    Date of "Ultimo Vencimiento".

    e.g. `2019-04-28` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//UltimoVencimiento'

    RPETC email: attachment / 'Cesion' / 'Ultimo Vencimiento'
    """

    cedente_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "cedente".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cedente//RazonSocial'

    RPETC email: attachment / 'Cedente' / 'Cedido por' (fraction)
    """

    cedente_direccion: str = dc_field()
    """
    Address ("Dirección") of the "cedente".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cedente//Direccion'

    RPETC email: attachment / 'Cedente' / 'Direccion'
    """

    cedente_email: str = dc_field()
    """
    Email address of the "cedente".

    .. warning:: Value may be an invalid email address.

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cedente//eMail'

    RPETC email: attachment / 'Cedente' / 'eMail'
    """

    # There 1 to 3 XML elements '..//Cesion//DocumentoCesion//Cedente//RUTAutorizado'.
    #
    # cedente_persona_autorizada_rut: Rut = dc_field()
    # """
    # "Persona Autorizada" by the "cedente" to "Firmar la Transferencia" (RUT).
    #
    # .. note:: It might be the "cedente" itself, a "persona natural", etc.
    #
    # One of the
    # > Lista de Personas Autorizadas por el Cedente a Firmar la Transferencia
    #
    # AEC doc XML element (1..3 occurrences of 'RUTAutorizado'):
    #     '..//Cesion//DocumentoCesion//Cedente//RUTAutorizado//RUT'
    # """
    #
    # cedente_persona_autorizada_nombre: str = dc_field()
    # """
    # "Persona Autorizada" by the "cedente" to "Firmar la Transferencia" (name).
    #
    # .. note:: It might be the "cedente" itself, a "persona natural", etc.
    #
    # One of the
    # > Lista de Personas Autorizadas por el Cedente a Firmar la Transferencia
    #
    # AEC doc XML element (1..3 occurrences of 'RUTAutorizado'):
    #     '..//Cesion//DocumentoCesion//Cedente//RUTAutorizado//Nombre'
    # """

    cesionario_razon_social: str = dc_field()
    """
    "Razón social" (legal name) of the "cesionario".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cesionario//RazonSocial'

    RPETC email: attachment / 'Cesionario' / 'Cedido a' (fraction)
    """

    cesionario_direccion: str = dc_field()
    """
    Address ("Dirección") of the "cesionario".

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cesionario//Direccion'

    RPETC email: attachment / 'Cesionario' / 'Direccion'
    """

    cesionario_email: str = dc_field()
    """
    Email address of the "cesionario".

    .. warning:: Value may be an invalid email address.

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//Cesionario//eMail'

    RPETC email: attachment / 'Cesionario' / 'eMail'
    """

    dte_deudor_email: Optional[str] = dc_field(default=None)
    """
    Email address of the "deudor" of the DTE.

    .. warning:: Value may be an invalid email address.

    AEC doc XML element:
        '..//Cesion//DocumentoCesion//eMailDeudor'

    RPETC email: no.
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

    AEC doc XML element (optional):
        '..//Cesion//DocumentoCesion//Cedente//DeclaracionJurada'

    RPETC email: attachment / 'Cesion' / 'Declaracion Jurada'
    **but only whether "declaración jurada" was included or not**,
    not the "declaración jurada" itself.
    """

    def __post_init__(self) -> None:
        """
        Run validation automatically after setting the fields values.

        :raises TypeError, ValueError:

        """
        # TODO: validate value of 'fecha_cesion_dt_naive', in relation to the DTE data.
        # TODO: validate value of 'ultimo_vencimiento_date', in relation to the DTE data.

        if not isinstance(self.dte, dte_data_models.DteDataL1):
            raise TypeError("Inappropriate type of 'dte'.")
        if not isinstance(self.seq, int):
            raise TypeError("Inappropriate type of 'seq'.")
        if not isinstance(self.cedente_rut, Rut):
            raise TypeError("Inappropriate type of 'cedente_rut'.")
        if not isinstance(self.cesionario_rut, Rut):
            raise TypeError("Inappropriate type of 'cesionario_rut'.")
        if not isinstance(self.monto, int):
            raise TypeError("Inappropriate type of 'monto'.")
        if not isinstance(self.fecha_cesion_dt_naive, datetime):
            raise TypeError("Inappropriate type of 'fecha_cesion_dt_naive'.")
        if not isinstance(self.ultimo_vencimiento_date, date):
            raise TypeError("Inappropriate type of 'ultimo_vencimiento_date'.")

        if not isinstance(self.cedente_razon_social, str):
            raise TypeError("Inappropriate type of 'cedente_razon_social'.")
        validate_clean_str(self.cedente_razon_social)
        validate_non_empty_str(self.cedente_razon_social)

        if not isinstance(self.cedente_direccion, str):
            raise TypeError("Inappropriate type of 'cedente_direccion'.")
        validate_clean_str(self.cedente_direccion)
        validate_non_empty_str(self.cedente_direccion)

        if not isinstance(self.cedente_email, str):
            raise TypeError("Inappropriate type of 'cedente_email'.")
        validate_clean_str(self.cedente_email)
        validate_non_empty_str(self.cedente_email)

        if not isinstance(self.cesionario_razon_social, str):
            raise TypeError("Inappropriate type of 'cesionario_razon_social'.")
        validate_clean_str(self.cesionario_razon_social)
        validate_non_empty_str(self.cesionario_razon_social)

        if not isinstance(self.cesionario_direccion, str):
            raise TypeError("Inappropriate type of 'cesionario_direccion'.")
        validate_clean_str(self.cesionario_direccion)
        validate_non_empty_str(self.cesionario_direccion)

        if not isinstance(self.cesionario_email, str):
            raise TypeError("Inappropriate type of 'cesionario_email'.")
        validate_clean_str(self.cesionario_email)
        validate_non_empty_str(self.cesionario_email)

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

        data_models.validate_cesion_seq(self.seq)
        data_models.validate_cesion_monto(self.monto)
        dte_data_models.validate_contribuyente_razon_social(self.cedente_razon_social)
        dte_data_models.validate_contribuyente_razon_social(self.cesionario_razon_social)

    @property
    def natural_key(self) -> data_models.CesionNaturalKey:
        return data_models.CesionNaturalKey(dte_key=self.dte.natural_key, seq=self.seq)
