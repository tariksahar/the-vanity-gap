"""Does asymptotic cluster-robust inference hold its nominal size here?

Coverage is a different question from whether the MDE formula is calibrated, and
in this project the two have different answers. `run_wcb_mde.py` found the
formula calibrated (1.01x). This script finds the asymptotic test badly
mis-sized -- 20.7% rejection of true nulls at a nominal 5% under the dominant
cluster structure.

**The asymptotic test needs no bootstrap**, so it is run at many more trials than
WCB for the same compute. That matters: at 200 trials neither the EXCLUDE nor the
SPLIT structure could be distinguished from nominal, and SPLIT looked worse than
EXCLUDE when it is better. At 2,000 trials all three intervals exclude nominal.
The trial count is therefore reported alongside every rate, and every rate gets a
Wilson interval so a claimed ratio can be checked rather than taken.

Usage:
    python src/analysis/run_coverage_check.py <clusters.json> [--asym 2000] [--wcb 300]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from src.analysis.run_wcb_mde import build, split_groups  # noqa: E402
from src.analysis.score_precision import wilson  # noqa: E402
from src.analysis.wild_bootstrap import _t_stat, wcb_pvalue  # noqa: E402

NOMINAL = 0.05
CRITICAL = 1.959963985


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("clusters")
    parser.add_argument("--asym", type=int, default=2000)
    parser.add_argument("--wcb", type=int, default=300)
    parser.add_argument("--reps", type=int, default=99)
    parser.add_argument("--icc", type=float, default=0.05)
    args = parser.parse_args()

    data = json.loads(pathlib.Path(args.clusters).read_text(encoding="utf-8"))

    print(f"nominal size {NOMINAL}   asymptotic trials {args.asym}   "
          f"WCB trials {args.wcb} x {args.reps} reps\n")
    print(f"{'scenario':<9}{'dom':>7}   {'asymptotic CR':<26}{'ratio':<20}{'WCB'}")

    for scenario in ("KEEP", "EXCLUDE", "SPLIT"):
        sizes = data.get(scenario)
        if not sizes:
            continue
        treated, control = split_groups(sizes)
        dominance = max(sizes) / sum(sizes)

        rng = random.Random(20260815)
        asym = 0
        for _ in range(args.asym):
            y, x, groups = build(treated, control, 0.0, args.icc, rng)
            _beta, t = _t_stat(y, x, groups)
            if abs(t) > CRITICAL:
                asym += 1
        a_lo, a_hi = wilson(asym, args.asym)

        rng = random.Random(20260816)
        wcb = 0
        for _ in range(args.wcb):
            y, x, groups = build(treated, control, 0.0, args.icc, rng)
            if wcb_pvalue(y, x, groups, args.reps, rng) < NOMINAL:
                wcb += 1
        w_lo, w_hi = wilson(wcb, args.wcb)

        rate = asym / args.asym
        print(f"{scenario:<9}{dominance:>6.1%}   "
              + f"{rate:.3f} [{a_lo:.3f}, {a_hi:.3f}]".ljust(26)
              + f"{rate / NOMINAL:.1f}x [{a_lo / NOMINAL:.1f}, {a_hi / NOMINAL:.1f}]".ljust(20)
              + f"{wcb / args.wcb:.3f} [{w_lo:.3f}, {w_hi:.3f}]", flush=True)

    print("\nWilson intervals at 95%. A rate whose interval excludes 0.050 is")
    print("mis-sized. One whose interval contains it is not ESTABLISHED as")
    print("mis-sized at this trial count, whatever the point estimate suggests.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
