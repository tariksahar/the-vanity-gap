"""The three measurements A5 is waiting on, in one pass.

PREREGISTRATION.md 11 A5 is deferred pending measurement, not pending judgement.
This probe supplies all three inputs.

**MEASUREMENT 0 -- do the existing filters already dissolve the problem?**
Cheapest question first. The DESIGN.md 5.8 window, the `verified_purchase`
decision and the 1.3 mapping are already in the design. If a structurally-failing
listing loses most of its observations to filters we already apply, there is
nothing left to decide.

**MEASUREMENT 1 -- is a mega-listing ONE calibration unit?**
Parent-level clustering assumes it is. Three sub-questions, and only one of them
is answerable on this corpus:

  - single store?  TRIVIALLY YES BY CONSTRUCTION. `store` is a field on the
    parent's metadata row, so every asin under a parent shares it. The only way
    this could fail is an asin appearing under two parents, which is checked.
  - one size grid?  **NOT MEASURABLE.** Reviews carry no size field (they carry
    asin, parent_asin, rating, text, title, timestamp, user_id, verified_purchase
    and nothing else) and metadata is parent-level. The only size signal is
    self-reported text at 0.20% prevalence -- far too sparse per asin.
  - homogeneous fit across asins?  **MEASURABLE, and it is the real test.**
    Different designs under one parent should show different fit distributions if
    they are different products.

**MEASUREMENT 4 -- separate DEFF and MDE for the three objects.**
`Delta_men`, `Delta_women` and `tau`, under each of the three A5 scenarios.
The within-men object is the THREE-CATEGORY GRADIENT, not the two-level
difference: a common cut shift need not be monotone in the same order, so the
gradient is more informative about whether a men's pattern is vanity rather than
convention.

Scenarios:
  KEEP     cluster = parent, every listing
  EXCLUDE  cluster = parent, structurally-failing listings dropped
  SPLIT    cluster = asin for failing listings, parent otherwise

Usage:
    python a5_probe.py [--reviews 3000000] [--items 400000]
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import math
import statistics
import sys

import amazon_fit_probe
from amazon_fit_probe import (
    FIT_DICTIONARY, ROOT_SEGMENTS, WS_RX, _review_year, classify_gender,
    classify_gradient, classify_half, iter_records, label_fit, pct, rule,
)

sys.path.insert(0, ".")
from src.analysis.power import Cell, design_effect, mde  # noqa: E402
from src.analysis.power_trend import _scatter, mde_trend  # noqa: E402

GRADIENT_HALF = {"tshirt": "upper", "shirt": "upper", "jeans_trousers": "lower"}
ASIN_THRESHOLDS = (300, 500, 1000, 2000)
Z_SUM = 2.8015805601


def build_index(category: str, limit: int):
    index = {}
    stats = collections.Counter()
    for record in iter_records(f"raw_meta_{category}", category, limit):
        stats["seen"] += 1
        cats = record.get("categories") or []
        if isinstance(cats, str):
            cats = [cats]
        segments = [WS_RX.sub(" ", str(c)).strip().lower() for c in cats if c]
        if not segments:
            continue
        gender = classify_gender(" | ".join(segments))
        if gender not in ("men", "women"):
            continue
        garment = [s for s in segments if s not in ROOT_SEGMENTS]
        half = classify_half(garment)
        if half not in ("upper", "lower"):
            continue
        parent = record.get("parent_asin")
        if not parent:
            continue
        stats["in_scope"] += 1
        index[parent] = (gender, half, classify_gradient(garment),
                         WS_RX.sub(" ", str(record.get("title") or "")).strip(),
                         (record.get("store") or "").strip() or "(unnamed)")
    return index, stats


def probe(category: str, review_limit: int, item_limit: int, window_from: int):
    index, meta_stats = build_index(category, item_limit)

    asins = collections.defaultdict(set)                  # parent -> {asin}
    asin_parents = collections.defaultdict(set)           # asin -> {parent}
    survive = collections.defaultdict(collections.Counter)  # parent -> stage counts
    labelled_parent = collections.Counter()               # parent -> labelled (all filters)
    labelled_asin = collections.Counter()                 # (parent, asin) -> labelled
    asin_fit = collections.defaultdict(collections.Counter)  # (parent, asin) -> bucket
    cell_counts = collections.Counter()                   # (gender, half, bucket)
    grad_counts = collections.Counter()                   # (gender, gradient, bucket)
    grad_parent = collections.Counter()                   # (parent, gender, gradient)
    grad_asin = collections.Counter()                     # (parent, asin, gender, gradient)
    stats = collections.Counter()

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        stats["scanned"] += 1
        parent = record.get("parent_asin")
        entry = index.get(parent) if parent else None
        if entry is None:
            continue
        gender, half, gradient, _title, _store = entry
        asin = record.get("asin")
        if asin:
            asins[parent].add(asin)
            asin_parents[asin].add(parent)

        stage = survive[parent]
        stage["in_scope"] += 1                            # passed 1.3 already
        year = _review_year(record)
        in_window = year is not None and year >= window_from
        verified = bool(record.get("verified_purchase"))
        if in_window:
            stage["window"] += 1
        if verified:
            stage["verified"] += 1
        if in_window and verified:
            stage["window_verified"] += 1

        bucket, _ = label_fit(record.get("title", ""), record.get("text", ""))
        if bucket not in FIT_DICTIONARY:
            continue
        stage["labelled_any"] += 1
        if in_window:
            stage["labelled_window"] += 1
        if not (in_window and verified):
            continue
        stage["labelled_final"] += 1
        stats["labelled_final"] += 1

        labelled_parent[parent] += 1
        if asin:
            labelled_asin[(parent, asin)] += 1
            asin_fit[(parent, asin)][bucket] += 1
        cell_counts[(gender, half, bucket)] += 1
        if gradient:
            grad_counts[(gender, gradient, bucket)] += 1
            grad_parent[(parent, gender, gradient)] += 1
            if asin:
                grad_asin[(parent, asin, gender, gradient)] += 1

    return {"index": index, "meta_stats": meta_stats, "stats": stats,
            "asins": asins, "asin_parents": asin_parents, "survive": survive,
            "labelled_parent": labelled_parent, "labelled_asin": labelled_asin,
            "asin_fit": asin_fit, "cell_counts": cell_counts,
            "grad_counts": grad_counts, "grad_parent": grad_parent,
            "grad_asin": grad_asin}


# ---------------------------------------------------------------------------


def cluster_params(sizes: list[int]) -> tuple[float, float]:
    """(m_bar, CV) of a cluster-size distribution."""
    if not sizes:
        return (0.0, 0.0)
    mean = sum(sizes) / len(sizes)
    if mean <= 0:
        return (0.0, 0.0)
    sd = statistics.pstdev(sizes) if len(sizes) > 1 else 0.0
    return (mean, sd / mean)


def failing_parents(res: dict, threshold: int) -> set[str]:
    return {p for p, a in res["asins"].items() if len(a) > threshold}


def report_measurement_0(res: dict, threshold: int) -> None:
    rule("MEASUREMENT 0 -- do the filters we already apply dissolve the problem?")
    failing = failing_parents(res, threshold)
    print(f"structurally-failing listings at >{threshold} asins: {len(failing)}\n")
    print(f"{'parent':<13}{'in scope':>10}{'window':>9}{'verified':>10}"
          f"{'win+ver':>9}{'labelled':>10}{'survival':>10}  store")
    total_final = sum(res["labelled_parent"].values())
    for parent in sorted(failing, key=lambda p: -res["labelled_parent"][p])[:10]:
        s = res["survive"][parent]
        store = res["index"][parent][4]
        surv = (s["labelled_final"] / s["labelled_any"]) if s["labelled_any"] else 0
        print(f"{parent:<13}{s['in_scope']:>10,}{s['window']:>9,}{s['verified']:>10,}"
              f"{s['window_verified']:>9,}{s['labelled_final']:>10,}"
              f"{surv:>9.1%}  {store[:24]}")

    fail_final = sum(res["labelled_parent"][p] for p in failing)
    fail_any = sum(res["survive"][p]["labelled_any"] for p in failing)
    all_any = sum(v["labelled_any"] for v in res["survive"].values())
    print(f"\nfailing listings, labelled BEFORE window+verified: {fail_any:,}"
          f"  ({pct(fail_any, all_any)} of all)")
    print(f"failing listings, labelled AFTER  window+verified: {fail_final:,}"
          f"  ({pct(fail_final, total_final)} of all)")
    print(f"\n=> the existing filters remove {pct(fail_any - fail_final, fail_any)}"
          " of the failing listings' observations")
    if total_final and fail_final / total_final < 0.05:
        print("=> AND leave them under 5% of the analysis sample: PROBLEM DISSOLVES")
    else:
        print("=> and leave them ABOVE 5% of the analysis sample: problem persists")


def report_measurement_1(res: dict, threshold: int, min_reviews: int) -> None:
    rule("MEASUREMENT 1 -- is a mega-listing one calibration unit?")
    multi = {a: p for a, p in res["asin_parents"].items() if len(p) > 1}
    print(f"asins appearing under more than one parent: {len(multi)}")
    print("=> single-store claim holds by construction (store is a parent field)\n")
    print("size grid per asin: NOT MEASURABLE. Reviews carry no size field and")
    print("metadata is parent-level. Recorded as a limitation, not an answer.\n")

    failing = sorted(failing_parents(res, threshold),
                     key=lambda p: -res["labelled_parent"][p])[:4]
    print("FIT HOMOGENEITY ACROSS ASINS -- the answerable test\n")
    for parent in failing:
        title = res["index"][parent][3]
        n_asins = len(res["asins"][parent])
        counts = [res["labelled_asin"][(parent, a)] for a in res["asins"][parent]]
        counts = [c for c in counts if c]
        rich = [(a, res["asin_fit"][(parent, a)]) for a in res["asins"][parent]
                if res["labelled_asin"][(parent, a)] >= min_reviews]
        print(f"  [{parent}] {title[:60]}")
        print(f"    asins {n_asins:,}   asins with >=1 labelled {len(counts):,}"
              f"   with >={min_reviews} labelled {len(rich):,}")
        if len(rich) < 3:
            print(f"    CANNOT TEST: fewer than 3 asins reach {min_reviews} labelled"
                  " reviews.")
            print("    Each design carries about one observation, so within-parent")
            print("    homogeneity is unmeasurable -- and a cluster whose members")
            print("    cannot be compared is an assumption, not a finding.")
            continue
        shares = []
        for _a, fit in rich:
            total = sum(fit.values())
            shares.append(fit["ran_small"] / total)
        print(f"    ran_small share across those asins: "
              f"min {min(shares):.2f} median {statistics.median(shares):.2f} "
              f"max {max(shares):.2f}")
        if len(shares) > 1:
            print(f"    spread {max(shares) - min(shares):.2f} -- "
                  f"{'HETEROGENEOUS' if max(shares) - min(shares) > 0.3 else 'consistent'}")


def _mde_for(cells: dict, m_bar: float, cv: float, icc: float = 0.05) -> float:
    tup = tuple(Cell(k, v, 1.0) for k, v in cells.items())
    if len(tup) != 4 or any(v <= 0 for v in cells.values()):
        return float("nan")
    return mde(tup, mean_cluster_size=m_bar, icc=icc, cv=cv)


def report_measurement_4(res: dict, threshold: int) -> None:
    rule("MEASUREMENT 4 -- separate DEFF and MDE for the three objects")
    print("Within-men object is the THREE-CATEGORY GRADIENT (trend), not the")
    print("two-level difference. Delta_men is NOT separately identified -- see")
    print("PREREGISTRATION.md 9.8 -- so this says which arm binds, nothing more.\n")

    failing = failing_parents(res, threshold)
    grad = res["grad_counts"]

    for scenario in ("KEEP", "EXCLUDE", "SPLIT"):
        print(f"\n--- {scenario} " + "-" * 60)
        if scenario == "KEEP":
            sizes = list(res["labelled_parent"].values())
            drop = set()
        elif scenario == "EXCLUDE":
            sizes = [n for p, n in res["labelled_parent"].items() if p not in failing]
            drop = failing
        else:
            sizes = [n for p, n in res["labelled_parent"].items() if p not in failing]
            sizes += [n for (p, _a), n in res["labelled_asin"].items() if p in failing]
            drop = set()

        m_bar, cv = cluster_params(sizes)
        deff = design_effect(m_bar, 0.05, cv) if m_bar > 0 else float("nan")
        print(f"clusters {len(sizes):,}   m_bar {m_bar:.3f}   CV {cv:.3f}"
              f"   DEFF {deff:.2f}")

        counts = {}
        for gender in ("men", "women"):
            for gradient in ("tshirt", "shirt", "jeans_trousers"):
                total = sum(grad[(gender, gradient, b)] for b in FIT_DICTIONARY)
                if drop:
                    lost = sum(n for (p, g, gr), n in res["grad_parent"].items()
                               if p in drop and g == gender and gr == gradient)
                    total -= lost
                counts[(gender, gradient)] = total
        men = {g: counts[("men", g)] for g in ("tshirt", "shirt", "jeans_trousers")}
        women = {g: counts[("women", g)] for g in ("tshirt", "shirt", "jeans_trousers")}
        print(f"  men   tee {men['tshirt']:>6,}  shirt {men['shirt']:>6,}"
              f"  jeans {men['jeans_trousers']:>6,}")
        print(f"  women tee {women['tshirt']:>6,}  shirt {women['shirt']:>6,}"
              f"  jeans {women['jeans_trousers']:>6,}")

        try:
            tau_trend = mde_trend(men, women, mean_cluster_size=m_bar,
                                  icc=0.05, cv=cv, per_step=True)
            print(f"  MDE tau      (gradient trend, per step) {tau_trend:>8.3f} SD")
        except ValueError as exc:
            print(f"  MDE tau: {exc}")
        # Within-gender trend. Var(beta_g) = DEFF / S_g with S_g the
        # position-weighted scatter, so `_scatter` is reused rather than
        # rewritten -- an earlier hand-rolled version mapped tshirt to position
        # 0 in the mean and to position 2 in the deviation, which is wrong in a
        # way that would not have shown up as an error.
        for label, one in (("Delta_men", men), ("Delta_women", women)):
            scatter = _scatter(one)
            if scatter <= 0 or m_bar <= 0:
                print(f"  MDE {label}: undefined (no spread across the ordering)")
                continue
            var = design_effect(m_bar, 0.05, cv) / scatter
            print(f"  MDE {label:<12}(within-gender trend, per step) "
                  f"{(Z_SUM) * var ** 0.5:>8.3f} SD")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=3_000_000)
    parser.add_argument("--items", type=int, default=400_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--spread", type=int, default=24)
    parser.add_argument("--window-from", type=int, default=2019)
    parser.add_argument("--asin-threshold", type=int, default=1000)
    parser.add_argument("--min-asin-reviews", type=int, default=5)
    parser.add_argument("--dump-clusters", default="",
                        help="write cluster-size distributions per scenario as JSON, "
                             "so the wild bootstrap runs on the measured structure "
                             "rather than a distribution matched to its moments")
    args = parser.parse_args()

    amazon_fit_probe.SPREAD_BLOCKS = args.spread
    rule(f"A5 PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}  meta {args.items:,}  window {args.window_from}+"
          f"  asin threshold >{args.asin_threshold}")
    res = probe(args.category, args.reviews, args.items, args.window_from)

    rule("STRUCTURAL THRESHOLD SENSITIVITY")
    print("The criterion is 'more asins than a size grid can generate'. The")
    print("threshold is shown at several values rather than asserted once.\n")
    print(f"{'>asins':>8}{'listings':>10}{'labelled':>10}{'share':>8}")
    total = sum(res["labelled_parent"].values())
    for t in ASIN_THRESHOLDS:
        f = failing_parents(res, t)
        n = sum(res["labelled_parent"][p] for p in f)
        print(f"{t:>8}{len(f):>10,}{n:>10,}{pct(n, total):>8}")

    report_measurement_0(res, args.asin_threshold)
    report_measurement_1(res, args.asin_threshold, args.min_asin_reviews)
    report_measurement_4(res, args.asin_threshold)

    if args.dump_clusters:
        import json
        failing = failing_parents(res, args.asin_threshold)
        keep = list(res["labelled_parent"].values())
        exclude = [n for p, n in res["labelled_parent"].items() if p not in failing]
        split = [n for p, n in res["labelled_parent"].items() if p not in failing]
        split += [n for (p, _a), n in res["labelled_asin"].items() if p in failing]
        grad = {f"{g}|{gr}": sum(res["grad_counts"][(g, gr, b)] for b in FIT_DICTIONARY)
                for g in ("men", "women")
                for gr in ("tshirt", "shirt", "jeans_trousers")}
        cellshare = {f"{g}|{h}|{b}": res["cell_counts"][(g, h, b)]
                     for g in ("men", "women") for h in ("upper", "lower")
                     for b in FIT_DICTIONARY}
        pathlib.Path(args.dump_clusters).write_text(json.dumps(
            {"KEEP": keep, "EXCLUDE": exclude, "SPLIT": split,
             "gradient_cells": grad, "cell_bucket": cellshare,
             "failing": sorted(failing)}), encoding="utf-8")
        print(f"\ncluster-size distributions written to {args.dump_clusters}")

    rule("END")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
