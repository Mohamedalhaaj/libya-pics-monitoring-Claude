# PICS "Libya News Headlines" — exact format spec (from the 20 gold samples)

Derived by deep formatting + hyperlink extraction of all `samples/2026*.docx`
(1 June → 29 June, the human UNSMIL/PICS reports). This is the authoritative
"do it exactly as the samples" reference. Every detail below is verified across
the corpus. Pairs with `codex_enrichment_brief.md` (editorial rules) and
`codex_qa_lessons.md` (reading-only QA). Where this file and the brief disagree,
**this file wins on FORMAT**, the brief wins on editorial judgement.

---

## 1. Document-level format

| element | exact rule (from samples) |
|---|---|
| **Title** | `Libya News Headlines – {date}` — **centred, bold, Calibri**. Dash = EN DASH `–` (U+2013) with a space each side. Date = `D Month` (e.g. `9 June`) or, for a multi-day window, `D-D Month` (e.g. `25-28 June`). No year. No leading zero on the day. |
| **Body font** | Calibri **12pt** for bullets. |
| **Section headers** | font **Impact, 14pt** (NOT bold Calibri, NOT a Word "Heading" style). One blank line above each. |
| **Subsection / cluster headers** | **bold Calibri**, normal size. |
| **Bullets** | plain paragraphs (style is inconsistent in gold — "Normal" or "List Paragraph"; either is fine). |
| **Disclaimer** | a full-width rule line of hyphens, then the DISCLAIMER paragraph in *italic* Calibri (text in §5). |

---

## 2. Section order (strict) — 8 sections

```
United Nations
Politics
Military & Security
Human Rights & Rule of Law
Economy
Environment
Regional & International
Varieties
```

- **Omit a section only if it has no items.** United Nations is absent only on a
  genuinely no-UN-news day (seen once: 1 June). Environment is dropped on quiet
  days (e.g. 5-7 Jun, 25-28 Jun).
- Each section header appears **at most once**.

> **Social Media — OUT OF SCOPE (excluded by decision).** The recent gold reports
> (22 Jun onward) add a **Social Media** section (Impact header, right after United
> Nations) holding **Facebook**-sourced items (Raseen Media, Al Masar, Fawasel,
> Libya Press). **We do NOT produce this section** — our pipeline doesn't scrape
> social accounts yet. Do not add it to our reports or treat its absence as a
> defect. Revisit only if/when a social-media collection pass is built.

---

## 3. Bullet format (the line-level spec)

```
{English headline} – {Outlet}[ (Arabic)] / {Outlet2}[ (Arabic)] / …
```

Rules, all verified:
1. **NO terminal period on the headline.** Gold = **0%** of bullets end the
   headline with `.` (checked across 4 recent reports, 0/416). A headline is a
   headline, not a sentence. *(Our reports currently end 96–98% with a period —
   this is the #1 format defect; strip it.)*
2. **Separator** between headline and sources = ` – ` (space, EN DASH, space).
3. **Each outlet name is a hyperlink** to that outlet's **specific article URL**.
   A gold report has 80–250 such links. Same article URL never appears twice.
4. **Multiple outlets** joined by ` / `. English outlets listed first where natural.
5. **Language tag:** append ` (Arabic)` to an Arabic-language outlet **only**.
   **English outlets get NO tag** (`Reuters`, never `Reuters (English)`).
6. **Outlet names always in Latin script** — romanise any Arabic outlet name.
7. **One outlet listed at most once per bullet.**
8. **Role/title prefix** when a bullet reports a named person's words/act:
   `[Role] Surname: {quote/statement}` (colon) — OR — `[Role] Surname {verb}…`
   (no colon, when describing an action). Role-prefixed bullets ≈ **15–16%** of
   the report. Do **not** repeat the surname after the prefix
   (✗ `[PM] Dbeibah: dbeibah announces…`).

---

## 4. Varieties section — special format

Varieties is NOT ordinary bullets. Each item is a **bold tagged headline** then an
**italic 11pt Calibri summary paragraph** (1 short paragraph, a few sentences):

```
Analysis | {headline} – {Source}[ (Arabic)]          ← bold
{2–4 sentence italic summary of the piece}            ← italic, 11pt
```

- **Tags seen (frequency):** `Analysis |` (61), `Opinion |` (20), `Feature |`
  (16), `Report |` (2). Use ` | ` (space-pipe-space). Analysis dominates.
- The whole "Tag | headline" is bold; the ` – ` and ` (Arabic)` are not.
- Sports / culture short items can also appear in Varieties as ordinary bullets,
  but the flagship Varieties content is the tagged Analysis/Opinion/Feature pieces
  **with the italic summary** — our reports omit the summary; add it.

---

## 5. Disclaimer (verbatim, italic)

```
DISCLAIMER: The Media Monitoring Reviews are compiled by the Public Information &
Communications Section (PICS) of UNSMIL. These reports do not reflect the views or
official positions of UNSMIL, nor does UNSMIL vouch for the accuracy of the
information contained therein. If you have any questions/suggestions, please
contact unsmil-info-libya@un.org.
```
(Preceded by a hyphen rule line. Casing varies slightly across samples — "reports"
vs "Reports"; either is acceptable.)

---

## 6. Canonical glossary — match the gold's spellings

### Person names (gold's preferred form → forms WE got wrong)
| use this | NOT |
|---|---|
| **Menfi** (PC President) | Al-Manfi, Al-Menfi |
| **Baour** (Acting FM) | Al-Baour |
| **Koni** (PC member, Musa al-Koni) | Al-Koni |
| **Agila Saleh** (HoR Speaker) | Aguila / Aqila / Ageela / Aqeela |
| **Dbeibah** (PM) | Dbeibeh |
| Tetteh, Koury, Takala, Saddam Haftar, Khaled Haftar, Hammad, Boulos, Gharyani, Shakshak, Hwaij | — (these we got right) |

### Role tags (canonical bracket vocabulary, by frequency)
`[HoR Member]` · `[Acting FM]`/`[AFM]` · `[HCS Member]`/`[SD Member]` ·
`[PC President]` · `[HCS President]` · `[PM]` · `[Structured Dialogue Member]` ·
`[SRSG]` / `[DSRSG]` · `[HoR-appointed]` / `[HoR-appointed PM]` / `[HoR-appointed FM]` ·
`[CoS]` · `[HoR Speaker]` · `[PC Member]` · `[MoI]` · `[Mufti]`/`[Grand Mufti]` ·
`[EU Ambassador]` · `[Defence Undersecretary]` · `[LNA]` · `[Transport Minister]`.
Abbreviations: **HoR** House of Representatives, **HCS** High Council of State,
**PC** Presidential Council, **SD** Structured Dialogue, **CoS** Chief of Staff,
**MoI** Ministry of Interior, **FM** Foreign Minister, **SRSG/DSRSG** the UN envoys.
(Prefer these short forms over long ad-hoc ones, e.g. use `[US Adviser]` style
sparingly; gold used `[U.S. Senior Advisor for Arab and African Affairs]` for Boulos.)

### Subsection headers actually used (reuse these names)
- **United Nations:** named meeting clusters (`SRSG Tetteh's meetings in Tunis`,
  `DSRSG Stephanie Koury meetings in Benghazi`, `DSRSG … interview with Al Masar TV`),
  `Other UN News`.
- **Politics:** `Structured Dialogue`, `Political Process`, `Support for US proposal`,
  event clusters (`Cairo hosts talks between USA, Türkiye, Egypt and Saudi Arabia`),
  `Other political news`.
- **Military & Security:** `Combating crime`, `Other security news`.
- **Human Rights & Rule of Law:** `Migration`, `Rule of Law`, `Other Human Rights`.
- **Economy:** `Banking`, `Energy`, `Reconstruction and infrastructure`, `Other economic news`.
- **Environment:** event clusters (`Floods in southwestern regions`), `Other environmental news`.
- Subsection headers are a MIX of (a) standard thematic ones above and (b) named
  **event clusters** for a running story.

---

## 7. Concrete defects found in OUR last reports (25-28, 28-29, 29-30)

Measured against the gold, in priority order:

1. **Terminal periods** — every bullet ends with `.` (96–98%); gold = 0%. Strip.
2. *(Social Media section — intentionally excluded, see §2; not a defect for us.)*
3. **Varieties missing the italic summary paragraph** and inconsistent `Tag |`
   bolding; gold has bold `Analysis |/Opinion |/Feature |` + a summary each.
4. **Name forms wrong:** Al-Baour→**Baour**, Al-Koni→**Koni**, Al-Manfi→**Menfi**,
   Ageela/Aguila→**Agila Saleh** (counts: 28-29 had Al-Baour ×6, Al-Koni ×9,
   Ageela/Aguila ×5; 29-30 had Al-Koni ×9, Al-Manfi ×5, Ageela/Aguila ×9).
5. **Doubled role-prefix leads** — `[PM] Dbeibah: dbeibah announces…` (mechanical
   artifact; the name is repeated). ~10–15 per report.
6. **Name mistranslations** (28-29): MP `النعاس` → "Sleepiness"; `هدية` → "Gift".
   Preserve transliterated surnames; never translate a name as a common noun.
7. **Cross-section duplication** of the lead story (intel-chief story spread over
   Politics + Military + Health, ~27 bullets in 29-30).
8. **Miscategorization** — flagship energy story in Politics; sports in Energy.
9. **Junk/aggregator sources** — but see §10: the human KEEPS minor aggregators;
   only true SEO-spam/irrelevant get cut. Don't over-strip.
10. **Bullet volume vs the human:** gold 25-28 = **110** bullets; our 25-28 = 333;
    our 28-29 = 247; 29-30 = 219. The completeness mandate intentionally exceeds
    the human, but ≥2–3× signals residual under-merging/over-inclusion, not just
    completeness — most of the excess is the same story un-merged across sections
    (defects 7–8), which is NOT what the mandate asks for.

---

## 8. Collection implications

- *(Social-media collection pass — deferred; the Social Media section is out of
  scope until that pass exists. See §2.)*
- Gold cites a few items we don't reach (audit-firm/frozen-assets via Al Menassa,
  Anatolian Eagle via Libya Update EN, Athens-Greece via Al Menassa) — shallow
  custom-CMS feeds; deepen those source listings (see pics-codex-handoff memory).

---

## 9. SOP changes to fold in (proposed)

Into `codex_enrichment_brief.md`: add (a) **no terminal period** rule; (b)
**Varieties tagged format** with italic summary; (c) the **canonical name +
role-tag glossary** (§6); (d) **body=Calibri 12pt, section header=Impact 14pt,
title centred bold**. *(Social Media section deliberately NOT added — out of scope.)*
Into `CODEX.md` self-audit: add a **Pass 6 — format conformance** that checks the
no-period rule, the 8-section set (no Social Media), Varieties tag+summary, and the
name glossary.
Into the build script / `utils/exports.py`: stop appending `.` to headlines; render
section headers in Impact 14pt; emit the Varieties summary paragraphs.

---

## 10. Calibration from the 30 June MANUAL report (human, tracked-changes edit of the Codex 29-30 draft)

The human built 30 June by editing the Codex draft with Track Changes (≈1085 ins,
4007 del). The accepted/final version **validates every rule in §§1-6** — and adds
three calibrations:

1. **Selectivity & merge level.** Human = **141 bullets** vs our Codex 29-30 = **220**
   for the same window. The cut came from (a) **harder multi-source merging** — one
   event = one bullet citing 6-30 outlets (e.g. the CBL-leak bullet cites 6, the Eni
   gas bullet 30, the intel-dispute bullets 8), and (b) dropping only the *most* minor
   items. So "completeness" in practice ≈ **merge aggressively, keep distinct stories,
   land ~140 — NOT 220 un-merged**. Our over-count is under-merging, not extra coverage.
2. **Source-keeping is LENIENT — don't over-strip (corrects the old Pass-5).** The
   human KEPT aggregators we had flagged for deletion: **Breakingthenews.net,
   Demócrata, Mirage News**, and even **25h.app / Businessfront / Inspenet** inside
   the 30-outlet Eni merge. They removed only **SEO-spam / clickbait / irrelevant**
   (Travel And Tour World, eTurboNews, tovima.com, facilitiesmanagement-now). Rule:
   drop a source only if it's SEO-spam, auto-translation, or not actually about Libya;
   a minor-but-real outlet is fine, **especially as one of several** in a merged bullet.
   Never leave a story sourced ONLY to junk when a better source exists — but you need
   not purge every aggregator.
3. **Subsection headers are named after the specific event/meeting.** The human writes
   very descriptive cluster headers: `SRSG Tetteh and DSRSG Koury meeting with Acting
   FM Baour`, `DSRSGs Koury and Richardson meet with Head of the Audit Bureau`, `US
   Secretary of State Marco Rubio meets with Saddam Haftar in Washington`, `Senior US
   Advisor on African and Arab Affairs, Massad Boulos interview`, `Dispute over the
   Presidential Council's selection of the Head of General Intelligence Service`,
   `Indian Delegation visits Libya`. Plus the standard thematic ones (Banking, Energy,
   Migration, Rule of Law, Crime, Other X news).

**What the human's edit confirms we get wrong in Codex** (all fixed in the manual):
- Consolidated the intelligence story into ONE Politics cluster (Codex spread it over
  3 sections / 27 bullets) — exactly the CODEX_FIX recommendation.
- Recategorised (Eni gas → Energy; sports dropped, not in Energy).
- Canonical names throughout: **Menfi, Agila Saleh, Baour, Mlegta** (Codex had
  Al-Manfi / Aguila / Al-Baour).
- Stripped the terminal periods.

Name nuance: the human writes **"Al Koni"** (with space) for the PC deputy — accept
either `Al Koni` or `Koni`. Minor unfinished bits in the draft (a residual duplicate
"Diplomacy and foreign relations" block still carrying periods) are cleanup-in-progress,
not format rules.
