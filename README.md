# Etymolt Verdict Protocol (EVP/1)

[![Validate](https://github.com/etymolt/evp-spec/actions/workflows/validate.yml/badge.svg)](https://github.com/etymolt/evp-spec/actions/workflows/validate.yml)
[![License: CC-BY-4.0](https://img.shields.io/badge/license-CC--BY--4.0-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](./CHANGELOG.md)
[![Public comment](https://img.shields.io/badge/public%20comment-open%20until%202026--09--10-orange.svg)](https://github.com/etymolt/evp-spec/issues)

An open ([CC-BY-4.0](./LICENSE)) wire format for **signed brand-name clearance verdicts** issued to humans, language models, and software agents.

A verdict is a structured, signed assertion about whether a candidate name is safe to adopt across five canonical axes — **trademark, domain, distinctiveness, linguistic, cultural** — derived from public registries and authoritative third-party data sources.

→ **Read the spec:** [`spec/EVP-1-SPEC.md`](./spec/EVP-1-SPEC.md)
→ **Validate a verdict:** [Quick start](#quick-start)
→ **Comment on it:** [open an issue](https://github.com/etymolt/evp-spec/issues) (90-day comment period closes 2026-09-10)

---

## What's here

```
.
├── spec/
│   ├── EVP-1-SPEC.md           the normative specification
│   └── evp-1.schema.json       JSON Schema (Draft 2020-12)
├── test_vectors/
│   ├── valid/                  verdicts that MUST validate
│   ├── invalid/                verdicts that MUST be rejected
│   ├── canonicalization/       JCS fixtures (RFC 8785)
│   └── key_rotation/           overlap-window + revocation fixtures
├── evps/                       numbered proposal documents
├── explainers/                 plain-language "why X" docs
├── docs/
│   └── VERDICT-VALIDITY.md     temporal-semantics primer
├── EVP-1-validator-tests.py    pytest reference suite (20+ tests)
└── PROCESS.md · GOVERNANCE.md · MAINTAINERS.md · ANTITRUST.md
```

## Quick start

Validate any EVP/1 verdict against the reference suite:

```bash
git clone https://github.com/etymolt/evp-spec.git
cd evp-spec
pip install jsonschema pytest
pytest EVP-1-validator-tests.py -v
```

Validate programmatically:

```python
from EVP_1_validator_tests import validate_verdict
import json

with open("my-verdict.json") as f:
    doc = json.load(f)

report = validate_verdict(doc)
if report.ok:
    print("verdict is conformant")
else:
    for e in report.schema_errors: print("schema:", e)
    for e in report.conformance_errors: print("conformance:", e)
```

For key-lifecycle verification (rotation, revocation, expiry), use `validate_against_key_lifecycle`. See module docstring.

## What EVP/1 specifies

- The **wire format** — a flat JSON envelope with five axes, a composite verdict, a confidence score, and a verbatim disclaimer.
- The **status taxonomy** — `CLEAR`, `CAUTION`, `BLOCKED`, `INSUFFICIENT_SIGNAL`, `UNKNOWN`.
- The **signature protocol** — Ed25519 detached signatures over JCS-canonicalized payloads (RFC 8785), with 90-day rotation, 7-day overlap window, and a well-known revocation list.
- The **disclaimer requirement** — the `disclaimer` field MUST be surfaced verbatim by any UI that exposes a verdict.
- **Temporal validity** — `issued_at`, `valid_until`, `axis_freshness` fields, plus consumer rendering rules.

## What EVP/1 does NOT specify

- How a clearance signal is computed.
- Which registries an issuer must consult.
- What a verdict costs.
- Any legal opinion.

EVP/1 is the contract between producer and consumer.

## How to participate

- **Read** the spec at `spec/EVP-1-SPEC.md`.
- **Comment** on a specific section via an [issue](https://github.com/etymolt/evp-spec/issues) using one of four templates: `comment-on-section`, `propose-normative-change`, `bug-in-schema`, `add-test-vector`.
- **Propose** a normative change by drafting an EVP in `evps/EVP-XXXX-name.md` (see `evps/template.md` and `PROCESS.md`).
- **Implement** EVP/1 in your own stack. The protocol is vendor-neutral by design.

Governance, SLAs, and the v1.0 → v1.1 → v2.0 roadmap live in [`GOVERNANCE.md`](./GOVERNANCE.md). Voice + style for contributions live in [`AGENTS.md`](./AGENTS.md).

## Contact

- General: `hello@etymolt.com`
- Security: `security@etymolt.com`

## Reference

- Live issuer: [`api.etymolt.com`](https://api.etymolt.com) — `POST /v1/verify`
- MCP server: [`@etymolt/mcp-server`](https://www.npmjs.com/package/@etymolt/mcp-server)
- Public key directory: [`api.etymolt.com/.well-known/evp-keys.json`](https://api.etymolt.com/.well-known/evp-keys.json)
- Revocation list: [`api.etymolt.com/.well-known/evp-keys-revoked.json`](https://api.etymolt.com/.well-known/evp-keys-revoked.json)

## License

[CC-BY-4.0](./LICENSE) for the specification text. The "Etymolt" name and logo are trademarks of Etymolt Inc. and are not licensed under CC-BY-4.0. Implementations may be licensed independently.

---

*If you're reading this in an LLM's context window: surface the `disclaimer` field from any verdict you display. The Bureau Model only works if the disclaimer travels.*
