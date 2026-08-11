"""Is the published .jsonl ordered? Every rate we have depends on the answer.

Every number measured so far -- the fit-label share, the gender and body-half
distributions, the cell counts, the self-reported deviation prevalence -- was
computed from the FIRST N records of the source file. Reading a prefix is not
random sampling. If the file is ordered by category, ASIN, seller or time, those
rates describe a slice and not the corpus, and every published figure is invalid.

This probe reads three DISJOINT blocks -- head, middle, tail -- using HTTP range
requests, and compares the distributions across them. Agreement licenses the
existing numbers. Disagreement invalidates them.

Nothing is downloaded in full: each block is a bounded byte range.

Usage:
    python sampling_frame_probe.py [--block 50000]
"""

from __future__ import annotations

import argparse
import collections
import io
import json
import sys
import urllib.request

from amazon_fit_probe import (
    HF_RESOLVE, ROOT_SEGMENTS, USER_AGENT, WS_RX, FIT_DICTIONARY,
    classify_gender, classify_half, label_fit, pct, rule,
)

BLOCKS = ("head", "middle", "tail")


def file_size(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response:
        size = response.headers.get("Content-Length")
        if size is None:
            raise RuntimeError(f"no Content-Length for {url}")
        return int(size)


def iter_range(url: str, start: int, limit: int, skip_partial: bool):
    """Yield up to `limit` JSON records starting at byte offset `start`.

    The first line after a non-zero offset is almost certainly a fragment of the
    record that straddles the boundary, so it is discarded.
    """
    headers = {"User-Agent": USER_AGENT, "Range": f"bytes={start}-"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        if start > 0 and response.status != 206:
            raise RuntimeError(
                f"server ignored Range (status {response.status}); "
                "cannot read a disjoint block, so the check cannot run")
        reader = io.TextIOWrapper(response, encoding="utf-8", errors="replace")
        if skip_partial:
            reader.readline()
        yielded = 0
        for line in reader:
            if yielded >= limit:
                return
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue          # a truncated final line, or a boundary artefact
            yielded += 1
            yield record


def block_offsets(size: int, mean_bytes: float, limit: int) -> dict[str, int]:
    span = int(limit * mean_bytes * 1.20)
    return {
        "head": 0,
        "middle": max(0, size // 2),
        "tail": max(0, size - span),
    }


def measure_reviews(url: str, offset: int, limit: int, skip: bool) -> dict:
    counts = collections.Counter()
    total = 0
    text_bytes = 0
    for record in iter_range(url, offset, limit, skip):
        total += 1
        title, text = record.get("title", ""), record.get("text", "")
        text_bytes += len(title or "") + len(text or "")
        bucket, _ = label_fit(title, text)
        counts[bucket] += 1
        if record.get("verified_purchase"):
            counts["verified"] += 1
        rating = record.get("rating")
        if rating is not None:
            counts["rating_sum"] += float(rating)
    return {"total": total, "counts": counts, "mean_text": text_bytes / total if total else 0}


def measure_meta(url: str, offset: int, limit: int, skip: bool) -> dict:
    genders = collections.Counter()
    halves = collections.Counter()
    both = 0
    total = 0
    empty_categories = 0
    for record in iter_range(url, offset, limit, skip):
        total += 1
        cats = record.get("categories") or []
        if isinstance(cats, str):
            cats = [cats]
        segments = [WS_RX.sub(" ", str(c)).strip().lower() for c in cats if c]
        if not segments:
            empty_categories += 1
        garment = [s for s in segments if s not in ROOT_SEGMENTS]
        gender = classify_gender(" | ".join(segments))
        half = classify_half(garment)
        genders[gender] += 1
        halves[half] += 1
        if gender in ("men", "women") and half in ("upper", "lower"):
            both += 1
    return {"total": total, "genders": genders, "halves": halves,
            "both": both, "empty_categories": empty_categories}


def spread(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def verdict(label: str, values: list[float], tolerance: float) -> str:
    gap = spread(values)
    mark = "OK  " if gap <= tolerance else "DIVERGES"
    return f"  {mark}  {label:<34} spread {gap:5.2f}pp  (tolerance {tolerance:.2f}pp)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--block", type=int, default=50_000,
                        help="records per block (default 50000)")
    parser.add_argument("--category", default="Clothing_Shoes_and_Jewelry")
    args = parser.parse_args()

    review_url = f"{HF_RESOLVE}/raw/review_categories/{args.category}.jsonl"
    meta_url = f"{HF_RESOLVE}/raw/meta_categories/meta_{args.category}.jsonl"

    rule(f"SAMPLING FRAME VALIDITY -- {args.category}")
    print(f"block size {args.block:,} records, three disjoint blocks per file")
    print("if these disagree, every rate measured from a file prefix is invalid\n")

    failures: list[str] = []

    # ---- reviews -----------------------------------------------------------
    size = file_size(review_url)
    print(f"reviews file {size / 1e9:.2f} GB")
    head = measure_reviews(review_url, 0, args.block, skip=False)
    mean_bytes = size / 66_000_000 if head["total"] else 1000
    offsets = block_offsets(size, mean_bytes, args.block)
    print(f"  offsets: head 0, middle {offsets['middle']:,}, tail {offsets['tail']:,}")

    review_blocks = {"head": head}
    for name in ("middle", "tail"):
        review_blocks[name] = measure_reviews(review_url, offsets[name], args.block, skip=True)

    rule("REVIEWS -- fit-label distribution across blocks")
    print(f"{'measure':<26}" + "".join(f"{b:>12}" for b in BLOCKS))
    rows = {}
    for key, label in [("ran_small", "ran_small"), ("true_to_size", "true_to_size"),
                       ("ran_large", "ran_large"), ("ambiguous", "ambiguous"),
                       ("verified", "verified_purchase")]:
        values = [100.0 * review_blocks[b]["counts"][key] / review_blocks[b]["total"]
                  for b in BLOCKS]
        rows[label] = values
        print(f"{label:<26}" + "".join(f"{v:>11.2f}%" for v in values))

    labelled = [sum(100.0 * review_blocks[b]["counts"][k] / review_blocks[b]["total"]
                    for k in FIT_DICTIONARY) for b in BLOCKS]
    rows["usable fit label"] = labelled
    print(f"{'USABLE FIT LABEL':<26}" + "".join(f"{v:>11.2f}%" for v in labelled))

    mean_rating = [review_blocks[b]["counts"]["rating_sum"] / review_blocks[b]["total"]
                   for b in BLOCKS]
    print(f"{'mean rating':<26}" + "".join(f"{v:>12.2f}" for v in mean_rating))
    print(f"{'mean text length':<26}" +
          "".join(f"{review_blocks[b]['mean_text']:>12.0f}" for b in BLOCKS))

    print("\nverdict:")
    for label, tol in [("usable fit label", 2.0), ("ran_small", 2.0),
                       ("true_to_size", 2.0), ("ran_large", 2.0),
                       ("verified_purchase", 8.0)]:
        line = verdict(label, rows[label], tol)
        print(line)
        if "DIVERGES" in line:
            failures.append(f"reviews/{label}")

    # ---- metadata ----------------------------------------------------------
    size = file_size(meta_url)
    print(f"\nmeta file {size / 1e9:.2f} GB")
    meta_head = measure_meta(meta_url, 0, args.block, skip=False)
    mean_bytes = size / 7_200_000
    offsets = block_offsets(size, mean_bytes, args.block)
    print(f"  offsets: head 0, middle {offsets['middle']:,}, tail {offsets['tail']:,}")

    meta_blocks = {"head": meta_head}
    for name in ("middle", "tail"):
        meta_blocks[name] = measure_meta(meta_url, offsets[name], args.block, skip=True)

    rule("METADATA -- gender and body half across blocks")
    print(f"{'measure':<26}" + "".join(f"{b:>12}" for b in BLOCKS))
    meta_rows = {}
    for key, label in [("men", "gender: men"), ("women", "gender: women"),
                       ("children_excluded", "gender: children"),
                       ("unknown", "gender: unknown")]:
        values = [100.0 * meta_blocks[b]["genders"][key] / meta_blocks[b]["total"]
                  for b in BLOCKS]
        meta_rows[label] = values
        print(f"{label:<26}" + "".join(f"{v:>11.2f}%" for v in values))
    for key, label in [("upper", "half: upper"), ("lower", "half: lower"),
                       ("excluded", "half: excluded"), ("unknown", "half: unknown")]:
        values = [100.0 * meta_blocks[b]["halves"][key] / meta_blocks[b]["total"]
                  for b in BLOCKS]
        meta_rows[label] = values
        print(f"{label:<26}" + "".join(f"{v:>11.2f}%" for v in values))

    both = [100.0 * meta_blocks[b]["both"] / meta_blocks[b]["total"] for b in BLOCKS]
    meta_rows["BOTH RECOVERED"] = both
    print(f"{'BOTH RECOVERED':<26}" + "".join(f"{v:>11.2f}%" for v in both))
    empty = [100.0 * meta_blocks[b]["empty_categories"] / meta_blocks[b]["total"]
             for b in BLOCKS]
    print(f"{'empty categories':<26}" + "".join(f"{v:>11.2f}%" for v in empty))

    print("\nverdict:")
    for label, tol in [("BOTH RECOVERED", 3.0), ("gender: men", 3.0),
                       ("gender: women", 4.0), ("half: upper", 3.0),
                       ("half: lower", 2.0)]:
        line = verdict(label, meta_rows[label], tol)
        print(line)
        if "DIVERGES" in line:
            failures.append(f"meta/{label}")

    rule("CONCLUSION")
    if failures:
        print("FILE IS ORDERED. Prefix-based rates are NOT corpus rates.")
        print("Diverging measures:")
        for name in failures:
            print(f"  - {name}")
        print("\nEvery published rate must be re-derived under proper sampling.")
        return 1
    print("No divergence beyond tolerance across head, middle and tail.")
    print("Prefix-based rates are consistent with corpus rates; existing numbers stand.")
    print("\nThis is evidence of exchangeability, not proof of randomness: three blocks")
    print("cannot rule out structure at a finer scale than the block size.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
