"""MDE at each candidate analysis window.

Uses `power.py` unchanged -- the module recovered from the Phase 0 tree, which
produced the published table in `docs/phase0-collection-blocker-and-power.md`
§3. Reusing it rather than reimplementing it is deliberate: the two sets of
figures have to be comparable, and a second implementation of the same formula
is a place for them to silently diverge.

Cell counts come from `time_window_probe.py` (docs/phase1c-time-window.md).
They are ALREADY usable observations -- labelled reviews joined to an in-scope
style -- so `response_rate` is 1.0 here. In Phase 0 the response rate did the
work of converting raw Mavi reviews into answered ones; on Amazon the fit label
is derived from text, so the dictionary's recall is what has already been applied
and it is baked into the counts.

Usage:
    python src/analysis/run_window_power.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from src.analysis.power import Cell, design_effect, mde  # noqa: E402

# Measured 2026-08-11, 600,000-review block sample against a 250,000-record
# style index. NOT corpus totals -- see the note at the foot of the report.
WINDOWS: dict[str, dict[str, int]] = {
    "18 months (2022+)": {"men_upper": 23, "men_lower": 12,
                          "women_upper": 141, "women_lower": 50},
    "3 years (2021+)": {"men_upper": 214, "men_lower": 151,
                        "women_upper": 1045, "women_lower": 446},
    "5 years (2019+)": {"men_upper": 405, "men_lower": 307,
                        "women_upper": 1721, "women_lower": 798},
    "8 years (2016+)": {"men_upper": 514, "men_lower": 394,
                        "women_upper": 1876, "women_lower": 960},
    "full history": {"men_upper": 535, "men_lower": 431,
                     "women_upper": 1893, "women_lower": 981},
}

# Phase 0 swept these rather than guessing, and they are still unmeasured on
# Amazon, so they are still swept. m_bar is the Phase 0 Mavi figure; Amazon's
# reviews-per-style is not yet measured, which is stated as a caveat.
M_BAR = 20.0
SCENARIOS = [
    ("no clustering", 0.0, 0.0),
    ("ICC 0.02, CV 1", 0.02, 1.0),
    ("ICC 0.05, CV 1", 0.05, 1.0),
    ("ICC 0.05, CV 2", 0.05, 2.0),
    ("ICC 0.10, CV 2", 0.10, 2.0),
]


def cells_of(counts: dict[str, int]) -> tuple[Cell, ...]:
    return tuple(Cell(name=k, n_reviews=v, response_rate=1.0)
                 for k, v in counts.items())


def variance_share(counts: dict[str, int]) -> dict[str, float]:
    total = sum(1.0 / n for n in counts.values())
    return {k: (1.0 / n) / total for k, n in counts.items()}


def main() -> int:
    line = "=" * 78
    print(line)
    print("MDE BY ANALYSIS WINDOW -- SD units of fit_score")
    print(line)
    print(f"method: src/analysis/power.py (Phase 0 module, unchanged), m_bar={M_BAR:.0f}")
    print("counts are usable observations, so response_rate = 1.0\n")

    header = "".join(f"{name:>16}" for name, _, _ in SCENARIOS)
    print(f"{'window':<20}{'min cell':>10}{header}")
    for window, counts in WINDOWS.items():
        cells = cells_of(counts)
        row = f"{window:<20}{min(counts.values()):>10,}"
        for _name, icc, cv in SCENARIOS:
            value = mde(cells, mean_cluster_size=M_BAR, icc=icc, cv=cv)
            row += f"{value:>16.3f}"
        print(row)

    print("\n" + line)
    print("DESIGN EFFECTS APPLIED")
    print(line)
    for name, icc, cv in SCENARIOS:
        print(f"  {name:<18} DEFF = {design_effect(M_BAR, icc, cv):.2f}")

    print("\n" + line)
    print("WHERE Var(tau) LIVES -- 5 years (2019+)")
    print(line)
    counts = WINDOWS["5 years (2019+)"]
    for cell, share in sorted(variance_share(counts).items(), key=lambda kv: -kv[1]):
        print(f"  {cell:<16}{share:>7.1%}")
    mens = sum(v for k, v in variance_share(counts).items() if k.startswith("men"))
    print(f"\n  the two men's cells carry {mens:.0%} of the variance between them")
    print("  -- the estimand's precision is set by the smaller pair, which is")
    print("  DESIGN.md 5.5 in arithmetic rather than in prose")

    print("\n" + line)
    print("WHAT WOULD MOVE IT -- 5 years, ICC 0.05 / CV 1")
    print(line)
    current = mde(cells_of(counts), mean_cluster_size=M_BAR, icc=0.05, cv=1.0)
    print(f"  current                       {current:.3f} SD")
    for target in (0.30, 0.25, 0.20, 0.15):
        print(f"  to reach {target:.2f} SD             x{(current / target) ** 2:>6.2f} on every cell")
    full = WINDOWS["full history"]["men_lower"] / counts["men_lower"]
    print(f"\n  widening to full history gives only x{full:.2f} on the anchor cell,")
    print("  and readmits the regime drift the window exists to exclude.")
    print("  Dictionary recall scales every cell directly and is the larger lever.")

    print("\n" + line)
    print("CAVEATS")
    print(line)
    print("  - Counts are from a 600,000-review sample against a 250,000-item index,")
    print("    not corpus totals. A full-index pass yields more, so these are the")
    print("    pessimistic end. The RATIOS between windows do not depend on that.")
    print("  - m_bar = 20 is the Phase 0 Mavi figure. Amazon reviews-per-style is")
    print("    not yet measured; it enters DEFF linearly, so this is the weakest")
    print("    assumption in the table.")
    print("  - ICC and CV are swept, not measured, exactly as in Phase 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
