import pytest

from app.database.models import Job, SearchProfile
from app.matching.engine import score_job


@pytest.mark.parametrize("period,amount,expected", [
    ("annual", 36000, 100),
    ("per-year", 24000, 66),
    ("yearly", 18000, 50),
    ("monthly", 3000, 100),
    ("per-month", 1500, 50),
    (None, 3000, 58),
    ("unspecified", 6000, 58),
    ("hourly", 50, 58),
    ("per-week", 1000, 58),
])
def test_salary_minimum_compares_only_supported_monthly_equivalents(period, amount, expected):
    job = Job(
        fingerprint="salary-period", title="DevOps Engineer", company="Example", description="Linux support",
        salary_from=amount, salary_currency="USD", salary_period=period,
    )
    search = SearchProfile(settings={"minimum_salary": {"USD": 3000}})

    result = score_job(job, search, [], [])

    assert result.salary_score == expected
    assert job.salary_from == amount
    assert job.salary_period == period
