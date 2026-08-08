"""Text signals that the reviewer is not the wearer, or is not the garment's gender.

DESIGN.md 1.4 conditions the estimand on the BUYER's gender. Amazon's
`categories` field gives only the gender the garment is MARKETED TO. The gap
between those two is documented in docs/phase1-amazon-probe.md 5.5, and it is
not ordinary noise: women buying men's garments is more common than the reverse,
and a large part of the reason is wanting them loose -- which lands in the data
as "men's upper garment, ran large", the exact cell and direction of the men's
hypothesis. The confound pushes toward a FALSE POSITIVE.

This module is the primary mitigation: a text filter applied to every row, so it
costs no coverage. It returns flags, not a verdict -- whether a flagged row is
dropped, reweighted, or carried as a covariate is a pre-registration decision.

Deliberately high-recall and low-precision in the third-party direction: it is
cheaper to flag an ambiguous row than to leave contamination in the primary
sample. The measured flag rate is therefore an UPPER bound on contamination, and
must be read as such.
"""

from __future__ import annotations

import re

# Someone other than the reviewer is the wearer. "for my husband", "bought it
# for my son", "a gift for her".
THIRD_PARTY_PATTERNS = [
    r"\bfor\s+(?:my|our|his|her|their)\s+(?:husband|wife|son|daughter|boyfriend|girlfriend|"
    r"partner|spouse|dad|father|mom|mother|brother|sister|grandson|granddaughter|grandpa|"
    r"grandma|grandfather|grandmother|nephew|niece|kid|kids|child|children|baby|friend|"
    r"co-?worker|colleague|teen|teenager|fiance[e]?)\b",
    r"\b(?:bought|ordered|purchased|got|buying|ordering)\s+(?:this|it|them|these|one)?\s*"
    r"(?:as\s+)?(?:a\s+)?(?:gift|present)\b",
    r"\b(?:gift|present)\s+for\b",
    r"\bmy\s+(?:husband|wife|son|daughter|boyfriend|girlfriend|partner|spouse|dad|father|"
    r"mom|mother|brother|sister|grandson|granddaughter|nephew|niece)\s+"
    r"(?:loves?|likes?|wears?|wore|is|was|has|had|says?|said|needs?|wanted|got|uses?)\b",
    r"\b(?:he|she|they)\s+(?:loves?|likes?|wears?|wore)\s+(?:it|them|this|these)\b",
    r"\bfor\s+(?:him|her)\b",
]

# The reviewer names themselves as a different gender than the garment's
# marketing category. Only unambiguous self-reference is used.
SELF_WOMAN_PATTERNS = [
    r"\bi(?:'m|\s+am)\s+(?:a\s+)?(?:woman|female|girl|lady|mom|mother|wife)\b",
    r"\bas\s+a\s+(?:woman|female|girl)\b",
    r"\bmy\s+(?:bust|bra\s+size|cup\s+size)\b",
    r"\bi(?:'m|\s+am)\s+(?:a\s+)?\d{2}\s*(?:year\s*old\s*)?(?:woman|female)\b",
]
SELF_MAN_PATTERNS = [
    r"\bi(?:'m|\s+am)\s+(?:a\s+)?(?:man|male|guy|dude|dad|father|husband)\b",
    r"\bas\s+a\s+(?:man|male|guy)\b",
    r"\bi(?:'m|\s+am)\s+(?:a\s+)?\d{2}\s*(?:year\s*old\s*)?(?:man|male)\b",
]

# The reviewer says outright that they are buying outside the marketed gender.
CROSS_GENDER_PATTERNS = [
    r"\b(?:men|mens|men's)\s+(?:sizes?|shirts?|t-?shirts?|pants?|jeans?|clothing)\b[^.]{0,60}"
    r"\b(?:for\s+)?(?:women|woman|me|myself)\b",
    r"\bi\s+(?:buy|bought|order|ordered|wear|prefer|like)\s+(?:the\s+)?(?:men|mens|men's|"
    r"women|womens|women's)\s+(?:version|sizes?|cut|style)\b",
    r"\bi(?:'m|\s+am)\s+a\s+(?:woman|female)\b[^.]{0,80}\b(?:men|mens|men's)\b",
    r"\bwomen\s+(?:can|should|could)\s+(?:also\s+)?(?:buy|order|wear)\b",
]

THIRD_PARTY_RX = [re.compile(p) for p in THIRD_PARTY_PATTERNS]
SELF_WOMAN_RX = [re.compile(p) for p in SELF_WOMAN_PATTERNS]
SELF_MAN_RX = [re.compile(p) for p in SELF_MAN_PATTERNS]
CROSS_GENDER_RX = [re.compile(p) for p in CROSS_GENDER_PATTERNS]

WS_RX = re.compile(r"\s+")


def flags(title: str, text: str, garment_gender: str | None = None) -> dict:
    """Return buyer-identity flags for one review.

    `garment_gender` is the gender from `categories`. When supplied, a mismatch
    against the reviewer's stated self-description is reported as
    `stated_mismatch` -- the direct measurement of the confound.
    """
    blob = WS_RX.sub(" ", f"{title or ''} {text or ''}".lower()).strip()

    third_party = any(rx.search(blob) for rx in THIRD_PARTY_RX)
    self_woman = any(rx.search(blob) for rx in SELF_WOMAN_RX)
    self_man = any(rx.search(blob) for rx in SELF_MAN_RX)
    cross_gender = any(rx.search(blob) for rx in CROSS_GENDER_RX)

    stated_gender = None
    if self_woman and not self_man:
        stated_gender = "women"
    elif self_man and not self_woman:
        stated_gender = "men"

    stated_mismatch = bool(
        stated_gender and garment_gender in ("men", "women")
        and stated_gender != garment_gender
    )

    return {
        "third_party": third_party,
        "cross_gender": cross_gender,
        "stated_gender": stated_gender,
        "stated_mismatch": stated_mismatch,
        "suspect": third_party or cross_gender or stated_mismatch,
    }


def is_own_purchase(title: str, text: str) -> bool:
    """True when nothing in the text suggests the reviewer is not the wearer."""
    result = flags(title, text)
    return not (result["third_party"] or result["cross_gender"])
