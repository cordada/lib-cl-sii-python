"""
Timezone utils
==============


Naive and aware
---------------

These concept are defined in Python standard library module datetime
`docs <https://docs.python.org/3/library/datetime.html#module-datetime>`_.

"""
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


TZ_UTC = pytz.UTC  # type: PytzTimezone
_TZ_CL_SANTIAGO: PytzTimezone = pytz.timezone('America/Santiago')


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
    # warning: setting 'tzinfo' does not work for many timezones. To be safe, only use it for UTC
    #   and None.
    #   > Unfortunately using the tzinfo argument of the standard datetime constructors
    #   > "does not work" with pytz for many timezones.
    #   https://pythonhosted.org/pytz/#localized-times-and-date-arithmetic
    return datetime.utcnow().replace(tzinfo=TZ_UTC)


def convert_naive_dt_to_tz_aware(dt: datetime, tz: PytzTimezone) -> datetime:
    """
    Convert an offset-naive datetime object to a timezone-aware one.

    >>> dt_naive = datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_naive.isoformat()
    datetime.datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_naive.isoformat()
    '2018-10-23T01:54:13'

    >>> dt_tz_aware_1 = convert_naive_dt_to_tz_aware(dt_naive, TZ_UTC)
    >>> dt_tz_aware_1
    datetime.datetime(2018, 10, 23, 1, 54, 13, tzinfo=<UTC>)
    >>> dt_tz_aware_1.isoformat()
    '2018-10-23T04:54:13+00:00'

    >>> dt_tz_aware_2 = convert_naive_dt_to_tz_aware(dt_naive, _TZ_CL_SANTIAGO)
    >>> dt_tz_aware_2
    datetime.datetime(2018, 10, 23, 1, 54, 13, tzinfo=<DstTzInfo 'America/Santiago'
    -03-1 day, 21:00:00 DST>)
    >>> dt_tz_aware_2.isoformat()
    '2018-10-23T01:54:13-03:00'

    :param dt: offset-naive datetime
    :param tz: timezone e.g. ``pytz.timezone('America/Santiago')``
    :raises ValueError: if ``dt`` is already timezone-aware

    """
    # equivalent to:
    #   dt.astimezone(tz)
    dt_tz_aware = tz.localize(dt)  # type: datetime
    return dt_tz_aware


def convert_tz_aware_dt_to_naive(dt: datetime, tz: PytzTimezone = None) -> datetime:
    """
    Convert a timezone-aware datetime object to an offset-naive one.

    Default ``tz`` is UTC.

    >>> dt_tz_aware = datetime(2018, 10, 1, 2, 30, 0, tzinfo=TZ_UTC)
    >>> dt_tz_aware.isoformat()
    '2018-10-01T02:30:00+00:00'

    >>> dt_naive_utc = convert_tz_aware_dt_to_naive(dt_tz_aware, TZ_UTC)
    >>> dt_naive_utc.isoformat()
    '2018-10-01T02:30:00'

    >>> dt_naive_cl_santiago = convert_tz_aware_dt_to_naive(dt_tz_aware, _TZ_CL_SANTIAGO)
    >>> dt_naive_cl_santiago.isoformat()
    '2018-09-30T23:30:00'

    >>> int((dt_naive_cl_santiago - dt_naive_utc).total_seconds() / 3600)
    -3
    >>> (dt_naive_cl_santiago.date() - dt_naive_utc.date()).days
    -1

    :param dt: timezone-aware datetime
    :param tz: timezone e.g. ``pytz.timezone('America/Santiago')``
    :raises ValueError: if ``dt`` is not timezone-aware

    """
    if not dt_is_aware(dt):
        raise ValueError("Value must be a timezone-aware datetime object.")

    if tz is None:
        tz = TZ_UTC
    dt_naive = dt.astimezone(tz).replace(tzinfo=None)  # type: datetime
    return dt_naive


def dt_is_aware(value: datetime) -> bool:
    """
    Return whether datetime ``value`` is "aware".

    >>> dt_naive = datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_is_aware(dt_naive)
    False
    >>> dt_is_aware(convert_naive_dt_to_tz_aware(dt_naive, TZ_UTC))
    True
    >>> dt_is_aware(convert_naive_dt_to_tz_aware(dt_naive, _TZ_CL_SANTIAGO))
    True

    """
    if not isinstance(value, datetime):
        raise TypeError
    # source: 'django.utils.timezone.is_aware' @ Django 2.1.7
    return value.utcoffset() is not None


def dt_is_naive(value: datetime) -> bool:
    """
    Return whether datetime ``value`` is "naive".

    >>> dt_naive = datetime(2018, 10, 23, 1, 54, 13)
    >>> dt_is_naive(dt_naive)
    True
    >>> dt_is_naive(convert_naive_dt_to_tz_aware(dt_naive, TZ_UTC))
    False
    >>> dt_is_naive(convert_naive_dt_to_tz_aware(dt_naive, _TZ_CL_SANTIAGO))
    False

    """
    if not isinstance(value, datetime):
        raise TypeError
    # source: 'django.utils.timezone.is_naive' @ Django 2.1.7
    return value.utcoffset() is None


def validate_dt_tz(value: datetime, tz: PytzTimezone) -> None:
    """
    Validate that ``tz`` is the timezone of ``value``.
    """
    if not dt_is_aware(value):
        raise ValueError("Value must be a timezone-aware datetime object.")

    # The 'zone' attribute is not defined in the abstract base class 'datetime.tzinfo'. We need to
    # check that it is there before using it below to prevent unexpected exceptions when dealing
    # with Python Standard Library time zones that are instances of class 'datetime.timezone'.
    assert hasattr(value.tzinfo, 'zone'), f"Object {value.tzinfo!r} must have 'zone' attribute."
    assert hasattr(tz, 'zone'), f"Object {tz!r} must have 'zone' attribute."

    if value.tzinfo.zone != tz.zone:  # type: ignore
        raise ValueError(f"Timezone of datetime value must be '{tz.zone!s}'.", value)
