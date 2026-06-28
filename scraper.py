from __future__ import annotations

import argparse
import asyncio
import logging
import urllib.parse
from pathlib import Path

import html as _html
import re as _re
from datetime import date, datetime, timedelta

from parsers import get_parser
from parsers.feed import FeedListParser
from parsers.generic import deduplicate_articles
from utils.config import load_sources
from utils.dates import in_date_range, parse_cli_date
from utils.enrich import EnrichmentUnavailable, enrich_report
from utils.feeds import discover_feed_url, fetch_feed_text, google_news_url
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

# Workhorse Libyan outlets that publish daily — if one returns nothing it is
# almost certainly a scrape failure (bot-block / dead URL), not a quiet news
# day. The scrape-health gate flags these. A source may also opt in per-config
# with ``"critical": true``.
CRITICAL_SOURCE_IDS = frozenset({
    "akhbar_libya_24", "al_wasat", "libya_observer", "lana", "lana_6", "lana_21",
    "ean_libya", "al_shahed", "al_marsad", "al_menassa", "libya_24", "libya_review",
    "al_saaa_24", "libya_al_ahrar", "libya_herald", "address_libya", "rna_reportage",
    "libya_update",
})


def _registrable_domain(url: str) -> str:
    """Bare host for a source URL (drops scheme, ``www.`` and any path)."""
    host = urllib.parse.urlsplit(url if "://" in url else f"https://{url}").netloc.lower()
    return host[4:] if host.startswith("www.") else host


async def _site_query_fallback(
    source: dict, keywords: list[str]
) -> tuple[list[Article], str]:
    """Recover a source that the direct scrape couldn't reach.

    Many outlets (e.g. Akhbar Libya 24) return 403/empty to the scraper while
    remaining fully indexed by Google News. Query ``site:<domain>`` so a
    bot-blocked but indexed source is backfilled instead of silently dropped.
    """
    domain = _registrable_domain(source.get("url", ""))
    if not domain:
        return [], ""
    language = source.get("language", "en")
    term = "ليبيا" if language == "ar" else "Libya"
    url = google_news_url(f"site:{domain} {term}", language)
    try:
        text = await fetch_feed_text(url)
    except Exception as exc:  # noqa: BLE001 - fallback is best-effort
        logger.debug("site: fallback failed for %s: %s", source["id"], exc)
        return [], url
    return deduplicate_articles(FeedListParser(source, keywords).parse(text)), url


async def _date_archive_backfill(
    source: dict, fetcher: BrowserFetcher, start_date, end_date
) -> list[Article]:
    """Crawl ``/YYYY/MM/DD/`` archives per day for WordPress date-permalink sources.

    Listing/category pages are shallow and often hide per-article dates, so the
    parser silently drops a busy day's stories (this lost ~20 Al Marsad articles
    over 25-28 June). The dated archive lists a full day's output, paginates, and
    carries the date in the URL — giving complete in-window coverage. Sources that
    don't use date permalinks (LANA, Libya Observer) yield nothing on day one and
    exit immediately, so this is safe to run for every critical source.
    """
    domain = _registrable_domain(source.get("url", ""))
    if not domain or not (start_date and end_date):
        return []
    start = start_date.date() if hasattr(start_date, "date") else start_date
    end = end_date.date() if hasattr(end_date, "date") else end_date
    seen: dict[str, str] = {}
    day = start
    while day <= end:
        ymd = f"{day.year:04d}/{day.month:02d}/{day.day:02d}"
        link_re = _re.compile(
            r'<a[^>]+href="(https?://(?:www\.)?%s/%s/[^"/?#]+/?)"[^>]*>(.*?)</a>'
            % (_re.escape(domain), ymd), _re.S)
        for page in range(1, 6):
            url = f"https://{domain}/{ymd}/" if page == 1 else f"https://{domain}/{ymd}/page/{page}/"
            try:
                res = await fetcher.fetch(url)
            except Exception:
                break
            new = 0
            for m in link_re.finditer(res.html):
                u = m.group(1)
                title = _html.unescape(_re.sub(r"<[^>]+>", "", m.group(2))).strip()
                if len(title) >= 15 and u not in seen:
                    seen[u] = title
                    new += 1
            if new == 0:
                break
        # Day one produced nothing for this whole domain → not a date-permalink
        # site; don't waste fetches on the remaining days.
        if day == start and not seen:
            return []
        day += timedelta(days=1)
    articles: list[Article] = []
    for u, title in seen.items():
        m = _re.search(r"/(\d{4})/(\d{2})/(\d{2})/", u)
        published = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
        articles.append(Article(
            source_id=source["id"], source_name=source["name"],
            language=source.get("language", "ar"), country_focus=source.get("country_focus", "Libya"),
            title=title, url=u, published_at=published, matched_keywords=[]))
    return articles


async def _collect_articles(
    source: dict,
    fetcher: BrowserFetcher,
    keywords: list[str],
) -> tuple[list[Article], str, str]:
    """Collect raw articles for a source, preferring a clean RSS/Atom feed.

    Returns (articles, final_url, method) where method is "feed", "feed(auto)"
    or "html". Feeds are tried first (configured ``feed`` URL); on any failure
    or empty result we fall back to the boilerplate-stripped HTML scrape, and
    opportunistically try a feed advertised by the page itself.
    """
    # Google News fan-out: many queries (topics + outlet `site:` filters), each
    # surfacing a different slice of publishers, fetched concurrently.
    queries = source.get("google_news_queries")
    if queries:
        urls = [google_news_url(query, source.get("language", "en")) for query in queries]
        results = await asyncio.gather(*(fetch_feed_text(url) for url in urls), return_exceptions=True)
        collected: list[Article] = []
        for query, result in zip(queries, results):
            if isinstance(result, Exception):
                logger.debug("gnews query failed (%s): %s", query, result)
                continue
            collected.extend(FeedListParser(source, keywords).parse(result))
        collected = deduplicate_articles(collected)
        if collected:
            return collected, urls[0], f"gnews x{len(queries)}"
        logger.warning("Google News fan-out for %s returned nothing", source["id"])

    feed_url = source.get("feed")
    if feed_url:
        try:
            text = await fetch_feed_text(feed_url)
            articles = FeedListParser(source, keywords).parse(text)
            if articles:
                return articles, feed_url, "feed"
            logger.warning("Feed %s returned no items; falling back to HTML", feed_url)
        except Exception as exc:
            logger.warning("Feed fetch failed for %s (%s); falling back to HTML", source["id"], exc)

    # Only wait on an explicit, specific selector. Passing the generic article
    # selector (which matches dozens of `li` elements) made Playwright log
    # floods and could crash the driver, so rely on the fetcher's networkidle
    # settle for JS-rendered lists instead.
    result = await fetcher.fetch(source["url"], wait_for_selector=source.get("wait_for_selector"))

    if not feed_url and source.get("autodiscover_feed", True):
        discovered = discover_feed_url(result.html, result.final_url)
        if discovered:
            try:
                text = await fetch_feed_text(discovered)
                articles = FeedListParser(source, keywords).parse(text)
                if articles:
                    logger.info("Using autodiscovered feed for %s: %s", source["id"], discovered)
                    return articles, discovered, "feed(auto)"
            except Exception as exc:
                logger.debug("Autodiscovered feed failed for %s: %s", source["id"], exc)

    parser = get_parser(source["parser"])(source, keywords)
    html_articles = parser.parse(result.html)
    if html_articles:
        return html_articles, result.final_url, "html"

    # The page returned nothing — usually a 403/bot-block or a stale selector.
    # Don't drop the source: try to recover it from Google News by domain.
    site_articles, site_url = await _site_query_fallback(source, keywords)
    if site_articles:
        logger.info(
            "Recovered %s via site: fallback (%s articles)", source["id"], len(site_articles)
        )
        return site_articles, site_url, "gnews(site:)"
    return html_articles, result.final_url, "html"


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
        raw_articles, final_url, method = await _collect_articles(source, fetcher, keywords)
        # Critical Libyan outlets: also pull `site:<domain>` and merge, every run.
        # Their feeds/listing pages are shallow (~last 10 items), so on a busy day
        # real stories fall off even when the source scraped "ok" (e.g. LANA, Ean
        # Libya). Skip when the empty-source fallback already ran site: for us.
        if source_id in CRITICAL_SOURCE_IDS and not method.startswith("gnews(site:"):
            site_articles, _ = await _site_query_fallback(source, keywords)
            if site_articles:
                merged = deduplicate_articles(raw_articles + site_articles)
                if len(merged) > len(raw_articles):
                    logger.info(
                        "Backfilled %s via site: (%s -> %s raw)", source_id, len(raw_articles), len(merged)
                    )
                    method = f"{method}+site:"
                raw_articles = merged
        # Critical sources: also crawl per-day /YYYY/MM/DD/ archives so shallow
        # listings / hidden dates don't drop a busy day (no-op for non-date sites).
        if source_id in CRITICAL_SOURCE_IDS:
            archive = await _date_archive_backfill(source, fetcher, start_date, end_date)
            if archive:
                merged = deduplicate_articles(raw_articles + archive)
                if len(merged) > len(raw_articles):
                    logger.info(
                        "Backfilled %s via date-archive (%s -> %s raw)", source_id, len(raw_articles), len(merged)
                    )
                    method = f"{method}+archive"
                raw_articles = merged
        articles = [
            article
            for article in raw_articles
            if in_date_range(article.published_at, start_date, end_date, keep_undated)
        ]
        logger.info("source=%s method=%s collected=%s kept=%s", source_id, method, len(raw_articles), len(articles))
        # "empty" surfaces a source that fetched cleanly but yielded nothing
        # (broken selectors, a dead feed, or no in-range news) so silent
        # breakage is visible in the verification table.
        return articles, SourceVerification(
            source_id=source_id,
            source_name=source["name"],
            url=final_url,
            status="ok" if articles else "empty",
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


def report_scrape_health(
    sources: list[dict],
    verifications: list[SourceVerification],
    fail_on_critical: bool = False,
) -> None:
    """Surface sources that returned nothing so a silent scrape gap can't ship.

    A source marked ``"critical": true`` in the source config that yields no
    articles trips the gate (``docs/scraping_sop.md`` quality gate): the report
    must not be built on a scrape that lost a workhorse outlet.
    """
    by_id = {s["id"]: s for s in sources}
    problems = [v for v in verifications if v.status != "ok" or v.articles_found == 0]
    logger.info(
        "Scrape health: %s ok, %s empty/failed of %s sources",
        len(verifications) - len(problems),
        len(problems),
        len(verifications),
    )
    critical_misses = []
    for v in problems:
        is_critical = v.source_id in CRITICAL_SOURCE_IDS or bool(by_id.get(v.source_id, {}).get("critical"))
        logger.warning("  no articles: %s (%s)%s", v.source_name, v.status, " [CRITICAL]" if is_critical else "")
        if is_critical:
            critical_misses.append(v.source_name)
    if critical_misses:
        logger.error(
            "SCRAPE-HEALTH GATE: %s critical source(s) returned nothing: %s. "
            "Likely a bot-block (403) or dead URL — backfill before building the "
            "report (see docs/scraping_sop.md).",
            len(critical_misses),
            ", ".join(critical_misses),
        )
        if fail_on_critical:
            raise SystemExit(2)


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

    report_scrape_health(sources, verifications, fail_on_critical=args.fail_on_empty_critical)

    report_date = format_report_date(args.report_date, start_date, end_date)
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


def format_report_date(
    explicit: str | None,
    start_date: datetime | None,
    end_date: datetime | None,
) -> str:
    """Title-friendly coverage date or range, e.g. '21 June' or '18-21 June'.

    Mirrors the PICS report titles, which collapse a multi-day window into a
    single ``18-21 June`` style range (the previous version only used the end
    day and so mislabelled multi-day roundups).
    """
    if explicit:
        return explicit
    end: date = end_date.date() if end_date else date.today()
    start: date = start_date.date() if start_date else end
    if start == end:
        return f"{end.day} {end.strftime('%B')}"
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day}-{end.day} {end.strftime('%B')}"
    if start.year == end.year:
        return f"{start.day} {start.strftime('%B')} - {end.day} {end.strftime('%B')}"
    return (
        f"{start.day} {start.strftime('%B')} {start.year} - "
        f"{end.day} {end.strftime('%B')} {end.year}"
    )


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
    parser.add_argument(
        "--fail-on-empty-critical",
        action="store_true",
        help="Exit non-zero if a source marked \"critical\" in the config returns no articles (scrape-health gate).",
    )
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
