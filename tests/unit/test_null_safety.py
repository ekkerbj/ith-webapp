from ith_webapp.utils import Nnz, Zero


def test_nnz_coerces_null_and_non_numeric_values_to_zero():
    assert Nnz(None) == 0
    assert Nnz("abc") == 0
    assert Nnz("7.5") == 7.5


def test_zero_returns_zero_only_for_zeroing_keywords():
    assert Zero(12, "zero") == 0
    assert Zero(12, "keep") == 12
