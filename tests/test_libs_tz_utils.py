import unittest

from cl_sii.libs.tz_utils import (  # noqa: F401
    convert_naive_dt_to_tz_aware, convert_tz_aware_dt_to_naive,
    dt_is_aware, dt_is_naive, get_now_tz_aware, validate_dt_tz,
    PytzTimezone, TZ_UTC,
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
