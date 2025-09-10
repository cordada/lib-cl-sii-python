"""
cl_sii "extras" / Django-Filter.

(for Django views and DRF views)
"""

from __future__ import annotations


try:
    import django_filters
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'django-filter' is required to use this module.") from exc

from collections.abc import Sequence
from copy import deepcopy
from typing import Any, ClassVar, Mapping, Type

import django.db.models
import django.forms

import cl_sii.extras.dj_form_fields
import cl_sii.extras.dj_model_fields


FILTER_FOR_DBFIELD_DEFAULTS: Mapping[Type[django.db.models.Field], Mapping[str, object]] = {}


class RutFilter(django_filters.filters.CharFilter):
    """
    Matches on a RUT.

    Used with :class:`cl_sii.extras.dj_form_fields.RutField` by default.

    .. seealso::
        - https://django-filter.readthedocs.io/en/stable/ref/filters.html
        - https://github.com/carltongibson/django-filter/blob/24.2/docs/ref/filters.txt
    """

    field_class: Type[django.forms.Field]
    field_class = cl_sii.extras.dj_form_fields.RutField

    field_class_for_substrings: Type[django.forms.Field]
    field_class_for_substrings = django_filters.filters.CharFilter.field_class

    lookup_expressions_for_substrings: Sequence[str] = [
        'contains',
        'icontains',
        'startswith',
        'istartswith',
        'endswith',
        'iendswith',
    ]

    def __init__(
        self,
        field_name: Any = None,
        lookup_expr: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if lookup_expr in self.lookup_expressions_for_substrings:
            # Lookups that can be used to search for substrings will not always
            # work with the default field class because some substrings cannot
            # be converted to instances of class `Rut`. For example,
            # `…__contains="803"` fails because `Rut("803")` raises a `ValueError`.
            self.field_class = self.field_class_for_substrings

        super().__init__(field_name, lookup_expr, *args, **kwargs)


FILTER_FOR_DBFIELD_DEFAULTS = {
    **FILTER_FOR_DBFIELD_DEFAULTS,
    cl_sii.extras.dj_model_fields.RutField: {'filter_class': RutFilter},
}


class SiiFilterSet(django_filters.filterset.FilterSet):
    """
    Custom filterset with extra database field mappings.

    This class serves as a base class for filtersets that additionally need to
    support filtering one of the following database fields:
      - :class:`cl_sii.extras.dj_model_fields.RutField`

    .. seealso::
        - https://django-filter.readthedocs.io/en/main/ref/filterset.html
        - https://github.com/carltongibson/django-filter/blob/24.2/docs/ref/filterset.txt
    """

    FILTER_DEFAULTS: ClassVar[Mapping[Type[django.db.models.Field], Mapping[str, object]]]
    FILTER_DEFAULTS = {
        **deepcopy(django_filters.FilterSet.FILTER_DEFAULTS),
        **FILTER_FOR_DBFIELD_DEFAULTS,
    }
