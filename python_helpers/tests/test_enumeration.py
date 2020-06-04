import pytest

from python_helpers.enumeration import StringEnum


class Three(StringEnum):
    one = 1
    two = 2
    three = 3


def test_eq():
    one, two, _ = Three
    assert two == 'two'
    assert 'two' == two
    assert two == two
    assert two != one
    assert two != 'one'
    assert 'one' != two


def test_construction():
    assert Three.three is Three.from_str('three')


def test_disallowed_construction():
    with pytest.raises(ValueError):
        Three.from_str('four')


def test_allowed_values():
    return Three.allowed_values == 'one, two, three'
