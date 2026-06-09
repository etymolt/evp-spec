# Governance

EVP/1 is currently a **single-editor specification** under Etymolt Inc.'s stewardship. This is honest framing: a single editor moves faster, and at this stage of the brand-name-clearance ecosystem the cost of slow movement is higher than the cost of an under-debated change.

The protocol is published under [CC-BY-4.0](./LICENSE) for a reason. The intended trajectory is to evolve from single-editor to working-group as the implementer base grows.

## Evolution stages

| Stage | Governance | Window |
|---|---|---|
| **1.0 public comment** | Single editor. Public comment-period intake. Weekly digest. | **Now → 2026-09-10** |
| **1.0 release** | Same. Editor lands accepted changes; broader implementer feedback drives 1.1. | 2026-09-10 → 2026-11-15 |
| **1.1 release** | Single editor. **Two additional reviewers** drawn from implementing organizations sign off on normative changes. | 2026-11-15 → 2027-Q2 |
| **2.0 work** | **Working group** convened from at least three independent issuers, with rotating chair. Etymolt holds editorial responsibility but does not hold veto. | Tentatively H2 2027 |

If you want to participate in 1.1 review or in the 2.0 working group, open an issue using the `comment-on-section` template and tag it `governance`. We'd rather over-include than under-include.

## Decision rules during 1.0

The editor commits to:

| Activity | SLA |
|---|---|
| Acknowledge every issue with a triage holding label | **5 business days** |
| Apply a triage label (`accepted` / `clarification-needed` / `out-of-scope` / `editorial` / `deferred-to-1.1`) | **14 business days** |
| Publish weekly comment-period digest | Every Friday at [etymolt.com/docs/verdict-protocol/changelog](https://etymolt.com/docs/verdict-protocol/changelog) |
| Land editorial corrections (typos, broken links, clarifications) | Within 5 business days of triage |
| Land normative changes accepted for 1.1 | 1.1 draft by 2026-10-15; release by 2026-11-15 |

"Business days" are Mon–Fri excluding US federal holidays. The editor is based on US Pacific time; expect some clock skew on Fridays.

If you don't get an acknowledgment in 5 business days, **bump the issue or email `hello@etymolt.com` directly**. Process failures should be loud.

## What "accepted" means

A normative change labeled `accepted` will land in the next 1.x release **unless** the editor or a 1.1+ reviewer identifies a blocking concern. "Accepted" is not "committed" — it's "we agree this should land, pending implementation review."

## Conflict resolution

If two comments propose mutually incompatible changes to the same section, the editor will:

1. Publish both, side-by-side, in the next weekly digest.
2. Solicit reasoning from each commenter and any implementers affected.
3. Decide. Decisions are documented in the digest with the rationale.

There is no formal voting mechanism in 1.x. There will be one in 2.x.

## What governance does NOT cover

- Etymolt's commercial pricing, business model, or proprietary data corpora. Those are out of scope for the protocol.
- Third-party EVP/1 issuers' internal policies. Each issuer governs its own implementation.
- Implementations of EVP/1 in any language — those are licensed independently of the spec.

## Antitrust posture

EVP/1 is an open specification. Its adoption by multiple commercial issuers is encouraged. The editor will not use its position to favor Etymolt's commercial interests in normative decisions. If you believe a decision violates this posture, file an issue with the `governance` label.

## Maintainers

The current editor and reviewer list lives in [`CODEOWNERS`](./CODEOWNERS).

## Hosted by

Etymolt Inc. (Dear One Technologies Pvt Ltd) is the current steward. Hosting transfer to a neutral foundation (LF Projects, OpenSSF, or a new dedicated foundation) is on the 2.0 roadmap.
