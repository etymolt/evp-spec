# Changelog

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
  new conformance tests). They MAY narrow an underspecified area when the
  narrowing is published deliberately as part of the public-comment
  cycle.
- **PATCH** versions (1.0.0 → 1.0.1) are editorial: clarifications,
  typos, broken-link fixes, expanded examples. No conformance changes.

## [Unreleased]

Comments received during the public-comment period (2026-06-10 →
2026-09-10) are landed against this section. Editorial corrections roll
forward into the next patch release; normative changes accepted for the
next minor release are tagged `[accepted-for-1.2]` here and shipped in
1.2.0.

## [1.1.0] — 2026-06-10

This release reconciles three deliberate revisions that the v1.0.0 draft
left underspecified or aspirational. Each is published here, with
reasoning, so spec readers see a CONSCIOUS revision rather than a hidden
inconsistency or implementation drift.

### Changed (NORMATIVE — additive for live API consumers, BREAKING for v1.0.0 draft consumers)

**1. Three-value composite verdict.**

The composite verdict label moves from the v1.0.0 4-value taxonomy
(`PASS` / `DECIDE` / `BLOCK` / `INSUFFICIENT_SIGNAL`) to the **3-value**
canonical: `PROCEED` / `PROCEED_STRATEGIC` / `ABANDON`.

- The v1.0.0 schema (`spec/evp-1.schema.json`) already encoded the
  3-value enum — this changelog entry catches `SPEC.md` up to the schema
  and the live API.
- Founder ruling 2026-06-10 supersedes the Karthik Option-C 6–1 board
  ruling that proposed an additive `verdict_summary` alongside a
  5-value engine field. The canonical surface is now 3-value end-to-end.

**2. Axis vocabulary realignment — `distinctiveness` → `sound_symbolism`, `linguistic` → `pronunciation`.**

The v1.0.0 draft schema enumerated the five canonical axes as
`trademark` / `domain` / `distinctiveness` / `linguistic` / `cultural`,
with §516 stating the names "MUST NOT change." This revision changes two
of those names while the spec is in public comment:

- `distinctiveness` → `sound_symbolism`
- `linguistic` → `pronunciation`

Reason: the production engine has emitted `sound_symbolism` and
`pronunciation` as the per-axis scoring vocabulary since 2026-Q1. The
v1.0.0 draft's abstract category names (`distinctiveness` / `linguistic`)
never matched what the API actually scored — they were aspirational
supercategories that would have required a separate projection layer
to translate the engine's per-axis output. Rather than ship that
projection layer (and the test surface it would need) under launch
pressure, the spec is being brought into line with the operational
vocabulary while public comment is still open.

This is a CONSCIOUS revision, published deliberately. It is the precise
opposite of drift: the engine was right, the draft taxonomy was the
out-of-date layer, and the public-comment window is the correct moment
to reconcile.

**3. Per-axis value shape — `integer` OR `object` (deliberate dual form).**

Each axis value now accepts either:

- **integer 0–100** — terse v1.0 default form (the live API surface
  today).
- **object** with `status` / `score` / `findings` / `evidence_of_record`
  — v1.1+ structured form, recommended for verdicts that downstream
  agents will reason over.

The dual form is published in v1.1.0 as a permanent, deliberate
affordance — not a transitional accommodation. v1.2 may tighten this
to object-only with a deprecation window for the integer form once the
SDK ecosystem has converged. Until then, both shapes are normative.

**4. New verdict-envelope fields.**

- `status: "complete" | "partial"` — REQUIRED. Absorbs the v1.0.0
  top-level `INSUFFICIENT_SIGNAL` semantics, distinguishing verdict
  from data-quality. Per-axis `INSUFFICIENT_SIGNAL` is UNCHANGED.
- `reason: string` — REQUIRED. Stable closed-set sub-code:
  `clean` | `famous_mark` | `high_collision` | `no_distinctiveness` |
  `descriptive` | `insufficient_corpus`.
- `verdict_legacy: string` — OPTIONAL. Back-compat slot for issuers
  that still need to emit the v1.0.0 5-state engine vocabulary while
  consumers catch up.

### Migration

| v1.0.0 draft           | v1.1.0 canonical          | status      | reason                  |
|------------------------|---------------------------|-------------|-------------------------|
| `PASS`                 | `PROCEED`                 | `complete`  | `clean`                 |
| `DECIDE`               | `PROCEED_STRATEGIC`       | `complete`  | `high_collision`        |
| `BLOCK`                | `ABANDON`                 | `complete`  | `famous_mark`           |
| `INSUFFICIENT_SIGNAL`  | (best-effort estimate)    | `partial`   | `insufficient_corpus`   |

Issuers SHOULD populate `verdict_legacy` with the v1.0.0 4-value label
during the transition window (through 2026-08-10) so consumers built
against the v1.0.0 draft can dispatch on either field.

### Conformance

- Test fixtures B.1–B.4 updated to the 3-value enum + new envelope fields.
- New conformance vector `int-or-object/01-integer-form.json` exercises
  the integer per-axis shape.
- New conformance vector `int-or-object/02-object-form.json` exercises
  the object per-axis shape.
- Reference validator (`EVP-1-validator-tests.py`) and live conformance
  one-liner (post-deploy smoke against `api.etymolt.com/v1/verify`) both
  pass against the 1.1.0 schema. Soak verified 2026-06-11.

## [1.0.1] — 2026-06-10

Editorial superseded by 1.1.0. Retained for diff archaeology only.

## [1.0.0] — 2026-06-10

Initial public-comment release.

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
- Key rotation specification (§6.4): 90-day cadence, 7-day overlap
  window, dual-signature pattern during overlap, key-revocation list at
  a well-known URL, JWKS-style discovery.
- Conformance test vector inventory (§8.3) covering valid, invalid, and
  edge cases for issuers and consumers.
- Four worked sample verdicts in Appendix B (B.1 PASS `Inkstack`,
  B.2 DECIDE `Stratagem`, B.3 BLOCK `Sigil`, B.4 INSUFFICIENT_SIGNAL).
- JSON Schema (Draft 2020-12) as Appendix A and as a standalone file at
  `spec/evp-1.schema.json`.
- Reference validator (`EVP-1-validator-tests.py`) with 20 conformance
  tests covering all four sample verdicts, six invalid cases, six edge
  cases, and four lifecycle conformance checks.

### Why a single release at 1.0.0

EVP/1 ships at 1.0.0 — not 0.x — because the spec is intended to be
implemented against, not iterated against. A 0.x label invites
implementers to wait for "the real release"; that delays adoption and
delays the network effects this protocol depends on. The 90-day open
comment period is the iteration cycle. Normative changes accepted during
that period land in 1.1.0.

[Unreleased]: https://github.com/etymolt/evp-spec/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/etymolt/evp-spec/compare/v1.0.0...v1.1.0
[1.0.1]: https://github.com/etymolt/evp-spec/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/etymolt/evp-spec/releases/tag/v1.0.0
