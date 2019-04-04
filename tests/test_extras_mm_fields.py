import unittest

import marshmallow

from cl_sii.extras.mm_fields import Rut, RutField


class RutFieldTest(unittest.TestCase):

    def setUp(self) -> None:

        class MyObj:
            def __init__(self, emisor_rut: Rut, other_field: int = None) -> None:
                self.emisor_rut = emisor_rut
                self.other_field = other_field

        class MyBadObj:
            def __init__(self, some_field: int) -> None:
                self.some_field = some_field

        class MyMmSchema(marshmallow.Schema):

            class Meta:
                strict = False

            emisor_rut = RutField(
                required=True,
                load_from='RUT of Emisor',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class MyMmSchemaStrict(marshmallow.Schema):

            class Meta:
                strict = True

            emisor_rut = RutField(
                required=True,
                load_from='RUT of Emisor',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        self.MyObj = MyObj
        self.MyBadObj = MyBadObj
        self.MyMmSchema = MyMmSchema
        self.MyMmSchemaStrict = MyMmSchemaStrict

    def test_load_ok_valid(self) -> None:
        schema = self.MyMmSchema()

        data_valid_1 = {'RUT of Emisor': '1-1'}
        data_valid_2 = {'RUT of Emisor': Rut('1-1')}
        data_valid_3 = {'RUT of Emisor': ' 1.111.111-k \t '}

        result = schema.load(data_valid_1)
        self.assertDictEqual(dict(result.data), {'emisor_rut': Rut('1-1')})
        self.assertDictEqual(dict(result.errors), {})

        result = schema.load(data_valid_2)
        self.assertDictEqual(dict(result.data), {'emisor_rut': Rut('1-1')})
        self.assertDictEqual(dict(result.errors), {})

        result = schema.load(data_valid_3)
        self.assertDictEqual(dict(result.data), {'emisor_rut': Rut('1111111-K')})
        self.assertDictEqual(dict(result.errors), {})

    def test_dump_ok_valid(self) -> None:
        schema = self.MyMmSchema()

        obj_valid_1 = self.MyObj(emisor_rut=Rut('1-1'))
        obj_valid_2 = self.MyObj(emisor_rut=None)

        data, errors = schema.dump(obj_valid_1)
        self.assertDictEqual(data, {'emisor_rut': '1-1', 'other_field': None})
        self.assertDictEqual(errors, {})

        data, errors = schema.dump(obj_valid_2)
        self.assertDictEqual(data, {'emisor_rut': None, 'other_field': None})
        self.assertDictEqual(errors, {})

    def test_dump_ok_strange(self) -> None:
        # If the class of the object to be dumped has attributes that do not match at all the
        #   fields of the schema, there are no errors! Even if the schema has `strict = True` set.

        schema = self.MyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        obj_valid_1 = self.MyBadObj(some_field=123)
        obj_valid_2 = self.MyBadObj(some_field=None)

        data, errors = schema.dump(obj_valid_1)
        self.assertEqual((data, errors), ({}, {}))

        data, errors = schema_strict.dump(obj_valid_1)
        self.assertEqual((data, errors), ({}, {}))

        data, errors = schema.dump(obj_valid_2)
        self.assertEqual((data, errors), ({}, {}))

        data, errors = schema_strict.dump(obj_valid_2)
        self.assertEqual((data, errors), ({}, {}))

    def test_load_fail(self) -> None:

        schema = self.MyMmSchema()

        data_invalid_1 = {'RUT of Emisor': '123123123123'}
        data_invalid_2 = {'RUT of Emisor': 123}
        data_invalid_3 = {'RUT of Emisor': None}
        data_invalid_4 = {}

        result = schema.load(data_invalid_1)
        self.assertDictEqual(dict(result.data), {})
        self.assertDictEqual(dict(result.errors), {'RUT of Emisor': ['Not a syntactically valid RUT.']})  # noqa: E501

        result = schema.load(data_invalid_2)
        self.assertDictEqual(dict(result.data), {})
        self.assertDictEqual(dict(result.errors), {'RUT of Emisor': ['Invalid input type.']})

        result = schema.load(data_invalid_3)
        self.assertDictEqual(dict(result.data), {})
        self.assertDictEqual(dict(result.errors), {'RUT of Emisor': ['Field may not be null.']})

        result = schema.load(data_invalid_4)
        self.assertDictEqual(dict(result.data), {})
        self.assertDictEqual(dict(result.errors), {'RUT of Emisor': ['Missing data for required field.']})  # noqa: E501

    def test_dump_fail(self) -> None:
        schema = self.MyMmSchema()

        obj_invalid_1 = self.MyObj(emisor_rut=20)
        obj_invalid_2 = self.MyObj(emisor_rut='123123123123')
        obj_invalid_3 = self.MyObj(emisor_rut='')

        data, errors = schema.dump(obj_invalid_1)
        self.assertDictEqual(errors, {'emisor_rut': ['Invalid input type.']})

        data, errors = schema.dump(obj_invalid_2)
        self.assertDictEqual(errors, {'emisor_rut': ['Not a syntactically valid RUT.']})

        data, errors = schema.dump(obj_invalid_3)
        self.assertDictEqual(errors, {'emisor_rut': ['Not a syntactically valid RUT.']})
