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
from dataclasses import MISSING, _MISSING_TYPE
from datetime import date
from typing import Optional, Tuple, Union

import lxml.etree

from cl_sii.libs import xml_utils
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
    xml_doc: lxml.etree.ElementBase,
    set_missing_xmlns: bool = False,
    remove_doc_personalizado: bool = True,
) -> Tuple[lxml.etree.ElementBase, bool]:
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


def validate_dte_xml(xml_doc: lxml.etree.ElementBase) -> None:
    """
    Validate ``xml_doc`` against DTE's XML schema.

    :raises xml_utils.XmlSchemaDocValidationError:

    """
    # TODO: add better and more precise exception handling.
    xml_utils.validate_xml_doc(DTE_XML_SCHEMA_OBJ, xml_doc)


def parse_dte_xml(xml_doc: lxml.etree.ElementBase) -> data_models.DteDataL2:
    """
    Parse and deserialize DTE data from ``xml_doc``.

    """
    # TODO: separate the XML parsing stage from the deserialization stage, which could be
    #   performed by XML-agnostic code (perhaps using Marshmallow or data clacases?).
    #   See :class:`cl_sii.rcv.parse.RcvCsvRowSchema`.

    xml_element_root_tree = xml_doc.getroottree()

    obj_struct = data_models.DteDataL2(
        emisor_rut=_get_emisor_rut(xml_element_root_tree),
        tipo_dte=_get_tipo_dte(xml_element_root_tree),
        folio=_get_folio(xml_element_root_tree),
        fecha_emision_date=_get_fecha_emision(xml_element_root_tree),
        receptor_rut=_get_receptor_rut(xml_element_root_tree),
        monto_total=_get_monto_total(xml_element_root_tree),
        emisor_razon_social=_get_emisor_razon_social(xml_element_root_tree),
        receptor_razon_social=_get_receptor_razon_social(xml_element_root_tree),
        fecha_vencimiento_date=_get_fecha_vencimiento(xml_element_root_tree, default=None),
    )

    return obj_struct


###############################################################################
# helpers
###############################################################################

def _set_dte_xml_missing_xmlns(
    xml_doc: lxml.etree.ElementBase,
) -> Tuple[lxml.etree.ElementBase, bool]:

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


def _remove_dte_xml_doc_personalizado(
    xml_doc: lxml.etree.ElementBase,
) -> Tuple[lxml.etree.ElementBase, bool]:
    # Remove non-standard but popular element 'DocPersonalizado', it if exists.

    modified = False
    em_path = 'sii-dte:DocPersonalizado'

    xml_em = xml_doc.getroottree().find(em_path, namespaces=DTE_XMLNS_MAP)
    if xml_em is not None:
        modified = True
        xml_doc.remove(xml_em)

    return xml_doc, modified


def _get_tipo_dte(xml_etree: lxml.etree.ElementTree) -> constants.TipoDteEnum:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:IdDoc/sii-dte:TipoDTE'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'TipoDTE' was not found in the XML document.")
    return constants.TipoDteEnum(int(value_str))


def _get_folio(xml_etree: lxml.etree.ElementTree) -> int:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:IdDoc/sii-dte:Folio'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'Folio' was not found in the XML document.")
    return int(value_str)


def _get_fecha_emision(xml_etree: lxml.etree.ElementTree) -> date:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:IdDoc/sii-dte:FchEmis'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'FchEmis' was not found in the XML document.")
    return date.fromisoformat(value_str)


def _get_fecha_vencimiento(
    xml_etree: lxml.etree.ElementTree,
    default: Union[date, None, _MISSING_TYPE] = MISSING,
) -> Optional[date]:

    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:IdDoc/sii-dte:FchVenc'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        if default is None or isinstance(default, date):
            value = default
        elif default is MISSING:
            raise Exception("Element 'FchVenc' was not found in the XML document.")
        else:
            raise TypeError("Invalid type of 'default'.")
    else:
        value = date.fromisoformat(value_str)

    return value


def _get_emisor_rut(xml_etree: lxml.etree.ElementTree) -> Rut:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:Emisor/sii-dte:RUTEmisor'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'RUTEmisor' was not found in the XML document.")
    return Rut(value_str)


def _get_emisor_razon_social(xml_etree: lxml.etree.ElementTree) -> str:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:Emisor/sii-dte:RznSoc'

    value_str: str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'RznSoc' was not found in the XML document.")
    return value_str


def _get_receptor_rut(xml_etree: lxml.etree.ElementTree) -> Rut:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:Receptor/sii-dte:RUTRecep'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'RUTRecep' was not found in the XML document.")
    return Rut(value_str)


def _get_receptor_razon_social(xml_etree: lxml.etree.ElementTree) -> str:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:Receptor/sii-dte:RznSocRecep'

    value_str: str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'RznSocRecep' was not found in the XML document.")
    return value_str


def _get_monto_total(xml_etree: lxml.etree.ElementTree) -> int:
    em_path = 'sii-dte:Documento/sii-dte:Encabezado/sii-dte:Totales/sii-dte:MntTotal'

    value_str = xml_etree.findtext(em_path, namespaces=DTE_XMLNS_MAP)
    if value_str is None:
        raise Exception("Element 'MntTotal' was not found in the XML document.")
    return int(value_str)
