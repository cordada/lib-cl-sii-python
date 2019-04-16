"""
Contribuyente-related constants.

Source: XML types 'RznSocLargaType' and 'RznSocCortaType' in official schema
'SiiTypes_v10.xsd'.
https://github.com/fyndata/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L635-L651

"""


# TODO: RAZON_SOCIAL_LONG_REGEX = re.compile(r'^...$')

RAZON_SOCIAL_LONG_MAX_LENGTH = 100
""""Razón Social" max length ("long version")."""

RAZON_SOCIAL_SHORT_MAX_LENGTH = 40
""""Razón Social" max length ("short version")."""
