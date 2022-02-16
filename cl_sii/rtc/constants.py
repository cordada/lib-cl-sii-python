import enum
from typing import FrozenSet

from cl_sii.dte.constants import DTE_MONTO_TOTAL_FIELD_MAX_VALUE, TipoDte


# The collection of "tipo DTE" for which it is possible to "ceder" a "DTE".
#   They are defined in a document and also an XML schema.
#   - Document "Formato Archivo Electrónico de Cesión (AEC)"
#     (http://www.sii.cl/factura_electronica/cesion.pdf) are:
#     > Sólo códigos 33, 34, 46 y 43
#   - XML element 'CesionDefType/DocumentoCesion/IdDTE/TipoDTE'
#     - description: "Tipo de DTE"
#     - XML type: 'SiiDte:DTEFacturasType'
#     - source:
#       https://github.com/fyntex/lib-cl-sii-python/blob/7e1c4b52/cl_sii/data/ref/factura_electronica/schemas-xml/Cesion_v10.xsd#L38-L42
#   - XML type 'SiiDte:DTEFacturasType' in official schema 'SiiTypes_v10.xsd'
#     - source:
#       https://github.com/fyntex/lib-cl-sii-python/blob/7e1c4b52/cl_sii/data/ref/factura_electronica/schemas-xml/SiiTypes_v10.xsd#L100-L126
TIPO_DTE_CEDIBLES: FrozenSet[TipoDte] = frozenset(
    {
        TipoDte.FACTURA_ELECTRONICA,
        TipoDte.FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA,
        TipoDte.FACTURA_COMPRA_ELECTRONICA,
        TipoDte.LIQUIDACION_FACTURA_ELECTRONICA,
    }
)


###############################################################################
# Cesion Fields / "Monto Cedido"
###############################################################################

# Amount of the "cesión".
#
# Ref:
#   - https://github.com/fyntex/lib-cl-sii-api-python/blob/v0.4.4/cl_sii_api/rtc/data_models.py#L231
#   - Document "Formato Archivo Electrónico de Cesión 2013-02-11" (retrieved on 2019-08-12)
#     (https://www.sii.cl/factura_electronica/cesion.pdf)
CESION_MONTO_CEDIDO_FIELD_MIN_VALUE: int = 0
CESION_MONTO_CEDIDO_FIELD_MAX_VALUE: int = DTE_MONTO_TOTAL_FIELD_MAX_VALUE


###############################################################################
# Cesion Fields / "Secuencia"
###############################################################################

# Sequence number of the "cesión"
#
# > Campo: Número de Cesión
# > Descripción: Secuencia de la cesión
# > Tipo: NUM
# > Validación: 1 hasta 40
#
# Source:
#   Document "Formato Archivo Electrónico de Cesión 2013-02-11" (retrieved on 2019-08-12)
#   (https://www.sii.cl/factura_electronica/cesion.pdf)
CESION_SEQUENCE_NUMBER_MIN_VALUE: int = 1
CESION_SEQUENCE_NUMBER_MAX_VALUE: int = 40


###############################################################################
# Other
###############################################################################


@enum.unique
class RolContribuyenteEnCesion(enum.Enum):

    """
    "Rol" of "contribuyente" in a "cesion".
    """

    CEDENTE = 'CEDENTE'
    """Cesiones en las que el contribuyente ha sido cedente i.e. ha cedido"""

    CESIONARIO = 'CESIONARIO'
    """Cesiones en las que el contribuyente ha sido cesionario i.e. le han cedido"""

    DEUDOR = 'DEUDOR'
    """Cesiones de DTEs en que el contribuyente es el deudor."""
