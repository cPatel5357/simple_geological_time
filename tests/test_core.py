import math
import unittest

from simple_geological_time import to_scientific, from_scientific, GeologicalDateError


class TestToScientific(unittest.TestCase):
    def test_mega_annum(self):
        self.assertEqual(to_scientific("65 Ma"), 6.5e7)

    def test_giga_annum(self):
        self.assertEqual(to_scientific("1.5 Ga"), 1.5e9)

    def test_kilo_annum(self):
        self.assertEqual(to_scientific("3 ka"), 3.0e3)

    def test_plain_years(self):
        self.assertEqual(to_scientific("1000 a"), 1.0e3)

    def test_bare_number(self):
        self.assertEqual(to_scientific("1000"), 1.0e3)

    def test_scientific_notation_input(self):
        self.assertEqual(to_scientific("1.234e6 a"), 1.234e6)

    def test_decimal_with_unit(self):
        self.assertEqual(to_scientific("65.5 Ma"), 6.55e7)

    def test_extra_whitespace(self):
        self.assertEqual(to_scientific("  65   Ma  "), 6.5e7)

    def test_zero(self):
        self.assertEqual(to_scientific("0 a"), 0.0)

    def test_negative_age_rejected(self):
        with self.assertRaises(GeologicalDateError):
            to_scientific("-65 Ma")

    def test_bad_unit_rejected(self):
        with self.assertRaises(GeologicalDateError):
            to_scientific("65 Jy")

    def test_empty_input(self):
        with self.assertRaises(GeologicalDateError):
            to_scientific("")

    def test_no_number(self):
        with self.assertRaises(GeologicalDateError):
            to_scientific("Ma")

    def test_non_string_input(self):
        with self.assertRaises(GeologicalDateError):
            to_scientific(65)


class TestFromScientific(unittest.TestCase):
    def test_million_years(self):
        result = from_scientific(6.5e7)
        self.assertEqual(result, "65 Ma")

    def test_billion_years(self):
        result = from_scientific(1.5e9)
        self.assertEqual(result, "1.5 Ga")

    def test_thousand_years(self):
        result = from_scientific(3.0e3)
        self.assertEqual(result, "3 ka")

    def test_plain_years_small(self):
        result = from_scientific(1000.0)
        self.assertEqual(result, "1 ka")

    def test_small_number_years(self):
        result = from_scientific(500.0)
        self.assertEqual(result, "500 a")

    def test_zero(self):
        self.assertEqual(from_scientific(0.0), "0 a")

    def test_integer_input(self):
        self.assertEqual(from_scientific(65000000), "65 Ma")

    def test_rounding_significant_digits(self):
        # 65432109 -> with 2 sig digits -> 65 Ma
        result = from_scientific(65432109, significant_digits=2)
        self.assertEqual(result, "65 Ma")

    def test_more_significant_digits(self):
        result = from_scientific(65432109, significant_digits=3)
        self.assertEqual(result, "65.4 Ma")

    def test_negative_rejected(self):
        with self.assertRaises(GeologicalDateError):
            from_scientific(-5.0e6)

    def test_nan_rejected(self):
        with self.assertRaises(GeologicalDateError):
            from_scientific(float("nan"))

    def test_inf_rejected(self):
        with self.assertRaises(GeologicalDateError):
            from_scientific(float("inf"))

    def test_non_number_input(self):
        with self.assertRaises(GeologicalDateError):
            from_scientific("65 Ma")

    def test_bad_significant_digits(self):
        with self.assertRaises(GeologicalDateError):
            from_scientific(1e6, significant_digits=0)

    def test_float_comparison_not_exact(self):
        # We intentionally avoid == on floats in tests. Instead, parse the result
        # back and check relative error is within tolerance.
        original = 1.234567e7
        rendered = from_scientific(original, significant_digits=4)
        parsed_back = to_scientific(rendered)
        # Relative error should be small, not zero.
        relative_error = abs(parsed_back - original) / original
        self.assertLess(relative_error, 1e-3)


if __name__ == "__main__":
    unittest.main()
