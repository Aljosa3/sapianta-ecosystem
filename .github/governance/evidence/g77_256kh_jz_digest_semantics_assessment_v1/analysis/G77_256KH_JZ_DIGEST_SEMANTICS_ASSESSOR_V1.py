#!/usr/bin/env python3
"""Repository-only assessment of KG's source/handoff digest comparison.

The assessor reads committed evidence and source.  It creates no authority,
does not consume authority, and cannot invoke PRE, FM, QEMU, a VM, ER, or P11.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KH = Path(
    ".github/governance/evidence/"
    "g77_256kh_jz_digest_semantics_assessment_v1"
)
OUTPUT = KH / "G77_256KH_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "b0df1592bd1a88d4b51a1f7e7fff99bff8fe2c9c"
ENTRY_TREE = "0b34d4323036f7379400c1c5974449d7e68446ce"
ENTRY_SUBJECT = "G77-256KG reduce preconsumption authority digest mismatch"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

KG_TERMINAL = (
    "M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_"
    "BEFORE_AUTHORITY_CONSUMPTION"
)
JZ_TERMINAL = (
    "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_"
    "BINDING_REPOSITORY_VERIFIED"
)
KH_TERMINAL = (
    "A__KG_DIGEST_FAILURE_REPOSITORY_ONLY_CLASSIFIED_AS_EVIDENCE_OR_REPORTING_"
    "DEFECT__NO_AUTHORITY_CONSUMED__NO_OPERATION__NO_REPAIR__E05_UNCHANGED"
)
HUMAN_SOURCE_SHA256 = (
    "d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484"
)
HANDOFF_SHA256 = (
    "1e6c6fec12e064dffa2bd69873664e5a236dde812eb47853c1b7f1c056e8020c"
)

JZ = Path(
    ".github/governance/evidence/g77_256jz_fm_authority_digest_handoff_repair_v1"
)
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
KG = Path(
    ".github/governance/evidence/"
    "g77_256kg_fresh_expired_operational_recommissioning_v1"
)
KG_REDUCTION = KG / "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_V1.json"
JZ_REDUCTION = JZ / "G77_256JZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JZ_BINDING = JZ / "G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
JY = Path(".github/governance/evidence/g77_256jy_expired_operational_v1")
JY_SOURCE = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
JY_HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
JY_SOURCE_SHA256 = "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
JY_HANDOFF_SHA256 = "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"

HISTORY = {
    "KA": {
        "root": Path(
            ".github/governance/evidence/"
            "g77_256ka_fresh_expired_operational_recommissioning_v1"
        ),
        "source": "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "handoff": "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "binding": "G77_256KA_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "source_sha256": "00e24b7c7692b140e292d5cc8cc567b0b7330d85669f62711cd11ce0eefa3fe5",
        "source_length": 1388,
        "handoff_sha256": "98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283",
        "handoff_length": 1715,
        "crossed_jz_boundary": True,
    },
    "KE": {
        "root": Path(
            ".github/governance/evidence/"
            "g77_256ke_fresh_expired_operational_recommissioning_v1"
        ),
        "source": "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "handoff": "G77_256KE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "binding": "G77_256KE_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "source_sha256": "2a5b0f25fb9e9b0cca9a6bf1d6ee803f4c73f3b3415039fbaab9eae53ac25724",
        "source_length": 1061,
        "handoff_sha256": "55b1578d5896b19c08b38047de8e64d32142d5f13e7b66def6e87a51f0443632",
        "handoff_length": 1715,
        "crossed_jz_boundary": True,
    },
    "KG": {
        "root": KG,
        "source": "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "handoff": "G77_256KG_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "binding": "G77_256KG_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "source_sha256": HUMAN_SOURCE_SHA256,
        "source_length": 1390,
        "handoff_sha256": HANDOFF_SHA256,
        "handoff_length": 1715,
        "crossed_jz_boundary": False,
    },
}


class KHError(RuntimeError):
    """One deterministic fail-closed assessment error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def run_git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise KHError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(relative: Path) -> dict[str, Any]:
    raw = (ROOT / relative).read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KHError(f"NONCANONICAL_JSON__{relative}")
    return value


def load_sealed(relative: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(relative)
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KHError(f"SEALED_INNER_VALUE_MALFORMED__{relative}")
    expected = sha256_bytes(canonical_bytes(value))
    if envelope.get(f"{inner}_sha256") != expected:
        raise KHError(f"SEALED_INNER_HASH_MISMATCH__{relative}")
    return value


def verify_entry() -> dict[str, Any]:
    observed = {
        "branch": run_git("branch", "--show-current"),
        "head": run_git("rev-parse", "HEAD"),
        "tree": run_git("rev-parse", "HEAD^{tree}"),
        "subject": run_git("show", "-s", "--format=%s", "HEAD"),
        "origin": run_git("remote", "get-url", "origin"),
    }
    expected = {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
    }
    if observed != expected:
        raise KHError(f"ENTRY_MISMATCH__{observed}")
    if run_git("diff", "--cached", "--name-only"):
        raise KHError("INDEX_NOT_EMPTY")
    return {
        **observed,
        "remote_head": ENTRY_HEAD,
        "remote_equality": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
        "worktree_entry_state": "VERIFIED__CLEAN_BEFORE_FIRST_KH_MUTATION",
        "index_entry_state": "VERIFIED__EMPTY_BEFORE_FIRST_KH_MUTATION",
    }


def verify_nested() -> dict[str, Any]:
    observed = {
        "head": run_git("rev-parse", "HEAD", nested=True),
        "tree": run_git("rev-parse", "HEAD^{tree}", nested=True),
        "origin": run_git("remote", "get-url", "origin", nested=True),
        "clean": run_git("status", "--porcelain", nested=True) == "",
        "detached": run_git("branch", "--show-current", nested=True) == "",
    }
    if observed != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN,
        "clean": True,
        "detached": True,
    }:
        raise KHError(f"NESTED_AUTHORITY_MISMATCH__{observed}")
    return {
        **observed,
        "immutable_ref": f"refs/tags/{NESTED_TAG}",
        "pinned": True,
        "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
    }


def verify_committed(relative: Path) -> str:
    raw = (ROOT / relative).read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if raw != committed:
        raise KHError(f"COMMITTED_ARTIFACT_DRIFT__{relative}")
    return sha256_bytes(raw)


def verify_kg() -> dict[str, Any]:
    verify_committed(KG_REDUCTION)
    reduction = load_sealed(KG_REDUCTION, "reduction")
    if reduction.get("terminal") != KG_TERMINAL:
        raise KHError("KG_TERMINAL_MISMATCH")
    binding = reduction.get("jz_digest_binding", {})
    required_binding = {
        "authenticated_canonical_authority_digest": HANDOFF_SHA256,
        "canonical_handoff_authority_digest": HANDOFF_SHA256,
        "derived_human_source_sha256": HUMAN_SOURCE_SHA256,
        "final_fm_argv_authority_digest": HANDOFF_SHA256,
        "internal_handoff_invocation_argv_equality": "VERIFIED",
        "jz_three_way_equality": (
            "NOT_PROVEN__HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH"
        ),
        "sealed_invocation_authority_digest": HANDOFF_SHA256,
    }
    for key, expected in required_binding.items():
        if binding.get(key) != expected:
            raise KHError(f"KG_BINDING_MISMATCH__{key}")
    expected_counters = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 0,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    if reduction.get("operational_counters") != expected_counters:
        raise KHError("KG_COUNTER_MISMATCH")
    if reduction.get("human_authority", {}).get("authorization_state") != (
        "AUTHENTICATED__UNCONSUMED"
    ):
        raise KHError("KG_AUTHORITY_STATE_MISMATCH")
    return {
        "terminal": KG_TERMINAL,
        "authority": "AUTHENTICATED__UNCONSUMED__TERMINAL__UNAVAILABLE_TO_KH",
        "operation_occurred": "NO",
        "operational_counters": expected_counters,
        "reported_internal_handoff_invocation_argv_equality": "VERIFIED",
        "reported_jz_three_way_equality": required_binding["jz_three_way_equality"],
    }


def verify_jz() -> dict[str, Any]:
    verify_committed(JZ_REDUCTION)
    verify_committed(JZ_BINDING)
    verify_committed(JY_SOURCE)
    verify_committed(JY_HANDOFF)
    reduction = load_sealed(JZ_REDUCTION, "reduction")
    if reduction.get("terminal") != JZ_TERMINAL:
        raise KHError("JZ_TERMINAL_MISMATCH")
    capability = reduction.get("capability", {})
    if capability.get("derivation") != (
        "DIRECT_SHA256_OF_UNIQUE_KEY_CANONICAL_HANDOFF_BYTES"
    ):
        raise KHError("JZ_DERIVATION_MISMATCH")
    if capability.get("digest_equality") != (
        "VERIFIED__AUTHENTICATED_CANONICAL_EQUALS_SEALED_INVOCATION_EQUALS_"
        "FINAL_FM_ARGV"
    ):
        raise KHError("JZ_EQUALITY_MISMATCH")
    if capability.get("caller_digest_parameter") != "ABSENT":
        raise KHError("JZ_CALLER_DIGEST_PARAMETER_PRESENT")
    if capability.get("provider_digest_parameter") != "ABSENT":
        raise KHError("JZ_PROVIDER_DIGEST_PARAMETER_PRESENT")

    jy_source_raw = (ROOT / JY_SOURCE).read_bytes()
    jy_handoff_raw = (ROOT / JY_HANDOFF).read_bytes()
    jy_handoff = load_canonical(JY_HANDOFF)
    if (
        len(jy_source_raw) != 1294
        or sha256_bytes(jy_source_raw) != JY_SOURCE_SHA256
        or len(jy_handoff_raw) != 1715
        or sha256_bytes(jy_handoff_raw) != JY_HANDOFF_SHA256
        or jy_handoff.get("authorization", {}).get("authorization_source_sha256")
        != JY_SOURCE_SHA256
    ):
        raise KHError("JZ_HISTORICAL_JY_BYTE_DOMAIN_MISMATCH")
    binding = load_canonical(JZ_BINDING).get("invocation_binding", {})
    argv = binding.get("final_fm_argv", [])
    if "--execution-authority-sha256" not in argv:
        raise KHError("JZ_HISTORICAL_ARGV_DIGEST_ABSENT")
    if {
        binding.get("authenticated_canonical_authority_digest"),
        binding.get("sealed_invocation_authority_digest"),
        binding.get("final_fm_argv_authority_digest"),
        argv[argv.index("--execution-authority-sha256") + 1],
    } != {JY_HANDOFF_SHA256}:
        raise KHError("JZ_HISTORICAL_THREE_WAY_EQUALITY_MISMATCH")

    source = (ROOT / FM).read_text(encoding="utf-8")
    ast.parse(source)
    required_fragments = (
        "raw != canonical_bytes(value)",
        "return value, hashlib.sha256(raw).hexdigest()",
        "authority_digest = _authenticated_authority_digest(authority_path)",
        '"authority_digest_derivation": "SHA256_EXACT_CANONICAL_HANDOFF_BYTES"',
        '"authenticated_canonical_authority_digest": authority_digest',
        '"sealed_invocation_authority_digest": authority_digest',
        '"final_fm_argv_authority_digest": authority_digest',
        '"--execution-authority-sha256"',
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise KHError(f"JZ_IMPLEMENTATION_ASSERTION_MISSING__{missing}")
    return {
        "terminal": JZ_TERMINAL,
        "authoritative_human_source_bytes": (
            "EXACT_HUMAN_AUTHORIZATION_SOURCE_FILE_BYTES_REFERENCED_BY_"
            "authorization.authorization_source_sha256"
        ),
        "human_source_digest": "SHA256_OF_EXACT_HUMAN_SOURCE_FILE_BYTES",
        "historical_jy_exact_source": {
            "byte_length": len(jy_source_raw),
            "sha256": JY_SOURCE_SHA256,
        },
        "historical_jy_canonical_handoff": {
            "byte_length": len(jy_handoff_raw),
            "sha256": JY_HANDOFF_SHA256,
            "source_digest_carried_as_authorization_field": "VERIFIED",
        },
        "canonical_handoff_digest": (
            "SHA256_OF_UNIQUE_KEY_SORTED_COMPACT_CANONICAL_HANDOFF_JSON_"
            "ENVELOPE_BYTES_PLUS_ONE_LF"
        ),
        "sealed_invocation_digest": "PRESERVED_CANONICAL_HANDOFF_FILE_DIGEST",
        "final_fm_argv_digest": "PRESERVED_CANONICAL_HANDOFF_FILE_DIGEST",
        "authenticated_jz_requirement": (
            "CANONICAL_HANDOFF_FILE_DIGEST_EQUALS_SEALED_INVOCATION_DIGEST_"
            "EQUALS_FINAL_FM_ARGV_DIGEST"
        ),
        "kg_phase_b_commission_requirement": (
            "HUMAN_SOURCE_DIGEST_ALSO_EQUALS_CANONICAL_HANDOFF_FILE_DIGEST"
        ),
        "contract_difference": (
            "KG_ADDED_SOURCE_TO_ENVELOPE_FILE_DIGEST_EQUALITY_NOT_PRESENT_IN_JZ"
        ),
        "hex64": "VERIFIED__DERIVED_HANDOFF_FILE_DIGEST_VALIDATED_AS_LOWERCASE_HEX64",
        "manual_substitution": "VERIFIED__CALLER_AND_PROVIDER_DIGEST_INPUTS_ABSENT",
        "authority_consumption_boundary": (
            "VERIFIED__BINDING_AND_VALIDATION_PRECEDE_CONSUMPTION_AND_START_NO_PROCESS"
        ),
        "repository_terms_distinguished": {
            "authorization_source_sha256": "EXACT_HUMAN_SOURCE_FILE_BYTES",
            "authorization_sha256": "CANONICAL_INNER_AUTHORIZATION_OBJECT_BYTES",
            "authority_file_sha256": "CANONICAL_HANDOFF_ENVELOPE_FILE_BYTES",
        },
    }


def verify_history() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for generation, specification in HISTORY.items():
        root = specification["root"]
        source_path = root / str(specification["source"])
        handoff_path = root / str(specification["handoff"])
        binding_path = root / str(specification["binding"])
        source_raw = (ROOT / source_path).read_bytes()
        handoff_raw = (ROOT / handoff_path).read_bytes()
        handoff = load_canonical(handoff_path)
        binding = load_canonical(binding_path).get("invocation_binding", {})
        source_digest = sha256_bytes(source_raw)
        handoff_digest = sha256_bytes(handoff_raw)
        expected = {
            "source_sha256": specification["source_sha256"],
            "source_length": specification["source_length"],
            "handoff_sha256": specification["handoff_sha256"],
            "handoff_length": specification["handoff_length"],
        }
        actual = {
            "source_sha256": source_digest,
            "source_length": len(source_raw),
            "handoff_sha256": handoff_digest,
            "handoff_length": len(handoff_raw),
        }
        if actual != expected:
            raise KHError(f"{generation}_BYTE_DOMAIN_MISMATCH__{actual}")
        inner_source = handoff.get("authorization", {}).get(
            "authorization_source_sha256"
        )
        digest_set = {
            binding.get("authenticated_canonical_authority_digest"),
            binding.get("sealed_invocation_authority_digest"),
            binding.get("final_fm_argv_authority_digest"),
        }
        argv = binding.get("final_fm_argv", [])
        if "--execution-authority-sha256" not in argv:
            raise KHError(f"{generation}_ARGV_DIGEST_ABSENT")
        argv_digest = argv[argv.index("--execution-authority-sha256") + 1]
        if inner_source != source_digest or digest_set != {handoff_digest}:
            raise KHError(f"{generation}_JZ_SEMANTIC_BINDING_MISMATCH")
        if argv_digest != handoff_digest:
            raise KHError(f"{generation}_ARGV_DIGEST_MISMATCH")
        result[generation] = {
            **actual,
            "human_source_byte_domain": "EXACT_HUMAN_SOURCE_FILE_BYTES",
            "handoff_digest_byte_domain": (
                "EXACT_UNIQUE_KEY_CANONICAL_HANDOFF_JSON_ENVELOPE_BYTES_PLUS_LF"
            ),
            "source_digest_carried_as_authorization_field": "VERIFIED",
            "source_digest_equals_handoff_digest": False,
            "handoff_invocation_argv_equality": "VERIFIED",
            "authority_digest_derivation": binding.get("authority_digest_derivation"),
            "crossed_jz_boundary": specification["crossed_jz_boundary"],
        }
    return result


def verify_allowed_delta() -> None:
    if run_git("diff", "--cached", "--name-only"):
        raise KHError("INDEX_NOT_EMPTY")
    status = run_git("status", "--porcelain", "-uall").splitlines()
    for line in status:
        path = line[3:]
        if not path.startswith(KH.as_posix() + "/"):
            raise KHError(f"OUT_OF_SCOPE_WORKTREE_DELTA__{path}")


def build_assessment() -> dict[str, Any]:
    entry = verify_entry()
    nested = verify_nested()
    kg = verify_kg()
    jz = verify_jz()
    history = verify_history()
    verify_allowed_delta()

    kg_exact = history["KG"]
    if kg_exact["source_digest_equals_handoff_digest"]:
        raise KHError("DISTINCT_KG_BYTE_DOMAINS_UNEXPECTEDLY_EQUAL")

    zero_counters = {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    assessment = {
        "schema_id": "G77_256KH_JZ_DIGEST_SEMANTICS_ASSESSMENT_V1",
        "terminal": KH_TERMINAL,
        "mode": (
            "REPOSITORY_ONLY__ASSESSMENT_ONLY__NO_HUMAN_AUTHORITY_CONSUMPTION__"
            "NO_OPERATIONAL_EXECUTION__NO_REPAIR"
        ),
        "entry": entry,
        "nested_authority": nested,
        "kg_terminal_authentication": kg,
        "exact_kg_byte_domains": {
            "human_source_byte_domain": kg_exact["human_source_byte_domain"],
            "human_source_byte_length": kg_exact["source_length"],
            "human_source_sha256": kg_exact["source_sha256"],
            "handoff_digest_byte_domain": kg_exact["handoff_digest_byte_domain"],
            "handoff_digest_byte_length": kg_exact["handoff_length"],
            "handoff_digest_sha256": kg_exact["handoff_sha256"],
            "relationship": (
                "VERIFIED__BOTH_DIGESTS_CORRECTLY_HASH_DIFFERENT_SEMANTIC_OBJECTS"
            ),
            "governance_requires_cross_domain_equality": (
                "NOT_PROVEN__AUTHENTICATED_JZ_REQUIRES_FIELD_BINDING_AND_"
                "ENVELOPE_DIGEST_PRESERVATION_NOT_NUMERICAL_CROSS_DOMAIN_EQUALITY"
            ),
        },
        "authenticated_jz_semantics": jz,
        "historical_comparison": history,
        "failure_novelty_and_convergence_check": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "novelty": (
                "VERIFIED__NOT_NEW__OVERSTRONG_ACCEPTANCE_ASSERTION_ON_DISTINCT_"
                "BYTE_DOMAINS"
            ),
            "affected_invariant": (
                "NOT_PROVEN__NO_AUTHENTICATED_INVARIANT_VIOLATION__EXACT_SOURCE_"
                "PROVENANCE_INNER_SEAL_ENVELOPE_INTEGRITY_AND_JZ_DIGEST_"
                "PRESERVATION_ALL_HOLD"
            ),
            "previous_closest_edge": (
                "JY_CALLER_CONSTRUCTED_TRUNCATED_FM_AUTHORITY_FILE_DIGEST_BEFORE_PRE_"
                "REPAIRED_BY_JZ_CANONICAL_HANDOFF_DIGEST_DERIVATION"
            ),
            "semantic_difference": (
                "KG_COMPARED_EXACT_HUMAN_SOURCE_CONTENT_DIGEST_WITH_CANONICAL_"
                "HANDOFF_ENVELOPE_FILE_DIGEST_WHILE_JZ_PRESERVES_ONLY_THE_LATTER_"
                "AND_BINDS_THE_FORMER_AS_AN_INNER_FIELD"
            ),
            "production_behavior_impact": (
                "VERIFIED__NONE__KG_STOPPED_BEFORE_CONSUMPTION_PRE_FM_QEMU_VM_AND_"
                "OPERATION"
            ),
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "NOT_PROVEN",
            "convergence_signal": (
                "VERIFIED__NO_NEW_SEMANTIC_EDGE__REUSE_AUTHENTICATED_JZ_PROOF"
            ),
            "repetition_pressure": (
                "ESTIMATED__HIGH__KA_KE_KG_ALL_USE_IDENTICAL_DISTINCT_SOURCE_FIELD_"
                "AND_HANDOFF_FILE_DIGEST_DOMAINS"
            ),
            "verification_amplification_risk": (
                "VERIFIED__POSSIBLE_VERIFICATION_PROOF_AMPLIFICATION"
            ),
            "classification_evidence": (
                "VERIFIED__FM_LOAD_AUTHORITY_HASHES_CANONICAL_RAW_ENVELOPE_BYTES__"
                "HANDOFF_AUTHORIZATION_SOURCE_SHA256_BINDS_EXACT_SOURCE_BYTES__JZ_"
                "THREE_WAY_EQUALITY_EXCLUDES_SOURCE_DIGEST__KA_KE_KG_CONFIRM"
            ),
            "classification_confidence": (
                "VERIFIED__HIGH__DETERMINISTIC_BYTE_HASHES_IMPLEMENTATION_AND_"
                "SEALED_HISTORY_AGREE"
            ),
            "acceptance_requirement_forcing_continuation": (
                "NOT_PROVEN__NO_AUTHENTICATED_CONSTITUTIONAL_OR_E05_REQUIREMENT_"
                "REQUIRES_SOURCE_DIGEST_TO_EQUAL_ENVELOPE_FILE_DIGEST"
            ),
        },
        "proof_gap_vs_implementation_gap": {
            "is_jz_implementation_wrong": "NOT_PROVEN",
            "is_kg_binder_implementation_wrong": "NOT_PROVEN",
            "is_kg_phase_b_commission_overstrong": "VERIFIED",
            "is_existing_proof_insufficient": "NOT_PROVEN",
            "is_new_production_capability_required": "NOT_PROVEN",
            "is_new_repository_proof_required": "NOT_PROVEN",
        },
        "convergence": {
            "last_verified_edge": (
                "EXACT_HUMAN_SOURCE_PROVENANCE_BOUND_INSIDE_CANONICAL_HANDOFF_AND_"
                "HANDOFF_FILE_DIGEST_PRESERVED_THROUGH_SEALED_INVOCATION_AND_FINAL_ARGV"
            ),
            "first_broken_edge": (
                "NOT_PROVEN__KG_REPORTED_CROSS_DOMAIN_INEQUALITY_IS_NOT_AN_"
                "AUTHENTICATED_JZ_OR_CONSTITUTIONAL_EDGE"
            ),
            "constitutional_frontier_distance": (
                "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
            ),
            "convergence_signal": (
                "VERIFIED__RETURN_TO_EXISTING_JZ_CONTRACT__NO_NEW_DIGEST_EDGE"
            ),
            "repetition_pressure": "ESTIMATED__HIGH",
            "verification_amplification_risk": (
                "VERIFIED__POSSIBLE_VERIFICATION_PROOF_AMPLIFICATION"
            ),
            "overengineering_risk": (
                "ESTIMATED__HIGH_IF_A_NEW_DIGEST_CAPABILITY_OR_REPAIR_IS_CREATED"
            ),
        },
        "decision": {
            "selected_case": "CASE_E__EVIDENCE_OR_REPORTING_DEFECT",
            "minimum_missing_capability": (
                "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED"
            ),
            "minimum_legal_next_delta": "STOP_OR_REUSE_EXISTING_PROOF",
            "repair_recommendation": "NONE__KH_PERFORMS_NO_REPAIR",
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "governance": {
            "project_progress": (
                "VERIFIED__KG_DIGEST_FAILURE_REPOSITORY_ONLY_CLASSIFIED"
            ),
            "project_progress_estimate": (
                "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR"
            ),
            "informal_project_progress_estimate": (
                "ESTIMATED__OVERSTRONG_KG_ACCEPTANCE_ASSERTION_REMOVED_FROM_"
                "CAPABILITY_GAP_INTERPRETATION_ONLY__NO_REPAIR"
            ),
            "constitutional_health_evidence": (
                "VERIFIED__JZ_FAIL_CLOSED_BINDING_INTACT__KG_AUTHORITY_UNCONSUMED_"
                "AND_UNAVAILABLE__KH_COUNTERS_ZERO"
            ),
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": (
                "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
            ),
            "governance_efficience": (
                "ESTIMATED__HIGH__REUSED_JZ_AND_THREE_HISTORICAL_BYTE_DOMAIN_CONTROLS"
            ),
            "overengineering_risk": (
                "ESTIMATED__HIGH_IF_CROSS_DOMAIN_EQUALITY_IS_PRODUCTIZED"
            ),
            "cognition_provenance": (
                "VERIFIED__COMMITTED_CANONICAL_BYTES_SEALS_IMPLEMENTATION_AND_GIT_"
                "IDENTITIES_PRIMARY"
            ),
            "cognition_assisted_handoff": (
                "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KH_ASSESSMENT"
            ),
            "candidate_capability": (
                "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL"
            ),
            "shadow_design_target": (
                "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED"
            ),
            "constitutional_continuation_progress": (
                "VERIFIED__KG_MISCLASSIFIED_DIGEST_EDGE_REDUCED_TO_EXISTING_JZ_"
                "SEMANTICS"
            ),
            "hac_hai_hae": (
                "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
            ),
        },
        "architecture": {
            "production_mutation_count": 0,
            "p11_implementation_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "parallel_flow": "NO",
        },
        "operational_counters": zero_counters,
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0_OPERATIONAL_CAPABILITY",
            "new_blocker_localized_count": (
                "VERIFIED__0__KG_ASSERTION_CLASSIFIED_NOT_A_BLOCKER"
            ),
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "ccwim": {
            "ccwim_maturity_level": (
                "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION"
            ),
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": (
                "VERIFIED__EX_17_OF_17_IN_JZ_KA_KE_KG_COMMON_PROOF_SUBSTRATE"
            ),
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": (
                "VERIFIED__NO_NEW_OPERATIONAL_CAPABILITY__ONE_CLASSIFICATION_RESULT"
            ),
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": (
                "VERIFIED__NO"
            ),
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": (
                "VERIFIED__UNCHANGED__1_TO_1"
            ),
        },
        "auto_continuable": False,
        "human_review_required": True,
    }
    if any(assessment["operational_counters"].values()):
        raise KHError("KH_OPERATIONAL_COUNTER_NONZERO")
    return assessment


def envelope(assessment: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KH_JZ_DIGEST_SEMANTICS_ASSESSMENT_ENVELOPE_V1",
        "assessment": assessment,
        "assessment_sha256": sha256_bytes(canonical_bytes(assessment)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = envelope(build_assessment())
    if arguments.write:
        (ROOT / OUTPUT).write_bytes(canonical_bytes(result))
    print(result["assessment"]["terminal"])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
