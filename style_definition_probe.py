"""When is a `parent_asin` a style? -- and how do heavy listings sit in the cells.

DESIGN.md 1.6 treats `parent_asin` as a style. For print-on-demand sellers it is
not: one parent covers a whole catalogue of printed designs, and one such listing
holds 18.2% of all labelled observations (docs/phase1d-specification-error.md).

**The question must be asked structurally, not by observation count.** A
review-count threshold reads as chasing power -- exclude what hurts the MDE. A
content-heterogeneity criterion reads as applying a definition -- exclude what is
not a style. Only the second is legitimate, and it can be answered without
looking at the MDE at all. Observation count is used here ONLY to find
candidates; the criterion applied to them is structural.

**A limitation that cannot be worked around on this corpus.** The published
metadata is parent-level: one row per `parent_asin`, no `asin` field
(docs/phase1-amazon-probe.md 3.1). So "how many distinct product titles do the
sub-ASINs carry" is NOT answerable -- there are no per-sub-ASIN titles to count.
What is available:

  - distinct `asin` under each parent, from the REVIEWS, which do carry `asin`
  - reviews per distinct asin
  - the review text itself, printed for hand inspection

A garment design's variants are sizes and colours, so a normal parent should show
a modest asin count that saturates. A catalogue parent should show an asin count
that grows roughly with review count and never saturates, because each new design
is a new asin.

Also measured, for the attenuation bias term (PREREGISTRATION.md 9.7):
`P(assigned = k | gender, body_half)` in the analysis population, which is what
`p_0(cell)` is built from and which no existing probe reports.

Usage:
    python style_definition_probe.py [--reviews 3000000] [--items 400000]
"""

from __future__ import annotations

import argparse
import collections
import statistics
import sys

import amazon_fit_probe
from amazon_fit_probe import (
    FIT_DICTIONARY, ROOT_SEGMENTS, WS_RX, _review_year, classify_gender,
    classify_half, iter_records, label_fit, pct, rule,
)


def build_index(category: str, limit: int) -> tuple[dict, collections.Counter]:
    index: dict[str, tuple[str, str, str, str]] = {}
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
        half = classify_half([s for s in segments if s not in ROOT_SEGMENTS])
        if half not in ("upper", "lower"):
            continue
        parent = record.get("parent_asin")
        if not parent:
            continue
        stats["in_scope"] += 1
        index[parent] = (gender, half,
                         WS_RX.sub(" ", str(record.get("title") or "")).strip(),
                         (record.get("store") or "").strip() or "(unnamed)")
    return index, stats


def probe(category: str, review_limit: int, item_limit: int, window_from: int) -> dict:
    index, meta_stats = build_index(category, item_limit)

    cell_bucket = collections.Counter()          # (gender, half, bucket) -> n
    per_parent = collections.Counter()           # parent -> labelled reviews
    parent_asins = collections.defaultdict(set)  # parent -> {asin}
    parent_reviews_all = collections.Counter()   # parent -> reviews seen (labelled or not)
    examples = collections.defaultdict(list)
    stats = collections.Counter()

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        stats["scanned"] += 1
        year = _review_year(record)
        if year is None or year < window_from:
            continue
        parent = record.get("parent_asin")
        entry = index.get(parent) if parent else None
        if entry is None:
            continue
        stats["joined"] += 1
        parent_reviews_all[parent] += 1
        if record.get("asin"):
            parent_asins[parent].add(record["asin"])

        bucket, _ = label_fit(record.get("title", ""), record.get("text", ""))
        if bucket not in FIT_DICTIONARY:
            continue
        stats["labelled"] += 1
        gender, half, _title, _store = entry
        cell_bucket[(gender, half, bucket)] += 1
        per_parent[parent] += 1
        if len(examples[parent]) < 6:
            examples[parent].append(
                WS_RX.sub(" ", str(record.get("title") or ""))[:70])

    return {"index": index, "meta_stats": meta_stats, "stats": stats,
            "cell_bucket": cell_bucket, "per_parent": per_parent,
            "parent_asins": parent_asins, "parent_reviews_all": parent_reviews_all,
            "examples": examples}


def report(res: dict, window_from: int, top: int) -> None:
    index = res["index"]
    per_parent = res["per_parent"]
    stats = res["stats"]

    rule(f"CELL COMPOSITION -- P(assigned | gender, half), window {window_from}+")
    print(f"reviews scanned {stats['scanned']:,}   joined {stats['joined']:,}"
          f"   labelled {stats['labelled']:,}")
    print("\nThis is what p_0(cell) is built from. No existing probe reported it.\n")
    print(f"{'cell':<16}" + "".join(f"{b:>14}" for b in FIT_DICTIONARY) + f"{'total':>9}")
    cell_totals = {}
    for gender in ("men", "women"):
        for half in ("upper", "lower"):
            counts = [res["cell_bucket"][(gender, half, b)] for b in FIT_DICTIONARY]
            total = sum(counts)
            cell_totals[(gender, half)] = (counts, total)
            print(f"{gender + '/' + half:<16}" + "".join(f"{c:>14,}" for c in counts)
                  + f"{total:>9,}")
    print(f"\n{'cell':<16}" + "".join(f"{b:>14}" for b in FIT_DICTIONARY) + "   (shares)")
    for (gender, half), (counts, total) in cell_totals.items():
        if not total:
            continue
        print(f"{gender + '/' + half:<16}"
              + "".join(f"{c / total:>13.3%} " for c in counts))

    # ---- heavy listings -----------------------------------------------------
    rule("CANDIDATE HEAVY LISTINGS -- ranked to FIND them, not to judge them")
    total_labelled = sum(per_parent.values())
    ranked = per_parent.most_common(top)
    print(f"{'parent_asin':<14}{'labelled':>10}{'share':>8}{'all rev':>9}"
          f"{'asins':>7}{'rev/asin':>10}  {'cell':<12} store")
    for parent, n in ranked:
        gender, half, _title, store = index[parent]
        asins = len(res["parent_asins"][parent])
        allrev = res["parent_reviews_all"][parent]
        print(f"{parent:<14}{n:>10,}{n / total_labelled:>7.1%}{allrev:>9,}"
              f"{asins:>7,}{allrev / asins if asins else 0:>10.1f}  "
              f"{gender + '/' + half:<12} {store[:26]}")

    # ---- structural comparison ---------------------------------------------
    rule("STRUCTURAL COMPARISON -- heavy listings vs typical parents")
    heavy = {p for p, _ in ranked[:5]}
    typical = [p for p, n in per_parent.items() if p not in heavy and n >= 3]
    print("A garment design's variants are sizes and colours, so a normal parent's")
    print("asin count should SATURATE. A catalogue parent's should keep growing,")
    print("because every new printed design is a new asin.\n")
    for label, group in (("heavy (top 5)", list(heavy)), ("typical (>=3 labelled)", typical)):
        if not group:
            continue
        asins = [len(res["parent_asins"][p]) for p in group]
        revs = [res["parent_reviews_all"][p] for p in group]
        ratio = [r / a for r, a in zip(revs, asins) if a]
        print(f"  {label:<24} n={len(group):>4}   "
              f"median asins {statistics.median(asins):>6.1f}   "
              f"median reviews {statistics.median(revs):>7.1f}   "
              f"median reviews/asin {statistics.median(ratio) if ratio else 0:>5.2f}")

    print("\nReview titles from the heaviest listings -- do they describe ONE product?")
    for parent, _n in ranked[:3]:
        _g, _h, title, _s = index[parent]
        print(f"\n  [{parent}] {title[:72]}")
        for example in res["examples"][parent]:
            print(f"      - {example}")

    # ---- cell exposure ------------------------------------------------------
    rule("EXPOSURE -- how heavy listings sit across the four cells")
    print("If they concentrate in one cell, excluding them changes WHICH POPULATION")
    print("is described, not only the power.\n")
    print(f"{'cell':<16}{'labelled':>10}{'from top-5':>12}{'share':>8}"
          f"{'from top-20':>13}{'share':>8}")
    top20 = {p for p, _ in per_parent.most_common(20)}
    for gender in ("men", "women"):
        for half in ("upper", "lower"):
            total = sum(res["cell_bucket"][(gender, half, b)] for b in FIT_DICTIONARY)
            h5 = sum(n for p, n in per_parent.items()
                     if p in heavy and index[p][0] == gender and index[p][1] == half)
            h20 = sum(n for p, n in per_parent.items()
                      if p in top20 and index[p][0] == gender and index[p][1] == half)
            print(f"{gender + '/' + half:<16}{total:>10,}{h5:>12,}"
                  f"{pct(h5, total):>8}{h20:>13,}{pct(h20, total):>8}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=3_000_000)
    parser.add_argument("--items", type=int, default=400_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--spread", type=int, default=24)
    parser.add_argument("--window-from", type=int, default=2019)
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    amazon_fit_probe.SPREAD_BLOCKS = args.spread
    rule(f"STYLE DEFINITION PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}  meta {args.items:,}  spread {args.spread}"
          f"  window {args.window_from}+")
    report(probe(args.category, args.reviews, args.items, args.window_from),
           args.window_from, args.top)
    rule("END -- the criterion is structural; MDE is not consulted here")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
