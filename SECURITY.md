# Security Policy

EVP/1 is a cryptographic protocol. Reports of vulnerabilities in the signature scheme, key-rotation protocol, canonicalization rules, or any implementation of the reference validator are treated as in-scope security issues.

## In scope

- Signature-scheme weaknesses (§6.1–§6.3 of the spec): Ed25519 misuse, JCS canonicalization defects, replay-attack primitives, signature-stripping primitives, dual-signature confusion during the overlap window (§6.4.3).
- Key-rotation defects (§6.4): missing revocation enforcement, expired-key acceptance, cross-issuer key reuse, JWKS endpoint cache-poisoning.
- Schema confusion: any input that the JSON Schema (Draft 2020-12) accepts but the prose normative spec rejects, or vice versa.
- Reference-validator (`EVP-1-validator-tests.py`) defects that admit a conformance-failing verdict.
- Disclaimer-stripping primitives: any consumer-side rendering path that would surface a verdict without the verbatim disclaimer (§5).
- Temporal-validity bypass: any primitive that lets a consumer render a stale verdict (> `valid_until`) without the required staleness banner (§11).

## Out of scope

- Etymolt product surfaces — those report to `support@etymolt.com`.
- Trademark, legal, or business disputes about the verdicts themselves — Bureau Model (§5.2) applies; a verdict is a clearance signal, not legal advice.
- Third-party EVP/1 issuers — vulnerability reports about non-Etymolt issuers go to that issuer.

## How to report

Email **`security@etymolt.com`** with:

1. A description of the vulnerability.
2. Steps to reproduce (a small test vector + the expected vs. observed validator output is ideal).
3. Your name and affiliation if you'd like attribution. We will credit reporters in the changelog unless you ask not to be named.

We do not require encryption for the initial report, but if you'd prefer encrypted submission, request our PGP key in your first message and we'll send it from `security@etymolt.com`.

## What happens next

| Step | Target |
|---|---|
| Acknowledgment of receipt | 2 business days |
| Triage decision (in-scope / out-of-scope, severity tier) | 5 business days |
| Fix landing in the spec or validator (P0/P1) | 30 days from triage |
| Public disclosure + credit (if applicable) | After fix lands, coordinated with reporter |

For P0 vulnerabilities in the signature scheme — anything that would let a forged verdict validate against a legitimate `signature_key_id` — we will issue an out-of-band notice to all known implementers within 7 days, embargo timing TBD with the reporter.

## What this policy is not

This policy covers the **specification** and the **reference validator**. It does not cover the implementations of EVP/1 that live in other repositories (SDKs, MCP server, etc.); each implementation publishes its own security policy.

## Editorial corrections

Typos, broken links, and clarifications in the spec are not security issues — file those as regular GitHub issues using the `bug-in-schema` template.
