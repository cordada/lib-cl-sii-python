import datetime
import re
import unittest

from cl_sii.libs.tz_utils import (  # noqa: F401
    _TZ_CL_SANTIAGO,
    TZ_UTC,
    PytzTimezone,
    convert_naive_dt_to_tz_aware,
    convert_tz_aware_dt_to_naive,
    dt_is_aware,
    dt_is_naive,
    get_now_tz_aware,
    validate_dt_tz,
)


class FunctionsTest(unittest.TestCase):
    def test_get_now_tz_aware(self) -> None:
        # TODO: implement for 'get_now_tz_aware'
        # Reuse doctests/examples in function docstring.
        pass

    def test_convert_naive_dt_to_tz_aware(self) -> None:
        # TODO: implement for 'convert_naive_dt_to_tz_aware'
        # Reuse doctests/examples in function docstring.
        pass

    def test_convert_tz_aware_dt_to_naive(self) -> None:
        # TODO: implement for 'convert_tz_aware_dt_to_naive'
        # Reuse doctests/examples in function docstring.
        pass

    def test_dt_is_aware(self) -> None:
        # TODO: implement for 'dt_is_aware'
        # Reuse doctests/examples in function docstring.
        pass

    def test_dt_is_naive(self) -> None:
        # TODO: implement for 'dt_is_naive'
        # Reuse doctests/examples in function docstring.
        pass

    def test_validate_dt_tz(self) -> None:
        # TODO: implement for 'validate_dt_tz'
        pass

    def test_validate_dt_tz_tzinfo_zone_attribute_check(self) -> None:
        # Time zone: UTC. Source: Pytz:
        tzinfo_utc_pytz = TZ_UTC
        dt_with_tzinfo_utc_pytz = convert_naive_dt_to_tz_aware(
            datetime.datetime(2021, 1, 6, 15, 21),
            tzinfo_utc_pytz,
        )

        # Time zone: UTC. Source: Python Standard Library:
        tzinfo_utc_stdlib = datetime.timezone.utc
        dt_with_tzinfo_utc_stdlib = datetime.datetime.fromisoformat('2021-01-06T15:04+00:00')

        # Time zone: Not UTC. Source: Pytz:
        tzinfo_not_utc_pytz = _TZ_CL_SANTIAGO
        dt_with_tzinfo_not_utc_pytz = convert_naive_dt_to_tz_aware(
            datetime.datetime(2021, 1, 6, 15, 21),
            tzinfo_not_utc_pytz,
        )

        # Time zone: Not UTC. Source: Python Standard Library:
        tzinfo_not_utc_stdlib = datetime.timezone(datetime.timedelta(days=-1, seconds=75600))
        dt_with_tzinfo_not_utc_stdlib = datetime.datetime.fromisoformat('2021-01-06T15:04-03:00')

        # Test datetimes with UTC time zone:
        expected_error_message = re.compile(
            r"^Object datetime.timezone.utc must have 'zone' attribute.$"
        )
        with self.assertRaisesRegex(AssertionError, expected_error_message):
            validate_dt_tz(dt_with_tzinfo_utc_pytz, tzinfo_utc_stdlib)
        expected_error_message = re.compile(r"^Object UTC must have 'zone' attribute.$")
        with self.assertRaisesRegex(AssertionError, expected_error_message):
            validate_dt_tz(dt_with_tzinfo_utc_stdlib, tzinfo_utc_pytz)

        # Test datetimes with non-UTC time zone:
        expected_error_message = re.compile(
            r"^Object"
            r" datetime.timezone\(datetime.timedelta\(days=-1, seconds=75600\)\)"
            r" must have 'zone' attribute.$"
        )
        with self.assertRaisesRegex(AssertionError, expected_error_message):
            validate_dt_tz(dt_with_tzinfo_not_utc_pytz, tzinfo_not_utc_stdlib)  # type: ignore
        expected_error_message = re.compile(
            r"^Object" r" UTC-03:00" r" must have 'zone' attribute.$"
        )
        with self.assertRaisesRegex(AssertionError, expected_error_message):
            validate_dt_tz(dt_with_tzinfo_not_utc_stdlib, tzinfo_not_utc_pytz)
