import unittest

from cl_sii import rut  # noqa: F401
from cl_sii.rut import constants  # noqa: F401


class RutTest(unittest.TestCase):

    valid_rut_canonical: str
    valid_rut_dv: str
    valid_rut_digits: str
    valid_rut_digits_with_dots: str
    valid_rut_verbose: str
    valid_rut_leading_zero: str
    valid_rut_zero_zero: str
    valid_rut_zero_zero_dv: str

    invalid_rut_canonical: str
    invalid_rut_dv: str

    valid_rut_instance: rut.Rut
    invalid_rut_instance: rut.Rut
    valid_rut_instance_copy: rut.Rut
    valid_rut_leading_zero_instance: rut.Rut

    valid_rut_2_canonical: str
    valid_rut_2_instance: rut.Rut
    valid_rut_3_canonical: str
    valid_rut_3_instance: rut.Rut

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_rut_canonical = '6824160-K'
        cls.valid_rut_dv = 'K'
        cls.valid_rut_digits = '6824160'
        cls.valid_rut_digits_with_dots = '6.824.160'
        cls.valid_rut_verbose = '6.824.160-K'
        cls.valid_rut_leading_zero = '06824160-K'
        cls.valid_rut_zero_zero = '0-0'
        cls.valid_rut_zero_zero_dv = '0'

        cls.invalid_rut_canonical = '6824160-0'
        cls.invalid_rut_dv = '0'

        cls.valid_rut_instance = rut.Rut(cls.valid_rut_canonical)
        cls.invalid_rut_instance = rut.Rut(cls.invalid_rut_canonical)
        cls.valid_rut_instance_copy = rut.Rut(cls.valid_rut_canonical)
        cls.valid_rut_leading_zero_instance = rut.Rut(cls.valid_rut_leading_zero)

        cls.valid_rut_2_canonical = '60803000-K'
        cls.valid_rut_2_instance = rut.Rut(cls.valid_rut_2_canonical)
        cls.valid_rut_3_canonical = '61002000-3'
        cls.valid_rut_3_instance = rut.Rut(cls.valid_rut_3_canonical)

    ############################################################################
    # instance
    ############################################################################

    def test_fail_type_error(self) -> None:
        with self.assertRaises(TypeError):
            rut.Rut(object())
        with self.assertRaises(TypeError):
            rut.Rut(1)
        with self.assertRaises(TypeError):
            rut.Rut(None)

    def test_ok_same_type(self) -> None:
        self.assertEqual(
            rut.Rut(rut.Rut('1-1')),
            rut.Rut('1-1'),
        )

    def test_instance_empty_string(self) -> None:
        rut_value = ''
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut(rut_value)

        exception = context_manager.exception
        message, value = exception.args
        self.assertEqual(message, 'Syntactically invalid RUT.')
        self.assertEqual(value, rut_value, 'Different RUT value.')

    def test_instance_invalid_rut_format(self) -> None:
        rut_value = 'invalid rut format'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut(rut_value)

        exception = context_manager.exception
        message, value = exception.args
        self.assertEqual(message, 'Syntactically invalid RUT.')
        self.assertEqual(value, rut_value, 'Different RUT value.')

    def test_instance_short_rut(self) -> None:
        rut_value = '1-0'
        rut.Rut(rut_value)

    def test_instance_long_rut(self) -> None:
        rut_value = '123456789-0'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut(rut_value)

        exception = context_manager.exception
        message, value = exception.args
        self.assertEqual(message, 'Syntactically invalid RUT.')
        self.assertEqual(value, rut_value, 'Different RUT value.')

    def test_instance_validate_dv_ok(self) -> None:
        rut.Rut(self.valid_rut_canonical, validate_dv=True)

    def test_instance_validate_dv_in_lowercase(self) -> None:
        rut_instance = rut.Rut(self.valid_rut_canonical.lower(), validate_dv=True)
        self.assertFalse(rut_instance.dv.isnumeric())
        self.assertEqual(rut_instance.dv, self.valid_rut_dv)

    def test_instance_validate_dv_raise_exception(self) -> None:
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut(self.invalid_rut_canonical, validate_dv=True)

        exception = context_manager.exception
        message, value = exception.args
        self.assertEqual(message, "RUT's \"digito verificador\" is incorrect.")
        self.assertEqual(value, self.invalid_rut_canonical, 'Different RUT value.')

    ############################################################################
    # properties
    ############################################################################

    def test_canonical(self) -> None:
        self.assertEqual(self.valid_rut_instance.dv, self.valid_rut_dv)

    def test_verbose(self) -> None:
        self.assertEqual(self.valid_rut_instance.verbose, self.valid_rut_verbose)

    def test_digits(self) -> None:
        self.assertEqual(self.valid_rut_instance.digits, self.valid_rut_digits)

    def test_digits_with_dots(self) -> None:
        self.assertEqual(self.valid_rut_instance.digits_with_dots, self.valid_rut_digits_with_dots)

    def test_dv(self) -> None:
        self.assertEqual(self.valid_rut_instance.dv, self.valid_rut_dv)

    def test_dv_upper(self) -> None:
        self.assertTrue(self.valid_rut_instance.dv.isupper())

    ############################################################################
    # magic methods
    ############################################################################

    def test__str__(self) -> None:
        self.assertEqual(self.valid_rut_instance.__str__(), self.valid_rut_canonical)

    def test__repr__(self) -> None:
        rut_repr = f"Rut('{self.valid_rut_canonical}')"
        self.assertEqual(self.valid_rut_instance.__repr__(), rut_repr)

    def test__lt__true(self) -> None:
        # "<"
        self.assertLess(self.valid_rut_instance, self.valid_rut_2_instance)
        self.assertLess(self.valid_rut_2_instance, self.valid_rut_3_instance)

        # "<" and leading zero
        self.assertLess(self.valid_rut_leading_zero_instance, self.valid_rut_2_instance)

    def test__lt__false(self) -> None:
        # ">"
        self.assertFalse(self.valid_rut_2_instance < self.valid_rut_instance)
        self.assertFalse(self.valid_rut_3_instance < self.valid_rut_2_instance)

        # ">" and leading zero
        self.assertFalse(self.valid_rut_2_instance < self.valid_rut_leading_zero_instance)

        # "="
        self.assertFalse(self.valid_rut_instance < self.valid_rut_instance_copy)

    def test__lt__not_rut_instance(self) -> None:
        self.assertIs(self.valid_rut_instance.__lt__(self.valid_rut_canonical), NotImplemented)

    def test__le__true(self) -> None:
        # "<"
        self.assertLessEqual(self.valid_rut_instance, self.valid_rut_2_instance)
        self.assertLessEqual(self.valid_rut_2_instance, self.valid_rut_3_instance)

        # "<" and leading zero
        self.assertLessEqual(self.valid_rut_leading_zero_instance, self.valid_rut_2_instance)

        # "="
        self.assertLessEqual(self.valid_rut_instance, self.valid_rut_instance_copy)

    def test__le__false(self) -> None:
        # ">"
        self.assertFalse(self.valid_rut_2_instance <= self.valid_rut_instance)
        self.assertFalse(self.valid_rut_3_instance <= self.valid_rut_2_instance)

        # ">" and leading zero
        self.assertFalse(self.valid_rut_2_instance <= self.valid_rut_leading_zero_instance)

    def test__le__not_rut_instance(self) -> None:
        self.assertIs(self.valid_rut_instance.__le__(self.valid_rut_canonical), NotImplemented)

    def test__eq__true(self) -> None:
        rut_instance = rut.Rut(self.valid_rut_canonical)
        self.assertTrue(self.valid_rut_instance.__eq__(rut_instance))

    def test__eq__false(self) -> None:
        self.assertFalse(self.valid_rut_instance.__eq__(self.invalid_rut_instance))

    def test__eq__not_rut_instance(self) -> None:
        self.assertFalse(self.valid_rut_instance.__eq__(self.valid_rut_canonical))

    def test__gt__true(self) -> None:
        # ">"
        self.assertGreater(self.valid_rut_2_instance, self.valid_rut_instance)
        self.assertGreater(self.valid_rut_3_instance, self.valid_rut_2_instance)

        # ">" and leading zero
        self.assertGreater(self.valid_rut_2_instance, self.valid_rut_leading_zero_instance)

    def test__gt__false(self) -> None:
        # "<"
        self.assertFalse(self.valid_rut_instance > self.valid_rut_2_instance)
        self.assertFalse(self.valid_rut_2_instance > self.valid_rut_3_instance)

        # "<" and leading zero
        self.assertFalse(self.valid_rut_leading_zero_instance > self.valid_rut_2_instance)

        # "="
        self.assertFalse(self.valid_rut_instance > self.valid_rut_instance_copy)

    def test__gt__not_rut_instance(self) -> None:
        self.assertIs(
            self.valid_rut_instance.__gt__(self.valid_rut_canonical),  # type: ignore
            NotImplemented,
        )

    def test__ge__true(self) -> None:
        # ">"
        self.assertGreaterEqual(self.valid_rut_2_instance, self.valid_rut_instance)
        self.assertGreaterEqual(self.valid_rut_3_instance, self.valid_rut_2_instance)

        # ">" and leading zero
        self.assertGreaterEqual(self.valid_rut_2_instance, self.valid_rut_leading_zero_instance)

        # "="
        self.assertGreaterEqual(self.valid_rut_instance, self.valid_rut_instance_copy)

    def test__ge__false(self) -> None:
        # "<"
        self.assertFalse(self.valid_rut_instance >= self.valid_rut_2_instance)
        self.assertFalse(self.valid_rut_2_instance >= self.valid_rut_3_instance)

        # "<" and leading zero
        self.assertFalse(self.valid_rut_leading_zero_instance >= self.valid_rut_2_instance)

    def test__ge__not_rut_instance(self) -> None:
        self.assertIs(
            self.valid_rut_instance.__ge__(self.valid_rut_canonical),  # type: ignore
            NotImplemented,
        )

    def test__hash__(self) -> None:
        rut_hash = hash(self.valid_rut_instance.canonical)
        self.assertEqual(self.valid_rut_instance.__hash__(), rut_hash)

    ############################################################################
    # class methods
    ############################################################################

    def test_clean_str_lowercase(self) -> None:
        rut_value = f'  {self.valid_rut_verbose.lower()}  '
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_canonical)

    def test_clean_type_error(self) -> None:
        with self.assertRaises(AttributeError) as context_manager:
            rut.Rut.clean_str(1)  # type: ignore

        exception = context_manager.exception
        self.assertEqual(len(exception.args), 1)
        message = exception.args[0]
        self.assertEqual(message, "'int' object has no attribute 'strip'")

    def test_clean_str_leading_zeros(self) -> None:
        # One leading zero
        rut_value = f'0{self.valid_rut_canonical}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_canonical)

        # Two leading zeros
        rut_value = f'00{self.valid_rut_canonical}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_canonical)

        # Eight leading zeros
        rut_value = f'00000000{self.valid_rut_canonical}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_canonical)

        # RUT 0-0
        rut_value = self.valid_rut_zero_zero
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_zero_zero)

        # RUT 0-0 with one extra leading zero
        rut_value = f'0{self.valid_rut_zero_zero}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_zero_zero)

        # RUT 0-0 with two extra leading zero
        rut_value = f'00{self.valid_rut_zero_zero}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_zero_zero)

        # RUT 0-0 with eight extra leading zero
        rut_value = f'00000000{self.valid_rut_zero_zero}'
        clean_rut = rut.Rut.clean_str(rut_value)
        self.assertEqual(clean_rut, self.valid_rut_zero_zero)

    def test_calc_dv_ok(self) -> None:
        dv = rut.Rut.calc_dv(self.valid_rut_digits)
        self.assertEqual(dv, self.valid_rut_dv)

    def test_calc_dv_string_uppercase(self) -> None:
        digits = 'A'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut.calc_dv(digits)

        self.assertListEqual(
            list(context_manager.exception.args),
            ["Must be a sequence of digits."],
        )

    def test_calc_dv_string_lowercase(self) -> None:
        digits = 'a'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut.calc_dv(digits)

        self.assertListEqual(
            list(context_manager.exception.args),
            ["Must be a sequence of digits."],
        )

    def test_random(self) -> None:
        rut_instance = rut.Rut.random()
        self.assertIsInstance(rut_instance, rut.Rut)
        dv = rut.Rut.calc_dv(rut_instance.digits)
        self.assertEqual(rut_instance.dv, dv)
