# The Vanity Gap

**A clothing size label does not measure the body. It measures the desire — and the direction of
that desire is reversed by gender.**

---

## The question

Franz (2017, *JEBO*) documents size inflation in womenswear across 54 US retailers, and explains its
absence in menswear by asserting that **men do not care about the size label**. That is an
assumption, not a measured finding, and the reason it has never been tested is that the data to test
it does not exist in public form: the two clothing datasets with a structured fit field — ModCloth
and RentTheRunway — are **women-only**, and no menswear equivalent has been assembled.

This project argues that men do care about the label, in the opposite direction. The hypothesis is
that men whose true size is small tend to buy **up** — to appear larger on paper — while women above
a certain point tend to buy **down**. The state of public data is itself part of the argument: the
half of the question that contradicts Franz is unmeasured because nobody built the dataset.

## Identification, in three sentences

The obvious objection is that if small sizes sell poorly there may simply be few slim men — body
distribution, not behaviour. The answer is that the same man's waist is not a different size from
his torso: in trousers the waist is a binding constraint, in a t-shirt it is not, so if the deviation
appears in upper-body garments and vanishes in lower-body garments for the same population in the
same season, the body-distribution explanation collapses. That upper-versus-lower contrast is a
placebo test, it is differenced again across genders to give the estimand, and it is strengthened by
a predicted dose-response ordering — t-shirt (no constraint) > shirt (collar and sleeve) > jeans
(waist must fit).

The estimand:

```
tau = ( E[fit_score | men,   upper] - E[fit_score | men,   lower] )
    - ( E[fit_score | women, upper] - E[fit_score | women, lower] )
```

estimated as one regression with an interaction term and style-level fixed effects, with standard
errors clustered at the style level.

## Status

| Phase | State |
|---|---|
| Phase 0 — Turkish retailer feasibility | Complete. Collection **blocked** by a bot challenge; not circumvented, and will not be. |
| Power analysis | Complete. Realistic MDE 0.20–0.30 SD. |
| Phase 1 — Amazon Reviews'23 probe | Complete. `Clothing_Shoes_and_Jewelry` carries the primary estimand; purchased size is structurally absent from the corpus. **Precision measurement outstanding.** |
| Phase 1b — self-reported size deviation | Complete. Direct observation of the hypothesis exists at 0.20% of reviews (~131k corpus-wide), but the men's lower-body cell is too thin for it to be primary. |
| Phase 2a — dictionary validation | Complete. 46,223 ground-truth comparisons against ModCloth and RentTheRunway. Two pattern families carry nearly all the error. |
| Phase 2b — women's arm estimator | Not started. |
| Phase 3 — men's arm | Not started. This is the destination. |
| Pre-registration | **Not yet written.** No estimation happens before it exists. |

Findings and their reasoning live in [`docs/`](docs/). The two worth reading first are
[`docs/phase1-amazon-probe.md`](docs/phase1-amazon-probe.md) and
[`docs/phase2-dictionary-validation.md`](docs/phase2-dictionary-validation.md).

[`docs/phase2-divergence-precommitment.md`](docs/phase2-divergence-precommitment.md) was written
**before** the validation was run, and fixes in advance how a disagreement between the two
validation routes would be interpreted. Its commit predates the results it governs; that is the
point of it.

## Reproducing the probes

Python 3.11+. No third-party packages are required — the probes read published `.jsonl` over HTTPS
line by line and stop at the requested count. `datasets` is used if installed, but its script-based
loader path no longer works with `datasets` 5.x, so the HTTPS fallback is the supported route.

```bash
python amazon_fit_probe.py --category Clothing_Shoes_and_Jewelry --reviews 50000 --items 30000
```

Draw the hand-labelling sample for the precision measurement:

```bash
python amazon_fit_probe.py --precision-sample --category Clothing_Shoes_and_Jewelry --sample-items 200000 --sample-reviews 300000 --per-stratum 50
```

Probe explicit self-reported size deviation — reviewers who state both their usual size and the size
they bought:

```bash
python size_deviation_probe.py --reviews 800000 --items 250000
```

Validate the fit dictionary against structured ground truth. This one needs the two Clothing Fit
snapshots in `data/raw/` first; see the licensing note below:

```bash
python src/analysis/validate_dictionary.py
```

Nothing above writes to a source you do not control, and nothing downloads a corpus in full. Where
collection is permitted at all, the rule is one request per second, exponential backoff, a
descriptive User-Agent, and `robots.txt` respected. Where a source blocks automated access, the
source is closed until written permission is obtained.

## Data and licensing

**No data is committed to this repository, and none will be.** `data/` is git-ignored in its
entirety.

Both upstream datasets carry **no licence statement of any kind** — not a permissive licence, not a
restrictive one. The Amazon Reviews'23 HuggingFace page and the McAuley Lab Clothing Fit
distribution page each state only a request to cite the associated paper. Absent an affirmative
grant, redistribution of derived records is not authorised by default. Consequently:

- Aggregated results and code are publishable, and are what this repository contains.
- Raw review text and any user field are never published.
- The planned open-dataset deliverable is **aggregates only** unless and until the licence position
  is resolved in writing with the upstream authors.
- User identifiers are hashed at ingest; raw identifiers are not written to disk.

`data/processed/precision_sample.csv` contains raw review text for local hand-labelling and is
permanently git-ignored, including after it is labelled. Only the resulting precision *rates* are
publishable.

## Sources

- Franz, N. (2017). Economics of vanity sizing. *Journal of Economic Behavior & Organization*.
- Chattaraman, V., Simmons, K. P., & Ulrich, P. V. (2013). *Clothing and Textiles Research Journal*.
  Their prediction — deviation increasing with body size — is the direct rival to this one, and is
  set up here as a head-to-head rather than as related work.
- Misra, R., Wan, M., & McAuley, J. (2018). Decomposing fit semantics for product size
  recommendation in metric spaces. *RecSys*. (ModCloth, RentTheRunway)
- Hou, Y. et al. (2024). Bridging language and items for retrieval and recommendation.
  (Amazon Reviews'23)
