"""
DTE-related constants.

Sources: official XML schemas 'SiiTypes_v10.xsd' and 'DTE_v10.xsd'.
https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/

"""
import enum


###############################################################################
# DTE fields / Folio
###############################################################################

# XML element 'DTEDefType/Documento/Encabezado/IdDoc/Folio'
# - description: "Folio del Documento Electronico"
# - XML type: 'FolioType'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L52-L56
# XML type 'FolioType' in official schema 'SiiTypes_v10.xsd'.
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L153-L160

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
#   https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L1160-L1164
# XML type 'MontoType' in official schema 'SiiTypes_v10.xsd'
# - source:
#   https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L563-L570

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
#   https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L47-L51

DTE_TIPO_DTE_FIELD_TYPE = int
"""DTE field 'Tipo de DTE' type."""
DTE_TIPO_DTE_FIELD_MIN_VALUE = 1
"""DTE field 'Tipo de DTE' min value."""
# DTE_TIPO_DTE_FIELD_MAX_VALUE = ?
# """DTE field 'Tipo de DTE' max value."""


@enum.unique
class TipoDteEnum(enum.IntEnum):

    """
    Enum of "Tipo de DTE".

    Source: XML type ``DTEType`` (enum) in official schema ``SiiTypes_v10.xsd``.
    https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L63-L99

    """

    FACTURA_ELECTRONICA = 33
    """Factura electrónica de venta."""

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura electrónica de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta Electrónica'
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

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

    @property
    def is_factura(self) -> bool:
        if self is TipoDteEnum.FACTURA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.FACTURA_COMPRA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_factura_venta(self) -> bool:
        if self is TipoDteEnum.FACTURA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_factura_compra(self) -> bool:
        if self is TipoDteEnum.FACTURA_COMPRA_ELECTRONICA:
            result = True
        else:
            result = False

        return result

    @property
    def is_nota(self) -> bool:
        if self is TipoDteEnum.NOTA_DEBITO_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.NOTA_CREDITO_ELECTRONICA:
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
