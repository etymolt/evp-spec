# EVP-0002: Ed25519 detached signatures over JCS-canonicalized payloads

| | |
|---|---|
| **Status** | Stable |
| **Author** | Etymolt, `hello@etymolt.com` |
| **Created** | 2026-06-10 |
| **Last updated** | 2026-06-10 |

## Summary

Every EVP/1 verdict is signed with an Ed25519 detached signature over the JCS-canonicalized (RFC 8785) representation of its payload. Consumers verify the signature against the issuer's published public key.

## Motivation

A verdict that can be silently modified after issuance has no provenance. Without verifiability, the Bureau Model collapses — issuers cannot be held accountable for what they signed, and consumers cannot prove they rendered the original verdict.

Ed25519 (RFC 8032) gives short keys, fast verification, no per-message nonce concerns, and broad implementation maturity. JCS (RFC 8785) gives a deterministic JSON serialization independent of whitespace, key order, and number representation.

## Specification

- **Signature algorithm:** Ed25519 (RFC 8032).
- **Canonicalization:** JCS (RFC 8785) applied to the entire verdict object **except** the `signature`, `signature_key_id`, and `signature_payload_digest` fields, which are stripped before canonicalization.
- **Digest:** SHA-256 of the canonicalized bytes, recorded in `signature_payload_digest` (hex).
- **Signature encoding:** Base64-encoded raw 64-byte Ed25519 signature in `signature`.
- **Key identifier:** Issuer-stable string in `signature_key_id` (e.g., `etymolt-1779085662`).

## Rationale

Detached signatures over canonicalized payloads is the same pattern used by sigstore, in-toto, and JWS unencoded payload. It composes cleanly with the JSON Schema validation: schema first, signature second.

## Reference implementation

`EVP-1-validator-tests.py` includes a complete verification routine.

## Compatibility

Changing the signature algorithm or canonicalization scheme is a major-version bump.
