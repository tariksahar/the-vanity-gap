"""Wild cluster bootstrap, and the effective MDE it implies.

**Why this module exists.** With one cluster carrying a third of a cell, the
asymptotic cluster-robust variance estimator undercovers at any clustering level
-- the asymptotics are in the NUMBER of clusters, and one dominant cluster makes
the effective number small however many nominal clusters there are. The fix is
not a different sample. It is Cameron, Gelbach & Miller (2008): resample the
residuals with cluster-level sign flips, impose the null, and read the p-value off
the bootstrap distribution of the t-statistic.

**The consequence for the A5 numbers.** `MDE_design = 0.568` for the keep-listings
scenario comes from

    DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC

which is a formula about a size DISTRIBUTION. It has no term for "one cluster is
34% of the cell", and it is exactly this configuration in which it stops
describing the estimator's behaviour. So "keeping them requires lambda >= 1.89,
which is impossible" rests on the least trustworthy calculation in the whole
apparatus. Both numbers are reported side by side and the formula one is not
quoted alone.

**What is simulated.** Under the null there is no effect; the outcome is
`fit_score` in {-1, 0, +1} drawn to match the measured cell composition, with an
intra-cluster component so that the ICC is the assumed one. An effect is imposed
on the men's-upper cell, WCB is run with Rademacher weights, and power is the
rejection rate. The MDE is the smallest imposed effect reaching 80% power.

**What it assumes, stated because a simulation invites over-trust.** The ICC is
imposed rather than measured (as everywhere else in this project). The
cluster-size distribution is the measured one, which is the part that matters
here. The outcome is generated as a three-point variable rather than assumed
normal, because the whole point is that this outcome is coarse and lumpy.

Usage:
    python src/analysis/wild_bootstrap.py
"""

from __future__ import annotations

import math
import random
import statistics
import sys


def _t_stat(y: list[float], x: list[float], groups: list[int]) -> tuple[float, float]:
    """OLS slope and cluster-robust t on a single regressor with intercept."""
    n = len(y)
    xbar = sum(x) / n
    ybar = sum(y) / n
    sxx = sum((xi - xbar) ** 2 for xi in x)
    if sxx <= 0:
        return (0.0, 0.0)
    beta = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y)) / sxx
    alpha = ybar - beta * xbar
    resid = [yi - alpha - beta * xi for xi, yi in zip(x, y)]

    # CR1-style cluster-robust meat, sum over clusters of (sum_i x~_i u_i)^2
    by_group: dict[int, float] = {}
    for xi, ui, g in zip(x, resid, groups):
        by_group[g] = by_group.get(g, 0.0) + (xi - xbar) * ui
    meat = sum(v * v for v in by_group.values())
    n_g = len(by_group)
    if n_g <= 1 or meat <= 0:
        return (beta, 0.0)
    scale = n_g / (n_g - 1)
    var = scale * meat / (sxx * sxx)
    return (beta, beta / math.sqrt(var)) if var > 0 else (beta, 0.0)


def wcb_pvalue(y: list[float], x: list[float], groups: list[int],
               replicates: int = 399, rng: random.Random | None = None) -> float:
    """Two-sided wild cluster bootstrap p-value for H0: slope = 0.

    Rademacher weights, null imposed by regressing on the intercept only and
    resampling the restricted residuals.
    """
    rng = rng or random.Random(0)
    _beta, t_obs = _t_stat(y, x, groups)

    ybar = sum(y) / len(y)
    restricted = [yi - ybar for yi in y]          # null imposed: slope = 0

    unique = sorted(set(groups))
    count = 0
    for _ in range(replicates):
        flip = {g: (1.0 if rng.random() < 0.5 else -1.0) for g in unique}
        y_star = [ybar + restricted[i] * flip[groups[i]] for i in range(len(y))]
        _b, t_star = _t_stat(y_star, x, groups)
        if abs(t_star) >= abs(t_obs):
            count += 1
    return (count + 1) / (replicates + 1)


def _draw_cell(sizes: list[int], shares: dict[str, float], effect: float,
               icc: float, rng: random.Random) -> tuple[list[float], list[int]]:
    """Generate one cell: three-point outcome, cluster random effect, effect shift."""
    scores = (-1.0, 0.0, 1.0)
    probabilities = (shares["ran_small"], shares["true_to_size"], shares["ran_large"])
    sd_cluster = math.sqrt(icc)
    y: list[float] = []
    groups: list[int] = []
    for index, size in enumerate(sizes):
        shift = rng.gauss(0.0, sd_cluster)
        for _ in range(size):
            base = rng.choices(scores, weights=probabilities, k=1)[0]
            y.append(base + shift + effect)
            groups.append(index)
    return y, groups


def power_at(effect: float, cell_sizes: dict[str, list[int]],
             shares: dict[str, dict[str, float]], icc: float,
             trials: int = 200, replicates: int = 399,
             seed: int = 20260815) -> float:
    """Rejection rate of WCB at 5% for an effect imposed on men/upper."""
    rng = random.Random(seed)
    rejections = 0
    for _ in range(trials):
        y: list[float] = []
        x: list[float] = []
        groups: list[int] = []
        offset = 0
        for cell, sizes in cell_sizes.items():
            shift = effect if cell == "men_upper" else 0.0
            cy, cg = _draw_cell(sizes, shares[cell], shift, icc, rng)
            y.extend(cy)
            x.extend([1.0 if cell == "men_upper" else 0.0] * len(cy))
            groups.extend(g + offset for g in cg)
            offset += len(sizes)
        if wcb_pvalue(y, x, groups, replicates, rng) < 0.05:
            rejections += 1
    return rejections / trials


def mde_wcb(cell_sizes, shares, icc: float, target_power: float = 0.80,
            grid=(0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80),
            **kwargs) -> tuple[float | None, list[tuple[float, float]]]:
    """Smallest effect on the grid reaching `target_power`. Returns (mde, curve)."""
    curve = []
    found = None
    for effect in grid:
        p = power_at(effect, cell_sizes, shares, icc, **kwargs)
        curve.append((effect, p))
        if found is None and p >= target_power:
            found = effect
    return found, curve


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("wild cluster bootstrap -- self-check")
    rng = random.Random(1)
    # Under the null the p-value should be roughly uniform, so rejection ~5%.
    sizes = [50] + [3] * 40
    shares = {"ran_small": 0.30, "true_to_size": 0.53, "ran_large": 0.17}
    rejections = 0
    trials = 120
    for _ in range(trials):
        y, g = _draw_cell(sizes, shares, 0.0, 0.05, rng)
        y2, g2 = _draw_cell(sizes, shares, 0.0, 0.05, rng)
        yy = y + y2
        xx = [1.0] * len(y) + [0.0] * len(y2)
        gg = g + [i + len(sizes) for i in g2]
        if wcb_pvalue(yy, xx, gg, 199, rng) < 0.05:
            rejections += 1
    print(f"  null rejection rate at 5%: {rejections / trials:.3f} "
          f"(should be near 0.05; {trials} trials)")
    print("  a rate far above 0.05 would mean the bootstrap is not imposing the null")
