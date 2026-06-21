from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone

from dateutil import parser as date_parser

# Matches dates embedded in article URLs, e.g. /2026/06/20/ or /2026/6/18.
_URL_DATE_RE = re.compile(r"/(20\d{2})/(\d{1,2})(?:/(\d{1,2}))?(?:/|$|[?#])")

# Arabic-Indic and extended (Persian) digits → ASCII, so Arabic date strings
# parse with the standard tooling.
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

# Arabic month names → English, covering both the Levantine-Gregorian and the
# transliterated-Gregorian naming systems Libyan/Arab outlets use. dateutil
# understands the English names, so we translate before parsing.
_AR_MONTHS = {
    "يناير": "January", "كانون الثاني": "January",
    "فبراير": "February", "شباط": "February",
    "مارس": "March", "آذار": "March", "اذار": "March",
    "أبريل": "April", "إبريل": "April", "ابريل": "April", "نيسان": "April",
    "مايو": "May", "أيار": "May", "ايار": "May",
    "يونيو": "June", "يونيه": "June", "حزيران": "June",
    "يوليو": "July", "يوليه": "July", "تموز": "July",
    "أغسطس": "August", "اغسطس": "August", "آب": "August",
    "سبتمبر": "September", "أيلول": "September", "ايلول": "September",
    "أكتوبر": "October", "اكتوبر": "October", "تشرين الأول": "October", "تشرين الاول": "October",
    "نوفمبر": "November", "تشرين الثاني": "November",
    "ديسمبر": "December", "كانون الأول": "December", "كانون الاول": "December",
}

_REL_TODAY = ("اليوم", "الآن", "الان", "منذ قليل", "قبل قليل", "للتو")
_REL_YESTERDAY = ("أمس", "امس", "الأمس", "الامس", "البارحة", "أول أمس")
# "منذ ساعتين" / "قبل يومين": Arabic dual forms (no number). "يومين" = two
# days ago; hour/minute duals collapse to today at day granularity.
_REL_DUAL = {"يومين": 2, "ساعتين": 0, "دقيقتين": 0}
# "منذ N يوم/أيام" or "قبل N ساعة" etc.
_REL_AGO_RE = re.compile(
    r"(?:منذ|قبل)\s+(\d+)\s*(دقيقة|دقائق|ساعة|ساعات|يوم|أيام|أسبوع|أسابيع|شهر|أشهر)"
)


def _parse_relative_arabic(text: str, now: datetime) -> datetime | None:
    """Resolve Arabic relative phrases ('اليوم', 'أمس', 'منذ يومين')."""
    today = datetime.combine(now.date(), time.min)
    for token in _REL_YESTERDAY:
        if token in text:
            return today - timedelta(days=1)
    for token in _REL_TODAY:
        if token in text:
            return today
    for token, days in _REL_DUAL.items():
        if token in text:
            return today - timedelta(days=days)
    match = _REL_AGO_RE.search(text)
    if match:
        amount, unit = int(match.group(1)), match.group(2)
        if unit in ("دقيقة", "دقائق", "ساعة", "ساعات"):
            return today
        if unit in ("يوم", "أيام"):
            return today - timedelta(days=amount)
        if unit in ("أسبوع", "أسابيع"):
            return today - timedelta(days=7 * amount)
        if unit in ("شهر", "أشهر"):
            return today - timedelta(days=30 * amount)
    return None


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


def parse_article_date(value: str | None, now: datetime | None = None) -> datetime | None:
    if not value:
        return None
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    text = value.translate(_AR_DIGITS).strip()

    # Arabic relative phrases ("اليوم", "أمس", "منذ يومين") carry no parseable
    # absolute date, so resolve them against the run time first.
    relative = _parse_relative_arabic(text, now)
    if relative is not None:
        return relative

    # Translate Arabic month names so dateutil can read the absolute date.
    for arabic, english in _AR_MONTHS.items():
        if arabic in text:
            text = text.replace(arabic, english)

    # Fuzzy parsing happily turns arbitrary text (e.g. a category label that
    # landed in the date selector) into "today". Require at least one digit so
    # we only attempt to parse strings that plausibly contain a date.
    if not any(char.isdigit() for char in text):
        return None
    try:
        parsed = date_parser.parse(text, fuzzy=True)
    except (TypeError, ValueError, OverflowError):
        return None
    # Normalise to naive UTC so article dates compare consistently against the
    # naive CLI date bounds (see parse_cli_date).
    if parsed.tzinfo:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def parse_date_from_url(url: str | None) -> datetime | None:
    """Best-effort date from a date-stamped article URL (day defaults to 1)."""
    if not url:
        return None
    match = _URL_DATE_RE.search(url)
    if not match:
        return None
    year, month, day = match.group(1), match.group(2), match.group(3)
    try:
        return datetime(int(year), int(month), int(day) if day else 1)
    except ValueError:
        return None


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
