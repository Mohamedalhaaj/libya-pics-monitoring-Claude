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

## Be your own judge — audit the draft BEFORE you finalize

You are an LLM that can read Arabic and English and open links. The automated
`evaluate.py` (next section) catches the cheap, mechanical errors — but two things
only *you* can verify by actually reading the articles: whether each link matches
its bullet, and whether the same story was written twice. Run these four passes on
your draft and fix everything they surface. **Read the article (the CSV title/summary,
or open the URL in the browser when unsure) — do not guess.**

**Pass 1 — Link fidelity (every bullet, every source).**
For each bullet, read EACH article it cites. Every cited article must report the
bullet's exact event.
- A cited article about a *different* event → remove it from this bullet (give that
  story its own bullet if it matters).
- If the headline matches none of its links → rewrite the headline to the article,
  or drop the bullet.
- **Verify every SPECIFIC against the article (rule 10), not just the topic:** each
  name, number, sentence length, charge, place and date must appear in the source.
  Do not add a person, co-defendant or figure that isn't there, and never change a
  number (e.g. "seven years and four months" must not become "life"). If a detail
  isn't in the article, drop it. When unsure of a name/number, re-open the link.

**Pass 2 — Same-event merge (every multi-source bullet).**
Write the bullet's event in ≤5 words (e.g. "UNSMIL launches dialogue meetings").
EVERY cited source must fit that exact event. Sharing only a topic word (UNSMIL,
oil, migration, Dbeibeh) is NOT enough.
- WRONG: "UNSMIL launches dialogue" citing [the launch] + [a Mufti's fatwa against
  UNSMIL] + [an MP's criticism] → these are 3 events → 3 separate bullets.

**Pass 3 — Whole-report de-duplication (across sections AND languages).**
Give every bullet a short event-key = main proper noun + main action (e.g.
"Najim · prison sentence", "Dbeibeh · meets Egyptian intelligence"). Sort the keys
and find any event that appears **twice** — including an English-source bullet and
an Arabic-source bullet about the same event, or the same event placed in two
sections. Merge each into ONE bullet (one section, citing all outlets).
- Quick test for any two bullets: do they share the main proper noun AND the main
  action? If yes → same story → merge.
- Real failures to catch: a prison sentence written as 3 bullets; one Dbeibeh
  meeting as 3 bullets; an oil-output record twice.

**Pass 4 — Specificity.** Every bullet states one concrete fact. Delete vague
umbrellas ("officials reported…", "international outlets linked…").

**Pass 5 — Source credibility & attribution.** For every source ask "is this the
outlet that actually reported it, and does the bullet attribute it correctly?"
Full detail + real examples in [`docs/codex_qa_lessons.md`](docs/codex_qa_lessons.md).
> **Do this first — it's the #1 recurring miss:** underline every **named entity**
> (org, person, place, outlet) **and every scope word** ("and Tunisia", "and the
> ICJ", "chambers", "several", "political figures") in each bullet, and confirm
> **each is supported by one of that bullet's cited links.** Choosing the right
> outlet is only half the job — the *sentence* must match what the links say. If a
> claim isn't backed: add the source (often already in the CSV — search it), split
> the bullet (two organisations = two bullets), or narrow the wording. Don't name a
> second org, an extra country, or a vaguer group than the links support.
- **Drop junk sources** even when the fact is true: content aggregators
  (MSN/Yahoo/Bing/ground.news), auto-translation portals (`*.vn`, machine-translated
  mirrors), and off-topic local papers running a wire (mlive.com, daily-sun.com —
  red flag: the headline doesn't mention Libya). Cite the wire (AP/Reuters/AFP/ANSA)
  or a Libyan/regional outlet instead.
- **Displayed outlet == the linked URL's outlet**; if the sentence names an outlet
  or author, it must be the linked one (e.g. don't write "OilPrice.com argued" then
  link Anas Alhajji's Substack, or "Sada reports" then link New Arab).
- **`[Role]` only on a named person**, role verified — never on a website, a wire
  agency-as-publisher, or a category.
- **Every org/municipality/person named in a headline needs a supporting link**;
  otherwise narrow the headline or split it (don't claim "Amnesty and the ICJ" or
  "Kufra, Abyar and Green Mountain" with only one source).
- **Don't under-source the flagship story**: re-attach every CSV outlet on the
  *same* event (the fix for over-merging is not to drop same-event outlets).
- **Each source's publication date must be inside the window** (older event OK only
  via an in-window follow-up).
- **Never default to `[Analyst]`** — a `[Role]` must be the person's verified real
  role (look them up; e.g. Mohamed Baiou is a journalist/former media-authority head,
  not an analyst). If you can't verify it, use no bracket.
- **No headline starts with the outlet** — "Al Shahed cites…", "Sada reports…",
  "Coverage of … warns…", "Libya is reported to…" are wrong. Lead with the FACT; the
  outlet goes only after the en dash.
- **Analysis/Report/Opinion/Feature items go under Varieties**, not scattered in
  Politics/Economy/Environment; add a short neutral summary. Plain news carries no
  Analysis/Report prefix.

**Use the browser** whenever you are unsure two articles are the same event, or
whether a headline matches its link: open the URLs and read them.

Only once all four passes are clean, run the automated check below.

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
| **vague/umbrella bullets** | **0** — every bullet states one specific fact, not "officials reported …" |
| **headline ↔ link fidelity** | **0 mismatches** (English-source); each bullet must match the article it links |
| **over-merged bullets** | **0** — a bullet linking ≥3 sources must have them all on the SAME event, not just the same topic (merge by event, not topic) |
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
