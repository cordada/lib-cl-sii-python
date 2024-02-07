"""
Base / constants
================

"""

import enum

import pytz

from cl_sii.libs.tz_utils import PytzTimezone


TZ_CL_SANTIAGO: PytzTimezone = pytz.timezone('America/Santiago')

SII_OFFICIAL_TZ = TZ_CL_SANTIAGO


@enum.unique
class TipoDocumento(enum.IntEnum):
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

    FACTURA_ELECTRONICA = 33
    """Factura electrónica de venta."""

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura electrónica de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta Electrónica'
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

    BOLETA = 35
    """Boleta."""

    BOLETA_EXENTA = 38
    """Boleta exenta."""

    BOLETA_ELECTRONICA = 39
    """Boleta electrónica."""

    BOLETA_EXENTA_ELECTRONICA = 41
    """Boleta exenta electrónica."""

    FACTURA_COMPRA = 45
    """Factura de compra."""

    FACTURA_COMPRA_ELECTRONICA = 46
    """Factura electrónica de compra."""
    # aka 'Factura de Compra Electrónica'
    # Name should have been 'Factura Electrónica de Compra'.

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

    GUIA_DESPACHO = 50
    """Guía de despacho."""

    GUIA_DESPACHO_ELECTRONICA = 52
    """Guía electrónica de despacho."""
    # aka 'Guía de Despacho Electrónica'

    NOTA_DEBITO = 55
    """Nota de débito."""

    NOTA_DEBITO_ELECTRONICA = 56
    """Nota electrónica de débito."""
    # aka 'Nota de Débito Electrónica'

    NOTA_CREDITO = 60
    """Nota de crédito."""

    NOTA_CREDITO_ELECTRONICA = 61
    """Nota electrónica de crédito."""
    # aka 'Nota de Crédito Electrónica'

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
