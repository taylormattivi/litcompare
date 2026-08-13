import pytest

from litcompare.cli import _positive_int


def test_positive_int_accepts_positive_values():
    assert _positive_int("15") == 15


def test_positive_int_rejects_zero():
    with pytest.raises(Exception):
        _positive_int("0")


def test_positive_int_rejects_negative():
    with pytest.raises(Exception):
        _positive_int("-3")


def test_positive_int_rejects_non_numeric():
    with pytest.raises(Exception):
        _positive_int("abc")
