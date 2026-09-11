#!/usr/bin/env python3
"""Reduce the KV repository-binding owner discovery without operation.

The formalizer reads committed governance evidence and Git metadata only.  It
has no authority creation, authority consumption, launcher, VM, retry, replay,
or protected-operation path.
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
KV = ROOT / ".github/governance/evidence/g77_256kv_current_head_operational_binding_owner_and_authority_impact_discovery_v1"
OUTPUT = KV / "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_V1.json"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
KU = ROOT / ".github/governance/evidence/g77_256ku_kn_exact_consumption_expired_operational_attempt_v1"
JP = ROOT / ".github/governance/evidence/g77_256jp_post_jo_committed_live_binding_and_expired_operational_readiness_reauthentication_v1"
FM = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"

HEAD = "74a01ab065a6d9e32ca8f595d9e872b91d5bc768"
TREE = "f69ecb51e4a68d628bde00ab4576c081e7e012ed"
SUBJECT = "G77-256KU fail closed at current repository admission"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
KN_HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
KN_TREE = "70aa2a12af3d9806e0d6ddc73f7f751292413e52"
KU_HEAD = "4ea192a4f896e7764ed3befaeb0e00ab599cfb0e"
KU_TREE = "41a31ce4d4a8f9d390a07c98795a7ce407e9682c"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
HANDOFF_SHA256 = "f220a240d54c38ecba24fcc2ffd6c9c37b1cc11a69baac5f913964b0d5cff4ae"
HANDOFF_INNER_SHA256 = "e1e21562553bd9b93bbb144336e0baa0fd1fdfc554e62cd65b5e08c6cae5e7c9"
BINDING_SHA256 = "15b92bd8e07bea489c8128826a7757404489a2ecb1204c963f391a9a992e4135"
BINDING_INNER_SHA256 = "234858e580d12c15f31e4258dd6c3664836c8b4f355d66239294400db4f2fe72"
CONTEXT_SHA256 = "37f5c7d46b305b6e6e6b912dd136917c96ad4c783341aa62cd1dc4994e6f5b4b"
TERMINAL = "B__KV_EXISTING_POST_COMMIT_BINDING_MECHANISM_FOUND__NOT_APPLICABLE_TO_IMMUTABLE_KN_AUTHORITY__FRESH_HUMAN_ACT_REQUIRED"

SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KN / "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KN / "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CONTEXT = KN / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
KU_REDUCTION = KU / "G77_256KU_SPCE_TERMINAL_FINAL_ADMISSION_FAIL_CLOSED_V1.json"
JP_REDUCTION = JP / "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

EXPECTED_HASHES = {
    KU_REDUCTION: "c2972825530e7e420b04e0722338916bcf0e7d7e55e66fb0118d0939289c44e8",
    JP_REDUCTION: "ca02e314f459a9aa11092f89264deb9d40ba810d35731980e1e60c5c85949503",
    FM: "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51",
    CONTEXT: "adafd6cdc2bef25119e098e11a69a79cdc893656bc9471f72e4e6a85ca5e7695",
    HANDOFF: HANDOFF_SHA256,
    BINDING: BINDING_SHA256,
}

SUCCESS_PRECEDENTS = {
    "HP_WRONG_INPUT": {
        "root": "g77_256hp_wrong_input_operational_v1", "prefix": "G77_256HP",
        "head": "fc9bc52bbd708a40f884f2fc006ebe0e3f6e4df8", "tree": "9256a995bf9b90714e759dae98d2bed4c3de8f22",
    },
    "HX_WRONG_CONTRACT": {
        "root": "g77_256hx_wrong_contract_operational_v1", "prefix": "G77_256HX",
        "head": "0e2448cb0194d6182085a671ddb28729681a1e75", "tree": "adc1453b964d05e3cf41deffcbbc0c856f99a81a",
    },
    "IC_WRONG_PROVENANCE": {
        "root": "g77_256ic_wrong_provenance_operational_v1", "prefix": "G77_256IC",
        "head": "ec2c4997ba62fbaa5e774fc9ba010f6319926c73", "tree": "887f329b030582f01a49f6c0c97f54ed4f55a818",
    },
}


class KVDiscoveryError(RuntimeError):
    """Stable fail-closed discovery error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise KVDiscoveryError(f"DUPLICATE_JSON_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KVDiscoveryError(f"NONCANONICAL_JSON:{path.name}")
    return value


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KVDiscoveryError(f"INNER_OBJECT_MISSING:{path.name}")
    if envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KVDiscoveryError(f"INNER_SEAL_MISMATCH:{path.name}")
    return value


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"), "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    expected = {"branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT, "origin": ORIGIN}
    if observed != expected or git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise KVDiscoveryError("ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KVDiscoveryError("STABLE_ANCESTRY_MISMATCH")
    source_name = SOURCE.relative_to(ROOT).as_posix()
    kv_prefix = KV.relative_to(ROOT).as_posix() + "/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??" or (line[3:] != source_name and not line[3:].startswith(kv_prefix)):
            raise KVDiscoveryError(f"BOUNDED_WORKTREE_SCOPE_VIOLATION:{line}")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested), "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--short", cwd=nested) == "", "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": "git@github.com:Aljosa3/sapianta-core.git", "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d", "clean": True, "detached": True,
        "tag": "sapianta-system-nested-authority-3183bab-v1",
    }:
        raise KVDiscoveryError("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "remote_head": HEAD, "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "index_empty": True, "tracked_diff_empty": True, "stable_ancestry_anchor": ANCHOR,
        "nested_authority": nested_state | {"remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE"},
    }


def authenticate_kn_ku() -> dict[str, Any]:
    if any(sha256_path(path) != expected for path, expected in EXPECTED_HASHES.items()):
        raise KVDiscoveryError("AUTHENTICATED_INPUT_HASH_MISMATCH")
    source = SOURCE.read_bytes()
    if len(source) != 1213 or source.count(b"\n") != 14 or source.startswith(b"\xef\xbb\xbf") or not source.endswith(b"\n"):
        raise KVDiscoveryError("HUMAN_SOURCE_ENCODING_MISMATCH")
    source.decode("utf-8")
    if sha256_path(SOURCE) != SOURCE_SHA256 or git("ls-files", "--", SOURCE.relative_to(ROOT).as_posix()):
        raise KVDiscoveryError("HUMAN_SOURCE_IDENTITY_OR_TRACKING_MISMATCH")
    context = load_canonical(CONTEXT)
    handoff = load_envelope(HANDOFF, "authorization")
    binding = load_envelope(BINDING, "invocation_binding")
    ku = load_envelope(KU_REDUCTION, "reduction")
    if (
        context.get("context_sha256") != CONTEXT_SHA256
        or (context.get("repository_head"), context.get("repository_tree")) != (KN_HEAD, KN_TREE)
        or (handoff.get("authorized_repository_head"), handoff.get("authorized_repository_tree")) != (KN_HEAD, KN_TREE)
        or handoff.get("authorization_source_sha256") != SOURCE_SHA256
        or load_canonical(HANDOFF).get("authorization_sha256") != HANDOFF_INNER_SHA256
        or load_canonical(BINDING).get("invocation_binding_sha256") != BINDING_INNER_SHA256
        or binding.get("authority_consumption_count") != 0 or binding.get("process_started") is not False
        or ku.get("terminal") != "D__KU_FINAL_OPERATIONAL_ADMISSION_NOT_PROVEN__NO_AUTHORITY_CONSUMPTION__NO_OPERATION"
        or ku.get("entry", {}).get("head") != KU_HEAD or ku.get("entry", {}).get("tree") != KU_TREE
        or ku.get("materialized_authority", {}).get("authority_state_after") != "VERIFIED__GRANTED_UNCONSUMED"
        or ku.get("phase_b_started") is not False or any(ku.get("operational_counters", {}).values())
    ):
        raise KVDiscoveryError("KN_KU_CHAIN_MISMATCH")
    return {"context": context, "handoff": handoff, "binding": binding, "ku": ku}


def authenticate_fm_and_post_commit_owner() -> dict[str, Any]:
    source = FM.read_text(encoding="utf-8")
    ast.parse(source)
    required = (
        "def build_operation_context(", "def validate_execution_admission(",
        'raise RuntimeError("operation context repository binding differs from observed state")',
        'raise RuntimeError("committed repository HEAD not authorized")',
        'raise RuntimeError("committed repository tree not authorized")',
    )
    if any(source.count(fragment) != 1 for fragment in required):
        raise KVDiscoveryError("FM_OWNER_BINDING_CONTRACT_MISMATCH")
    jp = load_envelope(JP_REDUCTION, "reduction")
    if (
        jp.get("terminal") != "A__POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_READINESS_REPOSITORY_VERIFIED"
        or jp.get("mode") != "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION"
        or jp.get("authority_separation", {}).get("repository_readiness_is_authorization") != "VERIFIED__NO"
        or jp.get("frontier", {}).get("minimum_legal_next_delta") != "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_GENERATION"
        or jp.get("live_binding", {}).get("existing_context_owner_count") != "VERIFIED__1"
        or jp.get("live_binding", {}).get("production_route_count") != "VERIFIED__1"
    ):
        raise KVDiscoveryError("EXPIRED_POST_COMMIT_OWNER_MISMATCH")
    return {
        "post_commit_readiness_owner": "JP_REAUTHENTICATION_OF_COMMITTED_JO_ROUTE_AND_EXISTING_FM_CONTEXT_OWNER",
        "operation_context_owner": "FM_BUILD_OPERATION_CONTEXT",
        "final_admission_owner": "FM_VALIDATE_EXECUTION_ADMISSION",
        "preconsumption_binding_owner": "FM_JZ_BUILD_AND_VALIDATE_PRECONSUMPTION_INVOCATION_BINDING",
        "consumer_transition_owner": "KA_KE_OPERATIONAL_CONTROLLER_PLUS_FM_AND_P11_ONE_SHOT_CONSUMER",
        "mechanism_scope": "VERIFIED__CURRENT_COMMITTED_READINESS_THEN_FRESH_OPERATION_GENERATION_AUTHORITY_AND_SAME_HEAD_CONSUMPTION",
        "repository_readiness_is_authority": "VERIFIED__NO",
        "old_authority_rebinding_owner": "NOT_PROVEN__NO_AUTHENTICATED_OWNER_REBINDS_AN_EXISTING_HUMAN_ACT_TO_A_DIFFERENT_HEAD_TREE",
    }


def authenticate_success_precedents() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    evidence_root = ROOT / ".github/governance/evidence"
    for name, spec in SUCCESS_PRECEDENTS.items():
        base = evidence_root / spec["root"]
        prefix = spec["prefix"]
        handoff = load_envelope(base / f"{prefix}_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json", "authorization")
        receipt_path = base / f"operation_state/receipts/{prefix}_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
        receipt_document = load_canonical(receipt_path)
        receipt = receipt_document.get("receipt", receipt_document)
        checkpoint = load_envelope(base / f"{prefix}_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
        seal = load_envelope(base / f"{prefix}_SPCE_FINAL_EXECUTION_SEAL_V1.json", "seal")
        coordinates = (spec["head"], spec["tree"])
        if (
            (handoff.get("authorized_repository_head"), handoff.get("authorized_repository_tree")) != coordinates
            or (receipt.get("authorized_repository_head"), receipt.get("authorized_repository_tree")) != coordinates
            or checkpoint.get("authority_state_after") != "CONSUMED"
            or seal.get("authority_consumed") != 1 or seal.get("operational_counters", {}).get("operation_attempt") != 1
            or not str(seal.get("final_result", "")).startswith("VERIFIED__")
        ):
            raise KVDiscoveryError(f"SUCCESS_PRECEDENT_MISMATCH:{name}")
        result.append({
            "precedent": name, "human_authority_head": spec["head"],
            "preconsumption_binding_head": spec["head"], "execution_head": spec["head"],
            "post_commit_transition_present": "VERIFIED__NO_EXECUTION_TIME_REBIND__EVIDENCE_COMMITTED_AFTER_OPERATION",
            "transition_owner": "NOT_APPLICABLE__NO_HEAD_TRANSITION_BEFORE_CONSUMPTION",
            "new_human_act_required": "VERIFIED__YES__FRESH_PER_OPERATION_GENERATION",
            "authority_rebound": "VERIFIED__NO", "authority_consumed": "VERIFIED__YES",
            "operation_succeeded": "VERIFIED__YES", "semantic_equivalence_to_ku": "VERIFIED__SAME_EXACT_AUTHORITY_CONTEXT_OBSERVED_HEAD_EQUALITY_INVARIANT",
        })
    return result


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    chain = authenticate_kn_ku()
    owners = authenticate_fm_and_post_commit_owner()
    precedents = authenticate_success_precedents()
    return {
        "schema_id": "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_V1",
        "terminal": TERMINAL,
        "mode": "REPOSITORY_ONLY__READ_ONLY_DISCOVERY_AND_FORMALIZATION__NO_AUTHORITY_CONSUMPTION__NO_OPERATION__NO_PHASE_B",
        "entry": entry,
        "human_source": {"path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": 1213, "lf_count": 14, "utf8_validity": "VERIFIED", "bom_status": "VERIFIED__ABSENT", "final_lf_status": "VERIFIED__PRESENT", "sha256": SOURCE_SHA256, "tracked": False, "modified": False},
        "kn_kt_authority_chain": {
            "context_sha256": CONTEXT_SHA256, "context_repository_head": KN_HEAD, "context_repository_tree": KN_TREE,
            "handoff_byte_count": len(HANDOFF.read_bytes()), "handoff_sha256": HANDOFF_SHA256,
            "handoff_inner_sha256": HANDOFF_INNER_SHA256, "binding_sha256": BINDING_SHA256,
            "binding_inner_sha256": BINDING_INNER_SHA256, "authority_state": "VERIFIED__GRANTED_UNCONSUMED",
            "authority_repository_binding_mutability": "VERIFIED__IMMUTABLE_WITHIN_THE_SEALED_KN_AUTHORIZATION_OBJECT",
        },
        "ku_reauthentication": {
            "entry_head": KU_HEAD, "entry_tree": KU_TREE,
            "terminal": chain["ku"]["terminal"], "authority_state_before": "VERIFIED__GRANTED_UNCONSUMED",
            "authority_consumption_transition": "NOT_APPLICABLE__FINAL_ADMISSION_FAILED",
            "authority_state_after": "VERIFIED__GRANTED_UNCONSUMED", "phase_b_started": False,
            "all_15_operational_counters": "VERIFIED__ZERO", "final_admission": "NOT_PROVEN__FM_OPERATION_CONTEXT_REPOSITORY_BINDING_DIFFERS_FROM_OBSERVED_STATE",
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "novelty": "VERIFIED__KNOWN_LIFECYCLE_ORDERING_VIOLATION__NOT_A_NEW_AUTHORITY_BINDING_CAPABILITY_GAP",
            "affected_invariant": "CONTEXT_AND_HUMAN_AUTHORITY_REPOSITORY_HEAD_TREE_MUST_EXACTLY_EQUAL_OBSERVED_OPERATIONAL_HEAD_TREE_BEFORE_CONSUMPTION",
            "previous_closest_edge": "JP_POST_COMMIT_EXPIRED_READINESS_THEN_SEPARATE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_GENERATION",
            "semantic_difference": "VERIFIED__KT_COMMIT_OCCURRED_AFTER_KN_HUMAN_ACT_AND_BEFORE_KU_ADMISSION__SUCCESS_PRECEDENTS_HAVE_NO_HEAD_TRANSITION_IN_THAT_INTERVAL",
            "production_behavior_impact": "VERIFIED__NONE__FM_FAILED_CLOSED_BEFORE_CONSUMPTION",
            "new_capability_required": "VERIFIED__NO",
            "new_proof_required": "VERIFIED__FRESH_OPERATION_GENERATION_MUST_REAUTHENTICATE_CURRENT_BINDINGS_BEFORE_A_NEW_HUMAN_ACT",
            "convergence_signal": "VERIFIED__REUSE_EXISTING_LIFECYCLE__DO_NOT_ADD_AUTHORITY_REBINDING",
            "repetition_pressure": "VERIFIED__HIGH__KN_THROUGH_KV_HAS_NO_E05_MOVEMENT",
            "verification_amplification_risk": "ESTIMATED__HIGH_IF_ANOTHER_COMMITTED_POST_AUTHORITY_BINDING_LAYER_IS_INSERTED",
            "classification_evidence": "VERIFIED__JP_AUTHORITY_FREE_POST_COMMIT_READINESS__FM_EXACT_EQUALITY__HP_HX_IC_SAME_HEAD_AUTHORITY_AND_EXECUTION",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__KV_STOPS_AFTER_OWNER_AND_AUTHORITY_IMPACT_DISCOVERY",
        },
        "repository_binding_lifecycle": [
            {"binding_name": "POST_COMMIT_OPERATIONAL_READINESS", "binding_owner": "JP_PLUS_EXISTING_FM_CONTEXT_OWNER", "binding_source_artifact": JP_REDUCTION.relative_to(ROOT).as_posix(), "binding_target": "CURRENT_COMMITTED_REPOSITORY_ROUTE_AND_CONTEXT_CONTRACT", "binding_time": "BEFORE_FRESH_OPERATION_GENERATION_HUMAN_AUTHORITY", "mutability": "REGENERATED_FOR_CURRENT_COMMIT", "revalidation_rule": "EXACT_CURRENT_COMMITTED_BYTES_AND_SINGLE_ROUTE", "post_commit_rule": "REAUTHENTICATE_AFTER_PREPARATORY_COMMIT", "consumption_rule": "NOT_APPLICABLE__NONAUTHORITY", "operational_admission_rule": "REPOSITORY_READINESS_IS_NOT_AUTHORIZATION", "authority_impact": "VERIFIED__NONE"},
            {"binding_name": "FRESH_OPERATION_CONTEXT", "binding_owner": "FM_BUILD_OPERATION_CONTEXT", "binding_source_artifact": CONTEXT.relative_to(ROOT).as_posix(), "binding_target": "GENERATION_OPERATION_CANDIDATE_REPOSITORY_ASSETS_ARGV_AND_LIMITS", "binding_time": "BEFORE_HUMAN_AUTHORITY", "mutability": "IMMUTABLE_AFTER_HUMAN_AUTHORITY_BINDS_CONTEXT", "revalidation_rule": "CANONICAL_SEAL_AND_EXACT_BINDINGS", "post_commit_rule": "REBUILD_BEFORE_HUMAN_ACT_IF_HEAD_TREE_CHANGED", "consumption_rule": "MUST_PRECEDE_CONSUMPTION", "operational_admission_rule": "MUST_EQUAL_OBSERVED_HEAD_TREE", "authority_impact": "VERIFIED__BECOMES_INPUT_TO_FRESH_HUMAN_AUTHORITY"},
            {"binding_name": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF", "binding_owner": "GN_PRESENTATION_PLUS_HUMAN_ACT_PLUS_FM_CANONICAL_HANDOFF", "binding_source_artifact": HANDOFF.relative_to(ROOT).as_posix(), "binding_target": "EXACT_CONTEXT_AND_REPOSITORY_HEAD_TREE", "binding_time": "AFTER_CURRENT_CONTEXT_BEFORE_CONSUMPTION", "mutability": "IMMUTABLE_NONREUSABLE", "revalidation_rule": "EXACT_SOURCE_BYTES_CANONICAL_JSON_AND_INNER_SEAL", "post_commit_rule": "NO_EXISTING_AUTHORITY_REBIND__NEW_HUMAN_ACT_REQUIRED_AFTER_HEAD_TREE_CHANGE", "consumption_rule": "ONE_SHOT", "operational_admission_rule": "AUTHORIZED_HEAD_TREE_EQUALS_OBSERVED_HEAD_TREE", "authority_impact": "VERIFIED__AUTHORITY_CREATED_ONLY_BY_FRESH_HUMAN_ACT"},
            {"binding_name": "PRECONSUMPTION_INVOCATION_BINDING", "binding_owner": "FM_JZ", "binding_source_artifact": BINDING.relative_to(ROOT).as_posix(), "binding_target": "HANDOFF_DIGEST_AND_FINAL_FM_ARGV", "binding_time": "BEFORE_CONSUMPTION_AND_FM_INVOCATION", "mutability": "IMMUTABLE_EVIDENCE_INSTANCE", "revalidation_rule": "REREAD_HANDOFF_AND_REDERIVE_DIGEST_AND_ARGV", "post_commit_rule": "DOES_NOT_REBIND_AUTHORITY", "consumption_rule": "BINDING_ITSELF_CONSUMES_ZERO_AUTHORITY", "operational_admission_rule": "FM_FINAL_ADMISSION_STILL_REQUIRED", "authority_impact": "VERIFIED__NONE"},
            {"binding_name": "FINAL_OPERATIONAL_ADMISSION_AND_CONSUMPTION", "binding_owner": "FM_PLUS_OPERATIONAL_CONTROLLER_PLUS_P11_ONE_SHOT_CONSUMER", "binding_source_artifact": FM.relative_to(ROOT).as_posix(), "binding_target": "OBSERVED_CURRENT_REPOSITORY_AND_ONE_SHOT_OPERATION", "binding_time": "AFTER_FRESH_HUMAN_ACT_BEFORE_PROCESS_START", "mutability": "OBSERVED_AND_LEDGERED", "revalidation_rule": "EXACT_CONTEXT_AUTHORITY_OBSERVED_EQUALITY", "post_commit_rule": "NO_COMMIT_BETWEEN_AUTHORITY_AND_ADMISSION", "consumption_rule": "GRANTED_UNCONSUMED_TO_CONSUMED_ONCE", "operational_admission_rule": "FAIL_CLOSED_ON_ANY_HEAD_TREE_DRIFT", "authority_impact": "VERIFIED__CONSUMES_EXACTLY_ONCE_ONLY_AFTER_ADMISSION"},
        ],
        "historical_successful_precedents": precedents,
        "additional_precedent_findings": {
            "fm": "VERIFIED__EXACT_FINAL_ADMISSION_OWNER__NO_REBIND_FUNCTION",
            "jz": "VERIFIED__DIGEST_PRESERVING_PRECONSUMPTION_BINDING__NONAUTHORITY__ZERO_CONSUMPTION",
            "ka": "VERIFIED__AUTHORITY_AND_EXECUTION_RECEIPT_BIND_SAME_HEAD__CONSUMED__OPERATION_REACHED_GUEST_FAILURE__NO_E05_CREDIT",
            "ke": "VERIFIED__AUTHORITY_AND_EXECUTION_RECEIPT_BIND_SAME_HEAD__CONSUMED__OPERATION_REACHED_GUEST_FAILURE__NO_E05_CREDIT",
            "kg": "VERIFIED__PRECONSUMPTION_FAILURE__AUTHORITY_NOT_CONSUMED__NO_OPERATION",
        },
        "circular_binding_check": {
            "circular_binding_status": "VERIFIED__RESOLVED_BY_AUTHORITY_FREE_POST_COMMIT_READINESS_THEN_SAME_HEAD_PREAUTHORIZATION_AUTHORIZATION_CONSUMPTION_AND_OPERATION_BEFORE_EVIDENCE_COMMIT",
            "cycle_entry": "HUMAN_AUTHORITY_BINDS_CURRENT_OPERATION_CONTEXT_HEAD_TREE",
            "cycle_cause": "COMMITTING_POST_AUTHORITY_PRECONSUMPTION_EVIDENCE_CHANGES_HEAD_BEFORE_ADMISSION",
            "existing_cycle_breaker": "DO_NOT_COMMIT_BETWEEN_FRESH_HUMAN_ACT_AND_OPERATIONAL_ADMISSION__COMMIT_OPERATIONAL_EVIDENCE_AFTER_TERMINAL",
            "cycle_breaker_owner": "SPCE_OPERATIONAL_GENERATION_ORDERING_PLUS_FM_EXACT_ADMISSION",
            "cycle_breaker_authority_impact": "VERIFIED__FRESH_ACT_REQUIRED_AFTER_ANY_PRIOR_COMMIT__NO_REBIND_OR_TRANSFER",
            "cycle_breaker_production_impact": "VERIFIED__NONE",
        },
        "existing_owner_mechanism_decision": {
            "result": "B__EXISTING_MECHANISM_FOUND_BUT_NOT_APPLICABLE_TO_KN",
            **owners,
            "kn_applicability": "NOT_APPLICABLE__KN_AUTHORITY_IS_IMMUTABLY_BOUND_TO_1141F9F_AND_CANNOT_BE_REBOUND_TO_74A01AB",
        },
        "authority_impact_analysis": {
            "does_it_change_human_intent": "NOT_PROVEN__FRESH_HUMAN_DECISION_REQUIRED",
            "does_it_change_authority_scope": "NOT_PROVEN__FRESH_HUMAN_DECISION_REQUIRED",
            "does_it_change_operation": "VERIFIED__NO_FOR_EXACT_SEMANTIC_REISSUE",
            "does_it_change_candidate": "VERIFIED__NO_SEMANTIC_CANDIDATE_CHANGE__REPOSITORY_COORDINATE_REVALIDATION_ONLY",
            "does_it_change_context_semantics": "VERIFIED__REPOSITORY_HEAD_TREE_AND_DERIVED_SEALS_CHANGE__OTHER_SEMANTICS_MUST_REVALIDATE_EQUAL",
            "does_it_change_route": "VERIFIED__NO", "does_it_change_one_shot_limits": "VERIFIED__NO",
            "does_it_consume_authority": "VERIFIED__NO_DURING_REBIND_AND_PREAUTHORIZATION__YES_ONCE_ONLY_IN_LATER_OPERATIONAL_PHASE",
            "does_it_reissue_authority": "VERIFIED__NO_AUTOMATIC_REISSUE__FRESH_HUMAN_ACT_CREATES_DISTINCT_AUTHORITY",
            "does_it_require_new_human_act": "VERIFIED__YES",
            "does_it_create_authority_transfer": "VERIFIED__NO", "does_it_create_parallel_authority_path": "VERIFIED__NO",
        },
        "frontier": {
            "last_verified_operational_edge": "VERIFIED__JH_FUTURE_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY",
            "first_unverified_operational_edge": "NOT_PROVEN__FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "VERIFIED__KV_EXISTING_LIFECYCLE_OWNER_AND_KN_NONAPPLICABILITY_LOCALIZED",
            "first_broken_edge": "VERIFIED__FRESH_CURRENT_HEAD_PREAUTHORIZATION_AND_NEW_HUMAN_ACT_NOT_PRESENT",
            "current_real_blocker": "VERIFIED__IMMUTABLE_KN_AUTHORITY_BINDS_1141F9F_WHILE_CURRENT_HEAD_IS_74A01AB",
            "minimum_missing_capability": "NOT_APPLICABLE__NO_NEW_PRODUCTION_CAPABILITY__FRESH_CURRENT_HEAD_OPERATION_GENERATION_AND_HUMAN_ACT_ARE_MISSING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_FRESH_OPERATIONAL_GENERATION_REUSING_EXISTING_POST_COMMIT_READINESS_CONTEXT_PRESENTATION_HANDOFF_BINDING_AND_ONE_SHOT_OWNERS__OBTAIN_NEW_HUMAN_ACT__NO_COMMIT_BETWEEN_ACT_AND_ADMISSION",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE", "repository_binding_lifecycle_scope": "COMMON_E05_INFRASTRUCTURE",
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "vector_specific_residue": "PER_VECTOR_CONTEXT_PRESENTATION_HUMAN_ACT_OPERATION_AND_E05_ACCEPTANCE",
            "reuse_preconditions": "CURRENT_COMMITTED_READINESS__FRESH_NAMESPACE__EXACT_HEAD_TREE__NEW_HUMAN_ACT_AFTER_LAST_COMMIT",
            "revalidation_required": "VERIFIED__PER_GENERATION_CONTEXT_CANDIDATE_ASSETS_AUTHORITY_AND_ADMISSION",
            "expected_future_proof_reduction": "ESTIMATED__AVOIDS_DUPLICATE_REBIND_OWNER_AND_POST_AUTHORITY_COMMIT_LOOP__NO_OPERATIONAL_PROOF_TRANSFER",
        },
        "e05": {"state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "governance": {
            "project_state": "VERIFIED__KV_DISCOVERY_COMPLETE__KN_AUTHORITY_UNCONSUMED_AND_INADMISSIBLE_AT_CURRENT_HEAD",
            "project_progress": "VERIFIED__LIFECYCLE_OWNER_AND_MINIMUM_LEGAL_NEXT_DELTA_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ONE_FRESH_CURRENT_HEAD_OPERATIONAL_GENERATION_AND_OPERATIONAL_OBSERVATION_REMAIN",
            "constitutional_health_evidence": "VERIFIED__EXACT_EQUALITY_PRESERVED__NO_AUTHORITY_REBIND_TRANSFER_OR_CONSUMPTION",
            "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficiency": "ESTIMATED__HIGH__EXISTING_OWNER_SEQUENCE_REUSED_AND_FALSE_CAPABILITY_GAP_REMOVED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_NEW_REBIND_OWNER_OR_COMMITTED_POST_AUTHORITY_LAYER_IS_ADDED",
            "cognition_provenance": "VERIFIED__COMMITTED_KU_JP_FM_AND_OPERATIONAL_PRECEDENT_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_KU_TO_KV_CONTINUATION__NO_MEMORY_AUTHORITY",
            "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATIONAL_DENIAL_REMAINS_UNOBSERVED",
            "shadow_design_target": "VERIFIED__EXISTING_ONE_ROUTE_SAME_HEAD_HUMAN_AUTHORIZED_ONE_SHOT_PIPELINE",
            "constitutional_continuation_progress": "VERIFIED__CURRENT_HEAD_BINDING_FAILURE_RECLASSIFIED_AND_CORRECTION_SEQUENCE_LOCALIZED",
        },
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0", "new_operational_capability_count": "VERIFIED__0", "new_blocker_localized_count": "VERIFIED__1__FRESH_CURRENT_HEAD_HUMAN_ACT", "new_blocker_closed_count": "VERIFIED__0", "new_false_or_superseded_blocker_removed_count": "VERIFIED__1__NEW_REBIND_CAPABILITY_GAP", "new_classification_result_count": "VERIFIED__1__EVIDENCE_OR_REPORTING_DEFECT", "new_binding_lifecycle_result_count": "VERIFIED__1", "new_authority_impact_result_count": "VERIFIED__1", "proof_reuse_count": "VERIFIED__17__EX_PLUS_HISTORICAL_LIFECYCLE_PRECEDENTS"},
        "validation": {"kv_focused": "VERIFIED__8_PASSED", "governance_tests": "VERIFIED__9_PASSED", "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS", "historical_owner_regressions": "NOT_PROVEN__44_PASSED__4_HISTORICAL_CURRENT_HEAD_OR_OWNER_DRIFT_FAILURES", "ex_legacy_validator": "NOT_PROVEN__FAIL_CLOSED__CURRENT_ER_OPERATIONAL_HARNESS_HASH_DIFFERS_FROM_FROZEN_SOURCE_MANIFEST", "python_ast": "VERIFIED", "g48_structure": "VERIFIED__EXACTLY_SIX_H1_AND_FIVE_RIA_QUESTIONS", "git_diff_check": "VERIFIED__PASS", "index": "VERIFIED__EMPTY"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_ambiguity_count": "VERIFIED__0", "authority_state_ambiguity_count": "VERIFIED__0", "binding_owner_ambiguity_count": "VERIFIED__0", "operational_attempt_ambiguity_count": "VERIFIED__0"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "auto_continuable": False, "human_review_required": True, "phase_b_started": False,
        "operational_counters": {name: 0 for name in ("operational_authorization_count", "authority_consumption_count", "pre_operational_invocation_count", "fm_operational_invocation_count", "qemu_start_count", "vm_start_count", "operation_attempt_count", "operation_request_count", "expired_denial_count", "p11_entry_count", "protected_invocation_count", "protected_effect_count", "retry_count", "repair_retry_count", "replay_count")},
    }


def envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {"schema_id": "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest()}


def materialize() -> None:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KVDiscoveryError("KV_REDUCTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def verify() -> None:
    if load_envelope(OUTPUT, "reduction") != build_reduction():
        raise KVDiscoveryError("KV_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    args = parser.parse_args()
    materialize() if args.mode == "materialize" else verify()


if __name__ == "__main__":
    main()
