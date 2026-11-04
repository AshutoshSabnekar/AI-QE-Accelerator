import pytest
from src.calculator import divide, modulus, multiply, power, square_root, subtract


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (5, 3, 2),
        (3, 5, -2),
        (-5, -3, -2),
        (5, 0, 5),
    ],
)
@pytest.mark.calculator
@pytest.mark.subtraction
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 6),
        (-2, 3, -6),
        (-2, -3, 6),
        (5, 0, 0),
    ],
)
@pytest.mark.calculator
@pytest.mark.multiplication
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 2, 5.0),
        (5, 2, 2.5),
        (-10, 2, -5.0),
        (0, 5, 0.0),
        (20, -4, -5.0),
    ],
)
@pytest.mark.calculator
@pytest.mark.division
def test_divide_valid_inputs(a, b, expected):
    assert divide(a, b) == expected


@pytest.mark.calculator
@pytest.mark.division
def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 3, 1),
        (8, 4, 0),
        (-10, 3, 2),
    ],
)
@pytest.mark.calculator
@pytest.mark.modulus
def test_modulus(a, b, expected):
    assert modulus(a, b) == expected


@pytest.mark.calculator
@pytest.mark.modulus
def test_modulus_by_zero():
    with pytest.raises(ValueError, match="Cannot take modulus by zero"):
        modulus(10, 0)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 8),
        (5, 0, 1),
        (2, -2, 0.25),
    ],
)
@pytest.mark.calculator
@pytest.mark.power
def test_power(a, b, expected):
    assert power(a, b) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0),
        (1, 1.0),
        (4, 2.0),
        (9, 3.0),
        (2, 2**0.5),
    ],
)
@pytest.mark.calculator
@pytest.mark.square_root
def test_square_root_valid_inputs(value, expected):
    assert square_root(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", [-1, -9])
@pytest.mark.calculator
@pytest.mark.square_root
def test_square_root_negative_input(value):
    with pytest.raises(ValueError, match="negative number"):
        square_root(value)


@pytest.mark.parametrize("value", ["4", "Four", None, True])
@pytest.mark.calculator
@pytest.mark.square_root
def test_square_root_invalid_input_type(value):
    with pytest.raises(TypeError):
        square_root(value)
