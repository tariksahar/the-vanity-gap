# Phase 1e — dictionary precision, measured

**Date:** 2026-08-14
**Instrument:** `src/analysis/score_precision.py`
**Sample:** `data/processed/precision_sample_blind.xlsx`, drawn 2026-08-11 from the 2019 window,
blind, stratified three buckets × two genders
**Labelled:** **149 of 300 rows**

This is the `DESIGN.md` §4.1 gate measure, and it has been open since Phase 1.

---

## 0. Headline

| bucket | n | precision | 95% CI (Wilson) | gate |
|---|---|---|---|---|
| `ran_small` | 40 | **72.5%** | [57.2%, 83.9%] | **INCONCLUSIVE** |
| `true_to_size` | 60 | **96.7%** | [88.6%, 99.1%] | **PASS** |
| `ran_large` | 49 | **91.5%** | [80.1%, 96.6%] | **PASS** |

Two buckets clear the ~80% threshold with their whole interval above it. One spans it.

**Not a failure, and not a pass.** `ran_small` at 72.5% with an interval reaching 83.9% cannot be
called either way at this sample size, and the honest verdict is that the sample is too small to
decide the bucket that most needed deciding.

---

## 1. Partial coverage, by decision

**Labelling stopped at 149 of 300 rows. That was a decision, not an oversight**, and it is recorded
as one so that the partial coverage is never read as abandonment.

Roughly 25 scoreable rows per bucket per gender. At that n a Wilson interval on a proportion near
0.8 spans roughly ±13 points, so **every figure here must be quoted with its interval.** A point
estimate alone would overstate what 149 hand judgements can establish.

The intervals are wide by construction. An inconclusive verdict is a statement about the sample
size, not about the dictionary.

---

## 2. DISCLOSURE — the labels were revised, and the audit was not independent

This section exists because omitting it would make every number above less trustworthy, not more.

**What happened.** An initial pass of 46 rows was audited against `docs/coding-guide.md` and showed
three systematic misapplications:

1. coding the product's **calibration** instead of the buyer's **realized fit** (Rule 1),
2. taking the buyer's **satisfaction** over the **physical description** (Rule 4),
3. using `none` for short but explicit fit statements.

Those were corrected and labelling completed to 149. A second audit of the full set found **four
further rows to change** and four genuinely borderline ones.

**The part that matters.** The audit was **not independent**. It was performed by the same party
that shaped the coding guide, and **three of the four final corrections moved labels toward the
reading the dictionary would produce.**

**Bound on the inflation.** The revision touched 4 of 149 rows. Even if all four moved in the
dictionary's favour, the effect on measured precision is bounded at roughly **three percentage
points**. So `ran_small`'s 72.5% might be ~70%, and `ran_large`'s 91.5% might be ~89%.

**Standing: these figures are a slight UPPER bound, not a neutral estimate.** That does not change
the gate verdicts — `true_to_size` and `ran_large` clear the threshold with room, and `ran_small`
was already inconclusive — but it is the correct way to read them, and an independent second coder
is the fix if the number ever needs to bear more weight than it does now.

---

## 3. By gender

The men's arm is where the dictionary is extrapolated, so it is reported separately.

| bucket | men | 95% CI | women | 95% CI |
|---|---|---|---|---|
| `ran_small` | 78.9% (19) | [56.7%, 91.5%] | 66.7% (21) | [45.4%, 82.8%] |
| `true_to_size` | 92.9% (28) | [77.4%, 98.0%] | 100.0% (32) | [89.3%, 100.0%] |
| `ran_large` | 91.3% (25) | [73.2%, 97.6%] | 91.7% (24) | [74.2%, 97.7%] |

**The men's arm is not worse than the women's.** On `ran_small` it is better (78.9% vs 66.7%),
though the intervals overlap heavily and nothing should be concluded from the ordering. The
pre-registered worry — that precision measured on women would not transfer to men — is **not
supported by this sample**, which is the most useful thing in this table.

---

## 4. Where the errors are, and the ModCloth diagnosis transfers

Per-pattern breakdown of the 40 `ran_small` rows:

| pattern | ok | miss | precision |
|---|---|---|---|
| `runs (a bit) small` — the core family | 12 | 1 | **92%** |
| `ran small` | 1 | 0 | 100% |
| `very/really tight` | 2 | 0 | 100% |
| `go up a size` | 2 | 0 | 100% |
| `too small` | 5 | 2 | 71% |
| **`size up`** | 4 | 3 | **57%** |
| `way too small` | 1 | 2 | 33% |
| **`too tight`** | 0 | 2 | **0%** |

Grouped:

| family | precision | 95% CI |
|---|---|---|
| adjustment-advice (`size up`, `sized up`, …) | 63.6% (11) | [35.4%, 84.8%] |
| everything else in `ran_small` | 75.9% (29) | [57.9%, 87.8%] |

**This independently reproduces the Phase 2a ModCloth diagnosis on Amazon, by hand.** ModCloth put
the adjustment-advice family at 36–65% and the core `runs` family at 86–91%; the Amazon hand labels
put them at 64% and 92%. Two different corpora, two different methods — structured ground truth
versus human judgement — landing in the same place. That is the strongest validation of the §5.3
decision to move adjustment-advice language to a style-level covariate rather than into
`fit_score`.

**But removing that family does not rescue the bucket.** The remainder is still 75.9%, and
`too tight` (0/2) and `way too small` (1/3) are the partial-area family that ModCloth also flagged
at 52–77%. `ran_small`'s weakness is spread across two families, not concentrated in one.

### 4.1 Sign reversals

Four of the 40 `ran_small` rows were labelled `ran_large` by the human — **10%**, and sign reversal
is the error that damages `tau` rather than attenuating it.

All four are the same case: **the buyer sized up, and the garment came out loose.** The regex reads
"went a size up" as `ran_small` because the phrase describes the product; the human reads the
realized fit as `ran_large`. This is not noise, it is the §5.3 construct split appearing as a
measured disagreement.

For scale, ModCloth's equivalent rate — predicted `ran_small` where truth was `ran_large` — was
7.1%, and RentTheRunway's 3.5%. The Amazon 10% [4.0%, 23.1%] is consistent with both.

---

## 5. Labeller flags

| flag | rate | 95% CI | reading |
|---|---|---|---|
| `calibration_stated` | **3 / 149 = 2.0%** | [0.7%, 5.8%] | lower bound |
| `wearer_gender_mismatch` | **2 / 149 = 1.3%** | [0.4%, 4.8%] | lower bound |

**`calibration_stated` was re-coded; the original rule was too loose.** Under the initial reading 27
rows were flagged. Rule 8 required the review to name a brand, manufacturer or regional convention
**as the cause** — "runs big" is an observation, not an attribution — and under that reading it is
**3**. Without the restriction the flag simply duplicates `human_label` and carries no independent
information. The rule is sharpened and dated in `docs/coding-guide.md` §8 and §11.

> **File discrepancy, flagged rather than papered over.** The workbook on disk still carries the
> loose coding (27 flagged). The operative figure of 3 comes from the owner's re-coding and is not
> yet written back to the file. The two must be reconciled before the flag is used in any analysis;
> the artifact figure is the operative one.

**`wearer_gender_mismatch` at 1.3% materially reduces the §5.9 buyer-gender threat without closing
it.** Both flagged cases are genuine; one is a woman who bought a men's sweatshirt and reasoned
about sizing *"since it was men's"* — which is also one of the four sign-reversal rows. It is a
lower bound because most reviews say nothing about who wore the garment.

### 5.1 An uncovered contamination type

One row is an **adult women's product reviewed for a 7-year-old wearer**. §1.3 excludes children's
*products* but not child *wearers* of adult products, and `wearer_gender_mismatch` asks about gender
rather than age, so neither catches it.

**Noted, deliberately not fixed.** One occurrence in 149 rows is not evidence of a systematic
problem, and adding an age rule on that basis would be fitting the guide to a single case.

---

## 6. What the labeller actually saw

| human label | n | share |
|---|---|---|
| `true_to_size` | 64 | 43.0% |
| `ran_large` | 49 | 32.9% |
| `ran_small` | 31 | 20.8% |
| `none` | 3 | 2.0% |
| `unclear` | 2 | 1.3% |

**`none` at 2.0% and `unclear` at 1.3% are both low, and that is informative.** The dictionary very
rarely fires on text carrying no fit judgement at all — its errors are almost entirely *wrong
direction*, not *no signal*. And the construct itself is rarely ambiguous to a human: only two rows
in 149 could not be resolved.

---

## 7. The §4.1 gate

| measure | threshold | result | verdict |
|---|---|---|---|
| precision, `true_to_size` | ≥ ~80% | 96.7% [88.6, 99.1] | **PASS** |
| precision, `ran_large` | ≥ ~80% | 91.5% [80.1, 96.6] | **PASS** |
| precision, `ran_small` | ≥ ~80% | 72.5% [57.2, 83.9] | **INCONCLUSIVE** |
| purchased size recoverable | ≥ 50% | 0.82%, structurally absent | FAIL — secondary analyses only |
| men's lower-body cell | not vanishing | 2,005 per 3M reviews | PASS |
| reviews carrying a fit label | enough for smallest cell | 16.23% | PASS |

**The gate is not passed and not failed.** It rests on one bucket whose interval spans the
threshold.

Three routes forward, and the choice is the repository owner's:

1. **Label the remaining 151 rows.** Doubling n would narrow `ran_small`'s interval from ±13 to
   roughly ±9 points — enough to decide it if the true value is not sitting right on 80%.
2. **Repair the two weak families and re-measure on a fresh sample.** §5.2 of the pre-commitment
   requires a fresh sample for a repaired dictionary; the existing labels cannot score it.
3. **Accept `ran_small` at ~72% and carry it as a stated limitation**, on the argument that the
   errors are overwhelmingly confusion with `true_to_size` (attenuating) plus a 10% sign-reversal
   rate concentrated in a family §5.3 already routes out of `fit_score`.

Route 3 is coherent but should not be taken silently — it changes what the men's arm can claim.
