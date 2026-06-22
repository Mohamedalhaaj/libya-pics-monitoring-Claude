# CODEX.md — Generate a PICS "Libya News Headlines" report for any dates

Goal: given a **date range**, produce a UNSMIL/PICS **"Libya News Headlines"**
Word report at the quality of the human gold reports in `samples/`. Same process
every time: **collect → write per the brief → self-check → iterate.**

---

## Quickstart for a new report

Replace `START`/`END` with the coverage dates (ISO `YYYY-MM-DD`), e.g.
`2026-06-22` to `2026-06-25`.

```bash
pip install -r requirements.txt
playwright install chromium            # only needed for the collection step

# 1. Collect fresh data for the dates (live scrape -> output/libya_media_headlines.csv)
python scraper.py --start-date START --end-date END --no-enrich
#    Then VERIFY it before going further — see docs/scraping_sop.md §2 (quality gate).

# 2. Write the report (you, Codex) — see "Write the report" below.

# 3. Self-check, then iterate until it passes
python evaluate.py Libya_News_Headlines_<dates>_PICS.docx \
  --collected output/libya_media_headlines.csv
```

**Collection must be clean before anything else** — follow
[`docs/scraping_sop.md`](docs/scraping_sop.md): prerequisites (network +
chromium), the quality gate (0 `failed` sources, ≥95% dated, ≥50 outlets, 0
noise), and the CDP fallback for bot-protected sources. A bad scrape can't be
rescued by good editing.

> **Live data:** the scraper reads RSS/Atom feeds and Google News, which only
> return **recent** items. Run it within a few days of the coverage dates — you
> cannot reconstruct an old window later. The title auto-derives from the dates
> (e.g. `22-25 June`).

---

## Write the report

Read `docs/codex_enrichment_brief.md` **in full**, then turn
`output/libya_media_headlines.csv` into a Word document titled
`Libya News Headlines – <range>` (the brief explains the title rule). The CSV
columns are `source_name, language, title, summary, url, published_at, section`.

Save as `Libya_News_Headlines_<dates>_PICS.docx` in the repo root.

> **Shortcut:** if the environment has an `ANTHROPIC_API_KEY` with credit, skip
> the manual step entirely — `python scraper.py --start-date START --end-date END`
> (without `--no-enrich`) scrapes **and** writes the finished report via
> `utils/enrich.py`. The manual Codex path exists for when there is no API credit.

---

## Self-check — the quality bar

```bash
python evaluate.py <your_report>.docx --collected output/libya_media_headlines.csv
```

For a **new date range there is no date-matched gold**, so the coverage component
is not scored. A conformance total ≥ 90 is **necessary but not sufficient** — the
report can clear it while under-merging. You must also hit the dedup target:

| check | target |
|---|---|
| structure | 100 |
| **multi-source / dedup** | **≈ 0.20–0.30** (the `evaluate.py` "multi-source/dedup" line). If it's ~0.10–0.15 you UNDER-MERGED — fix before shipping. |
| **bullet count** | **≈ the day's distinct *stories*, not the article count** — typically ~70–90 for a single day. ~1.5–2× that (e.g. ~140) means you listed the same story separately per outlet instead of merging. |
| duplicate bullets | **0** (exact repeats) |
| boilerplate noise | 0 |
| Arabic outlet names | **0** |
| English headlines | 100% |
| sections in canonical order | yes |
| role-prefix ratio | ~0.15 (`[HoR Member] Jehani: …`) |

(When you *do* have a same-dates human report, add
`--gold path/to/that.docx` to also score outlet coverage.)

---

## Pitfalls that cost points — avoid them up front

- **MERGE the same story across outlets (brief rule 3 — the #1 mistake).** If six
  outlets report the same migrant shipwreck, that is **ONE bullet citing all six**
  (`… – Reuters / New Arab / Shafaq (Arabic) / …`), not six separate bullets.
  "No duplicate bullets" only forbids *exact* repeats — it does **not** excuse
  listing the same story once per outlet. Under-merging is what turns a correct
  ~80-bullet report into a bloated ~140-bullet one with a low dedup score. After
  drafting, scan for near-identical bullets across the report and merge them.
- **No duplicate bullets and no vague filler.** Each bullet = one distinct story,
  once. Never emit placeholders like "A Libya-related report covered domestic
  developments…". A shorter report of distinct bullets beats a padded one.
- **Tag only Arabic outlets** with `(Arabic)`; **never** `(English)`.
- **Emit each of the 8 sections exactly once** — don't repeat a section heading.
- **List every outlet that reported a story** (they are in the CSV), but **never
  repeat an outlet within one bullet**.
- **Bracket the role** on any named-official statement: `[SRSG] Tetteh warns…`,
  `[Mufti] Gharyani…`, `[HoR Member] Jehani: …`.

When `evaluate.py` reports the targets above with **0 duplicate bullets**, ship it.

---

## Reproducible worked example (18–21 June 2026)

A frozen snapshot from the original run is committed so you can validate the whole
loop without scraping, and against a real human gold:

```bash
python evaluate.py Libya_News_Headlines_18-21_June_2026_PICS.docx \
  --gold reference/Libya_News_Headlines_18-21_June_2026_GOLD.docx \
  --collected data/libya_media_headlines.csv
```

- `data/libya_media_headlines.csv` (+ `.json`) — the 456-article snapshot.
- `reference/…GOLD.docx` — the human report for those dates (scored 97.2 in our run).

Use this example to confirm your method, then apply the **Quickstart** to new dates.
