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

### 1.6 The dictionary precision measurement — observed 2026-08-14

The §4.1 gate measure is now measured, blind, on 149 hand-labelled rows:
`ran_small` **72.5%** [57.2, 83.9], `true_to_size` **96.7%** [88.6, 99.1], `ran_large` **91.5%**
[80.1, 96.6]. Two buckets pass; `ran_small` spans the threshold and is inconclusive at this n.

Men's-arm precision is **not worse** than women's (78.9% vs 66.7% on `ran_small`, intervals
overlapping), which is the pre-registered worry not being supported.

**Disclosure — the labels were revised and the audit was not independent.** An initial 46-row pass
was audited against the coding guide, three systematic misapplications were corrected, labelling
completed to 149, and a second audit changed four further rows. The audit was performed by the
party that shaped the coding guide, and **three of the four final corrections moved labels toward
the reading the dictionary produces.** The revision touched 4 of 149 rows, bounding the inflation at
roughly three percentage points. **These precision figures are therefore a slight UPPER bound, not a
neutral estimate.** Full detail: `docs/phase1e-precision-measurement.md` §2.

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

**Analysis window, binding:** **2019 onward** for the primary specification, with the robustness
ladder of §11 A1. Set empirically from composition stability and anchor-cell adequacy, not asserted.

**Sampling rule, binding:** every Amazon figure comes from `--spread N` block sampling across
disjoint file offsets. This applies **inside** the analysis window too — the window does not remove
the need for it. **A rate measured from a file prefix is never quoted.** This is systematic
sampling, not random sampling, and will be described as such in any write-up.

`Amazon_Fashion` is excluded: its `categories` field is empty in 100% of items, so it yields no cell.

**Body-half assignment** is the §1.3 table of `DESIGN.md`, frozen: dresses, jumpsuits, outerwear,
underwear, accessories, footwear and children's items are excluded; a dress spans both halves and
belongs to neither arm.

---

## 5. Variables

### 5.0 Labelling is BLIND, and the coding guide is fixed first

Two rules, both binding, both settled before any label is entered.

**Blind — and precisely which fields, with the reason for each.**

| Field | Shown? | Why |
|---|---|---|
| `review_id_hash` | shown | Join key. Carries no information. |
| `product_title` | **shown** | See below — the coding rules cannot be applied without it. |
| `review_title`, `review_text` | shown | The object of judgement. |
| `human_label`, `buyer_gender_mismatch` | shown, empty | What the labeller fills in. |
| `assigned_bucket` | **hidden** | The dictionary's guess. Showing it turns the exercise into scoring agreement with a number already in front of you. |
| `gender`, `body_half`, `category_path` | **hidden** | The stratum. Showing it lets the labeller reconstruct the design. |

Row order is shuffled, so order carries no information either. The hidden fields live in a key file
the labeller does not open, re-joined on `review_id_hash` after labels come back.

**Why `product_title` is deliberately NOT blinded.** The coding rules require non-garment items to
be marked `none`, and that rule is not optional: the 0/4 `ran_large` precision on `Amazon_Fashion`
was caused entirely by a purse, two watch straps and a pair of glasses. With review text alone that
rule cannot be applied — *"too big, returned it"* is unclassifiable without knowing whether the
product is a t-shirt or a watch strap, and that is the exact error mode the sample exists to
measure.

Blinding exists to stop the human being anchored to the dictionary's guess. **A product title
carries no signal about which bucket was assigned**, so including it does not compromise that. It
may leak gender, which is the weaker cost: precision by gender is a secondary breakdown, not the
gate.

There is also a consistency argument that settles it independently. The coding guide is developed
against the discarded sample, which carries category information. Applying those rules to a file
that lacks it would make them **unapplicable by construction** — the guide would refer to a
distinction the labeller cannot see.

An earlier version of this section blinded the product title as well. That was over-blinding, and
it is corrected here rather than silently.

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
Prediction: `beta3 > 0`.

### 7.1b Two estimands, named. The choice is substantive, not variance-driven.

Weighting is not a variance-reduction knob -- **it changes what is being estimated.** Both are named
here and one is chosen on substantive grounds, before any MDE is quoted for either.

| name | definition | what it answers |
|---|---|---|
| **`tau_review`** | observation-weighted: every labelled review counts equally | the average over **purchases** |
| `tau_style` | cluster-weighted: every style contributes equally regardless of review count | the average over **styles on offer** |

**`tau_review` is PRIMARY.** The hypothesis in §1.2 is about **buyer behaviour** -- which size a
person chooses when the garment permits escape from fit. The unit that behaviour happens in is a
purchase, not a product listing. `tau_style` would answer a question about catalogue composition,
which is a supply-side question this design is not built for.

`tau_style` is reported as a **secondary** specification, because a large divergence between the two
is informative: it would say the effect is concentrated in heavily-reviewed styles rather than spread
across purchases.

**Every MDE figure in this document and in the artifacts is `tau_review`.** That was the implicit
assumption throughout, and it is now explicit and matches the substantive choice rather than having
been selected to suit it. Switching to `tau_style` would require recomputing all of them.

### 7.1a OPERATIVE MDE — recorded as a number, 2026-08-11

Computed by `src/analysis/run_window_power.py` using `src/analysis/power.py` unchanged, so it is
directly comparable with the Phase 0 table.

| window | anchor cell | no clustering | ICC 0.02 / CV 1 | **ICC 0.05 / CV 1** | ICC 0.05 / CV 2 |
|---|---|---|---|---|---|
| 18 months | 12 | 1.099 | 1.466 | **1.888** | 2.681 |
| 3 years | 151 | 0.337 | 0.450 | **0.579** | 0.823 |
| **5 years (primary)** | **307** | 0.244 | 0.325 | **0.418** | 0.594 |
| 8 years | 394 | 0.218 | 0.291 | **0.375** | 0.532 |
| full history | 431 | 0.212 | 0.283 | **0.364** | 0.518 |

**OPERATIVE FIGURE: MDE = 0.418 SD** at the primary window under Phase 0's realistic central
scenario (ICC 0.05, CV 1.0, m_bar 20).

**The study as currently scoped is powered for a LARGE effect only.** 0.418 SD is outside the
0.20–0.30 SD band Phase 0 called realistic, and well outside §5.16's 0.15 SD. Even the no-clustering
corner is 0.244 SD. **The entire result rests on roughly 300 men's lower-body observations**, and
that is stated here rather than discovered at the estimation stage.

**Where the variance lives**, 5-year window:

| cell | share of Var(tau) |
|---|---|
| men / lower | **43.1%** |
| men / upper | 32.7% |
| women / lower | 16.6% |
| women / upper | 7.7% |

The two men's cells carry **76%** of the variance between them. That is §5.5 in arithmetic.

**Widening the window cannot fix this.** Full history gives only ×1.40 on the anchor cell — MDE
0.364 rather than 0.418 — while readmitting the regime drift the window exists to exclude. Reaching
0.30 SD needs ×1.95 on every cell; 0.25 SD needs ×2.80.

**Dictionary recall is now the principal lever on the binding constraint.** The anchor cell scales
directly with recall, and measured recall is 6.7–51.1% per bucket (§1.2), so the headroom is large —
larger than any available widening of the window. A recall improvement is worth more to this study
than more years of data, and it is the cheapest route to a defensible MDE.

**Two caveats, both stated so the figure is not read as harder than it is.** The counts come from a
600,000-review sample against a 250,000-item index, not from a full-index pass over 66M reviews, so
they are the pessimistic end and the ratios between windows are the durable part. And `m_bar = 20`
is the Phase 0 Mavi figure; Amazon reviews-per-style is unmeasured and enters the design effect
linearly, making it the weakest assumption in the table. **Measuring it is a prerequisite to
treating 0.418 as final.** Everything else in this document is secondary or exploratory and will be
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

### 7.2a Inference: wild cluster bootstrap. Reason: COVERAGE, not the MDE.

**Binding: all inference is by wild cluster bootstrap** (Cameron, Gelbach & Miller 2008) --
Rademacher sign flips at cluster level, null imposed, p-value from the bootstrap distribution of the
cluster-robust t. Implemented in `src/analysis/wild_bootstrap.py`.

**The reason changed once it was measured, and the original reason was wrong.** This section
previously argued that the DEFF formula understates the MDE when one cluster dominates. **It does
not.** Measured on the actual cluster structure (`docs/phase1h-a5-measurements.md` §4.1): formula MDE
0.2562, WCB MDE 0.260, distortion factor **1.01x**. The formula has no explicit term for cluster
dominance but `CV^2` absorbs it -- one cluster of 2,893 among 72 small ones produces a huge CV. So
`MDE_design = 0.568` is not discredited and the λ >= 1.89 arithmetic stands.

**The real reason is size, and it is severe.** Null rejection rate at a nominal 5%, 200 trials:

| scenario | dominant cluster | asymptotic CR | WCB |
|---|---|---|---|
| **KEEP** | 19.2% | **0.185** | **0.040** |
| EXCLUDE | 4.8% | 0.085 | 0.065 |
| SPLIT | 3.7% | 0.100 | 0.070 |

**Under KEEP the asymptotic cluster-robust test rejects true nulls 18.5% of the time at a nominal 5%
-- a false-positive rate 3.7x too high.** WCB returns 0.040.

A test can have a correctly calibrated MDE and still be badly mis-sized: the MDE says what effect the
design can detect, size says how often it cries wolf, and **they are independent.** Here one is fine
and the other is not.

SPLIT is worse-sized (0.100) than EXCLUDE (0.085) despite a smaller dominant cluster -- 6,462
clusters of which most hold one observation is its own problem for the asymptotic approximation, and
even WCB sits slightly high there (0.070). Monte Carlo SE at 200 trials is about 0.015.

**WCB is therefore mandatory in every scenario, including the ones where no single cluster
dominates.**

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

**ANSWERED 2026-08-11 at 20M reviews — PARTIALLY CONFIRMED.** A first attempt at 400,000 reviews
yielded 21 observations and was reported as inconclusive with no statistic quoted. Re-run at
19,999,992 reviews it yielded **1,253 positive-deviation observations across 649 stores**.

Result: **HHI 0.0231** against a spread benchmark of 0.0015; **43.2 effective stores** out of 649;
the top store alone carries **12.85%** of positive deviation; the top 50 carry 53%. Store-level mean
deviation ranges +0.25 to +1.45 among the top 15 — a 1.2-ladder-step spread, which is real
heterogeneity in the seller's ruler.

The pre-registered dichotomy — handful ⇒ calibration, spread ⇒ behavioural — **does not resolve
cleanly, and is reported as unresolved rather than forced to one side.** 43 effective stores is not
a handful; 15× the even-spread benchmark is not thinly spread.

**Consequences, binding:**

1. **The §5.4 deviation measure requires store fixed effects** in any specification, and any result
   from it states that identification leans on a concentrated set of sellers.
2. **The primary `fit_score` measure is protected**, for a structural reason: seller calibration is
   constant within a style, `parent_asin` is nested within store, so the **style fixed effects of
   §7.1 absorb it entirely.** This asymmetry is now an independent argument for `fit_score` as
   primary, additional to the cell-count argument.
3. Refutation condition §8.4 — "`beta3` driven by a small number of sellers" — is **not** triggered
   for the primary specification by this result, because §7.1 already absorbs the mechanism. It
   remains live for any deviation-based specification.

### 9.2 Buyer gender ≠ garment gender

§5.5. Pushes toward a **false positive**, so it cannot be dismissed as attenuation.

### 9.3 Supply-side label inflation

Narrowed: uniform within-gender inflation cancels in `tau`; only inflation that **differs between
upper and lower within a gender** survives. Unmeasurable on Amazon, testable on RentTheRunway.

### 9.4 Text-derived labels are noisy

Confusion is overwhelmingly with `true_to_size` rather than sign-reversal (131 and 13 sign errors in
46,223 rows), which attenuates `tau` toward zero. A biased-toward-null instrument that still finds an
effect is more credible, not less — but the noise is reported, not used as an excuse.

### 9.6 `fit_score` under-captures INTENTIONAL deviation — the Rule 4 limitation

From `docs/coding-guide.md` §4, and the most consequential limitation of the outcome measure.

The coding rule is to record the garment's physical relation to the body, not the buyer's
satisfaction: *"Perfect fit. Loose, but still flattering"* is `ran_large`. That rule is right, and
coding satisfaction instead would make the measure blind to the phenomenon under test.

**But it does not fully rescue the measure.** A buyer who sized up deliberately and is pleased may
not describe the looseness at all — they write that the item is good and say nothing about fit.
Those reviews yield no signal in either direction and simply fall out of the sample.

**So `fit_score` captures unintended misfit more completely than intended deviation — and intended
deviation is exactly what H1 and H2 predict.** The measure is therefore biased against the
hypothesis. Two consequences, both binding:

1. An effect found under this measure is **stronger** than its face value, because the instrument is
   insensitive to the mechanism it is testing. This is not a licence to inflate the estimate; it is
   a statement about the direction of the bias, and the estimate is reported as measured.
2. **A null result is correspondingly weaker as evidence against the hypothesis.** §8.1 —
   `beta3` ≤ 0 — must be read with this in mind, and the write-up says so rather than treating a
   null as clean.

This is the principal reason the §5.4 self-reported deviation measure is retained despite its own
problems: it captures intentional deviation **directly**. The two measures have opposite weaknesses,
which is what makes them worth carrying together rather than one being redundant.

### 9.7 Differential measurement error, and which estimate is confirmatory

Measured attenuation (`docs/phase1f-attenuation.md`): **λ = 0.763 pooled** [0.621, 0.927],
**λ_men = 0.741** [0.570, 0.978], **λ_women = 0.784** [0.551, 1.000].

The two gender-specific factors differ by 0.043 with intervals that overlap almost entirely, so
**there is no evidence of differential error — and the sample cannot exclude it either.** 149 rows
split by gender cannot resolve a difference of that size.

**Why this matters for the estimand.** If error were non-differential the measured quantity would be
a clean `λ·tau`, and dividing by λ would recover the truth. If it is differential the measured
quantity is instead

    tau_measured = λ_men · Δ_men − λ_women · Δ_women

which is **not** `λ·tau` for any single λ, and no scalar correction recovers `tau`. Worse, the
direction of the resulting bias **cannot be signed in advance**: it depends on the signs and relative
magnitudes of `Δ_men` and `Δ_women`, which are the very things being estimated. A correction applied
without knowing them could move the estimate either way.

### 9.8 `Delta_men` is not separately identified -- the §1.5 / §1.4 tension

**Shipping the men's arm alone is not on the table**, and it is worth writing down why, because the
§1.5 placebo logic makes it tempting and the temptation grows every time `tau` looks underpowered.

§1.5 draws its force from the within-man comparison: the same man's waist is not a different size
from his torso, so an upper-versus-lower gap cannot be body composition. **But it can be tailoring.**
Upper-body garments may simply be cut more generously for everyone, and that common shift makes
`Delta_men` differ from zero with no vanity involved. **Removing precisely that common shift is why
`tau` exists** -- the outer difference against women subtracts whatever is common to upper-versus-
lower across both genders.

So `Delta_men` is a **diagnostic**, not a publishable result. Its DEFF and MDE are measured because
they say which arm binds the design; they license no men's-only paper.

**Within men, the object is the three-category gradient rather than the two-level difference.** A
common cut shift need not be monotone in the predicted order tee > shirt > jeans, so the ordering
carries information the pooled difference discards. That makes it a better diagnostic; it does not
make it identified.

§1.4 names `tau` as the estimand, unchanged.

### 9.7a The residual `δ` is a term in `tau`, not a diagnostic

Measured `2026-08-14` (`docs/phase1g-style-definition.md` §4): **δ_men = +0.170, δ_women = +0.047**.
The gap of 0.123 is **three times** the λ gap.

From `E[y|cell] = c + λ·E[y*|cell] + δ·p₀(cell)`, the constant cancels in the double difference and
`δ·p₀` does not:

```
tau_measured = [λ_m·Δ*_m + δ_m·Δp₀_m] − [λ_w·Δ*_w + δ_w·Δp₀_w]
```

**So `tau` is biased whenever `δ` differs across genders and `Δp₀ ≠ 0`, even if `λ_men = λ_women`.**

**Measured bias: −0.0068 SD, 95% CI [−0.0260, +0.0172]** — 2.3% of the 0.30 SD target, sign not
established. `δ` comes from the 149 labels; `Δp₀` from the full analysis population, so the
uncertainty is essentially all on the label side and the interval above is a cluster bootstrap over
them.

**The direction runs AGAINST the hypothesis here, and that is not something to rely on.** A positive
δ pushes truly-fitting garments toward `ran_large`, which inflates the men's *level* — the direction
the hypothesis predicts. But the level cancels in the within-gender difference, and what survives
depends on the sign of `Δp₀`. Men's lower cell holds more truly-`true_to_size` items than men's
upper (0.574 vs 0.539), so the push is larger in the lower cell and the men's difference is pushed
**down**. **`Δp₀ > 0` would reverse this and the residual would mimic the effect.** The sign is a
property of this corpus under this window and dictionary; it is recomputed whenever any of those
change, never assumed.

**Binding: no output reports λ without δ.** They are two coefficients of one expansion, and λ alone
describes the measurement only under `δ = 0`, which is false.

**Fixed in advance, and binding:**

1. **The PRIMARY estimate is reported UNCORRECTED.** It is the measured `tau`, attenuated, and
   labelled as such. It is the confirmatory number.
2. **The λ-correction is a SENSITIVITY analysis**, reported alongside and never in place of the
   primary. Both the single-λ version (`tau/λ`) and the gender-specific version are shown.
3. **If the two disagree materially, that disagreement is the finding** and is reported as evidence
   that measurement error is differential — not resolved by picking whichever is more convenient.

This ordering is fixed now, before any estimate exists, precisely because the choice between a
corrected and an uncorrected headline is exactly the kind of decision that becomes unprincipled once
the numbers are visible.

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
| 2026-08-11 | **A1 - §5.8 time window reopened and re-set to 5 years (2019 onward), with a robustness ladder.** COMPLETE | Regime drift measured; the 12-18 month default yields 12 anchor-cell observations |
| 2026-08-11 | A2 - labelling made blind; coding guide required as Appendix A before labelling (§5.0) | An unblinded measurement is not a measurement |
| 2026-08-11 | A3 - `product_title` un-blinded in the labelling file (§5.0) | The non-garment coding rule cannot be applied to review text alone; a product title carries no signal about the assigned bucket |
| 2026-08-11 | **A4 - fixed effects moved off style level; §7.1a primary/secondary corrected.** COMPLETE | The style-FE specification was unidentified. See below. |
| 2026-08-14 | **A8 - `MDE_target` locked at 0.30 SD, before the A5 decision.** COMPLETE | The easiest mistake available; locked so it cannot drift. |
| 2026-08-14 | **A7 - the ~80% precision gate replaced by an attenuation gate `λ >= λ_min`.** COMPLETE | 80% was an underived convention unconnected to the target effect size. See below. |
| 2026-08-14 | **A6 - coding guide Rule 8 sharpened; Rule 1/4 boundary clarified.** COMPLETE | `calibration_stated` was duplicating `human_label`; four boundary rows needed a binding reading. See below. |

### A9 - transfer condition on `λ`, `δ` and `Δp₀`

**Dated 2026-08-15.** `λ`, `δ` and `Δp₀` are properties of the **analysis population**, not constants
of the dictionary. They were measured on 149 hand labels from one window, one seller mix and one
review register.

**Binding:** a materially different analysis population -- a different corpus, a different window, a
different scope, or a scale change that materially moves the composition -- **requires a fresh
hand-labelling round** before those quantities may be quoted for it. New blind draw, new coding pass
under the frozen guide, recomputed λ, δ and Δp₀.

The cost is recorded now rather than discovered later: that is roughly 150-300 hand judgements per
population, plus the re-derivation in `src/analysis/attenuation.py`.

**A note on what "materially different" means here.** Scaling more deeply within
`Clothing_Shoes_and_Jewelry` under the same window is the mildest case, since it samples the same
population harder rather than a new one. But the share held by catalogue listings is itself one of
the quantities being measured, and if it moves materially the labelled sample's composition moves
with it. The trigger is a change in composition, not merely in `n`.

### A8 - the target effect size is LOCKED at 0.30 SD

**Dated 2026-08-14. Fixed BEFORE the §11 A5 mega-listing decision, and before any
estimate of `tau`.**

`MDE_target = 0.30 SD`. It is not a new number: it is the pessimistic end of the
0.20-0.30 SD band the Phase 0 power analysis established as realistic for this design
(`docs/phase0-collection-blocker-and-power.md` §3.3), computed on Mavi before Amazon was
in scope and therefore uncontaminated by anything measured since.

**It will not be moved.** Not to 0.35, not to "a moderate effect", not to whatever the
final MDE happens to be. Every quantity downstream of it -- `λ_min = MDE_design /
MDE_target`, the gate verdict, the A5 decision -- inherits its authority from the target
having been fixed in advance. A target adjusted after seeing that something does not fit
inside it converts the whole apparatus into a description of what we found.

**This is the single easiest mistake available in this project**, because the machinery
is now elaborate enough that a small change here propagates invisibly: raising the target
to 0.35 would lower `λ_min` to 0.63, and every straddling interval in this document would
become a clean pass without a word being written about why.

If a later finding genuinely justifies a different target -- for instance a published
effect size for this phenomenon that makes 0.30 obviously wrong -- it is changed by a
dated amendment here that states what the old value was, what the new one is, what
evidence forced it, and **which verdicts flip as a result**. Never silently.

### A7 - the precision gate is replaced by an attenuation gate

**No estimate of `tau` had been run at the time of this amendment, and none has been run since.**

**Removed:** "hand-verified precision of each fit bucket >= ~80%". It was an underived convention,
never connected to the effect size the study needs to detect, and a per-bucket rate is the wrong
shape -- two dictionaries with identical precision can attenuate `tau` by very different amounts
depending on which way their errors go.

**Adopted:** `MDE_operative = MDE_design / λ`, gate `λ >= λ_min = MDE_design / MDE_target`. With
`MDE_target = 0.30` and `MDE_design = 0.219`, **λ_min = 0.73**.

**Measured result:**

Quoted at **store** clustering on the 139 store-resolved rows:

| subset | λ (forward) | 95% CI | verdict vs λ_min = 0.73 |
|---|---|---|---|
| as-is | 0.741 | [0.590, 0.920] | point above, **interval straddles** |
| **§5.3 routing** (operative) | **0.878** | [0.723, 1.000] | point above, **interval straddles** |
| men, as-is | 0.721 | [0.552, 1.000] | **point BELOW**, interval straddles |
| women, as-is | 0.761 | [0.513, 1.000] | point above, interval straddles |

**THE GATE IS NOT PASSED, AND NOT FAILED.** In every specification the point estimate sits above
λ_min and the interval spans it. This is a statement about **149 hand labels**: the interval is
roughly ±0.17 wide and cannot resolve λ_min unless the truth is far from it.

Neither upper bound is informative -- both pin at **1.000**, the boundary the percentile bootstrap
cannot cross, and λ <= 1 by construction.

**The §5.3 routing helps substantially and still does not clear the gate**: λ 0.741 -> 0.878,
interval lower bound 0.590 -> 0.723 against a threshold of 0.730. That is independent support for a
decision made on precision grounds, not a pass.

**Operative MDE:** 0.287 SD pooled with mega-listings excluded; **0.745 SD if they are kept.** The
gate is unsatisfiable in the second case, since it would require λ >= 1.89.

**A methodological correction inside this amendment.** The brief specified
`s_k = Σ_j P(true=j | assigned=k)·score(j)`, `λ = (s_large − s_small)/2` -- the REVERSE conditional.
Attenuation of a misclassified outcome is governed by the FORWARD conditional `P(assigned | true)`,
which is what makes `MDE_design / λ` correct; using the reverse in that formula inverts the
direction of the correction. Both are computed. The two differ by 0.014 here (0.763 vs 0.749), so
the distinction is numerically small in this instance -- but it is recorded because it could have
been large, and because the formula must be right for reasons that do not depend on this dataset.

### A6 - coding-guide amendments following the labelling pass

**No estimate of `tau` had been run at the time of this amendment, and none has been run since.**

**Rule 8 sharpened.** `calibration_stated` now requires the review to name a brand, manufacturer or
regional convention **as the cause** of the sizing. "Runs big" is an observation; "these must all be
tiny asia sizes" is an attribution. Without the restriction the flag duplicates `human_label` and
carries no independent information. The 149 rows were re-coded: **27 flagged under the loose
reading, 3 under the sharpened one (2.0%, lower bound).**

**Rule 1 / Rule 4 boundary fixed.** Four rows were genuine judgement calls -- a deliberate size-up
where the buyer is content with the resulting looseness. The binding reading, applied consistently
and now written into the guide: **code the realized fit of the garment received, even when the
looseness was intended.** A deliberate size-up producing a loose garment is `ran_large`.

**An uncovered contamination type** is recorded but not fixed: an adult women's product reviewed for
a 7-year-old wearer. §1.3 excludes children's products, not child wearers of adult products. One
occurrence in 149 rows does not justify a rule.

### A4 - the fixed-effects level, and the §7.1a correction

**No estimate of `tau` had been run at the time of this amendment, and none has been run since.**

**What was wrong.** §7.1 and `DESIGN.md` §1.4 specified style-level fixed effects. That
specification **cannot estimate its own estimand**: gender and body half do not vary within a style,
so `male`, `upper` and `male x upper` are perfectly collinear with the style dummies and none of the
three coefficients is identified. Confirmed on the drawn sample -- 170 styles, **zero** spanning more
than one gender x body-half cell. Full detail: `docs/phase1d-specification-error.md`.

**Seller FE was proposed and measured, and it does not work.** Of 2,014 sellers carrying 16,027
labelled observations, 67.50% span a single cell and are absorbed entirely. Only **30 sellers**
(15.74% of observations) span three or more cells, which is what identification of the interaction
requires. The anchor cell retains 37.3%. Resting the estimand on thirty sellers is not a primary
specification, and it is reported as unviable rather than adopted because it was the proposal.

**Adopted instead:**

| element | before | after |
|---|---|---|
| fixed effects | style (`parent_asin`) | **garment category** |
| seller | absent | **covariate** |
| standard errors | clustered on style | **unchanged** -- clustered on style |
| calibration covariate | style-level | **unchanged** |

Within a garment category `upper` is constant but `male` varies, so `beta3` is identified as the
difference in the male coefficient between upper-body and lower-body categories. This uses every
observation instead of 15.74% of them.

**Cost, stated rather than glossed:** seller FE would have absorbed the §9.1 calibration confound
directly. A seller covariate does not. **§9.1 therefore stays OPEN** and is not closed as a
by-product.

**Retained as robustness:** seller FE on the 30-seller subsample. Low-powered, but a within-seller
replication differences calibration out entirely, so it is a strong test despite its size. Published
whatever it shows.

**The §7.1a correction.** That section reported the MDE of the WIDE upper/lower sample against a
claim about the PRIMARY gradient specification. Measured cells at 3,000,000 reviews:

| sample | men/up | men/low | wom/up | wom/low | smallest |
|---|---|---|---|---|---|
| wide (secondary) | 2,385 | 2,005 | 8,465 | 3,174 | 2,005 |
| gradient (primary) | 1,433 | 1,644 | 5,895 | 1,548 | 1,433 |

The gradient is thinner but modestly -- 66% of the wide sample. **The primary specification is NOT
re-ranked**, and no amendment to which test is confirmatory is proposed or needed.

### A5 - `parent_asin` is not reliably a style. PROVISIONAL DEFAULT: KEEP.

**STATUS: OPEN. Provisional default KEEP. Resolution depends on measurements 0, 1 and 4 below. No
estimate of `tau` has been run, before or since.**

`m_bar` and CV were assumed from Phase 0's Mavi figures. Measured on Amazon:

| | m_bar | CV | DEFF (ICC 0.05) | MDE (wide) |
|---|---|---|---|---|
| Phase 0 assumption | 20.00 | 1.00 | 2.95 | 0.177 |
| **measured, all styles** | **4.571** | **11.31** | **30.40** | **0.568** |
| measured, excluding heaviest listing | 3.740 | 4.26 | 4.54 | 0.219 |

Cause: **2,916 labelled observations, 18.2% of the sample, sit in one `parent_asin`** -- a
print-on-demand listing whose single parent covers a catalogue of designs. Median across styles is 1.
`DESIGN.md` §1.6 treats `parent_asin` as a style; for these sellers it is a product line. Structural
evidence: `docs/phase1g-style-definition.md`.

#### Why deferring this does not damage the pre-registration

Stated as a general test rather than an excuse for this instance:

> **A decision may be deferred pending measurement if and only if the pending measurement is not a
> function of the outcome.**

Whether a listing prints many designs onto one blank garment carries **zero information about
`tau`**. So does the survival rate of its reviews under a filter, and so does a cluster-size
distribution. None of the three pending measurements can indicate which way the estimate will come
out. What damages a pre-registration is deciding **after seeing the result**; measuring **structure**
and deciding on that is what a pre-registration is for.

By contrast, "exclude them and see whether the MDE improves" **would** be illegitimate -- and that is
how this question was framed until 2026-08-14, which is why the framing was replaced.

#### The three pending measurements

**0 -- do the filters already in force dissolve the problem?** The §5.8 window, the
`verified_purchase` decision and the §1.3 mapping are already in the design. If the failing listings
lose most of their observations to filters we already apply, there is nothing to decide. Cheapest
question, asked first.

**1 -- is a mega-listing ONE calibration unit?** Parent-level clustering assumes so, and that
assumption was previously asserted as though it were evidence. It was not measured; that was an
error. Three sub-questions, one answerable:

- *single store?* Trivially yes by construction -- `store` is a field on the parent's metadata row.
  Only checked for asins appearing under two parents.
- *one size grid?* **NOT MEASURABLE.** Reviews carry `asin`, `parent_asin`, `rating`, `text`,
  `title`, `timestamp`, `user_id`, `verified_purchase` and nothing else -- no size field -- and
  metadata is parent-level.
- *homogeneous fit across asins?* **Measurable, and the real test.**

**4 -- separate DEFF and MDE for `Delta_men`, `Delta_women` and `tau`** under each scenario. What may
and may not be concluded from it: §9.8.

#### REFUTATION CONDITION, recorded in advance

**If measurement 1 shows the mega-listing is not a single calibration unit** -- heterogeneous fit
distributions across its asins -- **then parent-level clustering was wrong from the start, 0.568 is
an artefact of the wrong clustering, and the decision turns toward SPLIT.**

Written before the measurement so a heterogeneous result cannot later be reread as supporting
whatever is convenient.

#### The objection to excluding is NOT "differential filtering"

An earlier version objected on the ground that exclusion's incidence across cells is asymmetric.
**That argument was weak and is withdrawn.** A rule defined on product structure and applied
everywhere may have asymmetric incidence; that alone is not bias.

The correct objections are two, and stronger:

1. **A slogan t-shirt is a t-shirt.** Its buyer made exactly the size choice under study. Excluding
   it discards an **in-target behavioural observation** because of an **off-target accounting
   property** of how a seller organised their catalogue.
2. **It shifts the population from "garments purchased" to "styles"**, and because the shift is
   unequal across the four cells, the cells begin describing different populations.

#### MEASUREMENT RESULTS, 2026-08-15 -- `docs/phase1h-a5-measurements.md`

**0 -- the filters do not dissolve the problem; they concentrate it.** `verified_purchase` is 98.4%
on the mega-listing and the window does not bite on recent listings, so survival is 95.3%. The
failing listings' share of the analysis sample **rises from 18.61% to 23.23%** once the filters are
applied, because they remove proportionally more from conventional listings, whose reviews are older.
"The filters handle it" is off the table.

**1 -- UNTESTABLE. A third outcome, not pre-specified.** Of 12,725 asins under `B07TVHSDMQ`, 2,765
carry at least one labelled review and **2 carry five or more**; the other two failing listings have
none. Fit homogeneity across designs cannot be computed. The **pre-registered refutation condition is
therefore neither triggered nor cleared**, and is reported that way rather than pressed into either
branch.

**And untestability does NOT favour SPLIT.** A cluster-robust estimator imposes **no structure** on
within-cluster correlation -- it requires only independence *between* clusters. So KEEP asserts
**nothing** about how the 12,725 designs are correlated, while SPLIT asserts that correlation is
**zero**. KEEP is **assumption-minimal**, not merely conservative, and the difference matters:
conservatism is a preference, declining to assert an unmeasurable quantity is a standard.

The MDE ordering (SPLIT 0.132 < EXCLUDE 0.156 < KEEP 0.412) is a mechanical restatement of how much
each option assumes away, **not evidence about which is right.**

**4 -- the men's arm binds.**

| scenario | DEFF | MDE `tau` | MDE `Δ_men` | MDE `Δ_women` |
|---|---|---|---|---|
| KEEP | 31.64 | **0.412** | 0.341 | 0.232 |
| EXCLUDE | 3.95 | 0.156 | 0.120 | 0.099 |
| SPLIT | 3.27 | 0.132 | 0.110 | 0.074 |

All are the gradient trend per step. **0.412 and the earlier 0.568 are different objects** -- gradient
trend against the wide 2x2 contrast -- and neither supersedes the other. KEEP alone falls outside the
locked 0.30 target.

**What this does to the decision.** The strongest practical objection to KEEP was never its MDE, which
is honest at 0.412; it was that the standard errors would have been wrong by a factor of nearly four.
§7.2a settles that with WCB. KEEP is now the option that assumes least *and* reports honestly.

#### DECISION RULE: bound, do not choose

The three options are not rival guesses at one right answer. They are **points on an interval in an
unmeasurable parameter** -- the correlation of labelling errors across designs within a listing.
SPLIT sits at the zero-correlation end; KEEP sits at the assumption-minimal end. When a parameter
cannot be measured, the honest output is a **bound**, not a point. This is the same logic as the
Manski-style bounds §5.2 already applies to selection.

**BINDING:**

1. **PRIMARY: KEEP**, on assumption-minimality. It asserts nothing about the unmeasurable
   correlation.
2. **SPLIT and EXCLUDE are reported as PRE-SPECIFIED SENSITIVITY**, always, whatever they show.
3. **A finding is claimed only if it survives under KEEP.** If a result is significant only under
   SPLIT, **that significance is a product of the independence assumption** and is written that way
   -- as a statement about what follows *if* errors are uncorrelated across designs, not as a
   finding.

**Recorded alongside: SPLIT is also the worse-sized option.** Null rejection at nominal 5% is 0.100
for SPLIT against 0.085 for EXCLUDE, and even under wild cluster bootstrap SPLIT sits at 0.070 --
6,462 clusters of which most hold a single observation is its own problem for the approximation. So
the option that buys the smallest MDE is also the one whose inference is least trustworthy, which is
not a coincidence.

#### The three positions

1. **Keep** -- take the data as it is. **Primary.**
2. **Exclude** -- and state the population change explicitly. Sensitivity.
3. **Split** -- cluster on `asin` for listings failing the structural test. Sensitivity, and the
   assumption it imposes is named whenever it is quoted.

### A4 - the fixed-effects level, and the §7.1a correction

**No estimate of `tau` had been run at the time of this amendment, and none has been run since.**

**What was wrong.** §7.1 and `DESIGN.md` §1.4 specified style-level fixed effects. That
specification **cannot estimate its own estimand**: gender and body half do not vary within a style,
so `male`, `upper` and `male x upper` are perfectly collinear with the style dummies and none of the
three coefficients is identified. Confirmed on the drawn sample -- 170 styles, **zero** spanning more
than one gender x body-half cell. Full detail: `docs/phase1d-specification-error.md`.

**Seller FE was proposed and measured, and it does not work.** Of 2,014 sellers carrying 16,027
labelled observations, 67.50% span a single cell and are absorbed entirely. Only **30 sellers**
(15.74% of observations) span three or more cells, which is what identification of the interaction
requires. The anchor cell retains 37.3%. Resting the estimand on thirty sellers is not a primary
specification, and it is reported as unviable rather than adopted because it was the proposal.

**Adopted instead:**

| element | before | after |
|---|---|---|
| fixed effects | style (`parent_asin`) | **garment category** |
| seller | absent | **covariate** |
| standard errors | clustered on style | **unchanged** -- clustered on style |
| calibration covariate | style-level | **unchanged** |

Within a garment category `upper` is constant but `male` varies, so `beta3` is identified as the
difference in the male coefficient between upper-body and lower-body categories. This uses every
observation instead of 15.74% of them.

**Cost, stated rather than glossed:** seller FE would have absorbed the §9.1 calibration confound
directly. A seller covariate does not. **§9.1 therefore stays OPEN** and is not closed as a
by-product.

**Retained as robustness:** seller FE on the 30-seller subsample. Low-powered, but a within-seller
replication differences calibration out entirely, so it is a strong test despite its size. Published
whatever it shows.

**The §7.1a correction.** That section reported the MDE of the WIDE upper/lower sample against a
claim about the PRIMARY gradient specification. Measured cells at 3,000,000 reviews:

| sample | men/up | men/low | wom/up | wom/low | smallest |
|---|---|---|---|---|---|
| wide (secondary) | 2,385 | 2,005 | 8,465 | 3,174 | 2,005 |
| gradient (primary) | 1,433 | 1,644 | 5,895 | 1,548 | 1,433 |

The gradient is thinner but modestly -- 66% of the wide sample. **The primary specification is NOT
re-ranked**, and no amendment to which test is confirmatory is proposed or needed.

### A5 - clustering parameters measured; `parent_asin` is not reliably a style

`m_bar` and CV were assumed from Phase 0's Mavi figures. Measured on Amazon:

| | m_bar | CV | DEFF (ICC 0.05) | MDE (wide) |
|---|---|---|---|---|
| Phase 0 assumption | 20.00 | 1.00 | 2.95 | 0.177 |
| **measured, all styles** | **4.571** | **11.31** | **30.40** | **0.568** |
| measured, excluding heaviest listing | 3.740 | 4.26 | 4.54 | 0.219 |

`m_bar` is a quarter of the assumed value, which helps. **CV is eleven times it, which hurts far
more**, since it enters as `CV^2 + 1`.

The cause: **2,916 labelled observations -- 18.2% of the sample -- sit in a single `parent_asin`**, a
print-on-demand novelty listing whose one parent covers a whole catalogue of designs. Median across
styles is 1. `DESIGN.md` §1.6 treats `parent_asin` as a style; for these sellers it is a product
line.

**STRUCTURAL QUESTION ANSWERED 2026-08-14** -- `docs/phase1g-style-definition.md`. The framing
"exclude mega-listings or not" was unanswerable, because the MDE consequence of each answer was
already known. Asked as DESIGN.md 1.6's own question -- when is a `parent_asin` a style? -- it is
settled on structure without consulting the MDE:

`B07TVHSDMQ` carries **12,004 distinct asins** against a typical parent's median of **17**, at ~1
review per asin, and its review titles name unrelated products ("The boiler tshirt", "Vote tshirt"
under a civil-engineering slogan listing). **It is not a style.** By contrast a Hanes sweatshirt with
150 asins and 20.5 reviews each IS a style, and a heavy one -- heaviness is not the criterion. The
criterion is whether the asin count exceeds what the garment's size grid can generate.

**Reviews per asin does not discriminate** (1.15 heavy vs 1.26 typical) and is recorded as a failed
statistic.

**THE DECISION THAT REMAINS IS NOT ABOUT POWER.** The heavy listings supply **41.76% of women/upper
and 0.00% of women/lower**. Excluding them removes 42% of one arm of the women's within-gender
contrast and none of the other, reshaping what that difference measures. Men's cells are affected
more evenly (24.15% vs 14.11%).

Three coherent positions, to be chosen by the owner and fixed here before estimation:

1. **Exclude**, and state the population change -- the study describes conventional apparel.
2. **Keep**, and accept MDE 0.568 as the honest figure for the data as it is.
3. **Split the parent** -- cluster on `asin` for listings failing the structural test. Neither
   discards observations nor pretends one listing is one style. This option did not exist before the
   measurement.

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

**MEASURED 2026-08-11 — `docs/phase1c-time-window.md`.** Still no estimate of `tau` run, at the
time of measurement or since.

The three composition series become jointly flat from **2019**: mean review length settles into the
163–185 band after 2015, verified-purchase share into 88–96% after 2013, and fit-label share — the
series the outcome is built from, and the slowest to settle — into 16–18% from 2019.

Anchor-cell counts by candidate window (men's lower body, per the 600,000-review sample):

| window | from | **men's lower** | labelled total |
|---|---|---|---|
| 18 months | 2022 | **12** | 4,617 |
| 3 years | 2021 | 151 | 36,781 |
| **5 years** | **2019** | **307** | **66,133** |
| 8 years | 2016 | 394 | 88,071 |
| full history | all | 431 | 96,913 |

**The 12–18 month default of §5.8 yields twelve observations in the anchor cell and is therefore
unavailable** — not underpowered, unavailable: twelve style-clustered observations cannot support
the placebo test that carries the identification claim.

**PRIMARY WINDOW: 5 years, 2019 onward.** It is the only candidate satisfying both criteria at
once — it begins where composition flattens, and it gives the anchor cell 307 observations, 25× the
18-month figure. Extending to 8 years buys 87 more anchor observations at the cost of readmitting
2016–2018, when fit-label share was still drifting; that trade belongs on the ladder, not in the
primary.

**ROBUSTNESS LADDER, published whole:** 18 months (flagged underpowered, present for completeness
only), 3 years, **5 years (primary)**, 8 years, full history (with the survivorship caveat
attached). `tau` is estimated at every rung. Monotone movement across the ladder is itself a finding
and is reported as one, not resolved by choosing a rung.

**Amendment complete.** The window is fixed at 2019 onward for the primary specification.


---

## Appendix A — Coding guide for `human_label`

**STATUS: COMPLETE. `docs/coding-guide.md` v1.0, frozen 2026-08-11, incorporated here by
reference and forming part of this pre-registration.**

Written by the repository owner against the discarded, never-labelled sample of 2026-08-08
(`data/processed/precision_sample_DISCARDED_2026-08-08_for_coding_rules.*`), which is outside the
analysis window and part of no measurement. Rules developed on one sample and applied to a
different one cannot be tuned to the cases they will be scored on.

**The question the labeller answers** (guide §0): *relative to the buyer's own body, did the garment
they actually received run small, fit, or run large?* Not whether the product is correctly
calibrated against its label; not whether the buyer was happy.

**Rules, in brief** — the guide is authoritative and this is a map, not a substitute:

| § | Rule |
|---|---|
| 1 | Adjustment reports: code the fit of the size **actually received**. Advice to other shoppers describes the product, not the wearer, and is ignored. |
| 2 | **Wearer, not buyer.** Buying on someone else's behalf is not a mismatch; a fit judgement given for a body whose gender differs from the product's is. |
| 3 | A single region suffices if the direction is clear. Conflicting regions, or a judgement conditioned on a hypothetical body, are `unclear`. |
| 4 | **Physical fit, not satisfaction.** "Perfect fit. Loose, but still flattering" is `ran_large`. |
| 5 | Code fit **as first worn**; shrinkage follows the sizing decision rather than constituting it. |
| 6 | Code only the product the review is attached to. |
| 7 | Non-garment items are `none`, however fit-like the language. |
| 8 | `calibration_stated` when the review attributes sizing to the brand or a regional convention. |

**Three structural consequences, all applied:**

1. `buyer_gender_mismatch` is renamed **`wearer_gender_mismatch`**. This is a change of concept, not
   of label: what matters is whose body the judgement describes, not who paid.
2. **`calibration_stated`** is added, giving a manual upper bound on the §9.1 confound that does not
   wait on the corpus-scale seller analysis.
3. The **Rule 4 limitation** is recorded in §9.6 below and in `DESIGN.md` §5.1.

**Convergence worth recording.** Guide §1 and §5.3 of this document were written independently — the
guide by the repository owner from sample text, §5.3 from the ModCloth per-pattern diagnosis — and
reached the same rule: adjustment-advice language describes the product's calibration and is
excluded from `fit_score`. That is weak evidence the rule follows from the design rather than from
taste, and it is recorded as weak evidence, not as confirmation.

Any change to the guide follows the §11 amendment protocol and requires re-labelling the affected
rows: rules changed mid-pass produce an inconsistent measurement.
