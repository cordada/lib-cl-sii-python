from __future__ import annotations

import unittest

import django_filters

from cl_sii.extras.dj_filters import RutFilter, SiiFilterSet


class RutFilterTest(unittest.TestCase):
    """
    Tests for :class:`cl_sii.extras.dj_filters.RutFilter`.
    """

    @unittest.expectedFailure
    def test_new_instance(self) -> None:
        try:
            filter = RutFilter()
        except Exception as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        self.assertIsInstance(filter, RutFilter)
        self.assertIsInstance(filter, django_filters.filters.Filter)

    # TODO: Add tests.


class SiiFilterSetTest(unittest.TestCase):
    """
    Tests for :class:`cl_sii.extras.dj_filters.SiiFilterSet`.
    """

    @unittest.skip("TODO: Implement for 'filter_for_lookup'.")
    def test_filter_for_lookup(self) -> None:
        assert SiiFilterSet.filter_for_lookup()

    # TODO: Add tests.
