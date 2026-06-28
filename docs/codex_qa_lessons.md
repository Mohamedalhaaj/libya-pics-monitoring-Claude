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

> **⚠️ The #1 recurring miss (confirmed on the 22–23 re-run).** After this
> guidance first shipped, the redo fixed **every** junk source (MSN, Vietnam.vn,
> MLive, daily-sun all gone) and correctly split the multi-municipality bullet —
> but it **still** shipped bullets whose *sentence* names something the *cited
> link does not support*: an org that is named but not cited (ICJ), a vague
> "political figures" hiding one named person, an outlet named in the sentence
> that isn't the linked one ("Sada"), and a wrong actor ("chambers" vs the GNU).
> **Choosing the right outlet is only HALF the job. Every named entity AND every
> scope word in the bullet must be backed by one of its cited links** (§2–§3).
> Run that check as hard as the junk-source check.

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
  **Anas Alhajji**. → *"[Analyst] Anas Alhajji argues … – Anas Alhajji."*
  **(FIXED on the re-run.)**
- `#60` — *"**Sada** reports that factory generators…"* but the only link is
  **New Arab** (alaraby.co.uk). → drop "Sada", attribute to New Arab.
  **(RECURRED on the re-run — the source was fine, the sentence still named the
  wrong outlet. Don't name an outlet in the sentence that isn't the linked one.)**

## 3. Every CLAIM in the headline must be supported by a cited link — the #1 recurring miss
*SOP §7.2 (do not combine different actors), §2 (completeness), §11.3 (link↔headline).*

Read your finished bullet and underline **every named entity** (org, person,
institution, place) **and every scope word** ("and Tunisia", "and the ICJ",
"chambers", "several", "political figures"). **Each one must be backed by one of
the bullet's cited links.** If a claim isn't supported by a cited article:
1. **Add the source** — it is often already in the CSV (search it before deleting),
2. or **split** the bullet so each actor/claim sits with its own source,
3. or **narrow the sentence** to exactly what the cited links say.

Never name a second organisation, an extra country, or a vaguer/larger group than
your links actually support.

**22–23 examples:**
- `#41`/`#39` — *"Amnesty **and the International Commission of Jurists** condemn
  EU cooperation with Libya **and Tunisia**"* links **only Amnesty** (Rai Al-Youm,
  Le Monde). **RECURRED on the re-run.** The ICJ statement — which is exactly what
  adds "Tunisia" — **exists in the CSV** ("ICJ calls for an end to abusive
  migration externalization practices in Libya and Tunisia") but was **not cited**.
  → split into two bullets (Amnesty/Libya · ICJ/Libya & Tunisia) **or** cite the
  ICJ article. *(Two organisations = two statements; don't merge them under one.)*
- `#15` — *"**Kufra, Abyar and Green Mountain** municipalities endorse…"* with one
  Kufra link. → **FIXED on the re-run**: split into three bullets, each with its
  own Al Menassa article. **This is the model fix — do the same for #41.**
- `#68` — *"Libyan **chambers** discuss opening an Arab Academy branch"* but the
  cited RNA article says the **Government of National Unity (GNU)** does.
  **RECURRED.** → name the actor the source names.

## 4. Do not generalise one named person into a vague group
*SOP §9 (no vague/category labels); brief Pass 4 (specificity).*

If the article is one person's statement, **name the person and role**. "Political
figures / critics / officials / commentators" is only for a genuine multi-source
aggregate.

**22–23 example:** `#28`/`#30` *"Libyan political figures call for reviewing
diplomatic representation…"* when the article is one named person (**Al-Thulthi**,
questioning ambassador al-Sani). → *"[<role>] Al-Thulthi questions …"*
**RECURRED on the re-run** — "political figures / critics / officials" is a smell:
open the link and name who actually spoke.

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
*SOP §8.4 (consistent names/roles), §9 (role labels), §24 (verification); brief rule 10.*

- **`[Analyst]` is NOT a default label — it is the #2 recurring miss.** A `[Role]`
  bracket must be the person's **actual, verified role**, not a catch-all for
  "someone who commented." Look the person up.
  - `#10` — Mohamed Baiou is labelled **[Analyst]** but he is a **journalist /
    political writer** (former head of the Libyan Media Institution, ex-Gaddafi-era
    spokesman). Calling a partisan media figure "[Analyst]" is both wrong and lends
    false neutrality. → use his real role (e.g. `[Journalist]`/`[Writer]`) or, for a
    pure columnist/commentator, **no bracket** — never invent "[Analyst]".
  - The same caution applies to every commented opinion (#21, #22, #24, #31): verify
    each speaker's role; if you cannot, omit the bracket rather than guess "[Analyst]".
- `#30` — *"4+4 committee"*: the well-known body is the **6+6** committee —
  confirm which the article means before printing.
- `#68` — *"Libyan **chambers** discuss…"* but the sources say the **GNU
  (government)** discusses it. Confirm the actor.
- Names/numbers must appear in the source verbatim (e.g. Najim **"seven years and
  four months"** — confirmed correct; never round or invent — see brief rule 10).

## 8. Headlines lead with the FACT — never "Outlet reports/cites that…"
*SOP §8.1 (lead with the new fact, action or statement).*

The outlet name belongs **only** in the source line after the en dash — never inside
the headline as the subject. Do not write "Al Shahed cites…", "Sada reports…",
"Reports describe…", "Coverage of … warns…", "Libya is reported to be…", "market
coverage putting…". State the news directly; the link/source line carries the
attribution.
- WRONG `#02` — *"**Al Shahed cites** UNSMIL saying Structured Dialogue outputs
  reflect proposals…"* → *"UNSMIL says Structured Dialogue outputs reflect the
  proposals of thousands of Libyans. – Al Shahed (Arabic)."*
- Same fix for `#44` ("Reports describe…"), `#46` ("Local reporting warns…"),
  `#51` ("Coverage of family crimes warns…"), `#54` ("…market coverage putting…"),
  `#55` ("Libya is reported to be…"), `#60` ("Sada reports…"), `#90` ("…chess
  coverage highlights…"). **Recurred across 8 bullets on the 22–23 re-run.**
- (Note: `#02` is also the **same UNSMIL statement** as `#01` written twice — once
  in English, once in Arabic. Merge into one bullet citing both, per Pass 3.)

## 9. Analysis / Report / Opinion / Feature items belong in the Varieties section
*SOP §13 (Varieties content-type prefixes), §10 (classification).*

The `Analysis |`, `Report |`, `Opinion |`, `Feature |`, `Think Tank |`, `Podcast |`
and `Documentary |` prefixes are a **Varieties** device. Place such items under
**Varieties**, not scattered through the news sections — and add the short neutral
summary paragraph the SOP asks for beneath substantive analysis/feature items.
- `#19`, `#20` (*Analysis |*) sit in **Politics**; `#73` (*Report |*), `#74`
  (*Opinion |*) in **Economy**; `#80` (*Report |*) in **Environment**. → move to
  Varieties. (A plain straight-news item should not carry an Analysis/Report prefix
  at all — drop the prefix or reclassify.)

---

## Pre-delivery checklist (run on the finished DOCX, reading each link)

- [ ] **COMPLETENESS: bullet count ≈ the number of distinct in-window stories in the
      data** — every distinct Libya story is present, including minor/routine ones
      (ministry meetings, local councils, court cases, sports, op-eds). A draft far
      below the distinct-story count dropped real coverage. (Padding = repeats/filler
      only; never a real story. See CODEX.md "Completeness mandate".)
- [ ] **Every source is a real newsroom** for that story — no MSN/Yahoo/Bing
      aggregators, no `*.vn`/auto-translation, no off-topic local paper running a
      wire. If it's a wire, cite the wire (AP/Reuters/AFP/ANSA).
- [ ] **Displayed outlet name == the linked URL's outlet** for every source.
- [ ] **No `[Role]` bracket on a website, agency-as-publisher, or category** —
      persons only, role verified. **Never default to `[Analyst]`** — use the real
      role or no bracket (e.g. Mohamed Baiou = journalist, not analyst).
- [ ] **No headline starts with the outlet** ("Al Shahed cites…", "Sada reports…",
      "Coverage of … warns…") — lead with the fact; the outlet goes after the en dash.
- [ ] **Analysis/Report/Opinion/Feature items are in the Varieties section**, not in
      Politics/Economy/Environment, and carry a short neutral summary.
- [ ] **Underline every named entity AND scope word in each bullet** (org, person,
      place, "and Tunisia", "and the ICJ", "chambers", "several") — **each is backed
      by a cited link.** If not: add the source (check the CSV), split, or narrow.
- [ ] **Two organisations/statements = two bullets** (don't fuse Amnesty + ICJ).
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

These are the SOP working as intended. The items in §1–§9 are the remaining
reading-only gaps — close them in the self-audit (see `CODEX.md` **Pass 5**).
