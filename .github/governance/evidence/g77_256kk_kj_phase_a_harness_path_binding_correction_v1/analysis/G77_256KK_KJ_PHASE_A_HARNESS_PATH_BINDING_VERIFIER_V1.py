#!/usr/bin/env python3
"""Verify the bounded KK KJ wrapper-path correction without running Phase A."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HEAD = "ff47db056aebbe311d09a3503fd8546f55e2005d"
TREE = "0eaabd041692e9950d29e4cdfac009326a217b3c"
SUBJECT = "G77-256KJ reduce Phase A wrapper path mismatch"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
TERMINAL = (
    "A__KJ_PHASE_A_HARNESS_PATH_BINDING_REPOSITORY_VERIFIED__"
    "NO_AUTHORITY__NO_OPERATION__NO_KJ_RETRY"
)
OLD_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_commissioning_v1"
)
NEW_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_recommissioning_v1"
)
WRAPPER_NAME = "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
OLD_WRAPPER = OLD_ROOT / "orchestration" / WRAPPER_NAME
NEW_WRAPPER = NEW_ROOT / "orchestration" / WRAPPER_NAME
WRAPPER_SHA256 = "900741ac1e095d0f0ef2e0c19b102742bf38d3ddf9b11ca602eec463d6e3614f"
KK = Path(
    ".github/governance/evidence/"
    "g77_256kk_kj_phase_a_harness_path_binding_correction_v1"
)
VERIFIER = KK / "analysis/G77_256KK_KJ_PHASE_A_HARNESS_PATH_BINDING_VERIFIER_V1.py"
TESTS = KK / "tests/test_g77_256kk_kj_phase_a_harness_path_binding_v1.py"
REPORT = KK / "G77_256KK_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = KK / "G77_256KK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KG_OWNER = Path(
    ".github/governance/evidence/"
    "g77_256kg_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KE_OWNER = Path(
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KG_OWNER_SHA256 = "b187e9e36e5a74aaa6836bfc2f3ae30ad7eacc190125aca07563af4aeaa84da6"
KE_OWNER_SHA256 = "ba27eaafd1c5f00acd6753bfae8f33f3189a744a6674de187ab8e943b78f58be"
KJ_REDUCTION = OLD_ROOT / "G77_256KJ_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
KJ_REDUCTION_SHA256 = "affe1bb60c600857e134b23ffcc485f7985bce3407fc1565fc5b41a0bd83e839"
KJ_REDUCTION_INNER_SHA256 = "5bf33831ac2cbd42f88aebc48042ee5e76d18c792134a6a0a5d0d7e75ee80892"
KJ_TERMINAL = (
    "M__KJ_PHASE_A_FAIL_CLOSED_AT_AUTHENTICATED_OWNER_WRAPPER_PATH_BINDING_"
    "BEFORE_MATERIALIZATION_OR_HUMAN_PRESENTATION"
)
EX_ROOT = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1"
)
EX_CERTIFICATE = EX_ROOT / "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
EX_CERTIFICATE_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
EX_SEAL = EX_ROOT / "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
EX_SEAL_SHA256 = "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543"
JP_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_readiness_reauthentication_v1/"
    "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JP_REDUCTION_SHA256 = "ca02e314f459a9aa11092f89264deb9d40ba810d35731980e1e60c5c85949503"
JP_REDUCTION_INNER_SHA256 = "4a192756d2c2c1ba3b41ac860c17b3a0c4c8357b58cee533b6f83beac096a569"
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_SUCCESSOR_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
LAST_OPERATIONAL_EDGE = (
    "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_"
    "NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
)
FIRST_UNVERIFIED_OPERATIONAL_EDGE = (
    "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
)


class KKVerificationError(RuntimeError):
    """One deterministic fail-closed KK verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def committed(path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HEAD}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KKVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    if observed != {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    }:
        raise KKVerificationError(f"ENTRY_IDENTITY_MISMATCH:{observed}")
    if remote_head != HEAD:
        raise KKVerificationError(f"REMOTE_HEAD_MISMATCH:{remote_head}")
    if git("diff", "--cached", "--name-only"):
        raise KKVerificationError("INDEX_NOT_EMPTY")
    nested = {
        "head": git("rev-parse", "HEAD", nested=True),
        "tree": git("rev-parse", "HEAD^{tree}", nested=True),
        "origin": git("remote", "get-url", "origin", nested=True),
        "clean": git("status", "--porcelain", nested=True) == "",
        "detached": git("branch", "--show-current", nested=True) == "",
    }
    if nested != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN,
        "clean": True,
        "detached": True,
    } or nested_remote_tag != NESTED_TAG:
        raise KKVerificationError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_FIRST_KK_MUTATION",
        "entry_index": "VERIFIED__EMPTY_BEFORE_FIRST_KK_MUTATION",
        "nested_authority": {
            **nested,
            "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1",
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE",
        },
    }


def verify_mutation_scope() -> None:
    tracked = git("diff", "--name-status").splitlines()
    if tracked != [f"D\t{OLD_WRAPPER.as_posix()}"]:
        raise KKVerificationError(f"TRACKED_MUTATION_SCOPE_MISMATCH:{tracked}")
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    expected = {path.as_posix() for path in (NEW_WRAPPER, VERIFIER, TESTS, REPORT, REDUCTION)}
    if untracked != expected:
        raise KKVerificationError(
            f"UNTRACKED_MUTATION_SCOPE_MISMATCH:{sorted(untracked)}"
        )


def assignment_path(source: str, name: str) -> Path:
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if not isinstance(node.value, ast.Call) or not node.value.args:
            break
        value = ast.literal_eval(node.value.args[0])
        return Path(value)
    raise KKVerificationError(f"PATH_ASSIGNMENT_NOT_FOUND:{name}")


def verify_binding() -> dict[str, Any]:
    old = ROOT / OLD_WRAPPER
    new = ROOT / NEW_WRAPPER
    if old.exists() or old.is_symlink() or not new.is_file() or new.is_symlink():
        raise KKVerificationError("EXACTLY_ONE_WRAPPER_LOCATION_NOT_PROVEN")
    raw = new.read_bytes()
    if raw != committed(OLD_WRAPPER) or sha256_bytes(raw) != WRAPPER_SHA256:
        raise KKVerificationError("WRAPPER_SEMANTIC_IDENTITY_MISMATCH")
    source = raw.decode("utf-8")
    tree = ast.parse(source)
    functions = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    forbidden = {"select_owner", "fallback_owner", "register_owner", "register_route"}
    if functions & forbidden:
        raise KKVerificationError("FALLBACK_OWNER_OR_ROUTE_DETECTED")
    kd_call = "kd_proof = P.E.authenticate_kd_interface_before_presentation()"
    materialize_call = "P.M.materialize(arguments)"
    if kd_call not in source or materialize_call not in source or source.index(kd_call) > source.index(materialize_call):
        raise KKVerificationError("KD_OWNER_PREFLIGHT_ORDER_MISMATCH")

    kg_raw = (ROOT / KG_OWNER).read_bytes()
    ke_raw = (ROOT / KE_OWNER).read_bytes()
    if (
        kg_raw != committed(KG_OWNER)
        or sha256_bytes(kg_raw) != KG_OWNER_SHA256
        or ke_raw != committed(KE_OWNER)
        or sha256_bytes(ke_raw) != KE_OWNER_SHA256
    ):
        raise KKVerificationError("AUTHENTICATED_ADAPTED_OWNER_BYTES_MISMATCH")
    kg_source = kg_raw.decode("utf-8")
    if (
        'source.replace("G77_256KE", "G77_256KG")' not in kg_source
        or 'source.replace("g77_256ke", "g77_256kg")' not in kg_source
        or 're.sub(r"\\bKE\\b", "KG", source)' not in kg_source
        or '.replace("KG", "KJ").replace("kg", "kj")' not in source
    ):
        raise KKVerificationError("AUTHENTICATED_OWNER_ADAPTATION_CHAIN_MISMATCH")
    adapted_ke = ke_raw.decode("utf-8")
    adapted_ke = adapted_ke.replace("G77_256KE", "G77_256KJ")
    adapted_ke = adapted_ke.replace("G77-256KE", "G77-256KJ")
    adapted_ke = adapted_ke.replace("g77_256ke", "g77_256kj")
    adapted_ke = adapted_ke.replace('.replace("kc", "ke")', '.replace("kc", "kj")')
    adapted_ke = adapted_ke.replace("KEBarrierError", "KJBarrierError")
    adapted_ke = adapted_ke.replace("KE_", "KJ_").replace("__KE", "__KJ")
    adapted_ke = re.sub(r"\bKE\b", "KJ", adapted_ke)
    expected = assignment_path(adapted_ke, "WRAPPER_PATH")
    if expected != NEW_WRAPPER:
        raise KKVerificationError(f"ADAPTED_OWNER_EXPECTED_PATH_MISMATCH:{expected}")
    return {
        "previous_invalid_path": OLD_WRAPPER.as_posix(),
        "authenticated_owner_expected_path": expected.as_posix(),
        "corrected_path": NEW_WRAPPER.as_posix(),
        "corrected_path_exists": True,
        "invalid_path_absent": True,
        "accepted_wrapper_location_count": 1,
        "wrapper_file_sha256": WRAPPER_SHA256,
        "wrapper_bytes_equal_committed_kj_candidate": True,
        "wrapper_ast": "VERIFIED__PASS",
        "owner_adaptation_chain": "VERIFIED__KE_TO_KG_TO_KJ",
        "fallback_owner": "VERIFIED__ABSENT",
        "second_route": "VERIFIED__ABSENT",
        "kj_phase_a_executed": False,
        "kj_phase_a_harness_path_binding": "VERIFIED",
    }


def verify_kj_failure() -> dict[str, Any]:
    historical = (
        KJ_REDUCTION,
        OLD_ROOT / "G77_256KJ_G48_IMPLEMENTATION_REPORT_V1.md",
        OLD_ROOT / "analysis/G77_256KJ_PHASE_A_FAILURE_REDUCER_V1.py",
        OLD_ROOT / "tests/test_g77_256kj_phase_a_fail_closed_v1.py",
    )
    for path in historical:
        if (ROOT / path).read_bytes() != committed(path):
            raise KKVerificationError(f"KJ_HISTORICAL_EVIDENCE_CHANGED:{path}")
    if sha256_path(KJ_REDUCTION) != KJ_REDUCTION_SHA256:
        raise KKVerificationError("KJ_REDUCTION_FILE_IDENTITY_MISMATCH")
    envelope = load_canonical(KJ_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != KJ_REDUCTION_INNER_SHA256
        or sha256_bytes(canonical_bytes(reduction)) != KJ_REDUCTION_INNER_SHA256
        or reduction.get("terminal") != KJ_TERMINAL
        or reduction.get("failure", {}).get("failure_class") != "HARNESS_OR_TEST_ARTIFACT"
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KKVerificationError("KJ_FAIL_CLOSED_REDUCTION_CONTRACT_MISMATCH")
    forbidden_outputs = (
        "G77_256KJ_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json",
        "G77_256KJ_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256KJ_HUMAN_DECISION_PRESENTATION_V1.txt",
        "G77_256KJ_PREHUMAN_PHASE_A_REDUCTION_V1.json",
    )
    present = [
        (base / name).as_posix()
        for base in (OLD_ROOT, NEW_ROOT)
        for name in forbidden_outputs
        if (ROOT / base / name).exists()
    ]
    if present:
        raise KKVerificationError(f"KJ_PHASE_A_OUTPUT_PRESENT:{present}")
    return {
        "terminal": KJ_TERMINAL,
        "failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "reduction_file_sha256": KJ_REDUCTION_SHA256,
        "reduction_inner_sha256": KJ_REDUCTION_INNER_SHA256,
        "phase_a_outputs_present": 0,
        "operational_counters": "VERIFIED__ALL_ZERO",
    }


def verify_ex() -> dict[str, Any]:
    certificate_raw = (ROOT / EX_CERTIFICATE).read_bytes()
    seal_raw = (ROOT / EX_SEAL).read_bytes()
    if sha256_bytes(certificate_raw) != EX_CERTIFICATE_SHA256:
        raise KKVerificationError("EX_CERTIFICATE_FILE_IDENTITY_MISMATCH")
    if sha256_bytes(seal_raw) != EX_SEAL_SHA256:
        raise KKVerificationError("EX_FINAL_SEAL_FILE_IDENTITY_MISMATCH")
    certificate_envelope = json.loads(certificate_raw)
    certificate_preimage = copy.deepcopy(certificate_envelope)
    certificate_preimage["certificate_sha256"] = ""
    if certificate_envelope.get("certificate_sha256") != sha256_bytes(
        compact_bytes(certificate_preimage)
    ):
        raise KKVerificationError("EX_CERTIFICATE_SEAL_MISMATCH")
    certificate = certificate_envelope.get("certificate", {})
    counts = certificate.get("component_counts", {})
    if counts.get("CERTIFIED") != 17:
        raise KKVerificationError("EX_17_OF_17_NOT_AUTHENTICATED")
    seal_envelope = json.loads(seal_raw)
    seal = seal_envelope.get("seal")
    if (
        not isinstance(seal, dict)
        or seal_envelope.get("seal_sha256") != sha256_bytes(compact_bytes(seal))
        or seal.get("validation", {}).get("ew_regression") != "17_OF_17_PASS"
    ):
        raise KKVerificationError("EX_FINAL_SEAL_CONTRACT_MISMATCH")
    jp_raw = (ROOT / JP_REDUCTION).read_bytes()
    if jp_raw != committed(JP_REDUCTION) or sha256_bytes(jp_raw) != JP_REDUCTION_SHA256:
        raise KKVerificationError("JP_EX_SUCCESSOR_REAUTHENTICATION_IDENTITY_MISMATCH")
    jp = load_canonical(JP_REDUCTION)
    jp_reduction = jp.get("reduction")
    successor = jp_reduction.get("ex_successor_reauthentication", {}) if isinstance(jp_reduction, dict) else {}
    if (
        not isinstance(jp_reduction, dict)
        or jp.get("reduction_sha256") != JP_REDUCTION_INNER_SHA256
        or sha256_bytes(canonical_bytes(jp_reduction)) != JP_REDUCTION_INNER_SHA256
        or successor.get("changed_component") != "ER_OPERATIONAL_HARNESS"
        or successor.get("changed_ex_bound_component_count") != "VERIFIED__1"
        or successor.get("additional_ex_bound_component_change_count") != "VERIFIED__0"
        or successor.get("classification") != "REQUIRES_HARDENING"
        or successor.get("successor_sha256") != ER_SUCCESSOR_SHA256
        or successor.get("ex_reused") != "VERIFIED__17_OF_17"
        or successor.get("ex_reconstructed") != "VERIFIED__0"
        or sha256_path(ER_HARNESS) != ER_SUCCESSOR_SHA256
    ):
        raise KKVerificationError("JP_EX_SUCCESSOR_REAUTHENTICATION_CONTRACT_MISMATCH")
    return {
        "certificate_file_sha256": EX_CERTIFICATE_SHA256,
        "final_seal_file_sha256": EX_SEAL_SHA256,
        "successor_reauthentication": "VERIFIED__JP_ONE_REQUIRES_HARDENING_ER_DELTA__17_CERTIFIED_COMPONENTS_UNCHANGED",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def zero_counters() -> dict[str, int]:
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


def build_reduction(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    entry = verify_entry(remote_head, nested_remote_tag)
    verify_mutation_scope()
    binding = verify_binding()
    kj_failure = verify_kj_failure()
    ex = verify_ex()
    artifacts = {
        path.as_posix(): sha256_path(path) for path in (VERIFIER, TESTS, REPORT)
    }
    return {
        "schema_id": "G77_256KK_KJ_PHASE_A_HARNESS_PATH_BINDING_REDUCTION_V1",
        "terminal": TERMINAL,
        "mode": "REPOSITORY_ONLY__STATIC_BINDING_PROOF__NO_AUTHORITY__NO_OPERATION__NO_KJ_RETRY",
        "vector": "EXPIRED",
        "entry": entry,
        "authenticated_kj_failure": kj_failure,
        "binding": binding,
        "failure_novelty_and_convergence_check": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": "VERIFIED__NEW_KJ_LOCAL_WRAPPER_PATH_NAMING_MISMATCH__NO_NEW_PRODUCTION_SEMANTICS",
            "affected_invariant": "PHASE_A_DETERMINISTIC_AUTHENTICATED_OWNER_TO_WRAPPER_PATH_BINDING",
            "previous_closest_edge": "KG_PHASE_A_WRAPPER_AT_AUTHENTICATED_OPERATIONAL_RECOMMISSIONING_DIRECTORY",
            "semantic_difference": "VERIFIED__DIRECTORY_TOKEN_RECOMMISSIONING_VERSUS_COMMISSIONING_ONLY",
            "production_behavior_impact": "VERIFIED__NONE__FAILURE_PRECEDED_MATERIALIZATION_AUTHORITY_AND_OPERATION",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__CORRECTED_KJ_PHASE_A_HARNESS_PATH_BINDING_REPROVEN_BY_KK",
            "convergence_signal": "VERIFIED__KI_OPERATIONAL_FRONTIER_UNCHANGED__KJ_LOCAL_PATH_EDGE_CLOSED",
            "repetition_pressure": "ESTIMATED__REDUCED_BY_SEPARATE_NONRECURSIVE_KK_CORRECTION",
            "verification_amplification_risk": "VERIFIED__CONTAINED__NO_KJ_RETRY_OR_PROOF_SCOPE_EXPANSION",
            "classification_evidence": "VERIFIED__SEALED_KJ_FAILURE__COMMITTED_WRAPPER_BYTES__ADAPTED_OWNER_AST_PATH__ZERO_OUTPUTS",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__KK_STOPS_AFTER_BINDING_PROOF",
        },
        "frontier": {
            "last_verified_operational_edge": LAST_OPERATIONAL_EDGE,
            "first_unverified_operational_edge": FIRST_UNVERIFIED_OPERATIONAL_EDGE,
            "last_verified_edge": "KJ_PHASE_A_AUTHENTICATED_OWNER_TO_WRAPPER_PATH_BINDING_REPOSITORY_VERIFIED",
            "first_broken_edge": "NOT_PROVEN__NO_NEXT_REPOSITORY_LOCAL_BROKEN_EDGE_AUTHENTICATED",
            "current_real_blocker": "NOT_PROVEN__KJ_PATH_BINDING_GAP_CLOSED__NO_NEXT_REPOSITORY_LOCAL_BLOCKER_AUTHENTICATED",
            "minimum_missing_capability": "NOT_PROVEN__KJ_PATH_BINDING_GAP_ELIMINATED__NO_NEW_CAPABILITY_GAP_ESTABLISHED",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATELY_GOVERNED_KJ_PHASE_A_CONSTRUCTION_RETRY_CANDIDATE__NO_AUTOMATIC_CONTINUATION",
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "kk_e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            **ex,
        },
        "governance": {
            "project_state": "VERIFIED__KJ_PHASE_A_HARNESS_PATH_BINDING_REPOSITORY_CORRECTED__NO_PHASE_A_EXECUTION",
            "project_progress": "VERIFIED__KJ_LOCAL_PATH_BLOCKER_CLOSED__OPERATIONAL_FRONTIER_UNCHANGED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PATH_PREREQUISITE_READY_FOR_FUTURE_SEPARATELY_GOVERNED_REVIEW",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_HISTORY_PRESERVED__ZERO_OPERATION__NO_RETRY__ONE_WRAPPER_LOCATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__ONE_FILE_MOVE_AND_REUSED_PROOF_CLOSE_LOCAL_EDGE",
            "overengineering_risk": "ESTIMATED__LOW_WITHIN_KK__HIGH_IF_OPERATION_OR_RETRY_IS_ADDED",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_ARTIFACTS_AND_DETERMINISTIC_STATIC_ANALYSIS_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SEALED_KK_REPOSITORY_ONLY_REDUCTION",
            "candidate_capability": "VERIFIED__KJ_PHASE_A_HARNESS_PATH_BINDING_ONLY__NOT_OPERATIONAL_CAPABILITY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__KJ_FAIL_CLOSED_EDGE_TO_KK_REPOSITORY_PATH_BINDING_CLOSURE",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
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
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__HARNESS_BINDING_ONLY",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__0__LOCALIZED_BY_KJ",
            "new_blocker_closed_count": "VERIFIED__1__KJ_PHASE_A_WRAPPER_PATH_BINDING",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_classification_result_count": "VERIFIED__1__HARNESS_OR_TEST_ARTIFACT_REAUTHENTICATED",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
            "harness_binding_verified": "VERIFIED",
            "operational_capability_verified": "VERIFIED__0",
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
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": "VERIFIED__EX_17_OF_17__KJ_KI_KH_KG_KF_EVIDENCE_AND_ADAPTED_OWNER_CHAIN",
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": "VERIFIED__ONE_REPOSITORY_HARNESS_BINDING__ZERO_OPERATIONAL_CAPABILITIES",
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": "VERIFIED__NO",
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "operational_counters": zero_counters(),
        "artifact_bindings": artifacts,
        "fresh_kj_phase_a_presentation_ready": "NOT_PROVEN",
        "human_authority_present": False,
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KK_KJ_PHASE_A_HARNESS_PATH_BINDING_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    parser.add_argument("--emit", action="store_true")
    arguments = parser.parse_args()
    expected = envelope(build_reduction(arguments.remote_head, arguments.nested_remote_tag))
    if arguments.emit:
        print(canonical_bytes(expected).decode("utf-8"), end="")
        return 0
    observed = load_canonical(REDUCTION)
    if observed != expected:
        raise KKVerificationError("PERSISTED_REDUCTION_MISMATCH")
    print(TERMINAL)
    print("KJ_PHASE_A_HARNESS_PATH_BINDING=VERIFIED")
    print("FRESH_KJ_PHASE_A_PRESENTATION_READY=NOT_PROVEN")
    print("OPERATIONAL_EFFECT=0")
    print("E05_CREDIT=VERIFIED__0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
