"""
cl_sii "extras" / Django-Filter.

(for Django views and DRF views)
"""

from __future__ import annotations


try:
    import django_filters
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'django-filter' is required to use this module.") from exc

from copy import deepcopy
from typing import ClassVar, Mapping, Tuple, Type

import django.db.models
import django.forms

import cl_sii.extras.dj_form_fields
import cl_sii.extras.dj_model_fields


FILTER_FOR_DBFIELD_DEFAULTS: Mapping[Type[django.db.models.Field], Mapping[str, object]]
FILTER_FOR_DBFIELD_DEFAULTS = deepcopy(django_filters.filterset.FILTER_FOR_DBFIELD_DEFAULTS)


class RutFilter(django_filters.filters.CharFilter):
    """
    Matches on a RUT.

    Used with :class:`cl_sii.extras.dj_form_fields.RutField` by default.

    .. seealso::
        - https://django-filter.readthedocs.io/en/stable/ref/filters.html
        - https://github.com/carltongibson/django-filter/blob/24.2/docs/ref/filters.txt
    """

    field_class: ClassVar[Type[django.forms.Field]]
    field_class = cl_sii.extras.dj_form_fields.RutField


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
    FILTER_DEFAULTS = FILTER_FOR_DBFIELD_DEFAULTS

    @classmethod
    def filter_for_lookup(
        cls, field: django.db.models.Field, lookup_type: str
    ) -> Tuple[Type[django_filters.filters.Filter], Mapping[str, object]]:
        filter_class, params = super().filter_for_lookup(field, lookup_type)

        # Override RUT containment lookups.
        if isinstance(field, cl_sii.extras.dj_model_fields.RutField) and lookup_type in (
            'contains',
            'icontains',
        ):
            filter_class, params = django_filters.filters.CharFilter, {}

        return filter_class, params
