"""
Base / constants
================

"""
import pytz

from cl_sii.libs.tz_utils import PytzTimezone


TZ_CL_SANTIAGO: PytzTimezone = pytz.timezone('America/Santiago')

SII_OFFICIAL_TZ = TZ_CL_SANTIAGO
