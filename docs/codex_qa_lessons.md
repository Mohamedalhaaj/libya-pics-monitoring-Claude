# Codex QA lessons — link fidelity, source credibility & attribution

**Read this before writing a report, and again during the self-audit.** It is the
distilled output of a full bullet-by-bullet QA review (the 22–23 June 2026
report). Each item is a defect class that actually shipped, the rule it breaks,
and the fix so it does **not** recur.

Authority chain (highest wins): the user's current instruction → the input
dataset/CSV → the **PICS Master SOP** (`docs/PICS_Master_SOP_Codex_Operational_Edition.docx`)
→ the latest benchmark report → [`CODEX.md`](../CODEX.md) + the
[enrichment brief](codex_enrichment_brief.md). This file operationalises the
SOP's reading-comprehension checks that `evaluate.py` **cannot** see.

> The 22–23 report passed every mechanical check (0 Google-News redirects, 0
> tracking params, 0 duplicate URLs, clean structure, correct disclaimer) and
> still contained the problems below. **The score cannot see a junk source, a
> mismatched author, or an unsupported claim — only reading the article can.**

---

## 1. Source credibility — never cite an aggregator, auto-translation, or random local repost
*SOP §5.4 (exclude syndicated copies / non-Libya navigation), §24 (verify the outlet at article level).*

For **every** source ask: *is this the outlet that actually reported the story?*
Reject and replace these, even when the fact is true:

- **Content aggregators** — `msn.com`, `news.yahoo.*`, `bing.com/news`, `ground.news`.
  They re-host someone else's article. Cite the original (e.g. AGBI, not the MSN
  copy of AGBI).
- **Auto-translation / syndication portals** — `vietnam.vn`, any `*/ar/` machine
  translation of a foreign-language slug, content farms. These are not newsrooms.
- **Unrelated local papers running a wire** — `mlive.com` (Michigan),
  `daily-sun.com` (Bangladesh), etc. **Red flag: the headline does not even
  mention Libya.** Use the originating wire (**AP / Reuters / AFP / ANSA**), a
  Libyan outlet (Libya Herald, Libya Observer, Libya Review, LANA, Al Wasat), or
  a regional one (Arab News, Asharq Al-Awsat, Al Jazeera).

**22–23 examples:** `#46` Italy migrant-centre sourced *only* to **Vietnam.vn**;
`#41` boat tragedy (51 dead) sourced *only* to **MLive**; `#54` oil record paired
with an **MSN** copy of AGBI; `#40` Najim sentence on **daily-sun.com**.

> The fact can be 100% real and the source still wrong. The boat capsize is a
> genuine **AP** story; cite AP, not a Michigan paper.

## 2. The displayed source = the linked outlet, and the named person = the article's person
*SOP §11.3 (link-to-headline verification), §9 (role labels).*

- The outlet name after the en dash **must be the outlet of the URL** attached to it.
- If the headline sentence names an outlet or author, it must be the one you linked.
- `[Role]` brackets are **only** for a named **person's** verified role —
  **never** on a website, a wire agency-as-publisher, or a category.

**22–23 examples:**
- `#62` — *"[Analyst] OilPrice.com argued … – Anas Alhajji"* linking Anas
  Alhajji's **Substack**. Three errors in one bullet: a bracket-role on a
  website; the sentence names "OilPrice.com"; the real author/source is
  **Anas Alhajji**. → *"[Energy economist] Anas Alhajji argues … – Anas Alhajji."*
- `#60` — *"**Sada** reports that factory generators…"* but the only link is
  **New Arab** (alaraby.co.uk). → drop "Sada", attribute to New Arab.

## 3. Every entity named in the headline needs a supporting link
*SOP §7.2 (do not combine different actors), §2 (completeness before compression).*

If the headline names N organisations / municipalities / people, **each one must
have a link that supports it.** If you only have one source, name only what it
covers — or split into separate bullets, or pull the missing outlets from the CSV.

**22–23 examples:**
- `#39` — *"Amnesty **and the International Commission of Jurists** condemn EU
  cooperation with Libya **and Tunisia**"* — both links are **Amnesty / Libya**
  only; the ICJ (and the Tunisia scope) had **no** supporting source. → give ICJ
  its own bullet with its own link (as the gold does).
- `#15` — *"**Kufra, Abyar and Green Mountain** municipalities endorse…"* — the
  single Al Menassa link is **only about Kufra**. → add the other two articles
  (they were in the data) or narrow the headline.

## 4. Do not generalise one named person into a vague group
*SOP §9 (no vague/category labels); brief Pass 4 (specificity).*

If the article is one person's statement, **name the person and role**. "Political
figures / critics / officials / commentators" is only for a genuine multi-source
aggregate.

**22–23 example:** `#28` *"Libyan political figures call for reviewing diplomatic
representation…"* when the article is one named person (**Al-Thulthi**) on a
specific point. → *"[<role>] Al-Thulthi questions …"*

## 5. Same-event consolidation cuts BOTH ways — do not under-source the lead story
*SOP §11.1 (list every outlet that covered the same event), §7.2.*

The fix for **over-merging** (different events in one bullet) is **not** to drop
same-event outlets — it is to keep every outlet that covers the **same** event in
one bullet and split only the genuinely different events. After de-merging,
**re-attach every CSV outlet that covers the same event.**

**22–23 example:** `#54` the oil-output record — the single biggest economic
story of the window — shipped with only **MSN + AGBI**, when ~17 outlets covered
it. A flagship story with 2 sources (one an aggregator) is under-sourced.

> Watch the `evaluate.py` "multi-source/dedup" line: ~0.10–0.15 means you
> under-merged. Target ≈ 0.20–0.30. (See [`CODEX.md`](../CODEX.md) quality bar.)

## 6. Respect the publication-date window — even for wire stories
*SOP §5.2 (coverage-window test), §25 (date-verification protocol).*

Use the **article's publication date**. An older event qualifies only if the
cited article was **published inside the window** (a real follow-up with new
facts), not because the topic is recent.

**22–23 example:** `#41` boat capsize — the AP wire broke **~19 June**; a 22–23
report citing that wire is likely **out of window.** (The in-window angle is the
`#42` Tobruk body-recovery follow-up — cite that instead.)

## 7. Verify roles, institutions, committee names and numbers against the article
*SOP §8.4 (consistent names/roles), §24 (article-level verification); brief rule 10.*

- `#30` — *"4+4 committee"*: the well-known body is the **6+6** committee —
  confirm which the article means before printing.
- `#68` — *"Libyan **chambers** discuss…"* but the sources say the **GNU
  (government)** discusses it. Confirm the actor.
- Names/numbers must appear in the source verbatim (e.g. Najim **"seven years and
  four months"** — confirmed correct; never round or invent — see brief rule 10).

---

## Pre-delivery checklist (run on the finished DOCX, reading each link)

- [ ] **Every source is a real newsroom** for that story — no MSN/Yahoo/Bing
      aggregators, no `*.vn`/auto-translation, no off-topic local paper running a
      wire. If it's a wire, cite the wire (AP/Reuters/AFP/ANSA).
- [ ] **Displayed outlet name == the linked URL's outlet** for every source.
- [ ] **No `[Role]` bracket on a website, agency-as-publisher, or category** —
      persons only, role verified.
- [ ] **Every org/municipality/person named in a headline has a link** that
      supports it; otherwise narrowed or split.
- [ ] **No specific named person flattened into "officials/figures/critics".**
- [ ] **Flagship stories carry all same-event outlets** from the CSV, not 1–2.
- [ ] **Each source's publication date is inside the window** (follow-ups OK).
- [ ] **Roles, institutions, committee names, numbers** verified against the article.

---

## What the 22–23 OPERATIONAL report got RIGHT — keep doing this

- Resolved **all** Google-News redirects to direct article URLs; stripped
  tracking params (`utm_*`, `codex_audit=`).
- Removed the generated subtitle; correct title, section order and exact PICS
  disclaimer.
- Split the over-merged UN bullet into separate UN bullets (UN protection rule).
- Standardised names (Dbeibah) and used real `[Role] Name` labels in place of the
  draft's generic `[Media Analysis]`/`[Court Ruling]` category tags.
- Factual specifics correct (Najim = seven years and four months).

These are the SOP working as intended. The items in §1–§7 are the remaining
reading-only gaps — close them in the self-audit (see `CODEX.md` **Pass 5**).
