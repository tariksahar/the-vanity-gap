# Ethics, licensing and access

Companion to `DESIGN.md` §0.5 and §6. Records what was asked, of whom, when, and what came back —
including the requests that received no reply, because an undocumented attempt is indistinguishable
from no attempt.

---

## 1. Data licensing — UNRESOLVED

### 1.1 Position

Both upstream datasets carry **no licence statement of any kind.** Not a permissive licence, not a
restrictive one, not an unrecognised one — the field is simply absent.

| Dataset | Checked | Licence tag | Terms of use | Licence file | Stated condition |
|---|---|---|---|---|---|
| Amazon Reviews'23 (HuggingFace, McAuley-Lab) | 2026-08-08 | none | none | none | request to cite the paper |
| Clothing Fit — ModCloth, RentTheRunway (McAuley Lab, UCSD) | 2026-08-08 | none | none | none | request to cite the paper |

**Absent an affirmative grant, redistribution of derived records is not authorised by default.** A
citation request is an academic courtesy, not a licence, and it grants nothing about redistribution.

### 1.2 What this permits and forbids, pending resolution

**Permitted, and in force now:**

- Reading the data for analysis.
- Publishing **aggregated** results — rates, coefficients, tables, figures.
- Publishing all code.

**Forbidden until resolved:**

- Publishing raw review text or any user field, in any quantity (`DESIGN.md` §6).
- Redistributing derived record-level data.
- The §4.4 open-dataset deliverable in anything other than **aggregates-only** form.

Local working files containing raw text — `data/processed/precision_sample.csv` and its `.xlsx`
twin — are permanently git-ignored, including after they are labelled.

### 1.3 Enquiry sent to the McAuley Lab

**Status: DRAFTED, NOT SENT — awaiting the repository owner's approval.**

Recipient, date sent, and any reply are recorded in §1.5 below when they exist. The draft is in
§1.4 so that the exact wording asked is on the record, not a summary of it.

### 1.4 Draft message

> **Subject:** Licence terms for derived data — Amazon Reviews'23 and the Clothing Fit datasets
>
> Dear Professor McAuley and colleagues,
>
> I am working on an academic study of clothing size-label deviation, using the Amazon Reviews'23
> corpus (`McAuley-Lab/Amazon-Reviews-2023` on HuggingFace) and the Clothing Fit datasets
> (ModCloth and RentTheRunway) distributed by your lab. Both will be cited as requested; the
> relevant papers are Hou et al. (2024) and Misra, Wan & McAuley (2018).
>
> I could not find a licence statement for either dataset — the HuggingFace dataset page and the
> lab's distribution page each state a citation request, but neither carries a licence tag, terms
> of use, or a licence file. I would rather ask than assume, so I have three questions:
>
> 1. What terms apply to **derived data** — for example, aggregated statistics computed from the
>    reviews, or per-item summary variables?
> 2. May **record-level derived data** be redistributed as part of a replication package? I am
>    thinking of a table of item identifiers with derived labels attached, containing no review
>    text and no user identifiers.
> 3. Is there any restriction you would want observed on **publishing excerpts of review text** —
>    for instance a small number of example reviews shown in a paper to illustrate a coding rule?
>
> My current working assumption, which I will keep to unless you tell me otherwise, is the
> conservative one: publish aggregates and code only, redistribute no record-level data, and
> publish no raw review text or user fields. If that is the right reading, a one-line confirmation
> is all I need and I will not trouble you further.
>
> Thank you for making these datasets available — the Clothing Fit data in particular is the only
> public source I know of that pairs a structured fit judgement with body measurements.
>
> With thanks,
> Tarık Sahar

### 1.5 Record of correspondence

| Date | Direction | Summary |
|---|---|---|
| — | — | Nothing sent yet. |

### 1.6 If no reply arrives — decided in advance

Recorded now rather than discovered late.

- **After 4 weeks with no reply:** send one polite follow-up, logged in §1.5.
- **After 8 weeks with no reply:** treat the position as unresolved **permanently**. The
  conservative reading in §1.2 becomes final and is not revisited.
- **Consequence, accepted:** the §4.4 open-dataset deliverable ships as **aggregates only**. It is
  not silently dropped, and it is not silently expanded. The paper states that terms could not be
  established despite a documented request, and cites this file.
- Silence is **not** consent. An unanswered enquiry leaves the restriction in place; it does not
  lift it.

---

## 2. Access and collection

`DESIGN.md` §0.5 governs. In force and observed to date:

- **Mavi (Phase 0) is blocked** by a Cloudflare bot challenge. The block was **not circumvented and
  will not be.** No challenge solver, no replayed browser cookies, no fingerprint-impersonating
  client, no proxy rotation. The source is closed until written permission is obtained.
- All Amazon and McAuley Lab access is **read-only, stream-only** over HTTPS against published
  static files, single connection, sequential, with a descriptive User-Agent identifying the probe
  as an academic feasibility study.
- No dataset has been downloaded in full except the two Clothing Fit files, which are small,
  published for download, and retained as dated immutable snapshots under `data/raw/` per
  `DESIGN.md` §0.4.

A permission request to Mavi remains outstanding and is stronger once there is a finding to point
at; it is not yet sent.

---

## 3. Personal data

- Review data carries user identifiers. These are **hashed at ingest** and raw values are never
  written to disk. `review_id_hash` is SHA-256 over `user_id|asin|timestamp`, truncated to 16 hex
  characters, and is not reversible to a user identifier.
- No attempt is made, and none will be made, to re-identify any reviewer, to link reviewers across
  sources, or to infer any attribute of a named individual.
- The buyer-gender text filter (`src/analysis/buyer_gender.py`) infers a **statistical property of a
  review**, used only to flag rows whose garment-gender assignment may be wrong. It is never used to
  characterise a person, and its output is aggregate.
- Review text is analysed in bulk and published only as aggregate rates. The hand-labelling files
  contain raw text and are permanently git-ignored.
- Under KVKK and GDPR the lawful basis relied on is academic research on already-public data,
  processed in pseudonymised form and reported only in aggregate.

---

## 4. Research conduct

- `PREREGISTRATION.md` is frozen before estimation, and discloses in full what had already been
  observed when it was written — including a result whose sign runs against the hypothesis.
- All five refutation conditions in `PREREGISTRATION.md` §8 are published if met. A null result is
  a result.
- Amendments to the pre-registration are dated, reasoned, and state whether any estimate had been
  run at the time.
