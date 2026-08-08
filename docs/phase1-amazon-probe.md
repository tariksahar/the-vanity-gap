# Phase 1 — Amazon Reviews'23 probe

**Date:** 2026-08-08
**Instrument:** `amazon_fit_probe.py`
**Corpora probed:** `Amazon_Fashion` and `Clothing_Shoes_and_Jewelry`, 50,000 reviews and 30,000
item metadata records each
**Access:** stream-only. Nothing was downloaded; no raw snapshot was written (§0.4 is not engaged
because no capture was retained).

---

## 0. Scope verdict

> **Amazon CSJ can carry the primary estimand. Purchased size is structurally absent — the metadata
> file has one row per `parent_asin` and no `asin` field — so the secondary size-distribution
> analysis and the Chattaraman head-to-head cannot be run on this corpus. Live candidate for
> Phase 3, conditional on the precision measurement.**

**The precision number is PENDING.** It is the binding gate measure (§4.1) and it is not yet
established. `data/processed/precision_sample.csv` has been drawn for hand-labelling; §5 below gives
the sampling procedure. Until those labels exist, this corpus is a candidate and nothing more.

---

## 1. A reading-method correction before the numbers

The `load_dataset(..., trust_remote_code=True)` call documented in §3.1 **does not work.**
`datasets` 5.x removed script-based configs, and the Amazon-Reviews-2023 repository ships one:

```
RuntimeError: Dataset scripts are no longer supported, but found Amazon-Reviews-2023.py
```

The probe falls back to reading the published `.jsonl` over HTTPS line by line, stopping at the
requested count. Stream-only; nothing is downloaded in full. Both paths are retained in the script —
the loader is attempted first — so a future `datasets` release that restores script support needs no
code change. Recorded in DESIGN.md §5.1.

---

## 2. Question 1 — what share of reviews carry a fit judgement

| | `Amazon_Fashion` | `Clothing_Shoes_and_Jewelry` |
|---|---|---|
| reviews scanned | 50,000 | 50,000 |
| empty review text | 12 (0.02%) | 5 (0.01%) |
| `verified_purchase` | 41,974 (83.95%) | 32,440 (64.88%) |
| **usable fit label (exactly one bucket)** | **7,974 (15.95%)** | **9,755 (19.51%)** |
| ambiguous, dropped (≥2 buckets) | 645 (1.29%) | 898 (1.80%) |
| no fit language | 41,381 (82.76%) | 39,347 (78.69%) |

Split within the labelled set:

| Bucket | `Amazon_Fashion` | `Clothing_Shoes_and_Jewelry` |
|---|---|---|
| `ran_small` | 3,434 (43.06%) | 3,584 (36.74%) |
| `true_to_size` | 2,819 (35.35%) | 4,370 (44.80%) |
| `ran_large` | 1,721 (21.58%) | 1,801 (18.46%) |

**`ran_small` exceeds `ran_large` in both corpora, by roughly two to one.** This is not a finding
about garments. It is the §5.2 volunteering skew made visible: nobody is prompted, so buyers write
about fit mainly when the fit went wrong, and a garment that is too small is unwearable in a way
that a garment that is too large often is not. It is a warning about the estimator, not an input to
it. The §5.2 selection model is load-bearing and this table is the reason.

**These counts predate the dictionary correction in §4.** The two removed patterns were still active
when this pass ran, so the true `ran_large` share is slightly lower than shown — the removed
`large in size` pattern was the sixth most-fired `ran_large` pattern in `Amazon_Fashion` at 120
firings, about 7% of that bucket. The precision sample in §5 was drawn with the corrected
dictionary. These headline shares will be re-measured when the dictionary is frozen in
`PREREGISTRATION.md`; they are not gate-critical, since the gate asks only that there be *enough*
labelled reviews for the smallest cell, and 19.51% clears that comfortably.

---

## 3. Question 2 — purchased size: a structural absence, not a sparse field

This is the finding that changed the phase.

### 3.1 There is no variant-level record to join to

| Check | Result |
|---|---|
| metadata rows read | 30,000 |
| distinct `parent_asin` among them | 30,000 |
| **rows carrying an `asin` field** | **0** |
| reviews where `asin` ≠ `parent_asin` | 10.4% |

The published metadata is **style-level**: one row per `parent_asin`, with no variant records at
all. Size is a **variant** attribute. §3.1 of DESIGN.md asserted that joining `review.asin` to item
metadata would recover the purchased size; the join target does not exist. That claim has been
corrected in place.

The 10.4% figure is the interesting half: the *reviews* do distinguish variants that the *metadata*
cannot describe. So the information loss is real and one-directional — we know a specific variant
was purchased, and we cannot learn anything about it.

### 3.2 The free-text fallback does not rescue it

| | `Amazon_Fashion` | `Clothing_Shoes_and_Jewelry` |
|---|---|---|
| `details` has an exact `size` key | 1.22% | 1.71% |
| `details` has any size-like key | 1.26% | 1.72% |
| **normalisable, as share of all items** | **0.33%** | **0.82%** |
| normalisable, as share of those found | 26.12% | 47.87% |

Against a gate threshold of 50% of items. The best figure is 0.82%, short by a factor of about 60.

The strings that *are* present are largely not garment sizes: `3 Piece Set`,
`2 Count (Pack of 1)`, `9.4"x5.9"`, `5.5 B(M) US`, `4PACK`, `8 inch`, `One Size`. §5.3 anticipated
free-text messiness; the reality is that the field is mostly not answering the size question at all.

**No better parser fixes this.** The scarcity is downstream of §3.1 — the row that would hold a size
does not exist. This is why the size row is reported as closed rather than as needing more work.

### 3.3 What this costs

Recorded explicitly rather than glossed:

- **The §5.3 secondary size-distribution analysis dies on this corpus.** It needs an ordered size
  ladder per product. There is none.
- **The Chattaraman head-to-head (§2) dies on this corpus.** Chattaraman, Simmons & Ulrich predict
  deviation *increasing with body size* — the direct rival to this project's prediction of deviation
  concentrated at the small end. Testing it requires knowing the size purchased. It cannot be run on
  Amazon. **It relocates to the women's arm**, where ModCloth and RentTheRunway carry both purchased
  size and user body measurements. Relocated, not abandoned — but note that it can then only be
  tested on women, and the rival hypothesis is about men as much as women.
- **§5.4 supply-side label inflation becomes unmeasurable here.** It is also narrower than previously
  written: inflation acts on the purchased-size distribution and reaches `fit_score` only if it
  differs between upper and lower garments *within* a gender, since uniform within-gender inflation
  cancels in `tau`. Narrowed, unmeasurable on this corpus, and to be stated as a named limitation.

**What it does not cost: the primary estimand.** `tau` is built from `fit_score`, gender and body
half. Purchased size appears nowhere in it.

---

## 4. Dictionary corrections made during the probe

Recorded here because §5.1 requires the dictionary to be auditable, and because both changes were
made **before** the dictionary was frozen in `PREREGISTRATION.md` and **before** any ModCloth
validation number existed.

| Change | Evidence | Effect |
|---|---|---|
| Negation veto widened to allow intervening words: `not (\w+ ){0,3}?true to size` | "not **made** true to size" was defeating a veto that required `not` adjacent to `true` | 6 reviews per 50,000 moved out of `true_to_size` — immaterial, but wrong is wrong |
| **Removed** `\b(?:large\|big)\s+(?:in\s+)?siz(?:e\|ing)\b` | Fired on "she can usually wear medium underwear, but finds **the large size** to be more comfortable", where the phrase names the size *purchased*, not the fit delivered | 120 firings per 50,000 in `Amazon_Fashion` |
| **Removed** `\bsmall\s+(?:in\s+)?siz(?:e\|ing)\b` | Symmetric counterpart of the above, same defect | — |

Two bugs in the **category classifier** were also found and fixed, and they mattered more than the
dictionary changes:

1. Matching the joined category path let a multi-class parent node beat a single-class leaf —
   `women | tops, tees & blouses | blouses & button-down shirts` was classified from the parent's
   "tees". This misfiled **479 women's button-downs as t-shirts**; the women's shirt cell read 15
   before the fix and 574 after. Classification now walks from the leaf outwards and treats any
   segment naming two or more classes as ambiguous at that level.
2. `\bshirt` matches inside `t-shirts`, because the hyphen is a word boundary. Men's t-shirts were
   falling through to the parent node and being labelled `shirt`. The gradient classes are now
   mutually exclusive by construction.

Both bugs inflated one gradient cell at another's expense — precisely the primary comparison of
§1.2. Worth stating plainly: had this not been caught, the headline comparison would have been
measured on contaminated cells.

---

## 5. Question 3 — gender and body half

### 5.1 `Amazon_Fashion` cannot answer this at all

**`categories` is empty (`[]`) in 100% of 30,000 items.** The field is present; its value is an
empty list. Confirmed against an independent 3,000-row field audit, which also found
`bought_together` empty in 100% of rows. All four §1.3 cells are zero.

This alone forces the corpus choice. `Amazon_Fashion` is unusable for this design regardless of
anything else, and §7.1's instruction to start there is now a dead branch.

### 5.2 `Clothing_Shoes_and_Jewelry` answers it

`categories` populated in 100% of items.

| Gender | Share | | Body half | Share |
|---|---|---|---|---|
| women | 59.07% | | excluded (§1.3) | 66.59% |
| men | 25.83% | | upper | 17.94% |
| children (excluded) | 10.41% | | lower | 8.53% |
| unknown | 4.68% | | unknown | 6.94% |

**Both recovered: 23.87%.** Per 30,000 items:

| | upper | lower | row total |
|---|---|---|---|
| **men** | 1,812 | **759** | 2,571 |
| **women** | 3,186 | 1,404 | 4,590 |
| column total | 4,998 | 2,163 | 7,161 |

### 5.3 The men's lower-body cell

**759 items, 10.60% of the four cells — the smallest, and it does not vanish.**

This is the §5.5 binding constraint and the §1.5 placebo anchor, so it gets its own line. Phase 0's
254-review Mavi sample contained *zero* men's jeans reviews; this corpus does not have that problem.
It remains the cell to watch, and the cell whose size should drive any decision about how many
reviews to ingest.

The §1.2 three-step gradient — the primary comparison — has all six cells populated:

| | t-shirt | shirt | jeans / trousers |
|---|---|---|---|
| **men** | 849 | 534 | 483 |
| **women** | 1,143 | 574 | 624 |

### 5.4 Sampling procedure for the precision measurement

Reproducible, and stated here so the numbers can be checked:

```bash
python amazon_fit_probe.py --precision-sample --category Clothing_Shoes_and_Jewelry --sample-items 200000 --sample-reviews 300000 --per-stratum 50 --seed 20260808
```

1. **Style index.** Stream `raw_meta_Clothing_Shoes_and_Jewelry` and keep only items resolving to
   `men` or `women` **and** to `upper` or `lower` under §1.3. Everything else is dropped here, so the
   sample is garment-scoped by construction — the non-garment contamination that produced 0/4 on
   `Amazon_Fashion`'s `ran_large` bucket cannot enter.
2. **Join.** Stream `raw_review_Clothing_Shoes_and_Jewelry`, keep reviews whose `parent_asin` is in
   the index. Measured join rate at 20k×20k was 2.25%; it scales with both stream lengths.
3. **Label.** Apply the corrected dictionary. Ambiguous reviews are dropped, not sampled.
4. **Stratify.** Six strata: three buckets × {men, women}. **Reservoir sampling** within each
   stratum gives every eligible review equal selection probability in one pass, without holding the
   stream in memory.
5. **Shuffle** before writing, so row order carries no information about the assigned bucket and
   cannot bias the labeller.
6. `human_label` is written **blank**. The repository owner labels it. The probe does not label its
   own output.

**Allocation note, and a limitation.** 50 per stratum gives 100 per bucket as specified, 300 rows
total, while making the men's stratum 50 per bucket. At p≈0.8 that is a standard error of about
5.7 pp for a men's bucket, so a 95% interval spans roughly ±11 pp: it can distinguish 80% from 60%,
but not 80% from 72%. If the men's precision lands near the threshold the sample will need doubling
— `--per-stratum 100` gives 600 rows and about ±8 pp. That decision is the owner's and should be
made after seeing where the numbers fall, which is legitimate here because it concerns the precision
of a *measurement*, not the choice of a hypothesis.

**`data/processed/precision_sample.csv` contains raw review text and must not be committed or
published** (§6). `review_id_hash` is SHA-256 over `user_id|asin|timestamp`, truncated to 16 hex
characters; no raw `user_id` is written.

### 5.5 A construct problem found in the drawn sample — `gender` is the garment's, not the buyer's

Not anticipated in DESIGN.md, and it should be. The very first row of the drawn sample reads:

> category path `clothing, shoes & jewelry | men | clothing | shirts | t-shirts`
> title *"Great sleepwear for a woman, and excellent price"*
> text *"I like long-sleeved men's t-shirts with pockets for winter sleepwear along with leggings…"*

Classified `gender = men`. The **garment** is men's. The **buyer** is not. §1.4's estimand conditions
on the buyer's gender — the hypothesis in §1.2 is about how men and women choose labels — and
`categories` can only ever give the gender the garment is *marketed to*.

This is measurement error in the conditioning variable, and there are two reasons it is worse than
ordinary noise:

1. **It is asymmetric.** Women buying men's garments is considerably more common than the reverse.
2. **The asymmetry is correlated with the outcome.** Women buy men's garments substantially *because*
   they want them loose — which is the oversized-fashion channel of §5.7. Such a purchase enters the
   data as "men's upper garment, ran large": the exact cell and the exact direction of the men's
   hypothesis. **This confound pushes in the direction of a false positive**, so it cannot be waved
   off as attenuation toward the null the way §2's `true_to_size` confusion can.

Not resolvable from `categories`. Three partial routes, none free:

- **Measure it.** The hand-labelling sample is already being read row by row. Adding a
  `buyer_gender_mismatch` flag would cost the labeller almost nothing and would yield a direct
  estimate of the contamination rate per cell. This is the cheapest useful move and it is the one to
  take, but the column set was specified and is not being changed unilaterally.
- **Bound it.** Estimate the rate on the labelled sample, then report `tau` under worst-case
  reassignment of the mismatched share.
- **Restrict it.** Drop reviews whose text signals a cross-gender purchase. Rule-based, so it
  inherits the §5.1 precision problem, and it would need its own validation.

Belongs in `PREREGISTRATION.md` as a named threat with a chosen handling rule. It also applies to
the ModCloth and RentTheRunway arms only trivially — both are women-only platforms, so there is no
cross-gender cell for it to contaminate.

---

## 6. Licence

**The dataset carries no licence statement of any kind.** Not a restrictive licence, not an
unrecognised one — the HuggingFace dataset page has no licence tag, no terms-of-use section and no
licence file. The only stated condition is a request to cite the associated paper.

Absent an affirmative grant, redistribution of derived records is not authorised by default.
Consequences, per §6:

- Analysis and publication of **aggregates** proceed.
- §4.4's open dataset deliverable must be **aggregates only** until this is resolved in writing.
- The route to resolving it is an email to the McAuley Lab. Until then this stays an open item in
  `ETHICS.md`, which does not yet exist and should be written alongside `PREREGISTRATION.md`.

---

## 7. The §4.1 gate

| Measure | Threshold | Result | Verdict |
|---|---|---|---|
| Hand-verified precision per bucket | ≥ ~80% | **pending** — sample drawn, unlabelled | **OPEN** |
| Purchased size recoverable and normalisable | ≥ 50% of items | 0.82% at best, structurally unavailable | **FAIL** |
| Men's lower-body cell | not vanishing | 759 per 30,000 items, 10.60% of cells | **PASS** |
| Reviews carrying a usable fit label | enough for the smallest cell | 19.51% | **PASS** |

**Two pass, one fail, one open.** The failing row is the size row, and per the amended §4.1 it costs
the secondary analyses rather than the corpus. The gate as a whole therefore turns on the precision
row, which is open.

An indicative hand-check of 4 examples per bucket was run during the probe: 7/12 correct on
`Amazon_Fashion`, 10/12 on `Clothing_Shoes_and_Jewelry`. All four `Amazon_Fashion` errors were
**non-garments** — a purse, two watch bands, a pair of glasses — where "too big" describes an object,
not a fit. This is diagnostic of *why* the garment-scoped, gender-stratified sample is the right
instrument, and it is **not** a precision measurement. n=4 per bucket is an indication. It is
reported here only so the reasoning is traceable.

---

## 8. What Phase 2 must settle

Phase 2 is now doing double duty, and the second job came out of this probe:

1. The women's arm as a standalone evidence contribution (§4.2), now also carrying the relocated
   Chattaraman head-to-head.
2. **Ground-truth validation of the §5.1 dictionary.** ModCloth and RentTheRunway carry review text
   *and* a structured fit label on the same record — thousands of ground-truth comparisons against
   300 hand judgements.

The interpretation of any divergence between the two validation routes was fixed in advance, before
either was run, in **`docs/phase2-divergence-precommitment.md`**. The two constraints that matter
most: those platforms *prompt* for fit while Amazon reviewers *volunteer* it, so their precision is
an **upper bound** for Amazon rather than a transfer; and both are **women-only**, so they validate
nothing for the men's arm — which is exactly where the dictionary is being extrapolated.

The men's arm is not being dropped. Phase 2 exists to validate the estimator against a structured
fit field before a regex dictionary is trusted on 66M reviews. Phase 3 is the destination.
