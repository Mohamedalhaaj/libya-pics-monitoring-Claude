"""Post-process a finished PICS report .docx to cut editor time.

Works on ANY report (Codex-authored or build-script), preserving hyperlinks:
  1. strips the terminal '.' from every headline (gold style = no full stop),
  2. normalises name/place spellings to the gold's canonical form (utils/names.py).

Usage:
  python scripts/clean_report_docx.py REPORT.docx [-o OUT.docx] [--no-names]
If -o is omitted, writes REPORT_clean.docx next to the input.

It does NOT remove sport/weather/old/duplicate items — those need editorial
judgement (see docs/codex_enrichment_brief.md); this only fixes the mechanical
two: trailing periods and spellings.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.names import normalize_names  # noqa: E402

DASHES = ("–", "—")  # en / em dash used between headline and sources


def strip_terminal_period(paragraph) -> bool:
    """Remove a '.' sitting immediately before the first headline↔source dash."""
    runs = paragraph.runs
    dash_i = next((i for i, r in enumerate(runs) if any(d in r.text for d in DASHES)), None)
    if dash_i is None:
        return False
    for j in range(dash_i, -1, -1):
        t = runs[j].text
        if j == dash_i:
            # only the portion before the dash counts
            cut = min((t.find(d) for d in DASHES if d in t), default=-1)
            before, rest = t[:cut], t[cut:]
            stripped = before.rstrip()
            if stripped.endswith("."):
                runs[j].text = stripped[:-1] + (" " if before.endswith(" ") else "") + rest
                return True
            if stripped:
                return False  # real text before dash, no period -> nothing to do
        else:
            stripped = t.rstrip()
            if stripped.endswith("."):
                runs[j].text = stripped[:-1] + t[len(stripped):]
                return True
            if stripped:
                return False
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-names", action="store_true", help="skip spelling normalisation")
    args = ap.parse_args()

    src = Path(args.docx)
    out = Path(args.out) if args.out else src.with_name(src.stem + "_clean.docx")
    doc = Document(str(src))

    periods = names = 0
    for p in doc.paragraphs:
        if any(d in p.text for d in DASHES):
            if strip_terminal_period(p):
                periods += 1
        if not args.no_names:
            for r in p.runs:  # direct runs only (won't touch hyperlink source labels)
                new = normalize_names(r.text)
                if new != r.text:
                    r.text = new
                    names += 1

    doc.save(str(out))
    print(f"periods stripped: {periods} | runs spelling-normalised: {names}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
