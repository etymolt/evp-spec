# EVP-0001: The five canonical axes

| | |
|---|---|
| **Status** | Stable |
| **Author** | Etymolt, `hello@etymolt.com` |
| **Created** | 2026-06-10 |
| **Last updated** | 2026-06-10 |

## Summary

EVP/1 verdicts MUST contain exactly five axes: **trademark, domain, cultural, sound, pronunciation**. The five-axis taxonomy is the load-bearing structural decision of the protocol.

## Motivation

A clearance verdict is a multi-dimensional signal. Reducing it to a single score loses information; expanding it to N axes per issuer makes verdicts incomparable across issuers. Five axes is the minimum count that captures the substantive dimensions a brand-name decision touches: legal (trademark), digital presence (domain), market reception (cultural), memorability (sound), usability (pronunciation).

## Specification

A conformant verdict MUST include the `axes` object with these five keys exactly:

```json
{
  "axes": {
    "trademark":     { "status": "...", "score": 0-1, "confidence": 0-1 },
    "domain":        { "status": "...", "score": 0-1, "confidence": 0-1 },
    "cultural":      { "status": "...", "score": 0-1, "confidence": 0-1 },
    "sound":         { "status": "...", "score": 0-1, "confidence": 0-1 },
    "pronunciation": { "status": "...", "score": 0-1, "confidence": 0-1 }
  }
}
```

Additional axes MAY appear under a `axes_extension` key (reserved for future EVPs).

## Rationale

Three axes is too few (always missing one of memorability/usability/digital). Seven or more invites issuer-specific axes that don't compare. Five maps cleanly to the founder mental model of "is this name safe to use, available, memorable."

## Reference implementation

`api.etymolt.com/v1/verify` returns exactly these five.

## Compatibility

Locked in v1.x. Adding or removing an axis requires a major-version bump.
