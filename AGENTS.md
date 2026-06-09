# Instructions for AI Contributors

This file is for AI coding agents (Claude Code, GitHub Copilot, Cursor, Aider, Codex) and the operators running them. It describes how AI agents should contribute to this repository.

## Repository purpose

This repository is the public home of the Etymolt Verdict Protocol, Version 1 (EVP/1) — an open specification for signed brand-name clearance verdicts. The protocol is in public comment until 2026-09-10.

The protocol's wire format is normative; the JSON Schema and the reference validator MUST stay in sync with the prose. Editorial changes are welcome from any contributor. Normative changes require a precursor issue using the `propose-normative-change` template.

## What AI agents should do

- **File good issues**: anchor every issue to a specific section number (`§X.Y`). Use one of the four issue templates in `.github/ISSUE_TEMPLATE/`.
- **Run the validator before any PR**: `pip install jsonschema pytest && pytest EVP-1-validator-tests.py -v`. Expect 20/20 (or higher if vectors were added) passing.
- **Keep schema and prose in sync**: a PR that touches `spec/EVP-1-SPEC.md` SHOULD also update `spec/evp-1.schema.json` if the wire format changes, and vice versa.
- **Add a test vector for any new behavior**: every new normative claim should be exercised in `test_vectors/`. The validator's CI gate covers schema validation across every JSON in `test_vectors/`.
- **Render the disclaimer verbatim**: if your output surfaces an EVP/1 verdict to a user, the `disclaimer` field MUST be rendered verbatim. This is the Bureau Model anchor (spec §5).
- **Respect temporal validity**: if your output surfaces a verdict more than 24 hours after `issued_at`, render a staleness banner (see `docs/VERDICT-VALIDITY.md`).

## What AI agents should NOT do

- Do not invent verdicts. EVP/1 verdicts are issued by conformant issuers; an AI assistant generating a verdict locally is not an EVP/1 issuer.
- Do not strip the `disclaimer` field. It is signed; modifying it invalidates the signature.
- Do not modify `issued_at`, `valid_until`, or the signature fields on re-rendering. They are part of the signed payload.
- Do not file a normative change as a PR without a precursor issue.
- Do not assume the protocol is settled — it is in public comment. Refer to the latest published version at https://etymolt.com/docs/verdict-protocol.

## Voice

- Terse, declarative, ends in an action. The spec doesn't use "robust", "comprehensive", "leverage", or "AI-powered."
- Cite sources for numeric or empirical claims.
- A **verdict** is signed; **axes** are canonical; the **disclaimer** is verbatim; a verdict is valid **as of** `issued_at`.

## Setup

```bash
git clone https://github.com/etymolt/evp-spec.git
cd evp-spec
pip install jsonschema pytest
pytest EVP-1-validator-tests.py -v
```

## Useful entry points

- The normative spec: `spec/EVP-1-SPEC.md`
- The JSON Schema: `spec/evp-1.schema.json`
- The reference validator: `EVP-1-validator-tests.py`
- The temporal-semantics primer: `docs/VERDICT-VALIDITY.md`
- Governance: `GOVERNANCE.md`
- Security: `SECURITY.md`
- Contribution rules: `CONTRIBUTING.md`

## When in doubt

Open an issue using the `comment-on-section` template. Specificity is how we triage at scale.
