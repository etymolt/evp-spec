# Why temporal validity?

A plain-language explainer of why every EVP/1 verdict carries timing metadata, and why consumers MUST render it.

## A verdict is a snapshot

When you ask "is this name safe to use?", the only honest answer is "as of this moment, here is what the records show." The trademark and domain landscapes change continuously:

- **Domain** registrations are real-time. Someone can buy `yourname.com` between the moment Etymolt's verdict says "available" and the moment you click "register." This half-life is minutes-to-seconds.
- **Trademark** filings appear in registries within hours of submission (USPTO TRTDXFAP refreshes daily; EUIPO is near-real-time). A name that was clear yesterday may have a new application against it today.
- **Cultural** databases evolve over months. The famous-marks denylist is revised quarterly. Half-life: months-to-years.
- **Sound** and **pronunciation** are essentially stable. The underlying heuristics don't drift.

A verdict's effective freshness window is bounded by its fastest-decaying axis. For most verdicts, that's domain (minutes) or trademark (hours).

## What the temporal-validity fields mean

EVP/1 verdicts carry three temporal-validity fields:

```jsonc
{
  "issued_at":   "2026-06-10T14:22:01.413Z",
  "valid_until": "2026-06-11T14:22:01.413Z",
  "axis_freshness": {
    "trademark":     "2026-06-10T12:00:00Z",   // 2h before issuance — fast-refreshing registry
    "domain":        "2026-06-10T14:21:55Z",   // 6s before issuance — real-time RDAP query
    "cultural":      "2026-05-15T00:00:00Z",   // 26 days before issuance — quarterly database
    "sound":         null,                      // null = stable, no refresh notion
    "pronunciation": null
  }
}
```

- **`issued_at`** is when the verdict was signed. Immutable.
- **`valid_until`** is the issuer-recommended hard staleness boundary. Default is `issued_at + 24h`. Past this, consumers MUST mark the verdict as historical.
- **`axis_freshness`** is the timestamp of the underlying data each axis was computed against. `null` for stable axes.

## The consumer's job

A consumer rendering an EVP/1 verdict — Etymolt's own homepage, a third-party SDK output, a Claude tool result, an enterprise integrator's dashboard — MUST:

1. **Surface "valid as of `issued_at`"** alongside the verdict label. Not buried in a footer. Above the score, ideally.
2. **Render a staleness banner** when `current_time > valid_until`. Suggested copy: *"This is a historical verdict. The trademark and domain landscapes may have changed. Re-verify for current state."*
3. **Surface per-axis freshness** when meaningful — typically when the delta between `axis_freshness[axis]` and `current_time` exceeds an hour.
4. **Provide a "Re-verify" affordance.** Users shouldn't have to leave your surface to get a fresh verdict.
5. **NOT alter `issued_at` or `valid_until`** on re-rendering. They're signed; modifying them invalidates the signature.

## What happens to permalinks

The `permalink` field on a verdict (`/v/<verdict_id>`) is a historical artifact by design. It always shows the verdict as issued, frozen at `issued_at`. Visiting a permalink a week later should:

- Render the original verdict content (unchanged).
- Render the staleness banner.
- Offer to re-verify the same name against current state (producing a NEW verdict with a new `verdict_id`).

The historical permalink is what gets cited in legal filings, due-diligence binders, and audit trails. The new verdict is what a founder acts on today.

## The business case

The temporal-validity story is what unlocks the recurring-revenue layer above EVP/1. A one-shot verdict tells you "as of right now." Continuous monitoring tells you "we'll re-issue and notify you when an axis changes." Monitoring services like Markify, BrandShield, and Compumark charge enterprise prices for exactly this loop. The EVP/1 wire format supports it without modification — a monitor is just a periodic re-issuer that emits signed deltas.

For Etymolt, this is the natural evolution from "$499 one-shot dossier" to "$99/month per watched name."
