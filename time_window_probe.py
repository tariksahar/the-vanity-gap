"""Where does the review-writing regime stabilise, and what does each window cost?

DESIGN.md 5.8 set a trailing 12-18 month window against SURVIVORSHIP bias alone.
The sampling-frame check of 2026-08-11 produced a second and stronger reason:
the review-writing regime itself drifts. Verified-purchase share ran 65% -> 95%,
mean length 316 -> 142 characters, fit-label share 19.3% -> 13.8% across the
file. Pooling a decade pools heterogeneous MEASUREMENT regimes, and if the mix
differs across cells it contaminates `tau` directly.

So the boundary is an empirical question, not a number picked in advance. This
probe answers two things:

  1. Per calendar year: verified-purchase share, mean review length, mean rating
     and fit-label share. The window should start where these flatten.

  2. Per candidate window: the four gender x body-half cell counts, and the
     men's-lower count specifically. DESIGN.md 5.5 makes cell imbalance -- not
     total volume -- the binding constraint, and the upper:lower ratio was
     already seen moving 2.14 -> 2.58 -> 2.63 across file blocks. A window that
     starves the men's-lower cell is unavailable however much total data it
     offers, because that cell is the placebo anchor of DESIGN.md 1.5.

Block-sampled throughout (DESIGN.md 5.13): a prefix read would answer the wrong
question here in the most direct way possible, since file position IS time.

Usage:
    python time_window_probe.py [--reviews 600000] [--items 250000]
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import sys

import amazon_fit_probe
from amazon_fit_probe import (
    FIT_DICTIONARY, WS_RX, build_style_index, iter_records, label_fit, pct, rule,
)

CANDIDATE_WINDOWS = [
    ("18 months", 1.5),
    ("3 years", 3.0),
    ("5 years", 5.0),
    ("8 years", 8.0),
    ("full history", None),
]


def review_year(record: dict) -> int | None:
    """Amazon Reviews'23 timestamps are milliseconds since the epoch."""
    raw = record.get("timestamp")
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value > 1e11:          # milliseconds
        value /= 1000.0
    try:
        return dt.datetime.utcfromtimestamp(value).year
    except (OverflowError, OSError, ValueError):
        return None


def probe(category: str, review_limit: int, item_limit: int) -> dict:
    index, meta_stats = build_style_index(category, item_limit)

    per_year = collections.defaultdict(lambda: collections.Counter())
    cells_by_year = collections.defaultdict(lambda: collections.Counter())
    scanned = 0
    no_timestamp = 0
    max_year = 0

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        scanned += 1
        year = review_year(record)
        if year is None:
            no_timestamp += 1
            continue
        max_year = max(max_year, year)

        title, text = record.get("title", ""), record.get("text", "")
        blob = WS_RX.sub(" ", f"{title or ''} {text or ''}").strip()

        bucket = per_year[year]
        bucket["n"] += 1
        bucket["chars"] += len(blob)
        if record.get("verified_purchase"):
            bucket["verified"] += 1
        rating = record.get("rating")
        if rating is not None:
            bucket["rating_sum"] += float(rating)

        label, _ = label_fit(title, text)
        if label in FIT_DICTIONARY:
            bucket["labelled"] += 1
            entry = index.get(record.get("parent_asin"))
            if entry is not None:
                gender, half, _path = entry
                cells_by_year[year][(gender, half)] += 1

    return {"meta_stats": meta_stats, "scanned": scanned, "no_timestamp": no_timestamp,
            "per_year": per_year, "cells_by_year": cells_by_year, "max_year": max_year}


def report(res: dict, min_year_n: int = 300) -> None:
    per_year = res["per_year"]
    rule("PER-YEAR COMPOSITION -- where does the regime stabilise?")
    print(f"reviews scanned {res['scanned']:,}   without a usable timestamp {res['no_timestamp']:,}")
    print(f"latest year seen: {res['max_year']}\n")
    print(f"{'year':<8}{'n':>9}{'verified':>11}{'mean len':>10}{'mean rating':>13}{'fit label':>12}")

    years = sorted(y for y in per_year if per_year[y]["n"] >= min_year_n)
    series = {}
    for year in years:
        bucket = per_year[year]
        n = bucket["n"]
        verified = 100.0 * bucket["verified"] / n
        length = bucket["chars"] / n
        rating = bucket["rating_sum"] / n
        labelled = 100.0 * bucket["labelled"] / n
        series[year] = (verified, length, rating, labelled)
        print(f"{year:<8}{n:>9,}{verified:>10.1f}%{length:>10.0f}{rating:>13.2f}{labelled:>11.1f}%")
    if not years:
        print("  (no year reached the reporting threshold)")
        return

    print(f"\nyears with fewer than {min_year_n} reviews are suppressed as unstable")

    # Year-on-year change, to locate the flattening point rather than assert one.
    print("\nYEAR-ON-YEAR CHANGE (absolute):")
    print(f"{'year':<8}{'d verified':>12}{'d mean len':>12}{'d fit label':>13}{'stable?':>10}")
    stable_from = None
    for previous, year in zip(years, years[1:]):
        d_verified = series[year][0] - series[previous][0]
        d_length = series[year][1] - series[previous][1]
        d_label = series[year][3] - series[previous][3]
        stable = abs(d_verified) < 2.0 and abs(d_length) < 15 and abs(d_label) < 1.5
        print(f"{year:<8}{d_verified:>+11.1f}%{d_length:>+12.0f}{d_label:>+12.1f}%"
              f"{'  yes' if stable else '  NO':>10}")
        if stable and stable_from is None:
            stable_from = year
        if not stable:
            stable_from = None
    if stable_from:
        print(f"\n  series flatten from {stable_from} onward")
    else:
        print("\n  no sustained flat run found in this sample")

    # ---- candidate windows, judged on the smallest cell ---------------------
    rule("CANDIDATE WINDOWS -- judged on the SMALLEST cell, not total volume")
    latest = res["max_year"]
    cells_by_year = res["cells_by_year"]
    print(f"{'window':<16}{'from':>6}{'labelled':>11}"
          f"{'men/up':>9}{'men/LOW':>9}{'wom/up':>9}{'wom/low':>9}{'min cell':>10}")
    for name, years_back in CANDIDATE_WINDOWS:
        start = -10_000 if years_back is None else latest - years_back + 1
        totals = collections.Counter()
        labelled = 0
        for year, counts in cells_by_year.items():
            if year >= start:
                totals.update(counts)
        for year, bucket in per_year.items():
            if year >= start:
                labelled += bucket["labelled"]
        cells = [totals[(g, h)] for g in ("men", "women") for h in ("upper", "lower")]
        smallest = min(cells) if cells else 0
        shown = "all" if years_back is None else f"{int(start)}"
        print(f"{name:<16}{shown:>6}{labelled:>11,}"
              f"{totals[('men', 'upper')]:>9,}{totals[('men', 'lower')]:>9,}"
              f"{totals[('women', 'upper')]:>9,}{totals[('women', 'lower')]:>9,}"
              f"{smallest:>10,}")

    print("\n  men/LOW is the DESIGN.md 1.5 placebo anchor and the DESIGN.md 5.5 binding")
    print("  constraint. A window that starves it is unavailable regardless of total volume.")
    print("  Counts are per this sample, not corpus totals -- scale by 66.0M / scanned.")

    scanned = res["scanned"]
    if scanned:
        print(f"\n  corpus scale factor: x{66_000_000 / scanned:,.0f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=600_000)
    parser.add_argument("--items", type=int, default=250_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--spread", type=int, default=16)
    parser.add_argument("--min-year-n", type=int, default=300)
    args = parser.parse_args()

    amazon_fit_probe.SPREAD_BLOCKS = args.spread

    rule(f"TIME WINDOW PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}   meta {args.items:,}   spread {args.spread} blocks")
    print("block-sampled: file position IS time here, so a prefix read would be worthless")

    report(probe(args.category, args.reviews, args.items), args.min_year_n)
    rule("END -- the window is chosen from these numbers, not before them")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
