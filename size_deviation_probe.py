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

# A disjunctive size -- "a small or medium", "l/xl" -- names a RANGE, not a
# point on the ladder. The 2026-08-08 hand-check found the extractor silently
# resolving these to the first term, and in two of the three observed cases that
# INFLATED the measured deviation ("usually a small or medium, ordered a medium"
# was recorded as +1 when the honest reading is 0). Ambiguity is a drop, never a
# guess (DESIGN.md 5.1), so any disjunctive size in the review drops the record.
# Deliberately conservative: it fires on a disjunction anywhere in the text, not
# only inside the matched phrase.
DISJUNCTIVE_SIZE_RX = re.compile(rf"\b{SIZE}\s*(?:/|\s+or\s+|\s*-\s*){SIZE}\b")

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

    if DISJUNCTIVE_SIZE_RX.search(blob):
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


def build_seller_index(category: str, limit: int) -> tuple[dict, dict]:
    """parent_asin -> (gender, half, store) for in-scope styles.

    Separate from build_style_index because it additionally captures `store`,
    which is what the DESIGN.md 5.9 calibration test needs.
    """
    from amazon_fit_probe import ROOT_SEGMENTS, classify_gender, classify_half

    index: dict[str, tuple[str, str, str]] = {}
    stats = {"seen": 0, "in_scope": 0, "no_store": 0}
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
            store = "(unnamed store)"
        stats["in_scope"] += 1
        index[parent] = (gender, half, store)
    return index, stats


def probe_sellers(category: str, review_limit: int, item_limit: int) -> dict:
    """Is the observed deviation the buyer's desire or the seller's ruler?

    DESIGN.md 5.9. Amazon is a marketplace. A large share of apparel sellers use
    non-US sizing that runs small, and "order two sizes up" is a review genre
    rather than a preference. If a small number of stores account for most of the
    positive deviation, the measurement is calibration, not behaviour. If it is
    spread thinly across many sellers, it is behavioural.
    """
    index, meta_stats = build_seller_index(category, item_limit)

    per_store = collections.defaultdict(lambda: {"n": 0, "sum": 0, "pos": 0})
    per_store_gender = collections.defaultdict(lambda: collections.Counter())
    observations: list[tuple[str, str, int]] = []   # (store, gender, deviation)
    scanned = joined = 0

    for record in iter_records(f"raw_review_{category}", category, review_limit):
        scanned += 1
        title, text = record.get("title", ""), record.get("text", "")
        blob = WS_RX.sub(" ", f"{title or ''} {text or ''}".lower()).strip()
        if "size" not in blob and "wear" not in blob and "order" not in blob:
            continue
        found = extract_sizes(title, text)
        if found is None:
            continue
        identity = buyer_flags(title, text)
        if identity["third_party"] or identity["cross_gender"]:
            continue
        entry = index.get(record.get("parent_asin"))
        if entry is None:
            continue
        joined += 1
        gender, half, store = entry
        observations.append((store, gender, found["deviation"]))
        bucket = per_store[store]
        bucket["n"] += 1
        bucket["sum"] += found["deviation"]
        if found["deviation"] > 0:
            bucket["pos"] += 1
            per_store_gender[store][gender] += 1

    return {"meta_stats": meta_stats, "scanned": scanned, "joined": joined,
            "per_store": dict(per_store), "per_store_gender": dict(per_store_gender),
            "observations": observations}


def variance_decomposition(observations: list[tuple[str, str, int]]) -> dict:
    """How much of the variance in deviation is BETWEEN stores vs WITHIN them?

    This is the question concentration statistics do not answer. HHI describes
    how observations spread across stores; it says nothing about whether the
    deviation is a property of the store (calibration) or of the person
    (behaviour). A one-way ANOVA on store does.

        eta^2 = SS_between / SS_total

    High eta^2 => stores differ systematically => the seller's ruler.
    Low eta^2  => deviation varies within stores as much as across them =>
                  a property of buyers, not of sellers.
    """
    if not observations:
        return {}
    values = [d for _s, _g, d in observations]
    grand = sum(values) / len(values)
    ss_total = sum((v - grand) ** 2 for v in values)

    by_store = collections.defaultdict(list)
    for store, _gender, deviation in observations:
        by_store[store].append(deviation)

    ss_between = sum(len(v) * (sum(v) / len(v) - grand) ** 2 for v in by_store.values())
    ss_within = ss_total - ss_between
    k, n = len(by_store), len(values)

    # Unbiased ICC via one-way random effects, since eta^2 is upward-biased when
    # groups are small and numerous -- which is exactly this data.
    icc = None
    if k > 1 and n > k:
        ms_between = ss_between / (k - 1)
        ms_within = ss_within / (n - k)
        sizes = [len(v) for v in by_store.values()]
        m0 = (n - sum(x * x for x in sizes) / n) / (k - 1)
        if m0 > 0 and ms_between + (m0 - 1) * ms_within != 0:
            icc = (ms_between - ms_within) / (ms_between + (m0 - 1) * ms_within)

    return {"eta_squared": ss_between / ss_total if ss_total else 0.0,
            "icc_store": icc, "n": n, "stores": k,
            "mean_obs_per_store": n / k if k else 0.0}


def within_store_gender(observations: list[tuple[str, str, int]]) -> dict:
    """The clean test: men vs women INSIDE the same store.

    A store's calibration is constant within that store, so comparing genders
    inside it differences calibration out entirely. A residual gender gap here
    cannot be the seller's ruler.

    Reports the overlap first, because if too few stores carry both genders the
    test does not exist and saying so is the honest answer.
    """
    by_store = collections.defaultdict(lambda: {"men": [], "women": []})
    for store, gender, deviation in observations:
        if gender in ("men", "women"):
            by_store[store][gender].append(deviation)

    both = {s: v for s, v in by_store.items() if v["men"] and v["women"]}
    covered = sum(len(v["men"]) + len(v["women"]) for v in both.values())
    men_obs = sum(len(v["men"]) for v in both.values())
    women_obs = sum(len(v["women"]) for v in both.values())

    gaps, weights = [], []
    for value in both.values():
        men_mean = sum(value["men"]) / len(value["men"])
        women_mean = sum(value["women"]) / len(value["women"])
        weight = min(len(value["men"]), len(value["women"]))
        gaps.append(men_mean - women_mean)
        weights.append(weight)

    weighted = (sum(g * w for g, w in zip(gaps, weights)) / sum(weights)
                if sum(weights) else None)
    return {"stores_with_both": len(both), "stores_total": len(by_store),
            "observations_covered": covered, "men_obs": men_obs,
            "women_obs": women_obs, "weighted_gap": weighted,
            "unweighted_gap": sum(gaps) / len(gaps) if gaps else None}


def report_sellers(res: dict) -> None:
    per_store = res["per_store"]
    rule("SELLER CALIBRATION vs BUYER BEHAVIOUR (DESIGN.md 5.9)")
    print(f"reviews scanned {res['scanned']:,}   joined with a store {res['joined']:,}")
    if not per_store:
        print("no joined observations; nothing to report")
        return

    total_pos = sum(v["pos"] for v in per_store.values())
    total_n = sum(v["n"] for v in per_store.values())
    print(f"distinct stores {len(per_store):,}   positive-deviation observations {total_pos:,}")

    ranked = sorted(per_store.items(), key=lambda kv: kv[1]["pos"], reverse=True)
    print("\nconcentration of POSITIVE deviation:")
    cumulative = 0
    for k in (1, 5, 10, 25, 50):
        cumulative = sum(v["pos"] for _, v in ranked[:k])
        print(f"  top {k:>3} stores  {cumulative:>6,}  {pct(cumulative, total_pos)} of positive deviation")

    shares = [v["pos"] / total_pos for _, v in ranked if total_pos]
    hhi = sum(s * s for s in shares)
    print(f"\n  HHI {hhi:.4f}   (1/n = {1 / len(per_store):.4f} if perfectly spread)")
    print(f"  effective number of stores  {1 / hhi:.1f}" if hhi else "")
    print("\n  CAVEAT: concentration describes how OBSERVATIONS spread across stores.")
    print("  It does NOT answer whether deviation is a property of the store or of")
    print("  the person. The two tests below do.")

    observations = res.get("observations") or []

    rule("VARIANCE DECOMPOSITION -- store property or person property?")
    decomposition = variance_decomposition(observations)
    if decomposition:
        print(f"observations {decomposition['n']:,}   stores {decomposition['stores']:,}"
              f"   mean obs/store {decomposition['mean_obs_per_store']:.1f}")
        print(f"\n  eta^2 (share of variance BETWEEN stores)  {decomposition['eta_squared']:.3f}")
        if decomposition["icc_store"] is not None:
            print(f"  ICC  (unbiased, one-way random effects)  {decomposition['icc_store']:.3f}")
        print("\n  eta^2 is upward-biased with many small groups -- read the ICC.")
        print("  High => stores differ systematically => calibration.")
        print("  Low  => varies within stores as much as across => behaviour.")

    rule("WITHIN-STORE GENDER TEST -- calibration differenced out")
    within = within_store_gender(observations)
    print(f"stores carrying BOTH genders  {within['stores_with_both']:,}"
          f" of {within['stores_total']:,}")
    print(f"observations covered          {within['observations_covered']:,}"
          f"  (men {within['men_obs']:,}, women {within['women_obs']:,})")
    if within["stores_with_both"] < 15 or within["men_obs"] < 30:
        print("\n  OVERLAP TOO THIN. The within-store test does not exist on this")
        print("  sample. Reported as unavailable rather than substituted with a")
        print("  weaker measure.")
    else:
        print(f"\n  within-store gap (men - women), weighted    {within['weighted_gap']:+.3f}")
        print(f"  within-store gap (men - women), unweighted  {within['unweighted_gap']:+.3f}")
        print("\n  A store's calibration is constant within it, so a residual gap")
        print("  here CANNOT be calibration.")

    print("\ntop 15 stores by positive-deviation count:")
    print(f"{'store':<34}{'n':>7}{'mean dev':>10}{'pos':>7}{'men':>6}{'women':>7}")
    for store, value in ranked[:15]:
        mean = value["sum"] / value["n"] if value["n"] else 0.0
        genders = res["per_store_gender"].get(store, {})
        print(f"{store[:33]:<34}{value['n']:>7,}{mean:>+10.2f}{value['pos']:>7,}"
              f"{genders.get('men', 0):>6,}{genders.get('women', 0):>7,}")


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
        gender, half, _path, _title = entry
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
    parser.add_argument("--spread", type=int, default=0,
                        help="block-sample across N disjoint file offsets "
                             "(0 = prefix read, which is biased -- see DESIGN.md 5.13)")
    parser.add_argument("--by-seller", action="store_true",
                        help="run the DESIGN.md 5.9 seller-calibration test instead")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    import amazon_fit_probe
    amazon_fit_probe.SPREAD_BLOCKS = args.spread

    if args.by_seller:
        rule(f"SELLER CALIBRATION TEST -- {args.category}")
        print(f"reviews {args.reviews:,}   meta {args.items:,}")
        report_sellers(probe_sellers(args.category, args.reviews, args.items))
        rule("END")
        return 0
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
