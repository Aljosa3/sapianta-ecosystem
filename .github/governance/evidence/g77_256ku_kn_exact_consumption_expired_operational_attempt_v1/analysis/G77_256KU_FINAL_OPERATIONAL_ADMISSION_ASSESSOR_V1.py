#!/usr/bin/env python3
"""Reauthenticate KU and fail closed before consumption on admission drift.

This assessor calls only the existing FM pure admission validator.  It has no
authority-consumption, launcher, subprocess-operation, retry, or replay path.
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
KU = ROOT / ".github/governance/evidence/g77_256ku_kn_exact_consumption_expired_operational_attempt_v1"
OUTPUT = KU / "G77_256KU_SPCE_TERMINAL_FINAL_ADMISSION_FAIL_CLOSED_V1.json"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
KT = ROOT / ".github/governance/evidence/g77_256kt_kn_nonconsuming_handoff_binding_materialization_v1"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
CONTEXT = KN / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = KN / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION_PRESENTATION = KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt"
HANDOFF = KN / "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KN / "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CONSUMPTION = KN / "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KN / "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KN / "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
PHASE_B_CHECKPOINT = KN / "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
KT_REDUCTION = KT / "G77_256KT_SPCE_TERMINAL_PRECONSUMPTION_MATERIALIZATION_V1.json"
KT_REPORT = KT / "G77_256KT_G48_IMPLEMENTATION_REPORT_V1.md"
KT_MATERIALIZER = KT / "analysis/G77_256KT_NONCONSUMING_HANDOFF_BINDING_MATERIALIZER_V1.py"
KT_TESTS = KT / "tests/test_g77_256kt_nonconsuming_handoff_binding_materialization_v1.py"
KO_INSTRUCTION = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1/G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"

HEAD = "4ea192a4f896e7764ed3befaeb0e00ab599cfb0e"
TREE = "41a31ce4d4a8f9d390a07c98795a7ce407e9682c"
SUBJECT = "G77-256KT materialize KN preconsumption authority binding"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
CONTEXT_HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
CONTEXT_TREE = "70aa2a12af3d9806e0d6ddc73f7f751292413e52"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
HANDOFF_SHA256 = "f220a240d54c38ecba24fcc2ffd6c9c37b1cc11a69baac5f913964b0d5cff4ae"
HANDOFF_INNER_SHA256 = "e1e21562553bd9b93bbb144336e0baa0fd1fdfc554e62cd65b5e08c6cae5e7c9"
BINDING_SHA256 = "15b92bd8e07bea489c8128826a7757404489a2ecb1204c963f391a9a992e4135"
BINDING_INNER_SHA256 = "234858e580d12c15f31e4258dd6c3664836c8b4f355d66239294400db4f2fe72"
CONTEXT_SHA256 = "37f5c7d46b305b6e6e6b912dd136917c96ad4c783341aa62cd1dc4994e6f5b4b"
CONTEXT_FILE_SHA256 = "adafd6cdc2bef25119e098e11a69a79cdc893656bc9471f72e4e6a85ca5e7695"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
REQUEST_SHA256 = "9c5941b007e5939da928b7e1cc6cf0668a8e20b29f75bbe29964520645eb57d5"
REQUEST_FILE_SHA256 = "f980e8cd5ac48c97bbc61a0f891f103e8305f14847a59333b39912024609831d"
AUTH_PRESENTATION_SHA256 = "71cc222249ad75b2b420d749c2d4bd66cf0bd2d982f054102384ddb14993e2ac"
DECISION_PRESENTATION_SHA256 = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
CANONICAL_ARGV_SHA256 = "96480352c744c6feb9d743fafc7eae111a143ebde6b18cf67160e05ac1e93816"
TEMPORAL_BINDING_SHA256 = "cc46cded2aa3c294ad84c172619092889639fb74dda5f32ec68645508a2a1f56"
KT_REDUCTION_SHA256 = "20dc1d487d9b56d0ef28a159b70a8013b2c6daf0af3e0aab58b9ccdd76081f31"
KT_REPORT_SHA256 = "1269903ed36435f57bf7523b3a24ad207e9a027f7a4d1d6020bbcdf2983e661c"
KT_MATERIALIZER_SHA256 = "aef43d32e3ff6fa4590c15d4693e03509641a8f7c1ce5f94eb4888dbece980e2"
KT_TESTS_SHA256 = "58371d84fda86c7055052e8d377b8261ac726c6d5990706fc9f2429e4d5879b5"
FM_SHA256 = "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
FM_ADMISSION_ERROR = "operation context repository binding differs from observed state"
TERMINAL = "D__KU_FINAL_OPERATIONAL_ADMISSION_NOT_PROVEN__NO_AUTHORITY_CONSUMPTION__NO_OPERATION"


class KUAdmissionError(RuntimeError):
    """Stable fail-closed KU preconsumption error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise KUAdmissionError(f"DUPLICATE_JSON_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KUAdmissionError(f"NONCANONICAL_JSON:{path.name}")
    return value


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KUAdmissionError(f"SEAL_MISMATCH:{path.name}")
    return value


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def exact_human_bytes() -> bytes:
    text = KO_INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KUAdmissionError("KO_SOURCE_MARKERS_INVALID")
    return text.split(begin, 1)[1].split(end, 1)[0].encode("utf-8")


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0, "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0, "fm_operational_invocation_count": 0,
        "qemu_start_count": 0, "vm_start_count": 0, "operation_attempt_count": 0,
        "operation_request_count": 0, "expired_denial_count": 0, "p11_entry_count": 0,
        "protected_invocation_count": 0, "protected_effect_count": 0,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }


def authenticate_entry() -> None:
    if (
        git("branch", "--show-current") != BRANCH or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise KUAdmissionError("KT_ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KUAdmissionError("STABLE_ANCESTRY_MISMATCH")
    source_name = SOURCE.relative_to(ROOT).as_posix()
    ku_prefix = KU.relative_to(ROOT).as_posix() + "/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??" or (line[3:] != source_name and not line[3:].startswith(ku_prefix)):
            raise KUAdmissionError(f"KU_BOUNDED_WORKTREE_SCOPE_VIOLATION:{line}")
    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("branch", "--show-current", cwd=nested) or git("status", "--short", cwd=nested)
        or git("describe", "--tags", "--exact-match", "HEAD", cwd=nested) != "sapianta-system-nested-authority-3183bab-v1"
    ):
        raise KUAdmissionError("NESTED_AUTHORITY_MISMATCH")


def load_fm() -> Any:
    if sha256_path(FM_PATH) != FM_SHA256:
        raise KUAdmissionError("FM_OWNER_IMMUTABILITY_FAILURE")
    specification = importlib.util.spec_from_file_location("g77_256ku_fm_owner", FM_PATH)
    if specification is None or specification.loader is None:
        raise KUAdmissionError("FM_OWNER_IMPORT_FAILURE")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_inputs() -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, Any]]:
    authenticate_entry()
    source = SOURCE.read_bytes()
    if (
        len(source) != 1213 or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source.startswith(b"\xef\xbb\xbf") or not source.endswith(b"\n")
        or source != exact_human_bytes() or git("ls-files", "--", SOURCE.relative_to(ROOT).as_posix())
    ):
        raise KUAdmissionError("HUMAN_SOURCE_IMMUTABILITY_FAILURE")
    source.decode("utf-8")
    expected_files = {
        KT_REDUCTION: KT_REDUCTION_SHA256, KT_REPORT: KT_REPORT_SHA256,
        KT_MATERIALIZER: KT_MATERIALIZER_SHA256, KT_TESTS: KT_TESTS_SHA256,
        CONTEXT: CONTEXT_FILE_SHA256, CANDIDATE: CANDIDATE_SHA256,
        REQUEST: REQUEST_FILE_SHA256, AUTH_PRESENTATION: AUTH_PRESENTATION_SHA256,
        DECISION_PRESENTATION: DECISION_PRESENTATION_SHA256,
        HANDOFF: HANDOFF_SHA256, BINDING: BINDING_SHA256,
    }
    if any(sha256_path(path) != expected for path, expected in expected_files.items()):
        raise KUAdmissionError("COMMITTED_KT_OR_KN_INPUT_MISMATCH")
    kt = load_envelope(KT_REDUCTION, "reduction")
    if (
        kt.get("terminal") != "A__KT_EXACT_NONCONSUMING_KN_CANONICAL_HANDOFF_AND_PRECONSUMPTION_BINDING_MATERIALIZED__AUTHORITY_UNCONSUMED__NO_PHASE_B__NO_OPERATION"
        or kt.get("human_authority", {}).get("human_authority_consumption_status") != "VERIFIED__UNCONSUMED"
        or kt.get("nonconsuming_proof", {}).get("handoff_preparation_consumes_authority") != "VERIFIED__NO"
        or kt.get("nonconsuming_proof", {}).get("binding_materialization_consumes_authority") != "VERIFIED__NO"
        or any(kt.get("operational_counters", {}).values()) or kt.get("phase_b_started") is not False
    ):
        raise KUAdmissionError("KT_TERMINAL_STATE_MISMATCH")
    fm = load_fm()
    handoff = fm.parse_authority_handoff_bytes(HANDOFF.read_bytes())
    if len(HANDOFF.read_bytes()) != 1715 or handoff.get("authorization_sha256") != HANDOFF_INNER_SHA256:
        raise KUAdmissionError("CANONICAL_HANDOFF_MISMATCH")
    binding_envelope = load_canonical(BINDING)
    if binding_envelope.get("invocation_binding_sha256") != BINDING_INNER_SHA256:
        raise KUAdmissionError("PRECONSUMPTION_BINDING_SEAL_MISMATCH")
    binding = fm.validate_preconsumption_invocation_binding(
        repository_root=ROOT, operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE, execution_authority=HANDOFF,
        envelope=binding_envelope,
    )
    context = load_canonical(CONTEXT)
    authorization = handoff["authorization"]
    if (
        context.get("generation_identity") != GENERATION or context.get("operation_identity") != OPERATION
        or context.get("context_sha256") != CONTEXT_SHA256
        or context.get("canonical_argv_sha256") != CANONICAL_ARGV_SHA256
        or hashlib.sha256(canonical_bytes(context["preclaim_temporal_binding"])).hexdigest() != TEMPORAL_BINDING_SHA256
        or context.get("repository_head") != CONTEXT_HEAD or context.get("repository_tree") != CONTEXT_TREE
        or authorization.get("authorized_repository_head") != CONTEXT_HEAD
        or authorization.get("authorized_repository_tree") != CONTEXT_TREE
        or authorization.get("authorization_source_sha256") != SOURCE_SHA256
        or authorization.get("authorized_generation_identity") != GENERATION
        or authorization.get("authorized_operation_identity") != OPERATION
        or authorization.get("authorized_vector") != "EXPIRED"
        or authorization.get("expired_operational_attempt_limit") != 1
        or authorization.get("retry_limit") != 0 or authorization.get("repair_limit") != 0
        or authorization.get("replay_limit") != 0 or authorization.get("authorization_reusable") is not False
        or binding.get("authority_consumption_count") != 0
        or binding.get("fm_operational_invocation_count") != 0
        or binding.get("process_started") is not False
    ):
        raise KUAdmissionError("KN_BINDING_OR_ONE_SHOT_LIMIT_MISMATCH")
    return fm, context, handoff, binding


def authenticate_collision_barrier(context: dict[str, Any]) -> None:
    forbidden = [CONSUMPTION, INVOCATION, RESULT, PHASE_B_CHECKPOINT]
    forbidden.extend((KN / relative) for relative in context.get("guest_output_relative_paths", []))
    forbidden.extend([
        Path(context["pre_receipt_path"]), Path(context["post_receipt_path"]),
        KN / "operation_state/receipts/G77_256KN_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
        KN / "operation_state/receipts/G77_256KN_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
    ])
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise KUAdmissionError("PRECONSUMPTION_NAMESPACE_COLLISION")


def reproduce_final_admission_failure(fm: Any, context: dict[str, Any], handoff: dict[str, Any]) -> str:
    try:
        fm.validate_execution_admission(
            context=context, authority=handoff,
            authority_file_sha256=HANDOFF_SHA256, supplied_authority_sha256=HANDOFF_SHA256,
            observed_head=HEAD, observed_tree=TREE, anchor_is_ancestor=True,
            repository_clean=True, observed_asset_sha256={}, argv=context["canonical_argv"],
            canonical_argv_sha256=CANONICAL_ARGV_SHA256, receipt_namespace_consumed=False,
            candidate_source_path=CANDIDATE.relative_to(ROOT),
        )
    except RuntimeError as error:
        if str(error) != FM_ADMISSION_ERROR:
            raise KUAdmissionError(f"UNEXPECTED_FM_ADMISSION_FAILURE:{error}") from error
        return str(error)
    raise KUAdmissionError("FM_FINAL_ADMISSION_UNEXPECTEDLY_PASSED")


def build_reduction() -> dict[str, Any]:
    fm, context, handoff, _ = authenticate_inputs()
    authenticate_collision_barrier(context)
    admission_error = reproduce_final_admission_failure(fm, context, handoff)
    return {
        "schema_id": "G77_256KU_SPCE_TERMINAL_FINAL_ADMISSION_FAIL_CLOSED_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A__READ_ONLY_FINAL_OPERATIONAL_ADMISSION__STOP_BEFORE_CONSUMPTION",
        "entry": {"branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT, "origin": ORIGIN, "remote_head": HEAD, "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE", "stable_ancestry_anchor": ANCHOR, "index_empty": True, "tracked_diff_empty": True},
        "nested_authority": {"origin": "git@github.com:Aljosa3/sapianta-core.git", "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1", "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66", "tree": "7c32ec05efc2be43297849bc38ec8766514a523d", "clean": True, "detached": True, "pinned": True, "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE"},
        "human_source": {"path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": 1213, "lf_count": 14, "utf8_validity": "VERIFIED", "bom_status": "VERIFIED__ABSENT", "final_lf_status": "VERIFIED__PRESENT", "sha256": SOURCE_SHA256, "exact_bytes_status": "VERIFIED__EXACT_KO_BYTE_EQUALITY", "modified": False},
        "materialized_authority": {"handoff_path": HANDOFF.relative_to(ROOT).as_posix(), "handoff_byte_count": 1715, "handoff_sha256": HANDOFF_SHA256, "authorization_inner_sha256": HANDOFF_INNER_SHA256, "binding_path": BINDING.relative_to(ROOT).as_posix(), "binding_file_sha256": BINDING_SHA256, "binding_inner_sha256": BINDING_INNER_SHA256, "human_authority_authentication": "VERIFIED__EXACT_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED", "human_authority_handoff_materialized": "VERIFIED__EXACT_NONCONSUMING_CANONICAL_HANDOFF", "human_authority_binding": "VERIFIED__EXACT_KN_PRECONSUMPTION_BINDING", "authority_state_before": "VERIFIED__GRANTED_UNCONSUMED", "authority_consumption_transition": "NOT_APPLICABLE__FINAL_ADMISSION_FAILED_BEFORE_TRANSITION", "authority_state_after": "VERIFIED__GRANTED_UNCONSUMED"},
        "failure_novelty_and_convergence_check": {"failure_class": "PROOF_GAP", "novelty": "VERIFIED__CURRENT_OPERATIONAL_ADMISSION_EDGE_NOT_SATISFIED_BY_OLDER_IMMUTABLE_KN_REPOSITORY_BINDING", "affected_invariant": "CONTEXT_AND_HUMAN_AUTHORITY_REPOSITORY_HEAD_TREE_MUST_EXACTLY_EQUAL_OBSERVED_OPERATIONAL_HEAD_TREE_BEFORE_CONSUMPTION", "previous_closest_edge": "KT_EXACT_PERSISTED_HANDOFF_AND_PRECONSUMPTION_BINDING_AT_KN_CONTEXT_COORDINATES", "semantic_difference": "VERIFIED__KT_PROVES_UNCONSUMED_BINDING_TO_1141F9F__KU_REQUIRES_OPERATIONAL_ADMISSION_AT_4EA192A", "production_behavior_impact": "VERIFIED__NONE__FM_FAILS_CLOSED_BEFORE_CONSUMPTION", "new_capability_required": "NOT_PROVEN__NO_NEW_PRODUCTION_CAPABILITY_MAY_BE_CREATED_IN_KU", "new_proof_required": "VERIFIED__EXACT_CURRENT_HEAD_TREE_OPERATIONAL_BINDING_COMPATIBLE_WITH_HUMAN_AUTHORITY", "convergence_signal": "VERIFIED__FIRST_BROKEN_EDGE_LOCALIZED_BY_EXISTING_FM_OWNER_WITHOUT_ANOTHER_OPERATIONAL_ATTEMPT", "repetition_pressure": "VERIFIED__HIGH__KN_THROUGH_KU_HAS_NO_E05_MOVEMENT", "verification_amplification_risk": "ESTIMATED__HIGH_IF_MORE_PROOF_ONLY_LAYERS_REPEAT_WITHOUT_LEGAL_CURRENT_HEAD_BINDING", "classification_evidence": f"VERIFIED__FM_VALIDATE_EXECUTION_ADMISSION__CONTEXT_HEAD_{CONTEXT_HEAD}__OBSERVED_HEAD_{HEAD}__ERROR_{admission_error.replace(' ', '_').upper()}", "classification_confidence": "VERIFIED__HIGH", "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__FM_EXACT_REPOSITORY_BINDING_FORCES_STOP_BEFORE_CONSUMPTION"},
        "cross_vector_reuse_assessment": {"cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE", "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN", "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION", "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"], "vector_specific_residue": "EXACT_CURRENT_REPOSITORY_BINDING__PER_GENERATION_HUMAN_AUTHORITY__CONSUMPTION__OPERATION__E05_ACCEPTANCE", "reuse_preconditions": "FRESH_NAMESPACE__EXACT_CURRENT_BINDINGS__STRICT_RELOAD__NO_AUTHORITY_OR_E05_TRANSFER", "revalidation_required": "VERIFIED__PER_GENERATION_VECTOR_HUMAN_ACT_BINDING_CONSUMPTION_AND_OPERATION", "expected_future_proof_reduction": "ESTIMATED__COMMON_MECHANISM_REUSE_ONLY__NO_VECTOR_OPERATIONAL_PROOF_OR_CREDIT_TRANSFER"},
        "phase_a": {"phase_a_reauthentication": "VERIFIED__EXACT_KT_KN_HUMAN_SOURCE_HANDOFF_BINDING_AND_ZERO_COUNTER_STATE", "human_intent_binding": "VERIFIED__EXACT_EXISTING_KN_HUMAN_ACT_REMAINS_BOUND_TO_THE_IMMUTABLE_KN_OBJECT", "operational_entry_binding": f"NOT_PROVEN__CONTEXT_AND_AUTHORITY_HEAD_{CONTEXT_HEAD}_DIFFER_FROM_CURRENT_HEAD_{HEAD}", "final_admission_status": f"NOT_PROVEN__FM_{admission_error.replace(' ', '_').upper()}"},
        "preconsumption_audit": {"preconsumption_collision_status": "VERIFIED__NO_CONSUMPTION_INVOCATION_RESULT_RECEIPT_OR_GUEST_OUTPUT_COLLISION", "preconsumption_replay_status": "VERIFIED__ZERO", "preconsumption_one_shot_status": "VERIFIED__UNCONSUMED__ONE_ATTEMPT_MAXIMUM__ZERO_RETRY_REPAIR_REPLAY", "preconsumption_namespace_status": "VERIFIED__CONSUMPTION_AND_OPERATION_NAMESPACES_FRESH"},
        "operation": {"exact_operation_attempted": "NOT_APPLICABLE__FINAL_ADMISSION_FAILED_BEFORE_CONSUMPTION", "actual_transition_order": ["KT_UNCONSUMED_STATE_REAUTHENTICATED", "KU_CURRENT_HEAD_OBSERVED", "FM_FINAL_ADMISSION_REJECTED_REPOSITORY_BINDING_DRIFT", "STOP_BEFORE_CONSUMPTION"], "expired_acceptance_evaluation": "NOT_PROVEN__NO_OPERATIONAL_ATTEMPT_OR_EXPIRED_OBSERVATION"},
        "operational_counters": zero_counters(), "phase_b_started": False,
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "frontier": {"last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD", "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR", "last_verified_edge": "KU_REAUTHENTICATED_EXACT_KT_UNCONSUMED_STATE_AND_LOCALIZED_CURRENT_HEAD_ADMISSION_FAILURE", "first_broken_edge": "EXACT_CURRENT_HEAD_TREE_OPERATIONAL_ENTRY_BINDING", "current_real_blocker": f"VERIFIED__IMMUTABLE_KN_CONTEXT_AND_AUTHORITY_BIND_{CONTEXT_HEAD}_BUT_CURRENT_OPERATIONAL_HEAD_IS_{HEAD}", "minimum_missing_capability": "NOT_PROVEN__LEGAL_CURRENT_HEAD_TREE_OPERATIONAL_BINDING_WITHOUT_REWRITING_IMMUTABLE_KN_OR_KT_EVIDENCE", "minimum_legal_next_delta": "SEPARATE_HUMAN_REVIEW__AUTHENTICATE_EXISTING_POST_COMMIT_BINDING_OWNER_AND_AUTHORITY_IMPACT__DO_NOT_CONSUM_OR_REUSE_AUTHORITY_UNTIL_EXACT_FINAL_ADMISSION_PASSES"},
        "governance": {"project_state": "VERIFIED__KU_STOPPED_AT_FINAL_ADMISSION_BEFORE_CONSUMPTION", "project_progress": "VERIFIED__CURRENT_REAL_BLOCKER_LOCALIZED_BY_EXISTING_FM_OWNER", "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "informal_project_progress_estimate": "ESTIMATED__CURRENT_HEAD_OPERATIONAL_BINDING_AND_THEN_ONE_OPERATIONAL_OBSERVATION_REMAIN", "constitutional_health_evidence": "VERIFIED__EXACT_REPOSITORY_BINDING_FAIL_CLOSED__AUTHORITY_UNCONSUMED__ZERO_OPERATION", "shadow_automation_status": "NOT_APPLICABLE__NO_AUTOMATIC_CONTINUATION", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "governance_efficiency": "ESTIMATED__HIGH__PURE_OWNER_VALIDATION_PREVENTED_ILLEGAL_CONSUMPTION", "overengineering_risk": "ESTIMATED__HIGH_IF_ANOTHER_PROOF_LAYER_IS_CREATED_WITHOUT_RESOLVING_CURRENT_HEAD_BINDING", "cognition_provenance": "VERIFIED__COMMITTED_KT_KN_FM_AND_DIRECT_PURE_ADMISSION_RESULT", "cognition_assisted_handoff": "VERIFIED__PROMPT_SCOPE_PLUS_AUTHENTICATED_REPOSITORY_STATE__NO_MEMORY_AUTHORITY", "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATIONAL_ATTEMPT_NOT_ADMITTED", "shadow_design_target": "VERIFIED__ONE_CONSUMPTION_THEN_ONE_FM_ER_P11_ATTEMPT__NOT_ENTERED", "constitutional_continuation_progress": "VERIFIED__FIRST_OPERATIONAL_ADMISSION_BLOCKER_EXACTLY_LOCALIZED"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0", "new_operational_capability_count": "VERIFIED__0", "new_blocker_localized_count": "VERIFIED__1__CURRENT_HEAD_OPERATIONAL_BINDING", "new_blocker_closed_count": "VERIFIED__0", "new_false_or_superseded_blocker_removed_count": "VERIFIED__0", "new_classification_result_count": "VERIFIED__1__PROOF_GAP", "new_operational_observation_count": "VERIFIED__0", "new_e05_credit_count": "VERIFIED__0", "ex_proof_reuse_count": "VERIFIED__17"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_ambiguity_count": "VERIFIED__0", "authority_state_ambiguity_count": "VERIFIED__0", "operational_attempt_ambiguity_count": "VERIFIED__0"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "authority_reusable": "NOT_APPLICABLE__AUTHORITY_REMAINS_UNCONSUMED_BUT_CURRENTLY_NOT_ADMISSIBLE",
        "second_operation_legal": "NOT_APPLICABLE__NO_FIRST_OPERATION_OCCURRED",
        "auto_continuable": False, "human_review_required": True,
    }


def envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {"schema_id": "G77_256KU_SPCE_TERMINAL_FINAL_ADMISSION_FAIL_CLOSED_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest()}


def materialize() -> None:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KUAdmissionError("KU_REDUCTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def verify() -> None:
    if load_envelope(OUTPUT, "reduction") != build_reduction():
        raise KUAdmissionError("KU_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    arguments = parser.parse_args()
    materialize() if arguments.mode == "materialize" else verify()


if __name__ == "__main__":
    main()
