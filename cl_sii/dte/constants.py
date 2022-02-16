"""
DTE-related constants.

Sources: official XML schemas 'SiiTypes_v10.xsd' and 'DTE_v10.xsd'.
https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/

"""
import enum


###############################################################################
# DTE fields / Folio
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/IdDoc/Folio'
# - description: "Folio del Documento Electronico"
# - XML type: 'FolioType'
# - source:
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L52-L56
# XML type 'FolioType' in official schema 'SiiTypes_v10.xsd'.
# - source:
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L153-L160

DTE_FOLIO_FIELD_TYPE = int
"""DTE field 'Folio' type."""
DTE_FOLIO_FIELD_MIN_VALUE = 1
"""DTE field 'Folio' min value."""
DTE_FOLIO_FIELD_MAX_VALUE = 10**10
"""DTE field 'Folio' max value."""


###############################################################################
# DTE fields / Monto Total
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/Totales/MntTotal'
# - description: "Monto Total del DTE"
# - XML type: 'MontoType'
# - source:
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L1160-L1164
# XML type 'MontoType' in official schema 'SiiTypes_v10.xsd'
# - source:
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L563-L570
# Specification for field 'Monto Total'
# - warning: In certain cases, such as whether negative values are allowed, the SII's specification
#   document may contradict the XML schema.
# - content:
#   > Campo: Monto Total <MntTotal>
#   > Descripción: [...]
#   > Largo máximo: 18
#   > Validación:
#   >   Valor Numérico de acuerdo a descripción.
#   >   En Liquidaciones-Factura, puede tomar valor negativo.
#   >   En Documentos de exportación es “0” (cero) si forma de pago es = 21 (sin pago).
#   > [...]
# - source: SII Chile. 2019-07-10. Formato Documentos Tributarios Electrónicos v2.2.
#   Contenido de Facturas y Documentos Asociados, Detalle por Zona, Encabezado, item nº 124.
#   http://www.sii.cl/factura_electronica/factura_mercado/formato_dte.pdf

DTE_MONTO_TOTAL_FIELD_TYPE = int
"""DTE field 'Monto Total' type."""
DTE_MONTO_TOTAL_FIELD_MIN_VALUE = -(10**18)
"""DTE field 'Monto Total' min value."""
DTE_MONTO_TOTAL_FIELD_MAX_VALUE = 10**18
"""DTE field 'Monto Total' max value."""


###############################################################################
# DTE fields / Tipo de DTE
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/IdDoc/TipoDTE'
# - description: "Tipo de DTE"
# - XML type: 'DTEType'
# - source:
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L47-L51

DTE_TIPO_DTE_FIELD_TYPE = int
"""DTE field 'Tipo de DTE' type."""
DTE_TIPO_DTE_FIELD_MIN_VALUE = 1
"""DTE field 'Tipo de DTE' min value."""
# DTE_TIPO_DTE_FIELD_MAX_VALUE = ?
# """DTE field 'Tipo de DTE' max value."""


@enum.unique
class TipoDte(enum.IntEnum):

    """
    Enum of "Tipo de DTE".

    Source: from official schema ``SiiTypes_v10.xsd``, the XML types (enums)
    ``DOCType``, ``DocType``, ``DTEType`` and ``DTEFacturasType`` which are
    VERY similar.
    https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd

    Notes:
    * Enums ``DocType`` and ``DTEType`` have exactly the same elements
      (although descriptions differ).
    * The elements of the following enums are strictly subgroups of enum ``DOCType``:
      * ``DocType`` and ``DTEType``: same elements.
      * ``DTEFacturasType``
      * ``LIQType``: "Tipos de Liquidaciones".
      * ``EXPType``: "Tipos de Facturas de Exportacion".

    """

    FACTURA_ELECTRONICA = 33
    """Factura electrónica de venta."""

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura electrónica de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta Electrónica'
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

    LIQUIDACION_FACTURA_ELECTRONICA = 43
    """Liquidación-Factura Electrónica."""
    # For more info about a "liquidación-factura [electrónica]" see:
    #   - SII / FAQ / "¿Qué son las Liquidaciones-Factura?"
    #     http://www.sii.cl/preguntas_frecuentes/catastro/001_012_0247.htm
    #   - SII / FAQ / "¿Para qué se utiliza la Liquidación Factura Electrónica?"
    #     http://www.sii.cl/preguntas_frecuentes/catastro/001_012_3689.htm
    #   - SII / FAQ / "¿Qué documentos tributarios deben emitir las partes involucradas en un
    #     contrato de consignación?"
    #     http://www.sii.cl/preguntas_frecuentes/catastro/001_012_2619.htm
    #   - SII / resoluciones / "Resolución Exenta SII N°108 del 24 de Octubre del 2005.
    #     Establece normas y procedimientos de operación referente a la emisión de
    #     liquidaciones-facturas electrónicas"
    #     http://www.sii.cl/documentos/resoluciones/2005/reso108.htm

    FACTURA_COMPRA_ELECTRONICA = 46
    """Factura electrónica de compra."""
    # aka 'Factura de Compra Electrónica'
    # Name should have been 'Factura Electrónica de Compra'.

    GUIA_DESPACHO_ELECTRONICA = 52
    """Guía electrónica de despacho."""
    # aka 'Guía de Despacho Electrónica'

    NOTA_DEBITO_ELECTRONICA = 56
    """Nota electrónica de débito."""
    # aka 'Nota de Débito Electrónica'

    NOTA_CREDITO_ELECTRONICA = 61
    """Nota electrónica de crédito."""
    # aka 'Nota de Crédito Electrónica'

    # TODO: add
    #   110 Factura de exportación electrónica
    #   111 Nota de débito de exportación electrónica
    #   112 Nota de crédito de exportación electrónica
    # https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L58-L60
    # https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L708-L717
    #   See 'cl_sii.rcv.constants.RcvTipoDocto'
    #   Should 'is_factura' be true for a "Factura de exportación electrónica" (110) ?

    @property
    def is_factura(self) -> bool:
        if self is TipoDte.FACTURA_ELECTRONICA:
            result = True
        elif self is TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA:
            result = True
        elif self is TipoDte.FACTURA_COMPRA_ELECTRONICA:
            result = True
        elif self is TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_factura_venta(self) -> bool:
        if self is TipoDte.FACTURA_ELECTRONICA:
            result = True
        elif self is TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA:
            result = True
        elif self is TipoDte.LIQUIDACION_FACTURA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_factura_compra(self) -> bool:
        if self is TipoDte.FACTURA_COMPRA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_nota(self) -> bool:
        if self is TipoDte.NOTA_DEBITO_ELECTRONICA:
            result = True
        elif self is TipoDte.NOTA_CREDITO_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def emisor_is_vendedor(self) -> bool:
        return self.is_factura_venta

    @property
    def receptor_is_vendedor(self) -> bool:
        return self.is_factura_compra
