import pytest

from app.sources.adapters.telegram_ingest import parse_telegram_job


def parse(text):
    return parse_telegram_job("Support Engineer\n" + text, source_ref="fixture")


def test_support_absence_and_denials_are_distinct():
    unknown = parse("Linux support")
    assert unknown.relocation is None and unknown.visa_sponsorship is None
    denied = parse("No visa sponsorship. No relocation assistance.")
    assert denied.visa_sponsorship is False and denied.relocation is False
    offered = parse("We provide visa sponsorship and relocation assistance.")
    assert offered.visa_sponsorship is True and offered.relocation is True


@pytest.mark.parametrize("text", ["No remote work", "Remote is not available", "Not remote", "Experience with remote servers"])
def test_negation_and_technical_mentions_do_not_establish_remote_mode(text):
    assert parse(text).work_mode is None


@pytest.mark.parametrize("text", ["Remote worldwide", "Fully remote", "Work remotely", "Удаленная работа"])
def test_explicit_work_mode_remains_remote(text):
    assert parse(text).work_mode == "remote"


@pytest.mark.parametrize("text", ["$20.50 hourly", "USD 20.50 per hour", "$3000-4500", "USD 3000", "CAD 3,000 monthly"])
def test_ambiguous_or_decimal_salary_is_source_text_without_numeric_inference(text):
    job = parse(text)
    assert job.salary_from is None and job.salary_to is None
    assert job.salary_currency is None and job.salary_period is None
    assert job.raw["source_salary_text"] == text


def test_explicit_whole_monthly_salary_keeps_currency_period_and_range():
    job = parse("USD 3000-4500 per month")
    assert (job.salary_from, job.salary_to, job.salary_currency, job.salary_period) == (3000, 4500, "USD", "monthly")
