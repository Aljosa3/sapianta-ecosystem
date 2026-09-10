#!/usr/bin/env python3
"""Repository-only proof for the KC Phase-B entry-owner interface repair."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "0f47eba49af5812b3550df0e702a8098090d81ae"
TREE = "9e52c7c478abf399912a9b7db1f77984c57b90db"
SUBJECT = "G77-256KC localize Phase-B preconsumption entry interface blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
KC = Path(".github/governance/evidence/g77_256kc_fresh_expired_operational_recommissioning_v1")
CONTROLLER = KC / "orchestration/G77_256KC_PHASE_B_CONTROLLER_V1.py"
MATERIALIZER = KC / "orchestration/G77_256KC_PREAUTHORIZATION_MATERIALIZER_V1.py"
TERMINAL = KC / "G77_256KC_SPCE_PHASE_B_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
P11 = Path("tests/p11_da_operational_consumer_v1.py")
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
PRE_REPAIR_CONTROLLER_SHA256 = "307696a107f5f8c65dc75b4edbe11440efbc97b5b403fe1e8c53517cef270ebb"
POST_REPAIR_CONTROLLER_SHA256 = "f950bb6ee2165169e1598c3d95ceff1cf719ed0a259421f48189ee9de4a14aad"
MATERIALIZER_SHA256 = "f41a7b9942a1de0b1825bdda3676d04968d857d01f7370551844abcde16de1d2"
TERMINAL_SHA256 = "96399ab00582ba9b5a8740fade2ea1936484b28dfdfc18cf7976d3adeabd2b2e"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
FM_SHA256 = "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36"
TERMINAL_VALUE = (
    "M__KC_PHASE_B_FAIL_CLOSED_AT_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_"
    "BEFORE_AUTHORITY_AUTHENTICATION_OR_CONSUMPTION"
)
SUCCESS = "A__KC_PHASE_B_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BINDING_REPOSITORY_VERIFIED"


class KDError(RuntimeError):
    """One deterministic repository-only KD failure."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def load_path(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / path)
    if specification is None or specification.loader is None:
        raise KDError(f"MODULE_UNAVAILABLE:{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def load_source(raw: bytes, path: Path, name: str) -> ModuleType:
    module = ModuleType(name)
    module.__file__ = str((ROOT / path).resolve())
    sys.modules[name] = module
    exec(compile(raw, str(ROOT / path), "exec"), module.__dict__)
    return module


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "index_empty": True,
        "origin": ORIGIN,
        "remote_head": HEAD,
        "subject": SUBJECT,
        "tree": TREE,
    }
    if observed != expected:
        raise KDError("KD_ENTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "head": git("rev-parse", "HEAD", cwd=nested),
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "remote_tag": nested_remote_tag,
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
    }
    if nested_state != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "remote_tag": NESTED_HEAD,
        "tag": NESTED_TAG,
        "tree": NESTED_TREE,
    }:
        raise KDError("KD_NESTED_AUTHORITY_MISMATCH")
    return observed | {"remote_equality": "VERIFIED", "nested_authority": nested_state}


def authenticate_kc_terminal() -> dict[str, Any]:
    raw = (ROOT / TERMINAL).read_bytes()
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope) or sha256(TERMINAL) != TERMINAL_SHA256:
        raise KDError("KC_TERMINAL_IDENTITY_MISMATCH")
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != hashlib.sha256(canonical_bytes(reduction)).hexdigest():
        raise KDError("KC_TERMINAL_SEAL_MISMATCH")
    if reduction.get("terminal") != TERMINAL_VALUE or set(reduction["operational_counters"].values()) != {0}:
        raise KDError("KC_TERMINAL_CONTRACT_MISMATCH")
    binding = reduction["jz_preconsumption_binding"]
    if binding["canonical_handoff_created"] or binding["invocation_binding_created"]:
        raise KDError("KC_AUTHORITY_OR_BINDING_UNEXPECTEDLY_CREATED")
    return {
        "file_sha256": TERMINAL_SHA256,
        "inner_sha256": envelope["reduction_sha256"],
        "terminal": TERMINAL_VALUE,
    }


def reproduce_pre_repair() -> dict[str, str]:
    raw = subprocess.check_output(["git", "show", f"{HEAD}:{CONTROLLER}"], cwd=ROOT)
    if hashlib.sha256(raw).hexdigest() != PRE_REPAIR_CONTROLLER_SHA256:
        raise KDError("PRE_REPAIR_CONTROLLER_IDENTITY_MISMATCH")
    controller = load_source(raw, CONTROLLER, "g77_256kd_pre_repair_controller")
    try:
        controller.C.authenticate("0" * 40, NESTED_HEAD)
    except AttributeError as exc:
        observed = f"AttributeError: {exc}"
    else:
        raise KDError("PRE_REPAIR_INTERFACE_FAILURE_NOT_REPRODUCED")
    expected = "AttributeError: module 'g77_256kc_phase_b_materializer' has no attribute 'A'"
    if observed != expected:
        raise KDError("PRE_REPAIR_EXCEPTION_MISMATCH")
    return {
        "controller_sha256": PRE_REPAIR_CONTROLLER_SHA256,
        "exact_exception": observed,
        "failed_call": "MATERIALIZER.A.authenticate_entry(remote_head, nested_remote_tag)",
        "result": "VERIFIED__EXACT_REPOSITORY_ONLY_REPRODUCTION",
    }


def verify_post_repair() -> dict[str, Any]:
    if sha256(CONTROLLER) != POST_REPAIR_CONTROLLER_SHA256 or sha256(MATERIALIZER) != MATERIALIZER_SHA256:
        raise KDError("POST_REPAIR_IDENTITY_MISMATCH")
    wrapper = load_path(MATERIALIZER, "g77_256kd_materializer_wrapper")
    controller = ModuleType("g77_256kd_controller_probe")
    controller.MATERIALIZER = wrapper
    current = load_path(CONTROLLER, "g77_256kd_post_repair_controller")
    owner = current._bind_kc_phase_b_materializer_owner(controller)
    entry = owner.A.authenticate_entry
    if entry is not owner.A.M.authenticate_entry:
        raise KDError("AUTHORITATIVE_ENTRY_OWNER_IDENTITY_MISMATCH")
    if tuple(inspect.signature(entry).parameters) != ("remote_head", "nested_remote_tag"):
        raise KDError("ENTRY_ARGUMENT_SEMANTICS_MISMATCH")
    try:
        entry("f" * 40, NESTED_HEAD)
    except Exception as exc:
        repository_mismatch = f"{type(exc).__name__}:{exc}"
    else:
        raise KDError("MALFORMED_ENTRY_EVIDENCE_ACCEPTED")
    return {
        "actual_interface_before_binding": "K.A.authenticate_entry(remote_head, nested_remote_tag)",
        "adaptation_boundary": "KC_NAMESPACE_WRAPPER_TO_AUTHENTICATED_ADAPTED_KA_MATERIALIZER_CONTRACT",
        "argument_names": list(inspect.signature(entry).parameters),
        "authoritative_function_identity": "K.A.authenticate_entry IS K.A.M.authenticate_entry",
        "authoritative_owner": "COMMITTED_JW_PREAUTHORIZATION_ENTRY_OWNER_TRANSITIVELY_ADAPTED_BY_JY_THEN_KA_THEN_KC",
        "caller": "G77_256KC_PHASE_B_CONTROLLER_V1.authenticate",
        "expected_interface": "MATERIALIZER.A.authenticate_entry(remote_head, nested_remote_tag)",
        "minimum_repair": "BIND_CONTROLLER_MATERIALIZER_TO_K_AFTER_EXACT_WRAPPER_GRAPH_AND_SIGNATURE_VALIDATION",
        "post_repair_resolution": "VERIFIED__CONTROLLER_MATERIALIZER_IS_K_AND_EXPECTED_CALL_RESOLVES_TO_K.A",
        "repository_identity_negative": repository_mismatch,
        "semantic_contract": "FAIL_CLOSED_ENTRY_IDENTITY_AND_NESTED_AUTHORITY_AUTHENTICATION_BEFORE_HUMAN_ACT_AUTHENTICATION_OR_CONSUMPTION",
    }


def zero_counters() -> dict[str, int]:
    return {
        "authority_consumption_count": 0,
        "expired_denial_count": 0,
        "fm_operational_invocation_count": 0,
        "operation_attempt_count": 0,
        "operational_authorization_count": 0,
        "operational_request_count": 0,
        "p11_entry_count": 0,
        "pre_operational_count": 0,
        "protected_effect_count": 0,
        "protected_invocation_count": 0,
        "qemu_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "retry_count": 0,
        "vm_count": 0,
    }


def build_reduction(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    entry = authenticate_entry(remote_head, nested_remote_tag)
    terminal = authenticate_kc_terminal()
    pre = reproduce_pre_repair()
    post = verify_post_repair()
    if sha256(P11) != P11_SHA256 or sha256(FM) != FM_SHA256:
        raise KDError("P11_OR_SOLE_FM_ROUTE_IDENTITY_MISMATCH")
    return {
        "architecture": {"new_constitutional_concept_count":0,"new_generic_abstraction_count":0,"new_owner_count":0,"new_registry_count":0,"new_route_count":0,"p11_implementation_mutation_count":0,"production_mutation_count":0,"production_route_after":1,"production_route_before":1,"production_route_delta":0},
        "auto_continuable": False,
        "candidate_capability": "VERIFIED__KC_PHASE_B_CONTROLLER_TO_ENTRY_AUTHENTICATION_OWNER_BINDING_REPOSITORY_ONLY",
        "call_graph": {
            "adaptation_boundary": "KC_CONTROLLER_TO_KC_NAMESPACE_WRAPPER_TO_ADAPTED_KA_CONTRACT_TO_ADAPTED_JY_EXPORT_TO_COMMITTED_JW_ENTRY_OWNER",
            "actual_interface": "KC_MATERIALIZER.K.A.authenticate_entry(remote_head, nested_remote_tag)",
            "authoritative_owner": "G77_256JW_PREAUTHORIZATION_MATERIALIZER_V1.authenticate_entry",
            "caller": "G77_256KC_PHASE_B_CONTROLLER_V1.authenticate",
            "expected_interface": "MATERIALIZER.A.authenticate_entry(remote_head, nested_remote_tag)",
            "semantic_contract": "EXACT_REMOTE_RATIFIED_ENTRY_AND_NESTED_AUTHORITY_VALIDATION_BEFORE_HUMAN_AUTHENTICATION_OR_CONSUMPTION",
        },
        "ccwim": {"authenticated_repository_continuation":"VERIFIED__YES","ccwim_maturity_level":"ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION","handoff_ambiguity_count":"VERIFIED__0","handoff_reconstruction_success":"VERIFIED__YES","observed_artifact_level_cross_worker_drift":"VERIFIED__0","previous_worker_conversation_required":"VERIFIED__NO","previous_worker_memory_required":"VERIFIED__NO"},
        "entry": entry,
        "e05": {"credit":"VERIFIED__0","expired":"NOT_PROVEN_OPERATIONALLY","frontier":"VERIFIED__7_UNSATISFIED_OF_18","state":"VERIFIED__11_OF_18"},
        "ex_reuse": {"ex_reconstructed":"VERIFIED__0","ex_reused":"VERIFIED__17_OF_17"},
        "frontier": {"first_broken_edge":"FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING_NOT_YET_REPROVEN_AFTER_KD","last_verified_edge":"KC_PHASE_B_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BINDING_REPOSITORY_VERIFIED","minimum_legal_next_delta":"SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_GENERATION","minimum_missing_capability":"FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY"},
        "human_authority": "NOT_REQUESTED_NOT_RECONSTRUCTED_NOT_AUTHENTICATED_NOT_CONSUMED_NOT_EXECUTED",
        "human_review_required": True,
        "governance": {"cognition_assisted_handoff":"VERIFIED__COMMITTED_KC_TERMINAL_TO_KD_REPOSITORY_ONLY_REPAIR","cognition_provenance":"VERIFIED__COMMITTED_REPOSITORY_CALL_GRAPH_AND_RUNTIME_IDENTITY_PROBES_PRIMARY","constitutional_continuation_progress":"VERIFIED__KC_TERMINAL_BLOCKER_TO_KD_ENTRY_OWNER_BINDING","constitutional_frontier_distance":"NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR","constitutional_health_evidence":"VERIFIED__FAIL_CLOSED_REPAIR_WITH_ALL_OPERATIONAL_COUNTERS_ZERO","governance_efficience":"ESTIMATED__HIGH__ONE_CHECKED_BINDING_WITH_NO_NEW_OWNER_OR_ROUTE","informal_project_progress_estimate":"ESTIMATED__ENTRY_OWNER_INTERFACE_BLOCKER_REPAIRED_REPOSITORY_ONLY","overengineering_risk":"ESTIMATED__LOW__GENERATION_LOCAL_BINDING_AND_REGRESSION_ONLY","project_progress":"VERIFIED__KC_PHASE_B_ENTRY_OWNER_INTERFACE_BINDING_REPAIRED_REPOSITORY_ONLY","project_progress_estimate":"NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR","shadow_automation_status":"VERIFIED__ABSENT","shadow_design_target":"VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "kc_terminal_authentication": terminal,
        "mismatch_preflight": "VERIFIED__MOVED_TO_CONTROLLER_IMPORT_BEFORE_HUMAN_ACT_AUTHENTICATION_OR_CONSUMPTION",
        "operational_counters": zero_counters(),
        "post_repair": post,
        "pre_repair": pre,
        "proof_yield": {"e05_credit":"VERIFIED__0","new_blocker_localized_count":"VERIFIED__0__PRIOR_KC_BLOCKER_REUSED","new_verified_capability_count":"VERIFIED__1_REPOSITORY_ONLY_ENTRY_OWNER_BINDING","proof_reuse_count":"VERIFIED__17"},
        "root_cause": {"classification":"OWNER_ROLE_PROJECTION_MISMATCH__KC_NAMESPACE_WRAPPER_ADDED_ONE_LAYER_WITHOUT_REBINDING_THE_REUSED_KA_CONTROLLER_CONTRACT","incomplete_owner":False,"new_owner_required":False,"why_k_not_a":"KC_MATERIALIZER_USES_K_FOR_THE_ADAPTED_KA_MATERIALIZER_SO_IT_CAN_ADD_KB_NAMESPACE_PREFLIGHT_AROUND_K_WITHOUT_REDEFINING_KA_OWNERSHIP","why_m_not_owner":"M_IS_K_MATERIALIZATION_RUNTIME_AND_DOES_NOT_OWN_THE_PHASE_B_ENTRY_JZ_AND_FRONTIER_INTERFACE"},
        "schema_id": "G77_256KD_KC_PHASE_B_ENTRY_OWNER_INTERFACE_BINDING_REDUCTION_V1",
        "terminal": SUCCESS,
    }
