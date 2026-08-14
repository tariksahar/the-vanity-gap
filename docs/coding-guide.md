# Coding guide — hand labelling of fit judgements

**Status:** v1.0, frozen before blind labelling begins.
**Purpose:** fixes the rules by which a human assigns `human_label` to a review, so that the
precision measurement of the §5.1 dictionary is consistent across all 300 rows and reproducible
by a second coder.

This document is referenced by `PREREGISTRATION.md` Appendix A and must be complete before any
blind labelling starts. It was developed against a discarded, unblinded sample
(`precision_sample_DISCARDED_2026-08-08_for_coding_rules`) which is not part of any measurement.

---

## 0. The question being answered

For each review, decide:

> **Relative to the buyer's own body, did the garment they actually received run small, fit, or
> run large?**

Not: is this product correctly calibrated against its label. Not: was the buyer happy.
The unit of judgement is **the physical relation between the garment as received and the body
that wore it.**

### Label values

| Value | Meaning |
|---|---|
| `ran_small` | the garment was tight or too small on the wearer |
| `true_to_size` | the garment fitted the wearer |
| `ran_large` | the garment was loose or too big on the wearer |
| `none` | the review says nothing about fit at all |
| `unclear` | the review discusses fit but the direction cannot be determined |

`none` and `unclear` are different and must not be merged. `none` speaks to how often fit is
mentioned at all (the dictionary's recall problem). `unclear` speaks to how often fit is mentioned
but unresolvable (the construct's own ambiguity). Both rates are reported.

**Never guess.** `unclear` is a valid answer and its rate is itself a finding.

---

## 1. Adjustment reports — judge the outcome, not the advice

A review may describe deviating from the buyer's usual size. Two superficially similar cases
resolve differently. The distinguishing question is: **did the garment they actually received fit
them?**

> *"DO order sizes up. Got 2xl and looked like it wouldn't fit an xl man, but it does."*

They received a 2XL and it fitted. → **`true_to_size`**
(The advice "order sizes up" describes the product's calibration, which is not what is being
measured.)

> *"I should have ordered one size down though as it is a little big."*

They received an XL and it was loose on them. → **`ran_large`**

**Rule.** Code the fit of the size actually received. Recommendations to other shoppers about
which size to order describe the product, not the wearer, and are ignored.

---

## 2. Wearer, not buyer

Many reviews are written by someone other than the wearer. What matters is **whose body the fit
judgement describes**, not who paid.

> *"My wife wore these jeans today… the size 27 fit her perfectly."* — women's jeans

The wearer is a woman in women's jeans. The judgement is valid for the women's cell. The reviewer
being her husband is irrelevant. → code normally, **no mismatch flag**.

> *"Great sleepwear for a woman… This shirt in a size small fits me perfectly (I'm 5' and 110#)"*
> — men's shirt

The wearer is a woman; the product is men's. This contaminates the men's cell. → code the fit
normally, **and set the mismatch flag**.

**Rule.** Set the mismatch flag when the fit judgement is given for a body whose gender differs
from the product's gender. Buying on someone else's behalf is not by itself a mismatch.

*Note: the column is currently named `buyer_gender_mismatch`. It should be read as
**wearer** gender mismatch, and renamed accordingly.*

---

## 3. Partial-area comments

Most single-region complaints are unambiguous and should be coded in the direction stated.

> *"Small in the bust. For a 3X, I expected it to fit generously and it was way too small in the
> bust."* → **`ran_small`**

Use `unclear` only when regions genuinely conflict, or the judgement is conditional on an
assumption about the reader's body.

> *"recommend sizing up if not petite… the sleeves were tight if tight around the chest if big
> chested. Nice length though."* → **`unclear`** (conditional, partial, and internally garbled)

**Rule.** A single region is enough if the direction is clear and undisputed elsewhere in the
review. Conflicting regions, or a judgement conditioned on a hypothetical body, are `unclear`.

---

## 4. Physical fit, not satisfaction — the most consequential rule

A buyer may deliberately choose a larger size and be pleased with the result. Their satisfaction
does not change the garment's relation to their body.

> *"Perfect fit. Loose, but still flattering."*

The garment is loose on the wearer. → **`ran_large`**, despite "perfect fit".

**Why this matters.** The hypothesis under test predicts exactly this behaviour: buyers who size up
deliberately and are content with the result. Coding satisfaction rather than physical fit would
make the measure blind to the phenomenon it exists to detect.

**Rule.** When the review describes the garment physically — loose, roomy, baggy, tight, snug,
clingy — code that description, regardless of whether the buyer approves of it. Code
`true_to_size` only when the garment is described as fitting, not merely as satisfactory.

**Known limitation, to be recorded in the write-up.** A buyer who sized up deliberately and is
happy may not describe the looseness at all, writing only that the item is good. Those cases yield
no signal in either direction. The fit-report measure therefore under-captures *intentional*
deviation, and captures *unintended* misfit more completely. This is the principal reason the
direct self-reported deviation measure ("I usually wear M, ordered L") is complementary to this
one rather than merely supplementary.

---

## 5. Washing and shrinkage

Fit may change after laundering.

> *"Purchased a xxl. Its huge compared to a xl. But they shrink easy enough. My suggestion buy a
> size larger… when it shrinks it doesnt look like your wearing your kids hoody."*

**Rule.** Code the fit **as first worn**. That is the outcome of the sizing decision; shrinkage is
a property of the fabric that follows it. If the review describes only the post-laundering state,
code that state. If both are described, the initial fit takes priority.

---

## 6. Multiple products in one review

> *"ordered two pair at the same time different colors different sellers. These ran big, the other
> ones fit much closer to true."*

**Rule.** Code only the product this review is attached to. Comparisons with other items — other
sizes, other colours, other brands — are context, not data. A comparative statement about the
reviewed product itself ("runs smaller than other Under Armour XL shirts") **is** a valid fit
judgement and should be coded.

---

## 7. Non-garment items

The sample is drawn from items that resolve to a gender and a body half under §1.3, so accessories,
footwear and watches should be largely absent. If one appears — a bag, a watch strap, eyewear —
"too big" refers to object dimensions, not fit.

**Rule.** Non-garment items are `none`, regardless of how fit-like the language looks.

---

## 8. Stated calibration — an additional flag

Some reviewers explicitly attribute the sizing to the brand or its origin rather than to their own
choice.

> *"Ive bought like 5 shirts on amazon… ive learned to buy 2 sizes up, even 3… These shirts must
> all be tiny asia sizes."*

This is the seller-calibration confound stated in the reviewer's own words: the deviation is the
manufacturer's ruler, not the buyer's preference.

**Rule (sharpened 2026-08-14 — the original wording was too loose).** Set `calibration_stated`
only when the review names **a brand, a manufacturer, or a regional sizing convention as the CAUSE**
of the sizing. Code the fit label normally as well — the flag is additional, not a substitute.

**The distinction is WHAT versus WHY.**

| | |
|---|---|
| *"runs big"*, *"too small"*, *"sized up"* | an **observation** about this garment → **`no`** |
| *"these must all be tiny asia sizes"*, *"this brand always runs small"*, *"Chinese sizing"* | an **attribution of cause** → **`yes`** |

Without that restriction the flag simply duplicates `human_label` and carries no independent
information: every `ran_small` review describes a garment running small, so flagging them all
measures nothing.

**The sample was re-coded under this rule.** Under the loose reading 27 of 149 rows were flagged;
under the sharpened reading **3 of 149 (2.0%)**. The operative figure is 3, and it is a **lower
bound** — a reviewer affected by seller calibration who does not say so is not counted.

This gives a cheap manual lower bound on the calibration confound without waiting for the
full-corpus seller-concentration analysis.

---

## 9. Columns to be filled

| Column | Values |
|---|---|
| `human_label` | `ran_small` / `true_to_size` / `ran_large` / `none` / `unclear` |
| `wearer_gender_mismatch` | `yes` / `no` / `unclear` |
| `calibration_stated` | `yes` / `no` |

Leave nothing blank. `unclear` and `no` are answers.

---

## 10. Procedure

Labelling is **blind**: the coder sees the review text and the product title, and does not see the
dictionary's assigned bucket, the stratum, the gender or the body half. Blindness is required —
seeing the assigned label anchors the judgement toward agreement and inflates measured precision.

Labels are joined back to the key file on `review_id_hash` after all rows are complete.

This guide is frozen at v1.0. If a case arises that none of the rules above resolve, do not
improvise: record the row, finish the remaining rows, and amend the guide as a dated revision
before re-labelling the affected rows. Rules changed mid-pass produce an inconsistent measurement.


---

## 11. Revisions

### 2026-08-14 — Rule 8 sharpened

`calibration_stated` narrowed to require an attribution of cause, not an observation of effect. See
Rule 8 above for the wording and the what-versus-why table. The 149 labelled rows were re-coded:
27 flagged under the loose reading, **3** under the sharpened one.

### 2026-08-14 — Rule 1 / Rule 4 boundary, clarified

Four rows in the labelled set were genuine judgement calls at the boundary between Rule 1 (code the
size actually received, ignore advice) and Rule 4 (code physical fit, not satisfaction): **a buyer
deliberately sizes up, and is content with the resulting looseness.**

The resolution applied, and now binding for all future labelling:

> **Code the realized fit of the garment received, even when the looseness was intended and the
> buyer is satisfied with it.** A deliberate size-up that produced a loose garment is `ran_large`.

This follows from both rules rather than trading them off: Rule 1 says judge the size received, and
Rule 4 says judge the physical relation rather than the buyer's approval of it. It is recorded here
because the four rows were decided consistently and that decision is now the operative reading, not
because the rules conflicted.

Worked example from the set — *"Read reviews and thought I ordered accordingly. Went a size up, but
should have just gotten a small… Got a medium. Won't bother returning it, but would have preferred
the small"* → **`ran_large`**. The reviewer sized up, the garment is bigger than they wanted, and
their tolerance of it does not change the physical fact.

**Consequence for the dictionary, not for the guide.** The regex reads *"went a size up"* as
`ran_small`, because the phrase describes the product's calibration. The human reads the realized
fit as `ran_large`. This is the §5.3 construct split showing up as a measured disagreement rather
than an argument, and it is the reason adjustment-advice language is a style-level covariate rather
than part of `fit_score`.

### 2026-08-14 — uncovered contamination type, noted not fixed

One labelled row is an **adult women's product reviewed for a 7-year-old wearer**. §1.3 excludes
children's *products* but says nothing about child *wearers* of adult products, so the exclusion
does not catch it and neither does `wearer_gender_mismatch`, which asks about gender rather than
age.

Recorded, deliberately **not fixed**: one occurrence in 149 rows is not evidence of a systematic
problem, and adding an age rule on that basis would be fitting the guide to a single case. If it
proves common in later labelling, it needs its own flag.
