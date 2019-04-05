"""
DTE-related constants.

Sources: official XML schemas 'SiiTypes_v10.xsd' and 'DTE_v10.xsd'.
https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/

"""
import enum


###############################################################################
# DTE fields / Folio
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/IdDoc/Folio'
# - description: "Folio del Documento Electronico"
# - XML type: 'FolioType'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/DTE_v10.xsd#L52-L56
# XML type 'FolioType' in official schema 'SiiTypes_v10.xsd'.
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/SiiTypes_v10.xsd#L153-L160

DTE_FOLIO_FIELD_TYPE = int
"""DTE field 'Folio' type."""
DTE_FOLIO_FIELD_MIN_VALUE = 1
"""DTE field 'Folio' min value."""
DTE_FOLIO_FIELD_MAX_VALUE = 10 ** 10
"""DTE field 'Folio' max value."""


###############################################################################
# DTE fields / Monto Total
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/Totales/MntTotal'
# - description: "Monto Total del DTE"
# - XML type: 'MontoType'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/DTE_v10.xsd#L1160-L1164
# XML type 'MontoType' in official schema 'SiiTypes_v10.xsd'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/SiiTypes_v10.xsd#L563-L570

DTE_MONTO_TOTAL_FIELD_TYPE = int
"""DTE field 'Monto Total' type."""
DTE_MONTO_TOTAL_FIELD_MIN_VALUE = 0
"""DTE field 'Monto Total' min value."""
DTE_MONTO_TOTAL_FIELD_MAX_VALUE = 10 ** 18
"""DTE field 'Monto Total' max value."""


###############################################################################
# DTE fields / Tipo de DTE
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/IdDoc/TipoDTE'
# - description: "Tipo de DTE"
# - XML type: 'DTEType'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/DTE_v10.xsd#L47-L51

DTE_TIPO_DTE_FIELD_TYPE = int
"""DTE field 'Tipo de DTE' type."""
DTE_TIPO_DTE_FIELD_MIN_VALUE = 1
"""DTE field 'Tipo de DTE' min value."""
# DTE_TIPO_DTE_FIELD_MAX_VALUE = ?
# """DTE field 'Tipo de DTE' max value."""


@enum.unique
class TipoDteEnum(enum.IntEnum):

    """
    Enum of Tipo de DTE.

    Source: XML type ``DTEType`` (enum) in official schema ``SiiTypes_v10.xsd``.
    https://github.com/fyndata/lib-cl-sii-python/blob/8b51350/cl_sii/data/ref/factura_electronica/schema_dte/SiiTypes_v10.xsd#L63-L99

    """

    FACTURA_ELECTRONICA = 33
    """Factura Electrónica."""

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura no Afecta o Exenta Electrónica."""
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

    FACTURA_COMPRA_ELECTRONICA = 46
    """Factura de Compra Electrónica."""
    # Name should have been 'Factura Electrónica de Compra'.

    GUIA_DESPACHO_ELECTRONICA = 52
    """Guía de Despacho Electrónica."""

    NOTA_DEBITO_ELECTRONICA = 56
    """Nota de Débito Electrónica."""

    NOTA_CREDITO_ELECTRONICA = 61
    """Nota de Crédito Electrónica."""
