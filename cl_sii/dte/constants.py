"""
DTE-related constants.

Sources: official XML schemas 'SiiTypes_v10.xsd' and 'DTE_v10.xsd'.
https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/

"""
import enum


@enum.unique
class TipoDocumentoEnum(enum.IntEnum):

    """
    Enum of "Tipo de Documento".

    They are defined in a document and also an XML schema.

    Source:
      - from official document "FORMATO DOCUMENTOS TRIBUTARIOS ELECTRÓNICOS (2019-11-15)" (retrieved on 2020-01-30)
        (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/docs/dte/formato-dtes/2019-11-15-formato-dtes-v2.2.y.pdf)
      - from official schema ``SiiTypes_v10.xsd``, the XML type (enum) ``DocType``. (retrieved on 2021-03-25)
        (https://github.com/cl-sii-extraoficial/archivos-oficiales/blob/master/src/code/rtc/2019-12-12-schema_cesion/schema_cesion/SiiTypes_v10.xsd)

    Notes:
    * It is assumed that ``DocType`` it is the main enumerative for "Tipos de Documentos"
      because even though it has the same elements as the enumerative ``DOCType``, in its
      description it does not contain the adjective "Electrónico".
      In any case, the governing definition should be taken as the one contained in the official
      document and not the XML schema.
    * The elements of the following enums are strictly subgroups of enum ``DocType``:
      * ``DOCType``: "Todos los tipos de Documentos Tributarios Electronicos".
                     (The subgroup of ``DocType`` that are considered "Electrónicos")
      * ``DTEType``: "Tipos de Documentos Tributarios Electronicos"
                    (The subgroup of ``DOCType`` for the choice ``DTEDefType/Documento``)
      * ``LIQType``: "Tipos de Liquidaciones".
                     (The subgroup of ``DOCType`` for the choice ``DTEDefType/Liquidacion``)
      * ``EXPType``: "Tipos de Facturas de Exportacion".
                     (The subgroup of ``DOCType`` for the choice ``DTEDefType/Exportaciones``)
      * ``DTEFacturasType``: "Tipos de Documentos Tributarios Electronicos"
                              (The subset of elements in ``DTEType`` and ``LIQType`` that are
                               "cedibles" or in other words can be included in a "cesión")
    """  # noqa: E501

    FACTURA = 30
    """Factura."""

    FACTURA_NO_AFECTA_O_EXENTA = 32
    """Factura de venta bienes y servicios no afectos o exentos de IVA."""

    BOLETA = 35
    """Boleta."""

    BOLETA_EXENTA = 38
    """Boleta exenta."""

    FACTURA_COMPRA = 45
    """Factura de compra."""

    NOTA_DEBITO = 55
    """Nota de débito."""

    NOTA_CREDITO = 60
    """Nota de crédito."""

    LIQUIDACION = 103
    """Liquidación."""

    LIQUIDACION_FACTURA = 40
    """Liquidación factura."""

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

    FACTURA_ELECTRONICA = 33
    """Factura electrónica de venta."""

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura electrónica de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta Electrónica'
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

    BOLETA_ELECTRONICA = 39
    """Boleta electrónica."""

    BOLETA_EXENTA_ELECTRONICA = 41
    """Boleta exenta electrónica."""

    FACTURA_COMPRA_ELECTRONICA = 46
    """Factura electrónica de compra."""
    # aka 'Factura de Compra Electrónica'
    # Name should have been 'Factura Electrónica de Compra'.

    NOTA_DEBITO_ELECTRONICA = 56
    """Nota electrónica de débito."""
    # aka 'Nota de Débito Electrónica'

    NOTA_CREDITO_ELECTRONICA = 61
    """Nota electrónica de crédito."""
    # aka 'Nota de Crédito Electrónica'

    GUIA_DESPACHO = 50
    """Guía de despacho."""

    GUIA_DESPACHO_ELECTRONICA = 52
    """Guía electrónica de despacho."""
    # aka 'Guía de Despacho Electrónica'

    FACTURA_EXPORTACION_ELECTRONICA = 110
    """Factura de exportación electrónica."""

    NOTA_DEBITO_EXPORTACION_ELECTRONICA = 111
    """Nota de débito de exportación electrónica."""

    NOTA_CREDITO_EXPORTACION_ELECTRONICA = 112
    """Nota de crédito de exportación electrónica."""

    ORDEN_COMPRA = 801
    """Orden de compra."""

    NOTA_PEDIDO = 802
    """Nota de pedido."""

    CONTRATO = 803
    """Contrato."""

    RESOLUCION = 804
    """Resolución."""

    PROCESO_CHILE_COMPRA = 805
    """Proceso ChileCompra."""

    FICHA_CHILE_COMPRA = 806
    """Ficha ChileCompra."""

    DOCUMENTO_UNICO_SALIDA = 807
    """Documento Único de Salida (DUS)."""

    GUIA_TRANSPORTE_MARITIMO = 808
    """Guía de transporte marítimo."""
    # aka B/L (Conocimiento de embarque).
    # Source:
    #   - INSTRUCCIONES PARA LLENAR LA DECLARACIÓN JURADA F3602
    #     https://www.sii.cl/pagina/iva/inst_exportaciones_3602.htm

    GUIA_TRANSPORTE_AEREO = 809
    """Guía de transporte aéreo (AWB)."""
    # aka 'Air Will Bill'
    # Source:
    #   - INSTRUCCIONES PARA LLENAR LA DECLARACIÓN JURADA F3602
    #     https://www.sii.cl/pagina/iva/inst_exportaciones_3602.htm

    MANIFIESTO_INTERNACIONAL_CARGA = 810
    """Manifiesto Internacional de Carga (MIC)."""
    # Source:
    #   - INSTRUCCIONES PARA LLENAR LA DECLARACIÓN JURADA F3602
    #     https://www.sii.cl/pagina/iva/inst_exportaciones_3602.htm

    CARTA_PORTE = 811
    """Carta de Porte."""

    RESOLUCION_SNA = 812
    """Resolución del SNA donde califica Servicios de Exportación."""

    PASAPORTE = 813
    """Pasaporte."""

    CERTIFICADO_DEPOSITO_BOLSA_PRODUCTO_CHILE = 814
    """Certificado de Depósito Bolsa Prod. Chile."""

    VALE_PRENDA_BOLSA_PRODUCTO_CHILE = 815
    """Vale de Prenda Bolsa Prod. Chile."""

    CODIGO_INSCRIPCION_REGISTRO_ACUERDOS = 820
    """Código de Inscripción en el Registro de Acuerdos con Plazo de Pago Excepcional."""


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
DTE_FOLIO_FIELD_MAX_VALUE = 10 ** 10
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
DTE_MONTO_TOTAL_FIELD_MIN_VALUE = -10 ** 18
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
#   https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/DTE_v10.xsd#L47-L51

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
        if self is TipoDteEnum.FACTURA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.FACTURA_COMPRA_ELECTRONICA:
            result = True
        elif self is TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
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
        elif self is TipoDteEnum.LIQUIDACION_FACTURA_ELECTRONICA:
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
