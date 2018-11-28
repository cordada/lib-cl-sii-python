# schema_iecv

This directory contains all the files of `schema_iecv.zip`, plus this text file.
All the files have been preserved as they were; schemas are in their original text encoding
(ISO-8859-1) and have not been modified in the slightest way.

The most significant structures are:
- XML element `LceCal`: "Certificado Autorizacion de Libros, generado por el SII".
- XML element `LceCoCertif`: "Comprobante de Certificacion".
- XML element `LibroCompraVenta`: "Informacion Electronica de Libros de Compra y Venta".

Notes:
- IECV means "Información Electrónica de Libros de Compra y Venta".
- LCE means "Libros Contables Electrónicos".


## Source

[schema_iecv.zip](http://www.sii.cl/factura_electronica/schema_iecv.zip) (2018-11-28),
referenced from official webpage
[SII](http://www.sii.cl)
/ [Factura electrónica](http://www.sii.cl/servicios_online/1039-.html)
/ [FORMATO XML DE DOCUMENTOS ELECTRÓNICOS](http://www.sii.cl/factura_electronica/formato_xml.htm)
as
"[Bajar schema XML de Información Electrónica de Compras y Ventas](http://www.sii.cl/factura_electronica/schema_iecv.zip)".


## Contents


### Detail

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

- `xmldsignature_v10.xsd`:
  - XML target namespace: `http://www.w3.org/2000/09/xmldsig#`.
  - XML included/imported schemas: none.
  - XML elements:
    - `Signature`: "Firma Digital sobre Documento".
  - XML data types:
    - `SignatureType`: "Firma Digital con Restricciones".


### Notes

- File `LibroCV_v10.xsd` defines many data types that are already defined in `LceSiiTypes_v10.xsd`.
- The two enums named `DoctoType` (one in `LibroCV_v10.xsd` and the other in `LceSiiTypes_v10.xsd`)
  **have different elements**.
- File `xmldsignature_v10.xsd` is identical to `../schema_dte/xmldsignature_v10.xsd`.
