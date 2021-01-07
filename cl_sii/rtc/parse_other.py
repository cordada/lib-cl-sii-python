"""


ConsultaRtcCesionDocumento


"""

from __future__ import annotations

import dataclasses
from dataclasses import field as dc_field
from datetime import date, datetime

# import cl_sii.contribuyente.constants
# import cl_sii.rut.constants
# from cl_sii.dte.constants import TipoDteEnum
from cl_sii.rut import Rut


@dataclasses.dataclass(frozen=True)
class RtcEnvioCesion:

    """
Rut Envio              : 77858280-5
Identificador de Envio : 3609810432
Fecha de Recepcion     : 29/03/2019 10:24:12
    """

    envio_rut: Rut = dc_field()
    """
    RUT of who submitted the "envío cesión".
    """

    envio_id: int = dc_field()
    """
    TODO. Do not confuse with "Identificador de Cesion" (in RPETC email attachment)
    """

    fecha_recepcion_dt: datetime = dc_field()
    """
    TODO.
    """


@dataclasses.dataclass(frozen=True)
class RtcResultadoEnvioCesionEmail:

    """

    """

    envio_cesion: RtcEnvioCesion
    """
    """

    estado_envio: str
    """
    TODO. enum?
    e.g. "EOK - Anotacion de Cesion Aceptada, Envio Aceptado"
    """


@dataclasses.dataclass(frozen=True)
class RpetcEmailCesion:

    """

    Ignored fields in RPETC email attachment:

    * "Otras Condiciones": apparently the value is always "SIN INFORMACION".
      No equivalent field in XML.

Cesion
------
Seq: 1
Fecha de la Cesion: 2019-03-29 10:18:35
Declaracion Jurada: Si
Monto Cedido: $ 49342
Ultimo Vencimiento: 2019-02-11
Otras Condiciones: SIN INFORMACION
Identificador de Cesion: Na0100Bu6489xQ0304hI
    """

    seq: int = dc_field()
    """
    TODO. must be >= 1
    e.g. 1

    AEC doc XML element:
        'AEC//DocumentoAEC//Cesiones//Cesion//DocumentoCesion//SeqCesion'
    RPETC email: attachment / 'Cesion' / 'Seq'
    """

    identificador: int = dc_field()
    """
    TODO. aka "Clave de Acceso"
    e.g. 'Na0100Bu6489xQ0304hI'

    AEC doc XML element: NO
    RPETC email: 'Identificador de Cesion'
    Consulta query: 'Clave de Acceso'
    """

    monto: int = dc_field()
    """
    TODO. must be ?

    AEC doc XML element:
        'AEC//DocumentoAEC//Cesiones//Cesion//DocumentoCesion//MontoCesion'
    RPETC email: attachment / 'Cesion' / 'Monto Cedido'
    """

    fecha_cesion_dt_naive: datetime = dc_field()
    """
    TODO.
    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element:
        'AEC//DocumentoAEC//Cesiones//Cesion//DocumentoCesion//TmstCesion'
    RPETC email: attachment / 'Cesion' / 'Fecha de la Cesion'
    """

    declaracion_jurada_included: bool
    """
    TODO.
    AEC doc XML element: NO
    RPETC email: attachment / 'Cesion' / 'Declaracion Jurada'
    """

    ultimo_vencimiento_date: date = dc_field()
    """
    TODO.
    e.g. `2019-03-29T10:18:35` (XML), 2019-03-29 10:18:35 (txt)

    AEC doc XML element:
        'AEC//DocumentoAEC//Cesiones//Cesion//DocumentoCesion//UltimoVencimiento'
    RPETC email: attachment / 'Cesion' / 'Ultimo Vencimiento'
    """
