"""
Base / constants
================

"""
from __future__ import annotations

import enum

import pytz

from cl_sii.libs.tz_utils import PytzTimezone


TZ_CL_SANTIAGO: PytzTimezone = pytz.timezone('America/Santiago')

SII_OFFICIAL_TZ = TZ_CL_SANTIAGO


class XmlSchemasVersionEnum(enum.Enum):
    """
    Enum of "SII XML Schema Version".
    The version name is selected considering the last updated timestamp
    of the files in the set

    """

    V2019_12_12_SII_RTC = '2019_12_12_sii_rtc'
    """
    Incremental update to version V2013_02_07_SII_OFFICIAL from the official
    XML schemas of AEC (Archivo Electrónico de Cesión).
    Source:
    https://github.com/cl-sii-extraoficial/archivos-oficiales/tree/c89dec54f664281721dcb77af327c4f6c58ec4ff/src/code/rtc/2019-12-12-schema_cesion

    Most recent modification timestamp of the XML schemas: 2019-12-12
    """

    V2017_10_23_LIBRE_DTE = '2017_10_23_libre_dte'
    """
    Incremental update to version V2013_02_07_SII_OFFICIAL, from an unofficial
    source since the files available on the SII website are outdated with respect
    to the regulations (and even the documentation PDFs published alongside)

    Source: repository/project "LibreDTE" at https://github.com/LibreDTE/libredte-lib

    Most recent modification timestamp of the XML schemas: 2017-10-23
    """

    V2013_02_07_SII_OFFICIAL = '2013_02_07_sii_official'
    """
    Official schemas of entities related to these domain concepts:
    - DTE (Documento Tributario Electrónico)
    - IECV (Información Electrónica de Libros de Compra y Venta)
    - LCE (Libros Contables Electrónicos)
    - RTC (Registro de Transferencia de Crédito)

    All the files have been preserved as they were; schemas are in their
    original text encoding (ISO-8859-1) and have not been modified in the
    slightest way.

    Sources (2021-04-19):
    http://www.sii.cl/factura_electronica/schema_dte.zip
    http://www.sii.cl/factura_electronica/schema_iecv.zip
    http://www.sii.cl/factura_electronica/schema_cesion.zip

    Most recent modification timestamp of the XML schemas: 2013-02-07
    """

    @classmethod
    def latest(cls) -> XmlSchemasVersionEnum:
        """Reference to the latest version available"""
        return cls.V2019_12_12_SII_RTC
