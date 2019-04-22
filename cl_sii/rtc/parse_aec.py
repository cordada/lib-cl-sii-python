"""
Helpers for parsing data from a "cesión"'s AEC XML doc.


Usage:

>>> from cl_sii.libs import xml_utils

>>> aec_xml_file_path = '/dir/my_aec.xml'
>>> with open(aec_xml_file_path, mode='rb') as f:
...     xml_doc = xml_utils.parse_untrusted_xml(f.read())

>>> validate_aec_xml(xml_doc)
>>> aec_xml_data = parse_aec_xml_data(xml_doc)

"""
import logging
import os
from datetime import date, datetime
from typing import List, Sequence

import cl_sii.dte.data_models
import cl_sii.dte.parse
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.dte.parse import DTE_XMLNS_MAP
from cl_sii.libs import xml_utils
from cl_sii.libs.xml_utils import XmlElement
from cl_sii.rut import Rut

from . import data_models_aec


logger = logging.getLogger(__name__)


_AEC_XML_SCHEMA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data/ref/factura_electronica/schemas-xml/AEC_v10.xsd',
    )
)
AEC_XML_SCHEMA_OBJ = xml_utils.read_xml_schema(_AEC_XML_SCHEMA_PATH)
"""
XML schema obj for AEC XML document validation.

..seealso::
    XML schema of ``{http://www.sii.cl/SiiDte}/AEC`` in
    'data/ref/factura_electronica/schemas-xml/AEC_v10.xsd' (c7adc5a2)

It is read from a file at import time to avoid unnecessary reads afterwards.
"""


###############################################################################
# main functions
###############################################################################

def validate_aec_xml(xml_doc: XmlElement) -> None:
    """
    Validate ``xml_doc`` against AEC's XML schema.

    :raises xml_utils.XmlSchemaDocValidationError:

    """
    # TODO: add better and more precise exception handling.
    xml_utils.validate_xml_doc(AEC_XML_SCHEMA_OBJ, xml_doc)


def parse_aec_xml_data(xml_doc: XmlElement) -> data_models_aec.AecXmlData:
    """
    Parse data from a "cesión"'s AEC XML doc.

    .. warning::
        It is assumed that ``xml_doc`` is an
        ``{http://www.sii.cl/SiiDte}/AEC``  XML element.

    """
    # TODO: separate the XML parsing stage from the deserialization stage, which could be
    #   performed by XML-agnostic code (perhaps using Marshmallow or dataclasses?).
    #   See :func:`cl_sii.dte.parse.parse_dte_xml`.

    aec_em = xml_doc

    documento_aec_em = aec_em.find('sii-dte:DocumentoAEC', namespaces=DTE_XMLNS_MAP)
    # signature_em = aec_em.find('ds:Signature', namespaces=xml_utils.XML_DSIG_NS_MAP)

    # This value seems to be worthless (only useful for internal references in the XML doc).
    #   e.g. 'HEF_AEC_T33F170_SEQ2', 'AEC1589423e81824cdcbfd2f0f4496f2dfb'
    # documento_aec_em_id = documento_aec_em.attrib['ID']

    caratula_em = documento_aec_em.find('sii-dte:Caratula', namespaces=DTE_XMLNS_MAP)
    cesiones_em = documento_aec_em.find('sii-dte:Cesiones', namespaces=DTE_XMLNS_MAP)

    # Caratula
    rut_cedente_em = caratula_em.find('sii-dte:RutCedente', namespaces=DTE_XMLNS_MAP)
    rut_cesionario_em = caratula_em.find('sii-dte:RutCesionario', namespaces=DTE_XMLNS_MAP)
    nmb_contacto_em = caratula_em.find('sii-dte:NmbContacto', namespaces=DTE_XMLNS_MAP)
    fono_contacto_em = caratula_em.find('sii-dte:FonoContacto', namespaces=DTE_XMLNS_MAP)
    mail_contacto_em = caratula_em.find('sii-dte:MailContacto', namespaces=DTE_XMLNS_MAP)
    tmst_firma_envio_em = caratula_em.find('sii-dte:TmstFirmaEnvio', namespaces=DTE_XMLNS_MAP)

    nmb_contacto_str = nmb_contacto_em.text.strip() if nmb_contacto_em is not None else None
    fono_contacto_str = fono_contacto_em.text.strip() if fono_contacto_em is not None else None
    mail_contacto_str = mail_contacto_em.text.strip() if mail_contacto_em is not None else None
    rut_cedente_value = Rut(rut_cedente_em.text)
    rut_cesionario_value = Rut(rut_cesionario_em.text)
    tmst_firma_envio_value = datetime.fromisoformat(tmst_firma_envio_em.text)

    # Cesiones
    # - 'DTECedido'
    dte_cedido_em = cesiones_em.find(
        'sii-dte:DTECedido', namespaces=DTE_XMLNS_MAP)
    documento_dte_cedido_em = dte_cedido_em.find(
        'sii-dte:DocumentoDTECedido', namespaces=DTE_XMLNS_MAP)
    dte_em = documento_dte_cedido_em.find(
        'sii-dte:DTE', namespaces=DTE_XMLNS_MAP)
    # dte_documento_em = dte_em.find(
    #     'sii-dte:Documento', namespaces=DTE_XMLNS_MAP)

    # This value seems to be worthless (only useful for internal references in the XML doc).
    #   e.g. 'DTE6e0d95997db9489aa4cdd768a45852f6', 'DTE5716484782d745b6822257822a3536d1'
    # documento_dte_cedido_em_id = documento_dte_cedido_em.attrib['ID']
    # This value seems to be worthless (only useful for internal references in the XML doc).
    #   e.g. 'MiPE76354771-13419', 'MiPE76399752-6048'
    # dte_documento_id = dte_documento_em.attrib['ID']

    cl_sii.dte.parse.validate_dte_xml(dte_em)
    # TODO: after we implement a proper DTE XML data model, use that instead.
    dte_data = cl_sii.dte.parse.parse_dte_xml(dte_em)

    # Cesiones
    # - 'Cesion' (1..N occurrences)
    cesion_em_list: Sequence[XmlElement] = cesiones_em.findall(
        'sii-dte:Cesion', namespaces=DTE_XMLNS_MAP)
    assert len(cesion_em_list) >= 1

    aec_xml_cesion_data_list: List[data_models_aec.AecXmlCesionData] = []
    for cesion_em in cesion_em_list:
        aec_xml_cesion_data_list.append(_parse_aec_xml_cesion_data(cesion_em))

    return data_models_aec.AecXmlData(
        # TODO: after we implement a proper DTE XML data model, use that instead.
        dte=dte_data,
        cedente_rut=rut_cedente_value,
        cesionario_rut=rut_cesionario_value,
        fecha_firma_dt_naive=tmst_firma_envio_value,
        cesiones=aec_xml_cesion_data_list,
        contacto_nombre=nmb_contacto_str,
        contacto_telefono=fono_contacto_str,
        contacto_email=mail_contacto_str,
    )


def _parse_aec_xml_cesion_data(xml_em: XmlElement) -> data_models_aec.AecXmlCesionData:
    """
    Parse data from a ``sii-dte:Cesion`` element in an AEC XML file.

    An AEC XML doc includes one or more ``sii-dte:Cesion`` XML elements.

    """
    documento_cesion_em = xml_em.find('sii-dte:DocumentoCesion', namespaces=DTE_XMLNS_MAP)
    # signature_em = xml_em.find('ds:Signature', namespaces=xml_utils.XML_DSIG_NS_MAP)

    # This value seems to be worthless (only useful for internal references in the XML doc).
    #   e.g. 'CES7393a78afa6c4f709ee9e9e943cb50a3', 'HEF_CESION_T33F170_SEQ2'
    # documento_cesion_id = documento_cesion_em.attrib['ID']

    seq_cesion_em = documento_cesion_em.find(
        'sii-dte:SeqCesion', namespaces=DTE_XMLNS_MAP)
    id_dte_em = documento_cesion_em.find(
        'sii-dte:IdDTE', namespaces=DTE_XMLNS_MAP)
    cedente_em = documento_cesion_em.find(
        'sii-dte:Cedente', namespaces=DTE_XMLNS_MAP)
    cesionario_em = documento_cesion_em.find(
        'sii-dte:Cesionario', namespaces=DTE_XMLNS_MAP)
    monto_cesion_em = documento_cesion_em.find(
        'sii-dte:MontoCesion', namespaces=DTE_XMLNS_MAP)
    ultimo_vencimiento_em = documento_cesion_em.find(
        'sii-dte:UltimoVencimiento', namespaces=DTE_XMLNS_MAP)
    tmst_cesion_em = documento_cesion_em.find(
        'sii-dte:TmstCesion', namespaces=DTE_XMLNS_MAP)
    deudor_email_em = documento_cesion_em.find(
        'sii-dte:eMailDeudor', namespaces=DTE_XMLNS_MAP)

    # simple types
    seq_cesion_value = int(seq_cesion_em.text)
    monto_cesion_value = int(monto_cesion_em.text)
    ultimo_vencimiento_value = date.fromisoformat(ultimo_vencimiento_em.text)
    tmst_cesion_value = datetime.fromisoformat(tmst_cesion_em.text)
    deudor_email = deudor_email_em.text.strip() if deudor_email_em is not None else None

    # 'id_dte_em' -> 'DteDataL1'
    cesion_dte_struct = cl_sii.dte.data_models.DteDataL1(
        emisor_rut=Rut(
            id_dte_em.find('sii-dte:RUTEmisor', namespaces=DTE_XMLNS_MAP).text),
        tipo_dte=TipoDteEnum(int(
            id_dte_em.find('sii-dte:TipoDTE', namespaces=DTE_XMLNS_MAP).text)),
        folio=int(
            id_dte_em.find('sii-dte:Folio', namespaces=DTE_XMLNS_MAP).text),
        fecha_emision_date=date.fromisoformat(
            id_dte_em.find('sii-dte:FchEmis', namespaces=DTE_XMLNS_MAP).text),
        receptor_rut=Rut(
            id_dte_em.find('sii-dte:RUTReceptor', namespaces=DTE_XMLNS_MAP).text),
        monto_total=int(
            id_dte_em.find('sii-dte:MntTotal', namespaces=DTE_XMLNS_MAP).text),
    )

    # 'cedente_em'
    cedente_rut = Rut(cedente_em.find(
        'sii-dte:RUT', namespaces=DTE_XMLNS_MAP).text)
    cedente_razon_social = cedente_em.find(
        'sii-dte:RazonSocial', namespaces=DTE_XMLNS_MAP).text.strip()
    cedente_direccion = cedente_em.find(
        'sii-dte:Direccion', namespaces=DTE_XMLNS_MAP).text.strip()
    cedente_email = cedente_em.find(
        'sii-dte:eMail', namespaces=DTE_XMLNS_MAP).text.strip()
    # 1..3 occurrences
    # cedente_persona_autorizada_em = cedente_em.find(
    #    'sii-dte:RUTAutorizado', namespaces=DTE_XMLNS_MAP)
    # cedente_persona_autorizada_rut = Rut(cedente_persona_autorizada_em.find(
    #    'sii-dte:RUT', namespaces=DTE_XMLNS_MAP).text)
    # cedente_persona_autorizada_nombre = cedente_persona_autorizada_em.find(
    #    'sii-dte:Nombre', namespaces=DTE_XMLNS_MAP).text
    # 0..1 occurrences
    cedente_declaracion_jurada_em = cedente_em.find(
        'sii-dte:DeclaracionJurada', namespaces=DTE_XMLNS_MAP)
    cedente_declaracion_jurada = cedente_declaracion_jurada_em.text \
        if cedente_declaracion_jurada_em.text is not None else None

    # 'cesionario_em'
    cesionario_rut = Rut(cesionario_em.find('sii-dte:RUT', namespaces=DTE_XMLNS_MAP).text)
    cesionario_razon_social = cesionario_em.find(
        'sii-dte:RazonSocial', namespaces=DTE_XMLNS_MAP).text.strip()
    cesionario_direccion = cesionario_em.find(
        'sii-dte:Direccion', namespaces=DTE_XMLNS_MAP).text.strip()
    cesionario_email = cesionario_em.find(
        'sii-dte:eMail', namespaces=DTE_XMLNS_MAP).text.strip()

    aec_cesiones_cesion_struct = data_models_aec.AecXmlCesionData(
        dte=cesion_dte_struct,
        seq=seq_cesion_value,
        cedente_rut=cedente_rut,
        cesionario_rut=cesionario_rut,
        monto=monto_cesion_value,
        fecha_cesion_dt_naive=tmst_cesion_value,
        ultimo_vencimiento_date=ultimo_vencimiento_value,
        cedente_razon_social=cedente_razon_social,
        cedente_direccion=cedente_direccion,
        cedente_email=cedente_email,
        # cedente_persona_autorizada_rut=cedente_persona_autorizada_rut,
        # cedente_persona_autorizada_nombre=cedente_persona_autorizada_nombre,
        cesionario_razon_social=cesionario_razon_social,
        cesionario_direccion=cesionario_direccion,
        cesionario_email=cesionario_email,
        dte_deudor_email=deudor_email,
        cedente_declaracion_jurada=cedente_declaracion_jurada,
    )

    return aec_cesiones_cesion_struct
