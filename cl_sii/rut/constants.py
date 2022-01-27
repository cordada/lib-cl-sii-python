"""
RUT-related constants.

Source: XML type 'RUTType' in official schema 'SiiTypes_v10.xsd'.
https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L127-L136

"""
import re

import cryptography.x509


RUT_CANONICAL_STRICT_REGEX = re.compile(r'^(?P<digits>\d{1,8})-(?P<dv>[\dK])$')
"""RUT (strict) regex for canonical format."""
RUT_CANONICAL_MAX_LENGTH = 10
"""RUT max length for canonical format."""
RUT_CANONICAL_MIN_LENGTH = 3
"""RUT min length for canonical format."""
RUT_DIGITS_MAX_VALUE = 99999999
"""RUT digits max value."""
RUT_DIGITS_MIN_VALUE = 50000000
"""RUT digits min value."""

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
