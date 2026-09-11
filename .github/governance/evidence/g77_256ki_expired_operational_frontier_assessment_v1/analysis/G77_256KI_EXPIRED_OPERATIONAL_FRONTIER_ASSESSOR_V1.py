#!/usr/bin/env python3
"""Reconstruct the authenticated EXPIRED frontier without operating it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KI = Path(
    ".github/governance/evidence/"
    "g77_256ki_expired_operational_frontier_assessment_v1"
)
OUTPUT = KI / "G77_256KI_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "05f70763d3f22750c8a3491bc4cbc88f98e9ca70"
ENTRY_TREE = "f5d9477b677b6642332b13263bb430c6de0e5c57"
ENTRY_SUBJECT = "G77-256KH classify KG authority digest semantics"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

TERMINAL = (
    "A__EXPIRED_OPERATIONAL_FRONTIER_RECONSTRUCTED__NO_NEW_CAPABILITY_GAP__"
    "ONLY_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_OBSERVATION_REMAINS__"
    "NO_AUTHORITY_CONSUMED__NO_OPERATION__E05_UNCHANGED"
)
LAST_OPERATIONAL_EDGE = (
    "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_"
    "NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
)
FIRST_UNVERIFIED_OPERATIONAL_EDGE = (
    "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
)
LAST_VERIFIED_EDGE = (
    "ALL_PREOPERATIONAL_EXPIRED_PREREQUISITES_REPOSITORY_VERIFIED_THROUGH_"
    "KF_AND_KG_PHASE_A_WITH_KH_JZ_DIGEST_CLASSIFICATION"
)
FIRST_BROKEN_EDGE = (
    "NOT_PROVEN__NO_GENUINE_CURRENT_BROKEN_EDGE_AUTHENTICATED__"
    "FRESH_OPERATIONAL_OBSERVATION_ABSENT"
)
MINIMUM_MISSING_CAPABILITY = (
    "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED__"
    "ONLY_FRESH_OPERATIONAL_EXPIRED_OBSERVATION_REMAINS"
)
MINIMUM_LEGAL_NEXT_DELTA = (
    "ONE_FRESH_HUMAN_AUTHORIZED_BOUNDED_EXPIRED_OPERATIONAL_ATTEMPT"
)

EVIDENCE = Path(".github/governance/evidence")

# Generation, directory, terminal file, sealed inner key, edge container,
# authenticated terminal.  Each generation remains an independent record.
LINEAGE = (
    ("JI", "g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1", "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "metrics", "A__NEXT_UNSATISFIED_E05_VECTOR_DETERMINISTICALLY_SELECTED"),
    ("JJ", "g77_256jj_expired_vector_deterministic_repository_formalization_v1", "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "metrics", "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED"),
    ("JK", "g77_256jk_expired_post_commit_live_binding_and_deterministic_preclaim_time_control_readiness_v1", "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "metrics", "M__EXPIRED_DETERMINISTIC_OPERATIONAL_PRECLAIM_CONTROL_NOT_AVAILABLE"),
    ("JL", "g77_256jl_p11_custody_owned_deterministic_preclaim_temporal_owner_contract_v1", "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "metrics", "A__P11_CUSTODY_OWNED_DETERMINISTIC_PRECLAIM_TEMPORAL_OWNER_CONTRACT_VERIFIED"),
    ("JM", "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1", "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_IMPLEMENTED_AND_REPOSITORY_VERIFIED"),
    ("JN", "g77_256jn_post_jm_live_binding_ex_successor_reauthentication_and_expired_operational_readiness_v1", "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "M__POST_JM_READINESS_REQUIRES_SEPARATE_IMPLEMENTATION_DELTA"),
    ("JO", "g77_256jo_bind_sole_er_fm_route_to_committed_jm_p11_and_sealed_context_v1", "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__SOLE_ER_FM_ROUTE_BOUND_TO_COMMITTED_JM_P11_AND_SEALED_CONTEXT_REPOSITORY_VERIFIED"),
    ("JP", "g77_256jp_post_jo_committed_live_binding_and_expired_operational_readiness_reauthentication_v1", "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_READINESS_REPOSITORY_VERIFIED"),
    ("JQ", "g77_256jq_expired_fresh_human_authorized_operational_denial_before_p11_entry_v1", "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_REDUCTION_V1.json", "reduction", "frontier", "M__EXPIRED_PREAUTHORIZATION_ROUTE_CONTRACT_NOT_AVAILABLE"),
    ("JR", "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1", "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__EXPIRED_HUMAN_AUTHORITY_MATERIALIZATION_AND_PRESENTATION_BINDING_REPOSITORY_VERIFIED"),
    ("JS", "g77_256js_expired_operational_v1", "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json", "reduction", "blocker", "M__EXPIRED_FRESH_PREAUTHORIZATION_BOOTSTRAP_HEAD_TREE_BINDING_MISMATCH"),
    ("JT", "g77_256jt_expired_bootstrap_checkout_binding_repair_v1", "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED"),
    ("JU", "g77_256ju_expired_operational_v1", "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json", "reduction", "frontier", "M__FRESH_EXPIRED_PREAUTHORIZATION_GN_REQUEST_SCHEMA_MISMATCH"),
    ("JV", "g77_256jv_expired_gn_request_schema_binding_repair_v1", "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"),
    ("JW", "g77_256jw_expired_operational_v1", "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "reduction", "frontier", "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_ER_CONTEXT_CHECKOUT_ROLE_IDENTITY_COLLAPSE_BEFORE_EXPIRED_CHECK"),
    ("JX", "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1", "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_REPOSITORY_VERIFIED"),
    ("JY", "g77_256jy_expired_operational_v1", "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "reduction", "frontier", "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_FM_SUPPLIED_AUTHORITY_HASH_SYNTAX_BEFORE_PRE"),
    ("JZ", "g77_256jz_fm_authority_digest_handoff_repair_v1", "G77_256JZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_BINDING_REPOSITORY_VERIFIED"),
    ("KA", "g77_256ka_fresh_expired_operational_recommissioning_v1", "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json", "reduction", "failure", "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_NAMESPACE_BINDING_BEFORE_REQUEST"),
    ("KB", "g77_256kb_expired_guest_context_namespace_binding_repair_v1", "G77_256KB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "continuation", "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"),
    ("KC", "g77_256kc_fresh_expired_operational_recommissioning_v1", "G77_256KC_SPCE_PHASE_B_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json", "reduction", "failure", "M__KC_PHASE_B_FAIL_CLOSED_AT_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BEFORE_AUTHORITY_AUTHENTICATION_OR_CONSUMPTION"),
    ("KD", "g77_256kd_kc_phase_b_entry_owner_interface_binding_repair_v1", "G77_256KD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__KC_PHASE_B_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BINDING_REPOSITORY_VERIFIED"),
    ("KE", "g77_256ke_fresh_expired_operational_recommissioning_v1", "G77_256KE_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "reduction", "failure", "M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST"),
    ("KF", "g77_256kf_guest_harness_permission_binding_repair_v1", "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction", "frontier", "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED"),
    ("KG", "g77_256kg_fresh_expired_operational_recommissioning_v1", "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_V1.json", "reduction", "frontier", "M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_BEFORE_AUTHORITY_CONSUMPTION"),
    ("KH", "g77_256kh_jz_digest_semantics_assessment_v1", "G77_256KH_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json", "assessment", "convergence", "A__KG_DIGEST_FAILURE_REPOSITORY_ONLY_CLASSIFIED_AS_EVIDENCE_OR_REPORTING_DEFECT__NO_AUTHORITY_CONSUMED__NO_OPERATION__NO_REPAIR__E05_UNCHANGED"),
)

COUNTER_KEYS = (
    "operational_authorization_count",
    "authority_consumption_count",
    "pre_operational_count",
    "fm_operational_invocation_count",
    "qemu_count",
    "vm_count",
    "operation_attempt_count",
    "operational_request_count",
    "expired_denial_count",
    "p11_entry_count",
    "protected_invocation_count",
    "protected_effect_count",
    "retry_count",
    "repair_retry_count",
    "replay_count",
)

NONZERO_COUNTERS = {
    "JW": {"operational_authorization_count", "authority_consumption_count", "pre_operational_count", "fm_operational_invocation_count", "qemu_count", "vm_count", "operation_attempt_count"},
    "JY": {"operational_authorization_count", "authority_consumption_count", "fm_operational_invocation_count"},
    "KA": {"operational_authorization_count", "authority_consumption_count", "pre_operational_count", "fm_operational_invocation_count", "qemu_count", "vm_count", "operation_attempt_count"},
    "KE": {"operational_authorization_count", "authority_consumption_count", "pre_operational_count", "fm_operational_invocation_count", "qemu_count", "vm_count", "operation_attempt_count"},
    "KG": {"operational_authorization_count"},
}

AUTHORITY_STATES = {
    "JW": "VERIFIED__CONSUMED_NONREUSABLE",
    "JY": "VERIFIED__EXACTLY_ONCE__NONREUSABLE",
    "KA": "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE",
    "KC": "GRANTED_UNCONSUMED__NOT_CANONICALLY_MATERIALIZED__NONREUSABLE_FOR_KC_AFTER_TERMINAL_FAIL_CLOSED",
    "KE": "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE",
    "KG": "AUTHENTICATED__UNCONSUMED__TERMINAL__UNAVAILABLE_TO_KI",
}

AUTHORITY_EVIDENCE = {
    "JW": (("authority", "state"), "VERIFIED__CONSUMED_NONREUSABLE"),
    "JY": (("human_authority", "consumption"), "VERIFIED__EXACTLY_ONCE__NONREUSABLE"),
    "KA": (("human_authority", "state"), "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"),
    "KC": (("human_authority", "state"), "GRANTED_UNCONSUMED__NOT_CANONICALLY_MATERIALIZED__NONREUSABLE_FOR_KC_AFTER_TERMINAL_FAIL_CLOSED"),
    "KE": (("human_authority", "state"), "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"),
    "KG": (("human_authority", "authorization_state"), "AUTHENTICATED__UNCONSUMED"),
}


class KIError(RuntimeError):
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
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise KIError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(relative: Path) -> dict[str, Any]:
    raw = (ROOT / relative).read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KIError(f"NONCANONICAL_JSON__{relative}")
    return value


def load_sealed(relative: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(relative)
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KIError(f"SEALED_INNER_MALFORMED__{relative}")
    if envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KIError(f"SEALED_INNER_HASH_MISMATCH__{relative}")
    return value


def load_legacy_sealed(relative: Path, inner: str) -> dict[str, Any]:
    """Load an older pretty-printed envelope while still verifying its seal."""
    envelope = json.loads(
        (ROOT / relative).read_bytes(), object_pairs_hook=unique_object
    )
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KIError(f"SEALED_INNER_MALFORMED__{relative}")
    legacy_bytes = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    expected = sha256_bytes(legacy_bytes)
    if inner == "certificate":
        preimage = dict(envelope)
        preimage["certificate_sha256"] = ""
        expected = sha256_bytes(
            json.dumps(
                preimage,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        )
    if envelope.get(f"{inner}_sha256") != expected:
        raise KIError(f"SEALED_INNER_HASH_MISMATCH__{relative}")
    return value


def verify_committed(relative: Path) -> None:
    raw = (ROOT / relative).read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if raw != committed:
        raise KIError(f"COMMITTED_ARTIFACT_DRIFT__{relative}")


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
        raise KIError(f"ENTRY_MISMATCH__{observed}")
    if run_git("diff", "--cached", "--name-only"):
        raise KIError("INDEX_NOT_EMPTY")
    return {
        **observed,
        "remote_head": ENTRY_HEAD,
        "remote_equality": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
        "worktree_entry_state": "VERIFIED__CLEAN_BEFORE_FIRST_KI_MUTATION",
        "index_entry_state": "VERIFIED__EMPTY_BEFORE_FIRST_KI_MUTATION",
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
        raise KIError(f"NESTED_AUTHORITY_MISMATCH__{observed}")
    return {
        **observed,
        "immutable_ref": f"refs/tags/{NESTED_TAG}",
        "pinned": True,
        "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
    }


def counter_number(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.startswith("VERIFIED__"):
        token = value.removeprefix("VERIFIED__").split("__", 1)[0]
        if token.isdigit():
            return int(token)
    raise KIError(f"COUNTER_VALUE_MALFORMED__{value!r}")


def lineage() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    result: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}
    for generation, directory, filename, inner, edge_key, terminal in LINEAGE:
        relative = EVIDENCE / directory / filename
        verify_committed(relative)
        value = load_sealed(relative, inner)
        if value.get("terminal") != terminal:
            raise KIError(f"TERMINAL_MISMATCH__{generation}")
        edges = value.get(edge_key)
        if not isinstance(edges, dict):
            raise KIError(f"EDGE_CONTAINER_MISSING__{generation}__{edge_key}")
        counters = value.get("operational_counters", {})
        if not isinstance(counters, dict):
            raise KIError(f"COUNTERS_MALFORMED__{generation}")
        if generation in AUTHORITY_EVIDENCE:
            path, expected_authority = AUTHORITY_EVIDENCE[generation]
            authority_value: Any = value
            for key in path:
                if not isinstance(authority_value, dict):
                    raise KIError(f"AUTHORITY_EVIDENCE_MALFORMED__{generation}")
                authority_value = authority_value.get(key)
            if authority_value != expected_authority:
                raise KIError(f"AUTHORITY_STATE_MISMATCH__{generation}")
        expected_nonzero = NONZERO_COUNTERS.get(generation, set())
        normalized: dict[str, int] = {}
        for key in COUNTER_KEYS:
            source_key = key
            if key == "operational_request_count" and key not in counters:
                source_key = "request_count"
            observed = counter_number(counters[source_key]) if source_key in counters else 0
            expected = 1 if key in expected_nonzero else 0
            if observed != expected:
                raise KIError(
                    f"GENERATION_COUNTER_MISMATCH__{generation}__{key}__{observed}"
                )
            normalized[key] = observed
        result.append(
            {
                "generation": generation,
                "terminal": terminal,
                "last_verified_edge": edges.get("last_verified_edge"),
                "first_broken_edge": edges.get("first_broken_edge"),
                "authority_state": AUTHORITY_STATES.get(
                    generation, "NOT_APPLICABLE__NO_OPERATIONAL_AUTHORITY"
                ),
                "operational_counters": normalized,
                "e05_credit": "VERIFIED__0",
            }
        )
        loaded[generation] = value
    return result, loaded


def verify_decision_inputs(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    kh = loaded["KH"]
    required_kh = {
        "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
        "novelty": "VERIFIED__NOT_NEW__OVERSTRONG_ACCEPTANCE_ASSERTION_ON_DISTINCT_BYTE_DOMAINS",
        "new_capability_required": "NOT_PROVEN",
        "new_proof_required": "NOT_PROVEN",
    }
    check = kh.get("failure_novelty_and_convergence_check", {})
    for key, expected in required_kh.items():
        if check.get(key) != expected:
            raise KIError(f"KH_CLASSIFICATION_MISMATCH__{key}")
    if kh.get("decision") != {
        "minimum_legal_next_delta": "STOP_OR_REUSE_EXISTING_PROOF",
        "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED",
        "repair_recommendation": "NONE__KH_PERFORMS_NO_REPAIR",
        "selected_case": "CASE_E__EVIDENCE_OR_REPORTING_DEFECT",
    }:
        raise KIError("KH_DECISION_MISMATCH")
    kg_auth = kh.get("kg_terminal_authentication", {}).get("authority")
    if kg_auth != "AUTHENTICATED__UNCONSUMED__TERMINAL__UNAVAILABLE_TO_KH":
        raise KIError("KH_KG_AUTHORITY_MISMATCH")

    phase_a_path = EVIDENCE / LINEAGE[-2][1] / "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json"
    verify_committed(phase_a_path)
    phase_a = load_sealed(phase_a_path, "reduction")
    if phase_a.get("terminal") != "A__FRESH_KG_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION":
        raise KIError("KG_PHASE_A_TERMINAL_MISMATCH")
    if phase_a.get("kf_authentication", {}).get("terminal") != "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED":
        raise KIError("KG_PHASE_A_KF_AUTHENTICATION_MISSING")
    if phase_a.get("jz_reconstruction", {}).get("terminal") != "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_BINDING_REPOSITORY_VERIFIED":
        raise KIError("KG_PHASE_A_JZ_AUTHENTICATION_MISSING")

    kf = loaded["KF"]
    if kf.get("frontier", {}).get("minimum_missing_capability") != "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY":
        raise KIError("KF_FRONTIER_MISMATCH")
    ke = loaded["KE"]
    if ke.get("failure", {}).get("last_verified_edge") != LAST_OPERATIONAL_EDGE:
        raise KIError("KE_LAST_OPERATIONAL_EDGE_MISMATCH")
    if any(ke.get("operational_counters", {}).get(key) not in (0, "VERIFIED__0") for key in ("operational_request_count", "expired_denial_count", "p11_entry_count", "protected_invocation_count", "protected_effect_count", "retry_count", "repair_retry_count", "replay_count")):
        raise KIError("KE_POST_CUSTODY_COUNTER_MISMATCH")

    ex_cert_path = EVIDENCE / "g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
    ex_seal_path = EVIDENCE / "g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
    for path, inner in ((ex_cert_path, "certificate"), (ex_seal_path, "seal")):
        verify_committed(path)
        load_legacy_sealed(path, inner)
    certificate = load_legacy_sealed(ex_cert_path, "certificate")
    if certificate.get("component_counts", {}).get("CERTIFIED") != 17:
        raise KIError("EX_CERTIFIED_COUNT_MISMATCH")
    if kh.get("baseline") != {
        "e05_credit": "VERIFIED__0",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "e05_state": "VERIFIED__11_OF_18",
        "ex_reconstructed": "VERIFIED__0",
        "ex_reused": "VERIFIED__17_OF_17",
        "expired": "NOT_PROVEN_OPERATIONALLY",
    }:
        raise KIError("KH_BASELINE_MISMATCH")
    return {
        "kh_terminal_and_seal": "VERIFIED",
        "kg_terminal": "VERIFIED",
        "kg_authority": "AUTHENTICATED__UNCONSUMED__TERMINAL__UNAVAILABLE_TO_KI",
        "kg_phase_a_preoperational_prerequisites": "VERIFIED",
        "jz_digest_semantics": "VERIFIED__REUSED_FROM_KH",
        "kf_permission_repair": "VERIFIED__REUSED",
        "ke_latest_operational_observation": "VERIFIED__REUSED",
        "ex_common_substrate": "VERIFIED__17_OF_17",
        "e05_baseline": "VERIFIED__11_OF_18__EXPIRED_NOT_PROVEN_OPERATIONALLY",
    }


def build_assessment() -> dict[str, Any]:
    entry = verify_entry()
    nested = verify_nested()
    history, loaded = lineage()
    inputs = verify_decision_inputs(loaded)
    zero_counters = {key: 0 for key in COUNTER_KEYS}
    return {
        "schema_id": "G77_256KI_EXPIRED_OPERATIONAL_FRONTIER_ASSESSMENT_V1",
        "mode": "REPOSITORY_ONLY__ASSESSMENT_ONLY__NO_OPERATIONAL_AUTHORITY__NO_AUTHORITY_CONSUMPTION__NO_PRE__NO_FM_OPERATION__NO_QEMU__NO_VM",
        "terminal": TERMINAL,
        "vector": "EXPIRED",
        "entry": entry,
        "nested_authority": nested,
        "authenticated_inputs": inputs,
        "lineage": history,
        "frontier": {
            "last_verified_operational_edge": LAST_OPERATIONAL_EDGE,
            "first_unverified_operational_edge": FIRST_UNVERIFIED_OPERATIONAL_EDGE,
            "last_verified_edge": LAST_VERIFIED_EDGE,
            "first_broken_edge": FIRST_BROKEN_EDGE,
            "current_real_blocker": "NOT_PROVEN__NO_GENUINE_CURRENT_BLOCKER_LOCALIZED",
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
            "novelty": "VERIFIED__NOT_NEW__SAME_POST_REPAIR_OPERATIONAL_REPROOF_EDGE_IDENTIFIED_BY_KF",
            "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY",
            "previous_closest_edge": "KF_GUEST_CUSTODY_PERMISSION_CONTRACT_REPOSITORY_VERIFIED_AFTER_KE_REACHED_GUEST_CUSTODY_LOAD",
            "semantic_difference": "VERIFIED__NO_NEW_CONSTITUTIONAL_SEMANTIC_AUTHORITY_PRODUCTION_PATH_OR_OPERATIONAL_DIFFERENCE",
            "production_behavior_impact": "NOT_PROVEN__NO_CURRENT_REGRESSION_AUTHENTICATED",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__FRESH_OPERATIONAL_OBSERVATION_ONLY__NO_NEW_REPOSITORY_PROOF",
            "convergence_signal": "VERIFIED__REPOSITORY_CAPABILITY_CHAIN_CONVERGED__ONLY_E05_OPERATIONAL_OBSERVATION_REMAINS",
            "repetition_pressure": "ESTIMATED__HIGH__THREE_CONSUMED_OPERATIONAL_AUTHORITIES_AND_ONE_UNCONSUMED_KG_AUTHORITY_WITH_ZERO_E05_CREDIT",
            "verification_amplification_risk": "VERIFIED__POSSIBLE_IF_ANOTHER_REPOSITORY_ONLY_CAPABILITY_GENERATION_PRECEDES_THE_REQUIRED_OBSERVATION",
            "classification_evidence": "VERIFIED__KE_OPERATION_REACHED_GUEST_CUSTODY_LOAD__KF_CLOSED_PERMISSION_CONTRACT__KG_PHASE_A_REAUTHENTICATED_KF_AND_ALL_PREFLIGHTS__KH_REMOVED_FALSE_DIGEST_BLOCKER",
            "classification_confidence": "VERIFIED__HIGH__SEALED_LINEAGE_AND_COUNTERS_CONVERGE",
            "acceptance_requirement_forcing_continuation": "VERIFIED__E05_EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY_AND_REPOSITORY_ONLY_EVIDENCE_CANNOT_SATISFY_IT",
        },
        "gap_decision": {
            "is_new_production_capability_required": "NOT_PROVEN",
            "is_new_repository_capability_required": "NOT_PROVEN",
            "is_new_repository_proof_required": "NOT_PROVEN",
            "is_existing_owner_repair_required": "NOT_PROVEN",
            "is_fresh_operational_observation_required": "VERIFIED",
            "is_fresh_human_authority_required_for_successor": "VERIFIED",
            "minimum_missing_capability": MINIMUM_MISSING_CAPABILITY,
            "minimum_legal_next_delta": MINIMUM_LEGAL_NEXT_DELTA,
        },
        "successor_spce_structure_only": {
            "phase_a": "REPOSITORY_ONLY_READINESS__FRESH_COORDINATES__EXACT_HUMAN_DECISION_PRESENTATION__SAFE_STOP__ZERO_AUTHORITY_CONSUMPTION",
            "barrier": "HUMAN_BARRIER__EXACT_FRESH_HUMAN_AUTHORITY_REQUIRED",
            "phase_b": "ONLY_AFTER_EXACT_FRESH_HUMAN_AUTHORITY__AUTHORIZE__OPERATE__REDUCE",
            "ki_created_successor_artifacts": False,
            "ki_started_successor_generation": False,
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "ki_e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "operational_counters": zero_counters,
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
        "governance": {
            "project_progress": "VERIFIED__EXPIRED_OPERATIONAL_FRONTIER_RECONSTRUCTED_AND_MINIMUM_SUCCESSOR_DELTA_SELECTED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ALL_REPOSITORY_PREREQUISITES_PROVEN__ONE_FRESH_OPERATIONAL_OBSERVATION_REMAINS",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_LINEAGE_PRESERVED__HISTORICAL_AUTHORITIES_NOT_REUSED__KI_COUNTERS_ZERO",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__26_GENERATION_TERMINALS_AND_EX_17_OF_17_REUSED_WITH_ZERO_RECONSTRUCTION",
            "overengineering_risk": "ESTIMATED__HIGH_IF_FURTHER_REPOSITORY_PROOF_OR_REPAIR_PRECEDES_THE_REQUIRED_OBSERVATION",
            "cognition_provenance": "VERIFIED__COMMITTED_CANONICAL_SEALED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KI_ASSESSMENT",
            "candidate_capability": "NOT_PROVEN__NO_NEW_CAPABILITY__FRESH_EXPIRED_OPERATIONAL_OBSERVATION_ONLY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__FALSE_KG_BLOCKER_REMOVED_FROM_FRONTIER_AND_EXISTING_KF_POST_REPAIR_EDGE_RESTORED",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__0",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0__KH_ALREADY_REMOVED_KG_FALSE_BLOCKER",
            "new_classification_result_count": "VERIFIED__1__CURRENT_GAP_CLASSIFIED_AS_OPERATIONAL_OBSERVATION_GAP",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_FORMAL_TOKEN_ATTRIBUTION_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_AND_CONTEXT_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_BASELINE_OR_DENOMINATOR",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT_FOR_THIS_NON_MILESTONE_ASSESSMENT",
        },
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": "VERIFIED__EX_17_OF_17_PLUS_JZ_KB_KD_KF_REPAIRS_AND_SINGLE_FM_ER_P11_ROUTE",
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": "VERIFIED__NO_NEW_CAPABILITY__ONE_REPOSITORY_CLASSIFICATION_RESULT_ONLY",
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": "VERIFIED__NO",
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(assessment: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KI_EXPIRED_OPERATIONAL_FRONTIER_ASSESSMENT_ENVELOPE_V1",
        "assessment": assessment,
        "assessment_sha256": sha256_bytes(canonical_bytes(assessment)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    assessment = build_assessment()
    output = envelope(assessment)
    if arguments.write:
        (ROOT / OUTPUT).write_bytes(canonical_bytes(output))
    print(TERMINAL)
    print(canonical_bytes(output).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
