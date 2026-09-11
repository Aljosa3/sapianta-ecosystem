#!/usr/bin/env python3
"""Repository-only G77-256KS Human-authority authentication reducer.

The reducer authenticates the existing KN Human decision and proves the
existing FM/JZ canonical handoff shape in memory.  It never persists an
authority handoff, binds or consumes authority, or invokes an operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KS = ROOT / ".github/governance/evidence/g77_256ks_existing_kn_authority_authentication_binding_readiness_v1"
OUTPUT = KS / "G77_256KS_CANONICAL_BINDING_READINESS_V1.json"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION_PRESENTATION = KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt"
CONTEXT = KN / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = KN / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
JZ_READINESS = KN / "G77_256KN_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
KO_INSTRUCTION = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1/G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
KR_REDUCTION = ROOT / ".github/governance/evidence/g77_256kr_kp_requirement_correction_v1/G77_256KR_SPCE_TERMINAL_CORRECTION_V1.json"
KQ_REDUCTION = ROOT / ".github/governance/evidence/g77_256kq_human_provenance_capability_discovery_v1/G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"

HEAD = "17106914969e59b1b3e685b8e50fa2f93b606cd7"
TREE = "96fd8e43381921b53aeceafb72209a3190d32061"
SUBJECT = "G77-256KR correct KP requirement and verify KN source readiness"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
CONTEXT_SHA256 = "37f5c7d46b305b6e6e6b912dd136917c96ad4c783341aa62cd1dc4994e6f5b4b"
CONTEXT_FILE_SHA256 = "adafd6cdc2bef25119e098e11a69a79cdc893656bc9471f72e4e6a85ca5e7695"
CANONICAL_ARGV_SHA256 = "96480352c744c6feb9d743fafc7eae111a143ebde6b18cf67160e05ac1e93816"
TEMPORAL_BINDING_SHA256 = "cc46cded2aa3c294ad84c172619092889639fb74dda5f32ec68645508a2a1f56"
REQUEST_SHA256 = "9c5941b007e5939da928b7e1cc6cf0668a8e20b29f75bbe29964520645eb57d5"
REQUEST_FILE_SHA256 = "f980e8cd5ac48c97bbc61a0f891f103e8305f14847a59333b39912024609831d"
AUTH_PRESENTATION_SHA256 = "71cc222249ad75b2b420d749c2d4bd66cf0bd2d982f054102384ddb14993e2ac"
DECISION_PRESENTATION_SHA256 = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
READINESS_FILE_SHA256 = "a178e6621e9d232d48143e353660e6dba8ce524059a8ad69d0c908cd7aa07a5f"
READINESS_INNER_SHA256 = "d26523b800ec42a3b3d0036087eaf110bb1b786dba455e13edd97d115ab1eb39"
SAFE_STOP_FILE_SHA256 = "5bc8f9a4b2c012cb45460a661aaf5642de222c1fbefc04b74ddb2abd159fc3f0"
SAFE_STOP_INNER_SHA256 = "965e892b39bfc3b1215a842703d186177ac39cf54565e51ad2147e2fd4742a1b"
KM_FILE_SHA256 = "b76a42cd95b5d227ba64fe5c7d8e777143f915d296d8d5811a3eec449e7751a4"
KM_INNER_SHA256 = "73a8d430c1ffd51bbfd8e39b51c08f66a1cc6550038153e0a58d19163d6c691d"
KJ_BINDER_SHA256 = "fcc1a60fdbc3fb246d918ac2e8143bd4888e3e65ebc2e3769298a039c5aeebbf"
KR_FILE_SHA256 = "fa0f4b4acb99b00b2b352bc303ff381906584ad8ecb528577cf02b96229f9352"
FM_FILE_SHA256 = "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
PROJECTED_HANDOFF_SHA256 = "f220a240d54c38ecba24fcc2ffd6c9c37b1cc11a69baac5f913964b0d5cff4ae"
PROJECTED_AUTHORIZATION_SHA256 = "e1e21562553bd9b93bbb144336e0baa0fd1fdfc554e62cd65b5e08c6cae5e7c9"
TERMINAL = "A__KS_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED_AND_CANONICAL_BINDING_READY__UNCONSUMED__NO_PHASE_B__NO_OPERATION"

GN_FIELDS = {
    "all_operational_counters_zero", "checkpoint_file_sha256",
    "checkpoint_inner_sha256", "checkpoint_path",
    "complete_deterministic_readiness", "gk_receipt_parent_false_positive_blocked",
    "preauth_final_admission_equivalence",
    "preauth_final_admission_equivalence_file_sha256",
    "receipt_parent_observation_file_sha256", "static_readiness_file_sha256",
}


class KSReductionError(RuntimeError):
    """Stable fail-closed KS reduction failure."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KSReductionError(f"NONCANONICAL_JSON:{path.name}")
    body = value.get(inner)
    if not isinstance(body, dict) or value.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(body)).hexdigest():
        raise KSReductionError(f"SEAL_MISMATCH:{path.name}")
    return body


def load_fm() -> Any:
    if sha256_path(FM_PATH) != FM_FILE_SHA256:
        raise KSReductionError("FM_OWNER_IMMUTABILITY_FAILURE")
    spec = importlib.util.spec_from_file_location("g77_256ks_fm_owner", FM_PATH)
    if spec is None or spec.loader is None:
        raise KSReductionError("FM_OWNER_IMPORT_FAILURE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_human_bytes() -> bytes:
    text = KO_INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KSReductionError("KO_SOURCE_MARKERS_INVALID")
    return text.split(begin, 1)[1].split(end, 1)[0].encode("utf-8")


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0, "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0, "fm_operational_invocation_count": 0,
        "qemu_start_count": 0, "vm_start_count": 0, "operation_attempt_count": 0,
        "operation_request_count": 0, "expired_denial_count": 0,
        "p11_entry_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0,
        "repair_retry_count": 0, "replay_count": 0,
    }


def build_projected_authorization(context: dict[str, Any], fm: Any) -> dict[str, Any]:
    return {
        "schema_id": fm.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": SOURCE_SHA256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "EXPIRED",
        "authorized_repository_head": context["repository_head"],
        "authorized_repository_tree": context["repository_tree"],
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": fm.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1, "qemu_system_execution_limit": 1,
        "expired_operational_attempt_limit": 1, "retry_limit": 0,
        "repair_limit": 0, "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False, "provider_authorized": False,
        "trusted_access_authorized": False, "authorization_reusable": False,
        "auto_continuable": False,
    }


def authenticate_inputs() -> dict[str, Any]:
    if (
        git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("diff", "--name-only") or git("diff", "--cached", "--name-only")
    ):
        raise KSReductionError("KR_ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KSReductionError("STABLE_ANCESTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("branch", "--show-current", cwd=nested) or git("status", "--short", cwd=nested)
    ):
        raise KSReductionError("NESTED_AUTHORITY_MISMATCH")

    source = SOURCE.read_bytes()
    if (
        len(source) != 1213 or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source.startswith(b"\xef\xbb\xbf") or not source.endswith(b"\n")
        or source != exact_human_bytes() or git("ls-files", "--", SOURCE.relative_to(ROOT).as_posix())
    ):
        raise KSReductionError("HUMAN_SOURCE_IMMUTABILITY_FAILURE")
    source.decode("utf-8")
    required_source_fragments = (
        GENERATION, OPERATION, CANDIDATE_SHA256, DECISION_PRESENTATION_SHA256,
        "AUTHORITY_SCOPE ONE_KN_GENERATION__ONE_KN_OPERATION__ONE_AUTHORITY_CONSUMPTION_MAXIMUM__ONE_OPERATIONAL_ATTEMPT_MAXIMUM",
        "EXPECTED_ROUTE FM_TO_ER_TO_P11", "E05_BEFORE_OPERATION VERIFIED__11_OF_18",
        "EXPIRED_BEFORE_OPERATION NOT_PROVEN_OPERATIONALLY",
    )
    if any(fragment not in source.decode("utf-8") for fragment in required_source_fragments):
        raise KSReductionError("HUMAN_SOURCE_SEMANTIC_BINDING_FAILURE")

    kr = load_envelope(KR_REDUCTION, "correction")
    kq = load_envelope(KQ_REDUCTION, "classification")
    if (
        sha256_path(KR_REDUCTION) != KR_FILE_SHA256
        or kr.get("terminal") != "A__KR_CORRECTION_VERIFIED__EXISTING_KN_SOURCE_READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
        or kr.get("correction", {}).get("correction_status") != "SUPERSEDED_FOR_FORWARD_KN_ACCEPTANCE_BY_AUTHENTICATED_KQ_CLASSIFICATION"
        or kr.get("anti_weakening", {}).get("anti_weakening_status") != "VERIFIED__ALL_AUTHENTICATED_ACCEPTANCE_INVARIANTS_RETAINED"
        or kr.get("human_source", {}).get("source_acceptance_readiness") != "VERIFIED__READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION_STEP__NOT_AUTHORITY_OR_BINDING"
        or any(kr.get("operational_counters", {}).values()) or kr.get("phase_b_started") is not False
        or kq.get("provenance_capability", {}).get("status") != "CURRENT_REQUIREMENT_NOT_AUTHENTICATED"
    ):
        raise KSReductionError("KR_OR_KQ_AUTHENTICATION_FAILURE")

    paths = {
        CONTEXT: CONTEXT_FILE_SHA256, CANDIDATE: CANDIDATE_SHA256,
        REQUEST: REQUEST_FILE_SHA256, AUTH_PRESENTATION: AUTH_PRESENTATION_SHA256,
        DECISION_PRESENTATION: DECISION_PRESENTATION_SHA256,
        KN / "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": READINESS_FILE_SHA256,
        KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
        ROOT / ".github/governance/evidence/g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1/G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": KM_FILE_SHA256,
        ROOT / ".github/governance/evidence/g77_256kj_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py": KJ_BINDER_SHA256,
    }
    if any(sha256_path(path) != expected for path, expected in paths.items()):
        raise KSReductionError("KN_COORDINATE_FILE_HASH_MISMATCH")
    request = load_envelope(REQUEST, "request")
    readiness = load_envelope(KN / "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json", "checkpoint")
    safe_stop = load_envelope(KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json", "checkpoint")
    km = load_envelope(ROOT / ".github/governance/evidence/g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1/G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction")
    context = json.loads(CONTEXT.read_bytes())
    temporal_sha = hashlib.sha256(canonical_bytes(context["preclaim_temporal_binding"])).hexdigest()
    if (
        json.loads(REQUEST.read_bytes()).get("request_sha256") != REQUEST_SHA256
        or set(request.get("preauthorization", {})) != GN_FIELDS
        or len(request.get("preauthorization", {})) != 10
        or readiness.get("schema_id") != "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1"
        or safe_stop.get("terminal") != "A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
        or context.get("generation_identity") != GENERATION or context.get("operation_identity") != OPERATION
        or context.get("context_sha256") != CONTEXT_SHA256
        or context.get("canonical_argv_sha256") != CANONICAL_ARGV_SHA256
        or context.get("candidate_manifest_sha256") != CANDIDATE_SHA256
        or temporal_sha != TEMPORAL_BINDING_SHA256
        or km.get("reduction_sha256") is not None
    ):
        raise KSReductionError("KN_EXACT_COORDINATE_OR_GN_SCHEMA_MISMATCH")
    if (
        json.loads((KN / "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json").read_bytes()).get("checkpoint_sha256") != READINESS_INNER_SHA256
        or json.loads((KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json").read_bytes()).get("checkpoint_sha256") != SAFE_STOP_INNER_SHA256
        or json.loads((ROOT / ".github/governance/evidence/g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1/G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json").read_bytes()).get("reduction_sha256") != KM_INNER_SHA256
    ):
        raise KSReductionError("KN_OR_KM_INNER_SEAL_MISMATCH")

    forbidden = (
        "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
        "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
    )
    if any((KN / name).exists() or (KN / name).is_symlink() for name in forbidden):
        raise KSReductionError("KN_AUTHORITY_OR_OPERATION_NAMESPACE_COLLISION")

    jz = load_envelope(JZ_READINESS, "proof")
    if (
        jz.get("binding_is_authority") is not False
        or jz.get("authority_consumption_count") != 0
        or jz.get("caller_digest_input_count") != 0
        or jz.get("provider_digest_input_count") != 0
        or jz.get("posthuman_binding_owner") != "FM.build_preconsumption_invocation_binding_THEN_FM.validate_preconsumption_invocation_binding"
    ):
        raise KSReductionError("JZ_PRECONSUMPTION_OWNER_MISMATCH")

    fm = load_fm()
    authorization = build_projected_authorization(context, fm)
    if set(authorization) != fm.authorization_fields(authorization):
        raise KSReductionError("PROJECTED_AUTHORIZATION_SCHEMA_MISMATCH")
    handoff_bytes = fm.canonical_authority_handoff_bytes(authorization)
    parsed = fm.parse_authority_handoff_bytes(handoff_bytes)
    if (
        hashlib.sha256(handoff_bytes).hexdigest() != PROJECTED_HANDOFF_SHA256
        or parsed.get("authorization_sha256") != PROJECTED_AUTHORIZATION_SHA256
        or parsed.get("authorization") != authorization
        or len(handoff_bytes) != 1715
    ):
        raise KSReductionError("CANONICAL_HANDOFF_PROJECTION_MISMATCH")
    return {"context": context, "authorization": authorization, "handoff_byte_count": len(handoff_bytes)}


def build_readiness() -> dict[str, Any]:
    return {
        "schema_id": "G77_256KS_CANONICAL_BINDING_READINESS_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A__REPOSITORY_ONLY_AUTHENTICATION_AND_BINDING_READINESS",
        "entry": {"branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT, "origin": ORIGIN, "remote_head": HEAD, "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE", "ancestry_anchor": ANCHOR, "ancestry_verified": True, "index_empty": True, "tracked_diff_empty": True},
        "nested_authority": {"origin": "git@github.com:Aljosa3/sapianta-core.git", "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1", "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66", "tree": "7c32ec05efc2be43297849bc38ec8766514a523d", "clean": True, "detached": True, "pinned": True, "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE"},
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "VERIFIED__NEW_REQUIRED_PROOF_EDGE__DISTINCT_FROM_KR_SOURCE_ACCEPTANCE_READINESS",
            "affected_invariant": "EXACT_AUTHENTICATED_HUMAN_DECISION_MUST_BIND_CANONICALLY_TO_EXACT_GENERATION_OPERATION_CANDIDATE_CONTEXT_SCOPE_AND_ONE_SHOT_LIMITS_BEFORE_CONSUMPTION",
            "previous_closest_edge": "KR_FORWARD_CORRECTION_AND_EXISTING_KN_SOURCE_ACCEPTANCE_READINESS",
            "semantic_difference": "VERIFIED__KS_AUTHENTICATES_THE_SOURCE_AS_THE_EXACT_HUMAN_DECISION_AND_PROVES_ITS_CANONICAL_HANDOFF_BINDING_SHAPE__KR_DID_NEITHER",
            "production_behavior_impact": "VERIFIED__NONE",
            "new_capability_required": "NOT_PROVEN__EXISTING_FM_JZ_KA_KG_AUTHORITY_MECHANISM_IS_REUSED",
            "new_proof_required": "VERIFIED__EXACT_HUMAN_AUTHORITY_AUTHENTICATION_PLUS_NONCONSUMING_CANONICAL_BINDING_READINESS",
            "convergence_signal": "VERIFIED__KR_FIRST_BROKEN_EDGE_CLOSED_WITH_EXISTING_MECHANISM_AND_NO_HANDOFF_PERSISTENCE",
            "repetition_pressure": "VERIFIED__HIGH__KN_THROUGH_KS_HAS_NO_E05_MOVEMENT",
            "verification_amplification_risk": "ESTIMATED__MODERATE__CONTROLLED_BY_REUSING_FM_CANONICAL_SERIALIZER_AND_JZ_BINDER",
            "classification_evidence": "VERIFIED__SEALED_KR_AND_KQ__EXACT_KN_SOURCE_REQUEST_PRESENTATIONS_CONTEXT_GN_SCHEMA__FM_KA_KG_JZ_MECHANISM",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "VERIFIED__KR_MINIMUM_LEGAL_NEXT_DELTA_AND_EXISTING_PRECONSUMPTION_PROTOCOL_REQUIRE_AUTHENTICATION_AND_CANONICAL_HANDOFF_BINDINGS_BEFORE_CONSUMPTION",
        },
        "authority_authentication": {
            "authority_authentication_owner": "VERIFIED__HUMAN_AUTHORITY_AT_DIRECT_HUMAN_INTERACTION_BOUNDARY__CANONICAL_HANDOFF_ENFORCED_BY_FM_JZ_KA_KG_CHAIN",
            "authority_authentication_mechanism": "VERIFIED__EXACT_KO_HUMAN_SOURCE_BYTES__DERIVED_SHA256__SEALED_KN_REQUEST_PRESENTATION_CONTEXT_BINDINGS__FM_CANONICAL_HANDOFF_SERIALIZER_AND_STRICT_PARSER",
            "authority_authentication_input": "VERIFIED__EXISTING_UNMODIFIED_KN_HUMAN_SOURCE_PLUS_COMMITTED_REQUEST_PRESENTATIONS_CONTEXT_CANDIDATE_READINESS_AND_SAFE_STOP",
            "authority_authentication_output": "VERIFIED__EXACT_HUMAN_DECISION_AUTHENTICATED_AND_CANONICAL_HANDOFF_PROJECTED_IN_MEMORY__NO_AUTHORITY_FILE_PERSISTED",
            "authority_authentication_bindings": "VERIFIED__GENERATION__OPERATION__VECTOR__SOURCE__PRESENTATION__REQUEST__CONTEXT__CANDIDATE__REPOSITORY_COORDINATES__ARGV__TEMPORAL__SCOPE__ROUTE__LIMITS",
            "authority_authentication_namespace": "VERIFIED__G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1__ABSENT_AND_UNCONSUMED",
            "authority_authentication_collision_guard": "VERIFIED__HANDOFF_BINDING_CHECKPOINT_CONSUMPTION_INVOCATION_AND_RESULT_PATHS_ALL_ABSENT",
            "authority_authentication_replay_guard": "VERIFIED__AUTHORIZATION_NONREUSABLE__REPLAY_LIMIT_ZERO__REPLAY_COUNT_ZERO",
            "authority_authentication_consumption_boundary": "VERIFIED__CANONICAL_HANDOFF_PREPARATION_IS_NONCONSUMING__TERMINAL_CONSUMPTION_CHECKPOINT_AND_OPERATION_REMAIN_SEPARATE_AND_NOT_ENTERED",
            "authority_authentication_reuse_legality": "VERIFIED__EXISTING_FM_SERIALIZER_JZ_BINDER_AND_KA_KG_PREPARE_PATTERN_REUSABLE_ONLY_WITH_EXACT_KN_BINDINGS_AND_FRESH_UNCONSUMED_NAMESPACE",
        },
        "human_authority": {
            "human_source_decision_status": "VERIFIED__EXACT_EXISTING_KN_HUMAN_DECISION_OBJECT",
            "human_source_provenance": "VERIFIED__DIRECT_HUMAN_INTERACTION_PROVENANCE_UNDER_KR_RESTORED_AUTHENTICATED_BASELINE__NOT_CALLER_REPOSITORY_OR_DIGEST_ASSERTION_ALONE",
            "human_authority_authentication": "VERIFIED__EXACT_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED__UNBOUND__UNCONSUMED",
            "human_authority_binding_readiness": "VERIFIED__EXACT_CANONICAL_FM_HANDOFF_SHAPE_AND_DIGEST_READY__NO_HANDOFF_FILE_PERSISTED",
            "human_authority_binding": "NOT_APPLICABLE__KS_PROVES_READINESS_ONLY_AND_PERSISTS_NO_AUTHORITY_HANDOFF",
            "authority_present_in_repository": False,
            "authority_consumption_count": 0,
        },
        "binding_readiness": {
            "authority_binding_generation": GENERATION,
            "authority_binding_operation": OPERATION,
            "authority_binding_candidate_sha256": CANDIDATE_SHA256,
            "authority_binding_presentation_sha256": DECISION_PRESENTATION_SHA256,
            "authority_binding_source_sha256": SOURCE_SHA256,
            "authority_binding_scope": "ONE_KN_GENERATION__ONE_KN_OPERATION__ONE_AUTHORITY_CONSUMPTION_MAXIMUM__ONE_OPERATIONAL_ATTEMPT_MAXIMUM",
            "authority_binding_route": "FM_TO_ER_TO_P11",
            "authority_binding_temporal_state": "VERIFIED__KN_PRECLAIM_TEMPORAL_BINDING_EXACT__PHASE_A_HEAD_IS_STABLE_ANCESTOR_OF_KS_HEAD__CURRENT_HEAD_OPERATIONAL_ADMISSION_NOT_ASSERTED",
            "authority_binding_namespace": ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
            "authority_binding_collision_status": "VERIFIED__ABSENT__FRESH_UNCONSUMED_NAMESPACE",
            "authority_binding_replay_status": "VERIFIED__ZERO__NONREUSABLE__NO_REPLAY",
            "projected_canonical_handoff_file_sha256": PROJECTED_HANDOFF_SHA256,
            "projected_authorization_inner_sha256": PROJECTED_AUTHORIZATION_SHA256,
            "projected_canonical_byte_count": 1715,
            "projection_class": "REPOSITORY_ONLY_IN_MEMORY_DERIVATION__NOT_PERSISTED_AUTHORITY__NOT_BINDING",
        },
        "kn_coordinates": {"generation": GENERATION, "operation": OPERATION, "candidate_sha256": CANDIDATE_SHA256, "context_sha256": CONTEXT_SHA256, "context_file_sha256": CONTEXT_FILE_SHA256, "canonical_argv_sha256": CANONICAL_ARGV_SHA256, "temporal_binding_sha256": TEMPORAL_BINDING_SHA256, "request_identity_sha256": REQUEST_SHA256, "request_file_sha256": REQUEST_FILE_SHA256, "authorization_presentation_sha256": AUTH_PRESENTATION_SHA256, "human_decision_presentation_sha256": DECISION_PRESENTATION_SHA256, "readiness_checkpoint_inner_sha256": READINESS_INNER_SHA256, "readiness_checkpoint_file_sha256": READINESS_FILE_SHA256, "safe_stop_checkpoint_inner_sha256": SAFE_STOP_INNER_SHA256, "safe_stop_checkpoint_file_sha256": SAFE_STOP_FILE_SHA256, "km_reduction_file_sha256": KM_FILE_SHA256, "km_inner_sha256": KM_INNER_SHA256, "corrected_kj_binder_sha256": KJ_BINDER_SHA256, "gn_exact_preauthorization_field_count": 10, "gn_exact_preauthorization_schema": "VERIFIED__UNCHANGED"},
        "cross_vector_reuse_assessment": {"cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE", "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN", "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION", "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"], "vector_specific_residue": "DIRECT_INTERACTION_EVIDENCE__SOURCE_BYTES__PRESENTATION__SCOPE__TEMPORAL_VALIDITY__AUTHORITY_AUTHENTICATION__OPERATIONAL_ACCEPTANCE__E05_CREDIT", "reuse_preconditions": "EXACT_PER_GENERATION_BINDINGS__FRESH_UNCONSUMED_NAMESPACE__CANONICAL_HANDOFF_VALIDATION__NO_AUTHORITY_TRANSFER", "revalidation_required": "VERIFIED__PER_GENERATION_VECTOR_HUMAN_ACT_BINDING_AND_OPERATION", "expected_future_proof_reduction": "ESTIMATED__REUSE_FM_SERIALIZER_JZ_DIGEST_BINDER_COLLISION_AND_ONE_SHOT_GUARDS__NO_OPERATIONAL_OR_E05_TRANSFER"},
        "frontier": {"last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD", "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR", "last_verified_edge": "KS_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED_AND_CANONICAL_BINDING_READINESS_VERIFIED", "first_broken_edge": "ACTUAL_NONCONSUMING_CANONICAL_HANDOFF_AND_PRECONSUMPTION_BINDING_MATERIALIZATION", "current_real_blocker": "VERIFIED__HUMAN_REVIEW_AND_COMMITTED_KS_CHECKPOINT_PRECEDE_ANY_ACTUAL_HANDOFF_OR_CONSUMPTION", "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP__EXISTING_NONCONSUMING_HANDOFF_PREPARE_STEP_REMAINS", "minimum_legal_next_delta": "AFTER_COMMITTED_KS_AND_HUMAN_REVIEW__SEPARATE_EXISTING_MECHANISM_CANONICAL_HANDOFF_AND_PRECONSUMPTION_BINDING__STOP_BEFORE_CONSUMPTION"},
        "governance": {"project_state": "VERIFIED__KS_AUTHENTICATION_AND_BINDING_READINESS_COMPLETE__AUTHORITY_UNBOUND_AND_UNCONSUMED", "project_progress": "VERIFIED__KR_FIRST_BROKEN_EDGE_CLOSED_WITH_EXISTING_AUTHORITY_MECHANISM", "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "informal_project_progress_estimate": "ESTIMATED__NONCONSUMING_HANDOFF_PREPARE_AND_LATER_SEPARATE_CONSUMPTION_DECISION_REMAIN", "constitutional_health_evidence": "VERIFIED__EXACT_BINDINGS__FAIL_CLOSED__NO_AUTHORITY_FILE__NO_CONSUMPTION__ONE_ROUTE", "shadow_automation_status": "NOT_APPLICABLE__NO_NEW_AUTOMATION_OR_TRUST_SYSTEM", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "governance_efficiency": "ESTIMATED__HIGH__REUSED_EXISTING_FM_JZ_KA_KG_MECHANISM_AND_CLOSED_REQUIRED_EDGE", "overengineering_risk": "ESTIMATED__LOW__NO_NEW_SIGNER_KEY_PKI_IDP_REGISTRY_OWNER_ROUTE_OR_ABSTRACTION", "cognition_provenance": "VERIFIED__COMMITTED_KR_KQ_KO_KN_KM_JZ_KA_KG_FM_AND_CANONICAL_CONTRACT_EVIDENCE", "cognition_assisted_handoff": "VERIFIED__COMMISSION_TO_AUTHENTICATED_REPOSITORY_CONTINUATION__NO_MEMORY_DEPENDENCY", "candidate_capability": "VERIFIED__EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATION_AND_BINDING_READINESS_ONLY__NOT_OPERATIONAL", "shadow_design_target": "VERIFIED__EXISTING_NONCONSUMING_FM_HANDOFF_PREPARE_THEN_SEPARATE_ONE_SHOT_CONSUMPTION_BOUNDARY", "constitutional_continuation_progress": "VERIFIED__SOURCE_READINESS_ADVANCED_TO_AUTHENTICATED_HUMAN_DECISION_AND_CANONICAL_BINDING_READINESS"},
        "e05": {"state": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0", "new_operational_capability_count": "VERIFIED__0", "new_blocker_localized_count": "VERIFIED__0", "new_blocker_closed_count": "VERIFIED__1__KR_AUTHORITY_AUTHENTICATION_AND_BINDING_READINESS_EDGE", "new_false_or_superseded_blocker_removed_count": "VERIFIED__0", "new_classification_result_count": "VERIFIED__1__HUMAN_AUTHORITY_AUTHENTICATED_AND_BINDING_READY", "authority_authentication_edge_count": "VERIFIED__1", "authority_binding_readiness_edge_count": "VERIFIED__1", "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "observed_artifact_level_cross_worker_drift": "VERIFIED__0"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "operational_counters": zero_counters(), "phase_b_started": False,
        "auto_continuable": False, "human_review_required": True,
    }


def envelope() -> dict[str, Any]:
    readiness = build_readiness()
    return {"schema_id": "G77_256KS_CANONICAL_BINDING_READINESS_ENVELOPE_V1", "readiness": readiness, "readiness_sha256": hashlib.sha256(canonical_bytes(readiness)).hexdigest()}


def verify() -> None:
    authenticate_inputs()
    if load_envelope(OUTPUT, "readiness") != build_readiness():
        raise KSReductionError("KS_READINESS_CONTENT_MISMATCH")
    print(TERMINAL)


def write() -> None:
    authenticate_inputs()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KSReductionError("KS_READINESS_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("write", "verify"), default="verify", nargs="?")
    args = parser.parse_args()
    write() if args.mode == "write" else verify()


if __name__ == "__main__":
    main()
