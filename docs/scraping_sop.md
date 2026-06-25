# Collection SOP — scrape cleanly, then verify before writing

The scraper already applies every collection workaround automatically — RSS/Atom
feed-first, a Google News topic + `site:` fan-out, per-item outlet attribution,
outlet-name aliasing, navigation/footer noise stripping, and Arabic + relative
date parsing. Your job is to **run it correctly and verify the output passes the
quality gate before writing the report.** Do not hand-edit the CSV.

## 0. Prerequisites (must hold or collection silently underperforms)

- **Network access** to the open internet (the feed hosts, `news.google.com`, and
  the source sites). In a no-network sandbox, collection cannot work — run where
  outbound HTTPS is allowed.
- `pip install -r requirements.txt` and `playwright install chromium` (the
  browser is only used for the HTML-fallback sources).
- **Recency:** feeds and Google News return only recent items, so scrape **within
  a few days** of the coverage dates. You cannot reconstruct an old window later.

## 1. Collect

```bash
python scraper.py --start-date START --end-date END --no-enrich
```

Writes:
- `output/libya_media_headlines.csv` — the articles (your source material)
- `output/source_verification_table.csv` — per-source status (`ok` / `empty` / `failed`)
- `logs/scraper.log` — per-source method (`feed` / `gnews xN` / `html`) and counts

## 2. Quality gate — run these and confirm they pass

```bash
# Source health: ok / empty / failed
python -c "import csv,collections;r=list(csv.DictReader(open('output/source_verification_table.csv',encoding='utf-8-sig')));print(collections.Counter(x['status'] for x in r))"

# Data sanity: article count, % dated, distinct outlets
python -c "import csv;r=list(csv.DictReader(open('output/libya_media_headlines.csv',encoding='utf-8-sig')));d=sum(1 for x in r if x['published_at']);print(f'{len(r)} articles | {100*d//max(len(r),1)}% dated | {len(set(x[\"source_name\"] for x in r))} outlets')"
```

**Pass criteria:**

| signal | expected | if not |
|---|---|---|
| `failed` sources | **0** | a network/parse error — check `logs/scraper.log`; re-run |
| `empty` sources | a few is normal | see §3 (bot-protected); the `site:` fallback + Google News usually cover them |
| **critical source empty** (Akhbar Libya 24, Al Wasat, Libya Observer, LANA, Ean Libya, Al Shahed, Al Marsad, Al Menassa, Libya 24, Libya Review) | **0** | a workhorse outlet returned nothing — **do not build**; the scrape-health gate logs `SCRAPE-HEALTH GATE`. Re-run, or run with `--cdp-url` (§3). Use `--fail-on-empty-critical` to make this a hard stop. |
| % dated | **≥ 95%** | a feed regressed; check the log for `method=html` sources |
| distinct outlets | **≥ 50** for a multi-day window | network or Google News blocked — see §0/§3 |
| boilerplate noise | **0** (the filter handles it) | report a bug, don't ship |

Only proceed to writing the report once these pass.

## 3. Bot-protected / JS-rendered sources (optional, for maximum coverage)

A few outlets (Al Wasat, Libya Observer, Alsaaa 24, Reuters/BBC via HTML, …) block
the headless browser with a 403 and show as `empty`. Two layers now recover them
automatically: the Google News fan-out, **and** a per-source `site:<domain>`
Google-News query that fires whenever a source's own scrape returns nothing
(`method=gnews(site:)` in the log). So most empty rows self-heal.

> **Why this matters (24–25 June 2026):** Akhbar Libya 24 — a top-3 workhorse —
> 403-blocked the scraper *and* wasn't surfaced by the topic fan-out, so it
> contributed **0** articles and nothing flagged it; the report still looked
> complete. The `site:akhbarlibya24.net` fallback + the critical-source gate now
> catch exactly this. A `critical` outlet at `empty` is a **silent scrape gap,
> not a quiet news day** — never ship over it.

To squeeze out anything still blocked, fetch through a real Chrome over the
DevTools protocol (this is what verified the recovery — the browser loads the
page the headless scraper can't):

```bash
# 1. Launch Chrome with a debugging port (separate profile):
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-scraper-profile about:blank

# 2. Point the scraper at it:
python scraper.py --cdp-url http://localhost:9222 --start-date START --end-date END --no-enrich
```

## 4. Common mistakes to avoid

- **Shipping without the quality gate.** An empty/garbled CSV produces a bad
  report no matter how good the editorial step is. Always run §2 first.
- **Editing the CSV by hand.** Fix collection in `sources.json`/the parsers, never
  in the output; otherwise the next run silently reverts your fix.
- **Scraping an old window.** Live feeds won't have it — the report will be thin.
- **Assuming `empty` = broken.** For most sources it just means the HTML was
  bot-blocked and Google News (or the `site:` fallback) picked up its stories.
- **Assuming `empty` = fine.** The opposite trap: an `empty` **critical** outlet
  is a silent loss of a whole source. Check the gate line and the critical-source
  row in §2 before building — don't let a 403 quietly delete a workhorse.

Once §2 passes, follow [`../CODEX.md`](../CODEX.md) "Write the report".
