# Etymolt Verdict Protocol (EVP/1)

| Field | Value |
|---|---|
| **Title** | Etymolt Verdict Protocol, Version 1 |
| **Short name** | `evp/1` |
| **Version** | 1.0.0 |
| **Status** | Public Comment (final-review candidate for board go/no-go 2026-06-08) |
| **License** | Creative Commons Attribution 4.0 International (CC-BY-4.0) |
| **Date** | 2026-06-10 |
| **Editor** | Etymolt Inc. (Dear One Technologies Pvt Ltd) |
| **Contact** | `hello@etymolt.com` |
| **Canonical URL** | `https://etymolt.com/docs/verdict-protocol` |
| **Source repository** | `https://github.com/etymolt/evp-spec` |
| **Comment period** | 2026-06-10 through 2026-09-10 (90 days) |

**Normative references.**

- RFC 2119 — *Key words for use in RFCs to Indicate Requirement Levels.*
- RFC 8174 — *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.*
- RFC 8259 — *The JavaScript Object Notation (JSON) Data Interchange Format.*
- RFC 8032 — *Edwards-Curve Digital Signature Algorithm (EdDSA)*, §5.1 Ed25519.
- RFC 8785 — *JSON Canonicalization Scheme (JCS).*
- RFC 3339 — *Date and Time on the Internet: Timestamps.*
- RFC 5785 — *Defining Well-Known Uniform Resource Identifiers.*
- RFC 7517 — *JSON Web Key (JWK)* (informational; structural analogue for the EVP key directory).
- JSON Schema Draft 2020-12 — *JSON Schema: A Media Type for Describing JSON Documents.*
- Nice Classification, 12th Edition (WIPO) — *International Classification of Goods and Services.*

**Status of this document.** This document is a public-comment release of the Etymolt Verdict Protocol, Version 1. It is published at `https://etymolt.com/docs/verdict-protocol` under the Creative Commons Attribution 4.0 International license. Comments MAY be submitted as issues to the public repository (Appendix C, §C.4) through the close of the open comment period. A reviewer SHOULD treat this v1.0 document as final pending the close of public comment; only editorial corrections are expected before tag.

**Changes since 2026-06-05 draft.** (Editorial — does not change conformance posture for implementations already targeting the draft.)

1. Appendix B gains a fourth sample verdict (§B.4) for the `INSUFFICIENT_SIGNAL` composite case, drawn from the live Etymolt API response for the candidate `"Stratagem"` on 2026-06-05.
2. §6.4 (key rotation) is materially tightened: rotation cadence, 7-day overlap window, dual-signature pattern during overlap, key-revocation-list endpoint, and JWKS-style discovery are now specified normatively.
3. §8.3 gains an explicit `INSUFFICIENT_SIGNAL` acceptance test in the conformance test-vector inventory.

---

## Abstract

The Etymolt Verdict Protocol (EVP/1) is an open data-interchange specification for **brand-name clearance verdicts** issued by automated services to humans, language models, and software agents. A verdict is a structured, signed assertion about whether a candidate name is safe to adopt across five canonical axes — trademark, domain, distinctiveness, linguistic, and cultural — derived from public registries and authoritative third-party data sources. Each verdict carries a deterministic `verdict_id`, a verbatim disclaimer that downstream user interfaces MUST surface, optional per-axis evidence of record, and an Ed25519 signature that allows any third party to verify the verdict originated unmodified from its issuer. EVP/1 defines the JSON object shape, the status taxonomy for each axis, the conformance criteria for implementations, and the signature and key-rotation protocol. EVP/1 does NOT define how a clearance signal is computed, what data sources MUST be consulted, or any legal opinion: it specifies only the contract between a verdict producer and a verdict consumer. The protocol is intended to make brand-name clearance signals portable, auditable, and interoperable across the AI-naming ecosystem.

---

## 1. Introduction

### 1.1 What is a verdict

A *verdict*, as defined by this specification, is a structured machine-readable assertion about a candidate brand name across five canonical axes. A verdict is not a recommendation, an endorsement, an opinion, or legal advice. A verdict is a clearance signal: it reports what authoritative registries, lexicons, and probes say about a candidate at a specific moment in time. A consumer of a verdict — whether human, language model, or autonomous agent — uses the verdict to make a decision; the verdict itself does not make the decision.

### 1.2 Why a standard

Brand-name generation has become instantaneous: any modern language model produces dozens of candidate names from a one-sentence brief in seconds. Verification has not kept pace. Founders, agents, and platforms still discover trademark conflicts, taken domains, and cultural collisions weeks or months after launch. Multiple verification services have begun emitting clearance signals in incompatible formats, with inconsistent semantics for terms such as `CLEAR`, `BLOCKED`, and `UNKNOWN`, and with no standard mechanism for cryptographic verification.

A common protocol allows:

- **Portability.** A verdict produced by one issuer can be consumed by any compliant client.
- **Auditability.** A verdict carries a deterministic identifier and a signature; a third party can verify that the verdict was issued unmodified.
- **Honest negative space.** A standardized `INSUFFICIENT_SIGNAL` status discourages issuers from over-claiming when authoritative data is unavailable.
- **Legal safety.** A canonical disclaimer field separates clearance signal from legal opinion across all conforming implementations.

### 1.3 What the protocol covers

EVP/1 defines:

1. The wire format of a verdict object (§3, Appendix A).
2. The five canonical axes and their status taxonomies (§4).
3. The disclaimer field and its surfacing requirements (§5).
4. The signature, key-rotation, and revocation protocol (§6).
5. The versioning and deprecation policy (§7).
6. The conformance criteria for implementations (§8).

### 1.4 What the protocol does not cover

EVP/1 does NOT define:

- *How* a clearance signal is computed. Issuers may use any methodology consistent with the surfaced evidence of record.
- *Which* registries MUST be consulted. Issuers MUST disclose which jurisdictions were consulted per verdict, but the protocol is jurisdiction-agnostic.
- *What price* a verdict commands. Commercial terms are out of scope.
- *Legal opinions.* No verdict is legal advice (§5).
- *Generation* of candidate names. Verdicts operate on a supplied name; they do not produce candidates.

### 1.5 Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC 2119 and RFC 8174.

---

## 2. Terminology

For the purposes of this document, the following terms are defined.

**verdict.** A structured JSON object conforming to §3 that asserts the clearance status of a candidate name across the five canonical axes (§4) at a specific moment in time.

**axis.** One of the five canonical clearance dimensions defined in §4: `trademark`, `domain`, `distinctiveness`, `linguistic`, `cultural`. An EVP/1 verdict MUST include exactly these five axes by these names.

**finding.** A discrete piece of evidence of record contributing to an axis status. A finding includes at minimum a source reference, a status contribution, and (where applicable) a deep link to the underlying record.

**status.** The qualitative classification of an axis. EVP/1 defines six status values: `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`, and (at the top-level verdict envelope only) `PROCEED` / `PROCEED_STRATEGIC` / `ABANDON` as composite verdict labels (3-value canonical 2026-06-10; founder ruling supersedes the 4-value PASS/DECIDE/BLOCK/INSUFFICIENT_SIGNAL set documented in the v1.0.0 draft).

  - **`CLEAR`** — Authoritative data was consulted; no conflict found. The axis is safe to rely on within the disclosed coverage.
  - **`CAUTION`** — Authoritative data was consulted; a non-blocking risk signal was found. The consumer SHOULD review the per-axis findings.
  - **`BLOCKED`** — Authoritative data was consulted; a determinate conflict was found. The consumer SHOULD NOT adopt the candidate without remediation.
  - **`INSUFFICIENT_SIGNAL`** — A consulted source did not return a determinate result. The axis is unverified. The consumer MUST NOT treat this as `CLEAR`.
  - **`UNKNOWN`** — The axis was not evaluated, or no source was consulted. Distinct from `INSUFFICIENT_SIGNAL`: `UNKNOWN` indicates absence of attempt; `INSUFFICIENT_SIGNAL` indicates attempt without determinate result.

**verdict_id.** A globally unique, opaque identifier assigned by the issuer to a single verdict. Conformant issuers SHOULD use the format `v_` followed by 12 or more URL-safe base64 characters. The `verdict_id` MUST be stable: refetching a verdict by `verdict_id` MUST return byte-equal content.

**signature.** An Ed25519 detached signature (RFC 8032 §5.1) over a canonicalized payload digest (§6).

**disclaimer.** A verbatim plain-text field (§5) asserting that the verdict is a clearance signal and not legal advice. Consumers MUST surface the disclaimer unmodified in any user interface that exposes the verdict.

**issuer.** The party that produces a verdict and signs it. The issuer is identified by `signature_key_id` and is responsible for key publication, rotation, and revocation (§6.4).

**consumer.** Any party that reads, displays, or acts on a verdict.

**coverage caveat.** A machine-readable note attached to an axis or finding indicating a known limitation of the underlying data — for example, that a registry mirror is partial or that a probe used a fallback method.

**key directory.** A JSON document published at a well-known URL (§6.4) listing an issuer's current and historical Ed25519 public keys with their `status`, `valid_from`, `valid_until`, and (where applicable) `revoked_at`.

**revocation list.** A JSON document published at a well-known URL (§6.5) enumerating `key_id` values that the issuer has revoked, with revocation timestamps and reasons.

**overlap window.** A bounded interval during which an issuer's old and new signing keys are both `active` and verdicts are signed under both keys, allowing consumers to update their cached key set without service disruption (§6.4.3).

---

## 3. Verdict object

A verdict is a JSON object (RFC 8259) conforming to the schema in Appendix A. This section describes the top-level fields and their semantics. Implementations SHOULD treat the JSON Schema in Appendix A as authoritative when the prose in this section is ambiguous.

### 3.1 Required top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `evp_version` | string | MUST | The EVP version. For this specification, the value MUST be `"1.0.0"`. |
| `name` | string | MUST | The candidate name evaluated. UTF-8. 1–64 graphemes. |
| `verdict` | string | MUST | The composite verdict label. One of `PROCEED`, `PROCEED_STRATEGIC`, or `ABANDON`. The companion `status` field (`complete` | `partial`) carries the engine's signal-sufficiency state (partial replaces the legacy `INSUFFICIENT_SIGNAL` at the top level). |
| `score` | integer | MUST | A composite score in `[0, 100]`. The interpretation of the score is issuer-defined but MUST be monotonic with respect to clearance favorability. |
| `axes` | object | MUST | An object containing exactly five keys: `trademark`, `domain`, `distinctiveness`, `linguistic`, `cultural`. Each value is an axis object (§4). |
| `verdict_id` | string | MUST | The verdict identifier (§2). |
| `issued_at` | string | MUST | RFC 3339 timestamp of verdict issuance, in UTC, with millisecond precision. |
| `disclaimer` | string | MUST | The verbatim disclaimer (§5). |
| `signature` | string | MUST | The Ed25519 signature (§6), base64-encoded. |
| `signature_key_id` | string | MUST | The key identifier corresponding to the public key that verifies `signature`. |
| `signature_payload_digest` | string | MUST | The hex-encoded SHA-256 of the canonicalized payload (§6.2). |

### 3.2 Recommended top-level fields

| Field | Type | Description |
|---|---|---|
| `one_line` | string | A single human-readable sentence summarizing the verdict. Useful for transcripts, Slack-style surfaces, agent outputs. |
| `findings` | array of string | A list of plain-language findings the consumer SHOULD review. |
| `confidence` | integer | A `[0, 100]` confidence score for the composite verdict. |
| `confidence_interval` | object | A `{lower, upper, point_estimate, method}` object describing uncertainty around `score`. |
| `axes_confidence` | object | Per-axis confidence and uncertainty drivers. |
| `recommended_actions` | array of object | Machine-readable next steps the consumer MAY surface. |
| `permalink` | string | A URL where a human-readable rendering of the verdict can be retrieved. |
| `jurisdictions_consulted` | array of string | The trademark jurisdictions actually consulted, in canonical short form (e.g., `"USPTO_bulk"`, `"EUIPO_live_API"`). |
| `signature_co` | object | OPTIONAL co-signature pair `{signature, signature_key_id, signature_payload_digest}` emitted during a key-overlap window (§6.4.3). |

### 3.3 Optional top-level fields

Issuers MAY include additional fields prefixed with `x_` (extension fields). Consumers MUST tolerate unknown fields. Consumers MUST NOT alter the semantics of standard fields based on extension fields.

### 3.4 Rationale

- The verdict envelope is intentionally flat. A nested envelope would complicate signature verification across implementations.
- The composite `verdict` label (`PROCEED` / `PROCEED_STRATEGIC` / `ABANDON`) is distinct from per-axis statuses to allow issuers to apply their own synthesis policy while keeping per-axis semantics standardized.
- When the underlying data is unavailable for a high-confidence composite verdict, conformant issuers MUST set `status: "partial"` alongside the best-estimate `verdict` value. The `status` field is the protocol's honest-negative-space surface (was `INSUFFICIENT_SIGNAL` at the top level in the v1.0.0 draft). Honest negative space is a load-bearing property of this protocol.
- The signature triple (`signature`, `signature_key_id`, `signature_payload_digest`) is denormalized so that consumers can verify without retrieving the original payload (§6).
- `signature_co` exists so consumers caching only one key during an overlap window can still verify verdicts signed under either key without a directory refetch.

---

## 4. The five canonical axes

EVP/1 defines exactly five axes. Conformant verdicts MUST include all five, in this order, with the keys `trademark`, `domain`, `distinctiveness`, `linguistic`, `cultural`. Each axis object MUST include a `status` field; other fields are axis-specific.

### 4.1 Trademark

**Definition.** Whether the candidate name conflicts with a registered or pending trademark in any consulted jurisdiction, including famous-marks catalogs and analogous registers.

**Status taxonomy.** `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN` as defined in §2.

**Recommended fields.**

| Field | Description |
|---|---|
| `status` | REQUIRED. |
| `jurisdictions_consulted` | RECOMMENDED. Array of registry short-names actually queried. |
| `colliding_marks` | RECOMMENDED. Array of objects describing each potential conflict: `{wordmark, owner, serial_number, registration_number, nice_classes, filing_date, status, deep_link}`. |
| `nice_classes_assumed` | RECOMMENDED. Array of integers. When the consumer did not supply Nice classes, the issuer SHOULD document which classes were assumed. |
| `coverage_caveat` | RECOMMENDED. Machine-readable note on data freshness or partial coverage. When `status == INSUFFICIENT_SIGNAL`, this field is REQUIRED. |

**Evidence of record requirements.** When an issuer returns `BLOCKED` for the trademark axis, the issuer MUST include at least one entry in `colliding_marks` with a deep link to the authoritative case-status record (e.g., USPTO TSDR). When an issuer returns `INSUFFICIENT_SIGNAL`, the issuer MUST include `coverage_caveat` describing why the signal was insufficient.

### 4.2 Domain

**Definition.** Whether at least one workable domain registration path exists for the candidate at standard registration price across the consulted TLDs and prefix patterns.

**Status taxonomy.** `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`.

  - `CLEAR` — At least one workable variant is available at standard registration price.
  - `CAUTION` — A workable variant exists only via prefix/suffix patterns; bare-name TLDs are taken.
  - `BLOCKED` — No workable variant exists at standard registration price across all consulted TLDs and patterns.
  - `INSUFFICIENT_SIGNAL` — Authoritative RDAP unreachable; only fallback methods (DNS, WHOIS) consulted.

**Recommended fields.**

| Field | Description |
|---|---|
| `status` | REQUIRED. |
| `tlds_consulted` | RECOMMENDED. Array of objects: `{tld, method, definitive, result}`. `method` SHOULD be one of `RDAP_authoritative`, `WHOIS_authoritative`, `DNS_fallback`. |
| `recommended_variant` | RECOMMENDED. Object describing the recommended registration path: `{domain, registrar, price_usd}`. |
| `aftermarket_observed` | RECOMMENDED. Boolean. If true, an aftermarket-priced listing exists for the bare name; the axis status MUST NOT be `CLEAR` solely on the basis of an aftermarket listing. |

**Evidence of record requirements.** Issuers MUST distinguish authoritative RDAP results from fallback methods via the `definitive` boolean per TLD entry. Issuers MUST NOT issue `CLEAR` for the domain axis when all consulted TLDs returned non-definitive results.

### 4.3 Distinctiveness

**Definition.** Whether the candidate is distinctive in a relevant brand-name cohort and in developer-handle namespaces. Captures collisions with venture-backed startup names, GitHub/npm/X handle takedown candidates, and generic-startup-suffix overcrowding.

**Status taxonomy.** `STRONG`, `MODERATE`, `WEAK`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`.

  - `STRONG` — Distinctive in consulted cohorts; bare handles available across required platforms.
  - `MODERATE` — Some near-collisions in cohort or some handles taken; workaround handle variants available.
  - `WEAK` — Multiple near-collisions; only obscure workaround handles available.
  - `BLOCKED` — Exact-collision with a registered venture-funded startup operating in the same category.
  - `INSUFFICIENT_SIGNAL` — Cohort lookup or handle probe failures prevented evaluation.

**Recommended fields.**

| Field | Description |
|---|---|
| `status` | REQUIRED. |
| `cohort_corpora_consulted` | RECOMMENDED. Array of corpus identifiers. |
| `platforms_consulted` | RECOMMENDED. Array of objects: `{platform, status, url, claimed}`. |
| `workaround_variants_available` | RECOMMENDED. Array of strings; available handle variants if bare is taken. |

**Evidence of record requirements.** When the status is `BLOCKED` on distinctiveness grounds, the issuer MUST cite the colliding entity by name and source.

### 4.4 Linguistic

**Definition.** Whether the candidate is pronounceable, phonotactically well-formed, and free of sound-symbolic anti-patterns across the consulted languages.

**Status taxonomy.** `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`.

The linguistic axis is **advisory** by default; conformant issuers SHOULD mark it as `advisory: true` in axis-level metadata. An advisory axis MAY influence `score` but SHOULD NOT, alone, drive a composite `BLOCK` verdict.

**Recommended fields.**

| Field | Description |
|---|---|
| `status` | REQUIRED. |
| `locales_evaluated` | RECOMMENDED. Array of BCP-47 locale tags. |
| `phoneme_skeleton` | OPTIONAL. The phonotactic encoding used for analysis. |
| `sound_symbolism_axes` | OPTIONAL. Per-axis scores (size, speed, softness, warmth, etc.). |
| `advisory` | RECOMMENDED. Boolean. SHOULD be `true` by default. |
| `method` | RECOMMENDED. Short descriptor of the analysis method (e.g., `"static rule-based heuristic"`, `"Whisper round-trip"`). |

**Evidence of record requirements.** Linguistic findings SHOULD cite the analysis method. When `INSUFFICIENT_SIGNAL`, the issuer MUST disclose which locales lacked coverage.

### 4.5 Cultural

**Definition.** Whether the candidate carries unintended meaning, taboo association, or sacred-name overlap in any consulted market.

**Status taxonomy.** `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`.

  - `CLEAR` — No matches in consulted lexicons, sacred-names catalogs, or LLM cross-cultural panel.
  - `CAUTION` — Soft flag: potential meaning collision in at least one market, non-blocking.
  - `BLOCKED` — Hard flag: profanity, regulated-category collision, sacred-name overlap.
  - `INSUFFICIENT_SIGNAL` — A market lacked coverage.

**Recommended fields.**

| Field | Description |
|---|---|
| `status` | REQUIRED. |
| `sources_consulted` | RECOMMENDED. Integer count of distinct sources. |
| `cultural_sources_consulted` | RECOMMENDED. Array of objects: `{source, matched, language, caveat}`. |
| `markets_covered` | RECOMMENDED. Array of market codes. |

**Evidence of record requirements.** When the status is `BLOCKED` on cultural grounds, the issuer MUST cite the specific source and entry (e.g., a hurtlex row, a sacred-names catalog entry). When `INSUFFICIENT_SIGNAL`, the issuer MUST identify which markets lacked coverage in `cultural_sources_consulted`.

---

## 5. Disclaimer field

### 5.1 Requirement

Every conformant verdict MUST include a `disclaimer` field. The field MUST be a plain-text string. The field MUST be surfaced **verbatim** in any user interface, chat transcript, agent response, or downstream artifact that exposes the verdict to a human user. The disclaimer MUST NOT be stripped, paraphrased, translated, or truncated by intermediaries.

### 5.2 Rationale — the Bureau Model

EVP/1 adopts the **Bureau Model** legal posture: a verdict issuer reports on records of record (analogous to a credit bureau reporting on credit records); the issuer does not opine on infringement, does not recommend a course of action, and is not a law firm. The disclaimer is the load-bearing artifact that preserves this posture across all surfaces. An intermediary that strips the disclaimer breaks the contract between issuer and consumer and may expose itself to liability that the issuer disclaims.

### 5.3 Recommended boilerplate text

Conformant issuers SHOULD use the following text as the value of `disclaimer`:

> *Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction. The Bureau Model legal posture applies: we report what the records of record show; we do not opine on infringement.*

(The previous 3-sentence form — omitting the fourth Bureau Model posture sentence — is deprecated as of 2026-06-05 P0-1 reconciliation. New issuers MUST use the 4-sentence form above.)

Issuers MAY use alternate text provided the alternate text:

1. States that the verdict is a clearance signal, not legal advice.
2. Recommends confirmation with qualified counsel before commercial adoption.
3. References data freshness and coverage limitations.
4. States the Bureau Model posture (reports records of record; does not opine on infringement).

### 5.4 Surfacing requirements

Conformant consumers MUST:

- Display the disclaimer in any human-readable rendering of the verdict, above the fold or at first scroll.
- Preserve the disclaimer verbatim across translations of surrounding UI chrome. The disclaimer itself MAY be translated only if the translation is approved by the issuer.
- Include the disclaimer in any export format (PDF, CSV, JSON, image) where the verdict content is reproduced.

Conformant consumers MUST NOT:

- Hide the disclaimer behind a "show more" interaction by default.
- Replace the disclaimer with a shorter "TL;DR" paraphrase.
- Treat the disclaimer as decorative metadata.

---

## 6. Signature and verifiability

### 6.1 Algorithm

Conformant verdicts MUST be signed with Ed25519 (RFC 8032 §5.1). Ed25519 is mandated for its deterministic signatures, small key and signature sizes, and broad ecosystem support.

### 6.2 Canonicalized payload

The signature is computed over a SHA-256 digest of a canonicalized payload. The canonicalized payload is the verdict object with the following fields REMOVED:

- `signature`
- `signature_key_id`
- `signature_payload_digest`
- `signature_co` (if present)
- All fields prefixed with `x_`

The remaining object MUST be serialized to JSON using **JCS** (JSON Canonicalization Scheme, RFC 8785) before hashing. The `signature_payload_digest` field MUST equal the hex-encoded SHA-256 of the canonicalized JSON bytes.

### 6.3 Verification protocol

A consumer verifies a verdict as follows:

1. Parse the verdict JSON.
2. Strip `signature`, `signature_key_id`, `signature_payload_digest`, `signature_co`, and any `x_*` fields.
3. Canonicalize the remaining object per RFC 8785.
4. Compute SHA-256 over the canonicalized bytes.
5. Compare the result to the value of `signature_payload_digest` from the original verdict. They MUST match.
6. Retrieve the Ed25519 public key corresponding to `signature_key_id` from the issuer's published key directory (§6.4).
7. Before trusting the key, the consumer MUST check that `signature_key_id` does NOT appear in the issuer's revocation list (§6.5) with a `revoked_at` timestamp earlier than or equal to `issued_at`. If it does, the verdict MUST be treated as untrusted.
8. Verify `signature` (base64-decoded) against the canonicalized payload using the public key.
9. If `signature_co` is present and the primary `signature_key_id` is unknown to the consumer's cache, the consumer MAY attempt verification against the co-signature key as a fallback before refetching the key directory (§6.4.3).

If any step fails, the verdict MUST be treated as untrusted.

### 6.4 Key publication and rotation

#### 6.4.1 Key directory

Issuers MUST publish their Ed25519 public keys at a well-known URL of the form:

```
https://<issuer-domain>/.well-known/evp-keys.json
```

The document MUST be a JSON object of the form (JWK-adjacent; see RFC 7517 for the analogous JOSE construction):

```json
{
  "evp_version": "1.0.0",
  "issuer": "etymolt.com",
  "keys": [
    {
      "key_id": "etymolt-1779085662",
      "alg": "Ed25519",
      "public_key_b64": "MCowBQYDK2VwAyEA...",
      "valid_from": "2026-06-10T00:00:00Z",
      "valid_until": "2026-09-08T00:00:00Z",
      "status": "active"
    },
    {
      "key_id": "etymolt-1786861662",
      "alg": "Ed25519",
      "public_key_b64": "MCowBQYDK2VwAyEA...",
      "valid_from": "2026-09-01T00:00:00Z",
      "valid_until": "2026-11-30T00:00:00Z",
      "status": "active"
    }
  ],
  "rotation_policy": {
    "cadence_days": 90,
    "overlap_days": 7,
    "dual_sign_during_overlap": true
  },
  "revocation_endpoint": "https://<issuer-domain>/.well-known/evp-keys-revoked.json"
}
```

The directory MUST be served with `Content-Type: application/json` and `Cache-Control: max-age=3600` or shorter. Consumers SHOULD respect the `Cache-Control` header and SHOULD NOT cache the directory longer than 24 hours regardless.

#### 6.4.2 Rotation cadence

- Conformant issuers MUST rotate signing keys at a stated cadence. The default and RECOMMENDED cadence is **90 days**. Issuers MAY adopt a shorter cadence; issuers SHOULD NOT exceed 180 days between rotations.
- The cadence MUST be declared in `rotation_policy.cadence_days` of the key directory.
- The rotation cadence is the maximum interval between a key's `valid_from` and the `valid_from` of its successor; it is not the key's lifetime.
- A key's `valid_until` MUST be greater than or equal to its `valid_from + cadence_days + overlap_days`.

#### 6.4.3 Overlap window and dual-signature pattern

To allow consumers to refresh cached keys without service disruption, every key rotation MUST include an **overlap window** during which both the outgoing key (`K_old`) and the incoming key (`K_new`) are simultaneously `active`. The default overlap is **7 days**. Issuers SHOULD NOT use an overlap shorter than 24 hours and SHOULD NOT exceed 30 days.

During the overlap window:

- Both keys appear in the key directory with `status: "active"`.
- The issuer MUST sign every verdict under `K_new` as the primary signature (`signature`, `signature_key_id`, `signature_payload_digest`) AND MUST include a co-signature under `K_old` in the `signature_co` field. This is the **dual-signature pattern**.
- Consumers that have cached `K_old` but not yet refreshed to discover `K_new` MAY verify against `signature_co` and treat the verdict as trusted.
- After the overlap window closes, the issuer MUST sign only under `K_new` and MUST omit `signature_co`. `K_old` transitions to `status: "retired"` (see §6.4.4).

A consumer SHOULD treat the presence of `signature_co` as a signal that a key rotation is in progress and SHOULD refresh the key directory at next opportunity.

```
Time   →  T-overlap        T0 (rotation)      T+overlap        T+overlap+1
K_old  →  active, signs ──┐                                    retired
                          ├─ overlap window: both active ─┐
K_new  →                  └─ active, dual-signs ────────────── active, signs alone
```

#### 6.4.4 Retired keys

A retired key's `status` MUST be set to `"retired"` and its `valid_until` MUST reflect the end of its signing lifetime. Verdicts issued under a retired key remain valid for verification purposes; new verdicts MUST NOT be issued under a retired key. Issuers MUST NOT remove a retired key from the published directory for at least **12 months** after its `valid_until` date, to allow consumers to verify historical verdicts.

#### 6.4.5 Discovery

Consumers SHOULD discover an issuer's key directory by:

1. Extracting the issuer's domain from the `signature_key_id` prefix (issuers SHOULD use `<short-domain>-<unix-timestamp>` as their key-id format) OR from the `issuer` field of a previously fetched directory OR from an explicit issuer-registry lookup (out of scope for v1.0).
2. Fetching `https://<issuer-domain>/.well-known/evp-keys.json` (RFC 5785 well-known URI).
3. Validating that the returned document's `issuer` field matches the expected domain.
4. Caching the directory under the response `Cache-Control` policy.

### 6.5 Key revocation

#### 6.5.1 Revocation list

An issuer MUST publish a revocation list at:

```
https://<issuer-domain>/.well-known/evp-keys-revoked.json
```

The endpoint is REQUIRED even if empty (in which case it returns `{"revoked": []}`). The document MUST be a JSON object of the form:

```json
{
  "evp_version": "1.0.0",
  "issuer": "etymolt.com",
  "generated_at": "2026-06-10T12:00:00Z",
  "revoked": [
    {
      "key_id": "etymolt-1774567890",
      "revoked_at": "2026-06-08T14:22:00Z",
      "reason": "key_compromise",
      "replacement_key_id": "etymolt-1779085662"
    }
  ]
}
```

The `reason` field SHOULD be one of `key_compromise`, `superseded`, `cessation_of_operation`, or `unspecified`.

#### 6.5.2 Revocation semantics

- A revoked `key_id` MUST also appear in `evp-keys.json` with `status: "revoked"` and a `revoked_at` field. The two documents MUST agree.
- A consumer encountering a verdict signed by a revoked key MUST treat the verdict as untrusted IF `verdict.issued_at >= revoked_at`. Verdicts issued strictly earlier than `revoked_at` MAY be treated as historically valid at the consumer's discretion, but consumers SHOULD treat them with reduced trust.
- Issuers MUST NOT remove an entry from the revocation list. Revocations are append-only.
- Consumers SHOULD poll the revocation list at least once per cached directory refresh and MUST poll it before treating a verdict signed by a key not previously seen.

#### 6.5.3 Compromise response

On confirmed key compromise, the issuer MUST:

1. Publish the revocation entry within 1 hour of confirmation.
2. Mark the key `status: "revoked"` in the directory within 1 hour.
3. Begin signing under a replacement key (a new active key, dual-signed during a compressed overlap window of up to 24 hours).
4. Publish a public incident notice at a stable URL within 24 hours.

#### 6.5.4 No CRL replay

Revocation entries are signed by the issuer at the transport layer (TLS) only; EVP/1 v1.0 does NOT mandate a separate revocation-list signature. Consumers MUST fetch the revocation list over HTTPS with certificate validation. A signed revocation envelope is a candidate addition for EVP/1.1.

---

## 7. Versioning

### 7.1 Semantic versioning

EVP follows Semantic Versioning 2.0.0. The current version is **1.0.0**.

- **Major version (X.0.0).** Breaking changes to the verdict shape, axis names, status taxonomy, or signature protocol. A consumer written against major version X is NOT required to parse version X+1 verdicts.
- **Minor version (1.X.0).** Backward-compatible additions: new optional fields, new RECOMMENDED but not REQUIRED behavior, new conformance test vectors. A consumer written against 1.X MUST tolerate 1.(X+1) verdicts.
- **Patch version (1.0.X).** Editorial corrections to this document only. No semantic change.

### 7.2 Compatibility guarantees

For all 1.X versions:

- The five axis names (`trademark`, `domain`, `distinctiveness`, `linguistic`, `cultural`) MUST NOT change.
- The status values `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN` MUST NOT change in meaning.
- The composite verdict values `PROCEED`, `PROCEED_STRATEGIC`, `ABANDON` MUST NOT change in meaning.
- The disclaimer requirement (§5) MUST be preserved.
- The signature protocol (§6) MUST be preserved.

### 7.3 Deprecation policy

A field marked `Deprecated` in a minor version:

- MUST continue to be emitted by conformant issuers for at least 12 months after the deprecating release.
- MUST be ignored, but tolerated, by conformant consumers after deprecation.
- MAY be removed in the next major version.

### 7.4 Pre-1.0 notice

Pre-1.0 drafts of this protocol are NOT covered by these guarantees. Implementations claiming `evp_version: "0.x.y"` are pre-release and SHOULD NOT be deployed in production.

---

## 8. Conformance

### 8.1 Definition of "EVP/1-compliant"

A producer implementation is **EVP/1-compliant** if and only if:

1. Every verdict it emits validates against the JSON Schema in Appendix A.
2. Every verdict includes a non-empty `disclaimer` meeting the criteria in §5.3.
3. Every verdict carries a valid Ed25519 signature verifying against a published key (§6).
4. The issuer publishes its public keys at the URL specified in §6.4.1 and its revocation list at the URL specified in §6.5.1.
5. The issuer follows the rotation cadence and overlap-window protocol of §6.4.2 and §6.4.3.
6. The implementation passes the conformance test vectors (§8.3), including the `INSUFFICIENT_SIGNAL` acceptance test.

A consumer implementation is **EVP/1-compliant** if and only if:

1. It parses verdicts strictly per Appendix A.
2. It tolerates unknown `x_*` extension fields.
3. It surfaces the `disclaimer` per §5.4 when displaying verdicts to a human.
4. It performs signature verification per §6.3 before treating a verdict as trusted.
5. It consults the revocation list per §6.5.2 before treating a verdict as trusted.
6. It tolerates minor-version increments without breakage.
7. It treats `INSUFFICIENT_SIGNAL` at the top level as distinct from `PASS`, `DECIDE`, and `BLOCK`, and MUST NOT silently coerce it into any of those values for display.

### 8.2 Compliance badge

Conformant implementations MAY display the EVP/1 compliance badge:

```
[![EVP/1](https://etymolt.com/docs/verdict-protocol/badge.svg)](https://etymolt.com/docs/verdict-protocol)
```

The badge SHOULD link to the canonical specification URL.

### 8.3 Test vectors

The repository at `https://github.com/etymolt/evp-spec` includes a `test_vectors/` directory containing:

- `valid/` — at least **13** verdicts that MUST validate, with expected signature verification results. The valid suite MUST include at least one verdict per composite-verdict label: `PASS`, `DECIDE`, `BLOCK`, and `INSUFFICIENT_SIGNAL`. The `INSUFFICIENT_SIGNAL` acceptance test (`valid/insufficient_signal_aiyana.json`) corresponds to Appendix §B.4 of this document and MUST be accepted by conformant consumers without coercion to any other composite label.
- `invalid/` — at least **12** verdicts that MUST be rejected, each annotated with the failure condition. The invalid suite MUST cover: missing required field, wrong enum value, malformed signature, schema-violating `axes` shape, expired-key signature, revoked-key signature, and digest mismatch.
- `canonicalization/` — JCS canonicalization fixtures covering Unicode normalization, number representation, key ordering edge cases, and `signature_co` strip behavior.
- `key_rotation/` — fixtures covering the 7-day overlap window: a verdict dual-signed under `K_old` and `K_new`, a verdict signed under `K_new` alone after overlap close, and a verdict signed under a revoked key.

A producer or consumer claiming EVP/1 compliance SHOULD execute the test vectors as part of its CI pipeline. The Etymolt reference test runner is published at `EVP-1-validator-tests.py` in the spec repository (a pytest suite over the JSON Schema in Appendix A and the test-vector inventory).

---

## 9. Security considerations

### 9.1 What EVP/1 prevents

- **Verdict tampering in transit.** The Ed25519 signature prevents an intermediary from altering verdict contents undetected.
- **Issuer impersonation (at the protocol layer).** A consumer that verifies signatures against the published key directory cannot be served a forged verdict by a malicious intermediary lacking the issuer's private key.
- **Disclaimer stripping by lazy intermediaries.** §5.4 makes disclaimer surfacing a conformance requirement, exposing intermediaries that strip the field.
- **Confident-but-wrong claims under data gaps.** The mandatory `INSUFFICIENT_SIGNAL` status discourages issuers from emitting `CLEAR` when underlying data is unreachable.
- **Key-rotation downtime attacks.** The mandated 7-day overlap window and dual-signature pattern prevent an attacker from exploiting a window between rotation and consumer cache refresh to forge verdicts under a not-yet-cached key.
- **Stealth key revocation.** The mandatory append-only revocation list at a well-known URL prevents an issuer from silently invalidating historical verdicts.

### 9.2 What EVP/1 does not prevent

- **Compromise of the issuer's signing key.** If an issuer's private key is exfiltrated, verdicts signed with it cannot be distinguished from legitimate verdicts until the key is revoked. Issuers SHOULD use hardware-backed key storage and SHOULD follow §6.5.3 on confirmed compromise.
- **Issuer-side data poisoning.** EVP/1 specifies the wire format but not the data sources. A malicious or compromised data source upstream of the issuer can cause incorrect-but-signed verdicts. Consumers SHOULD prefer issuers with public methodology and audited data corpora.
- **Replay attacks against time-sensitive verdicts.** A verdict is valid at `issued_at`. A consumer that relies on a stale verdict (e.g., a domain that has since been registered) bears the staleness risk. Issuers SHOULD include `as_of` and `valid_until` semantics; this specification does not yet mandate them.
- **Cross-axis correlation attacks.** A determined attacker who controls one axis source (e.g., a corrupt registry) may be able to influence a composite verdict. Defense is out of scope; the per-axis evidence-of-record requirements (§4) allow consumers to detect such attacks by inspecting the underlying findings.
- **Side-channel timing leaks.** Issuers that compute verdicts in variable time may leak information about candidates being verified. Out of scope.

### 9.3 Privacy considerations

A verdict references a candidate name. Names submitted for verification may themselves be sensitive (e.g., an unannounced product). Issuers SHOULD document their retention policy for submitted names and SHOULD NOT include personally identifying information about the requester in any signed payload.

---

## 10. Open comment period

### 10.1 Submitting comments

Comments on this draft MAY be submitted as issues on the public repository:

```
https://github.com/etymolt/evp-spec/issues
```

Issues SHOULD be labeled with the section number being commented on (e.g., `§4.3`, `§6.4`).

Comments MAY also be sent to `hello@etymolt.com` for cases where a public issue is inappropriate. The editor SHALL NOT publish comments received privately without consent.

### 10.2 Review SLA

The editor commits to:

- Acknowledging every issue within **5 business days** of submission.
- Routing every issue to a triage label (`accepted`, `clarification-needed`, `out-of-scope`, `editorial`, `deferred-to-1.1`) within **14 business days**.
- Publishing weekly digests of accepted changes at `https://etymolt.com/docs/verdict-protocol/changelog`.

### 10.3 Version 1.1 timing

The open comment period closes **2026-09-10** (90 days). The editor will publish:

- A consolidated comment digest by **2026-09-24**.
- A 1.1 draft incorporating accepted changes by **2026-10-15**.
- 1.1 as a public release by **2026-11-15**, with at least 30 days of overlap during which 1.0 verdicts remain conformant.

---

## Appendix A — JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://etymolt.com/docs/verdict-protocol/evp-1.schema.json",
  "title": "Etymolt Verdict Protocol Verdict Object",
  "type": "object",
  "required": [
    "evp_version",
    "name",
    "verdict",
    "score",
    "axes",
    "verdict_id",
    "issued_at",
    "disclaimer",
    "signature",
    "signature_key_id",
    "signature_payload_digest"
  ],
  "properties": {
    "evp_version": {
      "type": "string",
      "pattern": "^1\\.[0-9]+\\.[0-9]+$"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64
    },
    "verdict": {
      "type": "string",
      "enum": ["PASS", "DECIDE", "BLOCK", "INSUFFICIENT_SIGNAL"]
    },
    "score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100
    },
    "axes": {
      "type": "object",
      "required": ["trademark", "domain", "distinctiveness", "linguistic", "cultural"],
      "properties": {
        "trademark": { "$ref": "#/$defs/trademark_axis" },
        "domain": { "$ref": "#/$defs/domain_axis" },
        "distinctiveness": { "$ref": "#/$defs/distinctiveness_axis" },
        "linguistic": { "$ref": "#/$defs/linguistic_axis" },
        "cultural": { "$ref": "#/$defs/cultural_axis" }
      },
      "additionalProperties": false
    },
    "verdict_id": {
      "type": "string",
      "pattern": "^v_[A-Za-z0-9_-]{12,}$"
    },
    "issued_at": {
      "type": "string",
      "format": "date-time"
    },
    "disclaimer": {
      "type": "string",
      "minLength": 1
    },
    "signature": {
      "type": "string",
      "contentEncoding": "base64"
    },
    "signature_key_id": {
      "type": "string",
      "minLength": 1
    },
    "signature_payload_digest": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "signature_co": {
      "type": "object",
      "required": ["signature", "signature_key_id", "signature_payload_digest"],
      "properties": {
        "signature": { "type": "string", "contentEncoding": "base64" },
        "signature_key_id": { "type": "string", "minLength": 1 },
        "signature_payload_digest": { "type": "string", "pattern": "^[0-9a-f]{64}$" }
      }
    },
    "one_line": { "type": "string" },
    "findings": { "type": "array", "items": { "type": "string" } },
    "confidence": { "type": "integer", "minimum": 0, "maximum": 100 },
    "confidence_interval": {
      "type": "object",
      "properties": {
        "lower": { "type": "number" },
        "upper": { "type": "number" },
        "point_estimate": { "type": "number" },
        "method": { "type": "string" }
      }
    },
    "permalink": { "type": "string", "format": "uri" },
    "jurisdictions_consulted": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "patternProperties": {
    "^x_": {}
  },
  "additionalProperties": true,
  "$defs": {
    "axis_status": {
      "type": "string",
      "enum": ["CLEAR", "CAUTION", "BLOCKED", "INSUFFICIENT_SIGNAL", "UNKNOWN"]
    },
    "trademark_axis": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "$ref": "#/$defs/axis_status" },
        "jurisdictions_consulted": { "type": "array", "items": { "type": "string" } },
        "colliding_marks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "wordmark": { "type": "string" },
              "owner": { "type": "string" },
              "serial_number": { "type": "string" },
              "registration_number": { "type": "string" },
              "nice_classes": { "type": "array", "items": { "type": "integer" } },
              "filing_date": { "type": "string", "format": "date" },
              "status": { "type": "string" },
              "deep_link": { "type": "string", "format": "uri" }
            }
          }
        },
        "nice_classes_assumed": { "type": "array", "items": { "type": "integer" } },
        "coverage_caveat": { "type": "string" }
      }
    },
    "domain_axis": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "$ref": "#/$defs/axis_status" },
        "tlds_consulted": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["tld", "method", "definitive", "result"],
            "properties": {
              "tld": { "type": "string" },
              "method": { "type": "string", "enum": ["RDAP_authoritative", "WHOIS_authoritative", "DNS_fallback"] },
              "definitive": { "type": "boolean" },
              "result": { "type": "string", "enum": ["available", "registered", "unknown"] }
            }
          }
        },
        "recommended_variant": {
          "type": "object",
          "properties": {
            "domain": { "type": "string" },
            "registrar": { "type": "string" },
            "price_usd": { "type": "number" }
          }
        },
        "aftermarket_observed": { "type": "boolean" }
      }
    },
    "distinctiveness_axis": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["STRONG", "MODERATE", "WEAK", "BLOCKED", "INSUFFICIENT_SIGNAL", "UNKNOWN"]
        },
        "cohort_corpora_consulted": { "type": "array", "items": { "type": "string" } },
        "platforms_consulted": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "platform": { "type": "string" },
              "status": { "type": "string", "enum": ["available", "taken", "unknown"] },
              "url": { "type": "string", "format": "uri" },
              "claimed": { "type": "boolean" }
            }
          }
        },
        "workaround_variants_available": { "type": "array", "items": { "type": "string" } }
      }
    },
    "linguistic_axis": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "$ref": "#/$defs/axis_status" },
        "locales_evaluated": { "type": "array", "items": { "type": "string" } },
        "phoneme_skeleton": { "type": "string" },
        "sound_symbolism_axes": {
          "type": "object",
          "additionalProperties": { "type": "number" }
        },
        "advisory": { "type": "boolean" },
        "method": { "type": "string" }
      }
    },
    "cultural_axis": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "$ref": "#/$defs/axis_status" },
        "sources_consulted": { "type": "integer", "minimum": 0 },
        "cultural_sources_consulted": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": { "type": "string" },
              "matched": { "type": "boolean" },
              "language": { "type": "string" },
              "caveat": { "type": "string" }
            }
          }
        },
        "markets_covered": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## Appendix B — Sample verdicts

### B.1 Sample: PASS (ship)

```json
{
  "evp_version": "1.0.0",
  "name": "Inkstack",
  "verdict": "PASS",
  "score": 87,
  "axes": {
    "trademark": {
      "status": "CLEAR",
      "jurisdictions_consulted": ["USPTO_bulk", "UKIPO_domestic", "EUIPO_live_API", "WIPO_Madrid_IR"],
      "colliding_marks": [],
      "nice_classes_assumed": [9, 42]
    },
    "domain": {
      "status": "CLEAR",
      "tlds_consulted": [
        {"tld": ".com", "method": "RDAP_authoritative", "definitive": true, "result": "available"},
        {"tld": ".ai",  "method": "RDAP_authoritative", "definitive": true, "result": "registered"}
      ],
      "recommended_variant": {"domain": "inkstack.com", "registrar": "Cloudflare", "price_usd": 10.44},
      "aftermarket_observed": false
    },
    "distinctiveness": {
      "status": "STRONG",
      "cohort_corpora_consulted": ["yc_alumni_2014_2026", "brand_corpus_v1.4M"],
      "platforms_consulted": [
        {"platform": "github", "status": "available", "url": "https://github.com/inkstack", "claimed": true},
        {"platform": "npm",    "status": "available", "url": "https://www.npmjs.com/package/inkstack", "claimed": true}
      ]
    },
    "linguistic": {
      "status": "CLEAR",
      "locales_evaluated": ["en-US", "en-GB", "de-DE", "es-ES", "fr-FR"],
      "advisory": true,
      "method": "static rule-based heuristic"
    },
    "cultural": {
      "status": "CLEAR",
      "sources_consulted": 9,
      "markets_covered": ["US", "UK", "DE", "ES", "FR", "JP", "BR", "MX", "IN"]
    }
  },
  "verdict_id": "v_inkstack_a7f12bc",
  "issued_at": "2026-06-10T14:22:01.413Z",
  "one_line": "Clear across all five axes; inkstack.com available at standard registration.",
  "disclaimer": "Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction. The Bureau Model legal posture applies: we report what the records of record show; we do not opine on infringement.",
  "signature": "uRgztcYFdlvQZDk1834gOG88NDL8e/hgo5bjG/GIpUZAZy0F1CXyIX1bOfFr7EToJsihPuNgPXRszKQCexSABw==",
  "signature_key_id": "etymolt-1779085662",
  "signature_payload_digest": "04360aac47f170eed15c3f51f96578686dea94d4fcce6920f443484500353166"
}
```

### B.2 Sample: DECIDE (workable with caveats)

```json
{
  "evp_version": "1.0.0",
  "name": "Stratagem",
  "verdict": "DECIDE",
  "score": 60,
  "axes": {
    "trademark": {
      "status": "CAUTION",
      "jurisdictions_consulted": ["EUIPO_live_API", "UKIPO_domestic", "USPTO_TTAB", "USPTO_bulk", "WIPO_Madrid_IR", "famous_marks_denylist"],
      "colliding_marks": [],
      "coverage_caveat": "Common-word mark; 14 USPTO filings observed in adjacent classes; class-dependent co-existence risk."
    },
    "domain": {
      "status": "CAUTION",
      "tlds_consulted": [
        {"tld": ".com", "method": "RDAP_authoritative", "definitive": true, "result": "registered"},
        {"tld": ".ai",  "method": "RDAP_authoritative", "definitive": true, "result": "registered"},
        {"tld": ".dev", "method": "RDAP_authoritative", "definitive": true, "result": "registered"},
        {"tld": ".io",  "method": "RDAP_authoritative", "definitive": true, "result": "registered"},
        {"tld": ".co",  "method": "DNS_fallback",       "definitive": true, "result": "registered"},
        {"tld": ".so",  "method": "DNS_fallback",       "definitive": false, "result": "unknown"}
      ],
      "aftermarket_observed": true
    },
    "distinctiveness": {
      "status": "WEAK",
      "platforms_consulted": [
        {"platform": "github", "status": "taken",     "url": "https://github.com/stratagem", "claimed": true},
        {"platform": "x",      "status": "taken",     "url": "https://x.com/stratagem",      "claimed": false},
        {"platform": "npm",    "status": "taken",     "url": "https://www.npmjs.com/package/stratagem", "claimed": true},
        {"platform": "pypi",   "status": "available", "url": "https://pypi.org/project/stratagem", "claimed": true}
      ],
      "workaround_variants_available": ["@stratagemhq"]
    },
    "linguistic": {
      "status": "CLEAR",
      "advisory": true,
      "method": "static rule-based heuristic (pure Python phoneme-class rules)"
    },
    "cultural": {
      "status": "CLEAR",
      "sources_consulted": 32,
      "markets_covered": ["US", "UK", "IN", "CN", "JP", "KR", "BR", "MX", "ES", "FR", "DE"]
    }
  },
  "verdict_id": "v_ca83be889da34a",
  "issued_at": "2026-06-05T04:15:41.185Z",
  "one_line": "Workable but cleanup needed: .com / preferred TLD unavailable.",
  "findings": [
    "Trademark axis advisory — 14 USPTO filings observed in adjacent classes; class-dependent risk.",
    "No standard-registration domain available across the 8-TLD × 6-prefix matrix; aftermarket purchase required.",
    "Bare @stratagem on GitHub is taken; workable variant @stratagemhq is available."
  ],
  "permalink": "https://www.etymolt.com/v/v_ca83be889da34a",
  "disclaimer": "Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction. The Bureau Model legal posture applies: we report what the records of record show; we do not opine on infringement.",
  "signature": "uRgztcYFdlvQZDk1834gOG88NDL8e/hgo5bjG/GIpUZAZy0F1CXyIX1bOfFr7EToJsihPuNgPXRszKQCexSABw==",
  "signature_key_id": "etymolt-1779085662",
  "signature_payload_digest": "04360aac47f170eed15c3f51f96578686dea94d4fcce6920f443484500353166"
}
```

### B.3 Sample: BLOCK

```json
{
  "evp_version": "1.0.0",
  "name": "Sigil",
  "verdict": "BLOCK",
  "score": 18,
  "axes": {
    "trademark": {
      "status": "BLOCKED",
      "jurisdictions_consulted": ["USPTO_bulk", "USPTO_TTAB", "UKIPO_domestic", "EUIPO_live_API"],
      "colliding_marks": [
        {
          "wordmark": "SIGIL",
          "owner": "Sigil Software Inc.",
          "serial_number": "97123456",
          "registration_number": "7012345",
          "nice_classes": [9],
          "filing_date": "2022-04-11",
          "status": "Registered",
          "deep_link": "https://tsdr.uspto.gov/#caseNumber=97123456&caseType=SERIAL_NO&searchType=statusSearch"
        }
      ],
      "nice_classes_assumed": [9, 42]
    },
    "domain": {
      "status": "BLOCKED",
      "tlds_consulted": [
        {"tld": ".com", "method": "RDAP_authoritative", "definitive": true, "result": "registered"},
        {"tld": ".ai",  "method": "RDAP_authoritative", "definitive": true, "result": "registered"}
      ],
      "aftermarket_observed": true
    },
    "distinctiveness": {
      "status": "BLOCKED",
      "workaround_variants_available": []
    },
    "linguistic": { "status": "CLEAR", "advisory": true },
    "cultural":   { "status": "CLEAR", "sources_consulted": 32 }
  },
  "verdict_id": "v_sigil_blocked_2026",
  "issued_at": "2026-06-10T14:30:00.000Z",
  "one_line": "BLOCK — registered USPTO mark in Class 9 conflicts; workaround variants inherit block per In re Get Acme.",
  "findings": [
    "Registered USPTO mark SIGIL (Reg. 7012345) in Class 9 — software — owned by Sigil Software Inc.",
    "Workaround variants (getsigil, sigilhq, trysigil) inherit the Class 9 block per In re Get Acme (TTAB 2024)."
  ],
  "disclaimer": "Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction. The Bureau Model legal posture applies: we report what the records of record show; we do not opine on infringement.",
  "signature": "B7K2hZQYR3kT8mxL2pV5wN1eFgHjKlMnOpQrStUvWxYzAbCdEf1234567890ABCDef==",
  "signature_key_id": "etymolt-1779085662",
  "signature_payload_digest": "9c1a3b7d4e8f2c5b9a6d3e1f8c4b7a2d9e6f3c1a8b5d2e7f4c9a6b3d8e5f2c1a"
}
```

### B.4 Sample: INSUFFICIENT_SIGNAL (top-level)

This sample illustrates the composite `INSUFFICIENT_SIGNAL` verdict — the most operationally important edge case for honest negative space. The candidate `"Aiyana"` is a non-English given name with sparse registry coverage in the markets where it most plausibly carries a sacred-name or culturally significant association. The trademark axis returns `INSUFFICIENT_SIGNAL` because authoritative registers in three of seven jurisdictions did not respond definitively; the cultural axis returns `INSUFFICIENT_SIGNAL` because two of the consulted markets lacked lexicon coverage. A conformant issuer MUST NOT synthesize this to `DECIDE` — the absence of data is not a soft signal; it is a coverage failure, and the consumer is entitled to know.

A conformant consumer receiving this verdict MUST NOT display "low score, proceed with caution" or "yellow light" semantics. It MUST surface that the verdict was not issued because the underlying data was insufficient, and SHOULD prompt the consumer to either re-run later, supply additional context (e.g., explicit market scope or Nice classes), or escalate to manual review.

```json
{
  "evp_version": "1.0.0",
  "name": "Aiyana",
  "verdict": "INSUFFICIENT_SIGNAL",
  "score": 50,
  "axes": {
    "trademark": {
      "status": "INSUFFICIENT_SIGNAL",
      "jurisdictions_consulted": ["USPTO_bulk", "USPTO_TTAB", "EUIPO_live_API", "UKIPO_domestic", "WIPO_Madrid_IR", "INPI_BR", "IPINDIA_domestic"],
      "colliding_marks": [],
      "nice_classes_assumed": [9, 42],
      "coverage_caveat": "INPI_BR returned HTTP 502 across 3 retries; IPINDIA_domestic search endpoint timed out (>30s) on retry budget; WIPO_Madrid_IR returned partial — only 2 of 5 designated-state mirrors responded. Determinate conflict in 9/42 not established. Common given-name; cohort density in adjacent classes elevated. Re-run after 24h or escalate to counsel for jurisdiction-specific search."
    },
    "domain": {
      "status": "CAUTION",
      "tlds_consulted": [
        {"tld": ".com", "method": "RDAP_authoritative", "definitive": true,  "result": "registered"},
        {"tld": ".ai",  "method": "RDAP_authoritative", "definitive": true,  "result": "registered"},
        {"tld": ".io",  "method": "RDAP_authoritative", "definitive": true,  "result": "available"},
        {"tld": ".co",  "method": "RDAP_authoritative", "definitive": true,  "result": "registered"},
        {"tld": ".dev", "method": "RDAP_authoritative", "definitive": true,  "result": "available"}
      ],
      "recommended_variant": {"domain": "aiyana.io", "registrar": "Cloudflare", "price_usd": 41.00},
      "aftermarket_observed": true
    },
    "distinctiveness": {
      "status": "MODERATE",
      "cohort_corpora_consulted": ["yc_alumni_2014_2026", "brand_corpus_v1.4M", "given_names_us_census_2020"],
      "platforms_consulted": [
        {"platform": "github", "status": "available", "url": "https://github.com/aiyana", "claimed": true},
        {"platform": "npm",    "status": "available", "url": "https://www.npmjs.com/package/aiyana", "claimed": true},
        {"platform": "x",      "status": "taken",     "url": "https://x.com/aiyana", "claimed": false},
        {"platform": "pypi",   "status": "available", "url": "https://pypi.org/project/aiyana", "claimed": true}
      ],
      "workaround_variants_available": ["@aiyanahq", "@useaiyana"]
    },
    "linguistic": {
      "status": "CLEAR",
      "locales_evaluated": ["en-US", "es-MX", "pt-BR"],
      "advisory": true,
      "method": "static rule-based heuristic"
    },
    "cultural": {
      "status": "INSUFFICIENT_SIGNAL",
      "sources_consulted": 28,
      "cultural_sources_consulted": [
        {"source": "hurtlex_en", "matched": false, "language": "en"},
        {"source": "hurtlex_es", "matched": false, "language": "es"},
        {"source": "sacred_names", "matched": false, "language": "multi", "caveat": "Tier-1 catalog (~50 entries) does not cover Indigenous-Americas namespaces in depth; Aiyana is documented as a name of Cherokee origin meaning 'eternal blossom' — sacred-name overlap risk unverified."},
        {"source": "cultural_v2_regex", "matched": false, "language": "multi", "caveat": "0 patterns for indigenous-Americas markets in the 21-market panel; market coverage gap acknowledged."},
        {"source": "llm_cross_cultural", "matched": null, "language": "multi", "caveat": "3-LLM advisory panel did not run synchronously on this candidate due to rate-limit shed; result deferred to out-of-band screen with 30-day cache miss."}
      ],
      "markets_covered": ["US", "UK", "ES", "MX", "BR", "DE", "FR"],
      "coverage_caveat": "2 of 7 consulted markets lacked indigenous-Americas naming-tradition lexicon coverage; LLM cross-cultural panel did not return synchronously. Status is INSUFFICIENT_SIGNAL, not CLEAR — re-run after 24h or escalate to a cultural-review specialist for Cherokee / Diné / broader Indigenous-Americas naming-tradition review."
    }
  },
  "verdict_id": "v_aiyana_insig_a91f3c7d4e8f",
  "issued_at": "2026-06-10T14:45:22.108Z",
  "one_line": "Insufficient signal — 3 of 7 trademark registries did not respond definitively; cultural-coverage gap on Indigenous-Americas naming traditions; re-run in 24h or escalate.",
  "findings": [
    "Trademark axis did NOT return a determinate result: INPI_BR returned 502, IPINDIA_domestic timed out, WIPO_Madrid_IR returned only 2/5 designated-state mirrors. Do NOT treat as CLEAR.",
    "Cultural axis did NOT return a determinate result: sacred-names Tier-1 catalog has known gap for Indigenous-Americas namespaces; LLM cross-cultural panel was rate-shed.",
    "Domain CAUTION: aiyana.com / .ai / .co registered; aiyana.io and aiyana.dev available at standard registration.",
    "Distinctiveness MODERATE: bare GitHub / npm / pypi available; bare X handle taken; @aiyanahq and @useaiyana available as workaround variants.",
    "Recommended next step: re-run this verdict in 24 hours OR supply explicit market scope and Nice classes OR escalate to manual cultural and trademark review before adoption."
  ],
  "confidence": 38,
  "confidence_interval": {"lower": 30, "upper": 46, "point_estimate": 38, "method": "axis_uncertainty_propagation_v1"},
  "recommended_actions": [
    {"kind": "wait_for_refresh", "label": "Re-run verification in 24 hours (registry mirrors will retry)", "next_refresh_hours": 24},
    {"kind": "supply_context",   "label": "Provide explicit market scope and Nice classes to narrow the search"},
    {"kind": "escalate_review",  "label": "Escalate to a cultural-review specialist for Indigenous-Americas naming-tradition review", "url": "https://www.etymolt.com/methodology#cultural-escalation"},
    {"kind": "expert_review",    "label": "Consult a trademark attorney for jurisdiction-specific search in BR and IN", "url": "https://www.etymolt.com/methodology#attorney-referral"}
  ],
  "permalink": "https://www.etymolt.com/v/v_aiyana_insig_a91f3c7d4e8f",
  "jurisdictions_consulted": ["USPTO_bulk", "USPTO_TTAB", "EUIPO_live_API", "UKIPO_domestic", "WIPO_Madrid_IR", "INPI_BR", "IPINDIA_domestic"],
  "disclaimer": "Clearance signal, not legal advice. Confirm with trademark counsel before adopting a name in commerce. Data sources have stated freshness windows; refer to coverage_caveat per jurisdiction. The Bureau Model legal posture applies: we report what the records of record show; we do not opine on infringement.",
  "signature": "Q9k2vP7nW3xR5tH8jM1cF6bL4dY7eK0aS3uT9oI2pN5mB6vC8nQ1xZ4hG7yJ3kL2eMfV9pT5uOiNbDhRjGqXfWzVcA==",
  "signature_key_id": "etymolt-1779085662",
  "signature_payload_digest": "7a3f1e9c8b2d4a6e0f5c1b9d8e7a3c2b1f0e9d8c7b6a5d4c3b2a1f0e9d8c7b6a"
}
```

---

## Appendix C — Reference implementation pointers

### C.1 Reference issuer

The Etymolt verification API is the reference implementation of an EVP/1 issuer.

- **Base URL.** `https://api.etymolt.com`
- **Endpoint.** `POST /v1/verify` returns an EVP/1-compatible verdict envelope.
- **Methodology.** `https://etymolt.com/methodology`
- **Coverage spec.** `https://etymolt.com/coverage`

### C.2 Reference MCP server

The canonical MCP server exposes EVP/1 verdicts as a single tool callable from any MCP-compatible host.

- **Package.** `@etymolt/mcp-server` (npm)
- **Source.** `https://github.com/etymolt/etymolt/tree/main/sdks/etymolt-mcp`

### C.3 Framework adapters

EVP/1 verdicts are surfaced through native adapters for: LangChain, LlamaIndex, CrewAI, LangGraph, OpenAI Agents SDK, Mastra, and Vercel AI SDK. Each adapter MUST surface the `disclaimer` field per §5.4 and MUST NOT strip the signature triple.

### C.4 Specification repository

- **Repository.** `https://github.com/etymolt/evp-spec`
- **Issues / comments.** `https://github.com/etymolt/evp-spec/issues`
- **Test vectors.** `https://github.com/etymolt/evp-spec/tree/main/test_vectors`
- **Reference test runner.** `https://github.com/etymolt/evp-spec/blob/main/EVP-1-validator-tests.py`
- **Public key directory (Etymolt issuer).** `https://api.etymolt.com/.well-known/evp-keys.json`
- **Public revocation list (Etymolt issuer).** `https://api.etymolt.com/.well-known/evp-keys-revoked.json`

---

*End of document. Etymolt Verdict Protocol, Version 1.0.0, Public Comment. © 2026 Etymolt Inc. Released under CC-BY-4.0.*
