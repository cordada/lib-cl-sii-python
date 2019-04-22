"""
Helpers for parsing DTE data from representations such as XML documents.


Usage:

>>> from cl_sii.dte import parse
>>> from cl_sii.libs import xml_utils

>>> xml_file_path = '/dir/my_file.xml'
>>> with open(xml_file_path, mode='rb') as f:
...     xml_doc = xml_utils.parse_untrusted_xml(f.read())

>>> parse.clean_dte_xml(xml_doc)
True
>>> parse.validate_dte_xml(xml_doc)
>>> dte_struct = parse.parse_dte_xml(xml_doc)

"""
import io
import logging
import os
from datetime import date
from typing import Tuple

from cl_sii.libs import xml_utils
from cl_sii.libs.xml_utils import XmlElement
from cl_sii.rut import Rut
from . import constants
from . import data_models


logger = logging.getLogger(__name__)


DTE_XMLNS = 'http://www.sii.cl/SiiDte'
"""
XML namespace for DTE element in DTE XML schema.

Ref: target namespace in 'DTE_v10.xsd' and 'EnvioDTE_v10.xsd'.

* cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L19 (f57a326)
* cl_sii/data/ref/factura_electronica/schemas-xml/EnvioDTE_v10.xsd#L14 (f57a326)
"""

DTE_XMLNS_MAP = {
    'sii-dte': DTE_XMLNS,
}
"""
Mapping from XML namespace prefix to full name, for DTE processing.
"""


_DTE_XML_SCHEMA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data/ref/factura_electronica/schemas-xml/EnvioDTE_v10.xsd',
    )
)
DTE_XML_SCHEMA_OBJ = xml_utils.read_xml_schema(_DTE_XML_SCHEMA_PATH)
"""
XML schema obj for DTE XML document validation.

It is read from a file at import time to avoid unnecessary reads afterwards.
"""


###############################################################################
# main functions
###############################################################################

def clean_dte_xml(
    xml_doc: XmlElement,
    set_missing_xmlns: bool = False,
    remove_doc_personalizado: bool = True,
) -> Tuple[XmlElement, bool]:
    """
    Apply changes to ``xml_doc`` towards compliance to DTE XML schema.

    .. seealso:: :data:`DTE_XML_SCHEMA_OBJ`

    There is a kwarg to enable/disable each kind of change.

    .. warning::
        Do not assume the ``xml_doc``object is modified in-place because in
        some cases it will be replaced (i.e. a entirely different object).

    :returns: new ``xml_doc`` and whether it was modified or not

    """
    modified = False

    if set_missing_xmlns:
        xml_doc, _modified = _set_dte_xml_missing_xmlns(xml_doc)
        modified = modified or _modified

    if remove_doc_personalizado:
        xml_doc, _modified = _remove_dte_xml_doc_personalizado(xml_doc)
        modified = modified or _modified

    return xml_doc, modified


def validate_dte_xml(xml_doc: XmlElement) -> None:
    """
    Validate ``xml_doc`` against DTE's XML schema.

    :raises xml_utils.XmlSchemaDocValidationError:

    """
    # TODO: add better and more precise exception handling.
    xml_utils.validate_xml_doc(DTE_XML_SCHEMA_OBJ, xml_doc)


def parse_dte_xml(xml_doc: XmlElement) -> data_models.DteDataL2:
    """
    Parse data from a DTE XML doc.

    .. warning::
        It is assumed that ``xml_doc`` is an
        ``{http://www.sii.cl/SiiDte}/DTE``  XML element.

    """
    # TODO: separate the XML parsing stage from the deserialization stage, which could be
    #   performed by XML-agnostic code (perhaps using Marshmallow or data clacases?).
    #   See :class:`cl_sii.rcv.parse.RcvCsvRowSchema`.

    xml_em = xml_doc

    ###########################################################################
    # XML elements finding
    ###########################################################################

    documento_em = xml_em.find(
        'sii-dte:Documento',  # "Informacion Tributaria del DTE"
        namespaces=DTE_XMLNS_MAP)

    if documento_em is None:
        raise ValueError("Top level XML element 'Document' is required.")

    encabezado_em = documento_em.find(
        'sii-dte:Encabezado',  # "Identificacion y Totales del Documento"
        namespaces=DTE_XMLNS_MAP)

    id_doc_em = encabezado_em.find(
        'sii-dte:IdDoc',  # "Identificacion del DTE"
        namespaces=DTE_XMLNS_MAP)
    emisor_em = encabezado_em.find(
        'sii-dte:Emisor',  # "Datos del Emisor"
        namespaces=DTE_XMLNS_MAP)
    receptor_em = encabezado_em.find(
        'sii-dte:Receptor',  # "Datos del Receptor"
        namespaces=DTE_XMLNS_MAP)
    totales_em = encabezado_em.find(
        'sii-dte:Totales',  # "Montos Totales del DTE"
        namespaces=DTE_XMLNS_MAP)

    # (required):
    tipo_dte_em = id_doc_em.find(
        'sii-dte:TipoDTE',  # "Tipo de DTE"
        namespaces=DTE_XMLNS_MAP)
    folio_em = id_doc_em.find(
        'sii-dte:Folio',  # "Folio del Documento Electronico"
        namespaces=DTE_XMLNS_MAP)
    fecha_emision_em = id_doc_em.find(
        'sii-dte:FchEmis',  # "Fecha Emision Contable del DTE"
        namespaces=DTE_XMLNS_MAP)
    # (optional):
    fecha_vencimiento_em = id_doc_em.find(
        'sii-dte:FchVenc',  # "Fecha de Vencimiento del Pago"
        namespaces=DTE_XMLNS_MAP)

    emisor_rut_em = emisor_em.find(
        'sii-dte:RUTEmisor',  # "RUT del Emisor del DTE"
        namespaces=DTE_XMLNS_MAP)
    emisor_razon_social_em = emisor_em.find(
        'sii-dte:RznSoc',  # "Nombre o Razon Social del Emisor"
        namespaces=DTE_XMLNS_MAP)

    receptor_rut_em = receptor_em.find(
        'sii-dte:RUTRecep',  # "RUT del Receptor del DTE"
        namespaces=DTE_XMLNS_MAP)
    receptor_razon_social_em = receptor_em.find(
        'sii-dte:RznSocRecep',  # "Nombre o Razon Social del Receptor"
        namespaces=DTE_XMLNS_MAP)

    monto_total_em = totales_em.find(
        'sii-dte:MntTotal',  # "Monto Total del DTE"
        namespaces=DTE_XMLNS_MAP)

    ###########################################################################
    # values parsing
    ###########################################################################

    tipo_dte_value = constants.TipoDteEnum(int(tipo_dte_em.text.strip()))
    folio_value = int(folio_em.text.strip())
    fecha_emision_value = date.fromisoformat(fecha_emision_em.text.strip())
    fecha_vencimiento_value = None
    if fecha_vencimiento_em is not None:
        fecha_vencimiento_value = date.fromisoformat(fecha_vencimiento_em.text.strip())

    emisor_rut_value = Rut(emisor_rut_em.text.strip())
    emisor_razon_social_value = emisor_razon_social_em.text.strip()

    receptor_rut_value = Rut(receptor_rut_em.text.strip())
    receptor_razon_social_value = receptor_razon_social_em.text.strip()

    monto_total_value = int(monto_total_em.text.strip())

    return data_models.DteDataL2(
        emisor_rut=emisor_rut_value,
        tipo_dte=tipo_dte_value,
        folio=folio_value,
        fecha_emision_date=fecha_emision_value,
        receptor_rut=receptor_rut_value,
        monto_total=monto_total_value,
        emisor_razon_social=emisor_razon_social_value,
        receptor_razon_social=receptor_razon_social_value,
        fecha_vencimiento_date=fecha_vencimiento_value,
    )


###############################################################################
# helpers
###############################################################################

def _set_dte_xml_missing_xmlns(xml_doc: XmlElement) -> Tuple[XmlElement, bool]:

    # source: name of the XML element without namespace.
    #   cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L22 (f57a326)
    #   cl_sii/data/ref/factura_electronica/schemas-xml/EnvioDTE_v10.xsd#L92 (f57a326)
    em_tag_simple = 'DTE'

    em_namespace = DTE_XMLNS
    em_tag_namespaced = '{%s}%s' % (em_namespace, em_tag_simple)

    # Tag of 'DTE' should be ...
    assert em_tag_namespaced == '{http://www.sii.cl/SiiDte}DTE'

    modified = False

    root_em = xml_doc.getroottree().getroot()
    root_em_tag = root_em.tag

    if root_em_tag == em_tag_namespaced:
        pass
    elif root_em_tag == em_tag_simple:
        modified = True
        root_em.set('xmlns', em_namespace)
        f = io.BytesIO()
        xml_utils.write_xml_doc(xml_doc, f)
        new_xml_doc_bytes = f.getvalue()
        xml_doc = xml_utils.parse_untrusted_xml(new_xml_doc_bytes)
    else:
        exc_msg = "XML root element tag does not match the expected simple or namespaced name."
        raise Exception(exc_msg, em_tag_simple, em_tag_namespaced, root_em_tag)

    return xml_doc, modified


def _remove_dte_xml_doc_personalizado(xml_doc: XmlElement) -> Tuple[XmlElement, bool]:
    # Remove non-standard but popular element 'DocPersonalizado', it if exists.

    modified = False
    em_path = 'sii-dte:DocPersonalizado'

    xml_em = xml_doc.getroottree().find(em_path, namespaces=DTE_XMLNS_MAP)
    if xml_em is not None:
        modified = True
        xml_doc.remove(xml_em)

    return xml_doc, modified
