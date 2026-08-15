# Phase 1f — attenuation, and the gate that replaces the 80% rule

**Date:** 2026-08-14
**Instruments:** `src/analysis/attenuation.py`, `tests/test_attenuation.py`
**Source:** `data/processed/precision_sample_labelled_FINAL.xlsx` — 149 labelled rows, canonical
**Amendments:** `PREREGISTRATION.md` §11 A7, `DESIGN.md` §4.1a

---

## 0. Headline

Quoted at **store level**, on the 139 rows that resolve to a store:

| specification | λ | 95% CI (store cluster) | vs λ_min = 0.73 |
|---|---|---|---|
| as-is | **0.741** | [0.590, 0.920] | point above, **interval straddles** |
| **§5.3 routing** (operative) | **0.878** | [0.723, 1.000] | point above, **interval straddles** |
| men, as-is | 0.721 | [0.552, 1.000] | **point below**, interval straddles |
| women, as-is | 0.761 | [0.513, 1.000] | point above, interval straddles |

**The gate is not passed.** In every specification the point estimate sits above λ_min and the
interval spans it. That is a statement about **149 hand labels**, not about the dictionary: at this
sample size the interval is roughly ±0.17 wide and could not resolve λ_min either way unless the
truth were far from it.

Two things must not be said, and were said in an earlier draft of this document:

- **not** "the §5.3 specification passes on both point and interval". That was true at
  `parent_asin` clustering (lower bound 0.737) and is false at store clustering (0.723). A margin
  of 0.007 was never a pass in the first place.
- **not** that either upper bound is informative. Both sit at **1.000**, which is where the
  percentile bootstrap pins against the boundary. λ ≤ 1 by construction, so an upper bound of 1.000
  carries no information, and the same anti-conservatism that affects precision near 1 affects λ.

**Operative MDE at the §5.3 specification: 0.249 SD** with mega-listings excluded, **0.647 SD** with
them kept.

---

## 1. The canonical file

`precision_sample_labelled_FINAL.xlsx` was adopted and diffed cell-by-cell against the previous
copy. **30 cells differ, exactly as described:** `calibration_stated` 27 → 3 (rows 37, 48, 94 keep
`yes`), row 18's `human_label` `ran_large` → `true_to_size`, and row 18's stray `true_to_size`
cleared out of column G. `review_id_hash` order is identical and no other cell moved.

The file was found in the **old working directory** `Desktop/vanity_gap`, not in the repository —
the same trap as the `src/` tree (`docs/src-tree-audit.md`). It is now under `data/processed/` and
remains git-ignored.

The row-18 correction moves `true_to_size` precision from 96.7% to **98.3%** (59/60).

---

## 2. Confusion matrices — raw counts

### All labelled rows (n = 149)

| assigned ＼ human | ran_small | true_to_size | ran_large | none | unclear | total |
|---|---|---|---|---|---|---|
| `ran_small` | **29** | 5 | 4 | 2 | 0 | 40 |
| `true_to_size` | 0 | **59** | 1 | 0 | 0 | 60 |
| `ran_large` | 2 | 1 | **43** | 1 | 2 | 49 |
| total | 31 | 65 | 48 | 3 | 2 | 149 |

### Men (n = 72)

| assigned ＼ human | ran_small | true_to_size | ran_large | none | unclear | total |
|---|---|---|---|---|---|---|
| `ran_small` | **15** | 0 | 2 | 2 | 0 | 19 |
| `true_to_size` | 0 | **27** | 1 | 0 | 0 | 28 |
| `ran_large` | 1 | 1 | **21** | 0 | 2 | 25 |

### Women (n = 77)

| assigned ＼ human | ran_small | true_to_size | ran_large | none | unclear | total |
|---|---|---|---|---|---|---|
| `ran_small` | **14** | 5 | 2 | 0 | 0 | 21 |
| `true_to_size` | 0 | **32** | 0 | 0 | 0 | 32 |
| `ran_large` | 1 | 0 | **22** | 1 | 0 | 24 |

### Adjustment-advice family excluded (n = 135)

| assigned ＼ human | ran_small | true_to_size | ran_large | none | unclear | total |
|---|---|---|---|---|---|---|
| `ran_small` | **21** | 5 | 1 | 2 | 0 | 29 |
| `true_to_size` | 0 | **59** | 1 | 0 | 0 | 60 |
| `ran_large` | 1 | 1 | **41** | 1 | 2 | 46 |

**The men's and women's error structures differ in kind, not just in rate.** Men's `ran_small`
errors are two sign reversals and two `none`; women's are five leaks to `true_to_size` and two sign
reversals. Women's `ran_small` failures are the adjustment-advice construct; men's are more nearly
random. With 19 and 21 rows nothing can be concluded from that, but it is the shape to watch if
labelling resumes.

---

## 3. λ — and a correction to the specified formula

### 3.1 Which conditional

The brief specified `s_k = Σ_j P(true=j | assigned=k)·score(j)`, `λ = (s_large − s_small)/2` — the
**reverse** conditional, `P(true | assigned)`.

Attenuation of a **misclassified outcome** is governed by the **forward** conditional,
`P(assigned | true)`. Writing `y = score(assigned)`, `y* = score(true)`, under non-differential
misclassification `P(assigned=k | true=j, X) = M_kj`:

```
E[y | X] = Σ_j a_j · P(true=j | X),      a_j = Σ_k score(k) · M_kj
λ_forward = (a_large − a_small) / 2
```

so the measured difference is `λ_forward` times the true one, which is exactly what makes
`MDE_operative = MDE_design / λ` correct.

Using the reverse conditional in that formula inverts the direction: under the assumption that makes
it meaningful, one gets `E[y*|X] = c + λ_reverse·E[y|X]`, i.e. the **true** difference is
`λ_reverse` times the **measured** one — the measurement would be inflating, and dividing by it
would push the wrong way.

Our sample is stratified on the **assigned** bucket, so each matrix row is a direct draw from
`P(true | assigned)` and the reverse conditional is what we observe. The forward one is recovered by
Bayes using the assigned-bucket prevalence of the analysis population (`ran_small` 1054,
`true_to_size` 1706, `ran_large` 471 — the sampling frame of the 2026-08-11 draw), **not** the
sample's own proportions, which are equal-allocation by design and carry no information about the
corpus.

**In this instance the distinction turns out to be small: 0.763 against 0.749.** It is recorded
anyway, because it could have been large, and because the formula has to be right for reasons that
do not depend on how this particular dataset happened to come out.

### 3.2 Measured

| subset | **λ forward** | 95% CI (cluster bootstrap) | λ reverse | affinity residual |
|---|---|---|---|---|
| pooled | **0.763** | [0.621, 0.927] | 0.749 | +0.099 |
| men | 0.741 | [0.570, 0.978] | 0.777 | +0.160 |
| women | 0.784 | [0.551, 1.000] | 0.723 | +0.044 |
| **adjustment family excluded** | **0.886** | [0.737, 1.000] | 0.799 | −0.033 |

**The affinity residual** is `a_0 − (a_small + a_large)/2`, the amount by which the middle class
departs from the straight line through the two extremes. With three classes the single-λ summary is
two equations fitted to three, so a residual is expected; **the men's residual of +0.160 is the
largest and is a caveat on the men's λ specifically** — the one-number summary hides more structure
there than elsewhere.

### 3.3 The §5.3 routing gains about 0.14 of λ

At store clustering on the resolved rows, excluding the adjustment-advice family lifts λ from
**0.741 to 0.878**, and the interval's lower bound from 0.590 to **0.723**.

That decision was originally made on precision grounds, from the ModCloth per-pattern diagnosis, so
this is independent support from a different quantity computed a different way — worth more than the
same argument told twice.

**But it does not clear the gate.** 0.723 is below λ_min = 0.73. The routing moves λ a long way and
still leaves the interval spanning the threshold, which is the sample size talking rather than the
specification.

---

## 4. Operative MDE

| | λ | MDE_design = 0.219 (mega-listings excluded) | MDE_design = 0.568 (kept) |
|---|---|---|---|
| pooled | 0.763 | **0.287 SD** | 0.745 SD |
| men | 0.741 | 0.296 SD | 0.766 SD |
| women | 0.784 | 0.279 SD | 0.724 SD |

**The mega-listing decision (§11 A5) dominates everything else here.** With those listings excluded
the study lands at 0.287 SD, inside the 0.30 target. With them kept, λ would have to be ≥ 1.89 to
reach the target — impossible, since λ ≤ 1 by construction. **No dictionary improvement, no extra
labelling and no additional data can rescue the design if A5 resolves toward keeping them.**

---

## 5. Precision, with the right intervals

Four products carry more than 5% of rows each and the largest carries 10.1% (15 of 149), so rows are
not independent and Wilson intervals do not apply.

| bucket | precision | cluster bootstrap | Wilson (iid, for comparison) |
|---|---|---|---|
| `ran_small` | 72.5% | [59.2%, 85.0%] | [57.2%, 83.9%] |
| `true_to_size` | 98.3% | [94.0%, 100.0%] | [91.1%, 99.7%] |
| `ran_large` | 91.5% | [84.9%, 97.9%] | [80.1%, 96.6%] |

**Neither interval is right at both ends.** The cluster bootstrap is the appropriate one given the
clustering, but the percentile bootstrap is anti-conservative for proportions near 1 — it cannot
return an upper bound above the largest resample, and `true_to_size` sits at 59/60. Where the two
disagree at a boundary, **take the wider bound.**

### Cluster structure

| | |
|---|---|
| labelled rows | 149 |
| distinct `parent_asin` | **92** |
| mean rows per parent | 1.62 |
| largest parent | 15 rows (**10.1%**) |
| parents carrying > 5% of rows | **4** |
| parents with exactly one row | 75 (82%) |
| parents spanning > 1 assigned bucket | 13 |

Because 13 parents span more than one bucket, the bootstrap resamples parents **globally** rather
than within stratum; stratum sizes therefore vary across replicates, which is the conservative
choice.

The four heavy parents are the print-on-demand novelty listing (15 rows), an Amazon Essentials
flannel shirt (11), a Wrangler jean (10) and a jeggings listing (9) — the same mega-listing pattern
that drives CV = 11.3 in `docs/phase1d-specification-error.md`. It is the same phenomenon appearing
in a third place.

### 5.1 Store-level clustering — coarser, and probably the right one

`store` was resolved for **83 of the 92 parents**, covering **139 of 149 rows (93%)**, across
**68 distinct stores**.

| | parent-level | store-level |
|---|---|---|
| clusters | 92 | 68 |
| largest cluster | 15 rows (10.1%) | **20 rows (13.4%)** — Amazon Essentials |
| clusters > 5% of rows | 4 | 4 |
| **λ** | 0.763 | 0.741 |
| **λ 95% CI** | [0.621, 0.927] | **[0.590, 0.920]** |

Top stores by rows: Amazon Essentials 20 (13.4%), Funny Civil Engineers Shirt 15 (10.1%),
Wrangler Authentics 11 (7.4%), Prolific Health 9 (6.0%), Hanes 6 (4.0%).

**Store is preferred for a substantive reason.** Seller calibration is a property of the *store*,
not of the individual listing — the 20M-review analysis
(`docs/phase1b-size-deviation-probe.md` §4c) found store-level mean deviation spanning +0.25 to
+1.45. Two Amazon Essentials garments share that seller's ruler, so their labelling errors are not
independent even though the products are.

### 5.2 The clustering unit turns out barely to matter — a correction

An earlier draft of this document asserted that store clustering "gives the wider interval". **That
was wrong, and the same-sample comparison the brief asked for is what caught it.**

| | n | λ | 95% CI |
|---|---|---|---|
| all rows, cluster = parent | 149 | 0.763 | [0.621, 0.927] |
| resolved only, cluster = **parent** | 139 | **0.741** | **[0.589, 0.915]** |
| resolved only, cluster = **store** | 139 | **0.741** | **[0.590, 0.920]** |

On identical rows the two are **indistinguishable** — the same point estimate to three decimals and
intervals differing in the third. **The entire 0.022 shift is the ten dropped rows, not the
clustering unit.**

In hindsight the point estimates *had* to coincide: λ is computed from the confusion matrix, and the
clustering unit affects only the interval. The informative part is that the intervals coincide too,
and the reason is that the two partitions nearly are the same one — 68 stores across 83 parents, so
most stores contribute exactly one listing. Store is barely coarser than parent here, so it cannot
be much more conservative.

**What survives:** store remains the right unit on the substantive argument above, and the quoted
figure is the store one. What does not survive is any claim that choosing it buys extra caution.

Precision under store-level clustering, resolved subset: `ran_small` 69.4% [54.8%, 81.8%],
`true_to_size` 98.3% [93.5%, 100.0%], `ran_large` 90.7% [83.7%, 97.5%].

---

## 6. Differential error

λ_men 0.741 vs λ_women 0.784 — a gap of 0.043 with intervals overlapping almost entirely. **No
evidence of differential error, and no ability to exclude it** at 72 and 77 rows.

This matters because if error is differential the measured quantity is
`λ_men·Δ_men − λ_women·Δ_women`, which is not `λ·tau` for any single λ, and **the direction of the
resulting bias cannot be signed in advance** — it depends on the signs and magnitudes of `Δ_men` and
`Δ_women`, which are what the study is trying to estimate.

Hence the rule fixed in `PREREGISTRATION.md` §9.7: **the primary estimate is reported uncorrected
and is the confirmatory number; the λ-correction is a sensitivity analysis.** Fixed now, before any
estimate exists, because the choice between a corrected and an uncorrected headline becomes
unprincipled once the numbers are visible.

---

## 7. Why 80% had to go

The old gate read "hand-verified precision of each fit bucket ≥ ~80%". It was an **underived
convention** — nothing in the design implied it and it was never connected to the effect size the
study needs to detect.

It is also the **wrong shape**. Two dictionaries with identical per-bucket precision can attenuate
`tau` by very different amounts depending on which way their errors go. A bucket that leaks to
`true_to_size` costs less than one that leaks to the opposite extreme, and per-bucket precision
cannot tell them apart. `λ` can, because it is built from the scores rather than from a hit rate.

Concretely, in this sample: `ran_small` at 72.5% would have failed an 80% gate. But four of its
eleven errors are sign reversals and five are leaks to the middle, and λ answers the question the
gate was actually trying to ask — **is enough of the true effect surviving?** — with 0.763 rather
than a pass/fail on a number nobody derived.
