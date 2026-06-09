# EVP-0005: Temporal validity (`issued_at`, `valid_until`, `axis_freshness`)

| | |
|---|---|
| **Status** | Experimental (v1.1 candidate; Stable in v1.0 for `issued_at`) |
| **Author** | Etymolt, `hello@etymolt.com` |
| **Created** | 2026-06-10 |
| **Last updated** | 2026-06-10 |

## Summary

A verdict is a snapshot, not a guarantee. EVP/1 verdicts carry temporal-validity metadata so consumers can correctly mark stale verdicts as historical and re-verify when appropriate.

## Motivation

The trademark and domain landscapes change continuously. A verdict from a week ago may still be useful as a historical artifact but should not be presented to a user as "current state." Without explicit temporal-validity fields, consumers had no normative way to render a stale verdict differently from a fresh one.

## Specification

Three optional fields in v1.0; required in v1.1:

- **`issued_at`** (RFC 3339 timestamp, ms precision): when the verdict was issued. **Required in 1.0.**
- **`valid_until`** (RFC 3339 timestamp): issuer-recommended hard staleness boundary. Default: `issued_at + 24h`. **Recommended in 1.0; required in 1.1.**
- **`axis_freshness`** (object): per-axis "data last refreshed" timestamps. `null` for stable axes (sound, pronunciation). **Recommended in 1.0; required in 1.1.**
- **`re_verification_recommended_at`** (RFC 3339 timestamp): soft re-verification guidance. **Optional in both 1.0 and 1.1.**

Consumer rendering rules:

1. MUST surface "valid as of `issued_at`" alongside the verdict label.
2. MUST surface a staleness banner when `current_time > valid_until`.
3. SHOULD surface per-axis freshness when the delta exceeds 1 hour.
4. SHOULD provide a "Re-verify" affordance.
5. MUST NOT alter `issued_at` or `valid_until` on re-rendering.

## Rationale

Per-axis half-life varies dramatically: domain availability changes in minutes (adversarial speed); trademark filings appear in registries within hours-to-days; cultural databases evolve over months; sound/pronunciation are essentially stable. A single `valid_until` is correct as a coarse bound, but axis-level freshness is needed to communicate the actual signal stability.

See [`docs/VERDICT-VALIDITY.md`](../docs/VERDICT-VALIDITY.md) for the full half-life analysis.

## Reference implementation

Etymolt's homepage verdict card renders the "as of" indicator and the staleness banner. The wire-format fields are populated by `api.etymolt.com/v1/verify` as of v1.0.

## Compatibility

`issued_at` is stable in 1.0. The other three fields are experimental in 1.0 and advance to Stable in 1.1 conditional on the conformance criteria in [PROCESS.md](../PROCESS.md).

## Open questions

- Whether `valid_until` should be issuer-set or computed from a normative formula. Current: issuer-set.
- Whether `axis_freshness` should allow per-source granularity (e.g., trademark broken into USPTO/UKIPO/EUIPO) rather than per-axis. Current: per-axis only.
