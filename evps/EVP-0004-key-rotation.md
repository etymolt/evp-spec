# EVP-0004: 90-day key rotation with 7-day overlap window

| | |
|---|---|
| **Status** | Stable |
| **Author** | Etymolt, `hello@etymolt.com` |
| **Created** | 2026-06-10 |
| **Last updated** | 2026-06-10 |

## Summary

EVP/1 issuers MUST rotate signing keys at least every 90 days. During rotation, a 7-day overlap window allows both the old and new key to issue valid signatures simultaneously, with all verdicts signed dual-signature.

## Motivation

Signing keys are long-lived assets that accumulate compromise risk over time. A 90-day rotation cadence is the SOC2/SLSA standard. The 7-day overlap window prevents a "all signatures invalid" failure mode that occurs when a consumer's cached key directory hasn't refreshed before the rotation.

## Specification

- **Cadence:** Each signing key has a `valid_from` and `valid_until` timestamp at the well-known key directory (`/.well-known/evp-keys.json`). `valid_until - valid_from` ≤ 90 days.
- **Overlap window:** When a new key becomes active, the previous key's `valid_until` MUST be at least 7 days after the new key's `valid_from`. During the overlap, verdicts MAY include a `signatures: [...]` array with both signatures; consumers accept verification under either key.
- **Revocation:** A revoked key is listed in `/.well-known/evp-keys-revoked.json` with a `revoked_at` timestamp. Verdicts issued after `revoked_at` under a revoked key are non-conformant.
- **Discovery:** The key directory follows JWKS-style conventions (RFC 7517 informational).

## Rationale

Dual-signature during overlap solves the "split-brain consumer" problem without requiring synchronized clock or coordinated cache flush. The 7-day window is long enough to ride out CDN caches, DNS TTLs, and weekend operator unavailability.

## Reference implementation

`api.etymolt.com/.well-known/evp-keys.json` and `api.etymolt.com/.well-known/evp-keys-revoked.json`.

## Compatibility

Tightening the rotation cadence (e.g., from 90 to 30 days) is additive. Loosening it (e.g., from 90 to 180 days) is a breaking change.
