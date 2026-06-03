from __future__ import annotations

from datetime import date, datetime, time, timezone

from dateutil import parser as date_parser


def parse_cli_date(value: str | None, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    parsed = date_parser.parse(value)
    if isinstance(parsed, datetime):
        if parsed.time() == time.min and end_of_day:
            parsed = datetime.combine(parsed.date(), time.max)
        return parsed
    if isinstance(parsed, date):
        return datetime.combine(parsed, time.max if end_of_day else time.min)
    return None


def parse_article_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = date_parser.parse(value, fuzzy=True)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def in_date_range(
    published_at: datetime | None,
    start_date: datetime | None,
    end_date: datetime | None,
    keep_undated: bool,
) -> bool:
    if published_at is None:
        return keep_undated
    if start_date and published_at < start_date:
        return False
    if end_date and published_at > end_date:
        return False
    return True
