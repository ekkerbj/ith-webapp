from datetime import date

from ith_webapp.services.date_filtering import month_compare


def test_month_compare_returns_true_only_for_the_same_month_and_year():
    reference = date(2026, 4, 20)

    assert month_compare(date(2026, 4, 1), reference=reference)
    assert not month_compare(date(2026, 3, 31), reference=reference)
