import dataclasses
import unittest
from typing import Dict

from cl_sii.libs.dataclass_utils import (
    DcDeepCompareMixin, DcDeepComparison, dc_deep_compare, _dc_deep_compare_to,
)


@dataclasses.dataclass
class DataclassA:

    field_1: int = dataclasses.field()


@dataclasses.dataclass
class DataclassBWithoutMixin:

    field_1: object = dataclasses.field()
    field_2: Dict[str, object] = dataclasses.field()
    field_3: tuple = dataclasses.field()
    field_4: DataclassA = dataclasses.field()
    field_5: str = dataclasses.field(default=None)
    field_6: int = dataclasses.field(default=-1)


@dataclasses.dataclass
class DataclassBWithMixin(DataclassBWithoutMixin, DcDeepCompareMixin):

    pass


class NotADataclassWithMixin(DcDeepCompareMixin):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class DcDeepCompareTest(unittest.TestCase):

    def test__dc_deep_compare_ok(self) -> None:
        value_a_1 = DataclassA(field_1=23)
        value_a_2 = DataclassA(field_1='break typing hint, nobody cares')

        value_b_1 = DataclassBWithoutMixin(
            field_1=-56, field_2=dict(x=True), field_3=('hello', None, True), field_4=value_a_1)
        value_b_2 = DataclassBWithoutMixin(
            field_1=-56, field_2=dict(a='b'), field_3=('hello', None, True), field_4=value_a_1)
        value_b_3 = dataclasses.replace(value_b_1, field_5='some str')
        value_b_4 = dataclasses.replace(value_b_2, field_5='non-default value')
        value_b_5 = dataclasses.replace(value_b_2, field_4=value_a_2)

        self.assertEqual(_dc_deep_compare_to(value_b_1, value_b_1), DcDeepComparison.EQUAL)
        self.assertEqual(_dc_deep_compare_to(value_b_1, value_b_2), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_1, value_b_3), DcDeepComparison.SUBSET)
        self.assertEqual(_dc_deep_compare_to(value_b_1, value_b_4), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_1, value_b_5), DcDeepComparison.CONFLICTED)

        self.assertEqual(_dc_deep_compare_to(value_b_2, value_b_1), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_2, value_b_2), DcDeepComparison.EQUAL)
        self.assertEqual(_dc_deep_compare_to(value_b_2, value_b_3), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_2, value_b_4), DcDeepComparison.SUBSET)
        self.assertEqual(_dc_deep_compare_to(value_b_2, value_b_5), DcDeepComparison.CONFLICTED)

        self.assertEqual(_dc_deep_compare_to(value_b_3, value_b_1), DcDeepComparison.SUPERSET)
        self.assertEqual(_dc_deep_compare_to(value_b_3, value_b_2), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_3, value_b_3), DcDeepComparison.EQUAL)
        self.assertEqual(_dc_deep_compare_to(value_b_3, value_b_4), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_3, value_b_5), DcDeepComparison.CONFLICTED)

        self.assertEqual(_dc_deep_compare_to(value_b_4, value_b_1), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_4, value_b_2), DcDeepComparison.SUPERSET)
        self.assertEqual(_dc_deep_compare_to(value_b_4, value_b_3), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_4, value_b_4), DcDeepComparison.EQUAL)
        self.assertEqual(_dc_deep_compare_to(value_b_4, value_b_5), DcDeepComparison.CONFLICTED)

        self.assertEqual(_dc_deep_compare_to(value_b_5, value_b_1), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_5, value_b_2), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_5, value_b_3), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_5, value_b_4), DcDeepComparison.CONFLICTED)
        self.assertEqual(_dc_deep_compare_to(value_b_5, value_b_5), DcDeepComparison.EQUAL)

    def test_func_ok(self) -> None:
        self.assertEqual(
            dc_deep_compare(
                DataclassA(field_1=23),
                DataclassA(field_1=23)),
            DcDeepComparison.EQUAL)
        self.assertEqual(
            dc_deep_compare(
                DataclassA(field_1=23),
                DataclassA(field_1='break typing hint, nobody cares')),
            DcDeepComparison.CONFLICTED)

    def test_mixin_ok(self) -> None:
        value_a = DataclassBWithMixin(
            field_1=-56, field_2=dict(a='b'), field_3=('hello', None, True),
            field_4=DataclassA(field_1=23))
        value_b = dataclasses.replace(value_a, field_5='some str')
        self.assertEqual(
            value_a.deep_compare_to(value_b),
            DcDeepComparison.SUBSET)
        self.assertEqual(
            value_b.deep_compare_to(value_a),
            DcDeepComparison.SUPERSET)

    def test__dc_deep_compare_type_mismatch(self) -> None:
        value_a = DataclassA(field_1=23)
        value_b = DataclassBWithoutMixin(
            field_1=-56, field_2=dict(a='b'), field_3=('hello', None, True), field_4=value_a)

        with self.assertRaises(TypeError) as cm:
            _dc_deep_compare_to(value_b, value_a)
        self.assertEqual(cm.exception.args, ("Values to be compared must be of the same type.", ))
        with self.assertRaises(TypeError) as cm:
            _dc_deep_compare_to(value_a, value_b)
        self.assertEqual(cm.exception.args, ("Values to be compared must be of the same type.", ))

    def test_func_not_a_dataclass(self) -> None:
        dc_value_a = DataclassA(field_1=23)
        dc_value_b = DataclassBWithoutMixin(
            field_1=-56, field_2=dict(a='b'), field_3=('hello', None, True), field_4=dc_value_a)

        with self.assertRaises(Exception) as cm:
            dc_deep_compare(dict(), 123)
        self.assertEqual(cm.exception.args, ("Values must be dataclass instances.", ))

        with self.assertRaises(TypeError) as cm:
            dc_deep_compare(dc_value_a, None)
        self.assertEqual(cm.exception.args, ("Values must be dataclass instances.", ))
        with self.assertRaises(TypeError) as cm:
            dc_deep_compare(dc_value_b, None)
        self.assertEqual(cm.exception.args, ("Values must be dataclass instances.", ))

        with self.assertRaises(TypeError) as cm:
            dc_deep_compare(dc_value_a, ('abc', 56, []))
        self.assertEqual(cm.exception.args, ("Values must be dataclass instances.", ))
        with self.assertRaises(TypeError) as cm:
            dc_deep_compare(dc_value_b, ('abc', 56, []))
        self.assertEqual(cm.exception.args, ("Values must be dataclass instances.", ))

    def test_mixin_self_not_a_dataclass(self) -> None:
        value_1 = NotADataclassWithMixin(field_1='kjdhsf')
        value_2 = NotADataclassWithMixin(field_1=None)

        with self.assertRaises(Exception) as cm:
            value_1.deep_compare_to(value_2)
        self.assertEqual(
            cm.exception.args,
            ("Programming error. Only dataclasses may subclass 'DcDeepCompareMixin'.", ))

    def test_mixin_value_not_a_dataclass(self) -> None:
        value_a = DataclassA(field_1=23)
        value_b = DataclassBWithMixin(
            field_1=-56, field_2=dict(a='b'), field_3=('hello', None, True), field_4=value_a)

        with self.assertRaises(TypeError) as cm:
            value_b.deep_compare_to(None)
        self.assertEqual(cm.exception.args, ("Value must be a dataclass instance.", ))

        with self.assertRaises(TypeError) as cm:
            value_b.deep_compare_to(('abc', 56, []))
        self.assertEqual(cm.exception.args, ("Value must be a dataclass instance.", ))
