"""Step 1: enumerate the catalogue from the sitemap.

Writes an immutable dated snapshot of every document fetched, then derives the
product URL list into data/processed/. Re-running on the same date refuses to
overwrite an existing raw capture.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from src.adapters import mavi
from src.collect.http import Fetcher, RateLimiter

REPO_ROOT = Path(__file__).resolve().parents[2]


def raw_dir(source: str, snapshot: str) -> Path:
    path = REPO_ROOT / "data" / "raw" / source / snapshot
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_raw(directory: Path, name: str, payload: bytes) -> Path:
    """Write a raw capture, refusing to clobber an existing one."""
    target = directory / name
    if target.exists():
        raise FileExistsError(
            f"raw capture already exists: {target}. Raw data is immutable - "
            f"use a new snapshot date rather than overwriting."
        )
    target.write_bytes(payload)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=date.today().isoformat())
    parser.add_argument("--rate", type=float, default=1.0, help="requests per second")
    args = parser.parse_args()

    out = raw_dir(mavi.SOURCE, args.snapshot)
    fetcher = Fetcher(RateLimiter(min_interval=1.0 / args.rate))

    print(f"snapshot: {args.snapshot}")
    print(f"raw dir : {out}")

    # 1. robots.txt - re-verify the crawl policy live rather than trusting a
    #    copy transcribed into a document weeks ago.
    print("\n[1/3] robots.txt")
    robots = fetcher.get(mavi.ROBOTS)
    write_raw(out, "robots.txt", robots)
    print(robots.decode("utf-8", errors="replace").strip())

    # 2. sitemap index
    print("\n[2/3] sitemap index")
    index_bytes = fetcher.get(mavi.SITEMAP_INDEX)
    write_raw(out, "sitemap-index.xml", index_bytes)
    children = mavi.parse_sitemap_index(index_bytes)
    print(f"  {len(children)} child sitemaps listed")
    for url in children:
        print(f"    {url}")

    product_sitemaps = mavi.select_product_sitemaps(children)
    if not product_sitemaps:
        print("  ERROR: no product sitemap matched", file=sys.stderr)
        return 1
    print(f"  {len(product_sitemaps)} product sitemap(s) after https rewrite:")
    for url in product_sitemaps:
        print(f"    {url}")

    # 3. product sitemap(s)
    print("\n[3/3] product sitemap")
    all_urls: list[str] = []
    for i, url in enumerate(product_sitemaps):
        payload = fetcher.get(url)
        write_raw(out, f"sitemap-products-{i}.xml", payload)
        urls = mavi.parse_url_set(payload)
        print(f"  {url}\n    {len(payload):,} bytes, {len(urls):,} <loc> entries")
        all_urls.extend(urls)

    product_urls = [u for u in all_urls if "/p/" in u]
    codes = [mavi.product_code_from_url(u) for u in product_urls]
    pairs = [(u, c) for u, c in zip(product_urls, codes) if c]

    unique_codes = {c for _, c in pairs}
    # baseProduct is the leading segment of the variant code; confirmed against
    # the metadata block later, this is only a provisional count.
    provisional_styles = {c.split("-")[0] for c in unique_codes}

    print("\n--- catalogue ---")
    print(f"  <loc> entries total      : {len(all_urls):,}")
    print(f"  containing /p/           : {len(product_urls):,}")
    print(f"  code parsed              : {len(pairs):,}")
    print(f"  unique colour variants   : {len(unique_codes):,}")
    print(f"  provisional styles       : {len(provisional_styles):,}")

    processed = REPO_ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    catalogue_path = processed / f"catalogue-{mavi.SOURCE}-{args.snapshot}.jsonl"
    with catalogue_path.open("w", encoding="utf-8") as handle:
        for url, code in sorted(pairs, key=lambda p: p[1]):
            handle.write(
                json.dumps({"product_code": code, "url": url}, ensure_ascii=False) + "\n"
            )
    print(f"\n  wrote {catalogue_path}")
    print(f"  http stats: {fetcher.stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
