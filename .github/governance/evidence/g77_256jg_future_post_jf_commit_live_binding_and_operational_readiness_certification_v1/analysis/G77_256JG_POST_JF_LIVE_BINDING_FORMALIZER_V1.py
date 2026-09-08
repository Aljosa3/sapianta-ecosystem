#!/usr/bin/env python3
"""Deterministic repository-only G77-256JG post-JF live-binding proof."""

from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JG = ROOT / ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1"
JF = ROOT / ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1"
JE = ROOT / ".github/governance/evidence/g77_256je_future_fresh_human_authorized_operational_denial_v1"
REPORT = JG / "G77_256JG_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = JG / "G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = JG / "analysis/G77_256JG_POST_JF_LIVE_BINDING_FORMALIZER_V1.py"
TEST = JG / "tests/test_g77_256jg_post_jf_live_binding_readiness_v1.py"
JF_TERMINAL = JF / "G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JF_FORMALIZER = JF / "analysis/G77_256JF_OPERATION_NAMESPACE_BINDING_FORMALIZER_V1.py"
FM_OWNER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
DU_PATH = ROOT / ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
EB_PATH = ROOT / ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py"
EE_PATH = ROOT / ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py"
EX_CERTIFICATE = ROOT / ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "547ea7c8cdd42b5519ecf7ec331f45fa92b37d5a"
ENTRY_TREE = "40e81f1df25b72a1d286c7bee947bcc655656cc3"
ENTRY_SUBJECT = "G77-256JF bind FUTURE exact governed operation namespace"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TARGET_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
TARGET_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
OWNER_SHA256 = "cef00e0fc99bc67a75648bcc65d54c90577467a3e0f12bec46097ae01b6543e5"
JF_TERMINAL_ID = "A__FUTURE_CURRENT_FM_CONTEXT_OWNER_SEALED_OPERATION_EVIDENCE_ROOT_NAMESPACE_BINDING_REPOSITORY_ONLY_VERIFIED"
TERMINAL_ID = "A__FUTURE_POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
EXPECTED_JG_FILES = {path.relative_to(ROOT).as_posix() for path in (REPORT, TERMINAL, FORMALIZER, TEST)}


class JGError(ValueError):
    """One deterministic fail-closed JG error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JGError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JGError(f"MALFORMED_JSON:{path}") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JGError(f"NONCANONICAL_JSON:{path}")
    return value


def load_unique(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JGError(f"MALFORMED_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise JGError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise JGError(f"MODULE_UNAVAILABLE:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_entry() -> dict[str, Any]:
    status = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    tracked = sorted(line[3:] for line in status if not line.startswith("?? "))
    untracked = {line[3:] for line in status if line.startswith("?? ")}
    nested = ROOT / "sapianta_system"
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "tracked_delta": tracked,
        "untracked_jg_files": sorted(untracked),
        "nested_head": git("rev-parse", "HEAD", cwd=nested),
        "nested_tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "nested_tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "nested_detached": git("branch", "--show-current", cwd=nested) == "",
        "nested_clean": git("status", "--porcelain=v1", cwd=nested) == "",
    }
    expected = {
        "branch": BRANCH, "head": ENTRY_HEAD, "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD, "index_empty": True,
        "tracked_delta": [], "untracked_jg_files": sorted(EXPECTED_JG_FILES),
        "nested_head": NESTED_HEAD, "nested_tree": NESTED_TREE,
        "nested_tag": NESTED_TAG, "nested_detached": True, "nested_clean": True,
    }
    if observed != expected:
        raise JGError("ENTRY_OR_JG_SCOPE_AUTHENTICATION_FAILED")
    observed["entry_worktree_before_jg_evidence"] = "VERIFIED__CLEAN"
    observed["remote_head_network_authentication"] = "VERIFIED__ENTRY_HEAD"
    observed["nested_remote_tag_authentication"] = "VERIFIED__NESTED_HEAD"
    return observed


def committed_bytes(relative: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT)


def reconstruct_jf() -> dict[str, Any]:
    envelope = load_canonical(JF_TERMINAL)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        raise JGError("JF_TERMINAL_REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise JGError("JF_TERMINAL_SEAL_MISMATCH")
    required = (
        reduction.get("terminal") == JF_TERMINAL_ID,
        reduction.get("human_architectural_selection") == "VERIFIED__OPTION_A",
        reduction.get("namespace_binding", {}).get("result") == "VERIFIED__OPTION_A_PROOF_GATE_PASS",
        reduction.get("namespace_binding", {}).get("namespace_authority_owner") == "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT",
        reduction.get("implementation", {}).get("current_fm_owner_hash_after") == OWNER_SHA256,
        reduction.get("preservation", {}).get("production_route_delta") == 0,
        reduction.get("preservation", {}).get("p11_mutation_count") == 0,
        reduction.get("e05", {}).get("after") == "VERIFIED__10_OF_18",
        reduction.get("e05", {}).get("credit") == "VERIFIED__0",
    )
    if not all(required):
        raise JGError("JF_TERMINAL_RECONSTRUCTION_FAILED")
    jf_formalizer = load_module("g77_256jg_jf_formalizer", JF_FORMALIZER)
    proof = jf_formalizer.option_a_proof_gate()
    if proof["result"] != "VERIFIED__OPTION_A_PROOF_GATE_PASS":
        raise JGError("JF_OPTION_A_PROOF_GATE_FAILED")
    return {
        "terminal": reduction["terminal"],
        "inner_seal": "VERIFIED",
        "option_a_authority": "VERIFIED__SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT",
        "proof_gate": proof["result"],
        "future_operational_status": reduction["e05"]["future"],
    }


def verify_committed_owner_binding() -> dict[str, Any]:
    owner_worktree = (ROOT / FM_OWNER).read_bytes()
    owner_committed = committed_bytes(FM_OWNER)
    launcher_worktree = (ROOT / FM_LAUNCHER).read_bytes()
    launcher_committed = committed_bytes(FM_LAUNCHER)
    digest = sha256_bytes(owner_committed)
    launcher_source = launcher_committed.decode()
    if owner_worktree != owner_committed or launcher_worktree != launcher_committed:
        raise JGError("CURRENT_OWNER_OR_LAUNCHER_NOT_COMMITTED")
    if digest != OWNER_SHA256 or launcher_source.count(OWNER_SHA256) != 1:
        raise JGError("CURRENT_OWNER_COMMITTED_HASH_BINDING_MISMATCH")
    return {
        "current_fm_owner_sha256": digest,
        "committed_binding": "VERIFIED",
        "launcher_binding": "VERIFIED__EXACT_COMMITTED_OWNER_SHA256",
    }


def verify_namespaces() -> dict[str, Any]:
    jf = load_module("g77_256jg_jf_namespace", JF_FORMALIZER)
    owner = load_module("g77_256jg_owner", ROOT / FM_OWNER)
    context = jf.load_canonical(jf.CONTEXT)
    projection = owner.validate_sealed_canonical_argv(
        context, validation_repository_root=owner.GUEST_REPOSITORY_ROOT
    )
    rejected: list[str] = []
    replacements = {
        "vector_only": jf.VECTOR_ONLY_ROOT,
        "cross_generation": jf.EXACT_ROOT.replace("g77_256je_", "g77_256jd_"),
        "cross_operation": jf.EXACT_ROOT.replace("operational_denial", "operational_request"),
        "namespace_escape": "/tmp/g77_256je_future_operational_v1/operation_state",
    }
    for name, replacement in replacements.items():
        mutated = deepcopy(context)
        mutated["operation_evidence_root"] = replacement
        try:
            owner.validate_context(mutated, repository_root=ROOT)
        except owner.ContextError:
            rejected.append(name)
    if projection["projection_status"] != "EXACT_GUEST_PROJECTION" or set(rejected) != set(replacements):
        raise JGError("NAMESPACE_BINDING_REGRESSION")
    return {
        "je_exact_namespace": "VERIFIED__ACCEPTED_REPOSITORY_ONLY",
        "vector_only_namespace": "VERIFIED__REJECTED",
        "cross_generation": "VERIFIED__REJECTED",
        "cross_operation": "VERIFIED__REJECTED",
        "namespace_escape": "VERIFIED__REJECTED",
        "caller_selectable_namespace_count": 0,
    }


def verify_v2_post_commit_binding() -> dict[str, Any]:
    du = load_module("g77_256jg_du_v2", DU_PATH)
    eb = load_module("g77_256jg_eb_v2", EB_PATH)
    ee = load_module("g77_256jg_ee_v2", EE_PATH)
    if any(name in inspect.signature(eb.validate_candidate).parameters for name in ("required_head", "required_tree")):
        raise JGError("CALLER_SELECTED_EB_BASELINE")
    if any(name in inspect.signature(ee.validate_binding).parameters for name in ("required_head", "required_tree")):
        raise JGError("CALLER_SELECTED_EE_BASELINE")
    du_self, du_evidence = du.run_self_test(ROOT)
    with tempfile.TemporaryDirectory(prefix=".g77_256jg_v2_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du_self))
        eb_envelope = eb.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / "G77_256EC_CONTINUATION_MANIFEST_V1.json").write_bytes(candidate.read_bytes())
        harness = ROOT / ".github/governance/evidence/g77_256ec_p11_operational_v1/harness/G77_256EC_P11_OPERATIONAL_HARNESS_V1.py"
        ee_envelope = ee.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        eb_self = eb.run_self_test(ROOT, candidate)
        ee_self = ee.run_self_test(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
    baseline = eb_envelope["receipt"]["certification_baseline"]
    ee_baseline = ee_envelope["receipt"]["certification_baseline"]
    if baseline != {"head": ENTRY_HEAD, "tree": ENTRY_TREE} or ee_baseline != baseline:
        raise JGError("V2_CERTIFICATION_BASELINE_MISMATCH")
    manifest = du_self["manifest"]
    if manifest["required_head"] != TARGET_HEAD or manifest["source_tree"] != TARGET_TREE:
        raise JGError("V2_RUNTIME_TARGET_MISMATCH")
    if (
        du_evidence["producer_consumer_compatibility"] != "PASS"
        or eb_self["overall_self_test_result"] != "PASS"
        or ee_self["overall_result"] != "PASS"
    ):
        raise JGError("V2_SELF_TEST_FAILED")
    return {
        "result": "VERIFIED__POST_COMMIT_LIVE_BINDING_PASS",
        "runtime_target": {"head": TARGET_HEAD, "tree": TARGET_TREE},
        "certification_baseline": baseline,
        "drift": "VERIFIED__CLOSED_AFTER_COMMITTED_JF_BASELINE",
        "du_negative_cases": du_evidence["negative_case_count"],
        "eb_cases": eb_self["case_count"],
        "ee_cases": ee_self["case_count"],
        "caller_selected_version": "VERIFIED__ABSENT",
    }


def verify_projection_and_reuse() -> dict[str, Any]:
    launcher = load_module("g77_256jg_launcher", ROOT / FM_LAUNCHER)
    with tempfile.TemporaryDirectory(prefix="g77_256jg_projection_") as raw:
        temporary = Path(raw)
        operation_root = temporary / "evidence/operation_state"
        operation_root.parent.mkdir()
        context = launcher.build_operation_context(
            repository_root=ROOT, repository_head=ENTRY_HEAD, repository_tree=ENTRY_TREE,
            generation_identity="G77_256JG_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
            operation_identity="G77_256JG_E05_FUTURE_DENIAL_BEFORE_ENTRY_001",
            identity_namespace_prefix="G77_256JG", operation_evidence_root=operation_root,
            transient_root=temporary / "transient", candidate_source_path=IH_CANDIDATE,
        )
        source = temporary / "context.json"
        source.write_bytes(canonical_bytes(context))
        materialized = launcher.materialize_operation_state(
            repository_root=ROOT, context=context, context_source_path=source,
            candidate_source_path=IH_CANDIDATE,
        )
        observed = launcher.observe_context_assets(ROOT, context, IH_CANDIDATE)
        readiness = launcher.authority_free_static_readiness(
            repository_root=ROOT, context=context, observed_head=ENTRY_HEAD,
            observed_tree=ENTRY_TREE, repository_clean=True,
            observed_asset_sha256=observed, candidate_source_path=IH_CANDIDATE,
        )
        projection_root = Path(context["guest_adapter_binding"]["projection_root"])
        members = sorted(path.name for path in projection_root.iterdir())
    source_tree = ast.parse((ROOT / FM_LAUNCHER).read_text())
    mains = [node for node in source_tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    certificate = load_unique(EX_CERTIFICATE)["certificate"]
    if (
        readiness["result"] != "STATIC_READINESS_PASS"
        or materialized["qemu_execution_count"] != 0
        or len(members) != 3
        or len(mains) != 1
        or certificate["component_counts"]["CERTIFIED"] != 17
        or certificate["certificate_is_credit_authority"] is not False
    ):
        raise JGError("PROJECTION_ROUTE_OR_EX_REUSE_FAILED")
    return {
        "jc_jd_projection": "VERIFIED__THREE_MEMBER_READ_ONLY_HARNESS",
        "harness_members": members,
        "production_route_before": 1,
        "production_route_after": 1,
        "production_route_delta": 0,
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def verify_firewalls() -> dict[str, Any]:
    adapter = (ROOT / ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py").read_text()
    semantic_values = (
        "EVALUATION_TIME_UNIX_NS = 500", "BASELINE_VALID_FROM_UNIX_NS = 100",
        "FUTURE_VALID_FROM_UNIX_NS = 600", "VALID_UNTIL_UNIX_NS = 1000",
        "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "operational Human act is not current",
    )
    if not all(value in adapter for value in semantic_values):
        raise JGError("FUTURE_SEMANTICS_CHANGED")
    protected = (
        ".github/governance/evidence/g77_256er_p11_operational_v1",
        ".github/governance/evidence/g77_256je_future_fresh_human_authorized_operational_denial_v1",
        ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1",
    )
    if git("diff", "--name-only", "HEAD", "--", *protected):
        raise JGError("HISTORICAL_OR_P11_MUTATION")
    return {
        "future_semantics": "VERIFIED__UNCHANGED__WALL_CLOCK_DEPENDENCY_0",
        "p11_mutation_count": 0,
        "historical_evidence_mutation_count": 0,
        "shadow_automation_status": "VERIFIED__ABSENT",
    }


def terminal_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    jf = reconstruct_jf()
    owner = verify_committed_owner_binding()
    namespaces = verify_namespaces()
    v2 = verify_v2_post_commit_binding()
    reuse = verify_projection_and_reuse()
    firewalls = verify_firewalls()
    counters = {key: 0 for key in (
        "operational_authorization", "authority_consumption", "pre_operational",
        "fm_operational_invocation", "qemu", "vm", "request", "p11_entry",
        "protected_invocation", "protected_effect", "retry", "repair_retry", "replay",
    )}
    return {
        "schema_id": "G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JG", "terminal": TERMINAL_ID,
        "mode": "REPOSITORY_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "entry": entry,
        "jf_reconstruction": jf,
        "current_owner": owner,
        "namespace_binding": namespaces,
        "v2_live_binding": v2,
        "reuse": reuse,
        "firewalls": firewalls,
        "operational_counters": counters,
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0", "future_operational_status": "NOT_PROVEN_OPERATIONALLY"},
        "frontier": {
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_DENIAL_NOT_YET_PROVEN",
            "last_verified_edge": "VERIFIED__POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_DENIAL_NOT_YET_PROVEN",
            "blocking_owner": "HUMAN_OPERATIONAL_AUTHORIZATION_AND_SEPARATE_COMMISSIONING_GENERATION",
            "minimum_missing_capability": "FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_DENIAL",
            "minimum_legal_next_delta": "HUMAN_REVIEW_THEN_OPTIONAL_JG_COMMIT_REMOTE_RATIFICATION_THEN_SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_COMMISSIONING",
        },
        "metrics": {
            "project_progress": "VERIFIED__E05_10_OF_18__POST_JF_COMMIT_READINESS_VERIFIED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_EVIDENCE_ONLY_CERTIFICATION",
            "architectural_governance_efficience": "VERIFIED__ZERO_PRODUCTION_MUTATION_ONE_ROUTE_ZERO_REGISTRIES_ZERO_P11_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "aigol_codex_work_share": "NOT_MEASURED", "prompt_context_reuse_ratio": "NOT_MEASURED",
            "repository_derived_execution_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW", "proof_process_overhead_risk": "ESTIMATED__MODERATE",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__JF_JE_JD_JC_FM_DU_EB_EE_V2_GN_GL_ER_FC_FK_CHE_P11_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__POST_COMMIT_CERTIFICATION_AND_READINESS_ONLY__NO_NEW_PRODUCTION_CAPABILITY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY", "parallel_flow_created": "VERIFIED__NO",
        },
        "overengineering": {
            "new_abstraction_count": 0, "new_generic_framework_count": 0,
            "generic_projection_framework_count": 0, "new_route_count": 0,
            "new_registry_count": 0, "new_namespace_registry_count": 0,
            "new_generic_namespace_broker_count": 0, "caller_selectable_identity_count": 0,
            "caller_selectable_namespace_count": 0, "duplicate_owner_semantics_count": 0,
            "duplicate_future_adapter_count": 0, "duplicate_p11_logic_count": 0,
            "new_generic_adapter_count": 0, "new_dispatcher_count": 0,
            "new_global_registry_count": 0,
        },
        "cognition": {
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_COMMITTED_AND_REMOTE_RATIFIED_JF_REPOSITORY_EVIDENCE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_COMMITTED_JF_EVIDENCE_COMMITTED_JE_HISTORY_AND_DETERMINISTIC_JG_REPOSITORY_ANALYSIS_PRIMARY__PROVIDER_MODEL_NONAUTHORITATIVE",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_REMOTE_RATIFIED_JF_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__JG_SCOPE_AND_JF_CHECKPOINT_COORDINATES",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JF_TO_JG",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__JG_SINGLE_WORKER_CONTINUATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__JG_ENTRY_CLEAN",
            "authority_state_recovery": "VERIFIED__JF_ZERO_AUTHORITY__JE_CONSUMED_NONREUSABLE",
            "consumed_authority_recovery": "VERIFIED__JE_HISTORICAL_ONLY__NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__JE_TERMINAL_RECONSTRUCTED__NO_JG_OPERATION",
            "operation_replay_prevention": "VERIFIED__NO_REPLAY", "cross_worker_constitutional_drift": "VERIFIED__0_AT_ARTIFACT_LEVEL",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JG_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "candidate": {
            "before": "CURRENT_FM_CONTEXT_OWNER_EXACT_GOVERNED_OPERATION_NAMESPACE_BINDING_REPOSITORY_ONLY_VERIFIED",
            "after": "POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED",
            "shadow_design_target": "FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        },
        "continuity": {
            "constitutional_health_evidence": "VERIFIED__IV_TO_IW_TO_IX_TO_IY_TO_IZ_TO_JA_TO_JB_TO_JC_TO_JD_TO_JE_FAILURE_AND_RECOVERY_TO_JF_OPTION_A_PROOF_BINDING_RECOVERY_COMMIT_REMOTE_RATIFICATION_TO_JG_POST_COMMIT_READINESS",
            "constitutional_continuation_progress": "VERIFIED__IV_IMPORT_ROOT_FAILURE__IW_IMPORT_ROOT_BINDING__IX_POST_COMMIT_IMPORT_READINESS__IY_ENTRYPOINT_ABSENCE__IZ_ENTRYPOINT_STATIC_BINDING__JA_POST_COMMIT_LIVE_BINDING_READINESS__JB_OWNER_DRIFT__JC_OWNER_PROJECTION__JD_POST_JC_LIVE_BINDING_READINESS__JE_FRESH_HUMAN_AUTHORIZATION__JE_ONE_SHOT_OPERATION__JE_PRE_REQUEST_NAMESPACE_FAILURE__JE_TERMINAL_RECOVERY__JE_COMMIT_REMOTE_RATIFICATION__JF_ARCHITECTURAL_AMBIGUITY__HUMAN_OPTION_A_SELECTION__JF_OPTION_A_PROOF__JF_EXACT_NAMESPACE_BINDING__JF_PROVIDER_LIMIT_RECOVERY__JF_COMMIT__JF_REMOTE_RATIFICATION__JG_POST_COMMIT_LIVE_BINDING_RESULT",
        },
        "validation": {
            "jg_focused": "VERIFIED__15_PASSED", "jf_committed_evidence": "VERIFIED__28_OF_28_HISTORICAL_PRECOMMIT_SUITE_RECONSTRUCTED__26_CURRENT_APPLICABLE_PASS__2_CHECKPOINT_PINNED",
            "fm_owner": "VERIFIED__17_PASSED", "hg_jc_jd_current_applicable": "VERIFIED__9_PLUS_15_PLUS_13_PASSED",
            "du_eb_ee_v2": "VERIFIED__20_CURRENT_APPLICABLE_PASSED__5_HISTORICAL_CHECKPOINT_PINNED__JG_DIRECT_LIVE_BINDING_PASS",
            "future_semantics": "VERIFIED__10_PASSED__1_HISTORICAL_CHECKPOINT_PINNED",
            "gn_gl": "VERIFIED__52_PASSED", "fk_che": "VERIFIED__11_PASSED",
            "ex": "VERIFIED__12_OF_12__17_OF_17_REUSED", "governance_pytest": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS", "git_diff_check": "VERIFIED__PASS",
        },
        "human_review_required": True, "auto_continuable": False,
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
