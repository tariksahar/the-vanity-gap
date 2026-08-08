# Phase 1b — self-reported size deviation probe

**Date:** 2026-08-08
**Instrument:** `size_deviation_probe.py`
**Corpus:** `Clothing_Shoes_and_Jewelry`, 800,000 reviews streamed, 250,000 item metadata records
**Access:** stream-only, nothing downloaded, nothing written to disk

---

## 0. Verdict

**It works, it is real, and it does not become the primary measure.** The language exists at
0.20% of reviews — about **131,000 direct observations** across the full corpus — and the extraction
is accurate. But the cell that carries identification, men's lower-body, holds **4 observations per
800,000 reviews**, which extrapolates to roughly 330 corpus-wide. §5.5 again: the total is generous
and the binding cell is not.

Recommended standing: a **triangulation measure on the women's arm**, and a **qualitative check**
on the men's arm, not a replacement for `fit_score`.

---

## 1. Prevalence

| | n | share of 800,000 |
|---|---|---|
| states a usual size | 5,299 | 0.66% |
| states a bought size | 17,895 | 2.24% |
| **states both, unambiguously** | 1,624 | 0.20% |
| less third-party / cross-gender | 37 | 2.28% of pairs |
| **usable direct observations** | **1,587** | **0.20%** |

Extrapolated to the 66.0M-review corpus: **≈131,000 usable observations.**

That is below the 1–2% the task anticipated, but the absolute number is still large. The constraint
is not the total.

## 2. Signed deviation

`deviation = ladder(bought) − ladder(usual)`; positive means bought **larger** than usual.

| deviation | n | share |
|---|---|---|
| −3 | 2 | 0.13% |
| −2 | 11 | 0.69% |
| −1 | 184 | 11.59% |
| **0** | **346** | **21.80%** |
| **+1** | **797** | **50.22%** |
| +2 | 207 | 13.04% |
| +3 | 36 | 2.27% |
| +4 | 4 | 0.25% |

Mean **+0.708** ladder steps. Bought larger 65.78%, same 21.80%, smaller 12.41%.

**Do not read this as a finding.** Only 21.8% of these reviewers report *no* deviation, which is
not credible as a picture of buying behaviour and is instead a direct measurement of the selection
hazard written into §5.11 before this probe ran: **people narrate a decision they consider unusual.**
Someone who bought their normal size has no story to tell and does not write the sentence. The
distribution above describes who writes, not who buys.

## 3. Cells — the binding constraint

Join to in-scope styles: 398 of 1,587 pairs (25.08%), from an index of 57,256 in-scope styles.

| | upper | lower |
|---|---|---|
| **men** | 34 (+0.21) | **4** (+0.25) |
| **women** | 306 (+0.80) | 54 (+0.65) |

Cell entries are *n* (mean signed deviation).

Two things this table settles:

**The men's lower-body cell is 4.** Corpus-wide that is roughly 330 observations, clustered at the
style level, for the cell that anchors the §1.5 placebo test. This measure cannot carry the primary
estimand.

**Women outnumber men roughly 9:1 in this language** (306 vs 34 upper). That is a much sharper
asymmetry than the fit-comment asymmetry of §5.2, and it points the same way: men write less about
sizing. It is a finding about reporting behaviour and worth keeping.

**On the direction, stated plainly because it runs against the hypothesis.** Women's mean deviation
(+0.80) exceeds men's (+0.21) in both halves — the opposite of §1.2's prediction that men size up
and women size down. This is **not** evidence against the hypothesis and must not be reported as
though it were: n = 34 and 4 for men, the sample is selected on having deviated, and the sexes may
narrate deviation at different rates for reasons unrelated to how they buy. It is recorded here
because §7.2 requires stating in advance what would refute the hypothesis, and this is the first
number that has pointed the wrong way. If the same sign survives a proper estimate on adequate
cells, that is a refutation and must be published as one.

## 4. Extraction quality

Hand-scored on the 15 printed examples: **12/15 correct.**

All three errors share one fixable defect: a **disjunctive usual size** is silently resolved to its
first term rather than dropped.

- *"i normally wear a l/xl i ordered an xxl"* → recorded usual = L
- *"i usually wear a small or medium and ordered a medium"* → recorded usual = S, deviation +1
  when the honest reading is 0
- *"i usually wear a l or xl top … opted for the l"* → recorded usual = L

Note the direction: in two of the three the error **inflates** the measured deviation. The fix is to
treat `X or Y` and `X/Y` as ambiguous and drop, consistent with §5.1's rule that ambiguity is a drop
and never a guess. Not applied yet — the probe is reported as run.

The third-party filter removed 37 pairs (2.28%), and the sampled extractions show it working: pairs
where one person's usual size is paired with another person's purchase are meaningless, not merely
suspect, so they are dropped rather than flagged here.

## 5. What to do with it

1. **Not the primary measure.** The men's lower cell forbids it.
2. **Triangulation on the women's arm**, where cells are adequate (306 and 54 per 800k, so roughly
   25,000 and 4,500 corpus-wide). If the women's `fit_score` result and the women's direct-deviation
   result agree, that is genuine convergent evidence from two different constructs.
3. **Fix the disjunctive-size defect** before any use beyond feasibility.
4. **Model its selection separately.** §5.11 already forbids inheriting the §5.2 reporting model;
   this probe's 21.8%-zero-deviation figure shows why in one number.
5. **The 9:1 gender asymmetry in sizing talk is worth reporting in its own right**, alongside §5.2's
   prompted-response asymmetry. Two independent corpora now show men writing less about size.
