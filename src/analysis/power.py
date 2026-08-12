"""Minimum detectable effect for the difference-in-differences estimand.

The estimand is

    tau = ( E[fit | men,   upper] - E[fit | men,   lower] )
        - ( E[fit | women, upper] - E[fit | women, lower] )

estimated as a single interaction regression with style-level fixed effects and
standard errors clustered on style.

Three things inflate the standard error above the textbook value, and all three
are properties of this dataset specifically:

1.  Clustering. Reviews are nested in styles. Treating them as independent
    observations understates the standard error.
2.  Cluster-size skew. Review counts are heavily right-skewed - a handful of
    products carry a large share of the reviews. Unequal cluster sizes inflate
    the design effect beyond the equal-size Kish factor, and the inflation is
    driven by the *coefficient of variation* of cluster sizes, not the mean.
3.  Differential non-response. Only observations where the fit question was
    answered enter the estimator, and the answer rate varies by cell.

Everything here is expressed in standard-deviation units of fit_score, so no
assumption about the scale's variance is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist


def z(p: float) -> float:
    return NormalDist().inv_cdf(p)


def design_effect(mean_cluster_size: float, icc: float, cv: float = 0.0) -> float:
    """Design effect for clustered sampling with unequal cluster sizes.

    Uses the Eldridge/Kerry form

        DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC

    which reduces to the familiar Kish factor 1 + (m_bar - 1) * ICC when all
    clusters are the same size (CV = 0). The CV term is what makes the review
    skew of section 5.9 expensive: doubling the CV roughly quadruples its
    contribution.
    """
    if mean_cluster_size <= 0:
        raise ValueError("mean cluster size must be positive")
    effective = (cv**2 + 1.0) * mean_cluster_size - 1.0
    return 1.0 + effective * icc


@dataclass(frozen=True)
class Cell:
    """One gender x body-half cell of the 2x2 design."""

    name: str
    n_reviews: int  # raw reviews in the cell
    response_rate: float  # share answering the fit question (section 5.4)

    def usable(self) -> float:
        return self.n_reviews * self.response_rate

    def effective_n(self, mean_cluster_size: float, icc: float, cv: float) -> float:
        deff = design_effect(mean_cluster_size, icc, cv)
        return self.usable() / deff


def mde(
    cells: tuple[Cell, Cell, Cell, Cell],
    *,
    mean_cluster_size: float,
    icc: float,
    cv: float = 0.0,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Minimum detectable effect on tau, in standard deviations of fit_score.

    The DiD contrast is a sum of four independent cell means, so its variance is
    the sum of the four cell-mean variances. With sigma normalised to 1,

        Var(tau) = sum_k  1 / n_eff_k
        MDE      = (z_{1-alpha/2} + z_{power}) * sqrt(Var(tau))

    Note this is conservative in one respect: style fixed effects absorb
    between-style variation, which removes part of what the ICC is charging for.
    It is anti-conservative in another: it assumes the four cells are
    independent, and a style contributes to only one cell, which holds here.
    """
    variance = sum(
        1.0 / c.effective_n(mean_cluster_size, icc, cv) for c in cells
    )
    return (z(1 - alpha / 2) + z(power)) * variance**0.5


def required_n_per_cell(
    target_mde: float,
    *,
    mean_cluster_size: float,
    icc: float,
    cv: float = 0.0,
    response_rate: float = 0.55,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Raw reviews needed *per cell*, assuming four equal cells, to reach an MDE."""
    multiplier = z(1 - alpha / 2) + z(power)
    deff = design_effect(mean_cluster_size, icc, cv)
    # MDE = mult * sqrt(4 * deff / usable_per_cell)  ->  solve for usable
    usable_per_cell = 4.0 * deff * (multiplier / target_mde) ** 2
    return usable_per_cell / response_rate
