"""Canonical outlet names for aggregator (Google News) attribution.

Google News reports each item's publisher in its own language and house spelling
("بوابة الوسط", "Anadolu Ajansı", "allAfrica.com"). The PICS gold reports cite
those outlets by a consistent English label ("Al Wasat", "Anadolu Agency",
"all Africa"). Mapping the raw publisher to the gold label keeps attribution
consistent, lets the same story from a direct feed and from Google News
deduplicate, and makes coverage compare correctly against the gold report.

Only outlets that matter (appear in the gold reports or correspond to a monitored
source) are mapped; unmapped publishers pass through unchanged.
"""

from __future__ import annotations

# raw publisher (any script) -> canonical English label used in the gold reports
OUTLET_ALIASES: dict[str, str] = {
    # Arabic outlets
    "عين ليبيا": "Ean Libya",
    "بوابة الوسط": "Al Wasat",
    "الوسط": "Al Wasat",
    "العين الإخبارية": "Al Ain",
    "سكاي نيوز عربية": "Sky News Arabia",
    "الشرق الأوسط": "Asharq Al-Awsat",
    "العربي الجديد": "New Arab",
    "اندبندنت عربية": "Independent Arabia",
    "العربية": "Al Arabiya",
    "صحيفة الساعة 24": "Alsaaa 24",
    "الساعة 24": "Alsaaa 24",
    "تليكسبريس": "Telexpresse",
    "مركز المستقبل": "Future Center",
    "القدس العربي": "Al Quds Al Arabi",
    "الجزيرة نت": "Al Jazeera",
    "الجزيرة": "Al Jazeera",
    "الشرق للأخبار": "Asharq News",
    "الشرق مع بلومبرغ": "Asharq News",
    "شفق نيوز": "Shafaq",
    "سانا": "SANA",
    "إرم نيوز": "Erem News",
    "المصري اليوم": "Al-Masry Al-Youm",
    # English / Latin variants -> gold spelling
    "the libya observer": "Libya Observer",
    "libyaupdate.com": "Libya Update",
    "libyaobserver.ly": "Libya Observer",
    "the new arab": "New Arab",
    "anadolu ajansı": "Anadolu Agency",
    "anadolu ajansi": "Anadolu Agency",
    "allafrica.com": "all Africa",
    "allafrica": "all Africa",
    "middle-east-online.com": "Middle East Online",
    "annahar.com": "Annahar",
    "news.cgtn.com": "CGTN",
    "dw.com": "DW",
    "cbc": "CBC News",
    "新华网": "Xinhua",
    "fana news": "Fana",
    "ap news": "Associated Press",
    "the associated press": "Associated Press",
    "oilprice.com": "Oil Price",
    "timeslive": "Times Live",
    "meed": "Middle East Economic Digest",
    "the new times": "New Times",
    "the national": "National",
    "rna reportage": "RNA",
    # Arabic outlets surfaced by the Google News Arabic fan-out — romanise to a
    # consistent English label (the report and gold cite outlets in Latin script).
    "شبكة تواصل الإخبارية": "Tawasul News",
    "اليوم السابع": "Youm7",
    "بوابة الشروق": "Al-Shorouk",
    "بطولات": "Botola",
    "يلاكورة": "Yallakora",
    "الطاقة": "Attaqa",
    "حفريات": "Hafryat",
    "التلفزيون العربي": "Al-Araby TV",
    "شبكة رؤية الإخبارية": "Ruya News",
    "أخبار الغد": "Akhbar Al-Ghad",
    "معلومات مباشر": "Mubasher",
    "جريدة الشرق": "Al-Sharq",
    "جريدة البورصة": "Al-Borsa",
    "cnbc عربية": "CNBC Arabia",
    "إرم بزنس": "Erem Business",
    "cnn الاقتصادية": "CNN Arabic",
    "إيلاف": "Elaph",
    "جريدة زمان التركية": "Zaman",
    "عكاظ": "Okaz",
    "صدى البلد": "Sada El Balad",
    "الأيام نيوز": "Al-Ayam News",
    "بوابة الأهرام": "Ahram Gate",
    "بوابة روز اليوسف": "Rose El-Youssef",
    "صحيفة الخليج": "Al-Khaleej",
    "الاتحاد للأخبار": "Al-Ittihad",
    "الوقائع الإخبارية": "Al-Waqaie",
    "بوابة أخبار اليوم الإلكترونية": "Akhbar El-Yom",
    "جريدة القدس": "Al-Quds",
    "trt عربي": "TRT Arabic",
    "عربي21": "Arabi21",
    "راي اليوم": "Rai Al-Youm",
    "بوابة الوفد": "Al-Wafd",
    "النهار": "Annahar",
    "سكاي نيوز": "Sky News Arabia",
    "الوطن": "Al-Watan",
    "نبأ العرب": "Naba Al-Arab",
    "الخبر": "Al-Khabar",
    "اخبارك نت": "Akhbarak",
    "الإمارات ليكس": "Emirates Leaks",
    "جريدة آخر الأخبار": "Akher Al-Akhbar",
    "جريدة البلاد السعودية": "Al-Bilad",
    "جريدة المدينة": "Al-Madina",
    "جريدة النهار المصرية": "Al-Nahar",
    "نافذة العرب": "Nafidha Al-Arab",
    "البوابة نيوز": "Al-Bawaba News",
    "جريدة حابي": "Hapi Journal",
    "الهيئة الوطنية للإعلام": "National Media Authority",
    "اخبار ليبيا": "Akhbar Libya",
    "أخبار ليبيا": "Akhbar Libya",
    "سودافاكس": "Sudafax",
    "بوابة دار الهلال": "Dar Al-Hilal",
    "صوت الإمارات": "Sawt Al-Emarat",
    "الشرق بلومبرغ": "Asharq Bloomberg",
    "المنظمة العربية للتربية و الثقافة و العلوم": "ALECSO",
    "بيلبورد عربية": "Billboard Arabia",
    "وكالة الأنباء القطرية": "Qatar News Agency",
}

# Normalised lookup (casefolded). Arabic casefolds to itself, so this is safe.
_ALIASES_CF = {key.casefold(): value for key, value in OUTLET_ALIASES.items()}


def canonicalize_outlet(name: str) -> str:
    """Map a raw publisher name to its canonical label; pass through if unknown."""
    cleaned = (name or "").strip().strip("-|–—").strip()
    return _ALIASES_CF.get(cleaned.casefold(), cleaned)
