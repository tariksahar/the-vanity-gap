"""Probe: explicitly self-reported size deviation in Amazon review text.

Some reviewers state both the size they usually wear and the size they actually
bought -- "I usually wear a medium, ordered a large, fit perfectly". That pair
observes the DESIGN.md 1.2 hypothesis DIRECTLY: the deviation between habitual
size and purchased size is the quantity the whole project otherwise reaches for
by proxy through `fit_score`.

This probe measures whether that language is frequent enough to build on. It
answers three questions and nothing else:

  1. What share of reviews state BOTH a usual size and a purchased size?
  2. What is the signed deviation distribution on the alpha ladder, and what are
     the gender x body-half cell counts under DESIGN.md 1.3?
  3. Do the extractions look right? -- a hand-verifiable sample is printed.

Prevalence is measured over every review streamed. Cell counts require the item
metadata join, so they are measured over the joined subset only.

Nothing is downloaded; both streams stop at the requested count.

Usage:
    python size_deviation_probe.py [--reviews 800000] [--items 300000]
"""

from __future__ import annotations

import argparse
import collections
import random
import re
import sys

from amazon_fit_probe import (
    WS_RX, build_style_index, iter_records, pct, rule,
)

sys.path.insert(0, "src/analysis")
from buyer_gender import flags as buyer_flags  # noqa: E402

# ---------------------------------------------------------------------------
# The alpha size ladder
#
# Only the letter ladder is handled. Numeric sizes (waist 32, US 8) are a
# different ladder per garment and per seller, and DESIGN.md 5.3 already
# established that they do not normalise on this corpus. Mixing the two would
# reintroduce exactly that problem, so a review that pairs a letter with a
# number is dropped rather than guessed.
# ---------------------------------------------------------------------------

LADDER = {
    "xxs": 0, "xx-s": 0, "xxsmall": 0, "xx-small": 0, "2xs": 0,
    "xs": 1, "x-s": 1, "xsmall": 1, "x-small": 1, "extra small": 1, "extra-small": 1,
    "s": 2, "small": 2,
    "m": 3, "med": 3, "medium": 3,
    "l": 4, "large": 4,
    "xl": 5, "x-l": 5, "xlarge": 5, "x-large": 5, "extra large": 5, "extra-large": 5, "1x": 5,
    "xxl": 6, "xx-l": 6, "xxlarge": 6, "xx-large": 6, "2x": 6, "2xl": 6,
    "xxxl": 7, "xxx-l": 7, "xxxlarge": 7, "xxx-large": 7, "3x": 7, "3xl": 7,
}

LADDER_NAME = {0: "XXS", 1: "XS", 2: "S", 3: "M", 4: "L", 5: "XL", 6: "XXL", 7: "XXXL"}

# Longest alternatives first so "extra large" is not eaten by "large", and
# "xxl" is not eaten by "xl".
_SIZE_ALTS = sorted(LADDER, key=len, reverse=True)
SIZE = "(" + "|".join(re.escape(alt) for alt in _SIZE_ALTS) + ")"

# A size token must not be followed by unit-like text: "small pocket", "large
# print", "medium weight" are describing the garment, not naming a size.
NOT_A_SIZE_AFTER = (
    r"(?!\s*(?:print|pocket|weight|amount|size\s+chart|bit|dogs?|breed|"
    r"business|sized?\s+(?:dog|breed|room)|to\s+medium))"
)

USUAL_PATTERNS = [
    rf"\bi\s*(?:'m|\s+am)\s+(?:usually|normally|typically|generally)\s+(?:a\s+|an\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
    rf"\bi\s+(?:usually|normally|typically|generally|always|regularly)\s+(?:wear|take|buy|order|get|purchase|am)\s+(?:a\s+|an\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
    rf"\bmy\s+(?:usual|normal|regular|typical|everyday)\s+size\s+(?:is\s+)?(?:a\s+|an\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
    rf"\bi\s+(?:wear|take|buy|order)\s+(?:a\s+|an\s+)?(?:size\s+)?{SIZE}\s+in\s+(?:most|almost|every|all|other)\b",
    rf"\b(?:normally|usually|typically)\s+(?:a\s+|an\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
]

BOUGHT_PATTERNS = [
    rf"\bi\s+(?:ordered|order|got|bought|purchased|chose|picked|selected)\s+(?:a\s+|an\s+|the\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
    rf"\bi\s+went\s+(?:with|up\s+to|down\s+to)\s+(?:a\s+|an\s+|the\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
    # The trailing context keeps this from firing on "ordered a large dog bed".
    # It must allow punctuation with no preceding space -- "ordered a large,"
    # is the single most common form of this sentence.
    rf"\b(?:ordered|bought|purchased|got)\s+(?:a\s+|an\s+|the\s+)?(?:size\s+)?{SIZE}\s*(?:\band\b|\bwhich\b|\bthat\b|,|\.|;|\bit\b|$)",
    rf"\bthis\s+(?:one\s+)?is\s+(?:a\s+|an\s+)?(?:size\s+)?{SIZE}\s+and\b",
    rf"\bopted\s+for\s+(?:a\s+|an\s+|the\s+)?(?:size\s+)?{SIZE}\b{NOT_A_SIZE_AFTER}",
]

USUAL_RX = [(p, re.compile(p)) for p in USUAL_PATTERNS]
BOUGHT_RX = [(p, re.compile(p)) for p in BOUGHT_PATTERNS]

# A numeric size anywhere near the sizing language means the review is using a
# ladder this probe cannot place. Drop rather than guess (DESIGN.md 5.3).
NUMERIC_SIZE_RX = re.compile(
    r"\b(?:size\s+\d{1,2}\b|\d{2}w\b|\bw\d{2}\b|\b\d{2}x\d{2}\b|"
    r"(?:usually|normally|typically)\s+(?:wear|take|buy|a)\s+(?:a\s+)?\d{1,2}\b)"
)


def extract_sizes(title: str, text: str) -> dict | None:
    """Return the usual/bought size pair for a review, or None.

    None covers every ambiguous case: no pair found, two different usual sizes
    claimed, two different bought sizes claimed, or a numeric ladder in play.
    Ambiguity is always a drop, never a guess (DESIGN.md 5.1).
    """
    blob = WS_RX.sub(" ", f"{title or ''} {text or ''}".lower()).strip()
    if not blob:
        return None

    usual_hits, usual_pattern = set(), None
    for raw, rx in USUAL_RX:
        for match in rx.finditer(blob):
            usual_hits.add(LADDER[match.group(1)])
            usual_pattern = usual_pattern or raw
    if len(usual_hits) != 1:
        return None

    bought_hits, bought_pattern = set(), None
    for raw, rx in BOUGHT_RX:
        for match in rx.finditer(blob):
            bought_hits.add(LADDER[match.group(1)])
            bought_pattern = bought_pattern or raw
    if len(bought_hits) != 1:
        return None

    if NUMERIC_SIZE_RX.search(blob):
        return None

    usual, bought = usual_hits.pop(), bought_hits.pop()
    return {
        "usual": usual,
        "bought": bought,
        "deviation": bought - usual,
        "usual_pattern": usual_pattern,
        "bought_pattern": bought_pattern,
        "blob": blob,
    }


def probe(category: str, review_limit: int, item_limit: int,
          n_examples: int, rng: random.Random) -> dict:
    index, meta_stats = build_style_index(category, item_limit)

    scanned = 0
    with_usual = 0
    with_bought = 0
    pairs = 0
    raw_pairs = 0
    dropped_third_party = 0
    joined = 0
    joined_pairs = 0
    deviations = collections.Counter()
    cells = collections.Counter()
    cell_dev_sum = collections.Counter()
    examples: list[dict] = []
    seen_for_example = 0

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        scanned += 1
        title, text = record.get("title", ""), record.get("text", "")
        blob = WS_RX.sub(" ", f"{title or ''} {text or ''}".lower()).strip()

        # Cheap prefilter -- the full extraction is expensive and most reviews
        # contain no sizing language at all.
        if "size" not in blob and "wear" not in blob and "order" not in blob:
            continue
        if any(rx.search(blob) for _, rx in USUAL_RX):
            with_usual += 1
        if any(rx.search(blob) for _, rx in BOUGHT_RX):
            with_bought += 1

        found = extract_sizes(title, text)
        if found is None:
            continue
        raw_pairs += 1

        # A third-party or cross-gender purchase can pair one person's usual
        # size with another person's purchase, which is not a deviation at all.
        # Dropped here rather than flagged, because for THIS probe the pair is
        # meaningless, not merely suspect.
        identity = buyer_flags(title, text)
        if identity["third_party"] or identity["cross_gender"]:
            dropped_third_party += 1
            continue

        pairs += 1
        deviations[found["deviation"]] += 1

        seen_for_example += 1
        if len(examples) < n_examples:
            examples.append(found)
        else:
            j = rng.randrange(seen_for_example)
            if j < n_examples:
                examples[j] = found

        parent = record.get("parent_asin")
        entry = index.get(parent) if parent else None
        if entry is None:
            continue
        joined += 1
        joined_pairs += 1
        gender, half, _path = entry
        cells[(gender, half)] += 1
        cell_dev_sum[(gender, half)] += found["deviation"]

    return {
        "meta_stats": meta_stats,
        "scanned": scanned,
        "with_usual": with_usual,
        "with_bought": with_bought,
        "pairs": pairs,
        "raw_pairs": raw_pairs,
        "dropped_third_party": dropped_third_party,
        "joined_pairs": joined_pairs,
        "deviations": deviations,
        "cells": cells,
        "cell_dev_sum": cell_dev_sum,
        "examples": examples,
    }


def report(res: dict, category: str) -> None:
    scanned = res["scanned"]
    rule("QUESTION 1 -- how often is a usual/bought size pair stated?")
    print(f"reviews scanned                {scanned:>10,}")
    print(f"states a usual size            {res['with_usual']:>10,}  {pct(res['with_usual'], scanned)}")
    print(f"states a bought size           {res['with_bought']:>10,}  {pct(res['with_bought'], scanned)}")
    print(f"states BOTH, unambiguously     {res['raw_pairs']:>10,}  {pct(res['raw_pairs'], scanned)}")
    print(f"  less third-party/cross-gender {res['dropped_third_party']:>10,}  "
          f"{pct(res['dropped_third_party'], res['raw_pairs'])} of pairs")
    print(f"**usable direct observations**  {res['pairs']:>10,}  {pct(res['pairs'], scanned)}")
    print()
    print("Extrapolated to the full Clothing_Shoes_and_Jewelry corpus (66.0M reviews):")
    print(f"  approx {int(66_000_000 * res['pairs'] / scanned):,} direct observations")

    rule("QUESTION 2 -- signed deviation on the alpha ladder")
    total = sum(res["deviations"].values())
    print("deviation = ladder(bought) - ladder(usual);  + means bought LARGER than usual\n")
    for dev in sorted(res["deviations"]):
        n = res["deviations"][dev]
        bar = "#" * int(50 * n / max(res["deviations"].values()))
        print(f"  {dev:+d}  {n:>7,}  {pct(n, total)}  {bar}")
    mean = sum(d * n for d, n in res["deviations"].items()) / total if total else 0.0
    up = sum(n for d, n in res["deviations"].items() if d > 0)
    down = sum(n for d, n in res["deviations"].items() if d < 0)
    same = res["deviations"].get(0, 0)
    print(f"\n  mean signed deviation {mean:+.3f} ladder steps")
    print(f"  bought larger {up:,} ({pct(up, total)})   same {same:,} ({pct(same, total)})"
          f"   bought smaller {down:,} ({pct(down, total)})")

    rule("QUESTION 2b -- gender x body half cells (joined subset)")
    meta = res["meta_stats"]
    print(f"style index: {meta['in_scope']:,} in-scope styles from {meta['seen']:,} meta records")
    print(f"pairs joined to an in-scope style: {res['joined_pairs']:,} "
          f"({pct(res['joined_pairs'], res['pairs'])} of pairs)\n")
    cells, dev_sum = res["cells"], res["cell_dev_sum"]
    print(f"{'':<8}{'upper':>22}{'lower':>22}")
    for gender in ("men", "women"):
        row = ""
        for half in ("upper", "lower"):
            n = cells[(gender, half)]
            mean_dev = dev_sum[(gender, half)] / n if n else 0.0
            row += f"{n:>12,} ({mean_dev:+.2f}){'':>2}"
        print(f"{gender:<8}{row}")
    print("\n  cell entries are:  n  (mean signed deviation)")
    smallest = min(cells[(g, h)] for g in ("men", "women") for h in ("upper", "lower"))
    print(f"  smallest cell: {smallest:,}  <- DESIGN.md 5.5 binding constraint")

    rule("QUESTION 3 -- hand-verifiable sample")
    print("Read each and score whether both sizes were extracted correctly.\n")
    for i, ex in enumerate(res["examples"], 1):
        print(f"{i:>3}. usual={LADDER_NAME[ex['usual']]:<4} bought={LADDER_NAME[ex['bought']]:<4} "
              f"deviation={ex['deviation']:+d}")
        blob = ex["blob"]
        print(f"     {blob[:300]}{'...' if len(blob) > 300 else ''}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reviews", type=int, default=800_000)
    parser.add_argument("--items", type=int, default=300_000)
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    parser.add_argument("--examples", type=int, default=15)
    parser.add_argument("--seed", type=int, default=20260808)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rule(f"SELF-REPORTED SIZE DEVIATION PROBE -- {args.category}")
    print(f"reviews {args.reviews:,}   meta {args.items:,}   seed {args.seed}")
    print("stream-only: nothing is downloaded, nothing is written to disk")

    res = probe(args.category, args.reviews, args.items, args.examples, rng)
    report(res, args.category)
    rule("END -- this probe measures feasibility, it does not estimate anything")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
