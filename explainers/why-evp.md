# Why EVP/1?

A plain-language explainer of why the Etymolt Verdict Protocol exists.

## The problem

In 2026, AI naming tools generate millions of brand-name candidates a week. ChatGPT will write you a startup name in a sentence. Claude will produce ten. Namelix will list a hundred. Looka will brand them with logos. Squadhelp will sell you ones that have already been vetted.

Almost none of these tools check whether the names are actually safe to use.

The result: founders ship a name, fall in love with it, register the domain, file the trademark — and three months later receive a cease-and-desist letter. The IP press calls this an epidemic in 2025-2026. The rebrand cost is $25,000-$500,000.

## What "safe to use" means

A name is safe to use if:

1. **Trademark** — no senior registered or common-law mark in your classes.
2. **Domain** — the .com (or a credible alternative TLD) is available.
3. **Cultural** — no offensive, regulated, or reserved meaning in your target markets.
4. **Sound** — the phonetic pattern is distinctive enough to function as a wordmark.
5. **Pronunciation** — fluent speakers can say it on first read.

These are the five canonical axes EVP/1 codifies. (See [EVP-0001](../evps/EVP-0001-five-axes.md).)

## The interoperability problem

Several companies have started shipping clearance verdicts in incompatible formats:

- One issuer returns `{"safe": true, "score": 87}`.
- Another returns `{"verdict": "GREEN", "checks": {...}}`.
- A third returns 8 axes including ones no founder cares about.
- None of them sign their verdicts.
- None of them carry a stated freshness window.
- None of them say "this is a clearance signal, not legal advice."

A verdict that can be silently modified, that doesn't say what it isn't, and that's incomparable to other issuers' verdicts — is a verdict that no enterprise integrator will trust.

## What EVP/1 fixes

EVP/1 specifies:

- **A wire format** — every conformant verdict has the same shape: five axes, a composite verdict, a confidence interval, a verbatim disclaimer, a signature.
- **A status taxonomy** — `CLEAR / CAUTION / BLOCKED / INSUFFICIENT_SIGNAL / UNKNOWN`. The presence of `INSUFFICIENT_SIGNAL` as a load-bearing state is the most important honesty move in the spec.
- **A signature protocol** — Ed25519 over JCS-canonicalized payloads. Any verdict's authenticity is verifiable by anyone who has the issuer's public key.
- **A disclaimer requirement** — every consumer that renders a verdict MUST render the disclaimer verbatim. The Bureau Model anchor.

What EVP/1 does NOT specify:

- How a clearance signal is computed.
- Which registries an issuer MUST consult.
- What a verdict costs.
- Any legal opinion.

EVP/1 is the contract between producer and consumer. The contract that doesn't yet exist is the problem.

## Why open?

EVP/1 is CC-BY-4.0. The trust graph that makes brand-clearance verdicts useful is a network good: it compounds the more issuers, the more consumers, and the more downstream tools adopt it. If it were vendor-locked it wouldn't compound. So it's not.

Etymolt operates the reference issuer at `api.etymolt.com/v1/verify`. We expect (and welcome) other issuers — including direct competitors — to implement the same protocol. The protocol's value to Etymolt is that it exists, not that we own it.

## What's next

The 90-day public comment period (2026-06-10 → 2026-09-10) is the formal window for normative feedback. After that, v1.1 incorporates accepted changes; v2.0 work convenes a working group with at least three independent issuers.

If you're building anything that produces or consumes brand-name clearance verdicts, this protocol is for you. File issues, propose changes, ship implementations. The repo is the forum.
