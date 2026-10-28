import pytest

from src.calculator import factorial


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 1),
        (1, 1),
        (5, 120),
    ],
)
def test_factorial_valid_inputs(n, expected):
    assert factorial(n) == expected


@pytest.mark.parametrize("n", [-1, -2, -10])
def test_factorial_negative_input(n):
    with pytest.raises(ValueError, match="negative number"):
        factorial(n)


@pytest.mark.parametrize("n", [2.5, "5", True])
def test_factorial_invalid_type(n):
    with pytest.raises(TypeError, match="non-negative integer"):
        factorial(n)
