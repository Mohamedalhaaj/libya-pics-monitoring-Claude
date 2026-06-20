from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from datetime import date, datetime

from parsers import get_parser
from utils.config import load_sources
from utils.dates import in_date_range, parse_cli_date
from utils.enrich import EnrichmentUnavailable, enrich_report
from utils.exports import (
    build_fallback_report,
    ensure_output_dir,
    write_articles_csv,
    write_verification_csv,
    write_word_report,
)
from utils.fetcher import BrowserFetcher
from utils.logger import setup_logging
from utils.models import Article, SourceVerification, StructuredReport

logger = logging.getLogger(__name__)

DEFAULT_KEYWORDS = [
    "Libya",
    "Libyan",
    "Tripoli",
    "Benghazi",
    "Misrata",
    "Derna",
    "UNSMIL",
    "ليبيا",
    "الليبي",
    "طرابلس",
    "بنغازي",
    "مصراتة",
    "درنة",
    "البعثة الأممية",
]


async def scrape_source(
    source: dict,
    fetcher: BrowserFetcher,
    keywords: list[str],
    start_date,
    end_date,
    keep_undated: bool,
) -> tuple[list[Article], SourceVerification]:
    source_id = source["id"]
    logger.info("Collecting source=%s url=%s", source_id, source["url"])
    try:
        # Only wait on an explicit, specific selector. Passing the generic
        # article selector (which matches dozens of `li` elements) made
        # Playwright log floods and could crash the driver, so rely on the
        # fetcher's networkidle settle for JS-rendered lists instead.
        result = await fetcher.fetch(
            source["url"],
            wait_for_selector=source.get("wait_for_selector"),
        )
        parser_cls = get_parser(source["parser"])
        parser = parser_cls(source, keywords)
        articles = [
            article
            for article in parser.parse(result.html)
            if in_date_range(article.published_at, start_date, end_date, keep_undated)
        ]
        return articles, SourceVerification(
            source_id=source_id,
            source_name=source["name"],
            url=result.final_url,
            status="ok",
            articles_found=len(articles),
        )
    except Exception as exc:
        logger.exception("Source failed: %s", source_id)
        return [], SourceVerification(
            source_id=source_id,
            source_name=source["name"],
            url=source["url"],
            status="failed",
            error=str(exc),
        )


async def run(args: argparse.Namespace) -> None:
    setup_logging(args.log_file, args.verbose)
    output_dir = ensure_output_dir(args.output_dir)
    start_date = parse_cli_date(args.start_date)
    end_date = parse_cli_date(args.end_date, end_of_day=True)
    sources = load_sources(args.sources)
    keywords = DEFAULT_KEYWORDS + args.keyword

    logger.info("Loaded %s enabled sources", len(sources))
    all_articles: list[Article] = []
    verifications: list[SourceVerification] = []

    async with BrowserFetcher(
        timeout_ms=args.timeout * 1000,
        retries=args.retries,
        retry_delay_seconds=args.retry_delay,
        headless=not args.show_browser,
        cdp_url=args.cdp_url,
    ) as fetcher:
        for source in sources:
            articles, verification = await scrape_source(
                source=source,
                fetcher=fetcher,
                keywords=keywords,
                start_date=start_date,
                end_date=end_date,
                keep_undated=args.keep_undated,
            )
            all_articles.extend(articles)
            verifications.append(verification)

    all_articles.sort(key=lambda article: article.published_at or datetime.min, reverse=True)

    report_date = format_report_date(args.report_date, end_date)
    report = build_report(all_articles, report_date, enrich=not args.no_enrich, model=args.model)

    articles_csv = output_dir / "libya_media_headlines.csv"
    verification_csv = output_dir / "source_verification_table.csv"
    report_docx = output_dir / "unsmil_pics_daily_media_report.docx"

    write_articles_csv(all_articles, articles_csv)
    write_verification_csv(verifications, verification_csv)
    write_word_report(report, verifications, report_docx)

    logger.info("Wrote %s articles to %s", len(all_articles), articles_csv)
    logger.info("Wrote verification table to %s", verification_csv)
    logger.info("Wrote Word report (%s headlines) to %s", report.total_headlines(), report_docx)


def build_report(
    articles: list[Article],
    report_date: str,
    enrich: bool,
    model: str,
) -> StructuredReport:
    """Produce the editorial report, preferring Claude enrichment.

    Falls back to a mechanical source-grouped layout when enrichment is
    disabled or unavailable (no API key, missing SDK, or a failed call).
    """
    if enrich:
        try:
            return enrich_report(articles, report_date, model=model)
        except EnrichmentUnavailable as exc:
            logger.warning("Enrichment unavailable, using mechanical fallback: %s", exc)
    else:
        logger.info("Enrichment disabled; using mechanical fallback layout")
    return build_fallback_report(articles, report_date)


def format_report_date(explicit: str | None, end_date: datetime | None) -> str:
    """Title-friendly coverage date, e.g. '3 June'."""
    if explicit:
        return explicit
    day: date = end_date.date() if end_date else date.today()
    return f"{day.day} {day.strftime('%B')}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect Libya-related headlines for UNSMIL/PICS media monitoring.")
    parser.add_argument("--sources", default="sources.json", help="Path to source configuration JSON.")
    parser.add_argument("--output-dir", default="output", help="Directory for CSV and Word report outputs.")
    parser.add_argument("--start-date", help="Inclusive start date, for example 2026-06-01.")
    parser.add_argument("--end-date", help="Inclusive end date, for example 2026-06-03.")
    parser.add_argument(
        "--report-date",
        help="Title date for the report, e.g. '3 June'. Defaults to the end date (or today).",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-8",
        help="Claude model used for editorial enrichment.",
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Skip Claude enrichment and use the mechanical source-grouped layout.",
    )
    parser.add_argument("--keyword", action="append", default=[], help="Additional Arabic or English keyword filter.")
    parser.add_argument("--keep-undated", action="store_true", help="Keep articles where the source does not expose a date.")
    parser.add_argument("--timeout", type=int, default=30, help="Browser timeout per page in seconds.")
    parser.add_argument("--retries", type=int, default=3, help="Fetch retry attempts per source.")
    parser.add_argument("--retry-delay", type=float, default=2.0, help="Base retry delay in seconds.")
    parser.add_argument("--show-browser", action="store_true", help="Run Playwright with a visible browser.")
    parser.add_argument(
        "--cdp-url",
        help=(
            "Fetch through an already-running Chrome via DevTools, e.g. "
            "http://localhost:9222. Uses the real browser's identity/cookies to "
            "reach bot-protected, JS-rendered sources. Launch Chrome with "
            "--remote-debugging-port=9222 first."
        ),
    )
    parser.add_argument("--log-file", default="logs/scraper.log", help="Path to scraper log file.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
