"""Claude-powered editorial enrichment of scraped headlines.

The scraper collects raw, mostly-Arabic headlines. The UNSMIL/PICS report
(see docs/report_methodology.md) needs those translated to English, sorted
into a fixed thematic taxonomy, and de-duplicated across outlets so the same
story becomes one bullet citing every source. That editorial judgement is the
job of this module: it sends the collected articles to the Claude API and
returns a StructuredReport ready to render.

Enrichment is optional. When the `anthropic` package or an API key is missing
(or `enrich_report` raises), the caller falls back to a mechanical
source-grouped layout — see utils/exports.build_fallback_report.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from utils import taxonomy
from utils.models import (
    Article,
    HeadlineSource,
    ReportHeadline,
    ReportSection,
    ReportSubsection,
    StructuredReport,
)

logger = logging.getLogger(__name__)

# Default model for enrichment. Opus 4.8 is the most capable model and this is a
# translation + classification + clustering task where quality matters most.
DEFAULT_MODEL = "claude-opus-4-8"

# Output token ceiling. Reports can be long, so stream the response.
MAX_TOKENS = 32000


class EnrichmentUnavailable(RuntimeError):
    """Raised when enrichment cannot run (missing SDK, key, or API failure)."""


def _build_system_prompt() -> str:
    sections = "\n".join(f"{i + 1}. {name}" for i, name in enumerate(taxonomy.SECTION_ORDER))
    subsection_lines = []
    for section, subs in taxonomy.SUGGESTED_SUBSECTIONS.items():
        subsection_lines.append(f"- {section}: " + "; ".join(subs))
    subsections = "\n".join(subsection_lines)
    return (
        "You are a media-monitoring editor producing the UNSMIL/PICS daily "
        "\"Libya News Headlines\" report from a list of collected articles.\n\n"
        "Follow these rules exactly:\n"
        "1. Include only items about or directly affecting Libya. Drop generic "
        "regional/international items with no Libya connection, and anything you "
        "cannot summarise accurately in English.\n"
        "2. Translate Arabic headlines into clear, concise English. Each bullet "
        "is one sentence stating the news fact; never start with the source "
        "name. Do not add opinions.\n"
        "3. Organise items into this exact main section order (omit a section "
        f"only if it has no items):\n{sections}\n\n"
        "4. Use concise subsections where useful. Suggested subsections (use an "
        "empty subsection name when a section needs none):\n"
        f"{subsections}\n\n"
        "5. Deduplicate non-UN news: when several sources report the same story, "
        "produce ONE headline and list every reporting source. If a source adds "
        "materially different information, it may be a separate headline.\n"
        "6. UN-related news (UNSMIL, SRSG/DSRSG, UN agencies, Security Council, "
        "international mediation, humanitarian agencies, UN partnerships) must be "
        "kept even when repeated: combine identical reports into one headline "
        "listing all sources; keep separate bullets when wording/detail differs. "
        "Never drop UN coverage as a duplicate.\n"
        "7. For each headline, attach the sources that reported it, using each "
        "source's exact name and language from the input, and the article URL.\n\n"
        "Return the report via the provided JSON schema only."
    )


def _report_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string", "enum": taxonomy.SECTION_ORDER},
                        "subsections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {"type": "string"},
                                    "headlines": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "properties": {
                                                "text": {"type": "string"},
                                                "sources": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "additionalProperties": False,
                                                        "properties": {
                                                            "name": {"type": "string"},
                                                            "language": {
                                                                "type": "string",
                                                                "enum": ["ar", "en"],
                                                            },
                                                            "url": {"type": "string"},
                                                        },
                                                        "required": ["name", "language", "url"],
                                                    },
                                                },
                                            },
                                            "required": ["text", "sources"],
                                        },
                                    },
                                },
                                "required": ["name", "headlines"],
                            },
                        },
                    },
                    "required": ["name", "subsections"],
                },
            }
        },
        "required": ["sections"],
    }


def _articles_payload(articles: list[Article]) -> str:
    rows = [
        {
            "source_name": article.source_name,
            "language": article.language,
            "title": article.title,
            "summary": article.summary,
            "url": article.url,
            "published_at": article.published_at.isoformat() if article.published_at else "",
            "scraped_section": article.section,
        }
        for article in articles
    ]
    return json.dumps(rows, ensure_ascii=False, indent=2)


def _parse_report(data: dict[str, Any], report_date: str) -> StructuredReport:
    sections: list[ReportSection] = []
    for raw_section in data.get("sections", []):
        subsections: list[ReportSubsection] = []
        for raw_sub in raw_section.get("subsections", []):
            headlines = [
                ReportHeadline(
                    text=raw_headline["text"],
                    sources=[
                        HeadlineSource(
                            name=source["name"],
                            language=source.get("language", "en"),
                            url=source.get("url", ""),
                        )
                        for source in raw_headline.get("sources", [])
                    ],
                )
                for raw_headline in raw_sub.get("headlines", [])
                if raw_headline.get("text")
            ]
            if headlines:
                subsections.append(ReportSubsection(name=raw_sub.get("name", ""), headlines=headlines))
        if subsections:
            sections.append(ReportSection(name=raw_section["name"], subsections=subsections))

    sections.sort(key=lambda section: taxonomy.section_sort_key(section.name))
    return StructuredReport(report_date=report_date, sections=sections)


def enrich_report(
    articles: list[Article],
    report_date: str,
    model: str = DEFAULT_MODEL,
) -> StructuredReport:
    """Turn scraped articles into an editorial StructuredReport via Claude.

    Raises EnrichmentUnavailable when the SDK/key is missing or the call fails,
    so the caller can fall back to the mechanical layout.
    """
    if not articles:
        return StructuredReport(report_date=report_date, sections=[])

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise EnrichmentUnavailable(
            "The 'anthropic' package is not installed; run `pip install anthropic`."
        ) from exc

    try:
        client = anthropic.Anthropic()
    except Exception as exc:  # missing/invalid credentials surface here
        raise EnrichmentUnavailable(f"Could not initialise Anthropic client: {exc}") from exc

    system_prompt = _build_system_prompt()
    user_content = (
        f"Coverage date: {report_date}.\n"
        "Here are the collected articles as JSON. Produce the report.\n\n"
        f"{_articles_payload(articles)}"
    )

    logger.info("Enriching %s articles with %s", len(articles), model)
    try:
        # Stream because reports can be long enough to risk a non-streaming
        # HTTP timeout at this max_tokens.
        with client.messages.stream(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            output_config={"format": {"type": "json_schema", "schema": _report_schema()}},
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            message = stream.get_final_message()
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        raise EnrichmentUnavailable(f"Enrichment request failed: {exc}") from exc

    if message.stop_reason == "refusal":
        raise EnrichmentUnavailable("Model declined the enrichment request (refusal).")

    text = next((block.text for block in message.content if block.type == "text"), "")
    if not text:
        raise EnrichmentUnavailable("Model returned no text content.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EnrichmentUnavailable(f"Could not parse model output as JSON: {exc}") from exc

    return _parse_report(data, report_date)
