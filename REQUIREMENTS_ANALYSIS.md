# CRS Calculator – Requirements Analysis

**Status (updated 2026-10-13):** APPROVED and IMPLEMENTED. The document was approved on 2026-10-12 with the rulings recorded in §10 (from `Plan_review2.md`). The implementation, tests (308 passing), Flask UI and Docker packaging are complete. **Pending:** end-to-end comparison with the official IRCC calculator and real-user feedback (§13).
**Originally drafted:** 2026-10-12 (as a pre-implementation draft; sections that changed since are marked *History* / *Updated*).

## 1. Purpose and scope

A web calculator that computes an Express Entry **Comprehensive Ranking System (CRS)** score (0–1,200) from a candidate's profile. Rules come strictly from IRCC pages; where IRCC does not say, the item is listed in §10 as an **open question** and nothing is assumed.

### 1.1 Sources (all canada.ca, all "date modified 2026-06-22")

| Id | Page | Used for |
|----|------|----------|
| S1 | [CRS criteria](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html) | Point tables (authoritative for scoring) |
| S2 | [Check your score](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score.html) (official calculator) | Questions, definitions, input options, eligibility notes for Canadian study |
| S3 | [Language test results](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/language-test.html) | Test-score → CLB/NCLC conversion tables, accepted tests |
| S4 | [Educational credential assessment](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/education-assessment.html) | ECA rules for foreign credentials |

Third-party conversion charts found on the web were **not** used (they disagree with each other and with S3).

### 1.2 Decisions already taken

- Python project; scoring core in a pure-Python package; **Flask** serves the page and a JSON endpoint; HTML/CSS/vanilla-JS frontend.
- Language input = **raw test scores** per test (IELTS, CELPIP, PTE Core, TEF Canada, TCF Canada), converted by a `language_mapper` before scoring (reviewer requirement).
- Point tables live in a **declarative data layer** (`tables.py` / JSON), not in conditionals (reviewer requirement).
- Unit tests with pytest; table-driven, every row of every table.
- *Updated:* packaged with Docker (gunicorn image, `docker-compose.yml`, `scripts/publish.sh`) and licensed MIT.

## 2. Outdated / changed information

| Item | Status | Handling |
|------|--------|----------|
| **Job-offer points** (200 for NOC Major Group 00; 50 for other skilled jobs) | Removed from CRS as of **2025-03-25** (S1, S2). Job offers still matter for *eligibility* (FST, FSW, some PNP streams). | **No job-offer input and no points.** UI shows a short notice. (See Q10 – the official tool still asks the question, but it yields no points.) |

No other content on S1–S4 is marked outdated. (S3 mentions a TEF Canada scoring change window of 2023-12-11 to 2024-05-06, since reverted; the current grid is what is documented in §6.)

## 3. Score structure

| Section | Content | Max with spouse | Max without spouse |
|---------|---------|-----------------|--------------------|
| A | Core / human capital (age, education, 1st language, 2nd language, Canadian work) | 460 | 500 |
| B | Spouse / common-law partner | 40 | 0 (n/a) |
| C | Skill transferability | 100 | 100 |
| D | Additional points | 600 | 600 |
| **Total** | | **1,200** | **1,200** |

Caps (S1): C = min(100, Education + Foreign work + Trade certificate), each of the three groups ≤ 50. D "Maximum 600 points" (sum of sibling 15 + French up to 50 + Canadian study up to 30 + PNP 600 = up to 695, so a cap of 600 must be applied – see Q9).

## 4. Marital status logic (reviewer requirement)

S2 asks: (1) marital status, (2i) is spouse/partner a Canadian citizen or PR?, (2ii) will spouse/partner come with you?

| # | State | Scored as | Section B | Sibling question also covers |
|---|-------|-----------|-----------|------------------------------|
| 1 | Never married/single, annulled, divorced/separated, legally separated, widowed | **Single** | skipped | applicant only |
| 2 | Married or common-law AND (spouse is citizen/PR **or** is *not* coming) | **Single** | skipped | applicant only |
| 3 | Married or common-law AND spouse is **accompanying** (not citizen/PR) | **Couple** | scored | applicant **and** spouse |

Source: S1 ("You will earn points as if you don't have a spouse or partner if they are not coming with you … or they are a Canadian citizen or permanent resident") and S2 Q1–2, Q10.
*Implementation:* the UI collects marital status → (if married/common-law) spouse citizen/PR → (if no) spouse accompanying. `models.resolve_couple()` turns this into one decision; the core receives a `Profile` whose `spouse` is set only when scored as a couple, and the result exposes `scored_as_couple`.

## 5. Point tables (transcribed from S1; "W" = with spouse/partner, "S" = without)

### 5.1 Age (integer age; S2 Q3: age on date invited, or current age if no invitation yet)

| Age | W | S | | Age | W | S |
|-----|---|---|-|-----|---|---|
| ≤17 | 0 | 0 | | 33 | 80 | 88 |
| 18 | 90 | 99 | | 34 | 75 | 83 |
| 19 | 95 | 105 | | 35 | 70 | 77 |
| 20–29 | 100 | 110 | | 36 | 65 | 72 |
| 30 | 95 | 105 | | 37 | 60 | 66 |
| 31 | 90 | 99 | | 38 | 55 | 61 |
| 32 | 85 | 94 | | 39 | 50 | 55 |
| | | | | 40 | 45 | 50 |
| | | | | 41 | 35 | 39 |
| | | | | 42 | 25 | 28 |
| | | | | 43 | 15 | 17 |
| | | | | 44 | 5 | 6 |
| | | | | ≥45 | 0 | 0 |

### 5.2 Level of education (A)

| Option | W | S |
|--------|---|---|
| Less than secondary | 0 | 0 |
| Secondary diploma | 28 | 30 |
| One-year post-secondary credential | 84 | 90 |
| Two-year post-secondary program | 91 | 98 |
| Bachelor's OR program of three or more years | 112 | 120 |
| Two or more credentials, one of them a program of three or more years | 119 | 128 |
| Master's OR entry-to-practice professional degree (medicine, veterinary medicine, dentistry, optometry, law, chiropractic medicine, pharmacy) | 126 | 135 |
| Doctoral (Ph.D.) | 140 | 150 |

Foreign credentials need an ECA from a designated organization, less than 5 years old (S4). To get points for 2+ credentials each needs an ECA; at least one must be a 3+-year program; order of completion is irrelevant (S4, S2 Q11 example: two bachelor's, or bachelor's + 2-year diploma ⇒ the "two or more" row).

### 5.3 First official language – per ability (reading, writing, speaking, listening)

| CLB/NCLC | W | S |
|----------|---|---|
| < 4 | 0 | 0 |
| 4 or 5 | 6 | 6 |
| 6 | 8 | 9 |
| 7 | 16 | 17 |
| 8 | 22 | 23 |
| 9 | 29 | 31 |
| ≥10 | 32 | 34 |

Max 4 × 32 = 128 (W) / 4 × 34 = 136 (S).

### 5.4 Second official language – per ability (same for W and S)

| CLB/NCLC | Points |
|----------|--------|
| ≤4 | 0 |
| 5 or 6 | 1 |
| 7 or 8 | 3 |
| ≥9 | 6 |

Max 22 (W) / 24 (S) – i.e. (ruling Q7 approved) the combined sum is capped at 22 when scored as couple, 24 when single (4 × 6 = 24; W cap 22 per S1 "up to a combined maximum of 22").

### 5.5 Canadian work experience (applicant)

| Years | W | S |
|-------|---|---|
| None / < 1 | 0 | 0 |
| 1 | 35 | 40 |
| 2 | 46 | 53 |
| 3 | 56 | 64 |
| 4 | 63 | 72 |
| ≥5 | 70 | 80 |

Definition (S1, S2 Q6i): paid, full-time (or equal part-time), skilled work (NOC TEER 0–3) in the last 10 years, working for a Canadian employer **while physically in Canada** (remote work from Canada counts).

### 5.6 Section B – spouse/partner (only when scored as couple)

Education:

| Option | Pts |
|--------|-----|
| Less than secondary | 0 |
| Secondary | 2 |
| One-year program | 6 |
| Two-year program | 7 |
| Bachelor's / 3+ year program | 8 |
| Two or more credentials (one ≥ 3 years) | 9 |
| Master's / professional degree | 10 |
| Doctoral | 10 |

First official language – per ability (max 5 × 4 = 20): CLB ≤4 → 0; 5–6 → 1; 7–8 → 3; ≥9 → 5.

Canadian work experience: <1 → 0; 1 → 5; 2 → 7; 3 → 8; 4 → 9; ≥5 → 10.

### 5.7 Section C – skill transferability (each group ≤ 50, total ≤ 100)

Let `lang1` = minimum CLB across the four first-official-language abilities; `cwe` = Canadian work years (0, 1, 2+); `fwe` = foreign work years (0, 1–2, 3+).

**Education group** (education tier from the applicant's education: tier "none" = secondary or less; tier "post-secondary" = one credential of ≥1 year – includes one-year, two-year and bachelor's; tier "high" = two-or-more with one ≥3 years, master's/professional, doctoral):

| Education tier | Lang CLB≥7, some ability <9 | Lang CLB≥9 all four | CWE = 1 yr | CWE ≥ 2 yrs |
|----------------|:--:|:--:|:--:|:--:|
| Secondary or less | 0 | 0 | 0 | 0 |
| Post-secondary ≥1 yr | 13 | 25 | 13 | 25 |
| High (2+ credentials with a 3-yr, Master's/professional, Doctoral) | 25 | 50 | 25 | 50 |

Education group = min(50, language component + Canadian-work component). CWE < 1 yr gives 0; lang CLB < 7 gives 0.

**Foreign work experience group:**

| Foreign years | Lang CLB≥7 (some <9) | Lang CLB≥9 all | CWE 1 yr | CWE ≥2 yrs |
|---------------|:--:|:--:|:--:|:--:|
| None | 0 | 0 | 0 | 0 |
| 1–2 | 13 | 25 | 13 | 25 |
| 3+ | 25 | 50 | 25 | 50 |

Foreign group = min(50, language component + Canadian-work component).

**Certificate of qualification (trades) group:** lang CLB ≥5 all four with at least one <7 → 25; CLB ≥7 all four → 50; otherwise 0. (Certificate must be from a Canadian province, territory or federal body – S2 Q7.)

### 5.8 Section D – additional points (cap 600)

| Factor | Points |
|--------|--------|
| Sibling in Canada (citizen/PR, ≥18, shares a parent with applicant or accompanying partner; blood, adoption or marriage/step) | 15 (flat, regardless of number of siblings) |
| French: NCLC ≥7 on all four French abilities **and** English CLB ≤4 (or no English test) | 25 |
| French: NCLC ≥7 on all four French abilities **and** English CLB ≥5 on all four | 50 |
| Canadian post-secondary credential of 1 or 2 years | 15 |
| Canadian post-secondary credential of 3+ years | 30 |
| Provincial/territorial nomination | 600 |

Canadian-study eligibility (S2 Q4b): ESL/FSL ≤ half the study; not under an award requiring return home; school physically in Canada (no foreign campuses; distance learning counts for education points but **not** for this bonus); full-time ≥ 8 months and physically present ≥ 8 months (exception: studies completed in whole or part between March 2020 and August 2022). Official tool maps the level to 15/30 via S2 Q4c: "secondary or less" → 0; "one- or two-year diploma/certificate" → 15; "degree/diploma/certificate of 3+ years, **or** a Master's, professional or doctoral degree of at least one academic year" → 30.

**UX note (reviewer):** A 3-year Canadian bachelor's scores in A (education 112/120) *and* D (30). The UI keeps these as two clearly separated questions ("highest education" in the Core/Spouse part; "Canadian study" in the Bonus part), with help text explaining that the second is a separate bonus.

## 6. Language test conversion (S3, "Federal Skilled Trades Program" grids – the only grids covering CLB 4–10)

Per ability the converter returns the highest CLB/NCLC whose lower bound is met. Values below the CLB/NCLC 4 bound → "<4".

**CELPIP-General:** score = CLB (1:1), 4…12, "10+" = ≥10.

**IELTS General Training**

| CLB | Speaking | Listening | Reading | Writing |
|-----|----------|-----------|---------|---------|
| 10+ | 7.5–9.0 | 8.5–9.0 | 8.0–9.0 | 7.5–9.0 |
| 9 | 7.0 | 8.0 | 7.0 | 7.0 |
| 8 | 6.5 | 7.5 | 6.5 | 6.5 |
| 7 | 6.0 | 6.0 | 6.0 | 6.0 |
| 6 | 5.5 | 5.5 | 5.0 | 5.5 |
| 5 | 5.0 | 5.0 | 4.0 | 5.0 |
| 4 | 4.0 | 4.5 | 3.5 | 4.0 |

**PTE Core**

| CLB | Speaking | Listening | Reading | Writing |
|-----|----------|-----------|---------|---------|
| 10+ | 89+ | 89+ | 88+ | 90+ |
| 9 | 84–88 | 82–88 | 78–87 | 88–89 |
| 8 | 76–83 | 71–81 | 69–77 | 79–87 |
| 7 | 68–75 | 60–70 | 60–68 | 69–78 |
| 6 | 59–67 | 50–59 | 51–59 | 60–68 |
| 5 | 51–58 | 39–49 | 42–50 | 51–59 |
| 4 | 42–50 | 28–38 | 33–41 | 41–50 |

**TEF Canada** – use the "Équivalence ancien score" column, **not** the "Score / 699" (S3 warning)

| NCLC | Speaking | Listening | Reading | Writing |
|------|----------|-----------|---------|---------|
| 10 | 393–450 | 316–360 | 263–300 | 393–450 |
| 9 | 371–392 | 298–315 | 248–262 | 371–392 |
| 8 | 349–370 | 280–297 | 233–247 | 349–370 |
| 7 | 310–348 | 249–279 | 207–232 | 310–348 |
| 6 | 271–309 | 217–248 | 181–206 | 271–309 |
| 5 | 226–270 | 181–216 | 151–180 | 226–270 |
| 4 | 181–225 | 145–180 | 121–150 | 181–225 |

**TCF Canada**

| NCLC | Speaking | Listening | Reading | Writing |
|------|----------|-----------|---------|---------|
| 10+ | 16–20 | 549–699 | 549–699 | 16–20 |
| 9 | 14–15 | 523–548 | 524–548 | 14–15 |
| 8 | 12–13 | 503–522 | 499–523 | 12–13 |
| 7 | 10–11 | 458–502 | 453–498 | 10–11 |
| 6 | 7–9 | 398–457 | 406–452 | 7–9 |
| 5 | 6 | 369–397 | 375–405 | 6 |
| 4 | 4–5 | 331–368 | 342–374 | 4–5 |

Cross-check: the FSW grids in S3 (CLB 7–10, and "CLB 5 and above" for second language) agree with the above for every cell compared (e.g. IELTS reading CLB5 = 4.0, PTE writing CLB 5 = 51, TCF listening CLB 5 = 369).

Test rules (S3/S2): approved tests are CELPIP-General, IELTS **General Training**, PTE **Core**, TEF Canada, TCF Canada; results must be < 2 years old; French results convert to NCLC, treated identically to CLB for CRS; IELTS One Skill Retake is not accepted.

## 7. Inputs the UI must collect

1. Marital status → spouse citizen/PR? → spouse accompanying? (see §4)
2. Age (integer)
3. Highest education (8 options, §5.2)
4. First-language test: test type + 4 scores; optional second-language test (different language than the first) + 4 scores
5. Canadian work years (0–5+), foreign work years (0, 1, 2, 3+)
6. Certificate of qualification (yes/no)
7. Provincial nomination (yes/no); sibling in Canada (yes/no)
8. Canadian study: a single dropdown (none / 1–2-year credential / 3+-year credential or Master's/professional/doctoral) with the S2 Q4b eligibility checklist shown as help text. *Updated:* the original draft listed a separate yes/no (4b) question; it was merged into this dropdown.
9. *If couple:* spouse education (8 options), spouse Canadian work years (0–5+), spouse language test + 4 scores. *Updated:* "not applicable" is the **"No test"** option of the test selector (0 points, ruling Q13).

Help texts: age is the age on the day of the Invitation to Apply (age accepted 17–100); language results must be less than 2 years old (help text only, ruling Q8); ECA validity is help text only (Q12).

Output: total + per-section breakdown (A, B, C, D) with line items (age, education, etc.). Line items are shown before the section cap; the section total is shown after the cap (C ≤ 100, D ≤ 600).

## 8. Architecture (as built)

```
src/crs/
  tables.py          declarative rule data (point grids, bands, caps, test conversions)  ← config layer
  engine.py          lookup_band(): generic band evaluation
  language_mapper.py raw test score → CLB/NCLC per ability, with score validation
  models.py          Profile, SpouseProfile, validation, resolve_couple()
  sections/          core.py, spouse.py, transferability.py, additional.py
  calculator.py      orchestrates, applies caps, returns breakdown (Score.to_dict())
  web/               app.py (GET /, POST /api/calculate), schema.py (JSON → Profile), templates/, static/
tests/               pytest, table-driven (test_language_mapper, core, spouse, transferability, additional, calculator, web)
Dockerfile, docker-compose.yml, scripts/publish.sh   packaging and Docker Hub publishing
```

*History:* the draft proposed JSON/YAML-loadable config; the implementation uses Python dictionaries in `tables.py` (still data-only, no point values in logic).

## 9. Test strategy

Every table row at boundaries; both W/S columns; each test's CLB bands incl. edges (e.g. IELTS 5.5 reading → CLB5, PTE 59 vs 60 listening); caps (50/100/600/1,200); three marital states; French bonus 25 vs 50; sibling cap; Canadian study vs education double-count; PNP; hand-computed full profiles; Flask endpoint tests.

## 10. Gaps and open questions – resolved

*History:* this table was originally "need your answers; nothing is assumed". All 14 were ruled on in `Plan_review2.md` on 2026-10-12 and implemented. The **Ruling** column is the current state; the "Proposed default" column is kept as history.

| # | Question | Why unresolved | Proposed default (original) | Ruling / current behaviour |
|---|----------|----------------|------------------------------|-----------------------------|
| Q1 | **Test scores between listed bands** (e.g. IELTS speaking 4.5 or reading 4.5; the PTE/TEF/TCF grids are contiguous so only IELTS is affected) | Tables list discrete thresholds only | Use the highest band whose lower bound is met (IELTS 4.5 speaking → CLB 4; reading 4.5 → CLB 5). UI restricts IELTS to 0.5 steps | Approved. Floor-threshold mapping; IELTS inputs in 0.5 steps. |
| Q2 | **Scores below the CLB 4 bound** | CRS tables say "<CLB 4 = 0" but conversion tables start at 4 | Return "<4" → 0 points; no error | Approved. Below CLB 4 → level 0 (`<4`), 0 points, no error. |
| Q3 | **Same-language tests**: first and second language both English or both French | Not stated | Validation error: second test must be in the other language | Approved. Validation error if both tests are the same language (backend; UI hides same-language tests in the second selector). |
| Q4 | **French bonus when English is mixed** (e.g. CLB 5 in two abilities, CLB 3 in two) | S1 only states "CLB 4 or lower" vs "CLB 5+ on all four" | No official rule for the gap; propose: 25 if *any*-ability English <5 (i.e. not all four ≥5), else 50. Please confirm | Approved with explicit rule: 50 only if min(English CLB) ≥ 5 (all four), else 25 (including no English test). |
| Q5 | **Transferability, single bachelor's / 1–2-year credential** | S1 has no bachelor's row; only "post-secondary credential of one year or longer" | Treated as tier "post-secondary" (13/25). Confirm | Approved. |
| Q6 | **Two credentials, none ≥3 yrs** (e.g. two 2-year diplomas) | Not covered by "two or more" row (requires a 3-yr one) | Core education: "Two-year program" (91/98); transferability: tier post-secondary | Approved. The user selects the "Two-year program" option in that case. |
| Q7 | **Cap on language second-language when couple** (22 vs 4×6 = 24) | S1 states "up to a combined maximum of 22" for W | Apply min(sum, 22) for couple, min(sum, 24) for single | Approved. |
| Q8 | **Test results older than 2 years** | S2 asks the question; consequences for score not specified | Include a "results < 2 years old" checkbox; if unchecked, language points = 0 and a warning is shown. Confirm, or drop the checkbox | **Revised – checkbox dropped.** Help text only; submitted scores are assumed valid. *(The original proposal of a validity checkbox was not built.)* |
| Q9 | **Section D cap 600 when PNP + others** | S1 says "Maximum 600 points" | Apply min(600, sum) | Approved. |
| Q10 | **Job-offer question**: official tool still asks, but gives no points | Not explained | Omit the input; show notice only | Approved. No job-offer input; notice box on the page. |
| Q11 | **Age input**: integer age vs date of birth + "invited on" date | S2 uses age on invitation date | Plain integer age with help text | Approved. Integer age 17–100 with help text. |
| Q12 | **ECA validity (< 5 yr) and language-validity are checklists** | Eligibility, not scoring | Show as help text only, not enforced | Approved. Help text only. |
| Q13 | **Spouse "language not applicable"** | S2 Q13 offers it | Spouse language = 0 points | Approved. Implemented as the "No test" option for the spouse; 0 points. |
| Q14 | **Max test values for validation** (TEF 450/360/300/450, TCF 20/699/699/20, PTE 90, IELTS 9, CELPIP 12) | Taken from the top of the conversion tables | Accept 0–max per ability | Approved. Ranges enforced in `tables.SCORE_RANGES` (TEF 450/360/300/450, TCF 20/699/699/20, PTE 90, IELTS 9 in 0.5 steps, CELPIP 12). |

## 11. Out of scope

Program eligibility (FSW/FST/CEC), proof of funds, NOC TEER lookup, job-offer scoring (removed), storing user data (calculation is stateless), PNP stream details.

## 12. Disclaimer text for the UI (from S2)

"This tool is intended solely for general guidance. In the event of any discrepancy, the results provided by the Express Entry electronic system shall govern."

## 13. Implementation tasks and status

| # | Task | Status |
|---|------|--------|
| 1 | Requirements analysis | Done, approved 2026-10-12 |
| 2 | Scaffold project (pyproject, venv, pytest, Flask) | Done |
| 3 | Data layer + language mapper (+ tests) | Done |
| 4 | Core/spouse/transferability/additional engines (+ tests) | Done |
| 5 | Calculator orchestration, caps, validation (+ worked examples) | Done |
| 6 | Flask API (+ tests) and responsive frontend (conditional spouse section, breakdown) | Done – automated tests and an API smoke test, plus a manual browser check by the user (UI loads and the score updates as inputs change). Scores were **not** compared against the official calculator |
| 7 | End-to-end verification vs. the official IRCC calculator | **Pending** – along with real-user acceptance feedback |
| 8 | Docker image, compose file, Docker Hub publish script, MIT license | Done – image built and run locally; the publish script has not been run |
