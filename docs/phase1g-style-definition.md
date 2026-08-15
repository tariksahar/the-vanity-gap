# Phase 1g — when is a `parent_asin` a style, and the residual bias term

**Date:** 2026-08-14
**Instruments:** `style_definition_probe.py`, `src/analysis/attenuation.py`
**Sample:** 3,000,000 block-sampled reviews, 2019 window, 400,000-record style index —
16,029 labelled in-scope observations
**Feeds:** `PREREGISTRATION.md` §11 A5 (open decision), §9.7 (differential error)

---

## 1. The question, asked structurally

`PREREGISTRATION.md` §11 A5 has been carrying the question as *"exclude mega-listings or not"*.
**That framing cannot be answered honestly**, because the MDE consequence of each answer is already
known (0.219 vs 0.568), so choosing is choosing the number.

The answerable question is `DESIGN.md` §1.6's own: **when is a `parent_asin` a style?** It can be
settled without consulting the MDE, and this probe settles it on structure alone. Observation count
is used *only* to find candidates; the criterion applied to them is structural.

### 1.1 What cannot be measured on this corpus

The brief asked how many distinct **product titles** the sub-ASINs of a heavy listing carry. **That
is not answerable here.** The published metadata is parent-level — one row per `parent_asin`, no
`asin` field at all (`docs/phase1-amazon-probe.md` §3.1). There are no per-sub-ASIN titles to count.

What is available, and used instead:

- distinct `asin` per parent, from the **reviews**, which do carry `asin`
- reviews per distinct asin
- the review titles themselves, read by hand

The reasoning: a garment design's variants are sizes and colours, so a real style's asin count is
**bounded by its size grid**. A catalogue listing's is not, because every new printed design is a
new asin.

---

## 2. What the measurement shows

| parent | labelled | all reviews | **distinct asins** | rev/asin | cell | store |
|---|---|---|---|---|---|---|
| `B07TVHSDMQ` | 2,916 (18.2%) | 13,837 | **12,004** | 1.2 | women/upper | Funny Civil Engineers Shirt |
| `B0C4G3VQ9W` | 576 (3.6%) | 3,077 | **150** | 20.5 | men/upper | Hanes |
| `B07XFXXZMV` | 352 (2.2%) | 1,932 | **1,729** | 1.1 | women/upper | Hail Satan Unicorn Cat |
| `B07T4WDPGJ` | 283 (1.8%) | 1,568 | **560** | 2.8 | men/lower | Wrangler Authentics |
| `B08R8W8GP9` | 267 (1.7%) | 1,059 | **984** | 1.1 | women/upper | Aura Apparel |
| `B07T7RFKSR` | 261 (1.6%) | 861 | **753** | 1.1 | women/upper | Fun Summer Gifts and Tee shirts |
| `B07QN1V2LF` | 178 (1.1%) | 730 | **706** | 1.0 | men/upper | Top Gun |

**Typical parent (≥3 labelled reviews, n=849): median 17 asins, 22 reviews.**

### 2.1 The asin count discriminates; the ratio does not

`B07TVHSDMQ` carries **12,004 distinct asins** against a typical parent's 17 — a factor of about
700. No size grid produces that. Ten sizes by thirty colours is 300; twelve thousand is two orders
beyond any plausible variant space for one garment design.

**Reviews per asin does NOT discriminate** — 1.15 for the heavy five against 1.26 for typical
parents. Both are near 1 because the sample is sparse relative to the variant space, not because the
listings are alike. This is worth recording as a negative result: it was the more intuitive
statistic and it is useless here.

### 2.2 The review titles settle it

Under `B07TVHSDMQ`, titled *"Funny Civil Engineers TShirt I'm A Crazy Civil Engineering T-Shirt"*:

> "Vet small" · "Fits as expected" · "The boiler tshirt" · **"Vote tshirt"**

**"The boiler tshirt" and "Vote tshirt" are not variants of a civil-engineering slogan shirt.** They
are different products. One `parent_asin`, one metadata row, one title — and a catalogue of
unrelated printed designs underneath. `DESIGN.md` §1.6 calls that a style; it is not one.

By contrast `B0C4G3VQ9W` — Hanes EcoSmart sweatshirt, 150 asins, 20.5 reviews per asin:

> "Hanes Men's Ecosmart Fleece Sweatshirt" · "Not bad for the price but need to size up" ·
> "Runs small" · "Wish I bought a medium"

Every review is about **one sweatshirt**. 150 asins is a size-by-colour grid. **This is a style, and
a heavy one — heaviness is not the criterion.**

### 2.3 The borderline case is real

`B07T4WDPGJ` — Wrangler Authentics jeans, **560 asins**, 2.8 reviews per asin. Jeans genuinely
multiply: waist × inseam × wash. Twenty waists by six inseams by five washes is 600. **560 asins is
consistent with one style.**

So the criterion cannot be a flat asin threshold. It is: **does the asin count exceed what this
garment's size grid can generate?** Twelve thousand for a t-shirt does. Five hundred and sixty for
jeans does not. Cases in between need the review titles, which is why they are printed.

---

## 3. Exposure across the cells — the finding that decides A5

**This is not a power question.**

| cell | labelled | from top-5 heavy | share | from top-20 | share |
|---|---|---|---|---|---|
| men/upper | 2,385 | 576 | 24.15% | 849 | 35.60% |
| men/lower | 2,005 | 283 | 14.11% | 592 | 29.53% |
| **women/upper** | 8,465 | **3,535** | **41.76%** | 3,990 | 47.14% |
| **women/lower** | 3,174 | **0** | **0.00%** | 582 | 18.34% |

**The heavy listings are wildly asymmetric across the design.** They supply 41.76% of women's upper
observations and **exactly none** of women's lower.

The estimand is
`(men_upper − men_lower) − (women_upper − women_lower)`. Excluding the heavy listings removes 42% of
one arm of the women's within-gender contrast and 0% of the other. **That changes what the women's
difference is measuring**, not merely how precisely it is measured.

The concern anticipated in the brief was concentration in **men's upper**. The measured
concentration is in **women's upper**, and it is worse, because the women's contrast is one of the
two differences the estimand takes — and because women/lower being untouched means the asymmetry
falls entirely on one side.

Men's cells are affected too but more evenly: 24.15% against 14.11%, a 10-point gap rather than a
42-point one.

---

## 4. The residual as a term in `tau`, not a footnote

### 4.1 Derivation, verified

With `a_{−1} = c − λ`, `a_0 = c + δ`, `a_{+1} = c + λ`:

```
E[y|X] = (c−λ)p₋₁ + (c+δ)p₀ + (c+λ)p₊₁
       = c·(p₋₁+p₀+p₊₁) + λ·(p₊₁−p₋₁) + δ·p₀
       = c + λ·E[y*|X] + δ·p₀(X)
```

since `E[y*|X] = p₊₁ − p₋₁`. Taking the within-gender difference kills `c` but **not** `δ·p₀`:

```
tau_measured = [λ_m·Δ*_m + δ_m·Δp₀_m] − [λ_w·Δ*_w + δ_w·Δp₀_w]
```

The existing `residual` in `attenuation.py` is `a_0 − (a_{−1}+a_{+1})/2 = a_0 − c = δ`, so it was
already the right quantity, reported as a diagnostic rather than used as a term.

### 4.2 Measured

`p₀(cell)` is built as `Σ_k P(true=0 | assigned=k) · P(assigned=k | cell)`. The first factor comes
from the **149 hand labels**; the second from the **whole analysis population** (§2's cell
composition, 16,029 observations). **All the uncertainty is on the label side.**

| gender | δ | p₀ upper | p₀ lower | Δp₀ | δ·Δp₀ |
|---|---|---|---|---|---|
| men | **+0.170** | 0.5386 | 0.5744 | **−0.0358** | −0.00607 |
| women | **+0.047** | 0.5860 | 0.6199 | **−0.0340** | −0.00159 |

```
bias (raw)  = −0.00607 − (−0.00159) = −0.00448
SD(fit_score) = 0.6629
bias (SD)   = −0.0068 SD          95% CI [−0.0260, +0.0172]
```

**2.3% of the 0.30 SD target.** The interval is a store-level cluster bootstrap over the labels,
which is where the uncertainty lives.

### 4.3 The direction is the opposite of what was anticipated — and the mechanism explains why

The brief expected the residual to **mimic** the effect: men's δ is positive, so genuinely-fitting
garments get pushed toward `ran_large`, inflating men's `fit_score` — the direction the hypothesis
predicts.

**That is right about the level and wrong about the double difference.** A level shift cancels in
the within-gender difference unless `p₀` differs between upper and lower. It does, and it goes the
other way: `p₀(men, upper) = 0.539 < p₀(men, lower) = 0.574`. Men's **lower** cell holds more truly
`true_to_size` items, so the upward push is **larger there**, which pushes the men's upper−lower
difference **down**. The bias is **−0.0068 SD: against the hypothesis, not toward it.**

Two things follow, and both matter:

1. **The mechanism the brief identified is real.** δ can mimic the effect — it does so whenever
   `Δp₀ > 0`. That it does not here is an empirical property of this corpus, not a guarantee. If the
   window, the category scope or the dictionary changes, `Δp₀` can change sign and the bias with it.
   **It must be recomputed, not assumed.**
2. **The measured bias is small and its sign is not established** — the interval spans zero. It is
   not currently a threat to the result; it is a term that has to be carried and re-checked.

Why it is small: `Δp₀` is nearly identical across genders (−0.0358 vs −0.0340), so the bias reduces
to roughly `(δ_m − δ_w) · Δp₀ = 0.123 × (−0.035)`. The δ gap is real and large — three times the λ
gap, as the brief said — but it multiplies a quantity that barely differs between genders.

### 4.4 Standing rule

**No output reports λ without δ.** They are two coefficients of the same expansion and λ alone
describes the measurement only under `δ = 0`, which is false here (δ = +0.170 for men). This is
recorded in `PREREGISTRATION.md` §9.7 alongside the differential-λ threat.

---

## 5. What A5 now needs from the owner

The structural question is answered: **`B07TVHSDMQ` and its kind are not styles.** Twelve thousand
asins under one listing, ~1 review each, and review titles naming unrelated products.

The decision that remains is **not** "does excluding them improve the MDE" — it does, from 0.568 to
0.219 — but what to do about §3:

- excluding them removes **41.76% of women/upper and 0% of women/lower**;
- that reshapes one arm of the double difference;
- and the excluded population is systematically different — novelty print-on-demand tees are not a
  random subset of women's upper-body garments.

Three coherent positions, none of which this document chooses:

1. **Exclude, and state the population change.** The study describes conventional apparel; POD
   catalogue listings are out of scope by definition. The women's upper cell is redefined, and the
   paper says so.
2. **Keep, and accept MDE 0.568.** If the cluster is genuinely there, 0.568 is the honest number and
   excluding to reach 0.219 claims a precision we do not have.
3. **Split the parent.** Treat each `asin` as the clustering unit for these listings only. This is
   the most faithful to what the data is, and the most work — and it needs a rule for which listings
   get split, which is exactly the structural criterion in §2.

Option 3 did not exist before this measurement and is worth weighing: it neither discards the
observations nor pretends one listing is one style.
