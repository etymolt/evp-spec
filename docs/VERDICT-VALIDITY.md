# Verdict Validity — Temporal Semantics

> **A verdict is a snapshot, not a guarantee.** It reflects the records of record at `issued_at`. The underlying landscape — trademark filings, domain registrations, cultural denylists — can change at any moment.

This document explains the temporal-validity model for EVP/1 verdicts and the rules every conformant consumer MUST follow when rendering one.

## Half-life per axis

Each of the five canonical axes decays at a different rate:

| Axis | Typical half-life | Why |
|---|---|---|
| `domain` | **minutes to seconds** | Anyone can register an available domain immediately after verdict issuance. Adversarial speed; the verdict's domain claim is the fastest-decaying signal. |
| `trademark` | **hours to days** | National registries index new filings within ~24h (USPTO TRTDXFAP daily refresh; EUIPO live API near-real-time; UKIPO + WIPO Madrid weekly). |
| `cultural` | **months to years** | Cultural-conflict databases evolve slowly. The famous-marks denylist is revised quarterly. |
| `sound` | **stable** | Phonetic structure is intrinsic to the name; the underlying heuristic is rule-based and doesn't drift. |
| `pronunciation` | **stable** | English-orthography rules are stable; the heuristic is deterministic. |

A verdict's effective freshness window is bounded by its **fastest-decaying axis**. For most verdicts that's `domain` (minutes) or `trademark` (hours).

## Wire-format fields

EVP/1 verdicts carry three temporal-validity fields:

```jsonc
{
  "issued_at": "2026-06-10T14:22:01.413Z",        // when issued (existing, §3)
  "valid_until": "2026-06-11T14:22:01.413Z",      // when consumers MUST treat as historical (§11)
  "axis_freshness": {                              // per-axis "data last refreshed" (§11.2)
    "trademark":     "2026-06-10T12:00:00Z",
    "domain":        "2026-06-10T14:21:55Z",
    "cultural":      "2026-05-15T00:00:00Z",
    "sound":         null,                         // null = stable, no refresh notion
    "pronunciation": null
  },
  "re_verification_recommended_at": "2026-06-10T20:22:01Z"  // softer guidance, §11.3
}
```

- `valid_until` is the **issuer-recommended hard staleness boundary**. Past this, consumers MUST surface a staleness banner. Default: `issued_at + 24h`.
- `axis_freshness[<axis>]` is the timestamp of the underlying data the axis was computed against, when meaningful. `null` indicates a stable/non-refreshing axis.
- `re_verification_recommended_at` is the **soft re-verification guidance**, typically the earliest among per-axis freshness deltas. Consumers SHOULD prompt the user to re-verify at or after this time.

## Consumer rendering rules (normative)

A conformant consumer:

1. **MUST surface a "valid as of `issued_at`" indicator** alongside the verdict label and score. This is the table-stakes temporal clarity.
2. **MUST surface a staleness banner** when the current time exceeds `valid_until`. Suggested text: *"This is a historical verdict. The trademark and domain landscapes may have changed. Re-verify for current state."*
3. **SHOULD surface per-axis freshness** when a value is present and the time delta from now exceeds 1 hour. Suggested form: *"Trademark data refreshed 2h ago"*.
4. **SHOULD provide a clear "Re-verify" affordance** in the rendering surface, especially when `current_time >= re_verification_recommended_at`.
5. **MUST NOT alter `issued_at` or `valid_until`** on re-rendering. These fields are immutable post-issuance and are part of the signed payload.

A consumer that renders a verdict more than 24 hours after `issued_at` without the staleness banner is **non-conformant** with EVP/1.

## Permalinks

The permalink route `/v/<verdict_id>` is a **historical artifact by design**. It always shows the verdict as issued, frozen at `issued_at`. Consumers viewing a permalink MUST:

- Render the original verdict content.
- Render the staleness banner if `now > valid_until`.
- Provide an affordance to re-verify the same name against the current state (which produces a NEW verdict with a new `verdict_id`, not an update to the historical one).

## What this means for naming

A verdict says *"as of right now, here is what the records show."* It does not say *"this name will remain safe to use."* For names entering production use, re-verification within the issuer-recommended window — and continuous monitoring beyond that — is the operating posture.

## Bureau Model alignment

The temporal-validity model is consistent with the Bureau Model (§5.2): a verdict issuer reports on records of record at a moment in time. A credit bureau's report from last week does not certify your creditworthiness today; an EVP/1 verdict from last week does not certify your name's safety today. Both are point-in-time reports.

## Continuous monitoring

Where a one-shot verdict is insufficient — for names already adopted in commerce, names under active trademark prosecution, or portfolios watched by counsel — continuous monitoring services are out of scope for the spec but are a natural product layer above it. A monitoring service can re-issue EVP/1 verdicts on a cadence and emit signed deltas when an axis status changes. The wire format supports this without modification.
