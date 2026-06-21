from __future__ import annotations

import html as html_lib
import re
from calendar import timegm
from datetime import datetime, timezone

import feedparser

from parsers.base import BaseParser
from parsers.generic import deduplicate_articles, match_keywords
from utils.models import Article

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    """Strip HTML tags/entities and collapse whitespace from a feed field."""
    return " ".join(_TAG_RE.sub(" ", html_lib.unescape(text or "")).split())


def _entry_datetime(entry) -> datetime | None:
    # feedparser normalises feed dates to a UTC struct_time. Convert to the
    # naive-UTC convention the rest of the pipeline compares against.
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            return datetime.fromtimestamp(timegm(struct), tz=timezone.utc).replace(tzinfo=None)
    return None


def _entry_section(entry) -> str:
    tags = entry.get("tags")
    if tags:
        return _clean(tags[0].get("term", ""))
    return _clean(entry.get("category", ""))


class FeedListParser(BaseParser):
    """Parse an RSS/Atom feed body into Article records.

    Feeds are already article lists, so there is no boilerplate to strip; we
    only apply the same keyword gate as the HTML parser (broad, site-wide feeds
    such as Asharq Al-Awsat or New Arab set ``require_keyword_match`` to filter
    down to Libya items).
    """

    def parse(self, feed_text: str) -> list[Article]:
        parsed = feedparser.parse(feed_text)
        require_keyword = self.source.get("require_keyword_match", True)
        articles: list[Article] = []

        for entry in parsed.entries:
            title = _clean(entry.get("title", ""))
            if not title:
                continue
            url = (entry.get("link") or "").strip()
            summary = _clean(entry.get("summary", entry.get("description", "")))

            matched_keywords = match_keywords(f"{title} {summary}", self.keywords)
            if require_keyword and not matched_keywords:
                continue

            articles.append(
                Article(
                    source_id=self.source["id"],
                    source_name=self.source["name"],
                    language=self.source["language"],
                    country_focus=self.source.get("country_focus", "Libya"),
                    title=title,
                    url=url,
                    published_at=_entry_datetime(entry),
                    summary=summary,
                    section=_entry_section(entry),
                    matched_keywords=matched_keywords,
                )
            )

        return deduplicate_articles(articles)
