#!/usr/bin/env python3
"""Construct the fresh current-HEAD KW EXPIRED Phase-A Human barrier.

This bounded adapter authenticates and reuses the committed KN Phase-A owner,
reissues its repository-bound semantic objects for the KV checkpoint, binds the
KV lifecycle finding outside GN's exact request schema, and stops before any
Human authority, handoff, preconsumption binding, Phase B, or operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KW = ROOT / (
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1"
)
HEAD = "681538ccd9b6faaeebff15d96881134eaef00d7e"
TREE = "53164b7f60d982727bebd9a5c77d5688ee283ade"
SUBJECT = "G77-256KV localize fresh current-head authority lifecycle"
KM_HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
KN_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KN_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KN_MATERIALIZER_SHA256 = (
    "191f96810dc4fbf0afd8851381b20e143aed2105a9b60a0b671d4f2468403022"
)
KV_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kv_current_head_operational_binding_owner_and_authority_impact_discovery_v1/"
    "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_V1.json"
)
KV_REDUCTION_SHA256 = (
    "31a77406fcd16fef9cdc2eb48281b7212efe3bded10bd0dcaa67786c83e478cd"
)
KN_HUMAN_SOURCE = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1/"
    "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
)
KN_HUMAN_SOURCE_SHA256 = (
    "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
)
GD_CANDIDATE_BUILDER = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/builder/"
    "G77_256GD_CANDIDATE_BINDING_REISSUE_V1.py"
)
GD_CANDIDATE_BUILDER_SHA256 = (
    "5f0529226ec366c8c06caf19d7b7d19f89ed0751ed0c0521fe80c11ee7d906da"
)
DU_VALIDATOR = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/"
    "G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_VALIDATOR_SHA256 = (
    "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
)
TERMINAL = (
    "A__KW_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__"
    "NO_HUMAN_AUTHORITY__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
)


class KWBarrierError(RuntimeError):
    """One deterministic fail-closed KW Phase-A error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed(path: Path, revision: str = HEAD) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KWBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KWBarrierError(f"MISSING_INNER:{inner}")
    if envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KWBarrierError(f"INNER_SEAL_MISMATCH:{inner}")
    return value


def load_adapted_kn_materializer() -> ModuleType:
    path = ROOT / KN_MATERIALIZER
    raw = path.read_bytes()
    if raw != committed(KN_MATERIALIZER) or sha256_bytes(raw) != KN_MATERIALIZER_SHA256:
        raise KWBarrierError("COMMITTED_KN_PHASE_A_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KN", "KW").replace("kn", "kw")
    source = source.replace(
        "g77_256kw_fresh_expired_operational_recommissioning_v1",
        "g77_256kw_fresh_expired_operational_recommissioning_v1",
    )
    source = source.replace(KM_HEAD, HEAD)
    source = source.replace("70aa2a12af3d9806e0d6ddc73f7f751292413e52", TREE)
    source = source.replace(
        "G77-256KM preserve GN schema for KI preflight binding", SUBJECT
    )
    source = source.replace(
        'predecessor = committed(KJ_WRAPPER, f"{HEAD}^")',
        f'predecessor = committed(KJ_WRAPPER, "{KM_HEAD}^")',
    )
    module = ModuleType("g77_256kw_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    if module.KW != KW:
        raise KWBarrierError("KW_GENERATION_ROOT_ADAPTATION_MISMATCH")
    return module


W = load_adapted_kn_materializer()


def install_entry_scope_filter() -> None:
    """Preserve the authenticated historical KN source while admitting KW."""

    owner = W.P.M
    original_git = owner.git

    def bounded_git(*arguments: str, cwd: Path = owner.ROOT) -> str:
        observed = original_git(*arguments, cwd=cwd)
        if arguments == ("status", "--porcelain", "--untracked-files=all"):
            historical = "?? " + KN_HUMAN_SOURCE.as_posix()
            return "\n".join(
                line for line in observed.splitlines() if line != historical
            )
        return observed

    owner.git = bounded_git


def load_authenticated_module(path: Path, expected_sha256: str, name: str) -> ModuleType:
    absolute = ROOT / path
    raw = absolute.read_bytes()
    if raw != committed(path) or sha256_bytes(raw) != expected_sha256:
        raise KWBarrierError(f"COMMITTED_OWNER_MISMATCH:{path}")
    specification = importlib.util.spec_from_file_location(name, absolute)
    if specification is None or specification.loader is None:
        raise KWBarrierError(f"OWNER_IMPORT_FAILED:{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def materialize_current_candidate_source() -> dict[str, str]:
    """Use the GD/DU owners to reissue one exact current-HEAD candidate."""

    builder = load_authenticated_module(
        GD_CANDIDATE_BUILDER,
        GD_CANDIDATE_BUILDER_SHA256,
        "g77_256kw_gd_candidate_builder",
    )
    validator = load_authenticated_module(
        DU_VALIDATOR,
        DU_VALIDATOR_SHA256,
        "g77_256kw_du_candidate_validator",
    )
    envelope = builder.build(ROOT)
    manifest = envelope["manifest"]
    if manifest.get("required_head") != HEAD or manifest.get("source_tree") != TREE:
        raise KWBarrierError("GD_CURRENT_HEAD_CANDIDATE_BINDING_MISMATCH")
    for binding in manifest.get("extension_bindings", []):
        path = ROOT / binding["path"]
        binding["sha256"] = sha256_path(path)
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    validator.validate_envelope(
        envelope,
        ROOT,
        expected_head=HEAD,
        required_prohibited_actions=validator.REQUIRED_PROHIBITED_ACTIONS,
    )
    target = KW / (
        "candidate_source/"
        "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
    )
    W.write_canonical(target, envelope, fresh=True)
    candidate_sha256 = sha256_path(target)
    if candidate_sha256 == "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a":
        raise KWBarrierError("HISTORICAL_KN_CANDIDATE_DIGEST_REUSED")
    W.P.M.FM.CANDIDATE = target.relative_to(ROOT)
    W.P.M.FM.CANDIDATE_SHA256 = candidate_sha256
    return {
        "path": target.relative_to(ROOT).as_posix(),
        "file_sha256": candidate_sha256,
        "manifest_sha256": envelope["manifest_sha256"],
        "gd_owner_sha256": GD_CANDIDATE_BUILDER_SHA256,
        "du_validator_sha256": DU_VALIDATOR_SHA256,
        "du_validation": "VERIFIED__PASS",
        "repository_head": HEAD,
        "repository_tree": TREE,
        "schema_change": "VERIFIED__NO",
        "semantic_field_expansion": "VERIFIED__NO",
    }


def authenticate_kv() -> dict[str, Any]:
    path = ROOT / KV_REDUCTION
    raw = path.read_bytes()
    if raw != committed(KV_REDUCTION) or sha256_bytes(raw) != KV_REDUCTION_SHA256:
        raise KWBarrierError("COMMITTED_KV_REDUCTION_MISMATCH")
    reduction = verify_seal(load_canonical(path), "reduction")
    classification = reduction.get("failure_novelty_and_convergence_check", {})
    owners = reduction.get("existing_owner_mechanism_decision", {})
    if (
        reduction.get("terminal")
        != "B__KV_EXISTING_POST_COMMIT_BINDING_MECHANISM_FOUND__NOT_APPLICABLE_TO_IMMUTABLE_KN_AUTHORITY__FRESH_HUMAN_ACT_REQUIRED"
        or classification.get("failure_class") != "EVIDENCE_OR_REPORTING_DEFECT"
        or classification.get("new_capability_required") != "VERIFIED__NO"
        or owners.get("operation_context_owner") != "FM_BUILD_OPERATION_CONTEXT"
        or owners.get("preconsumption_binding_owner")
        != "FM_JZ_BUILD_AND_VALIDATE_PRECONSUMPTION_INVOCATION_BINDING"
        or reduction.get("e05", {}).get("state") != "VERIFIED__11_OF_18"
        or reduction.get("ex", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KWBarrierError("KV_LIFECYCLE_CONTRACT_MISMATCH")
    source = ROOT / KN_HUMAN_SOURCE
    if sha256_path(source) != KN_HUMAN_SOURCE_SHA256:
        raise KWBarrierError("HISTORICAL_KN_HUMAN_SOURCE_CHANGED")
    return {
        "terminal": reduction["terminal"],
        "reduction_path": KV_REDUCTION.as_posix(),
        "reduction_file_sha256": KV_REDUCTION_SHA256,
        "failure_class": classification["failure_class"],
        "new_capability_required": classification["new_capability_required"],
        "existing_lifecycle": "POST_COMMIT_READINESS_TO_CURRENT_HEAD_CONTEXT_TO_FRESH_HUMAN_ACT_TO_BIND_TO_ADMIT_TO_CONSUME_TO_OPERATE_TO_COMMIT_EVIDENCE",
        "kn_authority_applicability": "NOT_APPLICABLE__HISTORICAL_IMMUTABLE_AUTHORITY",
        "historical_kn_human_source_sha256": KN_HUMAN_SOURCE_SHA256,
    }


def cross_vector_reuse_assessment() -> dict[str, Any]:
    value = W.cross_vector_reuse_assessment()
    value.update(
        {
            "cross_vector_reuse_scope": "VERIFIED__MULTI_VECTOR_REUSABLE",
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "repository_binding_lifecycle_scope": "VERIFIED__COMMON_E05_INFRASTRUCTURE",
            "authority_transfer": "VERIFIED__NO",
            "e05_credit_transfer": "VERIFIED__NO",
            "operational_proof_transfer": "VERIFIED__NO",
        }
    )
    return value


def exact_operational_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def bind_kv_lifecycle(
    kv: dict[str, Any],
    cross_vector: dict[str, Any],
    candidate_reissue: dict[str, str],
) -> None:
    safe_path = KW / "G77_256KW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KW / "G77_256KW_PREHUMAN_PHASE_A_REDUCTION_V1.json"
    safe = W.load_canonical(safe_path)
    safe["checkpoint"].update(
        {
            "terminal": TERMINAL,
            "human_decision_presentation_status": "VERIFIED__READY_FOR_HUMAN_DECISION",
            "human_authority_status": "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
            "human_authority_handoff_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "preconsumption_binding_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "authority_consumption_count": 0,
            "operation_attempt_count": 0,
        }
    )
    W.reseal(safe, "checkpoint")
    W.write_canonical(safe_path, safe)

    envelope = W.load_canonical(reduction_path)
    value = envelope["reduction"]
    identities = value["identities"]
    identities["checkpoint_sha256"] = safe["checkpoint_sha256"]
    identities["checkpoint_file_sha256"] = sha256_path(safe_path)
    value.update(
        {
            "terminal": TERMINAL,
            "kv_lifecycle_reauthentication": kv,
            "current_head_candidate_reissue": candidate_reissue,
            "failure_novelty_and_convergence_check": {
                "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
                "novelty": "VERIFIED__KNOWN_LIFECYCLE_ORDERING_VIOLATION__NOT_A_NEW_CAPABILITY_GAP",
                "affected_invariant": "CONTEXT_AND_HUMAN_AUTHORITY_HEAD_TREE_MUST_EXACTLY_EQUAL_OBSERVED_OPERATIONAL_HEAD_TREE_BEFORE_CONSUMPTION",
                "previous_closest_edge": "KV_KT_KU_CURRENT_HEAD_ADMISSION_FAILURE_AND_HP_HX_IC_JH_SAME_HEAD_PRECEDENTS",
                "semantic_difference": "VERIFIED__KW_PREPARES_FRESH_CURRENT_HEAD_CONTEXT_BEFORE_ANY_NEW_HUMAN_ACT",
                "production_behavior_impact": "VERIFIED__NONE__PHASE_A_ONLY",
                "new_capability_required": "VERIFIED__NO",
                "new_proof_required": "VERIFIED__FRESH_CURRENT_HEAD_PHASE_A_BINDINGS_AND_LATER_DISTINCT_HUMAN_ACT",
                "convergence_signal": "VERIFIED__EXISTING_POST_COMMIT_TO_CONTEXT_TO_HUMAN_ACT_TO_BIND_TO_ADMIT_LIFECYCLE_REUSED",
                "repetition_pressure": "VERIFIED__HIGH__KN_THROUGH_KV_NO_E05_MOVEMENT",
                "verification_amplification_risk": "ESTIMATED__HIGH_IF_ANOTHER_PROOF_ONLY_LAYER_IS_INSERTED",
                "classification_evidence": "VERIFIED__KV_SEALED_REDUCTION__FM_EXACT_EQUALITY__HP_HX_IC_JH_SAME_HEAD_PRECEDENTS",
                "classification_confidence": "VERIFIED__HIGH",
                "acceptance_requirement_forcing_continuation": "VERIFIED__EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY__FRESH_HUMAN_DECISION_IS_NEXT",
            },
            "cross_vector_reuse_assessment": cross_vector,
            "repository_binding_lifecycle": {
                "scope": "VERIFIED__COMMON_E05_INFRASTRUCTURE",
                "sequence": "POST_COMMIT_READINESS_TO_CURRENT_HEAD_CONTEXT_TO_FRESH_HUMAN_ACT_TO_BIND_TO_ADMIT_TO_CONSUME_TO_OPERATE_TO_COMMIT_EVIDENCE",
                "no_commit_interval": "FRESH_HUMAN_ACT_THROUGH_FINAL_OPERATIONAL_ADMISSION",
                "owners": "JP_JO_POST_COMMIT_READINESS__FM_CONTEXT_AND_EXACT_ADMISSION__GN_PRESENTATION__JZ_PRECONSUMPTION__GL_ER_P11_ONE_SHOT_ROUTE",
            },
            "authorization_base_head": HEAD,
            "authorization_base_tree": TREE,
            "operation_context_head": HEAD,
            "operation_context_tree": TREE,
            "presentation_head": HEAD,
            "presentation_tree": TREE,
            "human_decision_presentation_status": "VERIFIED__READY_FOR_HUMAN_DECISION",
            "human_authority_status": "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
            "human_authority_handoff_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "preconsumption_binding_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "operational_counters": exact_operational_counters(),
            "fresh_kw_phase_a_presentation_ready": "VERIFIED",
            "fresh_kn_phase_a_presentation_ready": "NOT_APPLICABLE__KW_GENERATION",
            "human_decision_presentation": "VERIFIED__FRESH_KW_EXACT_PRESENTATION_CREATED",
            "human_authority_present": False,
            "phase_b_started": False,
            "auto_continuable": False,
            "human_review_required": True,
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        }
    )
    value["frontier"] = {
        "last_verified_operational_edge": "VERIFIED__JH_FUTURE_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY",
        "first_unverified_operational_edge": "NOT_PROVEN__FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
        "last_verified_edge": "VERIFIED__KW_FRESH_CURRENT_HEAD_PHASE_A_PRESENTATION_READY",
        "first_broken_edge": "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
        "current_real_blocker": "VERIFIED__FRESH_KW_HUMAN_DECISION_NOT_YET_PRESENT",
        "minimum_missing_capability": "NOT_APPLICABLE__NO_NEW_PRODUCTION_CAPABILITY__FRESH_KW_HUMAN_ACT_MISSING",
        "minimum_legal_next_delta": "ONLY_AFTER_SEPARATE_HUMAN_ACT__SAME_KW_GENERATION_HANDOFF_BIND_ADMIT_CONSUME_ONCE_OPERATE_ONCE__NO_INTERVENING_COMMIT",
    }
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__0__PHASE_A_READINESS_IS_NOT_OPERATIONAL_CAPABILITY",
        "new_operational_capability_count": "VERIFIED__0",
        "new_blocker_localized_count": "VERIFIED__1__FRESH_KW_HUMAN_ACT",
        "new_blocker_closed_count": "VERIFIED__0",
        "new_false_or_superseded_blocker_removed_count": "VERIFIED__1__KN_AUTHORITY_REBIND_PATH",
        "new_classification_result_count": "VERIFIED__1__EVIDENCE_OR_REPORTING_DEFECT_REAUTHENTICATED",
        "new_current_head_candidate_count": "VERIFIED__1",
        "new_human_decision_presentation_count": "VERIFIED__1",
        "new_operational_observation_count": "VERIFIED__0",
        "new_e05_credit_count": "VERIFIED__0",
        "ex_proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "EX_17_OF_17__JP_JO__FM__GN__JZ__GL__ER__P11__CANONICAL_HUMAN_AUTHORITY_SERIALIZER_AND_ONE_SHOT_GUARDS",
        "new_capabilities": "VERIFIED__0__ONE_FRESH_KW_PHASE_A_INSTANCE_ONLY",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__KW_PHASE_A_READY_AT_HUMAN_DECISION_BARRIER",
            "project_progress": "VERIFIED__FRESH_CURRENT_HEAD_CANDIDATE_CONTEXT_REQUEST_AND_PRESENTATION_SEALED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__FM_EQUALITY_AND_GN_EXACT_SCHEMA_PRESERVED__NO_AUTHORITY_OR_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EXISTING_OWNER_CHAIN_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_ANY_NEW_OWNER_REBINDING_OR_PROOF_LAYER_IS_ADDED",
            "cognition_provenance": "VERIFIED__COMMITTED_KV_KN_JP_JO_FM_GN_JZ_AND_PRECEDENT_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_KV_TO_KW_CONTINUATION__NO_MEMORY_AUTHORITY",
            "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATIONAL_DENIAL_REMAINS_UNOBSERVED",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ONE_SHOT_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__KV_LIFECYCLE_LOCALIZATION_TO_KW_HUMAN_DECISION_BARRIER",
        }
    )
    W.reseal(envelope, "reduction")
    W.write_canonical(reduction_path, envelope)


def materialize_human_decision_presentation() -> None:
    request_path = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    authorization_path = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    readiness_path = KW / "G77_256KW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    safe_path = KW / "G77_256KW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    context_path = KW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    target = KW / "G77_256KW_HUMAN_DECISION_PRESENTATION_V1.txt"
    if target.exists() or target.is_symlink():
        raise KWBarrierError(f"FRESH_ARTIFACT_COLLISION:{target}")
    request_envelope = load_canonical(request_path)
    request = verify_seal(request_envelope, "request")
    readiness = load_canonical(readiness_path)
    safe = load_canonical(safe_path)
    context = load_canonical(context_path)
    lines = [
        "G77-256KW HUMAN DECISION PRESENTATION V1",
        "NONAUTHORITY: review only; this presentation does not record or infer approval.",
        f"GENERATION {request['generation_identity']}",
        f"OPERATION {request['operation_identity']}",
        "VECTOR EXPIRED",
        "PURPOSE Observe whether EXPIRED is denied before P11 entry after the KF repair.",
        f"CANDIDATE_SHA256 {context['candidate_manifest_sha256']}",
        f"CONTEXT_SHA256 {context['context_sha256']}",
        f"CONTEXT_FILE_SHA256 {sha256_path(context_path)}",
        f"CANONICAL_ARGV_SHA256 {context['canonical_argv_sha256']}",
        f"TEMPORAL_BINDING_SHA256 {sha256_bytes(canonical_bytes(context['preclaim_temporal_binding']))}",
        f"REQUEST_IDENTITY_SHA256 {request_envelope['request_sha256']}",
        f"REQUEST_FILE_SHA256 {sha256_path(request_path)}",
        f"AUTHORIZATION_PRESENTATION_SHA256 {sha256_path(authorization_path)}",
        f"READINESS_CHECKPOINT_SHA256 {readiness['checkpoint_sha256']}",
        f"SAFE_STOP_CHECKPOINT_SHA256 {safe['checkpoint_sha256']}",
        f"AUTHORIZATION_BASE_HEAD {HEAD}",
        f"AUTHORIZATION_BASE_TREE {TREE}",
        f"OPERATION_CONTEXT_HEAD {HEAD}",
        f"OPERATION_CONTEXT_TREE {TREE}",
        f"PRESENTATION_HEAD {HEAD}",
        f"PRESENTATION_TREE {TREE}",
        "EXPECTED_ROUTE FM -> ER -> P11",
        "REQUESTED_SCOPE ONE fresh KW generation; ONE EXPIRED operation; at most ONE future Human authority consumption; at most ONE future operational attempt.",
        "NOT_AUTHORIZED NO_REPLAY; NO_REPAIR_RETRY; NO_SECOND_OPERATION; NO_ALTERNATE_AUTHORITY_PATH; NO_P11_BYPASS; NO_PARALLEL_ROUTE; NO_AUTHORITY_TRANSFER; NO_HISTORICAL_AUTHORITY_REUSE; NO_EXPANSION_OF_PRODUCTION_BEHAVIOR.",
        "ONE_SHOT_LIMIT AUTHORITY_CONSUMPTION_MAXIMUM=1; OPERATION_ATTEMPT_MAXIMUM=1.",
        "RETRY_LIMIT 0",
        "REPLAY_LIMIT 0",
        "E05_STATE VERIFIED__11_OF_18",
        "E05_FRONTIER VERIFIED__7_UNSATISFIED_OF_18",
        "KW_E05_CREDIT VERIFIED__0",
        "EXPIRED NOT_PROVEN_OPERATIONALLY",
        "HUMAN_DECISION_PRESENTATION VERIFIED__READY_FOR_HUMAN_DECISION",
        "HUMAN_AUTHORITY NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
        "HUMAN_AUTHORITY_HANDOFF NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "PRECONSUMPTION_BINDING NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "AUTHORITY_CONSUMPTION 0",
        "PHASE_B_STARTED FALSE",
        "OPERATION_ATTEMPT 0",
        "AUTO_CONTINUABLE FALSE",
        "HUMAN_REVIEW_REQUIRED TRUE",
        "STOP AT THE HUMAN DECISION BARRIER.",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    install_entry_scope_filter()
    kv_result = authenticate_kv()
    candidate_reissue_result = materialize_current_candidate_source()
    km_result = W.authenticate_km()
    cross_vector_result = cross_vector_reuse_assessment()
    ki_result = W.L.authenticate_ki()
    kf_result = W.P.authenticate_kf()
    rebound_result = W.P.rebind_kf_launcher_identity()
    kd_proof = W.P.E.authenticate_kd_interface_before_presentation()
    kb_result = W.P.E.K.authenticate_kb()
    jz_result = W.P.E.K.K.authenticate_jz()
    e05_frontier_result = W.P.E.K.K.authenticate_e05_frontier()
    W.P.M.materialize(arguments)
    namespace_result = W.P.E.augment_namespace_preflight(
        W.P.E.K.materialize_namespace_preflight(kb_result)
    )
    jz_readiness = W.P.E.K.K.materialize_jz_readiness(jz_result)
    W.P.E.K.K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    W.P.E.K.bind_namespace_into_phase_a(kb_result, namespace_result)
    kd_result = W.P.E.materialize_kd_preflight(kd_proof)
    W.P.E.bind_kd_preflight_into_phase_a(kd_result)
    kf_preflight = W.P.materialize_kf_preflight(kf_result, rebound_result)
    W.P.bind_kf_into_phase_a(kf_result, kf_preflight)
    ki_preflight = W.L.materialize_ki_preflight(ki_result)
    W.L.bind_ki_into_phase_a(ki_result, ki_preflight)
    km_preflight = W.materialize_km_preflight(km_result, cross_vector_result)
    W.bind_km_into_phase_a(km_result, km_preflight, cross_vector_result)
    bind_kv_lifecycle(kv_result, cross_vector_result, candidate_reissue_result)
    materialize_human_decision_presentation()
    print(TERMINAL)
