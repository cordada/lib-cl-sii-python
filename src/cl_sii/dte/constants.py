"""
DTE-related constants.

Sources: official XML schemas 'SiiTypes_v10.xsd' and 'DTE_v10.xsd'.
https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/

"""

import enum
from datetime import date
from typing import FrozenSet


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


###############################################################################
# DTE Fields / "Referencia" / "Número Secuencial de Línea de Referencia"
###############################################################################

# Sequence number of the "referencia"
#
# > Campo: Número de Línea o Número de Secuencia
# > Descripción: Número de la referencia
# > Tipo: NUM
# > Validación: 1 hasta 40
#
# Note:
#   There is a mismatch in the maximum value allowed for this element between
#   the definition of "Información de Referencia" in the document "FORMATO DOCUMENTOS
#   TRIBUTARIOS ELECTRÓNICOS (pp. 41 - 43)" and the restriction for this
#   element in the XML schema. The first mentions a permitted range of 1 - 40 and the
#   second 1 - 99. Here we will use the definition at "FORMATO DOCUMENTOS TRIBUTARIOS
#   ELECTRÓNICOS (pp. 41 - 43)".
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/NroLinRef'
#     - description: "Numero Secuencial de Linea de Referencia"
#     - XML type: 'xs:positiveInteger'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1763-L1772)
DTE_REFERENCIA_LINE_NUMBER_MIN_VALUE: int = 1
DTE_REFERENCIA_LINE_NUMBER_MAX_VALUE: int = 40


###############################################################################
# DTE Fields / "Referencia" / "Folio de Referencia"
###############################################################################

# The folio of the document referred to.
#
# > Campo: Folio de Referencia
# > Descripción: Identificación del documento de referencia.
# > Tipo: ALFA
# > Validación: Longitud de 1 hasta 18
#
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/FolioRef'
#     - description: "Folio del Documento de Referencia"
#     - XML type: 'SiiDte:FolioRType'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1799-L1803)
DTE_REFERENCIA_FOLIO_MIN_LENGTH: int = 1
DTE_REFERENCIA_FOLIO_MAX_LENGTH: int = 18


###############################################################################
# DTE Fields / "Referencia" / "RUT Otro contribuyente"
###############################################################################

# The RUT of the "emisor" of the document referred to.
#
# > Campo: RUT Otro contribuyente
# > Descripción: Sólo si el documento de referencia es de tipo tributario y
#                fue emitido por otro contribuyente
# > Tipo: ALFA
# > Validación:
#       - Distinto del RUT emisor del DTE
#       - Solo aplica para un subconjunto de los tipos de documentos
#         en `TipoDocumento` [46, 56, 61, 110, 111, 112]
#
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/RUTOtr'
#     - description: "RUT Otro Contribuyente"
#     - XML type: 'SiiDte:RUTType'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1804-L1808)
# TODO: Use `TipoDocumento` after deprecate `TipoDte`
DTE_REFERENCIA_RUTOTR_TIPO_DOC_SET: FrozenSet[TipoDte] = frozenset(
    {
        TipoDte.NOTA_CREDITO_ELECTRONICA,
        TipoDte.NOTA_DEBITO_ELECTRONICA,
        TipoDte.FACTURA_COMPRA_ELECTRONICA,
    }
)


###############################################################################
# DTE Fields / "Referencia" / "Fecha de la Referencia"
###############################################################################

# The 'fecha_emision' of the document referred to.
#
# > Campo: Fecha de la Referencia
# > Descripción: Fecha del documento de referencia.
# > Tipo: ALFA
# > Validación: Desde 2002-08-01 hasta 2050-12-31
#
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/FchRef'
#     - description: "Fecha de la Referencia."
#     - XML type: 'SiiDte:FechaType'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1809-L1813)
DTE_REFERENCIA_FECHA_NOT_BEFORE: date = date(2002, 8, 1)
DTE_REFERENCIA_FECHA_NOT_AFTER: date = date(2050, 12, 31)


###############################################################################
# DTE Fields / "Referencia" / "Código de referencia"
###############################################################################

# The 'fecha_emision' of the document referred to.
#
# > Campo: Código de referencia
# > Descripción: Fecha del documento de referencia.
# > Tipo: NUM
# > Validación: Requerido para 56, 61, 111, 112
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/CodRef'
#     - description: "Tipo de Uso de la Referencia."
#     - XML type: 'xs:positiveInteger'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1814-L1837)
# TODO: Use `TipoDocumento` after deprecate `TipoDte`
DTE_REFERENCIA_CODREF_TIPO_DOC_MANDATORY_SET: FrozenSet[TipoDte] = frozenset(
    {
        TipoDte.NOTA_CREDITO_ELECTRONICA,
        TipoDte.NOTA_DEBITO_ELECTRONICA,
    }
)


@enum.unique
class CodigoReferencia(enum.IntEnum):
    """
    Enum of "Código de referencia".

    Source:
      - from official document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
        (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
      - from official schema ``SiiTypes_v10.xsd``, the XML type (enum) ``CodRef``. (retrieved on 2021-03-25)
        (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/SiiTypes_v10.xsd)

    Notes:
    > Código utilizado para los siguientes casos:
        a) Nota de Crédito que elimina documento de referencia en forma
        completa (Factura de venta, Nota de débito, o Factura de compra
        b) Nota de crédito que corrige un texto del documento de referencia
        (ver campo Corrección Factura)
        c) Nota de Débito que elimina una Nota de Crédito en la referencia
        en forma completa
        d) Notas de crédito o débito que corrigen montos de otro documento

        CASOS a) b) y c) DEBEN TENER UN ÚNICO DOCUMENTO DE REFERENCIA.

    """  # noqa: E501

    ANULA_DOCUMENTO_REFERENCIA = 1
    """Anula Documento de Referencia."""

    CORRIGE_TEXTO_DOCUMENTO_REFERENCIA = 2
    """Corrige Texto del Documento de Referencia."""

    CORRIGE_MONTO_DOCUMENTO_REFERENCIA = 3
    """Corrige Montos"""


###############################################################################
# DTE Fields / "Referencia" / "Razón referencia"
###############################################################################

# The reason the document is being referenced.
#
# > Campo: Razón referencia
# > Descripción: Razón explícita por la que se referencia el Documento.
# > Tipo: ALFA
# > Validación: Longitud de 0 hasta 90
#
#
# Source:
#   - Document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
#   - XML element 'DTEDefType/Documento/Referencia/FolioRef'
#     - description: "Folio del Documento de Referencia"
#     - XML type: 'SiiDte:FolioRType'
#     (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/DTE_v10.xsd#L1838-L1847)
DTE_REFERENCIA_RAZON_MAX_LENGTH: int = 90
