# Phase 1d — the §1.4 specification cannot estimate its own estimand

**Date:** 2026-08-11
**Instruments:** `seller_fe_probe.py`, `cluster_probe.py`
**Status:** no estimate of `tau` has been run, before or since.

---

## 0. The error

`DESIGN.md` §1.4 specified *"a single regression with an interaction term and style-level fixed
effects"*. That specification is **unidentified**.

Gender and body half do not vary within a style. A men's t-shirt style is men/upper for every review
it carries. So `male`, `upper` and `male × upper` are all perfectly collinear with the style dummies,
and none of β₁, β₂, β₃ can be estimated.

Confirmed directly on the drawn precision sample: **170 distinct styles, zero carrying more than one
gender × body-half cell.** Within-style variance of the treatment variables is exactly zero. This is
structural, not a sampling accident — `parent_asin` *is* a product, and a product has one gender and
one body half.

A second problem, milder and now moot: 62.7% of styles carry exactly one labelled review, and a
singleton is perfectly fit by its own dummy. Even had identification worked, style FE would have
discarded roughly two-thirds of the styles.

---

## 1. Seller fixed effects — measured, and NOT viable

Seller is the natural next level: a seller can carry both genders and both halves, so the
interaction varies within it. It would also absorb seller calibration (§5.9) as a by-product.

Measured on 3,000,000 block-sampled reviews, 2019 window, 400,000-record style index —
16,027 labelled in-scope observations across **2,014 sellers**:

| cells a seller spans | sellers | observations | share |
|---|---|---|---|
| **1** — absorbed entirely, contributes nothing | 1,816 | 10,818 | **67.50%** |
| 2 — main effects only, interaction not separable | 168 | 2,687 | 16.77% |
| 3 — interaction identified within seller | 17 | 1,434 | 8.95% |
| 4 — full 2×2 within seller | 13 | 1,088 | 6.79% |

**The interaction would be identified by 30 sellers, carrying 15.74% of observations.** The anchor
cell fares slightly better but not enough: of 2,005 men's-lower observations, **747 (37.3%)** sit in
a ≥3-cell seller.

Seller FE therefore discards 84% of the data and rests the entire estimand on thirty sellers. That is
not a primary specification. **Reported as unviable rather than adopted because it was the proposal.**

The seller table is worth reading for a second reason:

| seller | obs | cells | styles | m/up | m/low | w/up | w/low |
|---|---|---|---|---|---|---|---|
| Funny Civil Engineers Shirt | 2,916 | 1 | **1** | 0 | 0 | 2,916 | 0 |
| Hanes | 789 | 3 | 21 | 595 | 110 | 84 | 0 |
| Amazon Essentials | 611 | 4 | 89 | 157 | 144 | 207 | 103 |
| Wrangler Authentics | 471 | 2 | 12 | 14 | 457 | 0 | 0 |

Only the established apparel brands span cells. The single largest contributor spans one cell, from
one style.

---

## 2. `parent_asin` is not reliably a style

**2,916 labelled observations — 18.2% of the entire sample — sit in ONE `parent_asin`**, a
print-on-demand novelty t-shirt listing. Median across styles is 1.

That is not a data error, it is how print-on-demand sellers list: one parent covers a whole catalogue
of printed designs. `parent_asin` is a *listing*, and for these sellers a listing is a product line.
`DESIGN.md` §1.6 treats it as a style.

The consequence is quantitative and severe. Measured clustering parameters, wide sample:

| | m_bar | CV |
|---|---|---|
| Phase 0 assumption (Mavi, single brand) | 20.00 | 1.00 |
| **Measured, all styles** | **4.571** | **11.31** |
| Measured, excluding the single heaviest style | 3.740 | 4.26 |

`m_bar` came in at a quarter of the assumed value, which helps. **CV came in at eleven times the
assumed value, which hurts far more**, because it enters the design effect as `CV² + 1`.

---

## 3. The MDE, under measured parameters

Wide sample, cells 2,385 / 2,005 / 8,465 / 3,174, ICC 0.05:

| scenario | m_bar | CV | DEFF | **MDE** |
|---|---|---|---|---|
| Phase 0 assumption | 20.00 | 1.00 | 2.95 | 0.177 |
| **Measured, all styles** | 4.57 | 11.31 | **30.40** | **0.568** |
| Measured, excluding heaviest style | 3.74 | 4.26 | 4.54 | 0.219 |
| Measured m_bar, CV = 2 | 4.57 | 2.00 | 2.09 | 0.149 |

**Removing one listing moves the MDE from 0.568 to 0.219.** The study's power is currently hostage to
a handful of print-on-demand listings.

Note also that the earlier 0.418 figure was computed on cells from a much smaller pass (600,000
reviews, 250,000-item index). At 3,000,000 reviews and a 400,000-item index the same cells are
6–7× larger, so cell counts scale with effort roughly as expected and are *not* the binding problem.
**The binding problem is CV.**

---

## 4. Cells by sample definition — the primary/secondary correction

Measured at 3,000,000 reviews, 2019 window:

| sample | men/upper | men/lower | women/upper | women/lower | total | smallest |
|---|---|---|---|---|---|---|
| **Wide upper/lower** (§1.3, secondary) | 2,385 | 2,005 | 8,465 | 3,174 | 16,029 | 2,005 |
| **Gradient tee+shirt / jeans** (§1.2, primary) | 1,433 | 1,644 | 5,895 | 1,548 | 10,520 | 1,433 |

The gradient sample is thinner but **not dramatically so** — 66% of the wide sample's observations,
smallest cell 1,433 against 2,005. The earlier claim that the primary specification is materially
worse powered than the secondary is therefore true but modest, and it does not on its own justify
re-ranking them.

`PREREGISTRATION.md` §7.1a reported the wide sample's MDE against a primary-specification claim.
That is corrected in amendment A4.

---

## 5. What is proposed

**Not** seller FE — measured and unviable (§1).

**Fixed effects at a level where the interaction still varies.** Within a garment category, `upper`
is constant but `male` is not, so β₃ is identified as the difference in the male coefficient between
upper-body and lower-body categories. This uses every observation rather than 15.74% of them.

- **Fixed effects:** garment category.
- **Seller:** covariate, not fixed effect. It cannot absorb calibration as completely as seller FE
  would, so §9.1 stays open rather than being closed as a by-product.
- **Standard errors:** clustered at style level. Unchanged, and still right — that is a separate
  matter from the FE level.
- **Calibration covariate** from coding-guide Rule 1: unchanged, still style-level.
- **Seller FE on the 30-seller subsample:** retained as a **robustness check**. Low-powered, but a
  within-seller replication is a genuinely strong test precisely because calibration is differenced
  out. Reported whatever it shows.

**An open decision for the repository owner, not settled here.** What to do about print-on-demand
mega-listings. The options are to keep them (MDE 0.568), to exclude listings above a stated
observation threshold as not being styles (MDE ≈ 0.22), or to model them separately. This changes
the headline power figure by a factor of 2.6 and it is a judgement about what a "style" is, so it
belongs to the owner and must be fixed in `PREREGISTRATION.md` **before** estimation, with the rule
stated in advance rather than chosen after seeing which gives a better answer.
