import enum


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
