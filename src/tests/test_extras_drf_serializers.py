from __future__ import annotations

import unittest

import django.db.models
import rest_framework.serializers

import cl_sii.extras.drf_serializers


class ModelSerializerFieldMappingTestCase(unittest.TestCase):
    """
    Tests for :attr:`model_serializer_field_mapping`.
    """

    def test_types(self) -> None:
        serializer_field_mapping = {
            **rest_framework.serializers.ModelSerializer.serializer_field_mapping,
            **cl_sii.extras.drf_serializers.model_serializer_field_mapping,
        }

        for k, v in serializer_field_mapping.items():
            self.assertTrue(issubclass(k, django.db.models.Field))
            self.assertTrue(issubclass(v, rest_framework.serializers.Field))
