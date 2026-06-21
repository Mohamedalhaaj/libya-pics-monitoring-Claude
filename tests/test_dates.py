"""Tests for Arabic/relative date parsing and the report-title date range.

Runnable directly (`python tests/test_dates.py`) or under pytest.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.dates import parse_article_date, parse_cli_date  # noqa: E402
from scraper import format_report_date  # noqa: E402

NOW = datetime(2026, 6, 21, 12, 0)


def test_arabic_month_names():
    # Levantine-Gregorian and transliterated-Gregorian both resolve.
    d = parse_article_date("20 يونيو 2026", now=NOW)
    assert (d.year, d.month, d.day) == (2026, 6, 20)
    d = parse_article_date("18 حزيران 2026", now=NOW)
    assert (d.year, d.month, d.day) == (2026, 6, 18)
    # Arabic-Indic digits.
    d = parse_article_date("١٩ يوليو ٢٠٢٦", now=NOW)
    assert (d.year, d.month, d.day) == (2026, 7, 19)


def test_arabic_relative_dates():
    assert parse_article_date("اليوم", now=NOW).date() == NOW.date()
    assert parse_article_date("أمس", now=NOW).date() == datetime(2026, 6, 20).date()
    assert parse_article_date("منذ يومين", now=NOW).date() == datetime(2026, 6, 19).date()
    # Hours/minutes ago collapse to today (day granularity).
    assert parse_article_date("منذ 3 ساعات", now=NOW).date() == NOW.date()
    assert parse_article_date("قبل 5 أيام", now=NOW).date() == datetime(2026, 6, 16).date()


def test_non_date_text_rejected():
    # A category label that landed in a date field must not become "today".
    assert parse_article_date("سياسة", now=NOW) is None
    assert parse_article_date("Politics", now=NOW) is None


def test_report_date_range_title():
    start = parse_cli_date("2026-06-18")
    end = parse_cli_date("2026-06-21", end_of_day=True)
    assert format_report_date(None, start, end) == "18-21 June"
    # Single day.
    assert format_report_date(None, end, end) == "21 June"
    # Cross-month.
    s2 = parse_cli_date("2026-06-29")
    e2 = parse_cli_date("2026-07-02", end_of_day=True)
    assert format_report_date(None, s2, e2) == "29 June - 2 July"
    # Explicit override wins.
    assert format_report_date("3 June", start, end) == "3 June"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\nAll {len(tests)} date tests passed.")
