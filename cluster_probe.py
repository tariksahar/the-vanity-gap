"""Cell counts for BOTH samples, and the clustering parameters, measured.

Three things the MDE table currently assumes rather than knows.

**1. Which sample.** DESIGN.md 1.3 defines two: the three-category gradient
(tee / shirt / jeans) as PRIMARY, and the wider upper/lower sets as the
secondary, higher-powered version. The MDE published in PREREGISTRATION.md 7.1a
was computed on cells produced by `classify_half`, which uses the WIDE patterns.
So the published figure describes the secondary specification, and the primary
one is thinner. Both are measured here so the ladder can be read on the right
row.

**2. m_bar** -- mean labelled reviews per style. It enters the design effect
linearly and the table currently carries the Phase 0 Mavi figure of 20, which is
implausible on its face: Mavi's own mean was 12.7 reviews per variant across a
single brand, while Amazon has 7.2M items with a very heavy tail. At ICC 0.05 /
CV 1, m_bar 20 gives DEFF 2.95 and m_bar 5 gives 1.45 -- an MDE of roughly 0.29
instead of 0.418. This is the pivot, not a caveat.

**3. CV** -- coefficient of variation of that per-style count, the other assumed
input, and the one the Phase 0 analysis found expensive.

All within the DESIGN.md 5.8 analysis window and block-sampled.

Usage:
    python cluster_probe.py [--reviews 800000] [--items 300000] [--window-from 2019]
"""

from __future__ import annotations

import argparse
import collections
import math
import sys

import amazon_fit_probe
from amazon_fit_probe import (
    FIT_DICTIONARY, ROOT_SEGMENTS, WS_RX, _review_year, classify_gender,
    classify_gradient, classify_half, iter_records, label_fit, pct, rule,
)

# Gradient class -> body half, for the PRIMARY sample. The gradient is a
# three-step dose-response; the estimand still needs two halves, so tee and
# shirt are the upper arm and jeans/trousers the lower.
GRADIENT_HALF = {"tshirt": "upper", "shirt": "upper", "jeans_trousers": "lower"}


def build_index(category: str, limit: int) -> tuple[dict, dict]:
    """parent_asin -> (gender, wide_half, gradient_half)."""
    index: dict[str, tuple[str, str, str | None]] = {}
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
        wide = classify_half(garment)
        if wide not in ("upper", "lower"):
            continue
        parent = record.get("parent_asin")
        if not parent:
            continue
        gradient = classify_gradient(garment)
        narrow = GRADIENT_HALF.get(gradient) if gradient else None
        stats["in_scope_wide"] += 1
        if narrow:
            stats["in_scope_narrow"] += 1
        index[parent] = (gender, wide, narrow)
    return index, stats


def probe(category: str, review_limit: int, item_limit: int, window_from: int) -> dict:
    index, meta_stats = build_index(category, item_limit)

    wide_cells = collections.Counter()
    narrow_cells = collections.Counter()
    per_style_wide = collections.Counter()      # parent_asin -> labelled reviews
    per_style_narrow = collections.Counter()
    stats = collections.Counter()

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        stats["scanned"] += 1
        year = _review_year(record)
        if year is None or year < window_from:
            stats["outside_window"] += 1
            continue
        parent = record.get("parent_asin")
        entry = index.get(parent) if parent else None
        if entry is None:
            continue
        stats["joined"] += 1
        bucket, _ = label_fit(record.get("title", ""), record.get("text", ""))
        if bucket not in FIT_DICTIONARY:
            continue
        stats["labelled"] += 1
        gender, wide, narrow = entry
        wide_cells[(gender, wide)] += 1
        per_style_wide[parent] += 1
        if narrow:
            narrow_cells[(gender, narrow)] += 1
            per_style_narrow[parent] += 1

    return {"meta_stats": meta_stats, "stats": stats,
            "wide_cells": wide_cells, "narrow_cells": narrow_cells,
            "per_style_wide": per_style_wide, "per_style_narrow": per_style_narrow}


def cluster_stats(per_style: collections.Counter) -> dict:
    """m_bar and CV of labelled reviews per style -- the two DEFF inputs."""
    counts = list(per_style.values())
    if not counts:
        return {}
    n = len(counts)
    mean = sum(counts) / n
    variance = sum((c - mean) ** 2 for c in counts) / n
    sd = math.sqrt(variance)
    ordered = sorted(counts)
    return {"styles": n, "observations": sum(counts), "m_bar": mean,
            "sd": sd, "cv": sd / mean if mean else 0.0,
            "max": ordered[-1],
            "p50": ordered[n // 2],
            "p90": ordered[int(n * 0.90)],
            "p99": ordered[min(n - 1, int(n * 0.99))],
            "share_singletons": sum(1 for c in counts if c == 1) / n}


def report(res: dict, window_from: int) -> None:
    stats = res["stats"]
    rule(f"CELLS BY SAMPLE DEFINITION -- window {window_from} onward")
    print(f"reviews scanned {stats['scanned']:,}   outside window {stats['outside_window']:,}")
    print(f"joined {stats['joined']:,}   labelled {stats['labelled']:,}")
    meta = res["meta_stats"]
    print(f"\nstyle index: {meta['in_scope_wide']:,} in scope (wide), "
          f"{meta['in_scope_narrow']:,} in scope (gradient), "
          f"from {meta['seen']:,} meta records")

    for name, cells in (("WIDE upper/lower (DESIGN.md 1.3 secondary)", res["wide_cells"]),
                        ("GRADIENT tee+shirt / jeans (DESIGN.md 1.2 PRIMARY)", res["narrow_cells"])):
        print(f"\n{name}")
        print(f"{'':<8}{'upper':>10}{'lower':>10}")
        for gender in ("men", "women"):
            print(f"{gender:<8}{cells[(gender, 'upper')]:>10,}{cells[(gender, 'lower')]:>10,}")
        values = [cells[(g, h)] for g in ("men", "women") for h in ("upper", "lower")]
        print(f"  anchor cell (men/lower): {cells[('men', 'lower')]:,}"
              f"   smallest: {min(values):,}   total: {sum(values):,}")

    rule("CLUSTERING PARAMETERS -- measured, not assumed")
    for name, per_style in (("wide", res["per_style_wide"]),
                            ("gradient", res["per_style_narrow"])):
        c = cluster_stats(per_style)
        if not c:
            print(f"\n[{name}] no observations")
            continue
        print(f"\n[{name} sample]  styles {c['styles']:,}   observations {c['observations']:,}")
        print(f"  m_bar (mean labelled reviews per style)   {c['m_bar']:.3f}")
        print(f"  SD                                        {c['sd']:.3f}")
        print(f"  **CV**                                    {c['cv']:.3f}")
        print(f"  median {c['p50']}   p90 {c['p90']}   p99 {c['p99']}   max {c['max']}")
        print(f"  styles with exactly one labelled review   {c['share_singletons']:.1%}")

    print("\n  m_bar and CV enter DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC.")
    print("  The Phase 0 table assumed m_bar 20 (Mavi, single brand). If the measured")
    print("  value is far below that, the published MDE is too pessimistic.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=800_000)
    parser.add_argument("--items", type=int, default=300_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--spread", type=int, default=16)
    parser.add_argument("--window-from", type=int, default=2019)
    args = parser.parse_args()

    amazon_fit_probe.SPREAD_BLOCKS = args.spread
    rule(f"CLUSTER AND CELL PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}   meta {args.items:,}   spread {args.spread}"
          f"   window {args.window_from}+")
    report(probe(args.category, args.reviews, args.items, args.window_from),
           args.window_from)
    rule("END")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
