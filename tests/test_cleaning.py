"""Tests for the structural noise filter (utils.cleaning + GenericListParser).

Runnable directly (`python tests/test_cleaning.py`) or under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.cleaning import (  # noqa: E402
    is_boilerplate_title,
    is_nonarticle_url,
    looks_like_article,
)
from parsers.generic import GenericListParser  # noqa: E402

# A listing page modelled on the real noise: a nav menu, a footer with social
# and category links, pagination, and two genuine article cards in <main>.
NOISY_HTML = """
<html><body>
  <nav class="site-nav">
    <a href="/news">News</a>
    <a href="/sports">Sports</a>
    <a href="/category/economy">Economy</a>
  </nav>
  <header class="masthead"><a href="/">Home</a></header>
  <main>
    <ul class="article-list">
      <li><a href="/2026/06/20/elections">Libya's three councils reach agreement to hold elections before February 2027</a></li>
      <li><a href="/2026/06/20/migrants">At least 15 migrant bodies wash ashore in eastern Libya</a></li>
      <li><a href="/category/libya">Libya</a></li>
      <li><a href="/tag/oil">Oil</a></li>
      <li><a href="/page/2">2</a></li>
    </ul>
  </main>
  <aside class="sidebar"><a href="/2026/06/20/related">Most read this week in Tripoli</a></aside>
  <footer class="site-footer">
    <a href="https://facebook.com/outlet">Facebook</a>
    <a href="/about-us">About Us</a>
    <a href="/privacy">Privacy Policy</a>
  </footer>
</body></html>
"""

SOURCE = {
    "id": "test_source",
    "name": "Test Source",
    "language": "en",
    "url": "https://example.com/news",
    "parser": "generic_list",
    "require_keyword_match": False,  # isolate the structural filter
    "selectors": {
        "article": "article, .post, li",
        "title": "h2 a, h3 a, a",
        "url": "h2 a, h3 a, a",
        "summary": "p",
        "date": "time",
        "section": ".category",
    },
}


def test_boilerplate_titles():
    for label in ["Home", "News", "Sports", "Economy", "1", "•", "اقتصاد", "رياضة", "من نحن"]:
        assert is_boilerplate_title(label), label
    for headline in [
        "At least 15 migrant bodies wash ashore in eastern Libya",
        "Libya's three councils reach agreement to hold elections",
    ]:
        assert not is_boilerplate_title(headline), headline


def test_nonarticle_urls():
    for url in [
        "https://example.com/category/economy",
        "https://example.com/tag/oil",
        "https://example.com/page/2",
        "https://facebook.com/outlet",
        "https://example.com/about-us",
    ]:
        assert is_nonarticle_url(url), url
    assert not is_nonarticle_url("https://example.com/2026/06/20/elections")


def test_looks_like_article_combines_signals():
    # A real article: long title + article URL.
    assert looks_like_article(
        "At least 15 migrant bodies wash ashore in eastern Libya",
        "https://example.com/2026/06/20/migrants",
    )
    # A long, real-looking title is still rejected when the link is social.
    assert not looks_like_article(
        "At least 15 migrant bodies wash ashore in eastern Libya",
        "https://x.com/outlet/status/123",
    )
    # Short nav label rejected on word count even with a clean URL.
    assert not looks_like_article("Oil", "https://example.com/2026/06/20/oil")


def test_parser_drops_noise_keeps_headlines():
    articles = GenericListParser(SOURCE, keywords=[]).parse(NOISY_HTML)
    titles = {a.title for a in articles}
    assert "Libya's three councils reach agreement to hold elections before February 2027" in titles
    assert "At least 15 migrant bodies wash ashore in eastern Libya" in titles
    # Every flavour of noise must be gone.
    for noise in ["Home", "News", "Sports", "Economy", "Libya", "Oil", "2", "Facebook", "About Us", "Privacy Policy"]:
        assert noise not in titles, f"noise leaked: {noise}"
    # 2 real cards (+ maybe the sidebar item, which the boilerplate strip removes).
    assert len(articles) == 2, f"expected 2 articles, got {len(articles)}: {titles}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\nAll {len(tests)} cleaning tests passed.")
