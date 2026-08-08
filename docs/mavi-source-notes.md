# Mavi — source notes (collection blocked)

Verified in Phase 0 by live browser inspection, August 2026. Recorded so nothing has to be
rediscovered if access is restored. **Do not attempt automated collection** — see §5 and
`DESIGN.md` §0.5.

---

## 1. Reviews endpoint

```
GET https://www.mavi.com/customerReview/review/{productCode}
    ?hasMediaOnly=false&sort=DESC&sortField=creationtime&currentPage=0&pageSize=200
```

Plain JSON, no authentication, no special headers. `pageSize=200` returns all reviews of a typical
product in a single request. `pageSize=1` returns `pagination.totalNumberOfResults` — a cheap count
probe. Works for arbitrary product codes. History observed February 2021 → May 2026.

Response: `{ results: [...], sorts: [...], pagination: {...} }`

### Field status (n = 254 reviews across 20 products)

| Field | Status | Note |
|---|---|---|
| `productSize` | usable | purchased size |
| `percentageSizeRating` | usable | `{0,25,50,75,100}`; **0 = not answered** (§3) |
| `rating` | usable | 1–5 stars |
| `textDate` | usable | Turkish date string |
| `reviewDisplayStatus` | usable | fit-answered flag, not moderation (§4) |
| `comment` | sparse | non-empty in ~22% |
| `percentageLengthRating` | unusable | identical to `percentageSizeRating` in 163/163 |
| `sizeRating`, `lengthRating` | unusable | always null |
| `id`, `alias`, `principal` | unusable | always null — no dedup key, no user id |
| `user` | partial | always 2 characters (initials); hash on ingest |

No natural primary key. Deduplicate on a hash of
`(productCode, user, textDate, rating, productSize, percentageSizeRating)`.

After every fetch, assert `len(results) == pagination.totalNumberOfResults`.

---

## 2. Product page

```
GET https://www.mavi.com/p/{productCode}
```

Slug not required. Nothing on this page needs JavaScript.

### 2.1 Metadata block

Server-rendered into raw HTML as a JavaScript object literal. Anchor the parser on
`'pagetype': 'product',`.

```js
'pagetype': 'product',
'prodid': '065574-620',          // colour variant
'baseProduct': '065574',         // style  <- clustering unit
'pname': "Beyaz Basic Tişört",
'pvalue': '369.99',              // current price
'p_actual_price': '369.99',      // list price -> discount = difference
'theme': ["Yeni Sezon", "Back to School"],
'waist': "",
'fit': "Slim Fit / Dar Kesim",   // cut
'cuff': "",
'zipOrButton': "Düğmesiz",
'CD_Color': "Beyaz",
'pcat': "Tişört",                // category
'psubcat': "Basic",
'pgender': "Erkek",              // gender
'sleeve': "Kısa Kol",
'otherinfo': [...]
```

**Coverage, 60 random products:** `prodid`, `baseProduct`, `pname`, `pvalue`, `p_actual_price`,
`pgender`, `pcat`, `psubcat` all 100%. `CD_Color` 93%. `fit` 70% overall but **26/26 = 100% within
adult target categories** — misses are accessories, socks, bags, cosmetics.

The breadcrumb (`Anasayfa | Kadın | Jean | New York`) carries gender and category redundantly; use
as a cross-check in tests.

Jeans carry a richer cut descriptor than tops — `Straight, Yüksek Bel, Düz Paça` (cut + rise + leg)
versus a single `Slim Fit / Dar Kesim`. Granularity is not comparable across categories.

### 2.2 Per-SKU stock block

Also in raw HTML, as an array of variant objects:

```json
{
  "id": "8682067073979",          // EAN barcode — stable primary key
  "colourVariant": "065574-620",
  "averageSizeRating": "",        // never populated (0 of 269 SKUs)
  "averageLengthRating": "",      // never populated
  "size": "XXXL",                 // for jeans: waist
  "length": "",                   // for jeans: inseam
  "price": "",                    // always empty; use pvalue instead
  "stockLevel": 6,                // min(actual, 6) — right-censored
  "stockLevelStatus": "inStock"
}
```

One women's jean yielded 110 SKUs (16 waists × 7 inseams). Size buttons are absent from raw HTML —
they are rendered client-side from this array. Parse the array, not the DOM.

`stockLevel` is capped: across 60 sampled products observed values were `{0,2,3,4,5,6}` and the
maximum never exceeded 6. Interpretation: `0` = sold out (exact), `1–5` = exact remaining units,
`6` = "six or more", censored. Model as right-censored survival data. The informative region —
approaching stockout — is the uncensored one.

---

## 3. `percentageSizeRating = 0` means "not answered"

Confirmed four independent ways:

1. **Widget marker geometry.** The on-page fit bar's marker measured in pixels as a fraction of bar
   width. Pilot product: marker at 50.0%, where the non-zero median is 50 and the with-zeros mean
   would be 24.5. Second product: marker at 75.7%, where the non-zero mean/median is 75 and the
   with-zeros mean would be 52.5.
2. **All-zero product.** A product whose 7 reviews were all `0` rendered the marker at −24.3%,
   entirely off the bar. If `0` were "very tight" it would sit at 0%, the left end.
3. **`reviewDisplayStatus`.** `disp == false ⟺ pct == 0` in 240/254 (94%).
4. **Star profile.** The zero bucket's mean star rating (3.93) resembles the overall population,
   not an extreme group.

Scale: `{0 = missing, 25 = tight, 50 = ideal, 75 = wide, 100 = very wide}`.

Effective response rate on the fit question is roughly 45%, and it varies sharply by cell — see
`DESIGN.md` §5.2.

---

## 4. `reviewDisplayStatus` is the fit-answered flag

Distribution across 254 reviews: 147 `true`, 107 `false`. Coincides with `pct != 0` in 94% of
cases. **Not a moderation flag** — there is no hidden layer of suppressed reviews and no unseen
selection. Useful as a redundant missingness indicator; flag the ~6% where the two disagree.

---

## 5. Catalogue, size chart, store stock

**Catalogue.** `sitemap.xml` is an index. The `Product-tr-TRY-*.xml` entry is listed over `http://`
and must be rewritten to `https://` or the fetch fails. Counts: 5,629 product URLs → 5,629 colour
variants → 3,582 styles.

Do not use category listing pages: they render tiles client-side (raw HTML yielded 2 codes), and
`robots.txt` disallows the filtered category URLs.

Filtering is mandatory. The catalogue spans 28+ categories including Beauty, Cüzdan, Çanta, Çorap,
Aksesuar, Plaj, and children's products (`Kız Çocuk`, `Erkek Çocuk`).

**No published size chart.** `/beden-tablosu` is a marketing page — zero `<table>` elements in raw
HTML and after client-side rendering, no `Göğüs` or `Kalça` measurements, no size-chart image, no
iframe, 6,736 characters of prose. No size-guide link or modal on product pages either.

The only route to a label→centimetre mapping is the per-product model measurements
(*"Boy: 189 cm / Bel: 78 cm / Göğüs: 94 cm / Kalça: 88 cm, Üst: L, Alt: Bel 32"*), which is the
brand asserting "this body wears L". Coverage of that field is **untested**.

**No per-store stock.** The store locator exposes a province/district selector and these endpoints:

```
GET /magazalar/get/districts?provinceCode=P_ISTANBUL
GET /magazalar/get-stores?province=&district=&size=&length=&barcode=&page=
```

But responses are byte-identical with and without `size`, `length` and `barcode` (19,856 bytes in
all three tests), and the response carries no stock field. The endpoint returns stores by location
only. A regional placebo test is not possible via this route.

---

## 6. The blocker

Every path except `robots.txt` returns HTTP 403 with `Cf-Mitigated: challenge` — Cloudflare serves
an interactive bot challenge to non-browser clients.

| Client | `/robots.txt` | `/p/{code}` | `/sitemap.xml` |
|---|---|---|---|
| urllib, descriptive UA | 200 | 403 | 403 |
| urllib, Chrome UA | 200 | 403 | 403 |
| urllib, full browser header set | — | 403 | 403 |
| urllib, no User-Agent | — | 403 | 403 |
| curl (independent TLS stack) | 200 | 403 | 403 |
| Real browser | 200 | 200 | — |

Ruled out: User-Agent, header set, TLS fingerprint, scheme, host variant, path. Unknown paths
return 403 rather than 404, confirming the challenge fires at the edge before the origin.

Phase 0 succeeded because it ran through a live browser session holding a `cf_clearance` cookie.

`robots.txt` is byte-for-byte unchanged and still permits `/p/`, `/customerReview/` and `/medias/`.
**This is not a policy change; it is edge bot management refusing a client fingerprint.** That
distinction matters for a permission request: the ask is not for an exception to Mavi's stated
policy, it is to let through a crawl their own policy already allows.

Wayback Machine was checked: no `sitemap.xml` snapshot exists and `/p/` CDX results are 2014-era
category URLs. Coverage nil.

**`robots.txt` as recorded:**

```
User-agent: *
Disallow: /search/
Disallow: /login
Disallow: /checkout
Disallow: /cart
Disallow: /my-account
Disallow: /*?q=*
Disallow: /*?_gl=*
Disallow: /*?f=*
Allow: /*/jean/*?q=*fit*
```

No `Crawl-delay` specified. Phase 0 saw no throttling at 2–4 req/s over ~180 requests; production
should still start at 1 req/s.
