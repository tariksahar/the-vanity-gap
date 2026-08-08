"""Validate the DESIGN.md 5.1 fit dictionary against structured ground truth.

ModCloth and RentTheRunway carry review text *and* a structured fit label on the
same record, so running the dictionary over their text and comparing row by row
gives a confusion matrix over hundreds of thousands of ground-truth comparisons.

Read `docs/phase2-divergence-precommitment.md` before interpreting the output.
Two constraints from that document govern every number printed here:

  1. These platforms *prompt* for fit; Amazon reviewers *volunteer* it. Measured
     precision is an UPPER BOUND for Amazon, not a transfer.
  2. Both datasets are women-only. They validate NOTHING for the men's arm.

Usage:
    python src/analysis/validate_dictionary.py
"""

from __future__ import annotations

import collections
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from amazon_fit_probe import FIT_DICTIONARY, label_fit  # noqa: E402

SNAPSHOT = "2026-08-08"
BUCKETS = ["ran_small", "true_to_size", "ran_large"]

# Structured field -> canonical fit_score bucket (DESIGN.md 1.4).
FIT_MAP = {"small": "ran_small", "fit": "true_to_size", "large": "ran_large"}

# Amazon CSJ predicted-bucket prevalence, garment-scoped, from the precision
# sample frame of 2026-08-08 (6,981 labelled reviews joined to an in-scope
# style). Used to reweight ModCloth/RTR precision onto Amazon's base rates.
#
# APPROXIMATION, stated because it matters: this is Amazon's *predicted*
# prevalence, standing in for its unknown *true* prevalence. The two coincide
# only if precision is high and the errors are roughly symmetric. Once
# data/processed/precision_sample.csv is labelled, replace this with the
# observed true prevalence and re-run.
AMAZON_PREVALENCE = {"ran_small": 2316, "true_to_size": 3444, "ran_large": 1221}

# DESIGN.md 1.3 body-half assignment, per corpus.
#
# ModCloth's `category` field is merchandising, not garment taxonomy: "new" and
# "sale" name a shelf, not a garment, and are unusable for this design.
MODCLOTH_HALF = {
    "tops": "upper",
    "bottoms": "lower",
    "dresses": "excluded",
    "outerwear": "excluded",
    "wedding": "excluded",
    "new": "unknown",
    "sale": "unknown",
}

RTR_UPPER = {
    "top", "sweater", "blouse", "shirt", "cardigan", "tank", "tunic",
    "sweatshirt", "pullover", "knit", "turtleneck", "tee", "cami", "hoodie",
    "t-shirt", "henley", "crewneck", "blouson", "buttondown", "sweatershirt",
}
RTR_LOWER = {
    "skirt", "skirts", "pants", "pant", "culottes", "culotte", "leggings",
    "legging", "trouser", "trousers", "tight", "skort", "jogger", "jeans",
    "sweatpants", "overalls",
}
# Dresses, gowns, jumpsuits, outerwear, and anything spanning both halves.
RTR_EXCLUDED = {
    "dress", "gown", "sheath", "shift", "jumpsuit", "maxi", "romper", "jacket",
    "mini", "coat", "blazer", "shirtdress", "down", "vest", "frock", "bomber",
    "suit", "print", "cape", "midi", "poncho", "peacoat", "kimono", "trench",
    "kaftan", "parka", "ballgown", "duster", "combo", "caftan", "overcoat",
    "for",
}


def load(path: pathlib.Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def rtr_half(category: str) -> str:
    if category in RTR_UPPER:
        return "upper"
    if category in RTR_LOWER:
        return "lower"
    if category in RTR_EXCLUDED:
        return "excluded"
    return "unknown"


def evaluate(name: str, path: pathlib.Path, half_of) -> dict:
    """Run the dictionary over one corpus and tabulate against the structured label."""
    matrix = collections.Counter()          # (truth, prediction) -> n, in-scope only
    by_cell = collections.Counter()         # (half, truth, prediction) -> n
    per_pattern = collections.Counter()     # (bucket, pattern, correct?) -> n
    stats = collections.Counter()

    for record in load(path):
        stats["rows"] += 1
        truth = FIT_MAP.get(record.get("fit"))
        if truth is None:
            stats["no_structured_label"] += 1
            continue

        half = half_of(record)
        stats[f"half_{half}"] += 1
        if half not in ("upper", "lower"):
            continue
        stats["in_scope"] += 1

        summary = record.get("review_summary") or ""
        text = record.get("review_text") or ""
        if not f"{summary}{text}".strip():
            stats["in_scope_no_text"] += 1
            matrix[(truth, "no_text")] += 1
            by_cell[(half, truth, "no_text")] += 1
            continue

        prediction, hits = label_fit(summary, text)
        matrix[(truth, prediction)] += 1
        by_cell[(half, truth, prediction)] += 1
        if prediction in BUCKETS:
            per_pattern[(prediction, hits[prediction], prediction == truth)] += 1

    return {"name": name, "matrix": matrix, "by_cell": by_cell,
            "per_pattern": per_pattern, "stats": stats}


def pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:6.2f}%" if d else "     --"


def report(result: dict) -> None:
    name, matrix, stats = result["name"], result["matrix"], result["stats"]
    print("\n" + "=" * 78)
    print(f"{name}")
    print("=" * 78)
    print(f"rows                       {stats['rows']:>8,}")
    print(f"in scope (upper or lower)  {stats['in_scope']:>8,}  "
          f"{pct(stats['in_scope'], stats['rows'])} of rows")
    for half in ("upper", "lower", "excluded", "unknown"):
        print(f"  half = {half:<10}       {stats['half_' + half]:>8,}")
    if stats["in_scope_no_text"]:
        print(f"in scope but no review text {stats['in_scope_no_text']:>7,} "
              "(counts as a miss -- the dictionary cannot match absent text)")

    predictions = BUCKETS + ["ambiguous", "none", "no_text"]

    print("\nCONFUSION MATRIX -- rows = structured label (truth), cols = dictionary")
    header = "".join(f"{p:>13}" for p in predictions)
    print(f"{'truth':<15}{header}{'total':>10}")
    for truth in BUCKETS:
        row_total = sum(matrix[(truth, p)] for p in predictions)
        cells = "".join(f"{matrix[(truth, p)]:>13,}" for p in predictions)
        print(f"{truth:<15}{cells}{row_total:>10,}")
    col_totals = "".join(f"{sum(matrix[(t, p)] for t in BUCKETS):>13,}" for p in predictions)
    grand = sum(matrix.values())
    print(f"{'total':<15}{col_totals}{grand:>10,}")

    print("\nPRECISION AND RECALL PER BUCKET")
    print(f"{'bucket':<15}{'TP':>9}{'FP':>9}{'FN':>9}{'precision':>12}{'recall':>10}{'F1':>9}")
    raw_precision = {}
    for bucket in BUCKETS:
        tp = matrix[(bucket, bucket)]
        fp = sum(matrix[(t, bucket)] for t in BUCKETS if t != bucket)
        fn = sum(matrix[(bucket, p)] for p in predictions if p != bucket)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        raw_precision[bucket] = precision
        print(f"{bucket:<15}{tp:>9,}{fp:>9,}{fn:>9,}{precision:>11.1%}{recall:>10.1%}{f1:>9.1%}")

    # Prevalence reweighting (pre-commitment doc, section 4.3). Precision depends
    # on the base rate of each true class; Amazon's differs from these platforms
    # because its reviewers volunteer fit comments mostly when the fit was wrong.
    truth_totals = {t: sum(matrix[(t, p)] for p in predictions) for t in BUCKETS}
    amazon_total = sum(AMAZON_PREVALENCE.values())
    weights = {}
    for bucket in BUCKETS:
        target = AMAZON_PREVALENCE[bucket] / amazon_total
        observed = truth_totals[bucket] / sum(truth_totals.values()) if sum(truth_totals.values()) else 0
        weights[bucket] = target / observed if observed else 0.0

    print("\nPRECISION REWEIGHTED TO AMAZON BASE RATES")
    print("  target prevalence (Amazon CSJ, garment-scoped, predicted): " +
          ", ".join(f"{b} {AMAZON_PREVALENCE[b]/amazon_total:.1%}" for b in BUCKETS))
    print("  observed prevalence (this corpus):                        " +
          ", ".join(f"{b} {truth_totals[b]/sum(truth_totals.values()):.1%}" for b in BUCKETS))
    print(f"\n{'bucket':<15}{'raw':>12}{'reweighted':>14}{'shift':>10}")
    for bucket in BUCKETS:
        num = weights[bucket] * matrix[(bucket, bucket)]
        den = sum(weights[t] * matrix[(t, bucket)] for t in BUCKETS)
        reweighted = num / den if den else 0.0
        shift = (reweighted - raw_precision[bucket]) * 100
        print(f"{bucket:<15}{raw_precision[bucket]:>11.1%}{reweighted:>13.1%}{shift:>+9.1f}pp")


def report_recall_by_cell(results: list[dict]) -> None:
    """Recall per body-half cell -- DESIGN.md 5.2's differential-selection check.

    A dictionary whose recall differs between upper and lower garments imposes
    differential selection on exactly the contrast the estimand differences, so
    a recall gap here biases `tau` directly rather than merely attenuating it.
    """
    predictions = BUCKETS + ["ambiguous", "none", "no_text"]
    print("\n" + "=" * 78)
    print("RECALL PER CELL (DESIGN.md 5.2 -- differential selection check)")
    print("=" * 78)
    print("These corpora are women-only, so the cells are body halves, not gender x half.\n")

    for result in results:
        by_cell = result["by_cell"]
        print(f"[{result['name']}]")
        print(f"{'bucket':<15}{'upper n':>10}{'upper recall':>15}"
              f"{'lower n':>10}{'lower recall':>15}{'gap (pp)':>11}")
        for bucket in BUCKETS:
            row = f"{bucket:<15}"
            recalls = {}
            for half in ("upper", "lower"):
                total = sum(by_cell[(half, bucket, p)] for p in predictions)
                tp = by_cell[(half, bucket, bucket)]
                recall = tp / total if total else 0.0
                recalls[half] = recall
                row += f"{total:>10,}{recall:>14.1%}"
            gap = (recalls["upper"] - recalls["lower"]) * 100
            flag = "  <-- >5pp" if abs(gap) > 5 else ""
            row += f"{gap:>+10.1f}{flag}"
            print(row)

        # Overall labelling rate per half: the share of rows the dictionary
        # assigns to ANY bucket. This is the selection rate that matters.
        print()
        for half in ("upper", "lower"):
            total = sum(by_cell[(half, t, p)] for t in BUCKETS for p in predictions)
            labelled = sum(by_cell[(half, t, b)] for t in BUCKETS for b in BUCKETS)
            if total:
                print(f"  {half:<6} labelled at all: {labelled:>7,} / {total:>7,} "
                      f"= {labelled / total:6.2%}")
        print()


def report_patterns(results: list[dict], min_fires: int = 40) -> None:
    """Per-pattern precision, pooled. This is the diagnostic the hand-sample cannot give."""
    pooled = collections.Counter()
    for result in results:
        pooled.update(result["per_pattern"])

    print("\n" + "=" * 78)
    print("PER-PATTERN PRECISION (pooled, in-scope rows only)")
    print("=" * 78)
    print(f"patterns shown only where they fired at least {min_fires} times\n")

    for bucket in BUCKETS:
        rows = []
        for (b, pattern, correct), n in pooled.items():
            if b != bucket:
                continue
            found = next((r for r in rows if r[0] == pattern), None)
            if found is None:
                found = [pattern, 0, 0]
                rows.append(found)
            found[1 if correct else 2] += n
        rows = [r for r in rows if r[1] + r[2] >= min_fires]
        rows.sort(key=lambda r: r[1] / (r[1] + r[2]))
        print(f"[{bucket}]")
        if not rows:
            print("    (no pattern reached the firing threshold)")
        for pattern, right, wrong in rows:
            precision = right / (right + wrong)
            flag = "  <-- BELOW 80%" if precision < 0.80 else ""
            print(f"  {precision:6.1%}  n={right + wrong:>6,}  {pattern[:88]}{flag}")
        print()


def main() -> int:
    modcloth = ROOT / f"data/raw/modcloth/{SNAPSHOT}/modcloth_final_data.json.gz"
    rtr = ROOT / f"data/raw/renttherunway/{SNAPSHOT}/renttherunway_final_data.json.gz"
    for path in (modcloth, rtr):
        if not path.exists():
            print(f"missing raw snapshot: {path}")
            return 1

    print("=" * 78)
    print("DICTIONARY VALIDATION AGAINST STRUCTURED FIT LABELS")
    print("=" * 78)
    print("Interpretation is fixed in docs/phase2-divergence-precommitment.md.")
    print("These corpora PROMPT for fit; Amazon reviewers VOLUNTEER it.")
    print("=> the precision below is an UPPER BOUND for Amazon, not a transfer.")
    print("Both corpora are WOMEN-ONLY => zero validation for the men's arm.")

    results = [
        evaluate("MODCLOTH", modcloth,
                 lambda r: MODCLOTH_HALF.get(r.get("category"), "unknown")),
        evaluate("RENTTHERUNWAY", rtr,
                 lambda r: rtr_half(r.get("category"))),
    ]
    for result in results:
        report(result)
    report_recall_by_cell(results)
    report_patterns(results)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
