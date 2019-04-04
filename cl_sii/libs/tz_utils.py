from datetime import datetime
from typing import Union

import pytz
import pytz.tzinfo


# note: pytz does some magic with its timezone classes so we need to "invent" a parent class.
PytzTimezone = Union[
    pytz.tzinfo.BaseTzInfo,
    pytz.tzinfo.StaticTzInfo,
    pytz.tzinfo.DstTzInfo,
    pytz._FixedOffset,  # type: ignore
]


UTC = pytz.UTC  # type: PytzTimezone
TIMEZONE_CL_SANTIAGO = pytz.timezone('America/Santiago')  # type: PytzTimezone


def get_now_tz_aware() -> datetime:
    """
    Return the current UTC date and time as a timezone-aware object.

    >>> get_now_tz_aware()
    datetime.datetime(2018, 10, 23, 1, 54, 13, tzinfo=<UTC>)

    """
    # The following implementation alternatives look prettier but are less-performant:
    #   - `convert_naive_dt_to_tz_aware(dt=datetime.utcnow(), tz=pytz.UTC)`
    #   - `pytz.UTC.localize(datetime.utcnow())`

    # source: 'django.utils.timezone.now' @ Django 2.1.3
    return datetime.utcnow().replace(tzinfo=UTC)


def convert_naive_dt_to_tz_aware(dt: datetime, tz: PytzTimezone) -> datetime:
    """
    Convert an offset-naive datetime object to a timezone-aware one.

    >>> dt_naive = datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_naive.isoformat()
    datetime.datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_naive.isoformat()
    '2018-10-23T01:54:13'

    >>> dt_tz_aware_1 = convert_naive_dt_to_tz_aware(dt_naive, UTC)
    >>> dt_tz_aware_1
    datetime.datetime(2018, 10, 23, 1, 54, 13, tzinfo=<UTC>)
    >>> dt_tz_aware_1.isoformat()
    '2018-10-23T04:54:13+00:00'

    >>> dt_tz_aware_2 = convert_naive_dt_to_tz_aware(dt_naive, TIMEZONE_CL_SANTIAGO)
    >>> dt_tz_aware_2
    datetime.datetime(2018, 10, 23, 1, 54, 13, tzinfo=<DstTzInfo 'America/Santiago'
    -03-1 day, 21:00:00 DST>)
    >>> dt_tz_aware_2.isoformat()
    '2018-10-23T01:54:13-03:00'

    :param dt: offset-naive datetime
    :param tz: timezone e.g. ``pytz.timezone('America/Santiago')``
    :raises ValueError: if ``dt`` is already timezone-aware

    """
    dt_tz_aware = tz.localize(dt)  # type: datetime
    return dt_tz_aware
