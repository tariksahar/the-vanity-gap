"""Mavi-specific endpoints and parsers.

Everything that knows Mavi exists lives in this module. Collectors and analysis
code call these functions and never build a Mavi URL or touch Mavi HTML
themselves.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

SOURCE = "mavi"
BASE = "https://www.mavi.com"
SITEMAP_INDEX = f"{BASE}/sitemap.xml"
ROBOTS = f"{BASE}/robots.txt"

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# The product sitemap is listed inside the index over http://. Fetching it as
# listed fails; it must be rewritten to https:// first.
PRODUCT_SITEMAP_PATTERN = re.compile(r"Product-tr-TRY", re.IGNORECASE)

_PRODUCT_URL = re.compile(r"/p/([^/?#]+)")


# --------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------


def force_https(url: str) -> str:
    """Rewrite a plain-http URL to https."""
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


def parse_sitemap_index(xml_bytes: bytes) -> list[str]:
    """Return every child sitemap URL listed in a sitemap index."""
    root = ET.fromstring(xml_bytes)
    return [
        loc.text.strip()
        for loc in root.findall(".//sm:sitemap/sm:loc", SITEMAP_NS)
        if loc.text
    ]


def select_product_sitemaps(sitemap_urls: list[str]) -> list[str]:
    """Pick the product sitemap(s) out of the index, https-corrected."""
    return [force_https(u) for u in sitemap_urls if PRODUCT_SITEMAP_PATTERN.search(u)]


def parse_url_set(xml_bytes: bytes) -> list[str]:
    """Return every <url><loc> in a urlset sitemap."""
    root = ET.fromstring(xml_bytes)
    return [
        loc.text.strip()
        for loc in root.findall(".//sm:url/sm:loc", SITEMAP_NS)
        if loc.text
    ]


def product_code_from_url(url: str) -> str | None:
    """Extract the colour-variant code from a product URL.

    Mavi product URLs carry an optional slug before the code, e.g.
    ``/beyaz-basic-tisort/p/065574-620``. Only the trailing segment matters.
    """
    match = _PRODUCT_URL.search(url)
    return match.group(1) if match else None


def product_url(product_code: str) -> str:
    """Canonical product page URL. The slug is not required."""
    return f"{BASE}/p/{product_code}"


# --------------------------------------------------------------------------
# Product page metadata block
# --------------------------------------------------------------------------

# The block is a server-rendered JavaScript object literal. Anchor on the
# pagetype line, then read a bounded window forward: the object uses mixed
# quoting ('single' for keys and some values, "double" for others) so it is not
# valid JSON and cannot be parsed as such.
_ANCHOR = re.compile(r"['\"]pagetype['\"]\s*:\s*['\"]product['\"]")
_BLOCK_WINDOW = 4000

_SCALAR_FIELDS = (
    "prodid",
    "baseProduct",
    "pname",
    "pvalue",
    "p_actual_price",
    "waist",
    "fit",
    "cuff",
    "zipOrButton",
    "CD_Color",
    "pcat",
    "psubcat",
    "pgender",
    "sleeve",
)


def _scalar_pattern(field: str) -> re.Pattern[str]:
    # Value may be single- or double-quoted; capture lazily up to the matching
    # closing quote, allowing backslash escapes.
    return re.compile(
        r"['\"]" + re.escape(field) + r"['\"]\s*:\s*"
        r"(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\")"
    )


_COMPILED = {f: _scalar_pattern(f) for f in _SCALAR_FIELDS}


def parse_metadata_block(html: str) -> dict[str, str]:
    """Extract the product metadata fields from raw product-page HTML.

    Returns a dict with one entry per field found. Absent fields are omitted;
    fields present but empty are returned as empty strings, because "the site
    published an empty value" and "the parser did not find the field" are
    different facts and only the second one is a parser bug.
    """
    anchor = _ANCHOR.search(html)
    if not anchor:
        return {}

    window = html[anchor.start() : anchor.start() + _BLOCK_WINDOW]

    out: dict[str, str] = {}
    for field, pattern in _COMPILED.items():
        match = pattern.search(window)
        if match:
            value = match.group(1) if match.group(1) is not None else match.group(2)
            out[field] = value.strip()
    return out


# --------------------------------------------------------------------------
# Reviews
# --------------------------------------------------------------------------


def review_url(product_code: str, *, page: int = 0, page_size: int = 200) -> str:
    return (
        f"{BASE}/customerReview/review/{product_code}"
        f"?hasMediaOnly=false&sort=DESC&sortField=creationtime"
        f"&currentPage={page}&pageSize={page_size}"
    )


def review_probe_url(product_code: str) -> str:
    """Cheapest possible request that still returns the total review count."""
    return review_url(product_code, page_size=1)


def parse_review_count(payload: bytes) -> int:
    """Read pagination.totalNumberOfResults out of a reviews response."""
    data = json.loads(payload)
    pagination = data.get("pagination") or {}
    total = pagination.get("totalNumberOfResults")
    if total is None:
        raise ValueError("reviews response carried no pagination.totalNumberOfResults")
    return int(total)


# --------------------------------------------------------------------------
# Scope filter
# --------------------------------------------------------------------------

ADULT_GENDERS = frozenset({"Erkek", "Kadın"})

# Three-step gradient of the core hypothesis: unconstrained -> partially
# constrained -> strictly constrained.
CORE_CATEGORIES = frozenset({"Tişört", "Gömlek", "Jean"})

# Widening set, preserving the upper/lower split, held in reserve in case the
# core set proves underpowered.
EXTENDED_CATEGORIES = frozenset({"Sweatshirt", "Bluz", "Pantolon", "Şort"})

TARGET_CATEGORIES = CORE_CATEGORIES | EXTENDED_CATEGORIES

UPPER_BODY = frozenset({"Tişört", "Gömlek", "Sweatshirt", "Bluz"})
LOWER_BODY = frozenset({"Jean", "Pantolon", "Şort"})


@dataclass(frozen=True)
class FilterResult:
    keep: bool
    reason: str


def apply_scope_filter(meta: dict[str, str]) -> FilterResult:
    """Decide whether a product belongs to the study population.

    The filter is deliberately verbose about *why* something was dropped, so
    the ingest log can report the composition of the excluded set rather than
    just its size.
    """
    if not meta:
        return FilterResult(False, "no-metadata-block")

    gender = meta.get("pgender", "")
    category = meta.get("pcat", "")

    if not gender:
        return FilterResult(False, "missing-gender")
    if gender not in ADULT_GENDERS:
        # Kız Çocuk / Erkek Çocuk and anything else non-adult.
        return FilterResult(False, f"non-adult-gender:{gender}")
    if not category:
        return FilterResult(False, "missing-category")
    if category not in TARGET_CATEGORIES:
        return FilterResult(False, f"off-category:{category}")

    return FilterResult(True, "keep")


def body_half(category: str) -> str:
    if category in UPPER_BODY:
        return "upper"
    if category in LOWER_BODY:
        return "lower"
    return "other"
