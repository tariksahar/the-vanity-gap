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
| WCB needed for inference | secondary | **primary — asymptotic test overrejects 4.1×, and every scenario is mis-sized** |

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

### 2.2 Untestability does NOT favour SPLIT — and KEEP is assumption-MINIMAL, not merely conservative

An earlier draft of this section said parent-level clustering "assumes errors are perfectly
correlated within the catalogue". **That is wrong and it understated KEEP.**

A cluster-robust variance estimator **imposes no structure at all on within-cluster correlation** —
it admits an arbitrary within-cluster covariance matrix. The only thing it requires is
**independence between clusters**. So clustering at `parent_asin` is not a claim about how the
12,725 designs are correlated; it is the **absence** of such a claim.

| option | what it asserts about correlation across the 12,725 designs | |
|---|---|---|
| **KEEP** (cluster = parent) | **nothing.** Arbitrary within-parent correlation is permitted | **assumption-minimal** |
| **SPLIT** (cluster = asin) | **zero.** Independence across designs is imposed | assumes an unmeasured quantity is 0 |
| EXCLUDE | nothing — but only about the rows it retains | assumption-minimal on a smaller population |

**The distinction matters because conservatism is a preference and assumption-minimality is a
virtue.** Preferring a wider interval is a taste; declining to assert something you cannot measure is
a standard. Faced with a correlation that §2 established is **unmeasurable on this corpus**, the
right posture is the method that does not pretend to know it.

The MDE ordering — SPLIT 0.132 < EXCLUDE 0.156 < KEEP 0.412 — is therefore a mechanical restatement
of how much each option assumes away, not evidence about which is right. **Reading it as support for
SPLIT would be selecting the option that asserts the most and calling it the most precise.**

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

### 4.2 Is asymptotic inference valid? No — in every scenario.

Null rejection rate at a nominal 5%. **The asymptotic test needs no bootstrap, so it is run at
2,000 trials while WCB gets 300 × 99** — the headline number therefore carries a tight interval.
Wilson intervals at 95%:

| scenario | dominant cluster | **asymptotic CR** | ratio to nominal | **WCB** |
|---|---|---|---|---|
| **KEEP** | 19.2% | **0.207** [0.190, 0.226] | **4.1× [3.8×, 4.5×]** | 0.047 [0.028, 0.077] |
| EXCLUDE | 4.8% | **0.079** [0.068, 0.092] | **1.6× [1.4×, 1.8×]** | 0.050 [0.031, 0.081] |
| SPLIT | 3.7% | **0.064** [0.054, 0.075] | **1.3× [1.1×, 1.5×]** | 0.037 [0.021, 0.064] |

**Under KEEP the asymptotic cluster-robust t rejects true nulls 20.7% of the time at a nominal 5% —
four times too often, with the interval nowhere near nominal.** WCB returns 0.047.

This is a **coverage** failure, not an MDE failure. A test can have a correctly calibrated MDE and
still be badly mis-sized: the MDE says what effect the design can detect, size says how often it
cries wolf, and **they are independent.** Here one is fine and the other is not.

#### 4.2.1 The sharper run changed a conclusion, not just a decimal

An earlier 200-trial run gave 0.185 / 0.085 / 0.100. All three point estimates sit inside the new
intervals, so nothing was wrong — but at 200 trials **neither EXCLUDE nor SPLIT could be
distinguished from nominal**, and SPLIT's 0.100 looked worse than EXCLUDE's 0.085 when in fact it is
better (0.064 against 0.079).

At 2,000 trials **all three intervals exclude 0.050.** Even SPLIT, whose largest cluster is 3.7% of
observations, is mis-sized at 1.3× with a lower bound of 0.054.

**That kills the natural rule.** A trigger of the form "use WCB when a single cluster exceeds 10% of
a cell" would have passed EXCLUDE and SPLIT through as safe, and both are demonstrably mis-sized. The
supported rule is therefore **unconditional**, and it is supported by measurement rather than by
caution.

**Consequence: wild cluster bootstrap is mandatory for all inference in this project, with no
dominance threshold.** Recorded in `PREREGISTRATION.md` §7.2a.

### 4.3 What this does to the A5 decision

It removes the strongest practical objection to KEEP. The real risk of keeping the mega-listings was
never the MDE — 0.412 is an honest number — it was that we would have reported standard errors that
were wrong by a factor of four. **With WCB that risk is handled**, and KEEP becomes the option
that assumes least and now also reports honestly.

---

## 5. Two questions, separated

They have been reading as one uncertainty and they are not.

### 5.1 "Is it a style?" — CLOSED, and it needed no inference

`B07TVHSDMQ` carries **12,725 distinct designs** under one listing. That is a directly observed
count, not an estimate, and it does not meet the `DESIGN.md` §1.6 definition of a style. The review
titles corroborate it — "The boiler tshirt", "Vote tshirt" under a civil-engineering slogan listing.
**Closed. No further measurement can change it and none is pending.**

### 5.2 "How are the errors correlated?" — OPEN, and unmeasurable here

Whether labelling errors are correlated across those 12,725 designs is a different question, and it
is the only one still open. §2 established it cannot be answered on this corpus: two asins carry
five or more labelled reviews.

**This is the question the clustering choice turns on, and it is not the same as the style
question.** Answering the first does not answer the second, and conflating them made the whole thing
read as a single unresolved doubt when one half is settled.

## 6. Standing

A5 remains **open with provisional default KEEP**, on the assumption-minimality argument of §2.2
rather than on conservatism. What the measurements changed:

- measurement 0 removes "the filters handle it" from the table;
- measurement 1 separates two questions that had been travelling together (§5.1);
- measurement 4 confirms the men's arm binds and that KEEP alone falls outside the 0.30 target;
- the WCB work moves the objection to KEEP from "wrong MDE" to "was going to have wrong standard
  errors", and then answers it.

The decision still belongs to the repository owner. Nothing here consulted the outcome, and none of
these measurements could have: whether a listing prints many designs onto one blank garment carries
no information about `tau`.


---

## 7. The consequence, stated plainly

> **SUPERSEDED BY §9. The conclusion below was explicitly conditioned on "at this sample scale",
> and that condition has since been discharged: at 15,000,000 reviews the gate IS attainable under
> KEEP. The section is kept as written because the qualifier was load-bearing and the reasoning
> stands for the scale it describes.**

**At the 3,000,000-review scale, under KEEP, this corpus cannot pass the §4.1 gate.**

```
λ_min = MDE_design / MDE_target = 0.412 / 0.30 = 1.373
```

**λ ≤ 1 by construction.** A required λ above 1 is not a demanding threshold; it is an impossible
one. The measurement cannot carry an effect of the target size no matter how good the dictionary is,
because the shortfall is in the design, not in the instrument.

| scenario | MDE_design | λ_min | attainable? |
|---|---|---|---|
| **KEEP** | 0.412 | **1.373** | **no — exceeds 1** |
| EXCLUDE | 0.156 | 0.52 | yes |
| SPLIT | 0.132 | 0.44 | yes |

Measured λ is 0.741–0.878, so EXCLUDE and SPLIT clear their thresholds comfortably. **But they buy
that pass with an assumption that §5.2 establishes cannot be checked.** SPLIT asserts independence
across 12,725 designs; EXCLUDE discards the observations rather than modelling them.

**This is a finding, not a failure.** Stated as such:

> **This corpus, in this window, at this sample scale, cannot measure this effect without adding an
> assumption it cannot verify.**

That sentence is worth more than a marginal pass would have been. It is a specific, quantified
statement about what the public data can and cannot support — which is, per `README.md`, part of the
argument this project is making rather than an obstacle to it.

What it does **not** say: that the effect is absent, that the design is wrong, or that Amazon is
unusable. It says the current *scale* is insufficient under assumption-minimal clustering. Whether
scale fixes it is measurable and is the next step (§8).


---

## 8. The next step is SCALE, not a wider corpus — a correction

**The escalation this design planned has already happened.** `DESIGN.md` §7.1 wrote the sequence as
`Amazon_Fashion` first, then `Clothing_Shoes_and_Jewelry` as the wider slice. That step was taken on
2026-08-08 and it was **forced, not optional**: `Amazon_Fashion` has `categories` empty in 100% of a
30,000-item sample, so it yields no gender and no body half and cannot produce a single cell of the
estimand.

**Every measurement in this project since then has run on `Clothing_Shoes_and_Jewelry`** — the
window probe, the cluster probe, the style-definition probe, the precision draw, and all three A5
measurements. There is no un-escalated corpus waiting. Verified against the run logs: all carry
`Clothing_Shoes_and_Jewelry`.

So "the gate fails on `Amazon_Fashion`, therefore escalate to `Clothing_Shoes_and_Jewelry`" is not
available. **The gate fails on `Clothing_Shoes_and_Jewelry`, which is already the wider slice.**

### 8.1 What the remaining lever actually is

Not a different corpus — **more of this one.**

| | used | available | fraction |
|---|---|---|---|
| reviews streamed | 3,000,000 | 66,000,000 | **4.5%** |
| item index | 400,000 | 7,200,000 | **5.6%** |

Both multiply into the join, so the labelled sample is a small fraction of what the corpus can yield.
**MDE needs to improve by only 1.37× to bring KEEP inside the 0.30 target** (0.412 → 0.30), which is
a 1.9× increase in effective sample size if the design effect holds constant.

### 8.2 But whether it helps is genuinely open, and the previous claim is retracted

"A wider corpus improves DEFF by itself" was asserted in conversation and **never measured**. It is
retracted (`DESIGN.md` §5.9). At larger scale the design effect moves for competing reasons:

- **more reviews per existing parent** raises `m_bar`, which raises DEFF;
- **more parents entering** through a larger index lowers `m_bar` and adds clusters, which lowers it;
- **the catalogue listings scale too**, and if they scale faster than conventional ones — which
  measurement 0 already showed the *filters* do — CV worsens.

MDE improves as `sqrt(DEFF / n)`, so the sign of the net effect is not predictable from either term
alone. **It is measurable and is being measured**: a 15,000,000-review pass against a 1,500,000-item
index, reporting cell counts, gradient cells, the structurally-failing share, the cluster-size
distribution, CV, DEFF, and MDE under all three A5 scenarios.

### 8.3 The condition that travels with any change of population

Whether the population changes by widening scope or by scaling within it, the same rule applies and
it is not cheap:

> **`λ`, `δ` and `Δp₀` are properties of the analysis population, not constants of the dictionary.**

They were measured on 149 hand labels drawn from a specific window, seller mix and review register.
A different seller mix or a different review language does not inherit them. **A materially different
analysis population requires a fresh hand-labelling round** — a new blind draw, a new coding pass
under the frozen guide, and a re-computation of λ, δ and Δp₀.

Scaling *within* `Clothing_Shoes_and_Jewelry` under the same window is the mildest version of this,
since the population is the same one sampled more deeply — but the mega-listing share is one of the
things being measured, and if it moves materially the labelled sample's composition moves with it.
**Recorded as a transfer condition on §5.3 and A7, with its cost stated in advance rather than
discovered when the numbers arrive.**


---

## 9. Scale changes the answer — the gate is attainable under KEEP

15,000,000 reviews against a 1,500,000-item index, same window, same criterion.

### 9.1 The headline

| scenario | clusters | m_bar | CV | DEFF | **MDE `tau`** | 3M figure |
|---|---|---|---|---|---|---|
| **KEEP** | 29,420 | 5.668 | 15.30 | **67.60** | **0.185** | 0.412 |
| EXCLUDE | 29,414 | 4.996 | 4.04 | 5.28 | 0.055 | 0.156 |
| SPLIT | 46,865 | 3.558 | 4.53 | 4.78 | 0.049 | 0.132 |

Gradient cells: men 8,946 / 8,269 / 12,997, women 39,509 / 11,889 / 20,626.

```
λ_min under KEEP  =  0.185 / 0.30  =  0.617
measured λ        =  0.878  [0.723, 1.000]     (§5.3 routing, store clustering)
```

> **SUSPENDED — the two figures are not in the same clustering unit.** The MDE above is computed at
> **parent-level** clustering (29,420 clusters); λ is quoted at **store level**. Store is coarser, so
> `m_bar` and DEFF rise and the MDE worsens. Bracketed with existing modules, the comfortable pass
> becomes **tangent** across almost the whole plausible range and fails outright if stores are much
> coarser than parents:
>
> | stores per parent | m_bar | MDE @CV 18 | λ_min | vs λ lower bound 0.723 |
> |---|---|---|---|---|
> | 1.00 | 5.67 | 0.218 | 0.725 | tangent |
> | 0.80 | 7.09 | 0.243 | 0.810 | tangent |
> | 0.70 | 8.10 | 0.260 | 0.866 | tangent |
> | 0.60 | 9.45 | 0.280 | 0.935 | **fails on the point estimate too** |
>
> **No pass is declared until store-level DEFF and MDE are measured**, and until §9.4's composition
> question is settled — 3M → 15M moved composition by 10.7 points, and a population still in motion
> is not a population. See `docs/handoff-2026-08-17.md` §3.1 and §3.2.

At parent-level clustering, 0.617 sits below the measured λ on both the point estimate and the
interval's lower bound.

That reverses §7, whose qualifier "at this sample scale" was the load-bearing part.

### 9.2 DEFF got worse and the MDE improved anyway

Worth spelling out because the two move in opposite directions:

- **DEFF more than doubled**, 31.64 → 67.60, driven by CV 11.21 → 15.30 and `m_bar` 4.845 → 5.668.
- **Cells grew about 11×** (men's tee 786 → 8,946).
- MDE scales as `sqrt(DEFF / n)`, so the penalty is `sqrt(67.60/31.64) = 1.46` against a gain of
  `sqrt(11.4) = 3.38`. Net **2.31×**, and the observed improvement is **2.23×**. The arithmetic
  checks out.

So the retracted claim — "a wider corpus improves DEFF by itself" — is confirmed **false**: DEFF got
materially worse. Depth helped through sample size in spite of the design effect, not through it.

### 9.3 The concentration was partly an artefact of the small metadata index

| | 3M / 400k | 15M / 1.5M |
|---|---|---|
| labelled observations | 15,072 | 166,766 |
| clusters | 3,111 | 29,420 |
| largest cluster | 2,893 | 14,230 |
| **its share** | **19.2%** | **8.5%** |
| **structurally-failing share** | **23.2%** | **11.9%** |

**The mega-listing's share halved.** It grew 4.9× while the sample grew 11.1×, because a 1,500,000-
item index admits many conventional parents that a 400,000-item index never reached. A good part of
what looked like an intrinsic property of the corpus was a property of how thinly it had been
indexed.

This does **not** dissolve the A5 question — 11.9% is still a large share and the largest single
cluster is still 8.5% — but it materially changes its size, and it was not predicted.

### 9.4 Does A9 fire? Probably not, and here is the check

`PREREGISTRATION.md` §11 A9 requires a fresh hand-labelling round when the analysis population's
**composition** changes materially, not merely its `n`.

The labelled sample was drawn from a 600,000-review / 250,000-item join. Its own mega-listing share
is **10.1%** (15 of 149 rows). Against the analysis populations:

| population | failing-listing share | gap to the labelled sample |
|---|---|---|
| 3M / 400k | 23.2% | 13.1 points |
| **15M / 1.5M** | **11.9%** | **1.8 points** |

**The labelled sample resembles the scaled population more closely than the intermediate one.** That
is an accident of how it was drawn, not a design feature, but it is checkable and it points the
right way: scaling up moved the analysis population *toward* the sample λ was measured on, not away.

**Reading: A9 is not triggered by the scale-up on this evidence.** It would have been triggered by
quoting λ for the 3M population, where the gap is 13 points. That is worth noting, since the 3M
figures were the ones in circulation.

### 9.5 What is still not established

- These are 15M of 66M reviews (23%) and 1.5M of 7.2M items (21%). **Still not the full corpus.**
- DEFF is rising with scale. Whether it keeps rising, and how fast, is not known — the two runs give
  a slope of one segment, which is not a trend.
- The homogeneity test that would settle §5.2 was **invalid in the first scale run** and is being
  re-measured; see §10.


---

## 10. The refutation condition fired — and its stated consequence does not follow

This section is the awkward one and it is written before the convenient reading suggests itself.

### 10.1 The result, on a valid test

Multinomial dispersion with a parametric bootstrap p-value, at 15,000,000 reviews:

| listing | asins compared | X²/df | bootstrap p | verdict |
|---|---|---|---|---|
| **`B07TVHSDMQ`** | **60** | **2.09** | **0.001** | **heterogeneous beyond sampling noise** |
| `B07T7RFKSR` | 5 | 1.51 | 0.237 | not distinguishable |
| `B07XFXXZMV` | 3 | 1.19 | 0.546 | not distinguishable |
| `B08R8W8GP9` | 3 | 0.44 | 0.958 | not distinguishable |

Only the first has enough asins to test anything; three and five asins carry essentially no power, so
their non-rejections are uninformative rather than supportive.

**On the one listing that can be tested, the designs under it are not draws from one fit
distribution.** `PREREGISTRATION.md` §11 A5 recorded in advance that this is what would fire the
refutation condition. **It fired.**

### 10.2 But the consequence I pre-registered does not follow, and the reason is the error already corrected in §2.2

The refuter read: *"parent-level clustering was wrong from the start, the 0.568 figure is an artefact
of the wrong clustering, and the decision turns toward SPLIT."*

**That inference is invalid.** A cluster-robust variance estimator permits an **arbitrary
within-cluster covariance structure**. Heterogeneity among the asins inside a parent is precisely the
kind of thing it is built to absorb; it assumes nothing about within-cluster homogeneity, so
observing within-cluster heterogeneity cannot contradict it.

What *would* invalidate parent-level clustering is correlation **across parents** — a violation of
between-cluster independence. This test measures nothing about that.

**The refuter inherited the error the brief corrected on 2026-08-15**: it was written while this
document still described KEEP as "assuming perfect correlation within the catalogue". Under that
mistaken reading, evidence of internal heterogeneity would indeed have contradicted the assumption.
Under the correct reading there is no assumption to contradict.

### 10.3 This must not become a convenient escape

A pre-registered condition fired and is being declared non-binding. That is exactly the move a
refutation condition exists to prevent, so the reasoning has to stand on its own and be checkable:

- **The claim:** cluster-robust inference at level `g` requires independence *between* level-`g`
  units and imposes no restriction *within* them.
- **The consequence:** within-parent heterogeneity is orthogonal to the validity of parent-level
  clustering. It is evidence about the product, not about the estimator.
- **What follows instead:** if asins genuinely differ, they are not interchangeable — which is a
  reason to be *more* wary of treating them as independent units, not less. **The evidence points
  away from SPLIT, not toward it.**

If that reasoning is wrong, the refuter binds and the decision turns to SPLIT. It is stated this
plainly so it can be checked rather than taken on trust.

### 10.4 What the result DOES establish, and what should have been the refuter

**Established:** the mega-listing is internally heterogeneous. That **strengthens** the §5.1 finding
that it is not a style — it is not merely many asins, it is many asins that behave differently.
Nothing in §5.1 depended on this, but it is now independently corroborated.

**Not established, and untouched:** how errors are correlated. §5.2 remains open.

**A correctly specified refuter would have targeted the assumption that is actually made:**
between-cluster independence. Concretely — do parents belonging to the **same store** show correlated
errors? If they do, parent-level clustering is too fine and the correct level is **store**, which is
one level *up*, not down.

There is already partial evidence pointing that way: store-level mean deviation spans +0.25 to +1.45
across sellers (`docs/phase1b-size-deviation-probe.md` §4c), which is why λ is quoted at store
clustering. **The threat was always upward in the hierarchy, and the refuter pointed downward.**
That is the substantive lesson, and it is recorded as a defect in how the condition was written
rather than in the data.

### 10.5 Standing after this

- The **style** question (§5.1): closed, and further corroborated.
- The **correlation** question (§5.2): still open, and this test did not address it.
- **A5's provisional default remains KEEP**, now on two grounds rather than one — assumption
  minimality (§2.2), and the observation that heterogeneous asins are a reason against treating them
  as independent.
- **Outstanding and specified:** test between-parent, within-store error correlation. That is the
  refuter that should have been written, and it is now written for next time.
