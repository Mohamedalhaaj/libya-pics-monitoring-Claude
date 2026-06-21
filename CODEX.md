# CODEX.md — Generate the PICS "Libya News Headlines" report

You are producing the UNSMIL/PICS **"Libya News Headlines – 18-21 June"** report
from data that is already collected and frozen in this repo. **Do not re-scrape**
— everything you need is here.

## Inputs (in this repo)

| Path | What it is |
|---|---|
| `data/libya_media_headlines.csv` (and `.json`) | **Your source material** — 456 collected, deduplicated, dated articles (18–21 June 2026; 132 outlets; Arabic + English). Columns: `source_name, language, title, summary, url, published_at, section`. |
| `docs/codex_enrichment_brief.md` | **The editorial rules you MUST follow** — translation, dedup, attribution format, role prefixes, the 8-section taxonomy, disclaimer. Read it fully before writing anything. |
| `reference/Libya_News_Headlines_18-21_June_2026_GOLD.docx` | The human gold report for the same dates — for **self-scoring only**. Do not copy text from it. |
| `samples/*.docx` | Earlier gold reports — style reference and the eval profile. |

## Task

1. Read `docs/codex_enrichment_brief.md` end to end.
2. Turn `data/libya_media_headlines.csv` into a Word document titled
   **"Libya News Headlines – 18-21 June"**, following the brief exactly.
3. Save it as `Libya_News_Headlines_18-21_June_2026_PICS.docx` in the repo root.

## Self-check — iterate until it passes

```bash
pip install -r requirements.txt
python evaluate.py Libya_News_Headlines_18-21_June_2026_PICS.docx \
  --gold reference/Libya_News_Headlines_18-21_June_2026_GOLD.docx \
  --collected data/libya_media_headlines.csv
```

Aim for a **total ≥ 95**, matching the gold profile:

| check | target |
|---|---|
| structure | 100 |
| duplicate bullets | **0** |
| boilerplate noise | 0 |
| English headlines | 100% |
| sections in canonical order | yes |
| role-prefix ratio | ~0.15 (`[HoR Member] Jehani: …`) |
| distinct bullets | ~150–170, every one unique |
| ceiling coverage | as high as the data allows (~90%) |

## Pitfalls that cost points in earlier attempts — avoid them up front

- **No duplicate bullets and no vague filler.** Each bullet is one distinct story
  and appears once. Never emit placeholders like "A Libya-related report covered
  domestic developments…" or "Regional talks addressed Libya." If you can't state
  a specific fact, drop the item. (A shorter report of distinct bullets beats a
  padded one — the gold has zero duplicates.)
- **Tag only Arabic outlets** with `(Arabic)`; **never** write `(English)`.
- **Emit each of the 8 sections exactly once** — don't repeat a section heading.
- **List every outlet that reported a story** (they are in the data — this drives
  coverage), but **never repeat an outlet within a single bullet**.
- **Bracket the role** on any named-official statement: `[SRSG] Tetteh warns…`,
  `[Mufti] Gharyani issues a fatwa…`, `[HoR Member] Jehani: …`.

When `evaluate.py` reports **total ≥ 95 with 0 duplicate bullets**, you're done.

> Tip: if you have an `ANTHROPIC_API_KEY` with credit, you can instead let the
> pipeline do the editorial step itself —
> `python scraper.py --start-date 2026-06-18 --end-date 2026-06-21` — but that
> re-scrapes **live** data, which drifts day to day. Use the frozen `data/` files
> above for a reproducible result.
