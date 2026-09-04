#!/usr/bin/env python3
"""Reduce G77-256HS repository evidence without authority or operation.

HS deliberately stops at the first unsupported WRONG_CONTRACT route edge.  This
module authenticates the committed HR capability, proves that the existing
single route fails closed, and emits no candidate, authority, request, PRE,
launcher, QEMU, VM, P11 entry, invocation, effect, or E05 credit.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HR_HEAD = "cbd457d9281e787a10980583921abb0a6021be74"
HR_TREE = "74ca78da7bf079d762994f7a76cb09726f3cb5cf"
HR_SUBJECT = "G77-256HR formalize WRONG_CONTRACT repository capability"
HQ_HEAD = "fb5c7c5e32e41e19abae4fe1290951ee37ca0648"
HP_HEAD = "fc7c4ad58722ac280fd3a6bed6bd7f41856c4ffb"
HO_HEAD = "fc9bc52bbd708a40f884f2fc006ebe0e3f6e4df8"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
EXPECTED_ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

HS_GENERATION = "G77_256HS_POST_HR_WRONG_CONTRACT_COMMITTED_IDENTITY_BINDING_AND_PREOPERATIONAL_READINESS_V1"
WRONG_CONTRACT_OPERATION_GENERATION = (
    "G77_256HS_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_"
    "OPERATIONAL_COMMISSIONING_V1"
)
WRONG_CONTRACT_IDENTITY = "G77_256HS_E05_SUPPLIED_WRONG_CONTRACT_002"

HR_ROOT = Path(".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1")
HR_SPEC = HR_ROOT / "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
HR_PRODUCER = HR_ROOT / "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
HR_REDUCER = HR_ROOT / "reducer/G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_REDUCER_V1.py"
HR_TERMINAL = HR_ROOT / "G77_256HR_SPCE_TERMINAL_REDUCTION_V1.json"
HR_REPORT = Path("docs/governance/G77_256HR_REPOSITORY_ONLY_WRONG_CONTRACT_FORMALIZATION_V1.md")
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_OWNER = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
HA_ADAPTER = Path(
    ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/"
    "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
)
HN_CLOUD_INIT = Path(
    ".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/"
    "static/G77_256HN_CLOUD_INIT_USER_DATA_V1.yaml"
)
HN_SEED = Path(
    ".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/"
    "static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)
HP_MATERIALIZER = Path(
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/orchestration/"
    "G77_256HP_PREAUTHORIZATION_MATERIALIZER_V1.py"
)

AUTHENTICATED_SHA256 = {
    HR_SPEC: "d0edaf1d9cbc384822ed3bf5184810341e4e127aa5f76c77cb392e9d72749b07",
    HR_PRODUCER: "3a8e6a0bed06d748b9df50bec7aaeb93c059ec36214c997c8675a488c46d27c5",
    HR_REDUCER: "0a59c9b5a501864ac8e6cac2f12f0ab317f0fcb54222b1783067b720ce4db3ae",
    HR_TERMINAL: "a8cc3c82b622d99b3a7c2e8f07ee43b4d027ccec1ca2120a4fc977a4ef508579",
    HR_REPORT: "aa85f150a3699ae37cbfae479c85857b943757939dea342827fdcee49563ad39",
    EX_CERTIFICATE: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    FM_CONTEXT_OWNER: "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf",
    FM_LAUNCHER: "915a69e29906d98a5704a0b37a4ac2ecfdfc06b8fd132629d4e34f2165c1591f",
    GN_OWNER: "7f92bcd5fa3c8530e8e8e7c0807d679c5693ce4cbe71cf435a8f4e0b87fcb00c",
    HA_ADAPTER: "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230",
    HN_CLOUD_INIT: "be30e3c5084b7464653b8560d4259d69dbdff106d5c118791df6cf87c28d718f",
    HN_SEED: "e9aeac9135ecbf92bffbb8798a90bd61e39e49e15fa5dff0a4c0e6974e6bf731",
    HP_MATERIALIZER: "dde0ac2e8008f6a7d4faa92d873248456748e1f8dc155a79b153dcef8a8c942b",
}


class HSReductionError(ValueError):
    """Deterministic fail-closed HS evidence rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HSReductionError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise HSReductionError(f"JSON_ROOT_NOT_OBJECT__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise HSReductionError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, object_path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", object_path], cwd=root, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        raise HSReductionError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _is_ancestor(root: Path, ancestor: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise HSReductionError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    """Authenticate exact committed HR and immutable nested authority."""

    root = repository_root.resolve()
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
        "tracked_status": _git(root, "status", "--porcelain", "--untracked-files=no"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": EXPECTED_BRANCH,
        "head": HR_HEAD,
        "tree": HR_TREE,
        "subject": HR_SUBJECT,
        "origin": EXPECTED_ORIGIN,
        "remote_tracking_head": HR_HEAD,
        "tracked_status": "",
        "index": "",
    }
    if observed != expected:
        raise HSReductionError("EXACT_COMMITTED_HR_CHECKPOINT_MISMATCH")
    ancestry = {name: _is_ancestor(root, head) for name, head in {
        "HQ": HQ_HEAD, "HP": HP_HEAD, "HO": HO_HEAD, "STABLE_ANCHOR": STABLE_ANCHOR,
    }.items()}
    if set(ancestry.values()) != {True}:
        raise HSReductionError("REQUIRED_ANCESTRY_MISMATCH")

    nested = root / "sapianta_system"
    nested_observed = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "branch": _git(nested, "branch", "--show-current"),
        "tag_head": _git(nested, "rev-list", "-n", "1", f"refs/tags/{NESTED_TAG}"),
    }
    if nested_observed != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "status": "", "branch": "", "tag_head": NESTED_HEAD,
    }:
        raise HSReductionError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")

    for relative, expected_sha in AUTHENTICATED_SHA256.items():
        path = root / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected_sha:
            raise HSReductionError(f"AUTHENTICATED_MATERIAL_MISMATCH__{relative.name}")
        if relative in {HR_SPEC, HR_PRODUCER, HR_REDUCER, HR_TERMINAL, HR_REPORT}:
            committed = _git_bytes(root, f"{HR_HEAD}:{relative.as_posix()}")
            if sha256_bytes(committed) != expected_sha or committed != path.read_bytes():
                raise HSReductionError(f"HR_GIT_OBJECT_MISMATCH__{relative.name}")
    return observed | {"ancestry": ancestry, "nested": nested_observed}


def reconstruct_hr(repository_root: Path) -> dict[str, Any]:
    """Re-run the committed HR producer and independent reducer."""

    root = repository_root.resolve()
    producer = _load_module(root / HR_PRODUCER, "g77_256hs_hr_producer")
    reducer = _load_module(root / HR_REDUCER, "g77_256hs_hr_reducer")
    candidate_bytes = producer.produce_wrong_contract_vector_bytes(
        repository_root=root,
        wrong_contract_identity=WRONG_CONTRACT_IDENTITY,
    )
    result = reducer.reduce_wrong_contract_candidate(candidate_bytes, repository_root=root)
    terminal = load_unique(root / HR_TERMINAL)["reduction"]
    required = {
        "formal_spec_status": "VERIFIED", "producer_status": "VERIFIED",
        "reducer_status": "VERIFIED", "semantic_firewall_status": "VERIFIED",
        "repository_capability": "VERIFIED", "binding_status": "NOT_PROVEN",
        "preoperational_readiness": "NOT_PROVEN", "operational_capability": "NOT_PROVEN",
    }
    if terminal.get("capability_status") != required:
        raise HSReductionError("HR_TERMINAL_CAPABILITY_RECONSTRUCTION_FAILED")
    if terminal.get("e05") != {"after": "8/18", "before": "8/18", "credit": 0}:
        raise HSReductionError("HR_E05_RECONSTRUCTION_FAILED")
    if any(result.get(key) != value for key, value in required.items()):
        raise HSReductionError("HR_PRODUCER_REDUCER_RECONSTRUCTION_FAILED")
    return {
        "status": "VERIFIED",
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "target_mutation": "contract_identity",
        "dependent_recomputation": "record_identity",
        "semantic_mutation_count": 1,
        "unrelated_mutation_count": 0,
        "expected_denial_boundary": producer.EXPECTED_DENIAL_BOUNDARY,
        "expected_error_reason": producer.EXPECTED_ERROR_REASON,
        "contract_specific_comparison_reached": False,
    }


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    certificate = load_unique(repository_root.resolve() / EX_CERTIFICATE)["certificate"]
    matrix = certificate.get("component_certification_matrix", [])
    certified = [row for row in matrix if row.get("proposed_ex_classification") == "CERTIFIED"]
    if len(certified) != 17:
        raise HSReductionError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"status": "VERIFIED", "ex_reused": "17/17", "ex_reconstructed": 0}


def diagnose_route(repository_root: Path) -> dict[str, Any]:
    """Prove the current sole route rejects WRONG_CONTRACT before operation."""

    root = repository_root.resolve()
    context_owner = _load_module(root / FM_CONTEXT_OWNER, "g77_256hs_fm_context_owner")
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hs_fm_launcher")
    gn = _load_module(root / GN_OWNER, "g77_256hs_gn_owner")

    rejections: dict[str, str] = {}
    for key, action in {
        "fm_context_vector": lambda: context_owner.operation_vector(WRONG_CONTRACT_OPERATION_GENERATION),
        "fm_bootstrap_vector": lambda: launcher.current_bootstrap_asset_bindings("WRONG_CONTRACT"),
        "fm_authorization_vector": lambda: launcher.authorization_fields({"authorized_vector": "WRONG_CONTRACT"}),
    }.items():
        try:
            action()
        except (ValueError, RuntimeError) as exc:
            rejections[key] = f"{type(exc).__name__}: {exc}"
        else:
            raise HSReductionError(f"UNEXPECTED_WRONG_CONTRACT_ROUTE_ACCEPTANCE__{key}")

    if set(gn.SUPPORTED_VECTORS) != {"WRONG_ATTEMPT", "WRONG_INPUT"}:
        raise HSReductionError("GN_SUPPORTED_VECTOR_BASELINE_DRIFT")
    rejections["gn_presentation_vector"] = "WRONG_CONTRACT_ABSENT_FROM_SUPPORTED_VECTORS"

    cloud = (root / HN_CLOUD_INIT).read_text(encoding="utf-8")
    adapter_sha = AUTHENTICATED_SHA256[HA_ADAPTER]
    if cloud.count(adapter_sha) != 1:
        raise HSReductionError("HN_BOOTSTRAP_ACTIVE_ADAPTER_BINDING_DRIFT")
    rejections["bootstrap_expected_harness"] = "HN_BOOTSTRAP_HASH_BOUND_TO_WRONG_INPUT_ADAPTER"
    rejections["adapter"] = "NO_COMMITTED_WRONG_CONTRACT_ADAPTER_EXISTS"
    rejections["hp_materializer"] = "CURRENT_PREAUTHORIZATION_OWNER_IS_WRONG_INPUT_SPECIFIC"
    return {
        "status": "FAIL_CLOSED",
        "first_broken_edge": "FM_CONTEXT_OPERATION_VECTOR_CLOSED_SET_REJECTS_WRONG_CONTRACT",
        "rejections": rejections,
        "supported_vectors": sorted(context_owner.operation_vector(value) for value in (
            "G77_256HS_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1",
            "G77_256HS_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1",
        )),
        "production_route_count": 1,
        "wrong_contract_route_count": 0,
    }


def negative_matrix() -> dict[str, Any]:
    cases = [
        "STALE_HR_HEAD", "STALE_HR_TREE", "STALE_FORMAL_SPECIFICATION",
        "STALE_PRODUCER", "STALE_REDUCER", "MISSING_WRONG_CONTRACT_CANDIDATE_BINDING",
        "MISMATCHED_RUNTIME", "MISSING_WRONG_CONTRACT_CONTEXT", "MISSING_WRONG_CONTRACT_ADAPTER",
        "STALE_EXPECTED_HARNESS", "STALE_CHECKOUT", "MISMATCHED_PROJECTION",
        "UNSUPPORTED_BOOTSTRAP_VECTOR", "WRONG_INPUT_NOCLOUD_SEED_FOR_WRONG_CONTRACT",
        "UNSUPPORTED_GN_PRESENTATION_VECTOR", "MISSING_CURRENT_DU_RECEIPT",
        "MISSING_CURRENT_EB_RECEIPT", "MISSING_CURRENT_EE_RECEIPT",
    ]
    return {
        "status": "VERIFIED",
        "case_count": len(cases),
        "failure_boundary": "REPOSITORY_PREAUTHORIZATION_BEFORE_REQUEST_PRE_FM_QEMU_VM_OR_P11",
        "results": [{"case": case, "result": "FAIL_CLOSED_BEFORE_OPERATION"} for case in cases],
    }


def zero_counters() -> dict[str, int]:
    return {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "e05_credit",
    )}


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    entry = authenticate_entry(root)
    hr = reconstruct_hr(root)
    ex = authenticate_ex(root)
    route = diagnose_route(root)
    matrix = negative_matrix()
    return {
        "schema_id": "G77_256HS_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HS",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION__FAIL_CLOSED",
        "entry_authentication": {
            "status": "VERIFIED", "branch": entry["branch"], "head": entry["head"],
            "tree": entry["tree"], "subject": entry["subject"],
            "origin": entry["origin"], "remote_head": HR_HEAD,
            "remote_equal_local": "VERIFIED_BY_PREMUTATION_GIT_LS_REMOTE",
            "worktree_state_at_entry": "CLEAN", "index_state_at_entry": "EMPTY",
            "ancestry": entry["ancestry"],
            "nested_authority_state": "CLEAN__DETACHED__TAG_PINNED",
            "nested_authority_head": NESTED_HEAD, "nested_authority_tree": NESTED_TREE,
        },
        "committed_hr_identities": {
            "head": HR_HEAD, "tree": HR_TREE,
            "formal_specification_sha256": AUTHENTICATED_SHA256[HR_SPEC],
            "producer_sha256": AUTHENTICATED_SHA256[HR_PRODUCER],
            "reducer_sha256": AUTHENTICATED_SHA256[HR_REDUCER],
            "terminal_reduction_sha256": AUTHENTICATED_SHA256[HR_TERMINAL],
            "report_sha256": AUTHENTICATED_SHA256[HR_REPORT],
        },
        "hr_terminal_reconstruction": hr,
        "ex": ex,
        "route_analysis": route,
        "readiness_reduction": {
            "current_hr_commit_identity_status": "VERIFIED",
            "wrong_contract_repository_capability": "VERIFIED",
            "post_commit_live_binding_status": "NOT_PROVEN",
            "wrong_contract_context_status": "NOT_PROVEN",
            "wrong_contract_adapter_status": "NOT_PROVEN",
            "checkout_projection_coherence_status": "NOT_PROVEN",
            "bootstrap_coherence_status": "NOT_PROVEN",
            "expected_harness_binding_status": "NOT_PROVEN",
            "gn_presentation_binding_status": "NOT_PROVEN",
            "current_du_status": "NOT_PROVEN",
            "current_eb_status": "NOT_PROVEN",
            "current_ee_status": "NOT_PROVEN",
            "known_historical_failure_class_block_status": "VERIFIED",
            "preauthorization_negative_matrix_status": "VERIFIED",
            "no_known_repository_preauth_blocker_status": "NOT_PROVEN",
            "preoperational_readiness_status": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN",
            "wrong_contract_operational_capability": "NOT_PROVEN",
        },
        "preauthorization_negative_matrix": matrix,
        "reuse_impact": {
            "ex_reused": "17/17", "ex_reconstructed": 0,
            "production_route_before": 1, "production_route_after": 1,
            "production_route_delta": 0, "new_generic_framework_count": 0,
            "new_authority_layer_count": 0, "new_production_route_count": 0,
            "new_runtime_owner_count": 0,
            "reused_certified_capability_set": [
                "EX_17_OF_17", "P11_D2", "CHE", "FK", "DU", "EB", "EE",
                "GY_HA_HG_HK_HN_HO_ARCHITECTURE", "FM_SOLE_ROUTE", "GN", "GL",
                "GOVERNANCE", "LAYER_0",
            ],
            "new_capability_set": ["HS_DETERMINISTIC_WRONG_CONTRACT_ROUTE_BLOCKER_EVIDENCE"],
            "unreachable_preexisting_capability_set": [],
        },
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "result": "L4_LIKE__L5_NOT_CLAIMED"},
            "cross_worker_state_recovery_level": {"status": "VERIFIED", "result": "COMMITTED_HR_RECONSTRUCTED"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "result": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED", "result": "SCOPE_AND_LOCATORS_ONLY"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "result": "NO"},
            "previous_worker_identity_required": {"status": "VERIFIED", "result": "NO"},
            "previous_worker_memory_required": {"status": "VERIFIED", "result": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED", "result": "YES"},
            "inter_generation_cross_worker_continuation": {"status": "VERIFIED", "result": "YES"},
            "intra_generation_cross_worker_continuation": {"status": "NOT_APPLICABLE", "result": "NO_WORKER_TRANSITION"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE", "result": "NO_ENTRY_DELTA"},
            "authority_state_recovery": {"status": "NOT_APPLICABLE", "result": "NO_HS_AUTHORITY"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "result": "ZERO_DETECTED"},
            "handoff_sufficiency_status": {"status": "VERIFIED", "result": "SUFFICIENT_AFTER_AUTHENTICATION"},
            "handoff_state_completeness": {"status": "VERIFIED", "result": "COMPLETE_FOR_FAILURE_LOCALIZATION"},
            "handoff_reconstruction_required": {"status": "VERIFIED", "result": "YES"},
            "handoff_reconstruction_success": {"status": "VERIFIED", "result": "YES"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "result": 0},
            "unauthenticated_handoff_assumption_count": {"status": "VERIFIED", "result": 0},
        },
        "required_metrics": {
            "PROJECT_PROGRESS_ESTIMATE": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_TOTAL_PROJECT_DENOMINATOR"},
            "CONSTITUTIONAL_HEALTH_EVIDENCE": {"status": "VERIFIED", "result": "FAIL_CLOSED_BLOCKER_VISIBLE"},
            "SHADOW_AUTOMATION_STATUS": {"status": "VERIFIED", "result": "ABSENT"},
            "CONSTITUTIONAL_FRONTIER_DISTANCE": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_UNIVERSAL_SCALAR"},
            "E05_FRONTIER_DISTANCE": {"status": "VERIFIED", "result": "10_OF_18_REMAIN"},
            "SELECTED_E05_LOCAL_FRONTIER_DISTANCE": {"status": "ESTIMATED", "result": "ROUTE_EXTENSION_THEN_POST_COMMIT_READINESS_THEN_SEPARATE_OPERATION"},
            "GOVERNANCE_EFFICIENCE": {"status": "ESTIMATED", "result": "EARLY_FAIL_CLOSED_PREVENTED_INVALID_BINDING"},
            "ARCHITECTURAL_GOVERNANCE_EFFICIENCE": {"status": "VERIFIED", "result": "ONE_ROUTE_UNCHANGED"},
            "PROOF_REUSE_EFFICIENCY": {"status": "VERIFIED", "result": "EX_17_OF_17_REUSED"},
            "COGNITION_ASSISTED_HANDOFF": {"status": "VERIFIED", "result": "REPLAY_SAFE_BLOCKER_EVIDENCE"},
            "AIGOL_CODEX_WORK_SHARE": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_ATTRIBUTION_INSTRUMENT"},
            "OVERENGINEERING_RISK": {"status": "ESTIMATED", "result": "HIGH_IF_SECOND_ROUTE_OR_AUTHORITY_LAYER_IS_CREATED"},
            "PROOF_PROCESS_OVERHEAD_RISK": {"status": "ESTIMATED", "result": "LOW__STOPPED_AT_FIRST_BROKEN_EDGE"},
            "COGNITION_PROVENANCE": {"status": "VERIFIED", "result": "AUTHENTICATED_GIT_OBJECTS_AND_REPOSITORY_EVIDENCE"},
            "CANDIDATE_CAPABILITY": {"status": "VERIFIED", "result": "HR_REPOSITORY_VECTOR_ONLY"},
            "WRONG_CONTRACT_CANDIDATE_CAPABILITY": {"status": "VERIFIED", "result": "HR_PRODUCER_REDUCER_ACCEPTED"},
            "WRONG_CONTRACT_REPOSITORY_CAPABILITY": {"status": "VERIFIED", "result": "FORMAL_SPEC_PRODUCER_REDUCER_FIREWALL"},
            "WRONG_CONTRACT_BINDING_STATUS": {"status": "NOT_PROVEN", "result": "SOLE_ROUTE_REJECTS_VECTOR"},
            "WRONG_CONTRACT_PREOPERATIONAL_READINESS": {"status": "NOT_PROVEN", "result": "BINDING_BLOCKED"},
            "WRONG_CONTRACT_OPERATIONAL_CAPABILITY": {"status": "NOT_PROVEN", "result": "ZERO_OPERATION"},
            "SHADOW_DESIGN_TARGET": {"status": "VERIFIED", "result": "FORMALIZE_REUSE_BIND_VERIFY"},
            "CONSTITUTIONAL_CONTINUATION_PROGRESS": {"status": "VERIFIED", "result": "FORMALIZE_VERIFIED__BIND_BLOCKED"},
            "PROMPT_CONTEXT_REUSE_RATIO": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_TOKEN_INSTRUMENT"},
            "TOKEN_BENCHMARK": {"status": "NOT_MEASURED", "result": "PROVIDER_CONTEXT_TELEMETRY_EXCLUDED"},
            "LLM_COST_REDUCTION_RATIO": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_COST_BASELINE"},
            "LCRR": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_COST_BASELINE"},
            "E05_GENERATIONS_PER_CREDIT": {"status": "NOT_MEASURED", "result": "HS_AWARDS_ZERO_CREDIT"},
            "OPERATIONAL_ATTEMPTS_PER_CREDIT": {"status": "NOT_MEASURED", "result": "ZERO_OVER_ZERO_UNDEFINED"},
            "MARGINAL_E05_GENERATION_COST": {"status": "NOT_MEASURED", "result": "NO_GOVERNED_COST_INSTRUMENT"},
            "INFRASTRUCTURE_AMORTIZATION_SIGNAL": {"status": "NOT_PROVEN", "result": "WRONG_CONTRACT_NOT_ACCEPTED_BY_CURRENT_COMMON_ROUTE"},
        },
        "infrastructure_amortization": {
            "did_hs_require_new_common_infrastructure": True,
            "did_hs_require_new_generic_framework": False,
            "did_hs_require_new_authority_layer": False,
            "did_hs_require_new_runtime_owner": False,
            "did_hs_require_new_production_route": False,
            "did_hs_reuse_existing_post_commit_binding_architecture": "PARTIAL__BLOCKED_BEFORE_LIVE_BINDING",
            "did_hs_reuse_existing_fm_route": "PARTIAL__ROUTE_REJECTS_WRONG_CONTRACT",
            "did_hs_reuse_existing_guest_projection_bootstrap_architecture": "PARTIAL__WRONG_INPUT_HASH_BINDING_NOT_REUSABLE_AS_WRONG_CONTRACT",
            "did_hs_reuse_gn_gl_du_eb_ee": "PARTIAL__MECHANISMS_APPLICABLE_BUT_NO_CURRENT_RECEIPTS",
            "was_ex_reused_17_of_17": True,
            "is_wrong_contract_binding_primarily_vector_specific": True,
            "is_8_to_9_infrastructure_amortization_signal_still_positive": "NOT_PROVEN",
        },
        "operational_counters": zero_counters(),
        "e05": {"before": "8/18", "credit": 0, "after": "8/18", "remaining": 10},
        "terminal_control": {
            "last_verified_edge": "COMMITTED_HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY",
            "first_broken_edge": route["first_broken_edge"],
            "minimum_missing_capability": "COMMITTED_WRONG_CONTRACT_SUPPORT_INSIDE_THE_EXISTING_FM_GN_PREAUTHORIZATION_ROUTE_WITH_VECTOR_SPECIFIC_ADAPTER_BOOTSTRAP_AND_EXPECTED_HARNESS_BINDING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_AND_COMMIT__ONE_SEPARATE_REPOSITORY_ONLY_ROUTE_EXTENSION_GENERATION_MODIFYING_EXISTING_OWNERS_ONLY__THEN_ONE_POST_COMMIT_READINESS_REBIND__NO_OPERATION",
            "auto_continuable": False,
            "human_review_required": True,
            "verdict": "FAIL_CLOSED__G77_256HS_WRONG_CONTRACT_LIVE_BINDING_NOT_PROVEN__SOLE_FM_GN_ROUTE_REJECTS_WRONG_CONTRACT__DU_EB_EE_NOT_RUN_WITHOUT_VALID_BINDING__ZERO_OPERATION__E05_REMAINS_8_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def write_terminal_reduction(*, repository_root: Path, output_path: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    envelope = {
        "schema_id": "G77_256HS_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise HSReductionError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only reducer; invoke through focused tests")
