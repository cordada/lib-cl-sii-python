import unittest

from cl_sii import rut  # noqa: F401
from cl_sii.rut import constants  # noqa: F401


class RutTest(unittest.TestCase):

    valid_rut_canonical: str
    valid_rut_dv: str
    valid_rut_digits: str
    valid_rut_digits_with_dots: str
    valid_rut_verbose: str

    invalid_rut_canonical: str
    invalid_rut_dv: str

    valid_rut_instance: rut.Rut
    invalid_rut_instance: rut.Rut

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_rut_canonical = '6824160-K'
        cls.valid_rut_dv = 'K'
        cls.valid_rut_digits = '6824160'
        cls.valid_rut_digits_with_dots = '6.824.160'
        cls.valid_rut_verbose = '6.824.160-K'

        cls.invalid_rut_canonical = '6824160-0'
        cls.invalid_rut_dv = '0'

        cls.valid_rut_instance = rut.Rut(cls.valid_rut_canonical)
        cls.invalid_rut_instance = rut.Rut(cls.invalid_rut_canonical)

    ############################################################################
    # instance
    ############################################################################

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

    def test__eq__true(self) -> None:
        rut_instance = rut.Rut(self.valid_rut_canonical)
        self.assertTrue(self.valid_rut_instance.__eq__(rut_instance))

    def test__eq__false(self) -> None:
        self.assertFalse(self.valid_rut_instance.__eq__(self.invalid_rut_instance))

    def test__eq__not_rut_instance(self) -> None:
        self.assertFalse(self.valid_rut_instance.__eq__(self.valid_rut_canonical))

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

    def test_calc_dv_ok(self) -> None:
        dv = rut.Rut.calc_dv(self.valid_rut_digits)
        self.assertEqual(dv, self.valid_rut_dv)

    def test_calc_dv_string_uppercase(self) -> None:
        digits = 'A'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut.calc_dv(digits)

        self.assertListEqual(
            list(context_manager.exception.args),
            ["Must be a sequence of digits."]
        )

    def test_calc_dv_string_lowercase(self) -> None:
        digits = 'a'
        with self.assertRaises(ValueError) as context_manager:
            rut.Rut.calc_dv(digits)

        self.assertListEqual(
            list(context_manager.exception.args),
            ["Must be a sequence of digits."]
        )

    def test_random(self) -> None:
        rut_instance = rut.Rut.random()
        self.assertIsInstance(rut_instance, rut.Rut)
        dv = rut.Rut.calc_dv(rut_instance.digits)
        self.assertEqual(rut_instance.dv, dv)
