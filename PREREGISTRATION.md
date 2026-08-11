# Pre-registration — The Vanity Gap

**Version 1.0 — 2026-08-11.**
Frozen before any estimate of `tau` has been computed on any corpus.

This document fixes the hypotheses, the outcome, the sample, the specification and the refutation
conditions before estimation. Its value is entirely in being written first, so §1 discloses in full
what had already been observed when it was written. A pre-registration that hides its own prior
knowledge is worth less than no pre-registration, because it claims a credibility it does not have.

---

## 1. DISCLOSURE — what was already observed before this document was written

Four probes ran before this was written. Everything they showed is listed here, including the result
that points against the hypothesis.

### 1.1 Fit-label prevalence and its imbalance — observed

On `Clothing_Shoes_and_Jewelry`, 16.23% of reviews carry exactly one fit-dictionary label
(block-sampled, 50,000 reviews). Within the labelled set: `ran_small` 36.42%, `true_to_size` 43.69%,
`ran_large` 19.89%. **`ran_small` exceeds `ran_large` by roughly 1.8 to 1.** This is a fact about who
volunteers a fit comment, not about garments, and it is why §6 models selection rather than assuming
it away.

### 1.2 The ModCloth / RentTheRunway precision and recall matrix — observed

The fit dictionary was validated against 46,223 structured ground-truth rows. Per-bucket precision
raw: `ran_small` 62.7% / 61.5%, `true_to_size` 90.0% / 95.3%, `ran_large` 70.5% / 81.1%. Recall is
low (6.7%–51.1%) for the reason pre-committed in `docs/phase2-divergence-precommitment.md`: those
platforms prompt for fit, so most true labels have no fit language to match.

Two pattern families were identified as carrying nearly all the error — *adjustment advice*
(`size up`, `sized down`: 36–65%) and *partial-area fit* (`too tight`, `too loose`: 52–77%).
**No pattern was deleted in response.** §5 states what happens to them instead.

### 1.3 A mean deviation whose sign is OPPOSITE to the hypothesis — observed

This is the disclosure that matters most, and it is stated plainly rather than buried.

The self-reported size-deviation probe found a **mean signed deviation of +0.708 ladder steps
overall, with women at +0.80 and men at +0.21** in both body halves. §2's hypothesis predicts the
opposite ordering: men deviating upward more than women.

**This was seen before this document was written, and it did not change the hypothesis.** The
reasons, fixed here so they cannot be invented later:

- The cells are **n = 34 for men's upper and n = 4 for men's lower.** Four observations cannot move
  a hypothesis in either direction.
- The sample is **selected on having deviated** — only 21.8% of these reviewers report zero
  deviation, which is not a credible picture of buying and is instead a measurement of who narrates.
- Men and women may narrate deviation at different rates for reasons unrelated to how they buy, and
  the same probe found women outnumbering men **9 : 1** in this language.
- The measure is upward-biased by a known extraction defect (disjunctive sizes; §5.4), fixed but not
  yet re-run.

**Commitment:** if the same sign survives estimation on adequate cells under the §7 specification,
that is a refutation of §2 and will be published as one. It is written here so that the option of
quietly reframing it later does not exist.

### 1.4 The source files are ordered — observed

The Amazon `.jsonl` files carry a time gradient (`verified_purchase` 64.88% → 94.75%, mean review
length 316 → 142 characters, head to tail). Every rate measured from a file prefix was biased.
Rates have been re-measured under systematic block sampling; details in
`docs/phase1-amazon-probe.md` §5.6. All figures quoted in this document are block-sampled.

### 1.5 What has NOT been observed

**No estimate of `tau`, on any corpus, in any specification.** No regression of `fit_score` on
gender × body half has been run. No within-person estimate. No Chattaraman head-to-head. The
hand-labelled precision sample is drawn but unlabelled.

---

## 2. Hypotheses

**H1 (men).** Men whose true size is small buy larger than their true size; men at the large end buy
their true size. Direction: positive deviation concentrated at the small end of the men's ladder.

**H2 (women).** Women at the large end buy smaller than their true size; women at the small end buy
their true size. Direction: negative deviation concentrated at the large end of the women's ladder.

**H3 (gradient).** The deviation scales with how much the garment permits escape from fit:
**t-shirt > shirt > jeans/trousers**, because a waist that does not fit is unwearable while a loose
t-shirt is not. H3 is the discriminating prediction — a result without the ordering is not support.

**Rival hypothesis, tested head-to-head, not as related work.** Chattaraman, Simmons & Ulrich (2013)
predict deviation *increasing with body size*. On this project's account deviation concentrates at
the *small* end for men. The two make opposite predictions about where in the ladder deviation
lives, and the test is run on RentTheRunway, the only corpus carrying purchased size together with
body measurements.

---

## 3. Estimand

```
tau = ( E[fit_score | men,   upper] - E[fit_score | men,   lower] )
    - ( E[fit_score | women, upper] - E[fit_score | women, lower] )
```

**Prediction: `tau > 0`.**

The inner difference is a placebo contrast: body-composition explanations cannot produce a
gap between a man's upper and lower garments, because the same man wears both. The outer difference
removes anything common to upper-vs-lower across genders — fabric conventions, cut norms, the fact
that trousers simply fit more strictly than tops.

**Primary comparison is the H3 three-category gradient** (t-shirt / shirt / jeans). The wide
upper/lower sets are the secondary, higher-powered version. Both are reported. They are not
substituted for one another.

---

## 4. Data and sampling

| Corpus | Role | Access |
|---|---|---|
| Amazon Reviews'23, `Clothing_Shoes_and_Jewelry` | Men's arm and the primary estimand | Block-sampled, stream-only |
| ModCloth | Women's arm; dictionary ground truth | Read in full |
| RentTheRunway | Mechanism demonstration; Chattaraman head-to-head | Read in full |

**Sampling rule, binding:** every Amazon figure comes from `--spread N` block sampling across
disjoint file offsets. **A rate measured from a file prefix is never quoted.** This is systematic
sampling, not random sampling, and will be described as such in any write-up.

`Amazon_Fashion` is excluded: its `categories` field is empty in 100% of items, so it yields no cell.

**Body-half assignment** is the §1.3 table of `DESIGN.md`, frozen: dresses, jumpsuits, outerwear,
underwear, accessories, footwear and children's items are excluded; a dress spans both halves and
belongs to neither arm.

---

## 5. Variables

### 5.0 Labelling is BLIND, and the coding guide is fixed first

Two rules, both binding, both settled before any label is entered.

**Blind.** The labelling file carries `review_id_hash`, `review_title`, `review_text`, an empty
`human_label` and an empty `buyer_gender_mismatch`. It carries **no assigned bucket, no gender, no
category path and no body half.** Those live in a key file the labeller does not open, re-joined on
`review_id_hash` after labels come back. An unblinded precision measurement is not a measurement: a
labeller shown the assigned bucket is scoring agreement with a number already in front of them. Row
order is shuffled, so order carries no information either.

**Coding guide first.** What counts as a fit judgement is decided **before** blind labelling starts,
and is written into Appendix A of this document. It is developed on the **discarded** sample of
2026-08-08 (`data/processed/precision_sample_DISCARDED_2026-08-08_for_coding_rules.*`), which was
never labelled and is outside the analysis window. Developing the rules on one sample and applying
them to a different one is what keeps the rules from being tuned to the cases they will be scored
on.

The first sample was **discarded unlabelled** because it was drawn from the file head — the oldest
reviews, which the §5.8 window excludes. Full reasoning: `docs/phase1-amazon-probe.md` §5.7.

### 5.1 `fit_score` — the outcome

Buyer-relative realised fit, from review text, on `{-1, 0, +1}`:

| Value | Meaning | Bucket |
|---|---|---|
| −1 | garment ran small on the buyer | `ran_small` |
| 0 | fit as expected | `true_to_size` |
| +1 | garment ran large on the buyer | `ran_large` |

A review matching two or more buckets is **dropped as ambiguous, never guessed**. A review matching
none is not in the sample.

### 5.2 The dictionary is frozen as of commit `c9113fb`

The regex dictionary in `amazon_fit_probe.py` — `FIT_DICTIONARY` and `NEGATION_PATTERNS` — is frozen
at its state in commit `c9113fb`. Two patterns were removed before freezing, both demonstrated false
positives, both documented at the removal site: `\b(?:large|big)\s+(?:in\s+)?siz(?:e|ing)\b` and its
`small` counterpart.

**Amendment protocol.** Any later change requires (i) a dated entry in §11 of this document stating
the change and the evidence, and (ii) a **fresh** hand-labelled sample. Scoring a repaired
dictionary on the labels that exposed its defects is fitting to the validation set and is
prohibited.

### 5.3 Adjustment-advice language is a covariate, not part of the outcome

`size up`, `sized down`, `next size up` and the rest of that family measure **how tight-running the
style is**, not what the buyer wanted: "runs small, I took my usual size, too tight" and "runs small,
I sized up, perfect" say the same thing about the product. They are therefore:

- **excluded from `fit_score`** in the primary specification;
- **aggregated per `parent_asin` into `calibration_j`**, a style-level covariate — the mean firing
  rate of the family across that style's reviews;
- **folded back into `fit_score` in a named secondary specification**, because their error runs
  against the hypothesis, so a result surviving the fold is stronger.

`calibration_j` is style-level, so it is collinear with style fixed effects and is identified only in
the specification without them. This is stated so the collinearity is not later discovered and
presented as a finding.

### 5.4 Self-reported size deviation — secondary outcome, women's arm only

`deviation = ladder(bought) − ladder(usual)` on the alpha ladder, from reviews stating both. Numeric
ladders and disjunctive sizes ("small or medium", "l/xl") are **dropped as ambiguous**; the
disjunctive rule was added 2026-08-11 after it was found to inflate deviation, and prevalence has
not yet been re-measured under it.

**Not the primary measure.** The men's lower-body cell holds roughly 330 observations corpus-wide.
It is a triangulation measure on the women's arm and a qualitative check on the men's.

### 5.5 Gender

From `categories` — the gender the garment is **marketed to**, which is not the buyer's gender.
Mitigation, in standing order:

1. **Primary:** the text filter in `src/analysis/buyer_gender.py`, applied to every row, flagging
   third-party and cross-gender purchases. High-recall by design, so its rate is an **upper** bound.
2. **Robustness only:** `user_id` history inference on the ≥3-review subset. Never applied to the
   primary sample. This is **not** the within-person design of §7.3.
3. `buyer_gender_mismatch` is measured on the hand-labelled sample before it is dismissed.

---

## 6. Selection model

Fit comments are **volunteered**, not prompted, and volunteering is not random: `ran_small` exceeds
`ran_large` 1.8 : 1 (§1.1), and a garment that is too small is unwearable in a way that one slightly
too large is not.

**Commitments:**

- Report the labelled share **per cell**, not pooled. Differential labelling across the
  upper/lower contrast biases `tau` directly rather than attenuating it.
- Measured differential (ModCloth, RentTheRunway): lower-body garments are labelled 2.5–3.8pp more
  often than upper-body, same direction on both platforms. Carried into the model, not noted and
  forgotten.
- Recall on prompted platforms is **not** an estimate of recall on Amazon and will not be presented
  as one.
- The §5.4 deviation measure has a **different and probably worse** selection process, and inherits
  nothing from this section.

---

## 7. Specifications

### 7.1 Primary — one test, named

```
fit_score_ij = beta0 + beta1*male_i + beta2*upper_j + beta3*(male_i × upper_j) + alpha_s + eps_ij
```

on the **H3 three-category gradient sample**, with style fixed effects `alpha_s` and standard errors
clustered at the style level (`parent_asin`).

**`beta3` is the estimand `tau`. It is the single primary test of this pre-registration.**
Prediction: `beta3 > 0`. Everything else in this document is secondary or exploratory and will be
labelled as such.

### 7.2 Secondary, pre-specified

1. Wide upper/lower sets instead of the gradient sample.
2. Adjustment-advice family folded into `fit_score` (§5.3).
3. `calibration_j` included, without style fixed effects (§5.3).
4. The H3 ordering itself: t-shirt > shirt > jeans, as a monotonicity test.
5. Deviation as outcome on the women's arm (§5.4).
6. Chattaraman head-to-head on RentTheRunway.

**There are two with-and-without control axes — cut (`DESIGN.md` §1.7) and calibration — giving four
core specifications. All four are reported whichever way they fall.** No result is reported from a
specification not listed here without being labelled exploratory.

### 7.3 Within-person design

Where `user_id` supports it, the same buyer's upper and lower garments are differenced, removing
body composition entirely. Reported as robustness, not as the primary, because it selects on
multi-purchase users.

---

## 8. What would refute this

Stated in advance so that the answer cannot be negotiated afterwards:

1. **`beta3` ≤ 0 under §7.1.** The core prediction fails.
2. **`beta3` > 0 but the H3 ordering absent** — no monotone t-shirt > shirt > jeans. This would mean
   something produced a gender × half gap other than the escape mechanism, and the identification
   claim collapses even though the headline number "worked".
3. **The men's deviation runs below the women's on adequate cells** (§1.3), which is the sign
   already observed on n = 34 and n = 4.
4. **`beta3` driven by a small number of sellers** (§9.1) — calibration, not behaviour.
5. **Dictionary precision below ~80% per bucket on the men's stratum**, which would mean the men's
   arm was measuring noise.

Any of these is published. The project's contribution is the test, not the outcome.

---

## 9. Named threats

### 9.1 Seller calibration, not buyer behaviour — **directional and gender-correlated**

Amazon is a marketplace, and many apparel sellers use non-US sizing that runs small. "Order two sizes
up" is a **review genre**, not a preference. If this is gender-asymmetric — plausible, since overseas
fast-fashion skews women's — then the measured deviation is the seller's ruler rather than the
buyer's desire.

This is distinct from the generic seller heterogeneity already in `DESIGN.md` §5.9 because it is
**directional** and **correlated with the conditioning variable**.

**Test, pre-specified:** decompose positive deviation by `store` and report concentration (top-k
share, HHI, effective number of stores). Concentration in a handful of stores ⇒ calibration.
Spread thinly across many ⇒ behavioural.

**First attempt, 2026-08-11: INCONCLUSIVE — underpowered.** 400,000 block-sampled reviews joined to
200,000 metadata records yielded only **21** positive-deviation observations across 31 stores. No
concentration statistic computed on 21 points can distinguish calibration from behaviour, and none
is quoted here. The binding constraint is that the deviation language is rare (0.20%) and the
metadata join costs most of what survives. Reaching ~1,000 positive-deviation observations needs
roughly 20M streamed reviews. **This threat is therefore OPEN, not cleared**, and no result relying
on the §5.4 deviation measure may be published until it is answered. One observation worth carrying:
20 of the 21 were women's garments, consistent with the 9 : 1 asymmetry in §1.3.

### 9.2 Buyer gender ≠ garment gender

§5.5. Pushes toward a **false positive**, so it cannot be dismissed as attenuation.

### 9.3 Supply-side label inflation

Narrowed: uniform within-gender inflation cancels in `tau`; only inflation that **differs between
upper and lower within a gender** survives. Unmeasurable on Amazon, testable on RentTheRunway.

### 9.4 Text-derived labels are noisy

Confusion is overwhelmingly with `true_to_size` rather than sign-reversal (131 and 13 sign errors in
46,223 rows), which attenuates `tau` toward zero. A biased-toward-null instrument that still finds an
effect is more credible, not less — but the noise is reported, not used as an excuse.

### 9.5 Oversized fashion

A general trend toward loose fits would raise `ran_large` for everyone. It does not by itself
generate a gender × half interaction, which is why the estimand is a double difference.

---

## 10. Analysis rules

- **Multiple comparisons:** one primary test (§7.1). Everything else exploratory and labelled.
- **No outcome-dependent stopping.** Sample sizes are set by cell adequacy, not by looking at
  `beta3`.
- **Ambiguity is always a drop, never a guess.**
- **Every rate is block-sampled.**
- **Null results are published**, including all five refutation conditions in §8.
- **Data:** no raw review text or user field is ever published. Licence position unresolved
  upstream, so any released dataset is aggregates only.

---

## 11. Amendments

Every change after v1.0 is dated here, with what changed, why, and what evidence prompted it. An
amendment prompted by seeing a result must say so explicitly.

| Date | Change | Reason |
|---|---|---|
| 2026-08-11 | v1.0 frozen | Initial registration |
| 2026-08-11 | **A1 - §5.8 time window reopened as an empirical question.** IN PROGRESS | See below |
| 2026-08-11 | A2 - labelling made blind; coding guide required as Appendix A before labelling (§5.0) | An unblinded measurement is not a measurement |

### A1 - the analysis window is measured, not asserted

**Status: amendment in progress. No estimate of `tau` had been run at the time of this amendment,
and none has been run since.** That is stated explicitly because an amendment to an inclusion rule
made after seeing an estimate would be worthless.

**What changes.** `DESIGN.md` §5.8 set a trailing 12-18 month window. That figure was chosen against
**survivorship bias** alone - products that sold badly get delisted, so old reviews attach to
survivors.

**Why it changes.** The sampling-frame check produced a second and independent reason: **the
review-writing regime itself drifts.** Verified-purchase share 65% -> 95%, mean review length
316 -> 142 characters, fit-label share 19.3% -> 13.8%. Pooling a decade pools heterogeneous
*measurement* regimes, and if the regime mix differs across the four cells it contaminates `tau`
directly rather than merely adding noise.

**How the new boundary is chosen.** Empirically, by `time_window_probe.py`:

1. Per calendar year, in the target categories: verified-purchase share, mean length, mean rating,
   fit-label share. **The window starts where those series flatten**, not at a number picked in
   advance.
2. Each candidate window (18 months, 3 years, 5 years, 8 years, full history) is judged on the
   **smallest cell, not total volume** - specifically the **men's lower-body** count, which is the
   §1.5 placebo anchor and has already shrunk 26% under corrected sampling. A window that starves
   that cell is unavailable however much total data it offers. `DESIGN.md` §5.5 makes cell
   imbalance, not volume, the binding constraint on the MDE, and the upper:lower ratio was observed
   moving 2.14 -> 2.58 -> 2.63 across file blocks, so the window changes cell *balance* and not only
   cell size.
3. The outcome is a **primary window plus a robustness ladder**: `tau` estimated at every window
   length and reported together. Stability across the ladder is evidence that neither survivorship
   nor regime drift is biting; **monotone movement across the ladder is itself a finding** and is
   reported as one.

**Block sampling still applies inside the window.** Restricting to recent reviews does not remove
the need for `--spread`: three blocks detect only ordering coarser than the block size, so finer
grouping - by product or by seller - could still survive inside the window.

**This entry is completed with the measured numbers and the chosen window when the probe lands.**


---

## Appendix A — Coding guide for `human_label`

**STATUS: NOT YET WRITTEN. Blind labelling must not begin until this appendix is filled.**

To be written by the repository owner from the discarded sample
(`data/processed/precision_sample_DISCARDED_2026-08-08_for_coding_rules.xlsx`), which was never
labelled. It must settle at minimum:

- What counts as a **fit judgement** at all, versus a comment on an object's dimensions ("the ring
  is smaller than pictured"), on a garment's cut ("boxy"), or on one region only ("tight across the
  bust, fine elsewhere").
- How to treat a review describing **adjustment**: "runs small, I sized up, perfect". §5.3 makes this
  a calibration signal rather than part of `fit_score`; the coding guide must say what the labeller
  writes in that cell.
- When to use **`none`** (no fit judgement present) versus **`unclear`** (a judgement is present but
  the labeller cannot resolve it).
- What triggers **`buyer_gender_mismatch`**.
- Whether a **non-garment** item that reached the sample is `none` or is excluded.

Once written, this appendix is frozen alongside the rest of the document, and any later change
follows the §11 amendment protocol.
