"""Canonical name/place spellings for the PICS report, from the gold samples.

Used by `scripts/clean_report_docx.py` to normalise a finished report and by the
editorial step. Keep in sync with `docs/PICS_NAMES_AND_TITLES.md`. Each entry maps
a WRONG/variant spelling to the gold's canonical form; applied with word boundaries.
"""
from __future__ import annotations

import re

# variant (lowercased, matched whole-word) -> canonical replacement
NAME_NORMALIZATIONS: dict[str, str] = {
    # people
    "al-manfi": "Menfi",
    "al-menfi": "Menfi",
    "al manfi": "Menfi",
    "al-baour": "Baour",
    "al baour": "Baour",
    "al-koni": "Koni",
    "al koni": "Koni",
    "al-abani": "Abani",
    "aguila": "Agila",
    "aqila": "Agila",
    "ageela": "Agila",
    "aqeela": "Agila",
    "agila saleh": "Agila Saleh",
    "dbeibeh": "Dbeibah",
    "al-dbeibah": "Dbeibah",
    "al-dabaiba": "Dbeibah",
    "mleqta": "Mlegta",
    "al-tablaqi": "Al-Tablaki",
    # places
    "sabha": "Sebha",
    "kufra": "Kufrah",
    # role-tag variants -> canonical
    r"\[hor member\]": "[HoR Member]",
    r"\[hor member \]": "[HoR Member]",
    r"\[mo i\]": "[MoI]",
    r"\[moi\]": "[MoI]",
}

# Build compiled (pattern, repl) list. Keys already containing regex (start with
# '[' or contain '\\') are treated as regex; plain words get \b boundaries.
_COMPILED: list[tuple[re.Pattern[str], str]] = []
for variant, canon in NAME_NORMALIZATIONS.items():
    if variant.startswith(r"\[") or "\\" in variant:
        _COMPILED.append((re.compile(variant, re.IGNORECASE), canon))
    else:
        _COMPILED.append((re.compile(rf"\b{re.escape(variant)}\b", re.IGNORECASE), canon))


def normalize_names(text: str) -> str:
    """Replace variant name/place spellings with the gold's canonical form."""
    for pattern, canon in _COMPILED:
        text = pattern.sub(canon, text)
    return text
