"""
RUT-related constants.

Source: XML type 'RUTType' in official schema 'SiiTypes_v10.xsd'.
https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L127-L136

"""

import re
from typing import Pattern

import cryptography.x509


RUT_CANONICAL_STRICT_REGEX = re.compile(r'^(?P<digits>\d{1,8})-(?P<dv>[\dK])$')
"""RUT (strict) regex for canonical format."""
RUT_CANONICAL_MAX_LENGTH = 10
"""RUT max length for canonical format."""
RUT_CANONICAL_MIN_LENGTH = 3
"""RUT min length for canonical format."""
RUT_DIGITS_MAX_VALUE = 99999999
"""RUT digits max value."""
RUT_DIGITS_MIN_VALUE = 1
"""RUT digits min value."""

RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX: Pattern[str] = re.compile("^(\\d{1,8})-([\\dK])$")
"""
RUT (strict) JSON Schema regex for canonical format.

This regex is compatible with JSON Schema and OpenAPI, which use the regular expression syntax from
JavaScript (ECMA 262), which does not support Python’s named groups.

.. tip:: If you need the regex as a string, for example to use it in a JSON Schema or
    OpenAPI schema, use ``RUT_CANONICAL_STRICT_JSON_SCHEMA_REGEX.pattern``.
"""

SII_CERT_TITULAR_RUT_OID = cryptography.x509.oid.ObjectIdentifier("1.3.6.1.4.1.8321.1")
"""OID of the RUT of the certificate holder"""
# - Organismo: MINISTERIO DE ECONOMÍA / SUBSECRETARIA DE ECONOMIA
# - Decreto 181 (Julio-Agosto 2002)
#   "APRUEBA REGLAMENTO DE LA LEY 19.799 SOBRE DOCUMENTOS ELECTRONICOS, FIRMA ELECTRONICA
#   Y LA CERTIFICACION DE DICHA FIRMA"
# - ref: https://www.leychile.cl/Consulta/m/norma_plana?org=&idNorma=201668
# dice:
# > RUT del titular del certificado : 1.3.6.1.4.1.8321.1
# > RUT de la certificadora emisora : 1.3.6.1.4.1.8321.2
#
# - ref: http://acepta.newtenberg.com/1919/articles-82538_recurso_3.pdf
# dice:
# > OtherName: Para certificados de identidad de individuos, aquí se registra el RUT, en
# > la siguiente estructura:
#   Type-id = 1.3.6.1.4.1.8321.1
#   Value ='xx.xxx.xx-v'
# > El campo Value es un IA5String con el RUT del individuo titular del certificado.

PERSONA_JURIDICA_MIN_RUT_DIGITS: int = 50000000
"""
Lowest RUT digits for “personas jurídicas”.
"""
# Why must “personas jurídicas” have RUT ≥ 50000000-7?
#
# > ¿Qué es una Persona Jurídica?
# >
# > […] persona ficticia, capaz de ejercer derechos y contraer obligaciones civiles, y de ser
# > representada judicial y extrajudicialmente. Además de esto, poseen Rut sobre 50 millones.
#
# Source:
# [BancoEstado Microempresas → Información general sobre personas jurídicas](https://www.bancoestado.cl/content/bancoestado-public/cl/es/home/home-microempresa/servicios/informacion-general-sobre-personas-juridicas---bancoestado-micro.html#/) # noqa: E501
# (retrieved on 2025-01-28)
