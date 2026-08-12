"""Sweep the MDE across the parameters Phase 0 could not pin down.

Run:  python -m src.analysis.run_power_scenarios
"""

from __future__ import annotations

from src.analysis.power import Cell, design_effect, mde, required_n_per_cell

# --------------------------------------------------------------------------
# Inputs, all traceable to Phase 0
# --------------------------------------------------------------------------

# Estimated usable observations from section 5.16: ~2,420 target products
# x 12.7 reviews x 55% response = ~17,000. The *raw* review pool is ~30,700.
TOTAL_RAW_REVIEWS = 30_700

# Response rates measured in Phase 0 (section 5.4), collapsed to gender x
# body-half. Men: shirt 20%, tee 44% -> upper ~= 0.37 weighted by the observed
# 15/54 split. Men/lower was never observed; assume it matches men/upper, which
# is the optimistic assumption.
RESPONSE = {
    "men-upper": 0.37,
    "men-lower": 0.37,
    "women-upper": 0.67,  # tee 67%, shirt 70%
    "women-lower": 0.61,  # jean 61%
}

# Gender x body-half share of the RAW review pool. Phase 0's 254-review sample
# was 69 men / 185 women = 27% men, and contained zero men's jean reviews.
# Upper:lower within women was 105:80.
SCENARIOS = {
    "even split (section 5.16's implicit assumption)": {
        "men-upper": 0.25, "men-lower": 0.25,
        "women-upper": 0.25, "women-lower": 0.25,
    },
    "Phase 0 proportions (27% men)": {
        "men-upper": 0.155, "men-lower": 0.115,
        "women-upper": 0.415, "women-lower": 0.315,
    },
    "thin men's jean cell (men/lower = 5%)": {
        "men-upper": 0.27, "men-lower": 0.05,
        "women-upper": 0.40, "women-lower": 0.28,
    },
}

# Reviews per style. 5,629 variants / 3,582 styles = 1.57 variants per style,
# x 12.7 reviews per variant = ~20 raw reviews per style.
MEAN_CLUSTER = 20.0

ICC_GRID = (0.02, 0.05, 0.10)
CV_GRID = (0.0, 1.0, 2.0)  # 0 = equal sizes; 2.0 = heavy skew (section 5.9)


def build_cells(shares: dict[str, float]) -> tuple[Cell, ...]:
    return tuple(
        Cell(name=k, n_reviews=int(TOTAL_RAW_REVIEWS * shares[k]), response_rate=RESPONSE[k])
        for k in ("men-upper", "men-lower", "women-upper", "women-lower")
    )


def main() -> None:
    print("=" * 78)
    print("MDE on tau, in SD units of fit_score. alpha=0.05, power=0.80.")
    print(f"Raw review pool: {TOTAL_RAW_REVIEWS:,}   mean reviews/style: {MEAN_CLUSTER:.0f}")
    print("=" * 78)

    print("\nDesign effect at mean cluster size 20:")
    print(f"  {'ICC':>6} | " + " | ".join(f"CV={cv:<4.1f}" for cv in CV_GRID))
    for icc in ICC_GRID:
        row = " | ".join(f"{design_effect(MEAN_CLUSTER, icc, cv):7.2f}" for cv in CV_GRID)
        print(f"  {icc:>6.2f} | {row}")

    for label, shares in SCENARIOS.items():
        cells = build_cells(shares)
        print(f"\n--- {label} ---")
        usable = {c.name: c.usable() for c in cells}
        for name, u in usable.items():
            print(f"    {name:<14s} raw={int(TOTAL_RAW_REVIEWS*shares[name]):>6,}  usable={u:>8,.0f}")
        print(f"    {'TOTAL':<14s} {'':>10}  usable={sum(usable.values()):>8,.0f}")

        print(f"\n    {'ICC':>6} | " + " | ".join(f"CV={cv:<4.1f}" for cv in CV_GRID))
        for icc in ICC_GRID:
            row = " | ".join(
                f"{mde(cells, mean_cluster_size=MEAN_CLUSTER, icc=icc, cv=cv):7.3f}"
                for cv in CV_GRID
            )
            print(f"    {icc:>6.2f} | {row}")

    print("\n" + "=" * 78)
    print("Raw reviews needed PER CELL for a given MDE (4 equal cells, 55% response)")
    print("=" * 78)
    print(f"  {'target MDE':>10} | " + " | ".join(f"ICC={i:<5.2f}" for i in ICC_GRID))
    for target in (0.10, 0.15, 0.20, 0.30):
        row = " | ".join(
            f"{required_n_per_cell(target, mean_cluster_size=MEAN_CLUSTER, icc=i, cv=2.0):9,.0f}"
            for i in ICC_GRID
        )
        print(f"  {target:>10.2f} | {row}")
    print("\n  (at CV=2.0, i.e. the heavy review-count skew of section 5.9)")


if __name__ == "__main__":
    main()
