"""RSS/Atom feed fetching and discovery.

Feeds are the cleanest possible source: publisher-curated titles, real
publication dates, and no navigation/footer noise. They also reach several
outlets whose HTML is bot-protected (Akhbar Libya 24, New Arab, Arabi21), which
returned nothing on the headless browser. We fetch feeds over plain HTTP — a
real browser would render an XML feed as an HTML viewer wrapper — and keep the
browser path only for sources without a usable feed.
"""

from __future__ import annotations

import asyncio
import logging
import re
import urllib.request
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Accept": (
        "application/rss+xml, application/atom+xml, application/xml;q=0.9, "
        "text/xml;q=0.8, */*;q=0.5"
    ),
}

_FEED_LINK_RE = re.compile(
    r"<link[^>]+type=[\"']application/(?:rss|atom)\+xml[\"'][^>]*>", re.IGNORECASE
)
_HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.IGNORECASE)


def _get(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, "replace")


async def fetch_feed_text(url: str, timeout_seconds: float = 20.0) -> str:
    """Fetch a feed URL over HTTP without blocking the event loop."""
    return await asyncio.to_thread(_get, url, timeout_seconds)


def discover_feed_url(html: str, base_url: str) -> str | None:
    """Return the first RSS/Atom feed advertised via <link rel=alternate>."""
    for tag in _FEED_LINK_RE.findall(html or ""):
        match = _HREF_RE.search(tag)
        if match:
            return urljoin(base_url, match.group(1))
    return None
