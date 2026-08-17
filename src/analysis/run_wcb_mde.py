"""Effective MDE under wild cluster bootstrap, on the measured cluster structure.

The claim under test is narrow and specific. `MDE_design = 0.568` for the
keep-listings scenario comes from

    DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC

which is a statement about a size *distribution*. It has no term for "one cluster
holds a fifth of the observations", and that is exactly the configuration here:
2,893 of 15,072 labelled observations sit in one `parent_asin`. So the sentence
"keeping them would require lambda >= 1.89, which is impossible" rests on the
least trustworthy calculation in the project, and it is the most consequential
sentence in the gate.

**What this computes.** A deliberately stylised two-group contrast carrying the
MEASURED cluster-size distribution, with the dominant cluster in the treated
group. For that same design it computes (a) the formula MDE and (b) the MDE at
which wild cluster bootstrap reaches 80% power. The ratio between them is the
formula's error factor in this configuration, and it is the transportable
quantity -- not the stylised MDE itself.

**Why stylised rather than the full design.** The full estimand is a gradient
trend differenced across genders, and per-cell cluster-size distributions were
not retained. A two-group contrast isolates the question actually at issue --
does the DEFF formula describe the estimator when one cluster dominates -- without
pretending to reproduce the whole design. The distortion factor is then applied
to the reported figures.

Usage:
    python src/analysis/run_wcb_mde.py <clusters.json> [--trials 60]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from src.analysis.power import design_effect, z  # noqa: E402
from src.analysis.wild_bootstrap import wcb_pvalue  # noqa: E402

SHARES = {"ran_small": 0.30, "true_to_size": 0.53, "ran_large": 0.17}
Z_SUM = z(0.975) + z(0.80)


def split_groups(sizes: list[int]) -> tuple[list[int], list[int]]:
    """Treated group takes the dominant cluster plus enough others to reach ~half."""
    ordered = sorted(sizes, reverse=True)
    total = sum(ordered)
    treated = [ordered[0]]
    running = ordered[0]
    rest = []
    for size in ordered[1:]:
        if running < total / 2:
            treated.append(size)
            running += size
        else:
            rest.append(size)
    return treated, rest


def formula_mde(treated: list[int], control: list[int], icc: float) -> float:
    """Two-group difference in means, DEFF applied to each group."""
    out = []
    for sizes in (treated, control):
        mean = sum(sizes) / len(sizes)
        sd = statistics.pstdev(sizes) if len(sizes) > 1 else 0.0
        cv = sd / mean if mean else 0.0
        deff = design_effect(mean, icc, cv)
        out.append(deff / sum(sizes))
    return Z_SUM * (out[0] + out[1]) ** 0.5


def build(treated: list[int], control: list[int], effect: float, icc: float,
          rng: random.Random):
    scores = (-1.0, 0.0, 1.0)
    weights = (SHARES["ran_small"], SHARES["true_to_size"], SHARES["ran_large"])
    sd_cluster = icc ** 0.5
    y: list[float] = []
    x: list[float] = []
    groups: list[int] = []
    gid = 0
    for sizes, shift, flag in ((treated, effect, 1.0), (control, 0.0, 0.0)):
        for size in sizes:
            bump = rng.gauss(0.0, sd_cluster)
            for _ in range(size):
                y.append(rng.choices(scores, weights=weights, k=1)[0] + bump + shift)
                x.append(flag)
                groups.append(gid)
            gid += 1
    return y, x, groups


def power_at(effect: float, treated, control, icc, trials, replicates, seed):
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        y, x, g = build(treated, control, effect, icc, rng)
        if wcb_pvalue(y, x, g, replicates, rng) < 0.05:
            hits += 1
    return hits / trials


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("clusters")
    parser.add_argument("--scenario", default="KEEP")
    parser.add_argument("--icc", type=float, default=0.05)
    parser.add_argument("--trials", type=int, default=60)
    parser.add_argument("--replicates", type=int, default=199)
    parser.add_argument("--grid", default="0.05,0.10,0.15,0.20,0.30,0.45,0.60")
    args = parser.parse_args()

    data = json.loads(pathlib.Path(args.clusters).read_text(encoding="utf-8"))
    sizes = data[args.scenario]
    treated, control = split_groups(sizes)

    print("=" * 78)
    print(f"WILD CLUSTER BOOTSTRAP MDE -- scenario {args.scenario}")
    print("=" * 78)
    print(f"clusters {len(sizes):,}   observations {sum(sizes):,}")
    print(f"dominant cluster {max(sizes):,} = {max(sizes) / sum(sizes):.1%}")
    print(f"treated  {len(treated):,} clusters, {sum(treated):,} obs "
          f"(dominant one included)")
    print(f"control  {len(control):,} clusters, {sum(control):,} obs")

    f_mde = formula_mde(treated, control, args.icc)
    print(f"\nformula MDE for THIS two-group design: {f_mde:.4f} SD")
    print(f"(ICC {args.icc}; the same formula that yields the headline figures)")

    print(f"\nWCB power curve -- {args.trials} trials x {args.replicates} replicates")
    print(f"{'effect':>8}{'power':>8}   Monte Carlo SE ~"
          f"{(0.25 / args.trials) ** 0.5:.3f}")
    wcb_mde = None
    for effect in [float(v) for v in args.grid.split(",")]:
        p = power_at(effect, treated, control, args.icc, args.trials,
                     args.replicates, 20260815)
        flag = ""
        if wcb_mde is None and p >= 0.80:
            wcb_mde = effect
            flag = "  <- 80% power reached"
        print(f"{effect:>8.2f}{p:>8.2f}{flag}", flush=True)

    print()
    if wcb_mde is None:
        top = float(args.grid.split(",")[-1])
        print(f"80% power not reached on this grid: WCB MDE > {top:.2f} SD.")
        if top >= f_mde:
            print(f"Since the grid already exceeds the formula MDE ({f_mde:.4f}), the")
            print(f"formula UNDERSTATES the needed effect by at least "
                  f"{top / f_mde:.2f}x.")
        else:
            print(f"The grid top ({top:.2f}) is BELOW the formula MDE ({f_mde:.4f}),")
            print("so this run bounds nothing. Re-run with a grid spanning it.")
    else:
        print(f"WCB MDE  {wcb_mde:.3f} SD   vs   formula MDE  {f_mde:.4f} SD")
        print(f"DISTORTION FACTOR  {wcb_mde / f_mde:.2f}x")
        print("\nThe factor is the transportable quantity. Applied to the reported")
        print("keep-scenario figures it says how much the formula understates the")
        print("effect size actually needed.")
    print("\nCaveats: ICC imposed, not measured. Grid is coarse, so the MDE is the")
    print("smallest GRID point reaching 80%, an upper bound on the true crossing.")
    print("Monte Carlo error at these trial counts is not negligible.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
