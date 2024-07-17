from __future__ import annotations


try:
    import rest_framework
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'djangorestframework' is required to use this module.") from exc
try:
    import django
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'Django' is required to use this module.") from exc

from typing import Mapping, Type

import django.db.models
import rest_framework.serializers

import cl_sii.extras.dj_model_fields
import cl_sii.extras.drf_fields


model_serializer_field_mapping: Mapping[
    Type[django.db.models.Field], Type[rest_framework.serializers.Field]
]
"""
Mapping of Django model fields to DRF serializer fields.

Use this to extend DRF serializers that inherit from :class:`ModelSerializer` so
that Django model fields from :mod:`cl_sii.extras.dj_model_fields` do not have
to be explicitly defined in the serializer.

Usage example:

>>> class ExampleSerializer(rest_framework.serializers.ModelSerializer):
...     serializer_field_mapping = {
...         **rest_framework.serializers.ModelSerializer.serializer_field_mapping,
...         **model_serializer_field_mapping,
...     }
"""
model_serializer_field_mapping = {
    cl_sii.extras.dj_model_fields.RutField: cl_sii.extras.drf_fields.RutField,
}
