"""MDE for the gradient tested as an ORDERED CONTRAST rather than cell means.

DESIGN.md 1.2 predicts an ORDERING -- deviation largest in tees, medium in
shirts, near zero in jeans/trousers -- not three particular values. Testing that
as three cell means and their pairwise differences spends several degrees of
freedom on a claim that has one, and it throws away the middle category by
pooling tee and shirt into "upper".

An ordered contrast codes garment constraint as an ordered variable and
estimates a single trend coefficient. It spends one degree of freedom, uses every
observation including the shirts, and matches the shape of the hypothesis.

For grouped data with `n_k` observations at ordered position `x_k`, weighted
least squares gives

    beta_hat = sum_k n_k (x_k - xbar) ybar_k / S,   S = sum_k n_k (x_k - xbar)^2
    Var(beta_hat) = sigma^2 * DEFF / S

with `xbar` the observation-weighted mean position. The estimand is the
difference in trend between genders,

    tau_trend = beta_men - beta_women
    Var(tau_trend) = sigma^2 * DEFF * (1/S_men + 1/S_women)

`S` is the key quantity and it rewards SPREAD as well as count: observations at
the extremes of the ordering carry more weight than observations in the middle,
so a thin jeans cell hurts more than a thin shirt cell.

COMPARABILITY -- the trap this module exists to avoid. The trend coefficient is
per STEP of constraint. The 2x2 contrast is the difference between pooled upper
and pooled lower, and under a linear trend that contrast estimates

    (xbar_upper - xbar_lower) * beta

which is typically about 1.5 steps, not 2. Comparing a two-step trend against a
1.5-step contrast makes the trend look worse than it is. Both are therefore
converted to the SAME underlying per-step slope `beta` before comparison, which
is the only basis on which the two designs are estimating the same thing.

`design_effect` is imported from the recovered Phase 0 module rather than
reimplemented.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from src.analysis.power import design_effect, z  # noqa: E402

# Ordered constraint positions. Higher = more escape from fit permitted, which
# is the direction in which DESIGN.md 1.2 predicts larger deviation.
POSITIONS = {"jeans_trousers": 0.0, "shirt": 1.0, "tshirt": 2.0}
FULL_SPAN = 2.0


def _scatter(counts: dict[str, float]) -> float:
    """S = sum_k n_k (x_k - xbar)^2 for one gender."""
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    xbar = sum(POSITIONS[k] * n for k, n in counts.items()) / total
    return sum(n * (POSITIONS[k] - xbar) ** 2 for k, n in counts.items())


def mde_trend(men: dict[str, float], women: dict[str, float], *,
              mean_cluster_size: float, icc: float, cv: float = 0.0,
              alpha: float = 0.05, power: float = 0.80,
              per_step: bool = False) -> float:
    """MDE on the gender difference in constraint trend, in SD of fit_score.

    Returns the effect over the full jeans-to-tee span by default, so it is
    directly comparable with a pooled upper-vs-lower contrast. `per_step=True`
    returns the per-step coefficient instead.
    """
    s_men, s_women = _scatter(men), _scatter(women)
    if s_men <= 0 or s_women <= 0:
        raise ValueError("a gender has no spread across the ordering; "
                         f"trend unidentified (S_men={s_men}, S_women={s_women})")
    deff = design_effect(mean_cluster_size, icc, cv)
    variance = deff * (1.0 / s_men + 1.0 / s_women)
    per_step_mde = (z(1 - alpha / 2) + z(power)) * variance ** 0.5
    return per_step_mde if per_step else per_step_mde * FULL_SPAN


def _pooled_span(counts: dict[str, float]) -> float:
    """xbar_upper - xbar_lower, the number of steps the 2x2 contrast spans."""
    tee, shirt = counts.get("tshirt", 0), counts.get("shirt", 0)
    upper = tee + shirt
    if upper <= 0:
        return 0.0
    xbar_upper = (POSITIONS["tshirt"] * tee + POSITIONS["shirt"] * shirt) / upper
    return xbar_upper - POSITIONS["jeans_trousers"]


def mde_cellmeans(men: dict[str, float], women: dict[str, float], *,
                  mean_cluster_size: float, icc: float, cv: float = 0.0,
                  alpha: float = 0.05, power: float = 0.80) -> float:
    """MDE for the same data pooled into a 2x2: (tee + shirt) vs jeans.

    This is what the gradient looks like when forced into the upper/lower
    estimand. It discards the middle category's position information -- shirts
    are counted as "upper" alongside tees -- which is the cost the trend test
    avoids.
    """
    cells = []
    for counts in (men, women):
        upper = counts.get("tshirt", 0) + counts.get("shirt", 0)
        lower = counts.get("jeans_trousers", 0)
        cells.extend([upper, lower])
    if any(n <= 0 for n in cells):
        raise ValueError(f"empty cell; tau unidentified: {cells}")
    deff = design_effect(mean_cluster_size, icc, cv)
    variance = sum(deff / n for n in cells)
    return (z(1 - alpha / 2) + z(power)) * variance ** 0.5


def mde_cellmeans_in_beta(men: dict[str, float], women: dict[str, float],
                          **kwargs) -> float:
    """The 2x2 contrast MDE expressed as a per-step slope.

    Under a linear trend the pooled contrast estimates (xbar_upper - xbar_lower)
    * beta, so dividing by that span converts it to beta units. Both genders'
    spans are averaged, weighted by how much each contributes to the variance.
    """
    contrast = mde_cellmeans(men, women, **kwargs)
    spans = [_pooled_span(men), _pooled_span(women)]
    span = sum(spans) / 2.0
    if span <= 0:
        raise ValueError("pooled contrast spans zero steps")
    return contrast / span


def efficiency_gain(men: dict[str, float], women: dict[str, float], **kwargs) -> float:
    """Ratio of cell-means MDE to trend MDE, BOTH in per-step beta units.

    > 1 means the ordered contrast is better powered on the same observations.
    """
    trend = mde_trend(men, women, per_step=True, **kwargs)
    return mde_cellmeans_in_beta(men, women, **kwargs) / trend
