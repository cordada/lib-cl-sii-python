from __future__ import annotations

import unittest

import django_filters

from cl_sii.extras import dj_form_fields, dj_model_fields
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

    def test_filter_class_lookup_expressions(self) -> None:
        expected_field_class = dj_form_fields.RutField
        for lookup_expr in [
            'exact',
            'iexact',
            'in',
            'gt',
            'gte',
            'lt',
            'lte',
        ]:
            with self.subTest(field_class=expected_field_class, lookup_expr=lookup_expr):
                filter_instance = RutFilter(lookup_expr=lookup_expr)
                self.assertIs(filter_instance.field_class, expected_field_class)

        expected_field_class = django_filters.CharFilter.field_class
        for lookup_expr in [
            'contains',
            'icontains',
            'startswith',
            'istartswith',
            'endswith',
            'iendswith',
        ]:
            with self.subTest(field_class=expected_field_class, lookup_expr=lookup_expr):
                filter_instance = RutFilter(lookup_expr=lookup_expr)
                self.assertIs(filter_instance.field_class, expected_field_class)

    # TODO: Add tests.


class SiiFilterSetTest(unittest.TestCase):
    """
    Tests for :class:`cl_sii.extras.dj_filters.SiiFilterSet`.
    """

    @unittest.skip("TODO: Implement for 'filter_for_lookup'.")
    def test_filter_for_lookup(self) -> None:
        assert SiiFilterSet.filter_for_lookup()

    def test_filter_for_lookup_types(self) -> None:
        field = dj_model_fields.RutField()

        expected_field_class = dj_form_fields.RutField
        for lookup_type in [
            'exact',
            'iexact',
            'gt',
            'gte',
            'lt',
            'lte',
        ]:
            with self.subTest(field_class=expected_field_class, lookup_type=lookup_type):
                filter_class, params = SiiFilterSet.filter_for_lookup(field, lookup_type)
                filter_instance = filter_class(**{'lookup_expr': lookup_type, **params})
                self.assertIs(filter_instance.field_class, expected_field_class)

        for lookup_type in [
            'in',
        ]:
            with self.subTest(field_class=expected_field_class, lookup_type=lookup_type):
                filter_class, params = SiiFilterSet.filter_for_lookup(field, lookup_type)
                filter_instance = filter_class(**{'lookup_expr': lookup_type, **params})
                self.assertTrue(issubclass(filter_instance.field_class, expected_field_class))

        expected_field_class = django_filters.CharFilter.field_class
        for lookup_type in [
            'contains',
            'icontains',
            'startswith',
            'istartswith',
            'endswith',
            'iendswith',
        ]:
            with self.subTest(field_class=expected_field_class, lookup_type=lookup_type):
                filter_class, params = SiiFilterSet.filter_for_lookup(field, lookup_type)
                filter_instance = filter_class(**{'lookup_expr': lookup_type, **params})
                self.assertIs(filter_instance.field_class, expected_field_class)

    # TODO: Add tests.
