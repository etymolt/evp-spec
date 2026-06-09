# EVP-0003: The Bureau Model and the verbatim disclaimer

| | |
|---|---|
| **Status** | Stable |
| **Author** | Etymolt, `hello@etymolt.com` |
| **Created** | 2026-06-10 |
| **Last updated** | 2026-06-10 |

## Summary

EVP/1 issuers operate under the **Bureau Model**: a verdict issuer reports on records of record at a point in time; the issuer does not opine on infringement; the issuer is not a law firm. The `disclaimer` field carries this framing verbatim and MUST be rendered by any consumer surface that exposes the verdict.

## Motivation

A clearance signal that gets confused with legal advice is dangerous. A verdict labeled "PROCEED" is not a license to commit; it is a signal that the records-of-record we consulted, at the time we consulted them, do not surface a blocking conflict. The Bureau Model framing makes this distinction load-bearing rather than buried in a footer.

The parallel to credit bureaus is intentional: a credit bureau reports on credit records (it does not extend credit, it does not opine on creditworthiness in any binding sense). An EVP/1 issuer reports on clearance records.

## Specification

The `disclaimer` field is a required string. Its exact contents are set by the issuer but MUST include:

1. The phrase "clearance signal, not legal advice" or substantively equivalent.
2. A direction to confirm with trademark counsel before adopting a name in commerce.
3. A reference to per-jurisdiction `coverage_caveat` for freshness windows.

The Etymolt canonical disclaimer is:

> "Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction."

Consumers rendering the verdict MUST render the disclaimer verbatim. Stripping it makes the rendering non-conformant.

## Rationale

The disclaimer is signed (it's part of the canonicalized payload). Stripping it would invalidate the signature, which is detectable. The combination of verbatim-render requirement + signed-disclaimer prevents the "summarize the verdict, lose the disclaimer" failure mode that's common in LLM-mediated surfaces.

## Reference implementation

Every Etymolt verdict carries the canonical disclaimer. Consumer rendering rules are spelled out in `docs/VERDICT-VALIDITY.md`.

## Compatibility

The disclaimer text is issuer-specific within the constraints above. Changing the required constraints is a major-version bump.
