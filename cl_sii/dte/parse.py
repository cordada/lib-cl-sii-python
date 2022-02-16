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
>>> dte_xml_data = parse.parse_dte_xml(xml_doc)

"""
import io
import logging
import os
from datetime import date, datetime
from typing import Optional, Tuple

from cl_sii.libs import encoding_utils, tz_utils, xml_utils
from cl_sii.libs.xml_utils import XmlElement, XmlElementTree
from cl_sii.rut import Rut
from . import constants, data_models


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


def parse_dte_xml(xml_doc: XmlElement) -> data_models.DteXmlData:
    """
    Parse data from a DTE XML doc.

    .. warning::
        It is assumed that ``xml_doc`` is an
        ``{http://www.sii.cl/SiiDte}/DTE``  XML element.

    :raises ValueError:
    :raises TypeError:
    :raises NotImplementedError:

    """
    # TODO: separate the XML parsing stage from the deserialization stage, which could be
    #   performed by XML-agnostic code (perhaps using Marshmallow or data clacases?).
    #   See :class:`cl_sii.rcv.parse_csv.RcvVentaCsvRowSchema`.

    if not isinstance(xml_doc, (XmlElement, XmlElementTree)):
        raise TypeError("'xml_doc' must be an 'XmlElement'.")

    xml_em = xml_doc

    ###########################################################################
    # XML elements finding
    ###########################################################################

    # Schema requires one, and only one, of these:
    # a) 'Documento'
    # b) 'Liquidacion'
    # c) 'Exportaciones'
    documento_em = xml_em.find(
        'sii-dte:Documento',  # "Informacion Tributaria del DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    liquidacion_em = xml_em.find(
        'sii-dte:Liquidacion',  # "Informacion Tributaria de Liquidaciones"
        namespaces=DTE_XMLNS_MAP,
    )
    exportaciones_em = xml_em.find(
        'sii-dte:Exportaciones',  # "Informacion Tributaria de exportaciones"
        namespaces=DTE_XMLNS_MAP,
    )
    signature_em = xml_em.find(
        'ds:Signature',  # "Firma Digital sobre Documento"
        namespaces=xml_utils.XML_DSIG_NS_MAP,
    )

    if liquidacion_em is not None or exportaciones_em is not None:
        raise NotImplementedError("XML element 'Documento' is the only one supported.")

    if documento_em is None:
        raise ValueError("Top level XML element 'Document' is required.")

    # This value seems to be worthless (only useful for internal references in the XML doc).
    #   e.g. 'MiPE76354771-13419', 'MiPE76399752-6048'
    # documento_em_id = documento_em.attrib['ID']

    # 'Documento'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    #   - 'Detalle': (occurrences: 0..60)
    #     "Detalle de Itemes del Documento"
    #   - 'SubTotInfo': (occurrences: 0..20)
    #     "Subtotales Informativos"
    #   - 'DscRcgGlobal': (occurrences: 0..20)
    #     "Descuentos y/o Recargos que afectan al total del Documento"
    #   - 'Referencia': (occurrences: 0..40)
    #     "Identificacion de otros documentos Referenciados por Documento"
    #   - 'Comisiones': (occurrences: 0..20)
    #     "Comisiones y otros cargos es obligatoria para Liquidaciones Factura"
    encabezado_em = documento_em.find(
        'sii-dte:Encabezado',  # "Identificacion y Totales del Documento"
        namespaces=DTE_XMLNS_MAP,
    )
    # note: excluded because currently it is not useful.
    # ted_em = documento_em.find(
    #     'sii-dte:TED',  # "Timbre Electronico de DTE"
    #     namespaces=DTE_XMLNS_MAP)
    tmst_firma_em = documento_em.find(
        'sii-dte:TmstFirma',  # "Fecha y Hora en que se Firmo Digitalmente el Documento"
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Documento.Encabezado'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    #   - 'RUTMandante':
    #     "RUT a Cuenta de Quien se Emite el DTE"
    #   - 'RUTSolicita':
    #     "RUT que solicita el DTE en Venta a Publico"
    #   - 'Transporte':
    #     "Informacion de Transporte de Mercaderias"
    #   - 'OtraMoneda':
    #     "Otra Moneda"
    id_doc_em = encabezado_em.find(
        'sii-dte:IdDoc',  # "Identificacion del DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    emisor_em = encabezado_em.find(
        'sii-dte:Emisor',  # "Datos del Emisor"
        namespaces=DTE_XMLNS_MAP,
    )
    receptor_em = encabezado_em.find(
        'sii-dte:Receptor',  # "Datos del Receptor"
        namespaces=DTE_XMLNS_MAP,
    )
    totales_em = encabezado_em.find(
        'sii-dte:Totales',  # "Montos Totales del DTE"
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Documento.Encabezado.IdDoc'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    #   - 'IndNoRebaja':
    #     "Nota de Credito sin Derecho a Descontar Debito"
    #   - 'TipoDespacho':
    #     "Indica Modo de Despacho de los Bienes que Acompanan al DTE"
    #   - 'IndTraslado':
    #     "Incluido en Guias de Despacho para Especifiicar el Tipo de Traslado de Productos"
    #   - 'TpoImpresion':
    #     "Tipo de impresión N (Normal)  o T (Ticket)"
    #   - 'IndServicio':
    #     "Indica si Transaccion Corresponde a la Prestacion de un Servicio"
    #   - 'MntBruto':
    #     "Indica el Uso de Montos Brutos en Detalle"
    #   - 'TpoTranCompra':
    #     "Tipo de Transacción para el comprador"
    #   - 'TpoTranVenta':
    #     "Tipo de Transacción para el vendedor"
    #   - 'FmaPago':
    #     "Forma de Pago del DTE"
    #   - 'FmaPagExp':
    #     "Forma de Pago Exportación Tabla Formas de Pago de Aduanas"
    #   - 'FchCancel':
    #     "Fecha de Cancelacion del DTE"
    #   - 'MntCancel':
    #     "Monto Cancelado al emitirse el documento"
    #   - 'SaldoInsol':
    #     "Saldo Insoluto al emitirse el documento"
    #   - 'MntPagos': (occurrences: 0..30)
    #     "Tabla de Montos de Pago"
    #   - 'PeriodoDesde':
    #     "Periodo de Facturacion - Desde"
    #   - 'PeriodoHasta':
    #     "Periodo Facturacion - Hasta"
    #   - 'MedioPago':
    #     "Medio de Pago"
    #   - 'TpoCtaPago':
    #     "Tipo Cuenta de Pago"
    #   - 'NumCtaPago':
    #     "Número de la cuenta del pago"
    #   - 'BcoPago':
    #     "Banco donde se realiza el pago"
    #   - 'TermPagoCdg':
    #     "Codigo del Termino de Pago Acordado"
    #   - 'TermPagoGlosa':
    #     "Términos del Pago - glosa"
    #   - 'TermPagoDias':
    #     "Dias de Acuerdo al Codigo de Termino de Pago"
    # (required):
    tipo_dte_em = id_doc_em.find(
        'sii-dte:TipoDTE',  # "Tipo de DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    folio_em = id_doc_em.find(
        'sii-dte:Folio',  # "Folio del Documento Electronico"
        namespaces=DTE_XMLNS_MAP,
    )
    fecha_emision_em = id_doc_em.find(
        'sii-dte:FchEmis',  # "Fecha Emision Contable del DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    # (optional):
    fecha_vencimiento_em = id_doc_em.find(
        'sii-dte:FchVenc',  # "Fecha de Vencimiento del Pago"
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Documento.Encabezado.Emisor'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    #   - 'Telefono': (occurrences: 0..2)
    #     "Telefono Emisor"
    #   - 'Acteco': (occurrences: 0..4)
    #     "Codigo de Actividad Economica del Emisor Relevante para el DTE"
    #   - 'GuiaExport':
    #     "Emisor de una Guía de despacho para Exportación"
    #   - 'Sucursal':
    #     "Sucursal que Emite el DTE"
    #   - 'CdgSIISucur':
    #     "Codigo de Sucursal Entregado por el SII"
    #   - 'DirOrigen':
    #     "Direccion de Origen"
    #   - 'CmnaOrigen':
    #     "Comuna de Origen"
    #   - 'CiudadOrigen':
    #     "Ciudad de Origen"
    #   - 'CdgVendedor':
    #     "Codigo del Vendedor"
    #   - 'IdAdicEmisor':
    #     "Identificador Adicional del Emisor"
    # (required):
    emisor_rut_em = emisor_em.find(
        'sii-dte:RUTEmisor',  # "RUT del Emisor del DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    emisor_razon_social_em = emisor_em.find(
        'sii-dte:RznSoc',  # "Nombre o Razon Social del Emisor"
        namespaces=DTE_XMLNS_MAP,
    )
    emisor_giro_em = emisor_em.find(
        'sii-dte:GiroEmis',  # "Giro Comercial del Emisor Relevante para el DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    # (optional):
    emisor_email_em = emisor_em.find(
        'sii-dte:CorreoEmisor',  # "Correo Elect. de contacto en empresa del receptor" (wrong!)
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Documento.Encabezado.Receptor'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    #   - 'CdgIntRecep':
    #     "Codigo Interno del Receptor"
    #   - 'Extranjero':
    #     "Receptor Extranjero"
    #   - 'GiroRecep':
    #     "Giro Comercial del Receptor"
    #   - 'Contacto':
    #     "Telefono o E-mail de Contacto del Receptor"
    #   - 'CorreoRecep':
    #     "Correo Elect. de contacto en empresa del receptor"
    #   - 'DirRecep':
    #     "Direccion en la Cual se Envian los Productos o se Prestan los Servicios"
    #   - 'CmnaRecep':
    #     "Comuna de Recepcion"
    #   - 'CiudadRecep':
    #     "Ciudad de Recepcion"
    #   - 'DirPostal':
    #     "Direccion Postal"
    #   - 'CmnaPostal':
    #     "Comuna Postal"
    #   - 'CiudadPostal':
    #     "Ciudad Postal"
    # (required):
    receptor_rut_em = receptor_em.find(
        'sii-dte:RUTRecep',  # "RUT del Receptor del DTE"
        namespaces=DTE_XMLNS_MAP,
    )
    receptor_razon_social_em = receptor_em.find(
        'sii-dte:RznSocRecep',  # "Nombre o Razon Social del Receptor"
        namespaces=DTE_XMLNS_MAP,
    )
    # (optional):
    receptor_email_em = emisor_em.find(
        'sii-dte:CorreoRecep',  # "Correo Elect. de contacto en empresa del receptor"
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Documento.Encabezado.Totales'
    # Excluded elements (optional according to the XML schema but the SII may require some of these
    #   depending on 'tipo_dte' and other criteria):
    # - 'MntNeto':
    #   "Monto Neto del DTE"
    # - 'MntExe':
    #   "Monto Exento del DTE"
    # - 'MntBase':
    #   "Monto Base Faenamiento Carne" (???)
    # - 'MntMargenCom':
    #   "Monto Base de Márgenes de Comercialización. Monto informado"
    # - 'TasaIVA':
    #   "Tasa de IVA" (percentage)
    # - 'IVA':
    #   "Monto de IVA del DTE"
    # - 'IVAProp':
    #   "Monto del IVA propio"
    # - 'IVATerc':
    #   "Monto del IVA de Terceros"
    # - 'ImptoReten': (occurrences: 0..20)
    #   "Impuestos y Retenciones Adicionales"
    # - 'IVANoRet':
    #   "IVA No Retenido"
    # - 'CredEC':
    #   "Credito Especial Empresas Constructoras"
    # - 'GrntDep':
    #   "Garantia por Deposito de Envases o Embalajes"
    # - 'Comisiones':
    #   "Comisiones y otros cargos es obligatoria para Liquidaciones Factura"
    # - 'MontoNF':
    #   "Monto No Facturable - Corresponde a Bienes o Servicios Facturados Previamente"
    # - 'MontoPeriodo':
    #   "Total de Ventas o Servicios del Periodo"
    # - 'SaldoAnterior':
    #   "Saldo Anterior - Puede ser Negativo o Positivo"
    # - 'VlrPagar':
    #   "Valor a Pagar Total del documento"
    monto_total_em = totales_em.find(
        'sii-dte:MntTotal',  # "Monto Total del DTE"
        namespaces=DTE_XMLNS_MAP,
    )

    # 'Signature'
    # signature_signed_info_em = signature_em.find(
    #     'ds:SignedInfo',  # "Descripcion de la Informacion Firmada y del Metodo de Firma"
    #     namespaces=xml_utils.XML_DSIG_NS_MAP)
    # signature_signed_info_canonicalization_method_em = signature_signed_info_em.find(
    #     'ds:CanonicalizationMethod',  # "Algoritmo de Canonicalizacion"
    #     namespaces=xml_utils.XML_DSIG_NS_MAP)
    # signature_signed_info_signature_method_em = signature_signed_info_em.find(
    #     'ds:SignatureMethod',  # "Algoritmo de Firma"
    #     namespaces=xml_utils.XML_DSIG_NS_MAP)
    # signature_signed_info_reference_em = signature_signed_info_em.find(
    #     'ds:Reference',  # "Referencia a Elemento Firmado"
    #     namespaces=xml_utils.XML_DSIG_NS_MAP)
    signature_signature_value_em = signature_em.find(
        'ds:SignatureValue',  # "Valor de la Firma Digital"
        namespaces=xml_utils.XML_DSIG_NS_MAP,
    )
    signature_key_info_em = signature_em.find(
        'ds:KeyInfo',  # "Informacion de Claves Publicas y Certificado"
        namespaces=xml_utils.XML_DSIG_NS_MAP,
    )
    # signature_key_info_key_value_em = signature_key_info_em.find(
    #     'ds:KeyValue',
    #     namespaces=xml_utils.XML_DSIG_NS_MAP)
    signature_key_info_x509_data_em = signature_key_info_em.find(
        'ds:X509Data',  # "Informacion del Certificado Publico"
        namespaces=xml_utils.XML_DSIG_NS_MAP,
    )
    signature_key_info_x509_cert_em = signature_key_info_x509_data_em.find(
        'ds:X509Certificate',  # "Certificado Publico"
        namespaces=xml_utils.XML_DSIG_NS_MAP,
    )

    ###########################################################################
    # values parsing
    ###########################################################################

    tipo_dte_value = constants.TipoDte(int(_text_strip_or_raise(tipo_dte_em)))
    folio_value = int(_text_strip_or_raise(folio_em))
    fecha_emision_value = date.fromisoformat(_text_strip_or_raise(fecha_emision_em))
    fecha_vencimiento_value = None
    if fecha_vencimiento_em is not None:
        fecha_vencimiento_value = date.fromisoformat(_text_strip_or_raise(fecha_vencimiento_em))

    emisor_rut_value = Rut(_text_strip_or_raise(emisor_rut_em))
    emisor_razon_social_value = _text_strip_or_raise(emisor_razon_social_em)
    emisor_giro_value = _text_strip_or_raise(emisor_giro_em)
    emisor_email_value = None
    if emisor_email_em is not None:
        emisor_email_value = _text_strip_or_none(emisor_email_em)

    receptor_rut_value = Rut(_text_strip_or_raise(receptor_rut_em))
    receptor_razon_social_value = _text_strip_or_raise(receptor_razon_social_em)
    receptor_email_value = None
    if receptor_email_em is not None:
        receptor_email_value = _text_strip_or_none(receptor_email_em)

    monto_total_value = int(_text_strip_or_raise(monto_total_em))

    tmst_firma_value = tz_utils.convert_naive_dt_to_tz_aware(
        dt=datetime.fromisoformat(_text_strip_or_raise(tmst_firma_em)),
        tz=data_models.DteXmlData.DATETIME_FIELDS_TZ,
    )

    signature_signature_value = encoding_utils.decode_base64_strict(
        _text_strip_or_raise(signature_signature_value_em)
    )
    signature_key_info_x509_cert_der = encoding_utils.decode_base64_strict(
        _text_strip_or_raise(signature_key_info_x509_cert_em)
    )

    return data_models.DteXmlData(
        emisor_rut=emisor_rut_value,
        tipo_dte=tipo_dte_value,
        folio=folio_value,
        fecha_emision_date=fecha_emision_value,
        receptor_rut=receptor_rut_value,
        monto_total=monto_total_value,
        emisor_razon_social=emisor_razon_social_value,
        receptor_razon_social=receptor_razon_social_value,
        fecha_vencimiento_date=fecha_vencimiento_value,
        firma_documento_dt=tmst_firma_value,
        signature_value=signature_signature_value,
        signature_x509_cert_der=signature_key_info_x509_cert_der,
        emisor_giro=emisor_giro_value,
        emisor_email=emisor_email_value,
        receptor_email=receptor_email_value,
    )


def _text_strip_or_none(xml_em: XmlElement) -> Optional[str]:
    # note: we need the pair of functions '_text_strip_or_none' and '_text_strip_or_raise'
    #   because, under certain circumstances, an XML tag:
    #   - with no content -> `xml_em.text` is None instead of ''
    #   - with leading and/or trailing whitespace -> `xml_em.text` may or may not include that

    if xml_em is None:
        raise ValueError("Value must be an XML element, not None.")

    stripped_text: Optional[str] = None
    if xml_em.text is not None:
        stripped_text = xml_em.text.strip()

    return stripped_text


def _text_strip_or_raise(xml_em: XmlElement) -> str:
    # note: we need the pair of functions '_text_strip_or_none' and '_text_strip_or_raise'
    #   because, under certain circumstances, an XML tag:
    #   - with no content -> `xml_em.text` is None instead of ''
    #   - with leading and/or trailing whitespace -> `xml_em.text` may or may not include that

    if xml_em is None:
        raise ValueError("Value must be an XML element, not None.")

    if xml_em.text is None:
        raise ValueError("Text of XML element is None.")
    else:
        stripped_text: str = xml_em.text.strip()

    return stripped_text


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
