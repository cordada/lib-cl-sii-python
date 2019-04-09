"""
RUT-related constants.

Source: XML type 'RUTType' in official schema 'SiiTypes_v10.xsd'.
https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L127-L136

"""
import re


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
