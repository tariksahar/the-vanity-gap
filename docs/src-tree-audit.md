# `src/` tree audit — what was lost in the move, and what was recovered

**Date:** 2026-08-11
**Trigger:** `src/analysis/power.py` was found absent when the MDE calculation was requested,
despite being listed in `docs/phase0-collection-blocker-and-power.md` §4 as delivered.

---

## 1. What happened

The repository was rebuilt at `Desktop/the-vanity-gap` (hyphenated). The Phase 0 working tree lived
at **`Desktop/vanity_gap`** (underscore) and was never moved across. Because the git repository was
initialised fresh in the new location, there was no history to reveal the gap — the files were not
deleted, they were simply somewhere else, and every module written since was written from scratch on
top of an incomplete tree.

**Nothing was lost.** All five modules and the Mavi raw snapshot were recovered intact.

## 2. Inventory

Against the list published in `docs/phase0-collection-blocker-and-power.md` §4:

| Path | Status before audit | Now |
|---|---|---|
| `src/collect/http.py` | **missing** | recovered |
| `src/adapters/mavi.py` | **missing** | recovered |
| `src/collect/catalog.py` | **missing** | recovered |
| `src/analysis/power.py` | **missing** | recovered |
| `src/analysis/run_power_scenarios.py` | **missing** | recovered |
| `src/__init__.py`, `src/adapters/__init__.py`, `src/collect/__init__.py`, `src/analysis/__init__.py`, `tests/__init__.py` | missing | recovered |
| `data/raw/mavi/2026-08-07/robots.txt` | **missing** | recovered |

Written during this phase and unaffected:

| Path | Origin |
|---|---|
| `src/analysis/buyer_gender.py` | Phase 1, buyer-vs-garment gender filter |
| `src/analysis/validate_dictionary.py` | Phase 2a, ModCloth/RTR ground truth |
| `src/analysis/run_window_power.py` | Phase 1c, MDE by window |

**The recovered `robots.txt` matters beyond tidiness.** It is a dated raw capture under §0.4, and it
is the evidence that Mavi's access rules were checked before collection was attempted. Losing it
would have left an ethics claim in `ETHICS.md` §2 with no artifact behind it.

## 3. Reconciliation of the power figures

Before the tree was found, a replacement `power.py` was written from the formulas as documented in
`docs/phase0-collection-blocker-and-power.md` §3. The original was then recovered, and the
replacement was **discarded in favour of it** — the original is what produced the published table,
and keeping two implementations of one formula is a place for them to diverge silently.

They agree. Both implement the Eldridge/Kerry design effect

```
DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC
```

and the same variance sum, `Var(tau) = sum_k DEFF_k / n_k`, with
`MDE = (z_0.975 + z_0.80) * sqrt(Var(tau))`. Spot-check against the published Phase 0 design-effect
table, recomputed with the recovered module:

| ICC | CV=0 | CV=1 | CV=2 |
|---|---|---|---|
| 0.02 | 1.38 | 1.78 | 2.98 |
| 0.05 | 1.95 | 2.95 | 5.95 |
| 0.10 | 2.90 | 4.90 | 10.90 |

Identical to the published table. No figure in `docs/phase0-collection-blocker-and-power.md`
requires revision, and the Amazon MDE in `PREREGISTRATION.md` §7.1a is computed with the same module
and is therefore comparable with it rather than merely similar.

**One difference in usage, stated because it changes what the numbers mean.** Phase 0 applied a
`response_rate` per cell to convert raw Mavi reviews into answered ones. On Amazon there is no
prompted fit question; the label is derived from text, so the dictionary's recall has already been
applied and the window-probe counts are *already* usable observations. `response_rate` is therefore
1.0 in `run_window_power.py`. Setting it otherwise would deflate the counts twice.

## 4. Standing changes

1. The recovered tree is now tracked in the published repository, so this cannot recur silently.
2. `Desktop/vanity_gap` is left in place, untouched, until the recovered files have been confirmed
   against it. It is not the working directory and nothing should be written to it.
3. Any future claim in an artifact that a file was delivered should be checkable against the tracked
   tree. That is now true; before this audit it was not.
