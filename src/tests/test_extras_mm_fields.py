import decimal
import unittest
from datetime import date, datetime

import marshmallow

import cl_sii.dte.constants
from cl_sii.extras.mm_fields import (
    DteFolioField,
    RcvPeriodoTributario,
    RcvPeriodoTributarioField,
    RcvTipoDocto,
    RcvTipoDoctoField,
    Rut,
    RutField,
    TipoDte,
    TipoDteField,
)


class RutFieldTest(unittest.TestCase):
    def setUp(self) -> None:
        class MyObj:
            def __init__(self, emisor_rut: Rut, other_field: int = None) -> None:
                self.emisor_rut = emisor_rut
                self.other_field = other_field

        class MyBadObj:
            def __init__(self, some_field: int) -> None:
                self.some_field = some_field

        class DumpMyMmSchema(marshmallow.Schema):
            emisor_rut = RutField(
                required=True,
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class LoadMyMmSchema(marshmallow.Schema):
            emisor_rut = RutField(
                required=True,
                data_key='RUT of Emisor',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class MyMmSchemaStrict(marshmallow.Schema):
            emisor_rut = RutField(
                required=True,
                data_key='RUT of Emisor',
                validate_dv=True,
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        self.MyObj = MyObj
        self.MyBadObj = MyBadObj
        self.LoadMyMmSchema = LoadMyMmSchema
        self.DumpMyMmSchema = DumpMyMmSchema
        self.MyMmSchemaStrict = MyMmSchemaStrict

    def test_load_ok_valid(self) -> None:
        schema = self.LoadMyMmSchema()

        data_valid_1 = {'RUT of Emisor': '1-9'}
        data_valid_2 = {'RUT of Emisor': Rut('1-9')}
        data_valid_3 = {'RUT of Emisor': ' 1.111.119-k \t '}

        result = schema.load(data_valid_1)
        self.assertDictEqual(dict(result), {'emisor_rut': Rut('1-9')})

        result = schema.load(data_valid_2)
        self.assertDictEqual(dict(result), {'emisor_rut': Rut('1-9')})

        result = schema.load(data_valid_3)
        self.assertDictEqual(dict(result), {'emisor_rut': Rut('1111119-K')})

    def test_dump_ok_valid(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_valid_1 = self.MyObj(emisor_rut=Rut('1-9'))
        obj_valid_2 = self.MyObj(emisor_rut=None)

        data = schema.dump(obj_valid_1)
        self.assertDictEqual(data, {'emisor_rut': '1-9', 'other_field': None})

        data = schema.dump(obj_valid_2)
        self.assertDictEqual(data, {'emisor_rut': None, 'other_field': None})

    def test_dump_ok_strange(self) -> None:
        # If the class of the object to be dumped has attributes that do not match at all the
        #   fields of the schema, there are no errors!

        schema = self.DumpMyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        obj_valid_1 = self.MyBadObj(some_field=123)
        obj_valid_2 = self.MyBadObj(some_field=None)

        data = schema.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema.dump(obj_valid_2)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_2)
        self.assertEqual(data, {})

    def test_load_fail(self) -> None:
        schema = self.LoadMyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        data_invalid_1 = {'RUT of Emisor': '123123123123'}
        data_invalid_2 = {'RUT of Emisor': 123}
        data_invalid_3 = {'RUT of Emisor': None}
        data_invalid_4 = {}
        data_invalid_5 = {'RUT of Emisor': '1-1'}

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_1)
        self.assertDictEqual(
            cm.exception.messages, {'RUT of Emisor': ['Not a syntactically valid RUT.']}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_2)
        self.assertDictEqual(cm.exception.messages, {'RUT of Emisor': ['Invalid type.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_3)
        self.assertDictEqual(cm.exception.messages, {'RUT of Emisor': ['Field may not be null.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_4)
        self.assertDictEqual(
            cm.exception.messages, {'RUT of Emisor': ['Missing data for required field.']}
        )

        try:
            schema.load(data_invalid_5)
        except marshmallow.ValidationError as exc:
            self.fail(f'{exc.__class__.__name__} raised')

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema_strict.load(data_invalid_5)
        self.assertEqual(
            cm.exception.messages,
            {'RUT of Emisor': ["""RUT's "digito verificador" is incorrect."""]},
        )

    def test_dump_fail(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_invalid_1 = self.MyObj(emisor_rut=20)
        obj_invalid_2 = self.MyObj(emisor_rut='123123123123')
        obj_invalid_3 = self.MyObj(emisor_rut='')

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_1)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_2)
        self.assertEqual(cm.exception.messages, ['Not a syntactically valid RUT.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_3)
        self.assertEqual(cm.exception.messages, ['Not a syntactically valid RUT.'])


class TipoDteFieldTest(unittest.TestCase):
    def setUp(self) -> None:
        class MyObj:
            def __init__(self, tipo_dte: TipoDte, other_field: int = None) -> None:
                self.tipo_dte = tipo_dte
                self.other_field = other_field

        class MyBadObj:
            def __init__(self, some_field: int) -> None:
                self.some_field = some_field

        class LoadMyMmSchema(marshmallow.Schema):
            tipo_dte = TipoDteField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class DumpMyMmSchema(marshmallow.Schema):
            tipo_dte = TipoDteField(
                required=True,
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class MyMmSchemaStrict(marshmallow.Schema):
            tipo_dte = TipoDteField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        self.MyObj = MyObj
        self.MyBadObj = MyBadObj
        self.LoadMyMmSchema = LoadMyMmSchema
        self.DumpMyMmSchema = DumpMyMmSchema
        self.MyMmSchemaStrict = MyMmSchemaStrict

    def test_load_ok_valid(self) -> None:
        schema = self.LoadMyMmSchema()

        data_valid_1 = {'source field name': 33}
        data_valid_2 = {'source field name': TipoDte(33)}
        data_valid_3 = {'source field name': '  33 \t '}

        data = schema.load(data_valid_1)
        self.assertDictEqual(data, {'tipo_dte': TipoDte(33)})

        data = schema.load(data_valid_2)
        self.assertDictEqual(data, {'tipo_dte': TipoDte(33)})

        data = schema.load(data_valid_3)
        self.assertDictEqual(data, {'tipo_dte': TipoDte(33)})

    def test_dump_ok_valid(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_valid_1 = self.MyObj(tipo_dte=TipoDte(33))
        obj_valid_2 = self.MyObj(tipo_dte=None)

        data = schema.dump(obj_valid_1)
        self.assertDictEqual(data, {'tipo_dte': 33, 'other_field': None})

        data = schema.dump(obj_valid_2)
        self.assertDictEqual(data, {'tipo_dte': None, 'other_field': None})

    def test_dump_ok_strange(self) -> None:
        # If the class of the object to be dumped has attributes that do not match at all the
        #   fields of the schema, there are no errors!

        schema = self.DumpMyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        obj_valid_1 = self.MyBadObj(some_field=123)
        obj_valid_2 = self.MyBadObj(some_field=None)

        data = schema.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema.dump(obj_valid_2)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_2)
        self.assertEqual(data, {})

    def test_load_fail(self) -> None:
        schema = self.LoadMyMmSchema()

        data_invalid_1 = {'source field name': '123'}
        data_invalid_2 = {'source field name': True}
        data_invalid_3 = {'source field name': None}
        data_invalid_4 = {}

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_1)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ['Not a valid Tipo DTE.']}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_2)
        self.assertDictEqual(cm.exception.messages, {'source field name': ['Invalid type.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_3)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ['Field may not be null.']}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_4)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ['Missing data for required field.']}
        )

    def test_dump_fail(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_invalid_1 = self.MyObj(tipo_dte=100)
        obj_invalid_2 = self.MyObj(tipo_dte=True)
        obj_invalid_3 = self.MyObj(tipo_dte='FACTURA_ELECTRONICA')
        obj_invalid_4 = self.MyObj(tipo_dte='')
        obj_invalid_5 = self.MyObj(tipo_dte=date(2018, 12, 23))

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_1)
        self.assertEqual(cm.exception.messages, ['Not a valid Tipo DTE.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_2)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_3)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_4)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_5)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])


class RcvTipoDoctoFieldTest(unittest.TestCase):
    def setUp(self) -> None:
        class MyObj:
            def __init__(self, tipo_docto: RcvTipoDocto, other_field: int = None) -> None:
                self.tipo_docto = tipo_docto
                self.other_field = other_field

        class MyBadObj:
            def __init__(self, some_field: int) -> None:
                self.some_field = some_field

        class DumpMyMmSchema(marshmallow.Schema):
            tipo_docto = RcvTipoDoctoField(
                required=True,
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class LoadMyMmSchema(marshmallow.Schema):
            tipo_docto = RcvTipoDoctoField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class MyMmSchemaStrict(marshmallow.Schema):
            tipo_docto = RcvTipoDoctoField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        self.MyObj = MyObj
        self.MyBadObj = MyBadObj
        self.LoadMyMmSchema = LoadMyMmSchema
        self.DumpMyMmSchema = DumpMyMmSchema
        self.MyMmSchemaStrict = MyMmSchemaStrict

    def test_load_ok_valid(self) -> None:
        schema = self.LoadMyMmSchema()

        data_valid_1 = {'source field name': 33}
        data_valid_2 = {'source field name': RcvTipoDocto(33)}
        data_valid_3 = {'source field name': '  33 \t '}

        result = schema.load(data_valid_1)
        self.assertDictEqual(dict(result), {'tipo_docto': RcvTipoDocto(33)})

        result = schema.load(data_valid_2)
        self.assertDictEqual(dict(result), {'tipo_docto': RcvTipoDocto(33)})

        result = schema.load(data_valid_3)
        self.assertDictEqual(dict(result), {'tipo_docto': RcvTipoDocto(33)})

    def test_dump_ok_valid(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_valid_1 = self.MyObj(tipo_docto=RcvTipoDocto(33))
        obj_valid_2 = self.MyObj(tipo_docto=None)

        data = schema.dump(obj_valid_1)
        self.assertDictEqual(data, {'tipo_docto': 33, 'other_field': None})

        data = schema.dump(obj_valid_2)
        self.assertDictEqual(data, {'tipo_docto': None, 'other_field': None})

    def test_dump_ok_strange(self) -> None:
        # If the class of the object to be dumped has attributes that do not match at all the
        #   fields of the schema, there are no errors!

        schema = self.DumpMyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        obj_valid_1 = self.MyBadObj(some_field=123)
        obj_valid_2 = self.MyBadObj(some_field=None)

        data = schema.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema.dump(obj_valid_2)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_2)
        self.assertEqual(data, {})

    def test_load_fail(self) -> None:
        schema = self.LoadMyMmSchema()

        data_invalid_1 = {'source field name': '123'}
        data_invalid_2 = {'source field name': True}
        data_invalid_3 = {'source field name': None}
        data_invalid_4 = {}

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_1)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ["Not a valid RCV's Tipo de Documento."]}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_2)
        self.assertDictEqual(cm.exception.messages, {'source field name': ['Invalid type.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_3)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ['Field may not be null.']}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_4)
        self.assertDictEqual(
            cm.exception.messages, {'source field name': ['Missing data for required field.']}
        )

    def test_dump_fail(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_invalid_1 = self.MyObj(tipo_docto=100)
        obj_invalid_2 = self.MyObj(tipo_docto=True)
        obj_invalid_3 = self.MyObj(tipo_docto='FACTURA_ELECTRONICA')
        obj_invalid_4 = self.MyObj(tipo_docto='')
        obj_invalid_5 = self.MyObj(tipo_docto=date(2018, 12, 23))

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_1)
        self.assertEqual(cm.exception.messages, ["Not a valid RCV's Tipo de Documento."])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_2)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_3)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_4)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_5)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])


class RcvPeriodoTributarioFieldTest(unittest.TestCase):
    def setUp(self) -> None:
        class MyObj:
            def __init__(
                self,
                periodo_tributario: RcvPeriodoTributario,
                other_field: int = None,
            ) -> None:
                self.periodo_tributario = periodo_tributario
                self.other_field = other_field

        class MyBadObj:
            def __init__(self, some_field: int) -> None:
                self.some_field = some_field

        class DumpMyMmSchema(marshmallow.Schema):
            periodo_tributario = RcvPeriodoTributarioField(
                required=True,
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class LoadMyMmSchema(marshmallow.Schema):
            periodo_tributario = RcvPeriodoTributarioField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        class MyMmSchemaStrict(marshmallow.Schema):
            periodo_tributario = RcvPeriodoTributarioField(
                required=True,
                data_key='source field name',
            )
            other_field = marshmallow.fields.Integer(
                required=False,
            )

        self.MyObj = MyObj
        self.MyBadObj = MyBadObj
        self.DumpMyMmSchema = DumpMyMmSchema
        self.LoadMyMmSchema = LoadMyMmSchema
        self.MyMmSchemaStrict = MyMmSchemaStrict

    def test_load_ok_valid(self) -> None:
        schema = self.LoadMyMmSchema()

        data_valid_1 = {'source field name': '2019-12'}
        data_valid_2 = {'source field name': RcvPeriodoTributario(year=2019, month=12)}
        data_valid_3 = {'source field name': '2019-09'}
        data_valid_4 = {'source field name': '2019-9'}

        result = schema.load(data_valid_1)
        self.assertEqual(
            dict(result),
            {'periodo_tributario': RcvPeriodoTributario(year=2019, month=12)},
        )

        result = schema.load(data_valid_2)
        self.assertEqual(
            dict(result),
            {'periodo_tributario': RcvPeriodoTributario(year=2019, month=12)},
        )

        result = schema.load(data_valid_3)
        self.assertEqual(
            dict(result),
            {'periodo_tributario': RcvPeriodoTributario(year=2019, month=9)},
        )

        result = schema.load(data_valid_4)
        self.assertEqual(
            dict(result),
            {'periodo_tributario': RcvPeriodoTributario(year=2019, month=9)},
        )

    def test_dump_ok_valid(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_valid_1 = self.MyObj(periodo_tributario=RcvPeriodoTributario(year=2019, month=12))
        obj_valid_2 = self.MyObj(periodo_tributario=RcvPeriodoTributario(year=2019, month=9))
        obj_valid_3 = self.MyObj(periodo_tributario=None)

        data = schema.dump(obj_valid_1)
        self.assertEqual(data, {'periodo_tributario': '2019-12', 'other_field': None})

        data = schema.dump(obj_valid_2)
        self.assertEqual(data, {'periodo_tributario': '2019-09', 'other_field': None})

        data = schema.dump(obj_valid_3)
        self.assertEqual(data, {'periodo_tributario': None, 'other_field': None})

    def test_dump_ok_strange(self) -> None:
        # If the class of the object to be dumped has attributes that do not match at all the
        #   fields of the schema, there are no errors!

        schema = self.DumpMyMmSchema()
        schema_strict = self.MyMmSchemaStrict()

        obj_valid_1 = self.MyBadObj(some_field=123)
        obj_valid_2 = self.MyBadObj(some_field=None)

        data = schema.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_1)
        self.assertEqual(data, {})

        data = schema.dump(obj_valid_2)
        self.assertEqual(data, {})

        data = schema_strict.dump(obj_valid_2)
        self.assertEqual(data, {})

    def test_load_fail(self) -> None:
        schema = self.LoadMyMmSchema()

        data_invalid_1 = {'source field name': '2019-12-01'}
        data_invalid_2 = {'source field name': 201912}
        data_invalid_3 = {'source field name': ''}
        data_invalid_4 = {'source field name': None}
        data_invalid_5 = {}

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_1)
        self.assertEqual(
            cm.exception.messages, {'source field name': ['Not a valid RCV Periodo Tributario.']}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_2)
        self.assertEqual(cm.exception.messages, {'source field name': ['Invalid type.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_3)
        self.assertEqual(
            cm.exception.messages, {'source field name': ["Not a valid RCV Periodo Tributario."]}
        )

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_4)
        self.assertEqual(cm.exception.messages, {'source field name': ['Field may not be null.']})

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.load(data_invalid_5)
        self.assertEqual(
            cm.exception.messages, {'source field name': ['Missing data for required field.']}
        )

    def test_dump_fail(self) -> None:
        schema = self.DumpMyMmSchema()

        obj_invalid_1 = self.MyObj(periodo_tributario='2019-12-01')
        obj_invalid_2 = self.MyObj(periodo_tributario=date(2019, 12, 1))
        obj_invalid_3 = self.MyObj(periodo_tributario=datetime(2019, 12, 1, 22, 33))
        obj_invalid_4 = self.MyObj(periodo_tributario='')
        obj_invalid_5 = self.MyObj(periodo_tributario=201912)
        obj_invalid_6 = self.MyObj(periodo_tributario='  2019-12-01')

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_1)
        self.assertEqual(cm.exception.messages, ["Not a valid RCV Periodo Tributario."])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_2)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_3)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_4)
        self.assertEqual(cm.exception.messages, ["Not a valid RCV Periodo Tributario."])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_5)
        self.assertEqual(cm.exception.messages, ['Invalid type.'])

        with self.assertRaises(marshmallow.ValidationError) as cm:
            schema.dump(obj_invalid_6)
        self.assertEqual(cm.exception.messages, ["Not a valid RCV Periodo Tributario."])


class DteFolioFieldTest(unittest.TestCase):
    def test_load_valid(self) -> None:
        class MyMmSchema(marshmallow.Schema):
            folio = DteFolioField(required=True)

        schema = MyMmSchema()
        test_items = [
            (cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE, 1),
            (cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE, 10000000000),
            ('10000000000', 10000000000),
            (' 5 ', 5),
            (1.0, 1),
            (decimal.Decimal('1'), 1),
        ]

        for value, expected_value in test_items:
            with self.subTest(value=value):
                self.assertEqual({'folio': expected_value}, schema.load({'folio': value}))

    def test_load_invalid(self) -> None:
        class MyMmSchema(marshmallow.Schema):
            folio = DteFolioField(required=True)

        schema = MyMmSchema()
        test_items = [
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE - 1,
            cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE + 1,
            1.5,
            decimal.Decimal('1.9'),
            decimal.Decimal('NaN'),
            decimal.Decimal('Infinity'),
            float('nan'),
            float('inf'),
            '1.5',
            True,
            False,
            None,
        ]

        for value in test_items:
            with self.subTest(value=value):
                with self.assertRaises(marshmallow.ValidationError):
                    schema.load({'folio': value})

    def test_load_strict(self) -> None:
        class MyMmSchema(marshmallow.Schema):
            folio = DteFolioField(required=True, strict=True)

        schema = MyMmSchema()

        self.assertEqual({'folio': 5}, schema.load({'folio': 5}))
        for value in ['5', 1.0]:
            with self.subTest(value=value):
                with self.assertRaises(marshmallow.ValidationError):
                    schema.load({'folio': value})

    def test_dump(self) -> None:
        class MyMmSchema(marshmallow.Schema):
            folio = DteFolioField(required=True)

        class MyObj:
            def __init__(self, folio: int) -> None:
                self.folio = folio

        schema = MyMmSchema()

        self.assertEqual({'folio': 10000000000}, schema.dump(MyObj(folio=10000000000)))

    def test_custom_min_value_and_max_value(self) -> None:
        class MyMmSchema(marshmallow.Schema):
            folio = DteFolioField(required=True, min_value=100, max_value=200)

        schema = MyMmSchema()

        self.assertEqual({'folio': 100}, schema.load({'folio': 100}))
        self.assertEqual({'folio': 200}, schema.load({'folio': 200}))
        for value in [99, 201]:
            with self.subTest(value=value):
                with self.assertRaises(marshmallow.ValidationError):
                    schema.load({'folio': value})

    def test_custom_validate_is_added(self) -> None:
        def validate_even(value: int) -> None:
            if value % 2 != 0:
                raise marshmallow.ValidationError('Not even.')

        test_items = [validate_even, [validate_even]]

        for validate in test_items:
            with self.subTest(validate=validate):

                class MyMmSchema(marshmallow.Schema):
                    folio = DteFolioField(required=True, validate=validate)

                schema = MyMmSchema()

                self.assertEqual({'folio': 2}, schema.load({'folio': 2}))
                with self.assertRaises(marshmallow.ValidationError):
                    schema.load({'folio': 3})
                with self.assertRaises(marshmallow.ValidationError):
                    schema.load({'folio': 0})

    def test_metadata(self) -> None:
        self.assertEqual({'format': 'int64'}, DteFolioField().metadata)

    def test_custom_metadata_is_merged(self) -> None:
        field = DteFolioField(metadata={'description': 'Folio of the DTE.'})

        self.assertEqual({'format': 'int64', 'description': 'Folio of the DTE.'}, field.metadata)
