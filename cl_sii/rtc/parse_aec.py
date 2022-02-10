"""
Helpers for parsing data from a "cesión"'s AEC XML doc.


Usage:

>>> from cl_sii.libs import xml_utils

>>> aec_xml_file_path = '/dir/my_aec.xml'
>>> with open(aec_xml_file_path, mode='rb') as f:
...     xml_doc = xml_utils.parse_untrusted_xml(f.read())

>>> validate_aec_xml(xml_doc)
>>> aec_xml = parse_aec_xml(xml_doc)
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Optional, Sequence

import pydantic

import cl_sii.dte.data_models
import cl_sii.dte.parse
from cl_sii.dte.constants import TipoDte
from cl_sii.dte.data_models import DteXmlData
from cl_sii.dte.parse import DTE_XMLNS_MAP
from cl_sii.libs import encoding_utils, tz_utils, xml_utils
from cl_sii.libs.xml_utils import XmlElement
from cl_sii.rut import Rut
from . import data_models_aec


logger = logging.getLogger(__name__)


_AEC_XML_SCHEMA_PATH = Path(
    Path(__file__).parent.parent,
    Path('data/ref/factura_electronica/schemas-xml/AEC_v10.xsd'),
).resolve()

AEC_XML_SCHEMA_OBJ = xml_utils.read_xml_schema(str(_AEC_XML_SCHEMA_PATH))
"""
XML schema obj for AEC XML document validation.

..seealso::
    XML schema of ``{http://www.sii.cl/SiiDte}/AEC`` in
    'data/ref/factura_electronica/schemas-xml/AEC_v10.xsd' (c7adc5a2)

It is read from a file at import time to avoid unnecessary reads afterwards.
"""


###############################################################################
# Main Functions
###############################################################################


def validate_aec_xml(xml_doc: XmlElement) -> None:
    """
    Validate ``xml_doc`` against AEC's XML schema.

    :raises xml_utils.XmlSchemaDocValidationError:
    """
    # TODO: Add better and more precise exception handling.
    xml_utils.validate_xml_doc(AEC_XML_SCHEMA_OBJ, xml_doc)


def parse_aec_xml(xml_doc: XmlElement) -> data_models_aec.AecXml:
    """
    Parse data from a "cesión"'s AEC XML doc.

    .. warning::
        It is assumed that ``xml_doc`` is an ``{http://www.sii.cl/SiiDte}/AEC`` XML element.
    """
    aec_struct = _Aec.parse_xml(xml_doc)
    return aec_struct.as_aec_xml()


###############################################################################
# Parser Functions and Models
###############################################################################


def _empty_str_to_none(v: object) -> object:
    """
    Reusable Pydantic validator that converts empty strings to ``None``.
    """
    if isinstance(v, str):
        if not v.strip():
            v = None
    return v


def _validate_rut(v: object) -> object:
    """
    Reusable Pydantic validator for fields of type :class:`Rut`.
    """
    if isinstance(v, str):
        v = Rut(value=v, validate_dv=False)  # Raises ValueError if invalid.
    return v


class _XmlSignature(pydantic.BaseModel):
    """
    Parser for ``//Signature``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    signature_value: bytes
    key_info_x509_data_x509_cert: bytes

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: //Signature/KeyInfo
        key_info_em = xml_em.find('ds:KeyInfo', namespaces=xml_utils.XML_DSIG_NS_MAP)

        # XPath: //Signature/KeyInfo/X509Data
        key_info_x509_data_em = key_info_em.find(
            'ds:X509Data', namespaces=xml_utils.XML_DSIG_NS_MAP
        )

        # XPath: //Signature
        return dict(
            # XPath: //Signature/SignatureValue
            signature_value=xml_em.findtext(
                'ds:SignatureValue',
                namespaces=xml_utils.XML_DSIG_NS_MAP,
            ),
            #
            # XPath: //Signature/KeyInfo/X509Data/X509Certificate
            key_info_x509_data_x509_cert=key_info_x509_data_em.findtext(
                'ds:X509Certificate',
                namespaces=xml_utils.XML_DSIG_NS_MAP,
            ),
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator(
        'signature_value',
        'key_info_x509_data_x509_cert',
        pre=True,
    )
    def validate_base64(cls, v: object) -> object:
        if isinstance(v, (str, bytes)):
            v = encoding_utils.decode_base64_strict(v)  # Raises ValueError.
        return v

    # Note: Even though this validation seems to make perfect sense, there are some
    # real cases of SII-approved AEC where this is not fulfilled.
    # We will keep this validation in case we need it in the future.
    # @pydantic.validator('key_info_x509_data_x509_cert')
    # def validate_certificate_is_loadable(cls, v: object) -> object:
    #     if isinstance(v, bytes):
    #         _ = crypto_utils.load_der_x509_cert(v)  # Raises ValueError.
    #     return v


class _Cesionario(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cesionario``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    rut: Rut
    razon_social: str
    direccion: str
    email: str

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cesionario
        return dict(
            rut=xml_em.findtext('sii-dte:RUT', namespaces=DTE_XMLNS_MAP),
            razon_social=xml_em.findtext('sii-dte:RazonSocial', namespaces=DTE_XMLNS_MAP),
            direccion=xml_em.findtext('sii-dte:Direccion', namespaces=DTE_XMLNS_MAP),
            email=xml_em.findtext('sii-dte:eMail', namespaces=DTE_XMLNS_MAP),
        )

    ###########################################################################
    # Validators
    ###########################################################################

    _validate_rut = pydantic.validator(  # type: ignore[pydantic-field]
        'rut',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)


class _RutAutorizado(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente/RUTAutorizado``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    rut: Rut
    nombre: Optional[str]

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente/RUTAutorizado
        return dict(
            rut=xml_em.findtext('sii-dte:RUT', namespaces=DTE_XMLNS_MAP),
            nombre=xml_em.findtext('sii-dte:Nombre', namespaces=DTE_XMLNS_MAP),
        )

    ###########################################################################
    # Validators
    ###########################################################################

    _empty_str_to_none = pydantic.validator(  # type: ignore[pydantic-field]
        'nombre',
        pre=True,
        allow_reuse=True,
    )(_empty_str_to_none)

    _validate_rut = pydantic.validator(  # type: ignore[pydantic-field]
        'rut',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)


class _Cedente(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    rut: Rut
    razon_social: str
    direccion: str
    email: str
    ruts_autorizados: Sequence[_RutAutorizado]  # 1..3 occurrences
    declaracion_jurada: Optional[str]

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente/RUTAutorizado
        cedente_personas_autorizadas_em = xml_em.findall(
            'sii-dte:RUTAutorizado',
            namespaces=DTE_XMLNS_MAP,
        )
        cedente_persona_autorizada_dict_list = [
            _RutAutorizado.parse_xml_to_dict(cedente_persona_autorizada)
            for cedente_persona_autorizada in cedente_personas_autorizadas_em
        ]

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente
        return dict(
            rut=xml_em.findtext('sii-dte:RUT', namespaces=DTE_XMLNS_MAP),
            razon_social=xml_em.findtext('sii-dte:RazonSocial', namespaces=DTE_XMLNS_MAP),
            direccion=xml_em.findtext('sii-dte:Direccion', namespaces=DTE_XMLNS_MAP),
            email=xml_em.findtext('sii-dte:eMail', namespaces=DTE_XMLNS_MAP),
            declaracion_jurada=xml_em.findtext(
                'sii-dte:DeclaracionJurada',
                namespaces=DTE_XMLNS_MAP,
            )
            or None,
            ruts_autorizados=cedente_persona_autorizada_dict_list,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('rut', pre=True)
    def validate_rut(cls, v: object) -> object:
        if isinstance(v, str):
            v = Rut(value=v, validate_dv=False)  # Raises ValueError if invalid.
        return v

    @pydantic.validator('ruts_autorizados')
    def validate_ruts_autorizados_item_count(cls, v: object) -> object:
        if isinstance(v, Sequence):
            if len(v) < 1:
                raise ValueError("must contain at least one item")
            if len(v) > 3:
                raise ValueError("must contain at most three items")
        return v


class _IdDte(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/IdDTE``.
    """

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    rut_emisor: Rut
    tipo_dte: TipoDte
    folio: int
    fch_emis: date
    rut_receptor: Rut
    mnt_total: int

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/IdDTE
        return dict(
            rut_emisor=xml_em.findtext('sii-dte:RUTEmisor', namespaces=DTE_XMLNS_MAP),
            tipo_dte=xml_em.findtext('sii-dte:TipoDTE', namespaces=DTE_XMLNS_MAP),
            folio=xml_em.findtext('sii-dte:Folio', namespaces=DTE_XMLNS_MAP),
            fch_emis=xml_em.findtext('sii-dte:FchEmis', namespaces=DTE_XMLNS_MAP),
            rut_receptor=xml_em.findtext('sii-dte:RUTReceptor', namespaces=DTE_XMLNS_MAP),
            mnt_total=xml_em.findtext('sii-dte:MntTotal', namespaces=DTE_XMLNS_MAP),
        )

    def as_dte_data_l1(self) -> cl_sii.dte.data_models.DteDataL1:
        return cl_sii.dte.data_models.DteDataL1(
            emisor_rut=self.rut_emisor,
            tipo_dte=self.tipo_dte,
            folio=self.folio,
            fecha_emision_date=self.fch_emis,
            receptor_rut=self.rut_receptor,
            monto_total=self.mnt_total,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    _validate_rut_emisor = pydantic.validator(  # type: ignore[pydantic-field]
        'rut_emisor',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)

    _validate_rut_receptor = pydantic.validator(  # type: ignore[pydantic-field]
        'rut_receptor',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)

    @pydantic.validator('tipo_dte', pre=True)
    def validate_tipo_dte(cls, v: object) -> object:
        if isinstance(v, int):
            v = TipoDte(v)  # Raises ValueError if invalid.
        return v


class _DocumentoCesion(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    # id: str
    """
    This value seems to be worthless (only useful for internal references in the XML doc).
    e.g. 'CES7393a78afa6c4f709ee9e9e943cb50a3', 'HEF_CESION_T33F170_SEQ2'
    """

    seq_cesion: int
    id_dte: _IdDte
    cedente: _Cedente
    cesionario: _Cesionario
    monto_cesion: int
    ultimo_vencimiento: date
    tmst_cesion: datetime
    email_deudor: Optional[str]

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/IdDTE
        id_dte_em = xml_em.find('sii-dte:IdDTE', namespaces=DTE_XMLNS_MAP)
        id_dte_dict = _IdDte.parse_xml_to_dict(id_dte_em)

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cedente
        cedente_em = xml_em.find('sii-dte:Cedente', namespaces=DTE_XMLNS_MAP)
        cedente_dict = _Cedente.parse_xml_to_dict(cedente_em)

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion/Cesionario
        cesionario_em = xml_em.find('sii-dte:Cesionario', namespaces=DTE_XMLNS_MAP)
        cesionario_dict = _Cesionario.parse_xml_to_dict(cesionario_em)

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion
        return dict(
            # id=xml_em.get('ID'),
            seq_cesion=xml_em.findtext('sii-dte:SeqCesion', namespaces=DTE_XMLNS_MAP),
            id_dte=id_dte_dict,
            cedente=cedente_dict,
            cesionario=cesionario_dict,
            monto_cesion=xml_em.findtext('sii-dte:MontoCesion', namespaces=DTE_XMLNS_MAP),
            ultimo_vencimiento=xml_em.findtext(
                'sii-dte:UltimoVencimiento',
                namespaces=DTE_XMLNS_MAP,
            ),
            tmst_cesion=xml_em.findtext('sii-dte:TmstCesion', namespaces=DTE_XMLNS_MAP),
            email_deudor=xml_em.findtext('sii-dte:eMailDeudor', namespaces=DTE_XMLNS_MAP) or None,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('tmst_cesion')
    def validate_datetime(cls, v: object) -> object:
        if isinstance(v, str):
            v = datetime.fromisoformat(v)

        if isinstance(v, datetime):
            v = tz_utils.convert_naive_dt_to_tz_aware(
                dt=v,
                tz=data_models_aec.CesionAecXml.DATETIME_FIELDS_TZ,
            )
        return v


class _Cesion(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/Cesion``.
    """

    class Config:
        allow_mutation = False
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    documento_cesion: _DocumentoCesion
    # signature: _XmlSignature

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/DocumentoCesion
        doc_cesion_em = xml_em.find('sii-dte:DocumentoCesion', namespaces=DTE_XMLNS_MAP)
        doc_cesion_dict = _DocumentoCesion.parse_xml_to_dict(doc_cesion_em)

        # Signature over 'DocumentoCesion'
        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion/Signature
        # signature_over_doc_cesion_em = xml_em.find(
        #     'ds:Signature',
        #     namespaces=xml_utils.XML_DSIG_NS_MAP,
        # )
        # signature_over_doc_cesion_dict = _XmlSignature.parse_xml_to_dict(
        #     signature_over_doc_cesion_em,
        # )

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion
        return dict(
            documento_cesion=doc_cesion_dict,
            # signature=signature_over_doc_cesion_dict,
        )

    def as_cesion_aec_xml(self) -> data_models_aec.CesionAecXml:
        doc_cesion_struct = self.documento_cesion
        # signature_over_doc_cesion_struct = self.signature  # noqa: F841
        cesion_dte_struct = doc_cesion_struct.id_dte.as_dte_data_l1()
        cedente_persona_autorizada_struct_first = doc_cesion_struct.cedente.ruts_autorizados[0]

        return data_models_aec.CesionAecXml(
            dte=cesion_dte_struct,
            seq=doc_cesion_struct.seq_cesion,
            cedente_rut=doc_cesion_struct.cedente.rut,
            cesionario_rut=doc_cesion_struct.cesionario.rut,
            monto_cesion=doc_cesion_struct.monto_cesion,
            fecha_cesion_dt=doc_cesion_struct.tmst_cesion,
            fecha_ultimo_vencimiento=doc_cesion_struct.ultimo_vencimiento,
            cedente_razon_social=doc_cesion_struct.cedente.razon_social,
            cedente_direccion=doc_cesion_struct.cedente.direccion,
            cedente_email=doc_cesion_struct.cedente.email,
            cedente_persona_autorizada_rut=cedente_persona_autorizada_struct_first.rut,
            cedente_persona_autorizada_nombre=cedente_persona_autorizada_struct_first.nombre,
            cesionario_razon_social=doc_cesion_struct.cesionario.razon_social,
            cesionario_direccion=doc_cesion_struct.cesionario.direccion,
            cesionario_email=doc_cesion_struct.cesionario.email,
            dte_deudor_email=doc_cesion_struct.email_deudor,
            cedente_declaracion_jurada=doc_cesion_struct.cedente.declaracion_jurada,
            # signature_value=signature_over_doc_cesion_struct.signature_value,
            # signature_x509_cert_der=signature_over_doc_cesion_struct.key_info_x509_data_x509_cert,
        )


class _DocumentoDteCedido(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/DTECedido/DocumentoDTECedido``.
    """

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    # id: str
    """
    This value seems to be worthless (only useful for internal references in the XML doc).
      e.g. 'DTE6e0d95997db9489aa4cdd768a45852f6', 'DTE5716484782d745b6822257822a3536d1'
    """

    dte: DteXmlData
    # tmst_firma: datetime

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido/DocumentoDTECedido/DTE
        dte_em = xml_em.find('sii-dte:DTE', namespaces=DTE_XMLNS_MAP)

        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido/DocumentoDTECedido
        return dict(
            # id=xml_em.get('ID'),
            dte=dte_em,
            # tmst_firma=xml_em.findtext('sii-dte:TmstFirma', namespaces=DTE_XMLNS_MAP),
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('dte', pre=True)
    def validate_dte(cls, v: object) -> object:
        if isinstance(v, XmlElement):
            cl_sii.dte.parse.validate_dte_xml(v)
            v = cl_sii.dte.parse.parse_dte_xml(v)
        return v

    # @pydantic.validator('tmst_firma')
    # def validate_datetime(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         v = datetime.fromisoformat(v)
    #
    #     if isinstance(v, datetime):
    #         v = tz_utils.convert_naive_dt_to_tz_aware(
    #             dt=v,
    #             tz=data_models_aec.AecXml.DATETIME_FIELDS_TZ,
    #         )
    #     return v


class _DteCedido(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Cesiones/DTECedido``.
    """

    class Config:
        allow_mutation = False
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    documento_dte_cedido: _DocumentoDteCedido
    # signature: _XmlSignature

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido/DocumentoDTECedido
        doc_dte_cedido_em = xml_em.find(
            'sii-dte:DocumentoDTECedido',
            namespaces=DTE_XMLNS_MAP,
        )

        # Signature over 'DocumentoDTECedido'
        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido/Signature
        # signature_over_doc_dte_cedido_em = xml_em.find(
        #     'ds:Signature',
        #     namespaces=xml_utils.XML_DSIG_NS_MAP,
        # )
        # signature_over_doc_dte_cedido_dict = _XmlSignature.parse_xml_to_dict(
        #     signature_over_doc_dte_cedido_em,
        # )

        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido/DocumentoDTECedido
        doc_dte_cedido_dict = _DocumentoDteCedido.parse_xml_to_dict(doc_dte_cedido_em)

        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido
        return dict(
            documento_dte_cedido=doc_dte_cedido_dict,
            # signature=signature_over_doc_dte_cedido_dict,
        )


class _Caratula(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC/Caratula``.
    """

    class Config:
        allow_mutation = False
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        extra = pydantic.Extra.forbid
        min_anystr_length = 1

    ###########################################################################
    # Fields
    ###########################################################################

    rut_cedente: Rut
    rut_cesionario: Rut
    nmb_contacto: Optional[str]
    fono_contacto: Optional[str]
    mail_contacto: Optional[str]
    tmst_firmaenvio: datetime

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Caratula
        return dict(
            rut_cedente=xml_em.findtext('sii-dte:RutCedente', namespaces=DTE_XMLNS_MAP),
            rut_cesionario=xml_em.findtext('sii-dte:RutCesionario', namespaces=DTE_XMLNS_MAP),
            nmb_contacto=xml_em.findtext('sii-dte:NmbContacto', namespaces=DTE_XMLNS_MAP) or None,
            fono_contacto=xml_em.findtext('sii-dte:FonoContacto', namespaces=DTE_XMLNS_MAP) or None,
            mail_contacto=xml_em.findtext('sii-dte:MailContacto', namespaces=DTE_XMLNS_MAP) or None,
            tmst_firmaenvio=xml_em.findtext('sii-dte:TmstFirmaEnvio', namespaces=DTE_XMLNS_MAP),
        )

    ###########################################################################
    # Validators
    ###########################################################################

    _empty_str_to_none = pydantic.validator(  # type: ignore[pydantic-field]
        'nmb_contacto',
        'fono_contacto',
        'mail_contacto',
        pre=True,
        allow_reuse=True,
    )(_empty_str_to_none)

    _validate_rut_cedente = pydantic.validator(  # type: ignore[pydantic-field]
        'rut_cedente',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)

    _validate_rut_cesionario = pydantic.validator(  # type: ignore[pydantic-field]
        'rut_cesionario',
        pre=True,
        allow_reuse=True,
    )(_validate_rut)

    @pydantic.validator('tmst_firmaenvio')
    def validate_datetime(cls, v: object) -> object:
        if isinstance(v, str):
            v = datetime.fromisoformat(v)

        if isinstance(v, datetime):
            v = tz_utils.convert_naive_dt_to_tz_aware(
                dt=v,
                tz=data_models_aec.AecXml.DATETIME_FIELDS_TZ,
            )
        return v


class _DocumentoAec(pydantic.BaseModel):
    """
    Parser for ``/AEC/DocumentoAEC``.
    """

    class Config:
        allow_mutation = False
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    # id: str
    """
    This value seems to be worthless (only useful for internal references in the XML doc).
      e.g. 'HEF_AEC_T33F170_SEQ2', 'AEC1589423e81824cdcbfd2f0f4496f2dfb'
    """

    caratula: _Caratula
    cesiones_dte_cedido: _DteCedido
    cesiones_cesion: Sequence[_Cesion]

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @staticmethod
    def parse_xml_to_dict(xml_em: XmlElement) -> Mapping[str, object]:
        """
        Parse XML element and return a dictionary.
        """
        # XPath: /AEC/DocumentoAEC/Caratula
        caratula_em = xml_em.find('sii-dte:Caratula', namespaces=DTE_XMLNS_MAP)
        caratula_dict = _Caratula.parse_xml_to_dict(caratula_em)

        # XPath: /AEC/DocumentoAEC/Cesiones
        cesiones_em = xml_em.find('sii-dte:Cesiones', namespaces=DTE_XMLNS_MAP)

        # XPath: /AEC/DocumentoAEC/Cesiones/DTECedido
        dte_cedido_em = cesiones_em.find('sii-dte:DTECedido', namespaces=DTE_XMLNS_MAP)
        dte_cedido_dict = _DteCedido.parse_xml_to_dict(dte_cedido_em)

        # XPath: /AEC/DocumentoAEC/Cesiones/Cesion
        cesion_em_list: Sequence[XmlElement] = cesiones_em.findall(
            'sii-dte:Cesion',
            namespaces=DTE_XMLNS_MAP,
        )
        cesion_dict_list: Sequence[Mapping[str, object]]
        cesion_dict_list = [_Cesion.parse_xml_to_dict(cesion_em) for cesion_em in cesion_em_list]

        # XPath: /AEC/DocumentoAEC
        return dict(
            # id=xml_em.get('ID'),
            caratula=caratula_dict,
            cesiones_dte_cedido=dte_cedido_dict,
            cesiones_cesion=cesion_dict_list,
        )

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.validator('cesiones_cesion')
    def validate_cesiones_cesion_min_items(cls, v: object) -> object:
        if isinstance(v, Sequence):
            if len(v) < 1:
                raise ValueError("must contain at least one item")
        return v


class _Aec(pydantic.BaseModel):
    """
    Parser for ``/AEC``.
    """

    class Config:
        allow_mutation = False
        extra = pydantic.Extra.forbid

    ###########################################################################
    # Fields
    ###########################################################################

    documento_aec: _DocumentoAec
    signature: _XmlSignature

    ###########################################################################
    # Custom Methods
    ###########################################################################

    @classmethod
    def parse_xml(cls, xml_doc: XmlElement) -> _Aec:
        aec_dict = cls.parse_xml_to_dict(xml_doc)
        return cls.parse_obj(aec_dict)

    def as_aec_xml(self) -> data_models_aec.AecXml:
        doc_aec_struct = self.documento_aec
        signature_over_doc_aec_struct = self.signature

        caratula_struct = doc_aec_struct.caratula
        dte = doc_aec_struct.cesiones_dte_cedido.documento_dte_cedido.dte
        cesion_struct_list = doc_aec_struct.cesiones_cesion

        aec_xml_cesion_list: Sequence[data_models_aec.CesionAecXml]
        aec_xml_cesion_list = [
            cesion_struct.as_cesion_aec_xml() for cesion_struct in cesion_struct_list
        ]

        return data_models_aec.AecXml(
            dte=dte,
            cedente_rut=caratula_struct.rut_cedente,
            cesionario_rut=caratula_struct.rut_cesionario,
            fecha_firma_dt=caratula_struct.tmst_firmaenvio,
            signature_value=signature_over_doc_aec_struct.signature_value,
            signature_x509_cert_der=signature_over_doc_aec_struct.key_info_x509_data_x509_cert,
            cesiones=aec_xml_cesion_list,
            contacto_nombre=caratula_struct.nmb_contacto,
            contacto_telefono=caratula_struct.fono_contacto,
            contacto_email=caratula_struct.mail_contacto,
        )

    @staticmethod
    def parse_xml_to_dict(xml_doc: XmlElement) -> Mapping[str, object]:
        """
        Parse data from a "cesión"'s AEC XML doc and return a dictionary.
        """
        # XPath: /AEC
        aec_em = xml_doc

        # XPath: /AEC/DocumentoAEC
        doc_aec_em = aec_em.find('sii-dte:DocumentoAEC', namespaces=DTE_XMLNS_MAP)
        doc_aec_dict = _DocumentoAec.parse_xml_to_dict(doc_aec_em)

        # Signature over 'DocumentoAEC'
        # XPath: /AEC/Signature
        signature_over_doc_aec_em = aec_em.find(
            'ds:Signature',
            namespaces=xml_utils.XML_DSIG_NS_MAP,
        )
        signature_over_doc_aec_dict = _XmlSignature.parse_xml_to_dict(signature_over_doc_aec_em)

        # XPath: /AEC
        return dict(
            documento_aec=doc_aec_dict,
            signature=signature_over_doc_aec_dict,
        )
