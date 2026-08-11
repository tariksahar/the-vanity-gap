# Phase 1c — choosing the analysis window empirically

**Date:** 2026-08-11
**Instrument:** `time_window_probe.py`
**Sample:** `Clothing_Shoes_and_Jewelry`, 600,000 reviews block-sampled across 16 disjoint offsets,
joined to a 250,000-record style index
**Amendment:** `PREREGISTRATION.md` §11 A1

`DESIGN.md` §5.8 set a trailing 12–18 month window against **survivorship bias** alone. The
sampling-frame result added a second and independent reason — the **review-writing regime drifts** —
which makes the boundary an empirical question rather than a number to assert.

---

## 1. Per-year composition

| year | n | verified | mean length | mean rating | fit label |
|---|---|---|---|---|---|
| 2009 | 402 | 69.4% | 402 | 4.24 | 6.2% |
| 2010 | 694 | 85.2% | 408 | 4.18 | 14.6% |
| 2011 | 1,322 | 85.7% | 411 | 4.16 | 13.5% |
| 2012 | 3,199 | 89.4% | 355 | 4.24 | 13.4% |
| 2013 | 9,431 | 95.0% | 299 | 4.21 | 15.7% |
| 2014 | 18,887 | 88.6% | 216 | 4.23 | 14.4% |
| 2015 | 30,436 | 95.5% | 177 | 4.24 | 12.7% |
| 2016 | 42,145 | 93.8% | 184 | 4.25 | 13.4% |
| 2017 | 48,133 | 95.3% | 163 | 4.23 | 14.6% |
| 2018 | 59,510 | 93.2% | 167 | 4.23 | 15.6% |
| **2019** | 86,082 | 93.2% | 167 | 4.27 | 16.2% |
| **2020** | 88,441 | 93.1% | 173 | 4.22 | 17.5% |
| **2021** | 97,521 | 93.8% | 172 | 4.10 | 17.8% |
| **2022** | 86,003 | 90.4% | 182 | 4.07 | 17.2% |
| **2023** | 27,358 | 88.4% | 185 | 4.10 | 16.9% |

2023 is a partial year — the corpus ends in it.

**Where things stabilise, read series by series:**

- **Mean length** collapses 402 → 177 between 2009 and 2015, then is flat in the 163–185 band from
  2015 onward. This is the mobile transition, and it is over by 2015.
- **Verified-purchase share** is noisy early, then sits in the 88–96% band from 2013, with no trend.
- **Fit-label share** is the slowest to settle: 12.7% in 2015 rising to 17.8% by 2021, flat at
  16–18% from **2019**. This is the series that matters most, because it is the one the outcome is
  built from.

**All three are jointly flat from 2019 onward.** The script's automatic `stable?` flag reported
"flatten from 2023", which is its per-year tolerance being too strict for year-on-year noise — a
3.4pp wobble in verified share between 2021 and 2022 tripped it. The flag is reported as the script
produced it; the reading above is the honest one and does not rely on it.

---

## 2. Candidate windows, judged on the smallest cell

`DESIGN.md` §5.5 makes cell imbalance, not total volume, the binding constraint. The men's
lower-body cell is the §1.5 placebo anchor.

| window | from | labelled | men/upper | **men/LOWER** | women/upper | women/lower |
|---|---|---|---|---|---|---|
| 18 months | 2022 | 4,617 | 23 | **12** | 141 | 50 |
| 3 years | 2021 | 36,781 | 214 | **151** | 1,045 | 446 |
| **5 years** | **2019** | **66,133** | **405** | **307** | **1,721** | **798** |
| 8 years | 2016 | 88,071 | 514 | **394** | 1,876 | 960 |
| full history | all | 96,913 | 535 | **431** | 1,893 | 981 |

**The 12–18 month default of §5.8 yields twelve observations in the anchor cell.** That window is
unavailable. It is not a matter of low power — twelve style-clustered observations cannot support
the placebo test at all, and the placebo test is the identification claim.

The relative comparison is what governs here. These counts come from a 250,000-item index covering
about 3.5% of the corpus's items, so they undercount absolutely; the ratios between windows do not
depend on that.

---

## 3. Proposal

**Primary window: 5 years, 2019 onward.**

It is the only candidate that satisfies both criteria at once:

- it starts exactly where the three composition series become jointly flat (§1), so it does not pool
  heterogeneous measurement regimes;
- it gives the anchor cell **307** observations — **25× the 18-month window** — which is the
  difference between having a placebo test and not having one.

Extending to 8 years buys 87 more anchor observations (394 vs 307), a 28% gain, at the cost of
readmitting 2016–2018 when fit-label share was still drifting (13.4% → 15.6%). That trade is
available, and it is exactly what the robustness ladder is for rather than a reason to move the
primary boundary.

**Robustness ladder, all reported together:**

| rung | status |
|---|---|
| 18 months | Reported, and flagged **underpowered** — 12 anchor observations. Present for completeness, not for inference. |
| 3 years | Reported. |
| **5 years** | **Primary.** |
| 8 years | Reported. |
| full history | Reported, with the survivorship caveat of §5.8 attached. |

`tau` is estimated at every rung and the ladder is published whole. Stability across it is evidence
that neither survivorship nor regime drift is biting. **Monotone movement across the ladder is
itself a finding** and is reported as one rather than resolved by picking a rung.

---

## 4. What this does not fix

Restricting to a recent window does **not** remove the need for `--spread` inside it. Three blocks
detect only ordering coarser than the block size, so finer grouping — by product, or by seller —
could survive within the window untouched. Block sampling stays on for every draw.

The window also does not address survivorship, which was §5.8's original concern: reviews from 2019
still attach to products listed in 2023. It narrows the exposure rather than removing it, and the
full-history rung exists so the direction of that bias can be seen.
