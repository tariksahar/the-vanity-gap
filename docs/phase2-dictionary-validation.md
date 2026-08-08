# Phase 2a — dictionary validation against structured fit labels

**Date:** 2026-08-08
**Instrument:** `src/analysis/validate_dictionary.py`
**Raw snapshots:** `data/raw/modcloth/2026-08-08/`, `data/raw/renttherunway/2026-08-08/`
**Interpretation fixed in advance:** `docs/phase2-divergence-precommitment.md`, written before any
row of either dataset was read.

This is the first half of Phase 2. The women's-arm estimator (§4.2) is **not** in this document and
is still to be built; `docs/phase2-women-arm.md` does not yet exist.

---

## 0. Headline

Run over 46,223 ground-truth comparisons, the §5.1 dictionary **fails the 80% precision bar on two
of three buckets as it currently stands**, and the failure is **concentrated in two identifiable
pattern families** rather than spread across the dictionary. Removing those two families lifts all
three buckets above 80% at a large cost in recall.

Per the pre-commitment, **no pattern was removed in response to these numbers.** The diagnosis is
reported; the repair requires a dated amendment in `PREREGISTRATION.md` and a fresh Amazon
hand-sample, because scoring a repaired dictionary on the labels that exposed it is fitting to the
validation set.

---

## 1. Corpora, and what survives the §1.3 filter

| | ModCloth | RentTheRunway |
|---|---|---|
| rows | 82,790 | 192,544 |
| **in scope (upper or lower)** | **35,630 (43.04%)** | **10,593 (5.50%)** |
| upper | 20,364 | 7,950 |
| lower | 15,266 | **2,643** |
| excluded under §1.3 | 23,148 | 181,951 |
| unusable category | 24,012 | 0 |

Row counts reproduce Misra, Wan & McAuley (2018) exactly.

**ModCloth's category field is merchandising, not garment taxonomy.** Its seven values are `new`,
`tops`, `dresses`, `bottoms`, `outerwear`, `sale`, `wedding`. `new` (21,488) and `sale` (2,524) name
a *shelf*, not a garment — 29% of the dataset carries no recoverable body half. This is not
recoverable from the released fields.

**§1.3's concern about ModCloth's lower cell was misplaced; the concern belongs to
RentTheRunway.** DESIGN.md warned that ModCloth is dress-heavy and its lower cell would be thinner
than the headline row count suggests. Measured: ModCloth's lower cell is **15,266**, entirely
healthy. RentTheRunway is the dress-dominated one — 87% of it is dresses, gowns, sheaths, shifts and
jumpsuits, all excluded — and **192,544 rows collapse to a lower cell of 2,643.** That is §5.5 in
its purest form: total volume told us nothing, the smallest cell told us everything, and the larger
corpus is the weaker one.

---

## 2. Confusion matrices

Rows are the structured label (truth); columns are the dictionary's output.

### ModCloth — 35,630 in-scope rows

| truth ↓ | ran_small | true_to_size | ran_large | ambiguous | none | total |
|---|---|---|---|---|---|---|
| ran_small | **1,965** | 95 | 131 | 279 | 2,776 | 5,246 |
| true_to_size | 944 | **1,609** | 555 | 489 | 20,561 | 24,158 |
| ran_large | 223 | 83 | **1,640** | 257 | 4,023 | 6,226 |

### RentTheRunway — 10,593 in-scope rows

| truth ↓ | ran_small | true_to_size | ran_large | ambiguous | none | total |
|---|---|---|---|---|---|---|
| ran_small | **584** | 20 | 13 | 47 | 479 | 1,143 |
| true_to_size | 332 | **1,013** | 181 | 301 | 5,723 | 7,550 |
| ran_large | 33 | 30 | **831** | 50 | 956 | 1,900 |

**Directional errors are rare.** `ran_small` predicted where truth is `ran_large`: 131 and 13.
`ran_large` where truth is `ran_small`: 223 and 33. The dictionary very seldom gets the *sign*
backwards, which is the error that would be fatal to §1.4 — the sign is the whole estimand. Almost
all error is confusion with `true_to_size`, which attenuates `tau` toward zero rather than
reversing it. **That is the benign direction for this design**, and worth stating: a biased-toward-
null instrument that still finds an effect is more credible, not less.

---

## 3. Precision and recall

| Bucket | ModCloth precision | recall | RTR precision | recall |
|---|---|---|---|---|
| `ran_small` | **62.7%** | 37.5% | **61.5%** | 51.1% |
| `true_to_size` | 90.0% | **6.7%** | 95.3% | **13.4%** |
| `ran_large` | **70.5%** | 26.3% | 81.1% | 43.7% |

### 3.1 The low recall is the prompting signature, and it was pre-committed as harmless

`true_to_size` recall of 6.7% and 13.4% looks alarming until it is read against §5.1 of the
pre-commitment document, which fixed this in advance: *"Low recall with high precision is the
prompting signature and does not threaten Amazon."*

That is exactly the observed shape. On these platforms every record carries a structured label
whether or not the reviewer wrote a word about fit — and someone whose garment simply fit usually
writes about the fabric or the colour instead. 20,561 of ModCloth's 24,158 `true_to_size` rows
contain no fit language at all. There is nothing for a text rule to match. Amazon has no such
population, because on Amazon the label only exists when someone volunteered it.

**Recall on these corpora is therefore not an estimate of recall on Amazon**, and the pre-commitment
says so before the fact. Precision is the transferable quantity, and only as an upper bound.

### 3.2 Prevalence reweighting moves `ran_small` a long way

Precision depends on the base rates of the other classes. These platforms are far more
`true_to_size`-heavy than Amazon's volunteered population, so `ran_small` collects false positives
from a much larger pool than it would on Amazon. Reweighting to Amazon's garment-scoped bucket
prevalence (33.2% / 49.3% / 17.5%):

| Bucket | ModCloth raw → reweighted | RTR raw → reweighted |
|---|---|---|
| `ran_small` | 62.7% → **83.0%** (+20.2pp) | 61.5% → **87.3%** (+25.7pp) |
| `true_to_size` | 90.0% → 79.8% (−10.3pp) | 95.3% → 88.5% (−6.8pp) |
| `ran_large` | 70.5% → 70.1% (−0.4pp) | 81.1% → 83.1% (+2.0pp) |

The two corpora agree closely after reweighting, which is itself reassuring — they are different
platforms with different populations, and the residual disagreement is small.

**One caveat on this adjustment, stated because it weakens it.** The Amazon target prevalence used
here is Amazon's *predicted* bucket distribution standing in for its unknown *true* distribution.
Those coincide only if precision is high and errors are roughly symmetric — which is what is being
measured. It is mildly circular. When `data/processed/precision_sample.csv` comes back labelled, the
true prevalence is known and this table should be recomputed. The raw column is the safe one to
quote until then.

---

## 4. The diagnosis: two pattern families carry nearly all the error

This is what a 46,223-row ground truth buys that 300 hand judgements cannot.

| Family | Example patterns | Precision |
|---|---|---|
| **Adjustment advice** | `sized up` 36.1%, `sizing up` 48.9%, `size up` 50.9%, `sized down` 55.3%, `size down` 65.0% | **36–65%** |
| **Partial-area fit** | `too loose/baggy/roomy` 51.8%, `very baggy/loose` 55.1%, `too tight` 57.7%, `a bit tight` 59.2% | **52–77%** |
| Blunt magnitude | `too small` 68.4%, `too big/large` 66.5% | 66–68% |
| **Core "runs" family** | `runs small` 88.5%, `runs large` 90.9%, `ran small` 85.9%, `ran large` 89.2% | **86–91%** |
| **Explicit true-to-size** | `true to size` 95.8%, `perfect fit` 94.7%, `fits perfectly` 88.8% | **89–96%** |

### 4.1 Why "adjustment advice" fails — and it is not really a regex bug

`size up` is not a bad pattern. It is a pattern that measures a **different construct** from the one
the structured field records.

A reviewer who writes *"runs small, I sized up and it was perfect"* clicks **fit** — because the size
they actually received fitted them — while the text is advice about the garment's labelling. The
structured field measures *did the size I bought fit me*. The dictionary here measures *does this
garment run small relative to its label*.

**This deserves the repository owner's attention, because §1.4 does not currently distinguish the
two.** The `fit_score` definition — "garment ran small on the buyer" — reads as the first construct,
but the hypothesis in §1.2 is about which *label* people choose, which is closer to the second. The
two coincide only for buyers who did not adjust. Amazon has no structured field, so on Amazon the
dictionary measures whichever construct the text expresses, mixed. This is a **design question, not
a measurement error**, and it is flagged rather than resolved here.

### 4.2 Why "partial-area fit" fails

"A bit tight" frequently describes one region — bust, shoulders, calf — of a garment whose overall
fit the reviewer then rates as `fit`. On RentTheRunway, where the stock is formalwear, this is
routine. It is a genuine precision problem with no reinterpretation available.

### 4.3 What removal would buy — a projection, not a change

Recomputed with the offending families suppressed. **This is a diagnostic projection. No pattern has
been removed from the dictionary.**

| Configuration | `ran_small` | `true_to_size` | `ran_large` |
|---|---|---|---|
| Current (raw) | 62.7% / 61.5% | 90.0% / 95.3% | 70.5% / 81.1% |
| Drop adjustment-advice | **72.0%** (recall 28.6%) | 92.0% (8.3%) | **78.0%** (22.3%) |
| Drop adjustment + partial-area | **82.9%** (recall 15.9%) | **92.0%** (8.3%) | **81.6%** (20.3%) |

All three buckets clear 80% raw under the second configuration — before any prevalence reweighting,
which would raise `ran_small` further. The price is recall falling to 16–20% of an already selective
population.

**That price is not obviously affordable, and it is not a free win.** Lower recall means a *more*
selectively-sampled labelled set, which makes §5.2's selection model more load-bearing, not less.
Trading precision for selection bias is a real trade, not a strict improvement. On 66M reviews the
absolute volume is not the constraint — the smallest cell is (§5.5), and the men's lower-body cell
is the one to check the trade against.

---

## 5. Against the pre-commitment

| Pre-committed question | Answer |
|---|---|
| Is the gap < 8pp (agreement), 8–15pp (equivocal), or ≥ 15pp (divergence)? | **Not yet answerable.** `P_AM` does not exist — the Amazon hand-labels are outstanding. This document establishes `P_MC` only. |
| Recall pattern | Low recall, high precision on `true_to_size` — **the prompting signature**, pre-committed as not threatening Amazon. Confirmed as predicted. |
| Dictionary failure signature | **Present and specific.** Two named pattern families, consistent across two independent platforms. |
| Population difference | Not separable yet; the two platforms agree with each other after reweighting, which argues the effect is dictionary-driven rather than population-driven. |
| Men's arm | **Zero information, as pre-committed.** Both corpora are women-only. |

The standing rule holds: the §4.1 gate is decided by `P_AM`, the Amazon hand-labelled sample. This
document is diagnostic. It tells us *where* the dictionary breaks and *how* to repair it; it does
not tell us whether the repaired dictionary works on Amazon, and it cannot.

---

## 6. What this changes for the next step

1. **The precision sample now has a second job.** When labelling
   `data/processed/precision_sample.csv`, the rows to watch are those matched by the
   adjustment-advice and partial-area families. If those fail on Amazon the way they fail here, the
   repair is confirmed cross-platform and the case for it is strong.
2. **A construct question is open** (§4.1) and belongs in `PREREGISTRATION.md` before estimation:
   does `fit_score` measure *garment-vs-label* or *received-size-vs-body*? The answer determines
   whether the adjustment-advice family is an error at all.
3. **RentTheRunway's lower cell is 2,643** and it is women-only, so the within-person upper/lower
   design there will be thin. ModCloth is the better vehicle for the women's arm despite being less
   than half the size.
4. **Remaining Phase 2 work**, unstarted: the §1.4 estimator with style fixed effects and clustered
   standard errors, the within-person design, the relocated Chattaraman head-to-head, and the §5.4
   inflation test that these corpora *can* support because they carry purchased size and body
   measurements. That work produces `docs/phase2-women-arm.md`.

## 7. Licence

Like Amazon Reviews'23, the Clothing Fit datasets carry **no licence statement** on the McAuley Lab
distribution page — only a request to cite the RecSys 2018 paper. Same posture as §6 of DESIGN.md:
aggregates and code may be published, the underlying records may not be redistributed, and the raw
snapshots under `data/raw/` must stay out of any published repository.
