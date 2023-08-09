from __future__ import annotations

import enum
from typing import Optional

from ..dte.constants import TipoDte


@enum.unique
class RcvKind(enum.Enum):
    """
    The kind of RCV.

    Definitions:

    * Registro de Compras (RC):
      > [..] todas las operaciones de compras realizadas por un contribuyente
      > de acuerdo a los DTEs recepcionados por el SII, complementado con los
      > documentos tributarios de compras, en soporte distinto al electrónico,
      > en el cual deberá indicarse la naturaleza de las operaciones en
      > cuanto a la procedencia e identificación del crédito fiscal.

    * Registro de Ventas (RV):
      > [..] todas las operaciones de ventas realizadas por un contribuyente
      > de acuerdo a los DTEs recibidos en el SII.

    Definitions source: RCV_FAQ_

    .. _RCV_FAQ: http://www.sii.cl/ayudas/ayudas_por_servicios/rcv_faqs.pdf

    """

    COMPRAS = 'COMPRAS'
    """RCV / compras."""

    VENTAS = 'VENTAS'
    """RCV / ventas."""

    def is_estado_contable_compatible(self, value: Optional[RcEstadoContable]) -> bool:
        if value is not None and not isinstance(value, RcEstadoContable):
            raise TypeError("Value must be None or a 'RcEstadoContable'.")

        if self == RcvKind.COMPRAS and value is not None:
            result = True
        elif self == RcvKind.VENTAS and value is None:
            result = True
        else:
            result = False

        return result


@enum.unique
class RcEstadoContable(enum.Enum):
    """
    The "Estado Contable" of a "Registro de compras" (RC).

    Applies to ``RcvKind.COMPRAS``.

    Definitions:

    * "Registro":
      > [..] los Documentos Tributarios Electrónicos (DTE) y no Electrónicos
      > que conforman la Información de Compras válida, la cual se utiliza para
      > la determinación impositiva y es considerada como el registro oficial
      > del Contribuyente y respaldo de su contabilidad.

    * "No incluir":
      > [..] los Documentos Tributarios Electrónicos (DTE) y no Electrónicos
      > que no deben incluirse en el Registro de Compras, en virtud de
      > corresponder a compras y pagos de servicios que no tienen relación con
      > las actividades económicas del contribuyente y por lo tanto no deben
      > afectar la determinación impositiva.

    * "Reclamado(s)":
      > [..] los Documentos Tributarios Electrónicos (DTE) que han sido
      > reclamados por el mismo receptor en el Registro de Aceptación o Reclamo
      > de un DTE.
      > Por encontrarse en estado "Reclamado", no es posible ingresar estos
      > documentos en el Registro de Compras vigente o considerarse para la
      > determinación impositiva.

    * "Pendiente(s)":
      > [..] los Documentos Tributarios Electrónicos (DTE) que han sido
      > recibidos en el SII, pero que se encuentran pendientes de otorgarse el
      > Acuse de Recibo o entregarse un Reclamo por parte del receptor [..].

    Definitions source: RCV_web_app_

    .. _RCV_web_app: https://www4.sii.cl/consdcvinternetui/#/index

    """

    REGISTRO = 'REGISTRO'
    NO_INCLUIR = 'NO_INCLUIR'
    RECLAMADO = 'RECLAMADO'
    PENDIENTE = 'PENDIENTE'


@enum.unique
class RcvTipoDocto(enum.IntEnum):

    """
    Enum of "Tipo de Documento" for the RCV domain.

    Unlike :class:`cl_sii.dte.constants.TipoDte` this collection is not
    restricted to "documentos electrónicos". However, this is not a superset
    of the latter (e.g. "Guía electrónica de despacho" (52) is in
    ``TipoDte`` but not in ``RcvTipoDocto``).

    Sources:

    * XML type (enum) ``DoctoType`` ("Tipos de Documentos") in
      official schema ``LibroCV_v10.xsd``.
      https://github.com/fyntex/lib-cl-sii-python/blob/f57a326/cl_sii/data/ref/factura_electronica/schemas-xml/LibroCV_v10.xsd#L1563-L1622

    * Values returned by SII endpoint
      https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getDatosInicio

    * Constant ``cl_sii_api.rcv.AVAILABLE_DOCUMENT_TYPES`` in package
      ``cl-sii-api`` v0.2.2.
      https://github.com/fyntex/lib-cl-sii-api-python/blob/81b4a43/cl_sii_api/rcv.py

    """

    ###########################################################################
    # "facturas"
    ###########################################################################

    FACTURA_INICIO = 29
    """Factura de inicio."""

    FACTURA = 30
    """Factura."""

    FACTURA_ELECTRONICA = 33
    """Factura electrónica de venta."""

    FACTURA_NO_AFECTA_O_EXENTA = 32
    """Factura de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta'
    # aka 'Factura de Venta de Bienes y Servicios No afectos o Exento de IVA'

    FACTURA_NO_AFECTA_O_EXENTA_ELECTRONICA = 34
    """Factura electrónica de venta, no afecta o exenta de IVA."""
    # aka 'Factura no Afecta o Exenta Electrónica'
    # aka 'Factura Electrónica de Venta de Bienes y Servicios No afectos o Exento de IVA'

    FACTURA_COMPRA = 45
    """Factura de compra."""

    FACTURA_COMPRA_ELECTRONICA = 46
    """Factura electrónica de compra."""
    # aka 'Factura de Compra Electrónica'
    # Name should have been 'Factura Electrónica de Compra'.

    FACTURA_EXPORTACION = 101
    """Factura de Exportación."""

    FACTURA_EXPORTACION_ELECTRONICA = 110
    """Factura Electrónica de Exportación."""
    # aka 'Factura de Exportación Electrónica'
    # Name should have been 'Factura Electrónica de Exportación'.

    ###########################################################################
    # "notas"
    ###########################################################################

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

    NOTA_DEBITO_EXPORTACION = 104
    """Nota de débito de exportación."""

    NOTA_DEBITO_EXPORTACION_ELECTRONICA = 111
    """Nota electrónica de débito de exportación."""

    NOTA_CREDITO_EXPORTACION = 106
    """Nota de crédito de exportación."""

    NOTA_CREDITO_EXPORTACION_ELECTRONICA = 112
    """Nota electrónica de crédito de exportación."""

    ###########################################################################
    # "liquidación-factura"
    ###########################################################################

    # For more info about a "liquidación-factura" see
    #   'cl_sii.dte.constants.TipoDte'.

    LIQUIDACION_FACTURA = 40
    """Liquidación-Factura."""

    LIQUIDACION_FACTURA_ELECTRONICA = 43
    """Liquidación-Factura Electrónica."""

    ###########################################################################
    # "Total Op. del mes Boleta X"
    ###########################################################################

    TOTAL_OP_DEL_MES_BOLETA_AFECTA = 35
    """Total Oper. del mes Boleta Afecta."""

    TOTAL_OP_DEL_MES_BOLETA_EXENTA = 38
    """Total Oper. del mes Boleta Exenta."""

    TOTAL_OP_DEL_MES_BOLETA_EXENTA_ELECTR = 41
    """Total Op. del mes Boleta Exenta Electr."""

    TOTAL_OP_DEL_MES_BOLETA_ELECTR = 39
    """Total Oper. del mes Boleta Electr."""

    ###########################################################################
    # uncommon
    ###########################################################################

    TIPO_47 = 47
    """Total del mes Vale Electrónico Especial."""

    TIPO_48 = 48
    """Total mes Comprobantes Pago Electrónico."""

    TIPO_102 = 102
    """Factura vta. Exenta a Zona Franca Prim."""

    TIPO_103 = 103
    """Liquidación."""

    TIPO_105 = 105
    """Total Op. mes Boleta Liq. Res. 1423/76."""

    TIPO_108 = 108
    """SRF Solicitud Registro de Factura."""

    TIPO_109 = 109
    """Factura Turista."""

    TIPO_901 = 901
    """Fact. Vta. Emp. Terr. Pref. Res. 1057/85."""

    TIPO_902 = 902
    """Conocimiento Embarque Marítimo o Aéreo."""

    TIPO_903 = 903
    """Documento Único de Salida (DUS)."""

    TIPO_904 = 904
    """Factura de Traspaso."""

    TIPO_905 = 905
    """Factura de Reexpedición."""

    TIPO_906 = 906
    """Total Op. del mes Boleta Vta. Módulo ZF."""

    TIPO_907 = 907
    """Facturas Venta Módulo ZF."""

    TIPO_909 = 909
    """Facturas Venta Módulo ZF."""

    TIPO_910 = 910
    """Solicitud Traslado Zona Franca (ZF)."""

    TIPO_911 = 911
    """Decl. de Ingreso a Zona Franca Primaria."""

    TIPO_914 = 914
    """Declaración de Ingreso (DIN)."""

    TIPO_919 = 919
    """Resumen Vtas. Pasajes Nac. sin Factura."""

    TIPO_920 = 920
    """Otros registros no Docum. Aumenta Débito."""

    TIPO_922 = 922
    """Otros registros no Doc. Disminuye Débito."""

    TIPO_924 = 924
    """Resumen Vtas. Pasajes Inter. sin Fact."""

    def as_tipo_dte(self) -> TipoDte:
        """
        Return equivalent "Tipo DTE".

        :raises ValueError: if there is no equivalent one

        """
        try:
            value = TipoDte(self.value)
        except ValueError as exc:
            raise ValueError(
                f"There is no equivalent 'TipoDte' for 'RcvTipoDocto.{self.name}'."
            ) from exc

        return value
