from __future__ import annotations

import json
import unittest
from typing import ClassVar, Optional

import pydantic

import cl_sii.dte.constants
from cl_sii.extras.pydantic_types import DteFolio
from cl_sii.extras.pydantic_types import Rut as PydanticRut
from cl_sii.rut import Rut


class PydanticRutTest(unittest.TestCase):
    """
    Tests for :class:`PydanticRut`.
    """

    ThirdPartyType: ClassVar[type[Rut]]
    PydanticThirdPartyType: ClassVar[type[PydanticRut]]
    pydantic_type_adapter: ClassVar[pydantic.TypeAdapter]
    valid_instance_1: ClassVar[Rut]
    valid_instance_2: ClassVar[Rut]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.ThirdPartyType = Rut
        cls.PydanticThirdPartyType = PydanticRut
        cls.pydantic_type_adapter = pydantic.TypeAdapter(cls.PydanticThirdPartyType)

        cls.valid_instance_1 = cls.ThirdPartyType('78773510-K')
        assert isinstance(cls.valid_instance_1, cls.ThirdPartyType)

        cls.valid_instance_2 = cls.ThirdPartyType('77004430-8')
        assert isinstance(cls.valid_instance_2, cls.ThirdPartyType)

    def test_serialize_to_python(self) -> None:
        # -----Arrange-----

        instance = self.valid_instance_1
        expected_serialized_value = '78773510-K'

        # -----Act-----

        actual_serialized_value = self.pydantic_type_adapter.dump_python(instance)

        # -----Assert-----

        self.assertEqual(expected_serialized_value, actual_serialized_value)

    def test_serialize_none_to_python(self) -> None:
        # -----Arrange-----

        instance = None

        # -----Act-----

        actual_serialized_value = self.pydantic_type_adapter.dump_python(instance)

        # -----Assert-----

        self.assertIsNone(actual_serialized_value)

    def test_serialize_to_json(self) -> None:
        # -----Arrange-----

        instance = self.valid_instance_1

        expected_serialized_value = b'"78773510-K"'
        self.assertEqual(
            expected_serialized_value, json.dumps(json.loads(expected_serialized_value)).encode()
        )

        # -----Act-----

        actual_serialized_value = self.pydantic_type_adapter.dump_json(instance)

        # -----Assert-----

        self.assertEqual(expected_serialized_value, actual_serialized_value)

    def test_serialize_none_to_json(self) -> None:
        # -----Arrange-----

        instance = None

        expected_serialized_value = b'null'
        self.assertEqual(
            expected_serialized_value, json.dumps(json.loads(expected_serialized_value)).encode()
        )

        # -----Act-----

        actual_serialized_value = self.pydantic_type_adapter.dump_json(instance)

        # -----Assert-----

        self.assertEqual(expected_serialized_value, actual_serialized_value)

    def test_deserialize_from_instance(self) -> None:
        # -----Arrange-----

        obj = self.valid_instance_2
        expected_deserialized_value = self.valid_instance_2

        # -----Act-----

        actual_deserialized_value = self.pydantic_type_adapter.validate_python(obj)

        # -----Assert-----

        self.assertEqual(expected_deserialized_value, actual_deserialized_value)

    def test_deserialize_from_python(self) -> None:
        # -----Arrange-----

        obj = '78773510-K'
        expected_deserialized_value = self.valid_instance_1

        # -----Act-----

        actual_deserialized_value = self.pydantic_type_adapter.validate_python(obj)

        # -----Assert-----

        self.assertEqual(expected_deserialized_value, actual_deserialized_value)

    def test_deserialize_from_json(self) -> None:
        # -----Arrange-----

        data = '"78773510-K"'
        self.assertEqual(data, json.dumps(json.loads(data)))

        expected_deserialized_value = self.valid_instance_1

        # -----Act-----

        actual_deserialized_value = self.pydantic_type_adapter.validate_json(data)

        # -----Assert-----

        self.assertEqual(expected_deserialized_value, actual_deserialized_value)

    def test_deserialize_invalid(self) -> None:
        test_items = [
            78773510,
            -78773510,
            '78773510-k',
            '78.773.510-K',
            '78773510-X',
            '-78773510-K',
            True,
            None,
        ]

        for test_item in test_items:
            obj = test_item
            data = json.dumps(test_item)

            with self.subTest(item=test_item):
                with self.assertRaises(pydantic.ValidationError):
                    self.pydantic_type_adapter.validate_python(obj)

                with self.assertRaises(pydantic.ValidationError):
                    self.pydantic_type_adapter.validate_json(data)

    def test_json_schema_for_validation(self) -> None:
        # -----Arrange-----

        expected_json_schema = {
            'type': 'string',
            'pattern': '^(\\d{1,8})-([\\dK])$',
        }

        # -----Act-----

        actual_json_schema = self.pydantic_type_adapter.json_schema(mode='validation')

        # -----Assert-----

        self.assertEqual(expected_json_schema, actual_json_schema)

    def test_json_schema_for_serialization(self) -> None:
        # -----Arrange-----

        expected_json_schema = {
            'type': 'string',
            'pattern': '^(\\d{1,8})-([\\dK])$',
        }

        # -----Act-----

        actual_json_schema = self.pydantic_type_adapter.json_schema(mode='serialization')

        # -----Assert-----

        self.assertEqual(expected_json_schema, actual_json_schema)


class DteFolioTest(unittest.TestCase):
    """
    Tests for :data:`DteFolio`.
    """

    pydantic_type_adapter: ClassVar[pydantic.TypeAdapter]
    expected_json_schema: ClassVar[dict[str, object]]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.pydantic_type_adapter = pydantic.TypeAdapter(DteFolio)
        cls.expected_json_schema = {
            'type': 'integer',
            'format': 'int64',
            'minimum': cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE,
            'maximum': cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE,
        }

    def test_deserialize_valid(self) -> None:
        test_items = [
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE,
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE,
        ]

        for test_item in test_items:
            with self.subTest(item=test_item):
                self.assertEqual(test_item, self.pydantic_type_adapter.validate_python(test_item))
                self.assertEqual(
                    test_item, self.pydantic_type_adapter.validate_json(json.dumps(test_item))
                )

    def test_deserialize_invalid(self) -> None:
        test_items = [
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE - 1,
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE + 1,
            None,
        ]

        for test_item in test_items:
            data = json.dumps(test_item)

            with self.subTest(item=test_item):
                with self.assertRaises(pydantic.ValidationError):
                    self.pydantic_type_adapter.validate_python(test_item)

                with self.assertRaises(pydantic.ValidationError):
                    self.pydantic_type_adapter.validate_json(data)

    def test_json_schema_for_validation(self) -> None:
        actual_json_schema = self.pydantic_type_adapter.json_schema(mode='validation')

        self.assertEqual(self.expected_json_schema, actual_json_schema)

    def test_json_schema_for_serialization(self) -> None:
        actual_json_schema = self.pydantic_type_adapter.json_schema(mode='serialization')

        self.assertEqual(self.expected_json_schema, actual_json_schema)

    def test_json_schema_in_model(self) -> None:
        # -----Arrange-----

        class ExampleModel(pydantic.BaseModel):
            folio: DteFolio
            optional_folio: Optional[DteFolio]
            folios: list[DteFolio]

        expected_properties = {
            'folio': {'title': 'Folio', **self.expected_json_schema},
            'optional_folio': {
                'title': 'Optional Folio',
                'anyOf': [self.expected_json_schema, {'type': 'null'}],
            },
            'folios': {
                'title': 'Folios',
                'type': 'array',
                'items': self.expected_json_schema,
            },
        }

        # -----Act-----

        actual_json_schema = ExampleModel.model_json_schema()

        # -----Assert-----

        self.assertEqual(expected_properties, actual_json_schema['properties'])
