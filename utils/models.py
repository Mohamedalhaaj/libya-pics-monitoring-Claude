from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Article:
    source_id: str
    source_name: str
    language: str
    country_focus: str
    title: str
    url: str
    published_at: datetime | None = None
    summary: str = ""
    section: str = ""
    matched_keywords: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "language": self.language,
            "country_focus": self.country_focus,
            "title": self.title,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else "",
            "summary": self.summary,
            "section": self.section,
            "matched_keywords": "; ".join(self.matched_keywords),
        }


@dataclass(slots=True)
class SourceVerification:
    source_id: str
    source_name: str
    url: str
    status: str
    articles_found: int = 0
    error: str = ""
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_row(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "url": self.url,
            "status": self.status,
            "articles_found": self.articles_found,
            "error": self.error,
            "checked_at": self.checked_at.isoformat(timespec="seconds") + "Z",
        }
