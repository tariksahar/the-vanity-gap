# Divergence pre-commitment — dictionary validation across corpora

**Written 2026-08-08, before any ModCloth or RentTheRunway record was read.**
Nothing in this document was composed with knowledge of the numbers it governs. Its purpose is to
fix the interpretation of a result before the result exists, because the three candidate
explanations for divergence are all plausible and choosing between them afterwards is how a project
talks itself into the answer it wanted.

Referenced by `docs/phase1-amazon-probe.md` and to be folded into `PREREGISTRATION.md` (§7.2).

---

## 1. What is being compared

Two independent estimates of the same quantity — the precision of the §5.1 regex dictionary.

| | Source of truth | Scale | Covers |
|---|---|---|---|
| **P_MC** | ModCloth + RentTheRunway structured fit field | thousands of rows | women only |
| **P_AM** | Amazon CSJ hand-labelled sample, 100/bucket, gender-stratified | 300 judgements | men and women |

`P_MC` is obtained by running the dictionary over review text and comparing its output to the
structured label on the same record. `P_AM` is obtained by the repository owner labelling
`data/processed/precision_sample.csv` by hand.

## 2. Standing rule: which number is binding

**The §4.1 gate is decided by `P_AM`, not `P_MC`, in every scenario in this document.**

ModCloth and RentTheRunway prompt for fit; Amazon reviewers volunteer it. The vocabularies are
therefore drawn from different registers, and `P_MC` is an **upper bound** on Amazon performance,
not a transfer. This rule is stated first and up front precisely so that a comfortable `P_MC` cannot
later be substituted for an uncomfortable `P_AM`.

The role of `P_MC` is **diagnostic, not evidentiary**: it identifies *which individual patterns*
fail, at a volume no hand-labelling exercise can reach. That is a genuinely valuable thing and it
is the reason to run it. It is not a licence to skip the hand-labels.

**Corollary, and the sharpest limitation here.** ModCloth and RentTheRunway are women-only. They
provide **zero** validation for the men's arm, which is the one arm where the dictionary is being
extrapolated and the one arm that carries the novel contribution. No quantity of ModCloth
ground-truth closes that gap. The men's precision number can come only from the men's stratum of
the Amazon hand-sample.

## 3. What counts as divergence

`P_AM` at n=100 per bucket has a standard error of about 4 pp near p=0.8. `P_MC` rests on thousands
of rows, so its own error is negligible by comparison. The standard error of the difference is
therefore about 4 pp, and a 95% interval is about ±8 pp.

| Gap between `P_MC` and `P_AM`, per bucket | Reading |
|---|---|
| < 8 pp | Agreement — within sampling noise. |
| 8–15 pp | Equivocal. Report as equivocal; do not narrate it as either. |
| ≥ 15 pp | Real divergence. Section 5 applies. |

Comparisons are made **per bucket**, not on a pooled average. A pooled average can hide a bucket
that has collapsed — which is exactly what happened in the first hand-check, where `ran_large` scored
0/4 on `Amazon_Fashion` while the pooled figure looked survivable.

## 4. Confounds removed before the comparison is read

Three adjustments are specified now, so that they are corrections rather than rescues:

1. **Scope match.** Restrict ModCloth/RentTheRunway to items resolving to `upper` or `lower` under
   §1.3 — this drops dresses, which are a large part of ModCloth. Compare against the Amazon sample,
   which is already garment-filtered by construction.
2. **Gender match.** Compare `P_MC` against the **women's stratum** of `P_AM`. Comparing a
   women-only corpus against a mixed-gender sample would confound gender with corpus.
3. **Prevalence reweighting.** Precision depends on the base rate of each bucket, and the base rates
   genuinely differ: Amazon reviewers volunteer fit comments mostly when the fit was *wrong*, so
   `true_to_size` is rarer there. Report `P_MC` both raw **and** reweighted to the bucket prevalence
   observed in the Amazon labelled set. A gap that closes under reweighting was a base-rate
   artefact, not a dictionary problem.

If a gap survives all three adjustments, it is a real difference between the corpora.

## 5. Interpretation, fixed in advance

### 5.1 The three candidate explanations have different signatures

| Explanation | Predicted signature | How it is distinguished |
|---|---|---|
| **Prompted-vs-volunteered selection (§5.2)** | Hits **recall**, not precision. On ModCloth every record carries a structured label whether or not the text discusses fit, so many true labels have no fit language to match. Precision — of the reviews where the dictionary fires, how many agree — should be largely unaffected. | **Low recall with high precision is the prompting signature and does not threaten Amazon.** Report recall separately and do not read it as a precision failure. |
| **Dictionary failure** | **Pattern-specific and consistent across corpora.** The same named regex misfires in both places. | Report **per-pattern** precision on ModCloth, not just per-bucket, and cross-reference against the patterns that produced errors in the Amazon hand-labels. An overlapping set of offending patterns is the signature. |
| **Population difference** | Precision differs, but the **failure modes differ in kind** — different patterns, different vocabulary, no shared offender set. | Survives the §4 scope, gender and prevalence matching while the offending-pattern sets stay disjoint. |

These are not mutually exclusive and the report will not force a single winner where the evidence
supports two.

### 5.2 Direction matters, and the two directions are not symmetric

**If `P_AM` < `P_MC` — Amazon worse.** The expected direction. Candidate causes: volunteered-register
vocabulary, marketplace text quality, residual non-garment contamination. **Action: the Amazon number
governs.** ModCloth cannot rescue a corpus it is not drawn from. If `P_AM` for any bucket falls below
~80%, the gate fails on that bucket regardless of how good `P_MC` looks.

**If `P_AM` > `P_MC` — Amazon better.** Surprising, and the first hypothesis is **not** that the
dictionary is excellent. The likelier cause is noise in the ModCloth structured label itself: the
field records the buyer's verdict on their own purchase, while the text may discuss a different
size, a different garment, or nothing about fit at all. **Action: treat `P_MC` as a floor, and do
not let it raise confidence in Amazon above what `P_AM` independently supports.** In this branch
`P_MC` is discarded as a validation instrument and retained only for per-pattern diagnosis.

### 5.3 If they agree

Agreement is consistent with a dictionary that works, and it will be reported as encouraging. It is
**not** proof of transfer: both corpora could share a bias — for instance both over-firing on
"too small" used about a non-fit attribute. Agreement raises confidence for the **women's** arm
only. It says nothing about men (§2, corollary).

## 6. Actions on failure, chosen now

If a bucket's `P_AM` falls below ~80%, in this order of preference:

1. **Repair the offending patterns** identified by the ModCloth per-pattern diagnosis, then **draw a
   fresh Amazon hand-sample and re-measure.** The existing labels cannot be reused to score a
   repaired dictionary — that is fitting to the validation set. This costs a second labelling round
   and that cost is accepted.
2. **Drop the low-precision patterns** and accept lower recall. Precision is the gate; recall only
   has to be sufficient for the smallest cell (§5.5).
3. **Abandon the text route.** Phase 2's women's arm becomes the deliverable and the men's arm waits
   on a corpus with a structured fit field, or on the §4.6 survey.

Reinterpreting the threshold downward is not on this list.

## 7. Anti-gaming clauses

- The dictionary is **not** modified in response to ModCloth results except through a dated,
  recorded amendment in `PREREGISTRATION.md` that triggers a fresh Amazon hand-sample (§6.1).
- The two removals made on 2026-08-08 (`large in size`, `small in size`) predate this document and
  predate any ModCloth result; they are recorded in `amazon_fit_probe.py` at the removal site and in
  `docs/phase1-amazon-probe.md`.
- Bucket-level results are reported for all three buckets whichever way they fall. A bucket is not
  dropped from the report for being inconvenient.
- Recall is reported alongside precision everywhere, so that a high-precision, low-recall dictionary
  cannot be presented as unqualified success.
