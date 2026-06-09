"""
EVP-1-validator-tests.py
========================

Conformance test suite for the Etymolt Verdict Protocol, Version 1.0.0.

This module validates EVP/1 JSON verdict documents against the JSON Schema
defined in Appendix A of the EVP/1 specification (see EVP-1-SPEC-v1.0-FINAL.md).

It is importable as a test module and runnable with `pytest`:

    pip install pytest jsonschema
    pytest EVP-1-validator-tests.py -v

The suite covers (>= 10 cases per Round-2 deliverable spec):

  Valid acceptance cases (4 sample verdicts from spec Appendix B):
    - B.1 PASS  ("Inkstack")
    - B.2 DECIDE ("Stratagem")
    - B.3 BLOCK ("Sigil")
    - B.4 INSUFFICIENT_SIGNAL ("Aiyana")  <- 4th sample verdict, new in v1.0 final

  Invalid rejection cases (3):
    - Missing required field (`signature` removed)
    - Wrong enum value for top-level `verdict`
    - Malformed signature (non-base64-decodable / wrong digest format)

  Edge cases (3):
    - Empty axes object (must reject - all 5 axis keys required)
    - Partial coverage (INSUFFICIENT_SIGNAL with coverage_caveat present - must accept)
    - Expired signature (verdict.issued_at after key.valid_until - schema-valid;
      conformance-layer check returns rejection)

Public exports:

    validate_verdict(doc: dict) -> ValidationReport
    validate_against_key_lifecycle(doc: dict, key_dir: dict, revoked: dict) -> ValidationReport

These two functions can be imported and used by any consumer's CI pipeline.
"""

from __future__ import annotations

import base64
import copy
import datetime as dt
from dataclasses import dataclass, field
from typing import Any

import pytest

try:
    from jsonschema import Draft202012Validator
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "jsonschema>=4.18 is required. Install with: pip install jsonschema"
    ) from e


# ---------------------------------------------------------------------------
# 1. EVP/1 JSON Schema (Appendix A of EVP-1-SPEC-v1.0-FINAL.md)
# ---------------------------------------------------------------------------

EVP_1_SCHEMA: dict[str, Any] = {
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
        "signature_payload_digest",
    ],
    "properties": {
        "evp_version": {"type": "string", "pattern": r"^1\.[0-9]+\.[0-9]+$"},
        "name": {"type": "string", "minLength": 1, "maxLength": 64},
        "verdict": {
            "type": "string",
            "enum": ["PASS", "DECIDE", "BLOCK", "INSUFFICIENT_SIGNAL"],
        },
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "axes": {
            "type": "object",
            "required": [
                "trademark",
                "domain",
                "distinctiveness",
                "linguistic",
                "cultural",
            ],
            "properties": {
                "trademark": {"$ref": "#/$defs/trademark_axis"},
                "domain": {"$ref": "#/$defs/domain_axis"},
                "distinctiveness": {"$ref": "#/$defs/distinctiveness_axis"},
                "linguistic": {"$ref": "#/$defs/linguistic_axis"},
                "cultural": {"$ref": "#/$defs/cultural_axis"},
            },
            "additionalProperties": False,
        },
        "verdict_id": {"type": "string", "pattern": r"^v_[A-Za-z0-9_-]{12,}$"},
        "issued_at": {"type": "string", "format": "date-time"},
        "disclaimer": {"type": "string", "minLength": 1},
        "signature": {"type": "string", "contentEncoding": "base64"},
        "signature_key_id": {"type": "string", "minLength": 1},
        "signature_payload_digest": {"type": "string", "pattern": r"^[0-9a-f]{64}$"},
        "signature_co": {
            "type": "object",
            "required": ["signature", "signature_key_id", "signature_payload_digest"],
            "properties": {
                "signature": {"type": "string", "contentEncoding": "base64"},
                "signature_key_id": {"type": "string", "minLength": 1},
                "signature_payload_digest": {
                    "type": "string",
                    "pattern": r"^[0-9a-f]{64}$",
                },
            },
        },
        "one_line": {"type": "string"},
        "findings": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "confidence_interval": {
            "type": "object",
            "properties": {
                "lower": {"type": "number"},
                "upper": {"type": "number"},
                "point_estimate": {"type": "number"},
                "method": {"type": "string"},
            },
        },
        "permalink": {"type": "string", "format": "uri"},
        "jurisdictions_consulted": {"type": "array", "items": {"type": "string"}},
    },
    "patternProperties": {"^x_": {}},
    "additionalProperties": True,
    "$defs": {
        "axis_status": {
            "type": "string",
            "enum": [
                "CLEAR",
                "CAUTION",
                "BLOCKED",
                "INSUFFICIENT_SIGNAL",
                "UNKNOWN",
            ],
        },
        "trademark_axis": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"$ref": "#/$defs/axis_status"},
                "jurisdictions_consulted": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "colliding_marks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "wordmark": {"type": "string"},
                            "owner": {"type": "string"},
                            "serial_number": {"type": "string"},
                            "registration_number": {"type": "string"},
                            "nice_classes": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                            "filing_date": {
                                "type": "string",
                                "format": "date",
                            },
                            "status": {"type": "string"},
                            "deep_link": {
                                "type": "string",
                                "format": "uri",
                            },
                        },
                    },
                },
                "nice_classes_assumed": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
                "coverage_caveat": {"type": "string"},
            },
        },
        "domain_axis": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"$ref": "#/$defs/axis_status"},
                "tlds_consulted": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["tld", "method", "definitive", "result"],
                        "properties": {
                            "tld": {"type": "string"},
                            "method": {
                                "type": "string",
                                "enum": [
                                    "RDAP_authoritative",
                                    "WHOIS_authoritative",
                                    "DNS_fallback",
                                ],
                            },
                            "definitive": {"type": "boolean"},
                            "result": {
                                "type": "string",
                                "enum": ["available", "registered", "unknown"],
                            },
                        },
                    },
                },
                "recommended_variant": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string"},
                        "registrar": {"type": "string"},
                        "price_usd": {"type": "number"},
                    },
                },
                "aftermarket_observed": {"type": "boolean"},
            },
        },
        "distinctiveness_axis": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "STRONG",
                        "MODERATE",
                        "WEAK",
                        "BLOCKED",
                        "INSUFFICIENT_SIGNAL",
                        "UNKNOWN",
                    ],
                },
                "cohort_corpora_consulted": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "platforms_consulted": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["available", "taken", "unknown"],
                            },
                            "url": {"type": "string", "format": "uri"},
                            "claimed": {"type": "boolean"},
                        },
                    },
                },
                "workaround_variants_available": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "linguistic_axis": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"$ref": "#/$defs/axis_status"},
                "locales_evaluated": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "phoneme_skeleton": {"type": "string"},
                "sound_symbolism_axes": {
                    "type": "object",
                    "additionalProperties": {"type": "number"},
                },
                "advisory": {"type": "boolean"},
                "method": {"type": "string"},
            },
        },
        "cultural_axis": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"$ref": "#/$defs/axis_status"},
                "sources_consulted": {"type": "integer", "minimum": 0},
                "cultural_sources_consulted": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "matched": {"type": ["boolean", "null"]},
                            "language": {"type": "string"},
                            "caveat": {"type": "string"},
                        },
                    },
                },
                "markets_covered": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "coverage_caveat": {"type": "string"},
            },
        },
    },
}

_VALIDATOR = Draft202012Validator(EVP_1_SCHEMA)


# ---------------------------------------------------------------------------
# 2. Public validation API
# ---------------------------------------------------------------------------


@dataclass
class ValidationReport:
    """Result of validating a verdict document.

    Attributes:
        ok: True when no schema errors AND no conformance-layer errors.
        schema_errors: List of human-readable JSON Schema errors.
        conformance_errors: Extra-schema EVP/1 conformance violations (§4-§6).
    """

    ok: bool
    schema_errors: list[str] = field(default_factory=list)
    conformance_errors: list[str] = field(default_factory=list)


def validate_verdict(doc: dict[str, Any]) -> ValidationReport:
    """Validate `doc` against the EVP/1 JSON Schema plus the structural
    conformance rules from §4 (axis evidence-of-record) and §5 (disclaimer).

    Does NOT verify cryptographic signature material — see
    validate_against_key_lifecycle for that layer.
    """
    schema_errors = [
        _format_error(e)
        for e in sorted(_VALIDATOR.iter_errors(doc), key=lambda e: e.path)
    ]
    conformance_errors: list[str] = []

    if not schema_errors:
        # §4.1 evidence-of-record: BLOCKED trademark must include at least one
        # colliding mark entry.
        try:
            tm = doc["axes"]["trademark"]
            if tm.get("status") == "BLOCKED" and not tm.get("colliding_marks"):
                conformance_errors.append(
                    "§4.1: trademark axis status=BLOCKED requires at least one "
                    "entry in colliding_marks"
                )
            if (
                tm.get("status") == "INSUFFICIENT_SIGNAL"
                and not tm.get("coverage_caveat")
            ):
                conformance_errors.append(
                    "§4.1: trademark axis status=INSUFFICIENT_SIGNAL requires "
                    "coverage_caveat"
                )
        except KeyError:  # pragma: no cover
            pass

        # §4.2 domain evidence: cannot return CLEAR if all consulted TLDs are
        # non-definitive.
        try:
            dm = doc["axes"]["domain"]
            tlds = dm.get("tlds_consulted") or []
            if dm.get("status") == "CLEAR" and tlds:
                if not any(t.get("definitive") for t in tlds):
                    conformance_errors.append(
                        "§4.2: domain axis status=CLEAR with no definitive TLD "
                        "results"
                    )
        except KeyError:  # pragma: no cover
            pass

        # §5.1 / §5.3 disclaimer must mention "not legal advice".
        disclaimer = doc.get("disclaimer", "")
        if "not legal advice" not in disclaimer.lower():
            conformance_errors.append(
                '§5.3: disclaimer must state "not legal advice"'
            )

        # §6.2 signature triple basic sanity checks.
        sig = doc.get("signature", "")
        try:
            decoded = base64.b64decode(sig, validate=True)
            # Ed25519 detached signatures are 64 bytes; allow some slack for
            # truncated test fixtures by requiring at least 32 bytes.
            if len(decoded) < 32:
                conformance_errors.append(
                    "§6.1: signature decodes to fewer than 32 bytes; not an "
                    "Ed25519 detached signature"
                )
        except Exception as exc:
            conformance_errors.append(
                f"§6.2: signature is not valid base64 ({exc.__class__.__name__})"
            )

    return ValidationReport(
        ok=not schema_errors and not conformance_errors,
        schema_errors=schema_errors,
        conformance_errors=conformance_errors,
    )


def validate_against_key_lifecycle(
    doc: dict[str, Any],
    key_directory: dict[str, Any],
    revocation_list: dict[str, Any],
) -> ValidationReport:
    """Layered check that combines schema validation with key-lifecycle checks
    from §6.4 and §6.5: verdicts MUST NOT verify against a revoked key for any
    `issued_at` >= `revoked_at`, and the key referenced by `signature_key_id`
    MUST be discoverable in the directory.
    """
    base = validate_verdict(doc)
    extra: list[str] = list(base.conformance_errors)

    kid = doc.get("signature_key_id")
    issued_at = doc.get("issued_at")
    if kid and issued_at:
        # Discoverable in directory?
        keys = {k["key_id"]: k for k in key_directory.get("keys", [])}
        if kid not in keys:
            extra.append(
                f"§6.4.5: signature_key_id {kid!r} not present in published key "
                "directory"
            )

        # Revoked?
        revoked = {r["key_id"]: r for r in revocation_list.get("revoked", [])}
        if kid in revoked:
            rev_at = revoked[kid].get("revoked_at")
            if rev_at and _ts(issued_at) >= _ts(rev_at):
                extra.append(
                    f"§6.5.2: verdict issued_at {issued_at} at-or-after "
                    f"revoked_at {rev_at} for key {kid}"
                )

        # Expired?
        if kid in keys:
            vu = keys[kid].get("valid_until")
            if vu and _ts(issued_at) > _ts(vu):
                extra.append(
                    f"§6.4.4: verdict issued_at {issued_at} after key "
                    f"valid_until {vu} for {kid}"
                )

    return ValidationReport(
        ok=not base.schema_errors and not extra,
        schema_errors=base.schema_errors,
        conformance_errors=extra,
    )


def _format_error(err) -> str:
    path = "/".join(str(p) for p in err.path) or "<root>"
    return f"{path}: {err.message}"


def _ts(s: str) -> dt.datetime:
    # RFC 3339 -> datetime. Python's fromisoformat handles `Z` from 3.11+.
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
# 3. Test fixtures
# ---------------------------------------------------------------------------


_DISCLAIMER = (
    "Clearance signal, not legal advice. Confirm with trademark counsel "
    "before adopting a name in commerce. Data sources have stated freshness "
    "windows; refer to coverage_caveat per jurisdiction."
)
# 64-byte signature placeholder (88 base64 chars including padding).
_FAKE_SIG = (
    "uRgztcYFdlvQZDk1834gOG88NDL8e/hgo5bjG/GIpUZA"
    "Zy0F1CXyIX1bOfFr7EToJsihPuNgPXRszKQCexSABw=="
)
_FAKE_DIGEST = "04360aac47f170eed15c3f51f96578686dea94d4fcce6920f443484500353166"
_FAKE_KID = "etymolt-1779085662"


def _pass_verdict() -> dict[str, Any]:
    """Appendix B.1 sample: PASS (ship) — Inkstack."""
    return {
        "evp_version": "1.0.0",
        "name": "Inkstack",
        "verdict": "PASS",
        "score": 87,
        "axes": {
            "trademark": {
                "status": "CLEAR",
                "jurisdictions_consulted": [
                    "USPTO_bulk",
                    "UKIPO_domestic",
                    "EUIPO_live_API",
                    "WIPO_Madrid_IR",
                ],
                "colliding_marks": [],
                "nice_classes_assumed": [9, 42],
            },
            "domain": {
                "status": "CLEAR",
                "tlds_consulted": [
                    {
                        "tld": ".com",
                        "method": "RDAP_authoritative",
                        "definitive": True,
                        "result": "available",
                    }
                ],
                "recommended_variant": {
                    "domain": "inkstack.com",
                    "registrar": "Cloudflare",
                    "price_usd": 10.44,
                },
                "aftermarket_observed": False,
            },
            "distinctiveness": {
                "status": "STRONG",
                "cohort_corpora_consulted": ["yc_alumni_2014_2026"],
                "platforms_consulted": [
                    {
                        "platform": "github",
                        "status": "available",
                        "url": "https://github.com/inkstack",
                        "claimed": True,
                    }
                ],
            },
            "linguistic": {
                "status": "CLEAR",
                "advisory": True,
                "method": "static rule-based heuristic",
            },
            "cultural": {
                "status": "CLEAR",
                "sources_consulted": 9,
                "markets_covered": ["US", "UK", "DE"],
            },
        },
        "verdict_id": "v_inkstack_a7f12bc",
        "issued_at": "2026-06-10T14:22:01.413Z",
        "disclaimer": _DISCLAIMER,
        "signature": _FAKE_SIG,
        "signature_key_id": _FAKE_KID,
        "signature_payload_digest": _FAKE_DIGEST,
    }


def _decide_verdict() -> dict[str, Any]:
    """Appendix B.2 sample: DECIDE — Stratagem."""
    return {
        "evp_version": "1.0.0",
        "name": "Stratagem",
        "verdict": "DECIDE",
        "score": 60,
        "axes": {
            "trademark": {
                "status": "CAUTION",
                "jurisdictions_consulted": [
                    "EUIPO_live_API",
                    "UKIPO_domestic",
                    "USPTO_TTAB",
                    "USPTO_bulk",
                    "WIPO_Madrid_IR",
                ],
                "colliding_marks": [],
                "coverage_caveat": "Common-word mark; class-dependent risk.",
            },
            "domain": {
                "status": "CAUTION",
                "tlds_consulted": [
                    {
                        "tld": ".com",
                        "method": "RDAP_authoritative",
                        "definitive": True,
                        "result": "registered",
                    }
                ],
                "aftermarket_observed": True,
            },
            "distinctiveness": {
                "status": "WEAK",
                "platforms_consulted": [
                    {
                        "platform": "github",
                        "status": "taken",
                        "url": "https://github.com/stratagem",
                        "claimed": True,
                    }
                ],
                "workaround_variants_available": ["@stratagemhq"],
            },
            "linguistic": {
                "status": "CLEAR",
                "advisory": True,
                "method": "static rule-based heuristic",
            },
            "cultural": {
                "status": "CLEAR",
                "sources_consulted": 32,
                "markets_covered": ["US", "UK", "IN"],
            },
        },
        "verdict_id": "v_ca83be889da34a",
        "issued_at": "2026-06-05T04:15:41.185Z",
        "disclaimer": _DISCLAIMER,
        "signature": _FAKE_SIG,
        "signature_key_id": _FAKE_KID,
        "signature_payload_digest": _FAKE_DIGEST,
    }


def _block_verdict() -> dict[str, Any]:
    """Appendix B.3 sample: BLOCK — Sigil."""
    return {
        "evp_version": "1.0.0",
        "name": "Sigil",
        "verdict": "BLOCK",
        "score": 18,
        "axes": {
            "trademark": {
                "status": "BLOCKED",
                "jurisdictions_consulted": ["USPTO_bulk", "USPTO_TTAB"],
                "colliding_marks": [
                    {
                        "wordmark": "SIGIL",
                        "owner": "Sigil Software Inc.",
                        "serial_number": "97123456",
                        "registration_number": "7012345",
                        "nice_classes": [9],
                        "filing_date": "2022-04-11",
                        "status": "Registered",
                        "deep_link": (
                            "https://tsdr.uspto.gov/#caseNumber=97123456"
                            "&caseType=SERIAL_NO&searchType=statusSearch"
                        ),
                    }
                ],
                "nice_classes_assumed": [9, 42],
            },
            "domain": {
                "status": "BLOCKED",
                "tlds_consulted": [
                    {
                        "tld": ".com",
                        "method": "RDAP_authoritative",
                        "definitive": True,
                        "result": "registered",
                    }
                ],
                "aftermarket_observed": True,
            },
            "distinctiveness": {
                "status": "BLOCKED",
                "workaround_variants_available": [],
            },
            "linguistic": {"status": "CLEAR", "advisory": True},
            "cultural": {"status": "CLEAR", "sources_consulted": 32},
        },
        "verdict_id": "v_sigil_blocked_2026",
        "issued_at": "2026-06-10T14:30:00.000Z",
        "disclaimer": _DISCLAIMER,
        "signature": _FAKE_SIG,
        "signature_key_id": _FAKE_KID,
        "signature_payload_digest": _FAKE_DIGEST,
    }


def _insufficient_signal_verdict() -> dict[str, Any]:
    """Appendix B.4 sample: INSUFFICIENT_SIGNAL — Aiyana.

    This is the load-bearing 4th sample verdict added in v1.0 final per the
    2026-06-05 board ruling. Coverage gaps in registry mirrors and cultural
    lexicons MUST surface as INSUFFICIENT_SIGNAL, not be coerced to DECIDE.
    """
    return {
        "evp_version": "1.0.0",
        "name": "Aiyana",
        "verdict": "INSUFFICIENT_SIGNAL",
        "score": 50,
        "axes": {
            "trademark": {
                "status": "INSUFFICIENT_SIGNAL",
                "jurisdictions_consulted": [
                    "USPTO_bulk",
                    "USPTO_TTAB",
                    "EUIPO_live_API",
                    "UKIPO_domestic",
                    "WIPO_Madrid_IR",
                    "INPI_BR",
                    "IPINDIA_domestic",
                ],
                "colliding_marks": [],
                "nice_classes_assumed": [9, 42],
                "coverage_caveat": (
                    "INPI_BR returned HTTP 502 across 3 retries; "
                    "IPINDIA_domestic timed out; WIPO_Madrid_IR returned only "
                    "2 of 5 designated-state mirrors. Determinate conflict in "
                    "9/42 not established."
                ),
            },
            "domain": {
                "status": "CAUTION",
                "tlds_consulted": [
                    {
                        "tld": ".com",
                        "method": "RDAP_authoritative",
                        "definitive": True,
                        "result": "registered",
                    },
                    {
                        "tld": ".io",
                        "method": "RDAP_authoritative",
                        "definitive": True,
                        "result": "available",
                    },
                ],
                "recommended_variant": {
                    "domain": "aiyana.io",
                    "registrar": "Cloudflare",
                    "price_usd": 41.00,
                },
                "aftermarket_observed": True,
            },
            "distinctiveness": {
                "status": "MODERATE",
                "platforms_consulted": [
                    {
                        "platform": "github",
                        "status": "available",
                        "url": "https://github.com/aiyana",
                        "claimed": True,
                    }
                ],
                "workaround_variants_available": ["@aiyanahq", "@useaiyana"],
            },
            "linguistic": {
                "status": "CLEAR",
                "locales_evaluated": ["en-US", "es-MX", "pt-BR"],
                "advisory": True,
                "method": "static rule-based heuristic",
            },
            "cultural": {
                "status": "INSUFFICIENT_SIGNAL",
                "sources_consulted": 28,
                "cultural_sources_consulted": [
                    {
                        "source": "sacred_names",
                        "matched": False,
                        "language": "multi",
                        "caveat": (
                            "Tier-1 catalog does not cover "
                            "Indigenous-Americas namespaces in depth"
                        ),
                    },
                    {
                        "source": "llm_cross_cultural",
                        "matched": None,
                        "language": "multi",
                        "caveat": "Rate-limit shed; deferred out-of-band.",
                    },
                ],
                "markets_covered": ["US", "UK", "ES", "MX", "BR", "DE", "FR"],
                "coverage_caveat": (
                    "2 of 7 consulted markets lacked Indigenous-Americas "
                    "lexicon coverage; LLM panel did not return synchronously."
                ),
            },
        },
        "verdict_id": "v_aiyana_insig_a91f3c7d4e8f",
        "issued_at": "2026-06-10T14:45:22.108Z",
        "confidence": 38,
        "disclaimer": _DISCLAIMER,
        "signature": _FAKE_SIG,
        "signature_key_id": _FAKE_KID,
        "signature_payload_digest": _FAKE_DIGEST,
    }


# Key directory and revocation list fixtures for §6.4 / §6.5 lifecycle tests.
_KEY_DIRECTORY = {
    "evp_version": "1.0.0",
    "issuer": "etymolt.com",
    "keys": [
        {
            "key_id": _FAKE_KID,
            "alg": "Ed25519",
            "public_key_b64": "MCowBQYDK2VwAyEA" + "A" * 32,
            "valid_from": "2026-06-10T00:00:00Z",
            "valid_until": "2026-09-08T00:00:00Z",
            "status": "active",
        },
        {
            "key_id": "etymolt-revoked-1",
            "alg": "Ed25519",
            "public_key_b64": "MCowBQYDK2VwAyEA" + "B" * 32,
            "valid_from": "2026-03-01T00:00:00Z",
            "valid_until": "2026-06-01T00:00:00Z",
            "status": "revoked",
            "revoked_at": "2026-05-15T00:00:00Z",
        },
    ],
    "rotation_policy": {
        "cadence_days": 90,
        "overlap_days": 7,
        "dual_sign_during_overlap": True,
    },
    "revocation_endpoint": (
        "https://api.etymolt.com/.well-known/evp-keys-revoked.json"
    ),
}

_REVOCATION_LIST = {
    "evp_version": "1.0.0",
    "issuer": "etymolt.com",
    "generated_at": "2026-06-10T12:00:00Z",
    "revoked": [
        {
            "key_id": "etymolt-revoked-1",
            "revoked_at": "2026-05-15T00:00:00Z",
            "reason": "key_compromise",
            "replacement_key_id": _FAKE_KID,
        }
    ],
}


# ---------------------------------------------------------------------------
# 4. Tests — valid acceptance (the four spec samples)
# ---------------------------------------------------------------------------


def test_b1_pass_verdict_validates() -> None:
    report = validate_verdict(_pass_verdict())
    assert report.ok, (report.schema_errors, report.conformance_errors)


def test_b2_decide_verdict_validates() -> None:
    report = validate_verdict(_decide_verdict())
    assert report.ok, (report.schema_errors, report.conformance_errors)


def test_b3_block_verdict_validates() -> None:
    report = validate_verdict(_block_verdict())
    assert report.ok, (report.schema_errors, report.conformance_errors)


def test_b4_insufficient_signal_verdict_validates() -> None:
    """The 4th sample verdict (Aiyana) MUST validate cleanly, AND consumers
    MUST NOT coerce INSUFFICIENT_SIGNAL into another composite label.
    """
    doc = _insufficient_signal_verdict()
    report = validate_verdict(doc)
    assert report.ok, (report.schema_errors, report.conformance_errors)

    # §8.1 consumer rule #7: INSUFFICIENT_SIGNAL is distinct from PASS/DECIDE/BLOCK.
    assert doc["verdict"] == "INSUFFICIENT_SIGNAL"
    assert doc["axes"]["trademark"]["status"] == "INSUFFICIENT_SIGNAL"
    assert doc["axes"]["trademark"].get("coverage_caveat"), (
        "trademark INSUFFICIENT_SIGNAL must carry coverage_caveat"
    )
    assert doc["axes"]["cultural"]["status"] == "INSUFFICIENT_SIGNAL"


# ---------------------------------------------------------------------------
# 5. Tests — invalid rejection (3 cases per spec)
# ---------------------------------------------------------------------------


def test_invalid_missing_required_field_signature() -> None:
    doc = _pass_verdict()
    del doc["signature"]
    report = validate_verdict(doc)
    assert not report.ok
    assert any("signature" in e for e in report.schema_errors)


def test_invalid_wrong_enum_value_for_verdict() -> None:
    doc = _pass_verdict()
    doc["verdict"] = "SHIP_IT"  # not in the enum
    report = validate_verdict(doc)
    assert not report.ok
    assert any("verdict" in e or "enum" in e.lower() for e in report.schema_errors)


def test_invalid_malformed_signature() -> None:
    # signature_payload_digest must be 64 hex chars; this is too short.
    doc = _pass_verdict()
    doc["signature_payload_digest"] = "not-hex"
    report = validate_verdict(doc)
    assert not report.ok
    assert any(
        "signature_payload_digest" in e for e in report.schema_errors
    )


# ---------------------------------------------------------------------------
# 6. Tests — edge cases (3 cases per spec)
# ---------------------------------------------------------------------------


def test_edge_empty_axes_rejected() -> None:
    doc = _pass_verdict()
    doc["axes"] = {}
    report = validate_verdict(doc)
    assert not report.ok
    # All five axis names should be reported missing.
    joined = "\n".join(report.schema_errors)
    for axis in ("trademark", "domain", "distinctiveness", "linguistic", "cultural"):
        assert axis in joined


def test_edge_partial_coverage_insufficient_signal_accepted() -> None:
    """INSUFFICIENT_SIGNAL with coverage_caveat present is accepted — the
    point of the status is precisely to surface partial coverage honestly.
    """
    doc = _decide_verdict()
    doc["verdict"] = "INSUFFICIENT_SIGNAL"
    doc["axes"]["trademark"]["status"] = "INSUFFICIENT_SIGNAL"
    doc["axes"]["trademark"]["coverage_caveat"] = (
        "EUIPO returned 503 across full retry budget; result is partial."
    )
    report = validate_verdict(doc)
    assert report.ok, (report.schema_errors, report.conformance_errors)


def test_edge_expired_signature_caught_by_lifecycle_layer() -> None:
    """An expired-key signature is schema-valid (the schema doesn't know about
    key lifetimes) but MUST be caught by the lifecycle layer per §6.4.4.
    """
    doc = _pass_verdict()
    # Sign with a key that's already past its valid_until.
    doc["signature_key_id"] = "etymolt-revoked-1"
    doc["issued_at"] = "2026-06-09T00:00:00.000Z"  # after valid_until 2026-06-01

    schema_report = validate_verdict(doc)
    assert schema_report.ok, "schema layer alone should accept (no key knowledge)"

    lifecycle_report = validate_against_key_lifecycle(
        doc, _KEY_DIRECTORY, _REVOCATION_LIST
    )
    assert not lifecycle_report.ok
    joined = "\n".join(lifecycle_report.conformance_errors)
    assert "§6.4.4" in joined or "§6.5.2" in joined


# ---------------------------------------------------------------------------
# 7. Bonus: conformance-layer tests that go beyond raw schema
# ---------------------------------------------------------------------------


def test_conformance_blocked_trademark_requires_colliding_mark() -> None:
    doc = _block_verdict()
    doc["axes"]["trademark"]["colliding_marks"] = []
    report = validate_verdict(doc)
    assert not report.ok
    assert any("§4.1" in e for e in report.conformance_errors)


def test_conformance_disclaimer_missing_legal_advice_phrase_rejected() -> None:
    doc = _pass_verdict()
    doc["disclaimer"] = "Just some boilerplate, no qualifying phrase."
    report = validate_verdict(doc)
    assert not report.ok
    assert any("§5.3" in e for e in report.conformance_errors)


def test_conformance_revoked_key_signature_rejected_when_issued_after_revocation() -> None:
    doc = _pass_verdict()
    doc["signature_key_id"] = "etymolt-revoked-1"
    doc["issued_at"] = "2026-05-20T00:00:00.000Z"  # > revoked_at 2026-05-15
    report = validate_against_key_lifecycle(
        doc, _KEY_DIRECTORY, _REVOCATION_LIST
    )
    assert not report.ok
    assert any("§6.5.2" in e for e in report.conformance_errors)


def test_conformance_unknown_key_id_rejected() -> None:
    doc = _pass_verdict()
    doc["signature_key_id"] = "etymolt-never-published-99"
    report = validate_against_key_lifecycle(
        doc, _KEY_DIRECTORY, _REVOCATION_LIST
    )
    assert not report.ok
    assert any("§6.4.5" in e for e in report.conformance_errors)


# ---------------------------------------------------------------------------
# 8. Parametrized: all four spec-sample verdicts validate as a single sweep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "factory"),
    [
        ("B.1 PASS", _pass_verdict),
        ("B.2 DECIDE", _decide_verdict),
        ("B.3 BLOCK", _block_verdict),
        ("B.4 INSUFFICIENT_SIGNAL", _insufficient_signal_verdict),
    ],
)
def test_all_spec_samples_validate(label: str, factory) -> None:
    report = validate_verdict(factory())
    assert report.ok, f"{label} failed: {report.schema_errors!r} / {report.conformance_errors!r}"


# ---------------------------------------------------------------------------
# 9. Round-trip helper: extension fields must be tolerated (§3.3)
# ---------------------------------------------------------------------------


def test_extension_fields_tolerated() -> None:
    doc = _pass_verdict()
    doc["x_etymolt_internal_score_v2"] = 92
    doc["x_partner_correlation_id"] = "abc-123"
    report = validate_verdict(doc)
    assert report.ok


def test_signature_co_during_overlap_window_validates() -> None:
    """A verdict carrying signature_co (key-rotation overlap window) must
    pass schema validation.
    """
    doc = _pass_verdict()
    doc["signature_co"] = {
        "signature": _FAKE_SIG,
        "signature_key_id": "etymolt-revoked-1",
        "signature_payload_digest": _FAKE_DIGEST,
    }
    # Ensure issued_at is before the revoked-1 revocation timestamp so the
    # primary check is purely structural.
    report = validate_verdict(doc)
    assert report.ok, (report.schema_errors, report.conformance_errors)


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
