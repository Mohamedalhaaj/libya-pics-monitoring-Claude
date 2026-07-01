# Codex enrichment brief — build the PICS report from the raw CSV

Use this with the raw data in `output/libya_media_headlines.csv` to produce the
UNSMIL/PICS **“Libya News Headlines”** report. This is the editorial step the
pipeline normally hands to the Claude API (`utils/enrich.py`); the brief lets
another model do the same job. Reference the gold human reports in `samples/*.docx`
for tone and layout.

> **Also read before/while writing:**
> - [`PICS_REPORT_FORMAT_SPEC.md`](PICS_REPORT_FORMAT_SPEC.md) — the EXACT format
>   from the 20 gold samples (no-period headlines, Impact-14pt section headers,
>   Varieties `Analysis|`+italic-summary, fonts, selectivity/source calibration).
> - [`PICS_NAMES_AND_TITLES.md`](PICS_NAMES_AND_TITLES.md) — canonical name spellings
>   + role-tag glossary (Menfi, Baour, Agila Saleh, Dbeibah, Mlegta…). Use these.
> - [`codex_qa_lessons.md`](codex_qa_lessons.md) — link-fidelity, source-credibility
>   and attribution rules from QA review (displayed outlet = linked URL, every named
>   entity needs a supporting link, don't under-source the flagship story; **drop only
>   SEO-spam / auto-translation / non-Libya sources — minor real aggregators are OK,
>   esp. as one of several in a merged bullet**). These are the reading-only checks
>   `evaluate.py` can't catch; enforce them in the `CODEX.md` self-audit (Pass 5–6).
>   Authority: `PICS_Master_SOP_Codex_Operational_Edition.docx`.

## Editor's corrections — CONTROLLING (from the PICS editor, applies every time)

Direct feedback from the human editor on real output. These override anything below.

1. **No `.` at the end of any headline.** (Also auto-stripped by
   `scripts/clean_report_docx.py`, but write them without it.)
2. **Categorise tightly; one story lives in ONE section.** Recurring failures: Boulos
   and Rubio scattered across many sections; Politics polluted with human-rights,
   economy, international, varieties and Syria items; Koni's PC denial filed under
   Health. Use the **section definitions** below; put a running story in a single
   named cluster in its best-fit section, never repeated across sections.
3. **Remove ALL football and sport** — no match previews, results, leagues,
   championships, federations. (Overrides the completeness mandate for sport.)
4. **Drop low-value individual commentators / pundits / activists.** Obscure online
   commentators', analysts' and activists' opinion takes (Alsaaa 24 runs many) are not
   stories — cut them. The editor removed `[Activist]` Shaaban and `[Analyst]` Shallouf
   entirely. `[Analyst]`/`[Activist]` is only for a substantive expert whose piece is
   worth keeping (and then it belongs in Varieties, not the news sections).
5. **`[Role] Surname:` (colon) is for an actual QUOTE/statement only.** If the bullet
   describes an action, use no colon: `[PM] Dbeibah directs …` not `[PM] Dbeibah:
   Dbeibah directs …`. Never repeat the surname after the tag. **Bracket EVERY named
   person** with their `[Role]` (at least the lead actor of the bullet); institutional
   actors ("The Public Prosecution", "UNSMIL", "NOC") get no bracket. Get the title
   from `PICS_NAMES_AND_TITLES.md`, or read the source if it's not listed.
6. **Window discipline + no day-to-day repeats — but KEEP flagship ongoing stories.**
   Include ONLY stories dated inside the window (no March / early-June leftovers). Skip
   ROUTINE/minor items that already ran in the previous day's report. **Do NOT drop the
   day's flagship stories** (e.g. the Rubio–Haftar Washington meeting, the Eni-Sabratha
   gas start-up) just because they appeared the day before — the editor keeps major
   ongoing stories. Cross-day dedup targets small repeats, not the lead news.
7. **Use our spellings** — `PICS_NAMES_AND_TITLES.md` (Menfi, Baour, Koni, Abani,
   Agila Saleh, Dbeibah, Mlegta, Sebha, Kufrah…). Note **Hwaij = `[HoR-appointed FM]`**
   for foreign/consular items (only `[Minister of Economy]` for GNU economy/trade items).
   `clean_report_docx.py` normalises the common spellings.
8. **Varieties: pull the article's FIRST PARAGRAPH** as the italic summary under each
   Analysis/Opinion/Feature item.
9. **Don't over-tag Varieties.** Only label a piece `Analysis |`/`Opinion |`/`Feature |`
   when it really is one; the text after the tag must be the **article's real
   headline**, not your own analysis. Plain news gets no tag and is not "analysis".
10. **United Nations section = the UN (UNSMIL, SRSG/DSRSG **and UN agencies: UNDP,
    UNHCR, UNICEF, IOM, WHO, World Bank…**) DOING/ saying something.** Recognise the
    agencies (they were pulled but miscategorised). A Libyan/other figure *commenting
    on* the UN or the US initiative is **Politics**, not United Nations.
11. **Remove routine weather** — daily forecasts ("today will be …", temperatures,
    humidity). Environment keeps only substantive items (floods, power-grid sabotage,
    water/agriculture policy, environmental damage), not the daily bulletin.

### Section definitions (use for routing — point 2)
- **United Nations** — actions/statements BY UN bodies & agencies (see point 10).
- **Politics** — institutions & governance, the US/Boulos & UN-initiative diplomacy
  and Libyan reactions to it, elections/constitution, government & municipal affairs,
  the intelligence-leadership dispute. (Rubio/Boulos/initiative items cluster here.)
- **Military & Security** — army/LNA, 5+5, security ops, crime, weapons, borders.
- **Human Rights & Rule of Law** — migration, prosecutions/detentions, judiciary,
  health, education, vulnerable groups, civil liberties.
- **Economy** — banking/CBL, oil & energy (NOC/Eni/Brega), markets, reconstruction
  & infrastructure, electricity.
- **Environment** — weather EVENTS, climate, agriculture, water (not daily forecasts).
- **Regional & International** — foreign relations, bilateral visits (India,
  Mauritania…), maritime/EEZ, regional security.
- **Varieties** — culture, heritage, society; tagged Analysis/Opinion/Feature pieces
  (with first-paragraph summary). NO sport.

## Input

`output/libya_media_headlines.csv` (UTF-8, columns):

| column | meaning |
|---|---|
| `source_name` | report-friendly outlet name (cite this verbatim) |
| `language` | `ar` or `en` — Arabic items must be translated |
| `title` | headline as published (Arabic or English) |
| `summary` | short dek / publish line, if any |
| `url` | article link |
| `published_at` | ISO timestamp (all rows are dated) |
| `section` | publisher's own category, if any (a hint, not authoritative) |

Coverage date = the span of `published_at` (current data: **18–21 June 2026**).
Title the report `Libya News Headlines – 18-21 June` (collapse a multi-day window
to a `D-D Month` range; a single day is just `D Month`).

## Editorial rules

1. **Relevance.** Keep only items about or directly affecting Libya. Drop generic
   regional/international items with no Libya link, and anything you cannot
   summarise accurately in English.
2. **Translate.** Render every Arabic headline as one clear, concise English
   sentence stating the news fact. Never start a bullet with the outlet name. No
   opinion or editorialising. Use the **canonical name spellings** in
   [`PICS_NAMES_AND_TITLES.md`](PICS_NAMES_AND_TITLES.md) — **Menfi** (not Al-Manfi),
   **Baour** (not Al-Baour), **Al Koni**, **Agila Saleh** (not Aguila/Ageela),
   **Dbeibah**, Tetteh, Koury, Takala, Haftar, Boulos, Mlegta. Never translate a
   person's name into a common noun (real failures: النعاس→"Sleepiness", هدية→"Gift").
3. **Deduplicate by EVENT, not by topic.** Merge several outlets into ONE bullet
   **only when they report the same specific event** (the same announcement,
   meeting, incident, or statement). Sources sharing a mere topic are NOT the
   same story: a UN Mission *launch* of dialogue meetings, a Mufti's *fatwa
   against* the Mission, an MP's *criticism* of the Mission, and an analyst's
   *commentary* are **four separate bullets**, even though all mention UNSMIL.
   Before attaching a second source, confirm its article is about the SAME event
   as the bullet — if not, give it its own bullet. When in doubt, split. (Each
   linked article must match the bullet; see rule 9.)
4. **Never drop UN coverage as a duplicate.** UN items (UNSMIL, SRSG/DSRSG
   Tetteh/Koury, Security Council, UN agencies, international mediation,
   humanitarian agencies) are kept even if repeated — but still split by event
   per rule 3: combine outlets only when they cover the *same* UN event, never
   lump different UN stories into one bullet.
4b. **One story = one bullet in the WHOLE report — including across languages and
   sections.** If the data has an English article and an Arabic article about the
   *same event* (e.g. a court sentence, a Dbeibeh meeting, an oil-output record),
   that is ONE bullet citing both, NOT an English bullet and an Arabic bullet. A
   story belongs in exactly one section (its best fit) — never repeat it in two
   sections. Before writing a bullet, check you haven't already covered that event
   elsewhere. (Real failure seen: the same prison sentence appeared as 3 bullets
   across Military and Human Rights; one Dbeibeh meeting as 3 bullets.)
5. **Attribution format.** End each bullet with ` – ` then the outlets joined by
   ` / `. **Every outlet name MUST be in Latin script** — if the data gives an
   outlet in Arabic (e.g. `شبكة تواصل الإخبارية`, `اليوم السابع`, `حفريات`),
   romanise it to its common English name (`Tawasul News`, `Youm7`, `Hafryat`)
   and append ` (Arabic)`. Never leave an Arabic outlet name in the report.
   Append ` (Arabic)` **only** to Arabic-language outlets (the `language` column
   is `ar`); **never tag English outlets** — write `Reuters`, not
   `Reuters (English)`. **List each outlet at most once per bullet** — never
   `Libya Observer / Libya Observer`. English outlets first where natural. Example:
   `At least 15 migrant bodies wash ashore in eastern Libya – Reuters / New Arab / Shafaq (Arabic)`
6. **Role/title prefixes (REQUIRED formatting).** Whenever a bullet reports a
   named person's statement, it MUST start with their role in square brackets,
   then the surname. Do not write a bare `Name: …` — add the bracketed role:
   - write `[HoR Member] Jehani: the General Command's support gives the US initiative momentum`
     — NOT `Al-Jehani: Support from the General Command…`
   - `[SRSG] Tetteh warns the Security Council that disinformation threatens stability`
   - `[Mufti] Gharyani issues a fatwa calling on Libyans to reject the outcomes`
   The gold report brackets a role on ~15% of bullets; match that. Use the
   **canonical tag** from [`PICS_NAMES_AND_TITLES.md`](PICS_NAMES_AND_TITLES.md)
   (`[HoR Member]`, `[PC President]`, `[Acting FM]`, `[HCS Member]`, `[SD Member]`,
   `[SRSG]`/`[DSRSG]`, `[PM]`, `[CoS]`, `[Mufti]`…). Don't repeat the surname after
   the tag (✗ `[PM] Dbeibah: dbeibah announces…`).
7. **One sentence per bullet, NO terminal period.** Factual, present tense where
   natural. A headline is a headline, not a sentence — the gold ends bullets with
   **no full stop** (0% across the corpus); `…in Libya – Reuters`, never
   `…in Libya. – Reuters`. (Our past drafts wrongly ended 96–98% with `.`.)
8. **No duplicate or filler bullets — but cover EVERY distinct story.** Every
   bullet is a distinct story appearing exactly once (zero duplicates). Do NOT emit
   vague placeholders ("A Libya-related report covered domestic developments");
   if you cannot state a specific fact, drop *that* item. But "padding" means
   *repeats and filler*, **not** a real but minor story. **Completeness mandate
   (standing user instruction, overrides the SOP's low-value-exclusion):** include
   **every distinct in-window Libya story in the data** — a single ministry meeting,
   a local council statement, a municipal project, a court case all get a bullet.
   **EXCEPT the editor's exclusions (controlling): NO sport/football, NO routine
   weather forecasts, NO obscure-commentator opinion pieces** (see Editor's
   corrections 3, 4, 11). The report must be exhaustive, only de-duplicated; a draft
   far below the number of distinct stories in the data has dropped real coverage.
   Exclude only non-stories: exact duplicates, homepages/tag pages, broken links,
   non-Libya items, raw social posts.
   **Calibration (vs the human's 30 June report): completeness = MERGE HARDER, not
   more bullets.** The human covered the same window in **~140 bullets** where our
   Codex draft had **~220** — the gap was under-merging, not extra coverage. One
   event = ONE bullet citing 6–30 outlets (e.g. a leak story cites 6, an oil project
   30). Land near the distinct-story count by merging every same-event restatement
   across the whole report, NOT by emitting the same story 3× across sections.
9. **Fidelity — each bullet must match the article(s) it cites.** Write what the
   cited article actually reports; the headline and its link must be about the
   SAME story. Never write a generic umbrella sentence over several stories
   ("International outlets linked Libya's oil sector…", "Officials reported
   investment activity…") — that reads fine but won't match any single link.
   Only merge sources (rule 3) when they cover the **same event**; if two
   articles differ, keep them as separate bullets. Do not attach a source/URL to
   a bullet unless that article supports the bullet's exact claim. Each cited
   outlet's URL must be the **specific article** for THIS story — never reuse one
   article's URL on another bullet (a link must appear on exactly one bullet).
10. **Faithfulness — never assert a specific the source doesn't state.** Every
   name, number, sentence length, charge, place, date and figure in a bullet must
   come from the cited article(s). Do NOT add a person, co-defendant, figure or
   number from memory or inference. Copy specifics verbatim from the source: if
   the article says "seven years and four months," the bullet says that — never
   "life imprisonment"; if it names "Najim," do not add "al-Kikli." When the
   source doesn't give a detail, leave it out rather than guess. (Real failure
   seen: a 7-year-and-4-month sentence for one official was written as "life
   imprisonment for al-Kikli and Najim, in absentia" — none of which the cited
   articles said.) When unsure of a name or number, re-open the link and read it.

## Structure

Use this exact main section order; omit a section only if it has no items. **Each
main section appears at most once** — group all of its bullets and subsections
under a single heading; never emit the same section heading twice.

1. United Nations
2. Politics
3. Military & Security
4. Human Rights & Rule of Law
5. Economy
6. Environment
7. Regional & International
8. Varieties

Group bullets under concise subsections. You MAY also add a short **event-specific
sub-header** to cluster a major running story, e.g.
`Libyan governing institutions agree to hold elections before February 2027`,
`HoR members show support for US proposal`, `Cairo hosts talks between USA, Türkiye, Egypt and Saudi Arabia`.

Suggested subsections (use what fits; add an "Other …" bucket as needed):

- **United Nations:** UNSMIL and political process; UN agencies and international support; Security Council and international mediation; Other UN news
- **Politics:** Political institutions and governance; Elections and constitutional process; Government and municipal affairs; Other political news
- **Military & Security:** Security and crime; Border and military affairs; Armed groups and security arrangements; Other security news
- **Human Rights & Rule of Law:** Migration and human trafficking; Justice and accountability; Health, children and vulnerable groups; Civil liberties and human rights; Other
- **Economy:** Banking and currency; Energy and fuel; Markets, labour and services; Infrastructure and reconstruction; Other economic news
- **Environment:** Weather, climate and agriculture; Water and environmental resources; Other
- **Regional & International:** Diplomacy and foreign relations; Regional security; Gaza/convoy-related Libya news; Other
- **Varieties:** Culture, heritage and society; Sports; Other. **Analysis/Opinion
  pieces use a special format:** a **bold** `Analysis | {headline} – {Source}` (tags:
  `Analysis |`, `Opinion |`, `Feature |`, `Report |`) **followed by a 2–4-sentence
  italic summary paragraph** of the piece. (See FORMAT_SPEC §4.)

Subsection headers are a mix of (a) standard thematic ones above and (b) **named
event clusters** for a running story — make them descriptive, e.g. `SRSG Tetteh and
DSRSG Koury meeting with Acting FM Baour`, `Dispute over the Presidential Council's
selection of the Head of General Intelligence Service`, `Indian Delegation visits Libya`.

## Output

A Word-style document (formatting per `PICS_REPORT_FORMAT_SPEC.md`):

- **Centred bold title** `Libya News Headlines – 18-21 June` (en-dash, `D Month` or
  `D-D Month`, no year, no leading zero).
- **Section headers in Impact 14pt** (the 8 sections — NO "Social Media" section,
  out of scope); **bold Calibri sub-headers**; **body Calibri 12pt**.
- Bulleted headlines with **NO terminal period**; **each source name is a hyperlink**
  to its specific article; ` (Arabic)` on Arabic outlets only.
- Varieties Analysis/Opinion/Feature items get the bold `Tag | …` line + italic summary.
- End with the mandatory disclaimer (italic):

> DISCLAIMER: The Media Monitoring Reviews are compiled by the Public Information
> & Communications Section (PICS) of UNSMIL. These Reports do not reflect the
> views or official positions of UNSMIL, nor does UNSMIL vouch for the accuracy
> of the information contained therein. If you have any questions/suggestions,
> please contact: unsmil-info-libya@un.org

## Self-check

Score the result with `python evaluate.py <your_report>.docx --gold samples/<a_gold>.docx`
(or against `~/Downloads/20260621_headlines.docx`, the human 18–21 June report).
Targets to match the gold corpus: ~100% English bullets, sections in canonical
order, every bullet attributed, zero boilerplate, dedup rate ≈ 0.24.
