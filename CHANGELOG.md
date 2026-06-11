# Changelog


### Axis vocabulary realignment (conscious revision)

The draft v1.0.0 schema enumerated the five canonical axes as
`trademark` / `domain` / `distinctiveness` / `linguistic` / `cultural`,
with §516 stating the names "MUST NOT change." This revision changes
two of those names while the spec is in public comment:

  - `distinctiveness` → `sound_symbolism`
  - `linguistic`      → `pronunciation`

Reason: the production engine has emitted `sound_symbolism` and
`pronunciation` as the per-axis scoring vocabulary since 2026-Q1.
The v1.0.0 draft's abstract category names (`distinctiveness` /
`linguistic`) never matched what the API actually scored — they were
aspirational supercategories that would have required a separate
projection layer to translate the engine's per-axis output. Rather
than ship that projection layer (and the test surface it would need)
under launch pressure, the spec is being brought into line with the
operational vocabulary while public comment is still open.

This is a CONSCIOUS revision, not drift. It is published here and
flagged so spec readers see a deliberate change rather than a hidden
inconsistency.

### Axis value shape — int OR object (v1.0 dual form)

The schema now accepts each axis as either:
  - **integer 0-100** — terse v1.0 default form (the live API surface today)
  - **object** with status/score/findings/evidence_of_record — v1.1+
    structured form, recommended for verdicts downstream agents will
    reason over.

v1.1 will likely tighten this to object-only with a deprecation
window for the integer form.

## [1.1.0] — 2026-06-10

### Changed (BREAKING for v1.0.0 draft consumers — additive for live API consumers)

- Composite verdict label moved from 4-value (`PASS` / `DECIDE` / `BLOCK` / `INSUFFICIENT_SIGNAL`) to **3-value** (`PROCEED` / `PROCEED_STRATEGIC` / `ABANDON`).
  - The v1.0.0 schema (`spec/evp-1.schema.json`) already encoded the 3-value enum — this changelog entry catches SPEC.md up to the schema.
  - Founder ruling 2026-06-10 supersedes Karthik's Option C 6-1 board ruling (which proposed additive `verdict_summary` alongside the 5-value engine field). The canonical surface is now 3-value end-to-end.
- New `status` field on the verdict envelope: `"complete"` | `"partial"`. `partial` replaces the v1.0.0 top-level `INSUFFICIENT_SIGNAL` semantics. Per-axis `INSUFFICIENT_SIGNAL` is UNCHANGED.
- New `reason` field on the verdict envelope: stable closed-set sub-code (`clean` | `famous_mark` | `high_collision` | `no_distinctiveness` | `descriptive` | `insufficient_corpus`).
- New `verdict_legacy` OPTIONAL field for back-compat with the v1.0.0 5-state engine vocabulary.

### Migration

| v1.0.0 draft           | v1.1.0 canonical          | status      | reason                  |
|------------------------|---------------------------|-------------|-------------------------|
| PASS                   | PROCEED                   | complete    | clean                   |
| DECIDE                 | PROCEED_STRATEGIC         | complete    | high_collision          |
| BLOCK                  | ABANDON                   | complete    | famous_mark             |
| INSUFFICIENT_SIGNAL    | (best estimate)           | partial     | insufficient_corpus     |

Issuers SHOULD ship `verdict_legacy` populated with the v1.0.0 4-value label during the transition window (through 2026-08-10) so consumers built against the v1.0.0 draft can dispatch on both.
All notable changes to the Etymolt Verdict Protocol specification are
documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project's versioning aims for [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
applied to a specification rather than a software library:

- **MAJOR** versions (1.0.0 → 2.0.0) introduce normative breaking changes.
  An implementation conformant to a major version is NOT guaranteed to
  validate documents issued under a different major version.
- **MINOR** versions (1.0.0 → 1.1.0) add backwards-compatible normative
  capability (new optional fields, new enum values declared as extension,
  new conformance tests).
- **PATCH** versions (1.0.0 → 1.0.1) are editorial: clarifications,
  typos, broken-link fixes, expanded examples. No conformance changes.

## [Unreleased]

## [1.0.1] — 2026-06-10

### Changed (NORMATIVE)

- §3.4 verdict taxonomy reduced from 4-value (`PASS`/`DECIDE`/`BLOCK`/`INSUFFICIENT_SIGNAL`) to 3-value: `PROCEED` / `PROCEED_STRATEGIC` / `ABANDON`. Per Etymolt board ruling 2026-06-10 §7.2. The 4-value model was aspirational; the 3-value model aligns with the live API, all reference SDKs (`@etymolt/sdk` v0.2.0, `etymolt` v0.2.0), and the user-facing verdict UX.
- New required field `status: "complete" | "partial"` — absorbs the prior `INSUFFICIENT_SIGNAL` semantics, distinguishing verdict from data-quality.
- New optional field `reason: string` — sub-codes preserving granularity (`clean`, `coexistence_required`, `hard_blocker`, `no_workaround`, `insufficient_signal`).

### Conformance

Test fixtures B.1–B.4 updated. Sample verdicts rebased to new enum.



Comments received during the public-comment period (2026-06-10 →
2026-09-10) are landed against this section. Editorial corrections roll
forward into the next patch release; normative changes accepted for the
next minor release are tagged `[accepted-for-1.1]` here and shipped in
1.1.0.

## [1.0.0] — 2026-06-10

Initial public comment release.

### Added

- The normative wire format for an EVP/1 verdict envelope (§3, §4).
- The five-axis taxonomy: trademark, domain, distinctiveness, linguistic,
  cultural (§4.1 — §4.5).
- The composite verdict taxonomy: `PASS`, `DECIDE`, `BLOCK`,
  `INSUFFICIENT_SIGNAL` (§3.4).
- The per-axis status taxonomy: `CLEAR`, `CAUTION`, `BLOCKED`,
  `INSUFFICIENT_SIGNAL`, `UNKNOWN` (§3.5).
- The `disclaimer` field requirement (§5) — every consumer that surfaces
  a verdict MUST surface the disclaimer verbatim. This is the Bureau
  Model anchor.
- Ed25519 detached signature protocol over a JCS-canonicalized payload
  (§6.1 — §6.3, RFC 8032 + RFC 8785).
- Key rotation specification (§6.4): 90-day cadence, 7-day overlap window,
  dual-signature pattern during overlap, key-revocation list at a
  well-known URL, JWKS-style discovery.
- Conformance test vector inventory (§8.3) covering valid, invalid, and
  edge cases for issuers and consumers.
- Four worked sample verdicts in Appendix B:
  - B.1 PASS  (`Inkstack`) — the canonical "ship it" example.
  - B.2 DECIDE (`Stratagem`) — the canonical "judgment call" example.
  - B.3 BLOCK (`Sigil`) — the canonical "do not use" example.
  - B.4 INSUFFICIENT_SIGNAL — the canonical "we cannot tell" example,
    drawn from a live Etymolt API response.
- JSON Schema (Draft 2020-12) as Appendix A and as a standalone file at
  `spec/evp-1.schema.json`.
- Reference validator (`EVP-1-validator-tests.py`) with 20 conformance
  tests covering all four sample verdicts, six invalid cases, six edge
  cases, and four lifecycle conformance checks (key rotation overlap
  window, key revocation, unknown key id, signature expiry).

### Why a single release at 1.0.0

EVP/1 ships at 1.0.0 — not 0.x — because the spec is intended to be
implemented against, not iterated against. A 0.x label invites
implementers to wait for "the real release"; that delays adoption and
delays the network effects this protocol depends on. The 90-day open
comment period is the iteration cycle. Normative changes accepted during
that period land in 1.1.0.

### Changes since 2026-06-05 internal draft

These are documented here for transparency; they do not affect any
implementation already targeting the 2026-06-05 draft, since that draft
was internal.

1. Appendix B gained a fourth sample (§B.4) for the
   `INSUFFICIENT_SIGNAL` case. Implementations relying on Appendix B
   inventory should pull in B.4.
2. §6.4 (key rotation) was materially tightened: rotation cadence, 7-day
   overlap window, dual-signature pattern during overlap, key-revocation
   list at `/.well-known/evp-keys-revoked.json`, and JWKS-style key
   discovery at `/.well-known/evp-keys.json` are now normative.
3. §8.3 gained an explicit `INSUFFICIENT_SIGNAL` acceptance test in the
   conformance test-vector inventory.

[Unreleased]: https://github.com/etymolt/evp-spec/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/etymolt/evp-spec/releases/tag/v1.0.0
