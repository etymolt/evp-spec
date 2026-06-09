# Contributing to EVP/1

EVP/1 is in public comment from **2026-06-10 through 2026-09-10**. Comments received during this window land in v1.1 (target release 2026-11-15). Editorial corrections roll forward into the next patch release.

This document describes how to contribute. The full governance model lives in [`GOVERNANCE.md`](./GOVERNANCE.md).

## What you can contribute

| Type | Use this template |
|---|---|
| Comment on a specific section (`§X.Y`) | [`comment-on-section`](./.github/ISSUE_TEMPLATE/comment-on-section.yml) |
| Propose a normative change | [`propose-normative-change`](./.github/ISSUE_TEMPLATE/propose-normative-change.yml) |
| Report a bug in the schema or validator | [`bug-in-schema`](./.github/ISSUE_TEMPLATE/bug-in-schema.yml) |
| Add a test vector | [`add-test-vector`](./.github/ISSUE_TEMPLATE/add-test-vector.yml) |

If your contribution is a **vulnerability in the signature scheme or key-rotation protocol**, do not file a public issue. See [`SECURITY.md`](./SECURITY.md).

## Filing a good issue

Two things make an EVP/1 comment land:

1. **Anchor to a specific section number** (`§4.3.2`, not "the trademark axis"). The spec is 12 sections + 3 appendices; specificity is how we triage at scale.
2. **State what breaks today and what you would ship instead.** A diff is welcome but not required. A use case the spec doesn't currently handle is welcome. Free-form "this section is confusing" is welcome — but tell us *what* is confusing and *what* you expected.

If you represent an organization that may implement EVP/1, say so in the issue body. Implementation-surface comments are weighted higher because they tell us what breaks at production scale.

## Filing a good PR

Patches are welcome for:

- Editorial corrections (typos, broken links, prose clarity) — these land in the next patch release.
- New test vectors that exercise a corner of the spec the existing 19 don't cover.
- JSON Schema fixes (mismatches between the schema and the normative prose).
- Workflow + tooling improvements.

For **normative changes**, please open an issue first using the `propose-normative-change` template. A PR that lands a normative change without a precursor issue will be closed and re-opened against the issue thread.

## Validator + test workflow

Every PR runs `EVP-1-validator-tests.py` against all four Appendix B sample verdicts plus the full test_vectors/ corpus.

```bash
pip install jsonschema pytest
pytest EVP-1-validator-tests.py -v   # expect 20/20 passing
```

If you add a new test vector, also add a corresponding assertion in the validator so the new vector is exercised in CI.

## Style

- Voice: terse, declarative, ends in an action. The spec doesn't use "robust" or "comprehensive" or "leverage."
- Citations: every numeric claim in the spec traces to either a public source or the methodology. If it can't, it doesn't ship. Same rule applies to PRs.
- Vocabulary: a **verdict** is signed, an **axis** is canonical, the **disclaimer** is verbatim, a verdict is valid **as of** `issued_at`. See the spec §1 for the rest.

## IP

By contributing, you agree your contribution is licensed under [CC-BY-4.0](./LICENSE) for the specification text and under the Apache-2.0 License for any code (the validator, workflows, test vectors). You retain copyright; we get the right to incorporate your contribution under those terms.

## Out of scope for issues

- Etymolt product pricing, business model, or specific data corpora.
- Speculative comments about EVP/2 — those land in a 2.0 comment period.
- Generic "this is bad" / "this is good" feedback without a section reference.

## Maintainers

See [`CODEOWNERS`](./CODEOWNERS) for who reviews what.

For private comments — unannounced product names, legal-sensitive concerns from counsel, vendor-confidential details — email `evp@etymolt.com`. Private comments still count toward the comment record; we'll cite them as "anonymous comment received [date], summarized as [...]" in the consolidated digest.
