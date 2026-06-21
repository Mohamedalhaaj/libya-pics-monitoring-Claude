"""Structural noise removal for scraped HTML listings.

The generic list parser walks broad CSS selectors (down to bare ``li``/``a``) so
it works across many site layouts. The price is that navigation menus, footers,
social bars, category chips and pagination get pulled in as if they were
headlines — the raw scrape was ~80% such noise. This module strips the
structural boilerplate regions before extraction and provides a content filter
that rejects the non-article items that survive (category labels, "Home",
"Facebook", "1 2 3 …", links to /category//tag/ pages, and so on).

Everything here is deterministic and source-agnostic, so it is unit-tested
against synthetic HTML modelled on the real noise.
"""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from bs4.element import Tag

# Structural regions that are never article content. Whole subtrees are removed
# before extraction so their links cannot surface as headlines.
_BOILERPLATE_TAGS = ("nav", "header", "footer", "aside", "form")
_BOILERPLATE_ROLES = {
    "navigation",
    "banner",
    "contentinfo",
    "search",
    "complementary",
    "menu",
    "menubar",
}
# Substrings matched against an element's class/id tokens. Kept conservative so
# we strip chrome (menus, footers, sidebars, share/widget bars) without eating
# the article list itself.
_BOILERPLATE_HINTS = (
    "navbar", "nav-bar", "navigation", "menu", "submenu", "mega-menu",
    "header", "masthead", "footer", "site-footer", "site-header",
    "sidebar", "side-bar", "widget", "social", "share", "sharing",
    "breadcrumb", "pagination", "pager", "cookie", "subscribe",
    "newsletter", "related-posts", "tag-list", "tags-list", "comment",
    "offcanvas", "off-canvas", "drawer", "topbar", "top-bar", "toolbar",
    "skip-link", "back-to-top",
)

# Full-title nav/footer/category labels (normalised). Matched as a whole string,
# so a real headline that merely contains one of these words is never dropped.
_BOILERPLATE_TITLES = {
    # English chrome
    "menu", "home", "news", "sport", "sports", "opinion", "opinions",
    "variety", "varieties", "art", "arts", "cartoon", "cartoons", "crime",
    "crimes", "culture", "life", "science", "tech", "technology", "travel",
    "health", "education", "multimedia", "images", "image", "video", "videos",
    "print edition", "about", "about us", "contact", "contact us",
    "exchange rates", "advertise", "advertise with us", "terms",
    "terms & conditions", "terms and conditions", "privacy",
    "privacy policy", "subscribe", "newsletter", "login", "log in",
    "sign in", "register", "read more", "more", "entertainment", "business",
    "world", "politics", "economy", "economic", "environment", "weather",
    "climate", "climate crisis", "climate solutions", "follow us", "rss",
    "search", "gallery", "photos", "podcasts", "podcast", "live", "latest",
    "trending", "sections", "section", "categories", "category", "tags",
    "tag", "author", "authors", "archive", "archives", "menu close",
    "all news", "share", "next", "previous", "prev",
    # Arabic chrome / category labels seen in the raw scrape
    "القائمة", "الرئيسية", "من نحن", "تواصل معنا", "اتصل بنا", "إتصل بنا",
    "سياسة الخصوصية", "شروط الاستخدام", "شروط الإستخدام", "للإعلان",
    "أرسل مقالة", "فرص عمل", "شارك", "عن الوسط", "راديو الوسط", "جريدة الوسط",
    "صحافة المواطن", "إنفوجرافيك", "كل الأخبار", "مباشر", "اليوم", "أسبوع",
    "شهر", "أخبار", "أخبار الطقس", "الأخبار السياسية", "الأخبار الاقتصادية",
    "سياسة", "اقتصاد", "اقتصاد محلي", "اقتصاد عربي", "اقتصاد دولي", "اقتصاد محلى",
    "محلي", "محلى", "عربي", "عربى", "دولي", "دولى", "عربى ودولى", "عالمي",
    "عالمى", "أفريقيا", "رياضة", "منوعات", "منوعات وترفيه", "ثقافة",
    "ثقافة وفن", "ثقافة وفنون", "صحة", "طب وصحة", "رأي", "وجهات نظر", "فيديو",
    "تقارير", "أجندة", "تكنولوجيا", "علوم وتكنولوجيا", "مجتمع", "حياتنا",
    "سيارات", "كاريكاتير", "أناقة وجمال", "كوجينة", "ديكور", "أمني وعسكري",
    "سلاح", "فيسبوك", "تويتر", "إكس", "تيليغرام", "تليجرام", "إنستغرام",
    "انستغرام", "يوتيوب", "واتساب", "آر إس إس", "تابعنا", "ليبيا",
}

# URL path segments that mark a listing/section/social/auth page, not an article.
_NONARTICLE_URL_RE = re.compile(
    r"/(category|categories|cat|tag|tags|topic|topics|section|sections|"
    r"author|authors|writer|writers|page|pages|live|videos?|photos?|gallery|"
    r"galleries|about|about-us|contact|contact-us|privacy|terms|advertise|"
    r"subscribe|newsletter|login|signin|sign-in|register|rss|feed)"
    r"(/|$|\.|\?|#)",
    re.IGNORECASE,
)
_SOCIAL_HOSTS = (
    "facebook.", "twitter.", "x.com", "instagram.", "youtube.", "youtu.be",
    "t.me", "telegram.", "whatsapp.", "wa.me", "linkedin.", "tiktok.",
    "pinterest.", "snapchat.",
)
# At least one alphabetic letter (any script). Filters out "1", "2", "•", "—".
_HAS_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)

DEFAULT_MIN_TITLE_WORDS = 4


def normalize(text: str) -> str:
    """NFKC + casefold so the same label matches regardless of encoding."""
    return unicodedata.normalize("NFKC", text or "").casefold().strip()


def _decompose(element: Tag) -> None:
    # A subtree may already be gone if an ancestor was removed first.
    if element is None or element.parent is None:
        return
    try:
        element.decompose()
    except Exception:  # pragma: no cover - defensive against bs4 edge cases
        pass


def strip_boilerplate(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove navigation/header/footer/sidebar/social regions in place."""
    targets: list[Tag] = list(soup.find_all(_BOILERPLATE_TAGS))

    for element in soup.find_all(attrs={"role": True}):
        role = str(element.get("role", "")).strip().lower()
        if role in _BOILERPLATE_ROLES:
            targets.append(element)

    for element in soup.find_all(class_=True):
        tokens = " ".join(element.get("class", [])).lower()
        if any(hint in tokens for hint in _BOILERPLATE_HINTS):
            targets.append(element)

    for element in soup.find_all(id=True):
        if any(hint in str(element.get("id", "")).lower() for hint in _BOILERPLATE_HINTS):
            targets.append(element)

    for element in targets:
        _decompose(element)
    return soup


def is_boilerplate_title(title: str) -> bool:
    normalized = normalize(title)
    if not normalized:
        return True
    if normalized in _BOILERPLATE_TITLES:
        return True
    # Pure number / symbol runs (pagination, bullets, separators).
    if not _HAS_LETTER_RE.search(title):
        return True
    return False


def is_nonarticle_url(url: str) -> bool:
    if not url:
        return False
    parts = urlsplit(url)
    host = parts.netloc.lower()
    if any(social in host for social in _SOCIAL_HOSTS):
        return True
    if _NONARTICLE_URL_RE.search(parts.path or ""):
        return True
    return False


def looks_like_article(
    title: str,
    url: str,
    min_words: int = DEFAULT_MIN_TITLE_WORDS,
) -> bool:
    """True if (title, url) plausibly identifies a real article headline.

    Rejects chrome by three independent signals: a boilerplate/empty/numeric
    title, a listing/social/auth URL, or a title too short to be a headline.
    """
    title = (title or "").strip()
    if is_boilerplate_title(title):
        return False
    if is_nonarticle_url(url):
        return False
    if len(title.split()) < min_words:
        return False
    return True
