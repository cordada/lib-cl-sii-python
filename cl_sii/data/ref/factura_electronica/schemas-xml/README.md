# SII "factura_electronica" / XML schemas

This directory contains all the files of `schema_dte.zip` and `schema_iecv.zip`,
plus this text file.

The most significant structures are:
- common:
  - XML element `Signature`: "Firma Digital sobre Documento".
  - XML data type `SignatureType`: "Firma Digital con Restricciones".
- DTE:
  - XML element `EnvioDTE`: "Envio de Documentos Tributarios Electronicos".
  - XML data type `DTEDefType`: "Documento Tributario Electronico".
- IECV:
  - XML element `LceCal`: "Certificado Autorizacion de Libros, generado por el SII".
  - XML element `LceCoCertif`: "Comprobante de Certificacion".
  - XML element `LibroCompraVenta`: "Informacion Electronica de Libros de Compra y Venta".

Note:
- DTE means "Documento Tributario Electrónico".
- RTC: "Registro Transferencia de Crédito" aka RPETC; "Registro Electrónico de Cesión de Créditos".
- RPETC: "Registro Público Electrónico de Transferencia de Crédito" aka RTC.
- IECV means "Información Electrónica de Libros de Compra y Venta".
- LCE means "Libros Contables Electrónicos".


## Source

All the files were preserved as they were but later on updates were applied (even unofficial ones).
Files are kept in their original text encoding (ISO-8859-1).


### Original & Official


#### DTE

[schema_dte.zip](http://www.sii.cl/factura_electronica/schema_dte.zip) (2018-11-28),
referenced from official webpage
[SII](http://www.sii.cl)
/ [Factura electrónica](http://www.sii.cl/servicios_online/1039-.html)
/ [FORMATO XML DE DOCUMENTOS ELECTRÓNICOS](http://www.sii.cl/factura_electronica/formato_xml.htm)
as
"[Bajar schema XML de Documentos Tributarios Electrónicos](http://www.sii.cl/factura_electronica/schema_dte.zip) (Incluye Documentos de exportación)"


#### Cesion (RTC)

Archive [schema_cesion_201912](https://www.sii.cl/factura_electronica/schema_cesion_201912.zip),
referenced from official webpage
[SII](https://www.sii.cl)
/ [Servicios online](https://www.sii.cl/servicios_online/index.html)
/ [Factura electrónica](https://www.sii.cl/servicios_online/1039-.html)
/ [Sistema de facturación de mercado](https://www.sii.cl/servicios_online/1039-1184.html)
/ [Registro electrónico de cesión de créditos](https://palena.sii.cl/rtc/RTC/RTCMenu.html)
/ [Formatos de archivos electrónicos](https://www.sii.cl/factura_electronica/form_ele.htm)
as
"[Formato XML del Archivo Electrónico de Cesión](https://www.sii.cl/factura_electronica/schema_cesion_201912.zip)"

- Retrieval date: 2021-03-25
- MD5 checksum: `33639f61ef3aa0ec785557b1c8778cea`.
- Source: [cl-sii-extraoficial/archivos-oficiales@c89dec5](https://github.com/cl-sii-extraoficial/archivos-oficiales/tree/c89dec54f664281721dcb77af327c4f6c58ec4ff/src/code/rtc/2019-12-12-schema_cesion)


#### IECV

[schema_iecv.zip](http://www.sii.cl/factura_electronica/schema_iecv.zip) (2018-11-28),
referenced from official webpage
[SII](http://www.sii.cl)
/ [Factura electrónica](http://www.sii.cl/servicios_online/1039-.html)
/ [FORMATO XML DE DOCUMENTOS ELECTRÓNICOS](http://www.sii.cl/factura_electronica/formato_xml.htm)
as
"[Bajar schema XML de Información Electrónica de Compras y Ventas](http://www.sii.cl/factura_electronica/schema_iecv.zip)".


### Updates

Unfortunately the files available on SII's website are outdated with respect to the regulations
(and even with respect to the documentation PDFs published alongside).

Schema files will be updated as necessary, indicating the source in the corresponding commit.


## Contents


### Detail


#### Common

- `xmldsignature_v10.xsd`:
  - XML target namespace: `http://www.w3.org/2000/09/xmldsig#`.
  - XML included/imported schemas: none.
  - XML elements:
    - `Signature`: "Firma Digital sobre Documento".
  - XML data types:
    - `SignatureType`: "Firma Digital con Restricciones".


#### DTE

- `DTE_v10.xsd`: "XSD principal y que incluye a los 3" otros XSD.
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `SiiTypes_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `DTE`: (no description nor annotations)
  - XML data types:
    - `DTEDefType`: "Documento Tributario Electronico".

- `EnvioDTE_v10.xsd`: "descripción de documentos"
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `DTE_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `EnvioDTE`: "Envio de Documentos Tributarios Electronicos".
  - XML data types: none.

- `SiiTypes_v10.xsd`: "descripción de tipos de datos"
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: none.
  - XML elements: none.
  - XML data types:
    - `DOCType`: "Todos los tipos de Documentos Tributarios Electronicos".
    - `DocType`: "Tipos de Documento".
    - `DTEType`: "Tipos de Documentos Tributarios Electronicos".
    - `DTEFacturasType`: "Tipos de Documentos Tributarios Electronicos" (same description as
      `DTEType` but different elements).
    - `LIQType`: "Tipos de Liquidaciones".
    - `EXPType`: "Tipos de Facturas de  Exportacion".
    - `RUTType`: "Rol Unico Tributario (99..99-X)".
    - `MedioPagoType`: "Medios de Pago".
    - `TipMonType`: "Tipos de Moneda de Aduana".
    - `MontoType`: "Monto de 18 digitos".
    - `MntImpType`: "Monto de Impuesto - 18 digitos".
    - `ValorType`: "Monto de 18 digitos - Positivo o Negativo".
    - `FolioType`: "Folio de DTE - 10 digitos".
    - `FolioRType`: "Folio de Referencia - 18 digitos (incluye el cero)".
    - `ImpAdicType`: "Tipo de Impuesto o Retencion Adicional".
    - `ImpAdicDTEType`: "Tipo de Impuesto o Retencion Adicional de los DTE".
    - `MailType`: "Dirección email".
    - `DineroPorcentajeType`: "Unidad en que se expresa el Valor".
    - `NroResolType`: "Número de Resolución".
    - `RznSocLargaType`: "Razón Social (max 100)".
    - `RznSocCortaType`: "Razón Social (max 40)".
    - `DireccSoloDTEType`: "Dirección (maz 60)" (sic).
    - `DireccType`: "Dirección (max 80)".
    - `ComunaType`: "Comuna".
    - `CiudadType`: "Ciudad".
    - `FonoType`: "Fono".
    - `NombreType`: "Nombre".
    - `FechaType`: "Fecha entre 2000-01-01 y 2050-12-31".
    - `TipoTransCOMPRA`: "Tipo de Transacción para el comprador".
    - `TipoTransVENTA`: "Tipo de Transacción para el vendedor".
    - `FechaHoraType`: "FechaType + hora entre 00:00 y 23:59;".
    - `Dec16_2Type`: "Monto con 16 Digitos de Cuerpo y 2 Decimales".
    - `Dec14_4Type`: "Monto con 14 Digitos de Cuerpo y 4 Decimales".
    - `Dec14_4-0Type`: "Monto con 14 Digitos de Cuerpo y 4 Decimales partiendo de cero".
    - `Dec8_4Type`: "Monto con 8 Digitos de Cuerpo y 4 Decimales".
    - `Dec6_4Type`: "Monto con 6 Digitos de Cuerpo y 4 Decimales".
    - `Dec12_6Type`: "Monto con 12 Digitos de Cuerpo y 6 Decimales".
    - `PctType`: "Monto de Porcentaje ( 3 y 2)".


#### Cesion (RTC)

- `AEC_v10.xsd`: main schema; it includes (directly or indirectly) all the others of this section.
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `Cesion_v10.xsd`, `DTECedido_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `AEC`: "Archivo Electronico de Cesion"
      - `DocumentoAEC`: "Documento de AEC"
        - `Caratula`: "Informacion de AEC"
        - `Cesiones`: "Cesiones"
          - ref `DTECedido`: "Representacion XML y Grafica del DTE Cedido"
          - ref `Cesion` (1..N occurrences):
            "Informacion Electronica de Recepcion y Aceptacion del DTE por Parte del Receptor"
  - XML data types: no explicit definitions.

- `Cesion_v10.xsd`: ?
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `SiiTypes_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `Cesion`: "Envio de Informacion de Transferencias  Electronicas".
  - XML data types:
    - `CesionDefType`: "Documento Tributario Electronico" (sic).
      Relevant elements:
      - `DocumentoCesion`: (no description nor annotations)
        - `SeqCesion`: "Secuencia de Cesiones (1, 2, 3, ... )".
        - `IdDTE`: "Identificacion del DTE Cedido".
        - `Cedente`: "Identificacion del Cedente".
        - `Cesionario`: "Identificacion del Cesionario".
        - `MontoCesion`: "Monto del Credito Cedido".
        - `UltimoVencimiento`: "Fecha de Ultimo Vencimiento".
        - `OtrasCondiciones`: "Otras Condiciones de la Cesion".
        - `eMailDeudor`: "Correo Electronico del Deudor del DTE".
        - `TmstCesion`: "TimeStamp de la Cesion del DTE".

- `DTECedido_v10.xsd`: ?
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `DTE_v10.xsd`, `Recibos_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `DTECedido`: "DTE con Imagen y Recibos".
  - XML data types:
    - `DTECedidoDefType`: "Documento Tributario Electronico".
      Relevant elements:
      - `DocumentoDTECedido`: (no description nor annotations)
        - ref `DTE`: "Representacion XML del DTE Cedido".
        - `ImagenDTE` (optional): "Representacion PDF del DTE Cedido" (binary as base64)
        - ref `Recibo` (0..N occurrences):
          "Informacion Electronica de Recepcion y Aceptacion del DTE por Parte del Receptor".
        - `ImagenAR` (optional):
          "Representacion PDF del los Acuse de Recibo" (sic) (binary as base64)
        - `TmstFirma`:
          "Fecha y Hora en que se Firmo Digitalmente el Documento Cedido AAAA-MM-DDTHH:MI:SS".

- `Recibos_v10.xsd`: ?
  - XML target namespace: `http://www.sii.cl/SiiDte`.
  - XML included/imported schemas: `SiiTypes_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `Recibo`:
        doc 1: "Comprobante de Recepcion de Mercaderias o Servicios Prestados".
        doc 2: "Recibos de Recepcion de Mercaderias o Servicios Prestados".
  - XML data types:
    - `ReciboDefType`: "Documento Tributario Electronico" (sic)
      Relevant elements:
      - `DocumentoRecibo`: "Identificacion del Documento Recibido" (sic)
        - `TipoDoc`: "Tipo de Documento".
        - `Folio`: "Folio del Documento".
        - `FchEmis`: "Fecha Emision Contable del Documento (AAAA-MM-DD)".
        - `RUTEmisor`: "RUT Emisor del Documento".
        - `RUTRecep`: "RUT Receptor del Documento".
        - `MntTotal`: "Monto Total del Documento".
        - `Recinto`: "Lugar donde se materializa la recepción conforme".
        - `RutFirma`: "RUT de quien Firma el Recibo".
        - `Declaracion` (fixed string):
          "Texto Ley 19.983, acredita la recepcion mercaderías o servicio.".
        - `TmstFirmaRecibo`: "Fecha y Hora de la Firma del Recibo".


#### IECV

- `LceCal_v10.xsd`
  - XML target namespace: `http://www.sii.cl/SiiLce`.
  - XML included/imported schemas: `LceSiiTypes_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `LceCal`: "Certificado Autorizacion de Libros, generado por el SII".

- `LceCoCertif_v10.xsd`:
  - XML target namespace: `http://www.sii.cl/SiiLce`.
  - XML included/imported schemas: `LceSiiTypes_v10.xsd`, `LceCal_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `LceCoCertif`: "Comprobante de Certificacion".

- `LceSiiTypes_v10.xsd`:
  - XML target namespace: `http://www.sii.cl/SiiLce`.
  - XML included/imported schemas: none.
  - XML elements: none.
  - XML data types:
    - `RUTType`: "Rol Unico Tributario (99..99-X)".
    - `FolioType`: "Folio de DTE - 10 digitos".
    - `MontoType`: "Monto de 18 digitos y 4 decimales".
    - `ImptoType`: "Impuestos Adicionales".
    - `MntImpType`: "Monto 18 digitos (> cero)".
    - `PctType`: "Porcentaje (3 enteros y 2 decimales)".
    - `DoctoType`: "Tipos de Documentos".
    - `ValorType`: "Monto 18 digitos (positivo o negativo)".
    - `Periodo`: "lapso de tiempo. En forma AAAA-MM hasta AAAA-MM".
    - `MontoSinDecType`: "Monto 18 digitos (mayor o igual a cero)".

- `LibroCV_v10.xsd`:
  - XML target namespace: `http://www.sii.cl/SiiDte` (**not** `http://www.sii.cl/SiiLce`).
  - XML included/imported schemas: `LceCoCertif_v10.xsd`, `xmldsignature_v10.xsd`.
  - XML elements:
    - `LibroCompraVenta`: "Informacion Electronica de Libros de Compra y Venta".
  - XML data types:
    - `RUTType`: "RUT 99999999-X".
    - `MontoType`: "Monto 18 digitos (mayor o igual a cero)".
    - `ValorType`: "Monto 18 digitos (positivo o negativo)".
    - `MntImpType`: "Monto 18 digitos (> cero)".
    - `ImptoType`: "Impuestos Adicionales".
    - `DoctoType`: "Tipos de Documentos".
    - `PctType`: "Porcentaje (3 enteros y 2 decimales)".


### Notes

- Enums `DOCType`, `DocType`, `DTEType` and `DTEFacturasType` (all of them in `SiiTypes_v10.xsd`)
  are **very** similar.
- Enums `DocType` and `DTEType` have exactly the same elements (although descriptions differ).
- The elements of the following enums are strictly subgroups of enum `DOCType`:
  - `DocType` and `DTEType`: same elements.
  - `DTEFacturasType`
  - `LIQType`: "Tipos de Liquidaciones".
  - `EXPType`: "Tipos de Facturas de  Exportacion".
- File `LibroCV_v10.xsd` defines many data types that are already defined in `LceSiiTypes_v10.xsd`.
- The two enums named `DoctoType` (one in `LibroCV_v10.xsd` and the other in `LceSiiTypes_v10.xsd`)
  **have different elements**.
