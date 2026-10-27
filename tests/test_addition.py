import pytest

from src.calculator import add


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),
        (-2, -3, -5),
        (2, -3, -1),
        (-2, 0, -2),
        (2, 0, 2),
        (0, 0, 0),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
