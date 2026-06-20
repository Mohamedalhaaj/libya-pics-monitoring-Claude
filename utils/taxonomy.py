"""Canonical UNSMIL/PICS report taxonomy.

Defines the fixed section order, suggested subsections, and the mandatory
disclaimer used by the daily Libya News Headlines report. See
docs/report_methodology.md for the editorial rules behind these values.
"""

from __future__ import annotations

# Exact main section order required by the report. Sections with no items are
# omitted at render time, but their relative order never changes.
SECTION_ORDER: list[str] = [
    "United Nations",
    "Politics",
    "Military & Security",
    "Human Rights & Rule of Law",
    "Economy",
    "Environment",
    "Regional & International",
    "Varieties",
]

# Suggested subsections per section. Used to steer the enrichment model and to
# order subsections within a section; the model may add an "Other ..." bucket.
SUGGESTED_SUBSECTIONS: dict[str, list[str]] = {
    "United Nations": [
        "UNSMIL and political process",
        "UN agencies and international support",
        "Security Council and international mediation",
        "Other UN news",
    ],
    "Politics": [
        "Political institutions and governance",
        "Elections and constitutional process",
        "Government and municipal affairs",
        "Other political news",
    ],
    "Military & Security": [
        "Security and crime",
        "Border and military affairs",
        "Armed groups and ceasefire/security arrangements",
        "Other security news",
    ],
    "Human Rights & Rule of Law": [
        "Migration and human trafficking",
        "Justice and accountability",
        "Health, children and vulnerable groups",
        "Civil liberties and human rights",
        "Other human rights and rule-of-law news",
    ],
    "Economy": [
        "Banking and currency",
        "Energy and fuel",
        "Markets, labour and services",
        "Infrastructure and reconstruction",
        "Other economic news",
    ],
    "Environment": [
        "Weather, climate and agriculture",
        "Water and environmental resources",
        "Other environment news",
    ],
    "Regional & International": [
        "Diplomacy and foreign relations",
        "Regional security",
        "Gaza/convoy-related Libya news",
        "Other regional and international news",
    ],
    "Varieties": [
        "Culture, heritage and society",
        "Sports",
        "Other varieties",
    ],
}

DISCLAIMER = (
    "DISCLAIMER: The Media Monitoring Reviews are compiled by the Public "
    "Information & Communications Section (PICS) of UNSMIL. These Reports do not "
    "reflect the views or official positions of UNSMIL, nor does UNSMIL vouch "
    "for the accuracy of the information contained therein. If you have any "
    "questions/suggestions, please contact: unsmil-info-libya@un.org"
)


def section_sort_key(section_name: str) -> int:
    """Sort key placing sections in canonical order; unknown names go last."""
    try:
        return SECTION_ORDER.index(section_name)
    except ValueError:
        return len(SECTION_ORDER)
