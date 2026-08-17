# Phase 1h — the three A5 measurements, and why inference had to change

**Date:** 2026-08-15
**Instruments:** `a5_probe.py`, `src/analysis/wild_bootstrap.py`, `src/analysis/run_wcb_mde.py`
**Sample:** 3,000,000 block-sampled reviews, 2019 window, 400,000-record style index —
15,072 labelled observations across 3,111 parents
**Feeds:** `PREREGISTRATION.md` §11 A5 (still open), §7.2a (inference method)

---

## 0. What changed

Three measurements were pending on A5. All three are in, and two invert the expectation:

| | expected | measured |
|---|---|---|
| **0** existing filters dissolve the problem | plausible | **no — they concentrate it**, 18.61% → 23.23% |
| **1** mega-listing is one calibration unit | testable | **untestable**, and that is a third outcome |
| **4** DEFF/MDE per object | — | men's arm binds; KEEP 0.412, not 0.568 |
| WCB fixes an understated MDE | expected | **formula was already calibrated**, 1.01× |
| WCB needed for inference | secondary | **primary — asymptotic test overrejects 3.7×** |

---

## 1. Measurement 0 — the filters make it worse, not better

| parent | in scope | window | verified | window+ver | labelled | survival |
|---|---|---|---|---|---|---|
| `B07TVHSDMQ` | 14,672 | 13,837 | 14,436 | 13,632 | 2,893 | **95.3%** |
| `B07XFXXZMV` | 1,949 | 1,932 | 1,915 | 1,898 | 348 | **98.0%** |
| `B08R8W8GP9` | 1,161 | 1,059 | 1,132 | 1,032 | 260 | **87.8%** |

**`verified_purchase` does nothing here: 98.4% of the mega-listing's reviews are verified.** The
§5.8 window does nothing either — these listings are recent by construction.

And the share of the analysis sample held by structurally-failing listings **rises** from
**18.61% before the filters to 23.23% after**. The filters remove proportionally more from
conventional listings, whose reviews are older, so applying them **concentrates** the mega-listings
rather than diluting them.

The cheapest question was the right one to ask first, and the answer is that it buys nothing.

---

## 2. Measurement 1 — untestable, which is a third outcome

- **asins appearing under more than one parent: 0.** The single-store claim holds by construction,
  as expected — `store` is a field on the parent's metadata row.
- **size grid per asin: not measurable.** Reviews carry `asin`, `parent_asin`, `rating`, `text`,
  `title`, `timestamp`, `user_id`, `verified_purchase` and nothing else. No size field, and metadata
  is parent-level.
- **fit homogeneity across asins: CANNOT BE TESTED.**

| parent | asins | with ≥1 labelled | **with ≥5 labelled** |
|---|---|---|---|
| `B07TVHSDMQ` | 12,725 | 2,765 | **2** |
| `B07XFXXZMV` | 1,741 | 337 | **0** |
| `B08R8W8GP9` | 1,081 | 252 | **0** |

Each design carries about one observation. There is nothing to compare designs against each other
with. **A cluster whose members cannot be compared is an assumption, not a finding.**

### 2.1 The pre-registered refuter is neither triggered nor cleared

`PREREGISTRATION.md` §11 A5 recorded in advance: *if measurement 1 shows the mega-listing is not a
single calibration unit, parent-level clustering was wrong from the start and the decision turns
toward SPLIT.*

**It does not show that. It shows we cannot tell.** That is a third outcome, and it was not
pre-specified. Reported as such rather than pressed into either branch.

### 2.2 Untestability does NOT favour SPLIT — it makes SPLIT the aggressive choice

This inverts the intuition, and it is the most important thing in this document.

| option | clustering assumption about the 12,725 designs | stance |
|---|---|---|
| **KEEP** (cluster = parent) | errors are **perfectly correlated** within the catalogue | **most conservative** |
| **SPLIT** (cluster = asin) | errors are **uncorrelated** across designs — and with ~1 observation per asin those rows are effectively **independent** | **least conservative** |

The truth is between them and is exactly what cannot be measured. So the MDE ordering —
SPLIT 0.132 < EXCLUDE 0.156 < KEEP 0.412 — **is not evidence about which option is right.** It is a
mechanical restatement of how much correlation each option assumes away. Any option that assumes
less correlation will produce a smaller MDE, whether or not the assumption is true.

Reading the MDE ranking as support for SPLIT would be choosing the answer that assumes the most and
calling it the most precise.

---

## 3. Measurement 4 — the men's arm binds

Gradient cells: men 786 / 528 / 1,557 (tee / shirt / jeans), women 4,880 / 768 / 1,432.

| scenario | clusters | m_bar | CV | DEFF | **MDE `tau`** | MDE `Δ_men` | MDE `Δ_women` |
|---|---|---|---|---|---|---|---|
| KEEP | 3,111 | 4.845 | 11.21 | **31.64** | **0.412** | 0.341 | 0.232 |
| EXCLUDE | 3,108 | 3.723 | 3.89 | 3.95 | 0.156 | 0.120 | 0.099 |
| SPLIT | 6,462 | 2.332 | 4.34 | 3.27 | 0.132 | 0.110 | 0.074 |

All figures are the **gradient trend per step**.

**`Δ_women` is best powered in every scenario, `Δ_men` worse, `tau` worst.** The men's arm binds the
design, consistent with §5.5. Per §9.8 this says which arm binds and nothing more — `Δ_men` is not
separately identified and is a diagnostic, not a publishable result.

### 3.1 0.412 and 0.568 are different objects and must not be compared

The earlier 0.568 was the **wide upper/lower 2×2 contrast**. This 0.412 is the **three-category
gradient trend per step**. The ordered contrast is a better-powered object (`docs/phase1f` §3.3
measured the gain at 1.16–1.41×) and the cells here are larger. **Neither figure supersedes the
other; they answer different questions.** Quoting one as an improvement on the other would be a
category error.

KEEP at 0.412 is still above the locked 0.30 target. EXCLUDE and SPLIT are comfortably inside it.

### 3.2 Threshold sensitivity — the criterion is not a single number

| > asins | listings | labelled | share |
|---|---|---|---|
| 300 | 9 | 4,520 | 29.99% |
| 500 | 7 | 4,313 | 28.62% |
| **1000** | **3** | **3,501** | **23.23%** |
| 2000 | 1 | 2,893 | 19.19% |

Reported at several values rather than asserted once. The structural criterion is *"more asins than
this garment's size grid can generate"*, which is not a flat threshold — Wrangler's 560 asins are
legitimate (waist × inseam × wash), Hanes's 150 are legitimate, 12,725 are not.

---

## 4. Wild cluster bootstrap — the formula was calibrated, and inference still had to change

Two separate claims got conflated in the brief, and separating them is what this section is for.

### 4.1 Is the MDE formula understating? No.

Stylised two-group contrast carrying the **measured** KEEP cluster structure — 3,111 clusters,
15,072 observations, dominant cluster 19.2%, treated group 73 clusters including the dominant one:

```
formula MDE   0.2562 SD
WCB MDE       0.260  SD        distortion factor 1.01x
```

Power curve: 0.15 → 0.63, **0.26 → 0.87**, 0.40 → 0.93, 0.60 → 1.00.

**Why it holds up.** The formula has no explicit term for "one cluster is a fifth of the sample", but
**CV does that work** — one cluster of 2,893 among 72 small ones produces an enormous CV, and CV
enters as `CV²`. Without clustering this design's MDE would be 0.046; the formula charges it up to
0.256, a 31× variance penalty. WCB says that penalty is about right.

**What must not be over-read.** 30 trials gives a Monte Carlo SE near 0.091, and power of 0.87 at
0.26 places the 80% crossing anywhere from roughly 0.20 to 0.30. The grid is coarse. **The honest
statement is "no evidence the formula materially understates", not "the factor is 1.01".** A
distortion that is not there will not be manufactured.

So `MDE_design = 0.568` and the gradient's 0.412 are **not** discredited, and the sentence about
λ ≥ 1.89 stands as arithmetic. The brief's methodological worry was legitimate; it does not bite
empirically in this configuration.

### 4.2 Is asymptotic inference valid? No — and this is severe.

Null rejection rate at a nominal 5%, same measured structures, 200 trials each:

| scenario | dominant cluster | **asymptotic CR** | **WCB** |
|---|---|---|---|
| **KEEP** | 19.2% | **0.185** | **0.040** |
| EXCLUDE | 4.8% | 0.085 | 0.065 |
| SPLIT | 3.7% | 0.100 | 0.070 |

**Under KEEP the asymptotic cluster-robust t-test rejects true nulls 18.5% of the time at a nominal
5% — a false-positive rate 3.7× too high.** WCB returns 0.040, correct.

This is the claim that survives, and it is a **coverage** failure, not an MDE failure. A test can
have a correctly-calibrated MDE and still be badly mis-sized, because the MDE describes what effect
the design can detect while size describes how often it cries wolf. **They are independent, and here
one is fine and the other is not.**

Note also that SPLIT (0.100) is worse-sized than EXCLUDE (0.085) despite a smaller dominant cluster:
6,462 clusters of which most hold a single observation is its own problem for the asymptotic
approximation. Even WCB sits slightly high there (0.070). Monte Carlo SE at 200 trials is about
0.015, so 0.085 is marginal while 0.185 is not.

**Consequence: wild cluster bootstrap is mandatory for inference, in every scenario, and the reason
is coverage.** Recorded in `PREREGISTRATION.md` §7.2a with that rationale rather than the MDE one
originally proposed.

### 4.3 What this does to the A5 decision

It removes the strongest practical objection to KEEP. The real risk of keeping the mega-listings was
never the MDE — 0.412 is an honest number — it was that we would have reported standard errors that
were wrong by a factor of nearly four. **With WCB that risk is handled**, and KEEP becomes the option
that assumes least and now also reports honestly.

---

## 5. Standing

A5 remains **open with provisional default KEEP**. What the measurements changed:

- measurement 0 removes "the filters handle it" from the table;
- measurement 1 establishes that the parent-clustering assumption is **untestable**, which is neither
  the pre-registered refutation nor support, and which makes SPLIT the aggressive option rather than
  the neutral one;
- measurement 4 confirms the men's arm binds and that KEEP alone falls outside the 0.30 target;
- the WCB work moves the objection to KEEP from "wrong MDE" to "was going to have wrong standard
  errors", and then answers it.

The decision still belongs to the repository owner. Nothing here consulted the outcome, and none of
these measurements could have: whether a listing prints many designs onto one blank garment carries
no information about `tau`.
