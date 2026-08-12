"""Is seller-level fixed effects a feasible replacement for style-level?

DESIGN.md 1.4 specifies style-level fixed effects. That specification cannot
estimate its own estimand: gender and body half do not vary within a style -- a
men's t-shirt style is men/upper for every review it carries -- so `male`,
`upper` and their interaction are perfectly collinear with the style dummies and
none of the three coefficients is identified. Confirmed empirically: of 170
distinct styles in the precision sample, ZERO carry more than one gender x half
cell.

Seller is the natural next level up. A seller can carry both genders and both
body halves, so the interaction varies within seller and stays identified. It
also absorbs seller calibration directly, which is the DESIGN.md 5.9 threat.

But that has to be MEASURED, not assumed. Identification of the interaction
needs within-seller variation in `male * upper`, and a seller spanning only one
or two cells contributes little or nothing to it:

  - 1 cell   : contributes nothing; absorbed by its own dummy.
  - 2 cells  : contributes to a main effect, but the interaction is not
               separable from the main effects within that seller.
  - 3 cells  : the interaction becomes identified within that seller.
  - 4 cells  : full 2x2 within seller -- the ideal case.

So the numbers that matter are the count of sellers with >= 3 cells and the
SHARE OF OBSERVATIONS those sellers carry. If that share is small, seller FE
discards most of the data and the answer is category-level FE with seller as a
covariate instead.

Usage:
    python seller_fe_probe.py [--reviews 3000000] [--items 400000]
"""

from __future__ import annotations

import argparse
import collections
import sys

import amazon_fit_probe
from amazon_fit_probe import (
    FIT_DICTIONARY, ROOT_SEGMENTS, WS_RX, _review_year, classify_gender,
    classify_half, iter_records, label_fit, pct, rule,
)


def build_index(category: str, limit: int) -> tuple[dict, dict]:
    """parent_asin -> (gender, half, store)."""
    index: dict[str, tuple[str, str, str]] = {}
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
        store = (record.get("store") or "").strip()
        if not store:
            stats["no_store"] += 1
            continue          # a seller FE needs a seller; unnamed is unusable
        stats["in_scope"] += 1
        index[parent] = (gender, half, store)
    return index, stats


def probe(category: str, review_limit: int, item_limit: int, window_from: int) -> dict:
    index, meta_stats = build_index(category, item_limit)
    per_seller = collections.defaultdict(collections.Counter)   # store -> cell -> n
    per_seller_styles = collections.defaultdict(set)
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
        bucket, _ = label_fit(record.get("title", ""), record.get("text", ""))
        if bucket not in FIT_DICTIONARY:
            continue
        gender, half, store = entry
        stats["labelled"] += 1
        per_seller[store][(gender, half)] += 1
        per_seller_styles[store].add(parent)

    return {"meta_stats": meta_stats, "stats": stats,
            "per_seller": dict(per_seller),
            "per_seller_styles": {k: len(v) for k, v in per_seller_styles.items()}}


def report(res: dict, window_from: int) -> None:
    per_seller = res["per_seller"]
    stats, meta = res["stats"], res["meta_stats"]

    rule(f"SELLER FIXED EFFECTS -- feasibility, window {window_from}+")
    print(f"reviews scanned {stats['scanned']:,}   labelled in-scope {stats['labelled']:,}")
    print(f"style index {meta['in_scope']:,} in scope; "
          f"{meta['no_store']:,} in-scope styles dropped for having no store name")

    if not per_seller:
        print("\nNO SELLERS. Seller FE is not available on this sample.")
        return

    total_obs = sum(sum(c.values()) for c in per_seller.values())
    by_cells = collections.Counter()
    obs_by_cells = collections.Counter()
    for store, counts in per_seller.items():
        k = len(counts)
        by_cells[k] += 1
        obs_by_cells[k] += sum(counts.values())

    print(f"\nsellers {len(per_seller):,}   observations {total_obs:,}")
    print(f"\n{'cells spanned':<16}{'sellers':>10}{'observations':>15}{'share of obs':>15}")
    for k in (1, 2, 3, 4):
        print(f"{k:<16}{by_cells[k]:>10,}{obs_by_cells[k]:>15,}"
              f"{pct(obs_by_cells[k], total_obs):>15}")

    identifying = obs_by_cells[3] + obs_by_cells[4]
    identifying_sellers = by_cells[3] + by_cells[4]
    print(f"\n{'>= 3 cells (interaction identified within seller)':<52}")
    print(f"  sellers      {identifying_sellers:>8,}  "
          f"{pct(identifying_sellers, len(per_seller))}")
    print(f"  observations {identifying:>8,}  {pct(identifying, total_obs)}")

    print(f"\n{'>= 2 cells (contributes to main effects only)':<52}")
    partial = obs_by_cells[2]
    print(f"  observations {partial:>8,}  {pct(partial, total_obs)}")
    print(f"\n{'1 cell (absorbed entirely, contributes nothing)':<52}")
    print(f"  observations {obs_by_cells[1]:>8,}  {pct(obs_by_cells[1], total_obs)}")

    # The anchor cell is what governs power, so its survival matters most.
    anchor_total = sum(c[("men", "lower")] for c in per_seller.values())
    anchor_identifying = sum(c[("men", "lower")] for c in per_seller.values()
                             if len(c) >= 3)
    print(f"\nANCHOR CELL (men/lower)")
    print(f"  all sellers            {anchor_total:>8,}")
    print(f"  in >= 3-cell sellers   {anchor_identifying:>8,}  "
          f"{pct(anchor_identifying, anchor_total)} retained under seller FE")

    print("\ntop 12 sellers by observations, with cells spanned:")
    print(f"{'seller':<34}{'obs':>8}{'cells':>7}{'styles':>8}"
          f"{'m/up':>7}{'m/low':>7}{'w/up':>7}{'w/low':>7}")
    ranked = sorted(per_seller.items(), key=lambda kv: -sum(kv[1].values()))
    for store, counts in ranked[:12]:
        print(f"{store[:33]:<34}{sum(counts.values()):>8,}{len(counts):>7}"
              f"{res['per_seller_styles'][store]:>8,}"
              f"{counts[('men', 'upper')]:>7,}{counts[('men', 'lower')]:>7,}"
              f"{counts[('women', 'upper')]:>7,}{counts[('women', 'lower')]:>7,}")

    print("\nVERDICT CRITERION: seller FE is viable if the >= 3-cell share of")
    print("observations is large enough that discarding the rest is affordable,")
    print("AND the anchor cell survives. Otherwise use category-level FE with")
    print("seller as a covariate.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=3_000_000)
    parser.add_argument("--items", type=int, default=400_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--spread", type=int, default=24)
    parser.add_argument("--window-from", type=int, default=2019)
    args = parser.parse_args()

    amazon_fit_probe.SPREAD_BLOCKS = args.spread
    rule(f"SELLER FE PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}  meta {args.items:,}  spread {args.spread}"
          f"  window {args.window_from}+")
    report(probe(args.category, args.reviews, args.items, args.window_from),
           args.window_from)
    rule("END")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
