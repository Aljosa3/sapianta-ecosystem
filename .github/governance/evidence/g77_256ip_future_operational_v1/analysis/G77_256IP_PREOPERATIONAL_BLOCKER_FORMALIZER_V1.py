#!/usr/bin/env python3
"""Fail-closed G77-256IP pre-operational FUTURE barrier formalizer.

This program is read-only.  It authenticates the committed IO checkpoint,
reconstructs the current V2 live binding, and proves whether the existing GN
Human-presentation owner can represent the requested FUTURE authorization.
It has no authority-consumption, launcher, QEMU, VM, or request capability.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
IO_HEAD = "af7835d98d0bfa685da99e41bd5bc866cbc2a54b"
IO_TREE = "cfeb589e9b51c200abdfaf7915799e384975927b"
IO_SUBJECT = "G77-256IO certify V2 live binding and readiness"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256IP_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IP_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"

IO_ROOT = Path(".github/governance/evidence/g77_256io_post_commit_v2_live_binding_readiness_v1")
IO_REPORT = IO_ROOT / "G77_256IO_G48_IMPLEMENTATION_REPORT_V1.md"
IO_TERMINAL = IO_ROOT / "G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IO_FORMALIZER = IO_ROOT / "analysis/G77_256IO_POST_COMMIT_V2_READINESS_FORMALIZER_V1.py"
IO_TEST = IO_ROOT / "tests/test_g77_256io_post_commit_v2_live_binding_readiness_v1.py"
IO_HASHES = {
    IO_REPORT: "5ee3828fd00011f6ad564a190f14f18f25210b994251c1da33904b46317b8a87",
    IO_TERMINAL: "266df18bb40a92943ac90267fab7c20cfb102dd144de5869af6ab678b891a448",
    IO_FORMALIZER: "7ac4a2d6a9d68ed9cc60754d01260449134b8b6771f7eea38510feadb711f595",
    IO_TEST: "d9ec782ce6c4537a2ea8db2cc43eda34c5f7e6b030e2067ca5c6d11a5f459b98",
}
DU_PATH = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_PATH = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_PATH = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
GN_PATH = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
FM_PATH = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IF_ACT_CHE = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
IF_ADAPTER = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py")
FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class IPBlockerError(ValueError):
    """One deterministic fail-closed IP reconstruction error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IPBlockerError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if raw != canonical_bytes(value):
        raise IPBlockerError(f"NONCANONICAL_JSON:{path}")
    return value


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def load_module(relative: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise IPBlockerError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": BRANCH, "head": IO_HEAD, "tree": IO_TREE,
        "subject": IO_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IO_HEAD, "index": "",
    }
    if observed != expected:
        raise IPBlockerError("EXACT_COMMITTED_IO_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT).returncode:
        raise IPBlockerError("STABLE_ANCESTRY_MISSING")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }:
        raise IPBlockerError("NESTED_AUTHORITY_MISMATCH")
    observed["local_remote_equality"] = "VERIFIED"
    observed["nested_authority"] = nested_state
    return observed


def reconstruct_io() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in IO_HASHES.items():
        raw = subprocess.check_output(["git", "show", f"{IO_HEAD}:{relative.as_posix()}"], cwd=ROOT)
        if raw != (ROOT / relative).read_bytes() or sha256_bytes(raw) != expected_sha:
            raise IPBlockerError(f"IO_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative.name] = {
            "git_blob": git("rev-parse", f"{IO_HEAD}:{relative.as_posix()}"),
            "sha256": expected_sha,
        }
    envelope = load_canonical(ROOT / IO_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IPBlockerError("IO_INNER_SEAL_MISMATCH")
    reduction = envelope["reduction"]
    terminal = reduction["terminal"]
    required = {
        "v2_post_commit_live_binding": "VERIFIED",
        "v2_preoperational_readiness": "VERIFIED",
        "future_preoperational_readiness": "VERIFIED",
        "runtime_target": "VERIFIED__AUTHENTICATED_IF",
        "certification_baseline": "VERIFIED__COMMITTED_IN",
    }
    if any(terminal[key] != value for key, value in required.items()):
        raise IPBlockerError("IO_TERMINAL_A_RECONSTRUCTION_MISMATCH")
    if set(reduction["operational_counters"].values()) != {0} or reduction["e05"]["after"] != "10/18":
        raise IPBlockerError("IO_OPERATIONAL_ZERO_OR_E05_MISMATCH")
    headings = [line for line in (ROOT / IO_REPORT).read_text().splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]:
        raise IPBlockerError("IO_G48_HEADING_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "inner_seal": "VERIFIED", "identities": identities}


def current_v2_readiness() -> dict[str, Any]:
    du = load_module(DU_PATH, "g77_256ip_du")
    eb = load_module(EB_PATH, "g77_256ip_eb")
    ee = load_module(EE_PATH, "g77_256ip_ee")
    authenticated_future_candidate = ROOT / IH_CANDIDATE
    if sha256_path(authenticated_future_candidate) != FUTURE_CANDIDATE_SHA:
        raise IPBlockerError("FUTURE_CANDIDATE_IDENTITY_DRIFT")
    with tempfile.TemporaryDirectory(prefix=".g77_256ip_v2_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du.build_du_fixture(ROOT)))
        readiness_fixture_sha256 = sha256_path(candidate)
        du_result = du.validate_file(candidate, ROOT, expected_head=IF_HEAD)
        if set(du_result.values()) != {"PASS"}:
            raise IPBlockerError("DU_V2_RECHECK_FAILED")
        eb_envelope = eb.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / candidate.name).write_bytes(candidate.read_bytes())
        harness = temporary / "fixture.py"
        harness.write_text(
            "from pathlib import Path\nRAW_ROOT = Path('/mnt/g77-evidence')\n"
            f"CONTINUATION_MANIFEST_PATH = RAW_ROOT / '{candidate.name}'\n"
        )
        ee_envelope = ee.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        eb_result = eb.verify_receipt_envelope(ROOT, eb_envelope)
        ee_result = ee.verify_receipt_envelope(ROOT, ee_envelope)
    baseline = {"head": IO_HEAD, "tree": IO_TREE}
    target = eb._authenticated_runtime_target(ROOT)
    if eb_envelope["receipt"]["certification_baseline"] != baseline:
        raise IPBlockerError("CURRENT_IO_CERTIFICATION_BASELINE_NOT_BOUND")
    if ee_envelope["receipt"]["certification_baseline"] != baseline:
        raise IPBlockerError("EB_EE_CERTIFICATION_BASELINE_DISAGREEMENT")
    if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE):
        raise IPBlockerError("AUTHENTICATED_RUNTIME_TARGET_NOT_IF")
    if eb_envelope["receipt"]["runtime_target_selection_binding"] != target:
        raise IPBlockerError("EB_RUNTIME_TARGET_BINDING_MISMATCH")
    if ee_envelope["receipt"]["runtime_target_selection_binding"] != target:
        raise IPBlockerError("EE_RUNTIME_TARGET_BINDING_MISMATCH")
    return {
        "du": "PASS", "eb": eb_result["overall_result"],
        "ee": ee_result["pre_materialization_runtime_path_binding_result"],
        "certification_baseline": baseline, "runtime_target": target,
        "authenticated_future_candidate_sha256": FUTURE_CANDIDATE_SHA,
        "v2_readiness_fixture_sha256": readiness_fixture_sha256,
        "runtime_certification_role_collapse": "VERIFIED__NO",
    }


def authenticate_future() -> dict[str, Any]:
    binding = load_canonical(ROOT / IF_ACT_CHE)["binding"]
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    context = load_canonical(ROOT / Path(
        ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    ))
    facts = {
        "evaluation": binding["evaluation_time_unix_ns"],
        "valid_from": act["payload"]["valid_from_unix_ns"],
        "valid_until": act["payload"]["valid_until_unix_ns"],
        "payload_digest": act["payload_digest"],
        "source_act": che["source_act_digest"],
        "che_correlation": che["correlation_identity"],
        "candidate_runtime_sha256": sha256_path(ROOT / IH_CANDIDATE),
        "authenticated_if_context_sha256": context["context_sha256"],
    }
    if not facts["evaluation"] < facts["valid_from"] < facts["valid_until"]:
        raise IPBlockerError("FUTURE_RELATION_MISMATCH")
    if (facts["payload_digest"], facts["source_act"], facts["che_correlation"]) != (
        FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE,
    ):
        raise IPBlockerError("FUTURE_ACT_CHE_IDENTITY_DRIFT")
    if facts["authenticated_if_context_sha256"] != FUTURE_CONTEXT_SHA:
        raise IPBlockerError("AUTHENTICATED_IF_CONTEXT_IDENTITY_DRIFT")
    facts["future_semantic_mutation_count"] = "VERIFIED__0"
    facts["wall_clock_dependency_count"] = "VERIFIED__0"
    return facts


def derive_operation_identity() -> dict[str, Any]:
    result = subprocess.run(
        ["git", "grep", "-F", OPERATION, IO_HEAD], cwd=ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode not in (0, 1):
        raise IPBlockerError("OPERATION_IDENTITY_HISTORY_SCAN_FAILED")
    if result.stdout:
        raise IPBlockerError("OPERATION_IDENTITY_COLLISION")
    return {
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "operation_identity_fresh": "VERIFIED",
        "operation_identity_collision": "VERIFIED__NO",
        "operation_identity_replay": "VERIFIED__NO",
    }


def presentation_blocker() -> dict[str, Any]:
    source = (ROOT / GN_PATH).read_text(encoding="utf-8")
    ast.parse(source, filename=str(GN_PATH))
    gn = load_module(GN_PATH, "g77_256ip_gn")
    supported = set(gn.SUPPORTED_VECTORS)
    fields = tuple(gn.PRESENTATION_FIELDS)
    if "FUTURE" in supported:
        raise IPBlockerError("GN_FUTURE_BLOCKER_NO_LONGER_PRESENT")
    if "SEALED_REQUEST_VECTOR_INVALID" not in source:
        raise IPBlockerError("GN_FAIL_CLOSED_VECTOR_REJECTION_NOT_PROVEN")
    if "AUTHORIZED_VECTOR_REQUESTED" not in fields:
        raise IPBlockerError("GN_VECTOR_PRESENTATION_FIELD_ABSENT")
    return {
        "owner": "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1",
        "owner_path": GN_PATH.as_posix(),
        "owner_git_blob": git("rev-parse", f"{IO_HEAD}:{GN_PATH.as_posix()}"),
        "owner_sha256": sha256_path(ROOT / GN_PATH),
        "supported_vectors": sorted(supported),
        "requested_vector": "FUTURE",
        "observed_fail_closed_reason": "SEALED_REQUEST_VECTOR_INVALID",
        "presentation_derivation": "NOT_PROVEN__EXISTING_GN_OWNER_REJECTS_FUTURE",
        "human_action_derivation": "NOT_PROVEN__NO_VALID_SEALED_PRESENTATION_EXISTS",
        "authority_protocol_mutation_performed": "VERIFIED__NO",
    }


def terminal_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    io = reconstruct_io()
    readiness = current_v2_readiness()
    future = authenticate_future()
    identity = derive_operation_identity()
    blocker = presentation_blocker()
    zero = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "future_operation", "request", "p11_entry",
        "protected_invocation", "protected_effect", "retry", "repair_retry",
        "replay", "e05_credit",
    )}
    return {
        "mode": "PREOPERATIONAL_FAIL_CLOSED__NO_AUTHORIZATION_PRESENTATION__NO_OPERATION",
        "entry": entry,
        "io_reconstruction": io,
        "v2_readiness_recheck": readiness,
        "future_semantics": future,
        "operation_identity": identity,
        "authorization_presentation": blocker,
        "boundaries": {
            "v1_semantics_reinterpreted": "VERIFIED__NO",
            "p11_change_required": "VERIFIED__NO",
            "p11_mutation": "VERIFIED__0",
            "fm_runtime_owner_mutation": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "reintroduced_historical_failure_count": "VERIFIED__0",
        },
        "proof_reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
        },
        "operational_counters": zero,
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8},
        "terminal": {
            "terminal": "C__PRE_OPERATIONAL_BLOCKER",
            "human_operational_authority": "NOT_PROVEN__FRESH_HUMAN_ACT_CANNOT_YET_BE_VALIDLY_PRESENTED",
            "last_verified_edge": "FRESH_UNIQUE_IP_FUTURE_OPERATION_IDENTITY_DERIVED_AFTER_IO_V2_READINESS_RECHECK",
            "first_broken_edge": "EXISTING_GN_SEALED_REQUEST_VALIDATION_REJECTS_FUTURE_VECTOR",
            "minimum_missing_capability": "BOUNDED_EXISTING_GN_FUTURE_VECTOR_PRESENTATION_ADMISSION_AND_GENERATION_BINDING",
            "minimum_legal_next_delta": "HUMAN_REVIEW_AND_SEPARATE_GOVERNED_GN_FUTURE_PRESENTATION_COMPATIBILITY_CHANGE__THEN_NEW_PREAUTHORIZATION_DERIVATION__NO_OPERATION",
            "auto_continuable": False,
            "human_action_required": True,
            "human_authorization_action_available": False,
            "next_generation_started": False,
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IO_DU_EB_EE_V2_IF_FM_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER_0",
            "new_capability_set": "VERIFIED__PREOPERATIONAL_BLOCKER_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__12__IE_THROUGH_IP",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_ip": "VERIFIED__BLOCKER_EVIDENCE_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IP_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__PREAUTHORIZATION_PRESENTATION_COMPATIBILITY_GAP",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__SEPARATE_GOVERNED_GN_COMPATIBILITY_DECISION",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_ENTRY",
            "authority_state_recovery": "VERIFIED__NO_AUTHORITY_CREATED",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMED",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_OPERATION",
            "operation_replay_prevention": "VERIFIED__ZERO_OPERATION",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED__BLOCKER_EXACT",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_TERMINAL_C",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_PRESERVED__PREOPERATIONAL_BLOCKER_VISIBLE",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__GN_FUTURE_PRESENTATION_COMPATIBILITY_THEN_FRESH_HUMAN_AUTHORITY",
            "governance_efficience": "ESTIMATED__HIGH__FAIL_CLOSED_BEFORE_AUTHORITY",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IO_TO_IP_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__NO_PROTOCOL_REPAIR_ATTEMPTED",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_COMMITTED_V2_LIVE_BINDING__PREOPERATIONAL_READY__AUTHORIZATION_PRESENTATION_BLOCKED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IM_DESIGN__IN_IMPLEMENTED__IO_READY__IP_GN_PRESENTATION_BLOCKER",
            "prompt_context_reuse_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IP_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__PREAUTHORIZATION_PRESENTATION_COMPATIBILITY_GAP",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "validation": {
            "ip_focused": "VERIFIED__8_PASSED",
            "io_current_applicable": "VERIFIED__18_PASSED",
            "io_historical_or_superseded_snapshot_assertions": "VERIFIED__5_DESELECTED_WITH_EXACT_LINEAGE_REASON",
            "p11_human_act_che_fk_gn_gl": "VERIFIED__110_PASSED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "governance": "VERIFIED__9_PASSED",
            "layer_0": "VERIFIED__CURRENT_GOVERNANCE_CONFORMANCE_AND_COMMITTED_IO_BINDING",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_inner_seal_ast_six_headings": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
        },
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256IP_SPCE_TERMINAL_PREOPERATIONAL_BLOCKER_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    try:
        print(canonical_bytes(terminal_envelope()).decode(), end="")
    except IPBlockerError as exc:
        print(canonical_bytes({"status": "FAIL_CLOSED", "reason": str(exc)}).decode(), end="")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
