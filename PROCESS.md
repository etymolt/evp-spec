# EVP/1 Feature Life Cycle

This document defines the life cycle of any feature in EVP/1 — from initial proposal through final stable release. It complements [GOVERNANCE.md](./GOVERNANCE.md) (which defines who decides) by specifying how features advance through stages.

## States

```
┌──────────┐   ┌──────────┐   ┌───────────────┐   ┌────────┐   ┌────────────┐   ┌─────────┐
│ Concept  │ → │ Proposal │ → │ Experimental  │ → │ Stable │ → │ Deprecated │ → │ Removed │
└──────────┘   └──────────┘   └───────────────┘   └────────┘   └────────────┘   └─────────┘
```

## State definitions

### Concept

The feature is a thought, a discussion, an idea floated in an issue. No commitment to ship; no normative language; no test vectors.

**Advancement to Proposal:** the proposer writes a numbered EVP (Etymolt Verdict Proposal) document in `evps/` describing the feature, its motivation, the proposed wire-format changes, and at least one use case.

### Proposal

The feature has an EVP document in `evps/EVP-XXXX-name.md`. The proposal is open for community discussion via the PR adding the EVP. The proposer is responsible for maintaining the proposal as discussion evolves.

**Advancement to Experimental:** the editor accepts the proposal. The EVP is merged. The feature is added to the spec under a clearly-labeled experimental section. The JSON Schema is updated with the new fields marked `"x-experimental": true`. At least one reference implementation (Etymolt's own) implements the feature.

### Experimental

The feature ships in the spec, but consumers MUST NOT rely on its stability. The schema accepts inputs with and without the feature. The feature can be modified or removed without a major-version bump.

**Advancement to Stable:** at least **three independent implementations** support the feature; **at least four months** of experimental status have elapsed; no blocking concerns from the comment-period intake; the editor confirms the wire-format and semantics are settled.

### Stable

The feature is normative. Consumers may rely on it. Removal requires a major-version bump (e.g., 1.x → 2.0). Modifications require a minor-version bump (e.g., 1.1 → 1.2) and a deprecation cycle.

**Stability guarantees:**

| Within 1.x | Allowed? |
|---|---|
| Add a new optional field | Yes (minor bump) |
| Add a new required field | No (breaking; major bump only) |
| Remove a stable field | No (deprecation cycle first) |
| Change the semantics of a field | No (breaking) |
| Tighten a validation constraint | Case-by-case (treat as breaking if any existing valid input now fails) |
| Loosen a validation constraint | Yes (additive) |
| Add a new optional axis | Yes (minor bump) |
| Add a new required axis | No (breaking; the five axes are locked in 1.x) |

### Deprecated

The feature is still supported, but a successor exists or planned removal is announced. Consumers SHOULD migrate.

**Advancement to Removed:** at least one major-version cycle has passed since deprecation began; the editor confirms no implementer is blocked on removal.

### Removed

The feature is gone. Consumers using it are non-conformant with the current version.

## Advancement criteria summary

| Stage | Implementations | Time | Editor approval |
|---|---|---|---|
| Concept → Proposal | 0 (just an EVP) | Any | None |
| Proposal → Experimental | 1 (reference) | After EVP merge | Yes |
| Experimental → Stable | 3 independent | ≥4 months | Yes |
| Stable → Deprecated | Successor or replacement exists | ≥1 release cycle | Yes |
| Deprecated → Removed | None depend on it | ≥1 major version | Yes |

## EVP document structure

Every EVP in `evps/EVP-XXXX-name.md` follows the template:

```markdown
# EVP-XXXX: <Short feature name>

| | |
|---|---|
| **Status** | Proposal / Experimental / Stable / Deprecated / Removed |
| **Author** | <name>, `<email>` |
| **Created** | YYYY-MM-DD |
| **Last updated** | YYYY-MM-DD |
| **Replaces** | None / EVP-YYYY |
| **Replaced by** | None / EVP-ZZZZ |

## Summary

One paragraph. What the feature is, why it exists.

## Motivation

What problem does this solve? What breaks without it?

## Specification

The normative wire-format and validation changes. Include JSON Schema diff if applicable.

## Rationale

Why this design? What alternatives were considered? Why not those?

## Reference implementation

Pointer to the reference implementation (in Etymolt's stack or elsewhere).

## Compatibility

How does this affect existing consumers? Is it additive or breaking?

## Open questions

Anything not yet decided. Resolved before advancement to Stable.
```

## EVP numbering

EVPs are numbered sequentially starting from `EVP-0001`. Numbers are assigned when the EVP enters Proposal state (i.e., when its file is merged to main). Withdrawn EVPs keep their number and are marked `Status: Withdrawn` rather than being deleted — preserves the historical record.

## The first 5 EVPs (anchor set)

These are the founding EVPs that retroactively document the 1.0.0 design decisions:

- **EVP-0001** — The five axes (trademark, domain, cultural, sound, pronunciation).
- **EVP-0002** — Ed25519 detached signatures over JCS-canonicalized payloads.
- **EVP-0003** — The Bureau Model and the verbatim disclaimer requirement.
- **EVP-0004** — 90-day key rotation with 7-day overlap window.
- **EVP-0005** — Temporal validity (`issued_at`, `valid_until`, `axis_freshness`).

These are in `evps/` as historical anchors. New work continues with EVP-0006.
