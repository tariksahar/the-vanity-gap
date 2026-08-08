# Section 7.3 — collection blocked, power calculation delivered

**Date:** 2026-08-07
**Scope:** DESIGN.md section 7.3 (volume count and power calculation)
**Outcome:** volume count **blocked**; power calculation **delivered under sweep**

---

## 1. Summary

The catalogue build and the review-count probe could not be run. Every mavi.com
path except `robots.txt` now returns HTTP 403 with `Cf-Mitigated: challenge` —
Cloudflare serves an interactive bot challenge to non-browser clients. Passing it
is out of scope by policy and by section 0.6.

The power calculation was built and run anyway, parameterised on Phase 0's
measurements rather than on a full census. Its conclusion is decision-relevant on
its own: **section 5.16's stated MDE of 0.15 SD is the best case, not the
expected case.** Under realistic clustering and skew assumptions the MDE is
0.20–0.37 SD.

---

## 2. The blocker, characterised

`robots.txt` returns 200 and is byte-for-byte identical to the copy in section 6.
The crawl policy has not changed. The block is not a policy change; it is edge
bot-management.

| Client | `/robots.txt` | `/p/{code}` | `/sitemap.xml` |
|---|---|---|---|
| urllib, descriptive UA | 200 | 403 | 403 |
| urllib, Chrome UA | 200 | 403 | 403 |
| urllib, full browser header set | — | 403 | 403 |
| urllib, no User-Agent | — | 403 | 403 |
| curl (independent TLS stack) | 200 | 403 | 403 |
| Real browser | 200 | 200 | — |

Response evidence on the 403:

```
Cf-Mitigated: challenge
Server: cloudflare
Content-Security-Policy: ... https://challenges.cloudflare.com ...
<title>Just a moment...</title>
```

Ruled out as causes: User-Agent string, `Accept*` headers, TLS fingerprint
(curl fails identically), protocol scheme, host variant (`mavi.com` vs
`www.mavi.com`), and path (`/sitemap.xml`, `/p/`, `/customerReview/` all fail
alike; unknown paths return 403 rather than 404, confirming the challenge fires
at the edge before the origin is consulted).

`robots.txt` passes because Cloudflare serves it from the edge without invoking
the challenge, not because it is whitelisted for us.

### Why Phase 0 succeeded

Phase 0 was conducted by live browser inspection. A real browser session holds a
`cf_clearance` cookie and passes the challenge transparently. The section 0.6
premise — *"every data source needed by this project is reachable with plain
HTTP"* — was an inference from browser-based observation, and it does not hold
for an automated collector.

### Alternative sources checked and rejected

- **Wayback Machine.** No snapshot of `sitemap.xml` or `www.mavi.com/sitemap.xml`
  exists. The CDX index for `mavi.com/p/*` returns two pages of results, almost
  all 2014–2015 category URLs, not product pages. Coverage is nil.

### What was confirmed as still valid

- `robots.txt` matches section 6 exactly.
- The pilot product `065574-620` is unchanged: 163 reviews, `Slim Fit / Dar
  Kesim`, 369.99 TL.
- The section 7.11 model-measurements field is present and matches the documented
  format: `Boy: 189 cm / Bel: 78 cm / Göğüs: 94 cm / Kalça: 88 cm, Üst: L,
  Alt: Bel 32`.

---

## 3. Power calculation

### 3.1 Method

The estimand is a 2x2 difference in differences over gender x body-half. Its
variance is the sum of four cell-mean variances, so with `fit_score` normalised
to unit standard deviation:

```
Var(tau) = sum_k  DEFF_k / usable_k
MDE      = (z_0.975 + z_0.80) * sqrt(Var(tau))
```

Clustering enters through the design effect. Because review counts are heavily
right-skewed (section 5.9), the equal-size Kish factor understates it; the
unequal-cluster form is used:

```
DEFF = 1 + ((CV^2 + 1) * m_bar - 1) * ICC
```

`m_bar = 20` raw reviews per style (5,629 variants / 3,582 styles = 1.57 variants
per style, times 12.7 reviews per variant).

Two parameters are unknown and are swept rather than guessed:

- **ICC** — intra-style correlation of `fit_score`. Swept 0.02 / 0.05 / 0.10.
- **CV** — coefficient of variation of review counts per style. Swept 0 (equal)
  / 1.0 / 2.0 (heavy skew, consistent with the observed 163 / 89 / 15 / 4 / 3 / 1
  spread).

Response rates come from the measured section 5.4 table, collapsed to gender x
body-half: men 0.37, women/upper 0.67, women/lower 0.61.

### 3.2 Design effect

| ICC | CV=0 | CV=1 | CV=2 |
|---|---|---|---|
| 0.02 | 1.38 | 1.78 | 2.98 |
| 0.05 | 1.95 | 2.95 | 5.95 |
| 0.10 | 2.90 | 4.90 | 10.90 |

The skew is expensive. At ICC 0.05, going from equal cluster sizes to CV=2
triples the design effect — that is a factor of 1.75 on the standard error, paid
purely for the shape of the review distribution.

### 3.3 MDE, in SD units of `fit_score`

**Even split across the four cells** (what section 5.16 implicitly assumes):

| ICC | CV=0 | CV=1 | CV=2 |
|---|---|---|---|
| 0.02 | 0.110 | 0.125 | 0.161 |
| 0.05 | 0.130 | 0.160 | 0.228 |
| 0.10 | 0.159 | 0.207 | 0.308 |

**Phase 0 observed proportions** (27% of reviews are men's):

| ICC | CV=0 | CV=1 | CV=2 |
|---|---|---|---|
| 0.02 | 0.132 | 0.150 | 0.195 |
| 0.05 | 0.157 | 0.194 | 0.275 |
| 0.10 | 0.192 | 0.250 | 0.372 |

**Thin men's-jean cell** (men/lower = 5% of the pool):

| ICC | CV=0 | CV=1 | CV=2 |
|---|---|---|---|
| 0.02 | 0.161 | 0.183 | 0.237 |
| 0.05 | 0.192 | 0.236 | 0.335 |
| 0.10 | 0.234 | 0.304 | 0.453 |

### 3.4 Findings

**1. The 0.15 SD figure in section 5.16 is the optimistic corner.** It is
recovered only under an even cell split with low ICC and no skew. The realistic
central band is **0.20–0.30 SD**. Section 5.16 should be corrected — it currently
reads as an expected value and is being used to justify deferring Phase 5.

**2. The binding constraint is cell imbalance, not total volume.** Total usable
observations are roughly 17,000 in every scenario, yet the MDE moves by a factor
of 1.5 between them. A DiD is governed by its smallest cell. Adding observations
to the women's arm — already 73% of the pool — buys almost nothing.

**3. The men's lower-body cell is the whole design's weak point, and Phase 0 has
zero measurements on it.** Men's jean reviews did not appear once in the
254-review sample. That cell is the placebo anchor of section 1.5: if it is
thin, the identifying comparison is thin, regardless of how large the corpus is.
Men also answer the fit question least often (37%), so the cell is penalised
twice. **The single most valuable number still missing is the men's-jean review
count**, and it is a cheap measurement — a few hundred probes, not 5,629.

**4. Differential non-response costs more than it appears.** Men's 37% response
against women's ~64% means men contribute roughly 0.58 usable observations per
raw review compared to women. This compounds directly with finding 2.

**5. Reaching 0.15 SD by adding brands is expensive.** At ICC 0.05 and CV 2.0 it
needs about 15,100 raw reviews *per cell* — around 60,000 total, against Mavi's
estimated 30,700. That is roughly a second and third brand, assuming they are
comparable in size and that brand heterogeneity adds no noise. It does add noise.

### 3.5 What this means for scope

Detecting a **moderate** effect (0.25–0.30 SD) on Mavi alone is feasible if the
men's cells are not badly thin. Detecting a **small** effect (≤0.15 SD) is not
feasible on Mavi alone under any realistic parameter combination.

The literature does not pin down the expected magnitude. So the honest reading:
the study is adequately powered for the effect size the hypothesis implies if
that effect is large enough to matter substantively, and underpowered for a
subtle one. This does not by itself force Phase 5 ahead of Phase 4 — but it
removes section 5.16's grounds for treating the volume question as settled.

**Caveats.** ICC and CV are swept, not measured; the true values are unknown
until real data exists. `m_bar` and the 30,700-review pool are extrapolations
from a 20-product sample. Style fixed effects absorb some between-style variance,
which makes the design effect here somewhat conservative. All of these resolve
with the census that is currently blocked.

---

## 4. Code

- `src/collect/http.py` — rate-limited fetcher, exponential backoff, brand-agnostic
- `src/adapters/mavi.py` — Mavi endpoints, metadata-block parser, scope filter
- `src/collect/catalog.py` — sitemap enumeration (written, blocked at runtime)
- `src/analysis/power.py` — MDE and design-effect functions
- `src/analysis/run_power_scenarios.py` — the sweep reproduced above

Raw capture: `data/raw/mavi/2026-08-07/robots.txt`

---

## 5. Open decisions

The census cannot proceed against mavi.com by automated HTTP. Options, in the
order they should be considered:

1. **Request access from Mavi.** A short written request for permission to
   collect public product and review data for academic research, ideally with
   institution affiliation. Slow and uncertain, but it is the only route that
   restores the original plan intact.
2. **Bring Phase 1 forward — it was already first.** ModCloth and RentTheRunway
   are static downloads with no collection risk. They deliver method validation,
   a partial upper/lower placebo test, and the within-person design that Mavi
   cannot support (section 5.5). They do not deliver the men's arm.
3. **Bring Phase 5 forward and re-anchor on a different retailer.** The
   architecture already assumes one adapter per brand. Requires per-brand
   endpoint discovery, and each candidate must be checked for both technical
   accessibility and its own crawl policy before any collection.

Nothing here changes the design. The estimand, the identification strategy and
the trap list all survive; only the acquisition path for one brand is closed.
