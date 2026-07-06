import pytest
from app.exceptions import ValidationError
from app.operations import (
    Add,
    Subtract,
    Multiply,
    Divide,
    Power,
    Root,
    Modulus,
    IntDivide,
    Percent,
    AbsDiff,
    Operation,
)


class TestOperationBase:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            Operation()


class TestAdd:
    def test_positive_numbers(self):
        assert Add().execute(2, 3) == 5

    def test_negative_numbers(self):
        assert Add().execute(-2, -3) == -5

    def test_mixed_sign(self):
        assert Add().execute(-2, 5) == 3

    def test_floats(self):
        assert Add().execute(1.5, 2.5) == 4.0


class TestSubtract:
    def test_positive_result(self):
        assert Subtract().execute(5, 3) == 2

    def test_negative_result(self):
        assert Subtract().execute(3, 5) == -2

    def test_floats(self):
        assert Subtract().execute(5.5, 2.0) == 3.5


class TestMultiply:
    def test_positive_numbers(self):
        assert Multiply().execute(4, 3) == 12

    def test_with_zero(self):
        assert Multiply().execute(4, 0) == 0

    def test_negative_numbers(self):
        assert Multiply().execute(-2, 3) == -6

    def test_floats(self):
        assert Multiply().execute(2.5, 4) == 10.0


class TestDivide:
    def test_positive_numbers(self):
        assert Divide().execute(10, 2) == 5

    def test_negative_numbers(self):
        assert Divide().execute(-10, 2) == -5

    def test_floats(self):
        assert Divide().execute(7.5, 2.5) == 3.0

    def test_division_by_zero_raises(self):
        with pytest.raises(ValidationError, match="Division by zero"):
            Divide().execute(5, 0)

class TestPower:
    @pytest.mark.parametrize("a, b, expected", [
        (2, 3, 8),
        (5, 0, 1),
        (2, -2, 0.25),
        (-2, 3, -8),
        (9, 0.5, 3.0),
    ])
    def test_power(self, a, b, expected):
        assert Power().execute(a, b) == expected

    def test_zero_to_negative_power_raises(self):
        with pytest.raises(ValidationError, match="negative power"):
            Power().execute(0, -1)

    def test_negative_base_fractional_exponent_raises(self):
        with pytest.raises(ValidationError, match="fractional exponent"):
            Power().execute(-4, 0.5)


class TestRoot:
    @pytest.mark.parametrize("a, b, expected", [
        (9, 2, 3.0),
        (27, 3, 3.0),
        (16, 4, 2.0),
        (-27, 3, -3.0),
    ])
    def test_root(self, a, b, expected):
        assert Root().execute(a, b) == pytest.approx(expected)

    def test_zero_degree_raises(self):
        with pytest.raises(ValidationError, match="degree cannot be zero"):
            Root().execute(9, 0)

    def test_even_root_of_negative_raises(self):
        with pytest.raises(ValidationError, match="negative number"):
            Root().execute(-9, 2)


class TestModulus:
    @pytest.mark.parametrize("a, b, expected", [
        (10, 3, 1),
        (10, 5, 0),
        (7.5, 2, 1.5),
    ])
    def test_modulus(self, a, b, expected):
        assert Modulus().execute(a, b) == expected

    def test_modulus_by_zero_raises(self):
        with pytest.raises(ValidationError, match="Modulus by zero"):
            Modulus().execute(10, 0)


class TestIntDivide:
    @pytest.mark.parametrize("a, b, expected", [
        (10, 3, 3),
        (9, 3, 3),
        (7.5, 2, 3.0),
        (-10, 3, -4),
    ])
    def test_int_divide(self, a, b, expected):
        assert IntDivide().execute(a, b) == expected

    def test_int_divide_by_zero_raises(self):
        with pytest.raises(ValidationError, match="Integer division by zero"):
            IntDivide().execute(10, 0)


class TestPercent:
    @pytest.mark.parametrize("a, b, expected", [
        (50, 200, 25.0),
        (1, 4, 25.0),
        (3, 2, 150.0),
    ])
    def test_percent(self, a, b, expected):
        assert Percent().execute(a, b) == expected

    def test_percent_of_zero_raises(self):
        with pytest.raises(ValidationError, match="percentage of zero"):
            Percent().execute(50, 0)


class TestAbsDiff:
    @pytest.mark.parametrize("a, b, expected", [
        (10, 3, 7),
        (3, 10, 7),
        (-5, 5, 10),
        (2.5, 2.5, 0),
    ])
    def test_abs_diff(self, a, b, expected):
        assert AbsDiff().execute(a, b) == expected