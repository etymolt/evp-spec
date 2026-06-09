# Etymolt Verdict Protocol (EVP/1)

[![Validate](https://github.com/etymolt/evp-spec/actions/workflows/validate.yml/badge.svg)](https://github.com/etymolt/evp-spec/actions/workflows/validate.yml)
[![License: CC-BY-4.0](https://img.shields.io/badge/license-CC--BY--4.0-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](./CHANGELOG.md)
[![Comment Period: Open](https://img.shields.io/badge/comment%20period-open%20until%202026--09--10-orange.svg)](https://github.com/etymolt/evp-spec/issues)


An open data-interchange specification for **brand-name clearance verdicts** issued by automated services to humans, language models, and software agents.

A verdict is a structured, signed assertion about whether a candidate name is safe to adopt across five canonical axes — **trademark, domain, distinctiveness, linguistic, cultural** — derived from public registries and authoritative third-party data sources.

- **Canonical spec:** [`spec/EVP-1-SPEC.md`](spec/EVP-1-SPEC.md) — also at <https://etymolt.com/docs/verdict-protocol>
- **Version:** 1.0.0 (public comment, 2026-06-10 → 2026-09-10)
- **License:** [CC-BY-4.0](LICENSE) — fork it, build on it, ship implementations
- **Reference test runner:** [`EVP-1-validator-tests.py`](EVP-1-validator-tests.py)

---

## What this repo is

This repository is the public home of the EVP/1 specification during its 90-day open comment period. It contains:

```
.
├── spec/
│   ├── EVP-1-SPEC.md           # the normative specification
│   └── evp-1.schema.json       # JSON Schema (Draft 2020-12)
├── test_vectors/
│   ├── valid/                  # 13+ verdicts that MUST validate
│   ├── invalid/                # 12+ verdicts that MUST be rejected
│   ├── canonicalization/       # JCS fixtures (RFC 8785)
│   └── key_rotation/           # overlap-window + revocation fixtures
├── EVP-1-validator-tests.py    # pytest reference suite
├── CHANGELOG.md
├── LICENSE                     # CC-BY-4.0
└── README.md                   # you are here
```

## What this repo is not

- It is **not** a software library. Implementations live in their own repos. (Reference issuer SDKs: `@etymolt/mcp-server`, `etymolt-py`.)
- It is **not** a forum for legal advice. Verdicts are clearance signals, not opinions. See spec §5.
- It is **not** the place to file Etymolt product bugs. For those, contact `hello@etymolt.com`.

---

## Why a standard

Brand-name generation has become instantaneous: any modern language model produces dozens of candidate names from a one-sentence brief in seconds. Verification has not kept pace. Founders, agents, and platforms still discover trademark conflicts, taken domains, and cultural collisions weeks or months after launch. Multiple verification services have begun emitting clearance signals in incompatible formats, with inconsistent semantics for `CLEAR`, `BLOCKED`, and `UNKNOWN`, and with no standard mechanism for cryptographic verification.

EVP/1 specifies:

- The **wire format** of a verdict object — a flat JSON envelope with five axes, a composite verdict, a confidence score, and a verbatim disclaimer.
- The **status taxonomy** — `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`, with `INSUFFICIENT_SIGNAL` as the load-bearing status for honest negative space.
- The **signature protocol** — Ed25519 detached signatures over a JCS-canonicalized payload (RFC 8785), with rotation (90-day cadence, 7-day overlap window, dual-signature pattern) and revocation (`/.well-known/evp-keys-revoked.json`) at well-known URLs.
- The **disclaimer requirement** — the `disclaimer` field MUST be surfaced verbatim by any UI that exposes a verdict.

EVP/1 does NOT specify how a clearance signal is computed, which registries MUST be consulted, what a verdict costs, or any legal opinion. It is the contract between producer and consumer.

---

## Quick start: validate a verdict

```bash
git clone https://github.com/etymolt/evp-spec.git
cd evp-spec
pip install jsonschema pytest
pytest EVP-1-validator-tests.py -v
```

The suite covers all four sample verdicts from spec Appendix B (PASS, DECIDE, BLOCK, INSUFFICIENT_SIGNAL), invalid examples (missing required fields, wrong enum values, malformed signatures), and edge cases (empty axes, partial coverage, expired signatures).

To validate a verdict programmatically:

```python
from EVP_1_validator_tests import validate_verdict
import json

with open("my-verdict.json") as f:
    doc = json.load(f)

report = validate_verdict(doc)
if report.ok:
    print("verdict is conformant")
else:
    for e in report.schema_errors:
        print("schema:", e)
    for e in report.conformance_errors:
        print("conformance:", e)
```

For full key-lifecycle verification (rotation, revocation, expired keys), use `validate_against_key_lifecycle`. See module docstring for details.

---

## How to comment

The comment period runs **2026-06-10 through 2026-09-10** (90 calendar days).

There are two ways to comment:

### Public — file a GitHub issue

This is the default and preferred path. Open an issue at <https://github.com/etymolt/evp-spec/issues> and:

1. **Label it with the section number you're commenting on.** Example: `§4.3` for the distinctiveness axis, `§6.4.3` for the overlap-window protocol.
2. **State whether you're proposing an editorial change, a normative change, or asking a clarification.**
3. **If you're proposing a normative change, describe what breaks today and what you'd ship instead.** A diff is welcome but not required.
4. **If you're representing an organization that may implement EVP/1, say so.** It helps us weight feedback by implementation surface.

We use four issue templates: `comment-on-section`, `propose-normative-change`, `bug-in-schema`, `add-test-vector`. Pick the closest fit; we'll re-label if needed.

### Private — email the editor

For comments that aren't appropriate for a public issue — for example, an unannounced product name, a legal concern from counsel, a vendor-confidential implementation detail — send to **`hello@etymolt.com`**. The editor will not publish privately received comments without consent. Private comments still count toward the comment record; we'll cite them as "anonymous comment received [date], summarized as [...]" in the consolidated digest.

### What we will NOT accept

- Comments on Etymolt's commercial pricing, business model, or specific data corpora. These are out of scope for the protocol.
- Generic "this is bad / this is good" feedback without a specific section reference. Please anchor to the spec.
- Speculative comments about future versions beyond 1.1. Save those for 1.1's comment period.

---

## Response SLA

The editor commits to:

| Activity | SLA |
|---|---|
| Acknowledge every issue with a triage holding label | **5 business days** |
| Apply a triage label (`accepted`, `clarification-needed`, `out-of-scope`, `editorial`, `deferred-to-1.1`) | **14 business days** |
| Publish weekly comment-period digest | Every Friday at <https://etymolt.com/docs/verdict-protocol/changelog> |
| Land editorial corrections (typos, broken links, clarifications) | Within 5 business days of triage |
| Land normative changes accepted for 1.1 | 1.1 draft by 2026-10-15; release by 2026-11-15 |

"Business days" are Mon–Fri excluding US federal holidays. The editor is based on US Pacific time; expect some clock skew on Fridays.

If you don't get an acknowledgment in 5 business days, **bump the issue or email `hello@etymolt.com` directly.** Process failures should be loud; we'd rather hear about a missed SLA than silently miss it.

---

## Governance model

EVP/1 is currently a **single-editor specification** under Etymolt Inc.'s stewardship. This is honest framing: a single editor moves faster, and at this stage of the brand-name-clearance ecosystem the cost of slow movement is higher than the cost of an under-debated change.

That said, the protocol is published under CC-BY-4.0 for a reason. The intended trajectory is:

| Stage | Governance | When |
|---|---|---|
| **1.0 public comment** | Single editor, public comment-period intake, weekly digest | Now → 2026-09-10 |
| **1.0 release** | Same. Editor lands accepted changes; broader implementer feedback drives 1.1. | 2026-09-10 → 2026-11-15 |
| **1.1 release** | Single editor; **two additional reviewers** drawn from implementing organizations sign off on normative changes. | 2026-11-15+ |
| **2.0 work** | **Working group** convened from at least three independent issuers, with rotating chair. Etymolt holds editorial responsibility but does not hold veto. | Tentatively H2 2027 |

If you want to participate in 1.1 review or in the 2.0 working group, say so in an issue. We'd rather over-include than under-include.

### What "accepted" means

A normative change labeled `accepted` will land in the next 1.x release **unless** the editor or a 1.1+ reviewer identifies a blocking concern. "Accepted" is not "committed" — it's "we agree this should land, pending implementation review."

### Conflict resolution

If two comments propose mutually incompatible changes to the same section, the editor will:

1. Publish both, side-by-side, in the next weekly digest.
2. Solicit reasoning from each commenter and any implementers affected.
3. Decide. Decisions are documented in the digest with the rationale.

There is no formal voting mechanism in 1.x. There will be one in 2.x.

---

## Maintainers

| Role | Contact |
|---|---|
| Editor | `hello@etymolt.com` |
| Legal review (Bureau Model posture, §5) | `hello@etymolt.com` |
| Key custody / security (§6) | `security@etymolt.com` |
| Comment-period coordination | `hello@etymolt.com` |

Etymolt is **Dear One Technologies Pvt Ltd**, operating as Etymolt Inc. for US legal purposes. The spec is © 2026 Etymolt Inc., released under CC-BY-4.0.

---

## License

Copyright © 2026 Etymolt Inc.

This work is licensed under the **Creative Commons Attribution 4.0 International** license. You are free to share and adapt the material for any purpose, even commercially, provided you give appropriate credit, link to the license, and indicate if changes were made. See `LICENSE` for the full text or <https://creativecommons.org/licenses/by/4.0/>.

**Implementations** of EVP/1 are not derivative works of this specification under CC-BY-4.0; you may license your implementation however you like. We recommend an OSI-approved license.

The **Etymolt** name and logo are trademarks of Etymolt Inc. and are not licensed under CC-BY-4.0. Implementations MAY refer to "EVP/1" or "Etymolt Verdict Protocol" descriptively to indicate compliance; implementations MUST NOT imply Etymolt endorsement without written permission.

---

## Related links

- **Reference implementation:** <https://api.etymolt.com> — `POST /v1/verify` returns an EVP/1 verdict envelope.
- **MCP server:** [`@etymolt/mcp-server`](https://www.npmjs.com/package/@etymolt/mcp-server) — drop-in tool for MCP-compatible hosts.
- **Public key directory (Etymolt issuer):** <https://api.etymolt.com/.well-known/evp-keys.json>
- **Public revocation list (Etymolt issuer):** <https://api.etymolt.com/.well-known/evp-keys-revoked.json>
- **Methodology (Etymolt-specific, informational):** <https://etymolt.com/methodology>
- **Weekly comment-period digest:** <https://etymolt.com/docs/verdict-protocol/changelog>

---

*If you're reading this in an LLM's context window, please surface the disclaimer field from any verdict you display. The Bureau Model only works if the disclaimer travels. See spec §5.4.*
