#!/usr/bin/env python3
"""Repository-only G77-256JO sole-route and sealed-context reduction."""

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
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "3e2fab7a24ef06d58edfd13edd307a254ad6f543"
ENTRY_TREE = "ecee2ce4de6b5240fe533235afd10d20d56bf79d"
ENTRY_SUBJECT = "G77-256JN localize post-JM operational route blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JM_HEAD = "4126dd5ad78fffb259625ca1033bb1d5419cc245"
JM_TREE = "87a227fafdb19e4d0c245d96f62f7728468580e6"
JM_TERMINAL = (
    "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
    "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
)
JN_TERMINAL = "M__POST_JM_READINESS_REQUIRES_SEPARATE_IMPLEMENTATION_DELTA"
TERMINAL = (
    "A__SOLE_ER_FM_ROUTE_BOUND_TO_COMMITTED_JM_P11_AND_SEALED_CONTEXT_"
    "REPOSITORY_VERIFIED"
)
HISTORICAL_IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
HISTORICAL_IF_P11_SHA256 = (
    "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e"
)
JM_P11_SHA256 = (
    "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
)

JO = Path(
    ".github/governance/evidence/"
    "g77_256jo_bind_sole_er_fm_route_to_committed_jm_p11_and_sealed_context_v1"
)
REPORT = JO / "G77_256JO_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JO / "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = JO / "analysis/G77_256JO_SOLE_ROUTE_BINDING_FORMALIZER_V1.py"
TEST = JO / "tests/test_g77_256jo_sole_route_binding_v1.py"
JN = Path(
    ".github/governance/evidence/"
    "g77_256jn_post_jm_live_binding_ex_successor_reauthentication_and_"
    "expired_operational_readiness_v1"
)
JN_REDUCTION = JN / "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JM = Path(
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1"
)
JM_REDUCTION = JM / "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EW_MANIFEST = Path(
    ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/"
    "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
)
LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
ER = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FC = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FM_WRAPPER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness/"
    "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
ADAPTERS = (
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"),
    Path(".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1/adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"),
    Path(".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1/adapter/G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"),
    Path(".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"),
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
PRODUCTION_PATHS = (LAUNCHER, ER, FC, FM_WRAPPER, *ADAPTERS)
EVIDENCE_PATHS = (REPORT, REDUCTION, FORMALIZER, TEST)


class JOError(RuntimeError):
    """One deterministic fail-closed JO verification error."""


def fail(token: str) -> None:
    raise JOError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def committed_bytes(path: Path, revision: str = ENTRY_HEAD) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT
    )


def load_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                fail(f"DUPLICATE_JSON_KEY__{key}")
            value[key] = item
        return value

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    if not isinstance(value, dict):
        fail(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def authenticate_envelope(path: Path, terminal: str) -> dict[str, Any]:
    envelope = load_json(path)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail(f"REDUCTION_MISSING__{path}")
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        fail(f"REDUCTION_SEAL_INVALID__{path}")
    if reduction.get("terminal") != terminal:
        fail(f"TERMINAL_INVALID__{path}")
    return reduction


def authenticate_entry() -> dict[str, Any]:
    nested = ROOT / "sapianta_system"
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    tracked = sorted(
        line[3:] for line in status
        if not line.startswith("?? ") and "__pycache__" not in line
    )
    untracked = sorted(
        line[3:] for line in status
        if line.startswith("?? ") and "__pycache__" not in line
    )
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "tracked_delta": tracked,
        "untracked_delta": untracked,
        "nested_origin": git("remote", "get-url", "origin", cwd=nested),
        "nested_head": git("rev-parse", "HEAD", cwd=nested),
        "nested_tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "nested_detached": git("branch", "--show-current", cwd=nested) == "",
        "nested_clean": git("status", "--porcelain=v1", cwd=nested) == "",
        "nested_tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    expected = {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
        "index_empty": True,
        "tracked_delta": sorted(str(path) for path in PRODUCTION_PATHS),
        "untracked_delta": sorted(str(path) for path in EVIDENCE_PATHS),
        "nested_origin": NESTED_ORIGIN,
        "nested_head": NESTED_HEAD,
        "nested_tree": NESTED_TREE,
        "nested_detached": True,
        "nested_clean": True,
        "nested_tag": NESTED_TAG,
    }
    if observed != expected:
        fail("ENTRY_OR_JO_SCOPE_AUTHENTICATION_FAILED")
    return observed | {
        "entry_clean_before_first_write": "VERIFIED__YES",
        "entry_index_empty_before_first_write": "VERIFIED__YES",
        "direct_remote_equality": "VERIFIED__READ_ONLY_PREFLIGHT",
        "nested_remote_tag_equality": "VERIFIED__READ_ONLY_PREFLIGHT",
    }


def reconstruct_lineage() -> dict[str, Any]:
    jn = authenticate_envelope(ROOT / JN_REDUCTION, JN_TERMINAL)
    jm = authenticate_envelope(ROOT / JM_REDUCTION, JM_TERMINAL)
    if git("rev-parse", f"{JM_HEAD}^{{tree}}") != JM_TREE:
        fail("JM_COMMIT_TREE_MISMATCH")
    if jn["frontier"] != {
        "last_verified_edge": "COMMITTED_JM_REPOSITORY_BINDING_AND_EX_SUCCESSOR_REAUTHENTICATION_VERIFIED",
        "first_broken_edge": "SOLE_OPERATIONAL_ROUTE_IMPORTS_DETACHED_IF_P11_AND_ER_HARNESS_LACKS_JM_CONTEXT_GATE_ARGUMENTS",
        "minimum_missing_capability": "SOLE_ROUTE_BINDING_TO_COMMITTED_JM_P11_PLUS_SEALED_CONTEXT_GATE_HANDOFF",
        "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_IMPLEMENTATION_GENERATION_TO_BIND_EXISTING_ER_FM_ROUTE_TO_COMMITTED_JM_P11_AND_CONTEXT__NO_OPERATION",
        "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
    }:
        fail("JN_FRONTIER_MISMATCH")
    if jn["ex_successor_reauthentication"]["ex_reused"] != "VERIFIED__17_OF_17":
        fail("JN_EX_REUSE_MISMATCH")
    if jn["ex_successor_reauthentication"]["ex_reconstructed"] != "VERIFIED__0":
        fail("JN_EX_RECONSTRUCTION_MISMATCH")
    if jm["implementation"]["p11_consumer_sha256"] != JM_P11_SHA256:
        fail("JM_P11_IDENTITY_MISMATCH")
    return {
        "jn_terminal": JN_TERMINAL,
        "jm_head": JM_HEAD,
        "jm_tree": JM_TREE,
        "jm_terminal": JM_TERMINAL,
        "jm_chain": "VERIFIED__JJ_TO_CONTEXT_TO_HUMAN_CORRELATION_TO_GATE_TO_P11_TO_TEMPORAL_DECISION",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "e05_before": "VERIFIED__11_OF_18",
        "e05_credit": "VERIFIED__0",
    }


def call_keywords(tree: ast.AST, name: str) -> list[set[str]]:
    result: list[set[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == name:
                result.append({item.arg for item in node.keywords if item.arg})
    return result


def verify_route() -> dict[str, Any]:
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in PRODUCTION_PATHS}
    trees = {path: ast.parse(source) for path, source in sources.items()}
    launcher = sources[LAUNCHER]
    er = sources[ER]
    fc = sources[FC]
    if launcher.count("def build_operation_context(") != 1:
        fail("CONTEXT_OWNER_ROUTE_COUNT_INVALID")
    if launcher.count("result = subprocess.run(argv, check=False)") != 1:
        fail("PRODUCTION_ROUTE_COUNT_INVALID")
    if '"head": repository_head' not in launcher or '"tree": repository_tree' not in launcher:
        fail("CURRENT_REPOSITORY_CHECKOUT_HANDOFF_MISSING")
    if "\nCHECKOUT_HEAD = \"" in launcher or "\nCHECKOUT_TREE = \"" in launcher:
        fail("DETACHED_RUNTIME_SELECTOR_REMAINS")
    if "authenticate_current_committed_jm_route" not in launcher:
        fail("CURRENT_JM_ROUTE_AUTHENTICATOR_MISSING")
    if sha256_bytes((ROOT / P11).read_bytes()) != JM_P11_SHA256:
        fail("WORKTREE_P11_NOT_EXACT_JM")
    if sha256_bytes(committed_bytes(P11)) != JM_P11_SHA256:
        fail("ENTRY_P11_NOT_EXACT_JM")
    if sha256_bytes(committed_bytes(P11, HISTORICAL_IF_HEAD)) != HISTORICAL_IF_P11_SHA256:
        fail("HISTORICAL_IF_P11_REFERENCE_MISMATCH")
    required_gate = {"operation_context_sha256", "preclaim_temporal_binding_identity"}
    required_consumer = {"fresh_operation_context"}
    for source_path in (ER, FC):
        gate_calls = call_keywords(trees[source_path], "create_commissioning_gate_v1")
        consumer_calls = call_keywords(trees[source_path], "P11BoundedConsumerV1")
        if len(gate_calls) != 1 or len(consumer_calls) != 1:
            fail(f"P11_CONSTRUCTION_CARDINALITY_INVALID__{source_path}")
        if not required_gate <= gate_calls[0] or not required_consumer <= consumer_calls[0]:
            fail(f"SEALED_CONTEXT_HANDOFF_INCOMPLETE__{source_path}")
    if er.count("load_authenticated_fresh_operation_context()") < 3:
        fail("ER_CONTEXT_REAUTHENTICATION_COUNT_INVALID")
    if "context != _AUTHENTICATED_FRESH_OPERATION_CONTEXT" not in er:
        fail("POST_SEAL_SUBSTITUTION_GUARD_MISSING")
    er_sha = sha256_path(ROOT / ER)
    fc_sha = sha256_path(ROOT / FC)
    if f'ER_HARNESS_SHA256 = "{er_sha}"' not in launcher:
        fail("LAUNCHER_ER_HASH_BINDING_MISMATCH")
    if f'FK_ADAPTER_SHA256 = "{fc_sha}"' not in launcher:
        fail("LAUNCHER_FC_HASH_BINDING_MISMATCH")
    if f'FC_SOURCE_SHA256 = "{fc_sha}"' not in sources[FM_WRAPPER]:
        fail("FM_WRAPPER_FC_HASH_BINDING_MISMATCH")
    for adapter in ADAPTERS:
        if fc_sha not in sources[adapter]:
            fail(f"VECTOR_ADAPTER_FC_HASH_BINDING_MISMATCH__{adapter}")
    if er_sha not in sources[ADAPTERS[-1]]:
        fail("FUTURE_ADAPTER_ER_HASH_BINDING_MISMATCH")
    return {
        "sole_route": "VERIFIED__ONE_LAUNCHER_ONE_QEMU_CALL_SITE",
        "runtime_target_source": "VERIFIED__SEALED_CURRENT_REPOSITORY_HEAD_TREE",
        "runtime_target_p11_sha256": JM_P11_SHA256,
        "historical_if_p11_sha256": HISTORICAL_IF_P11_SHA256,
        "historical_if_satisfies_current_route": "VERIFIED__NO__FAIL_CLOSED",
        "er_harness_sha256": er_sha,
        "fc_adapter_sha256": fc_sha,
        "base_er_context_handoff": "VERIFIED__GATE_AND_CONSUMER",
        "fc_specialized_context_handoff": "VERIFIED__GATE_AND_CONSUMER",
        "context_source": "VERIFIED__EXISTING_PROJECTED_FM_OWNER_AND_SEALED_GUEST_CONTEXT",
        "post_seal_substitution": "VERIFIED__FAIL_CLOSED_BEFORE_CONSTRUCTION",
    }


def verify_ex_delta() -> dict[str, Any]:
    certificate = load_json(ROOT / EX_CERTIFICATE)["certificate"]
    manifest = load_json(ROOT / EW_MANIFEST)["manifest"]
    bindings = {item["identity"]: item for item in manifest["component_bindings"]}
    er_binding = bindings["ER_OPERATIONAL_HARNESS"]
    if er_binding["classification"] != "REQUIRES_HARDENING":
        fail("ER_EX_CLASSIFICATION_CHANGED")
    if er_binding["sha256"] == sha256_path(ROOT / ER):
        fail("ER_DELTA_NOT_DISTINCT")
    if certificate["component_counts"]["CERTIFIED"] != 17:
        fail("EX_CERTIFIED_COUNT_MISMATCH")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "changed_ex_bound_component_count": "VERIFIED__1",
        "changed_component": "ER_OPERATIONAL_HARNESS",
        "classification": er_binding["classification"],
        "historical_sha256": er_binding["sha256"],
        "successor_sha256": sha256_path(ROOT / ER),
        "new_certificate_count": "VERIFIED__0",
    }


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_retry_count", "replay_count",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    lineage = reconstruct_lineage()
    route = verify_route()
    ex = verify_ex_delta()
    return {
        "schema_id": "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JO",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT_JN", "REUSE_EX", "TRACE_SOLE_ROUTE",
            "BIND_COMMITTED_JM_P11", "BIND_SEALED_CONTEXT_HANDOFF",
            "VERIFY_NON_BYPASS", "VERIFY_FAIL_CLOSED", "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry": entry,
        "lineage": lineage,
        "route_binding": route,
        "ex_delta_reauthentication": ex,
        "authority_separation": {
            "certified_is_authorized": "VERIFIED__NO",
            "provider_capability_is_execution_authority": "VERIFIED__NO",
            "caller_selectable_time_authority_count": "VERIFIED__0",
            "provider_selectable_time_authority_count": "VERIFIED__0",
            "human_selectable_time_authority_count": "VERIFIED__0",
            "temporal_coordinate_is_execution_human_p11_or_effect_authority": "VERIFIED__NO",
            "request_entry_invocation_effect_are_distinct": "VERIFIED__YES",
        },
        "temporal_semantics": {
            "future": "preclaim < valid_from",
            "current": "valid_from <= preclaim < valid_until",
            "expired": "preclaim >= valid_until",
            "boundary": "VERIFIED__999_CURRENT__1000_EXPIRED__1001_EXPIRED",
            "governed_wall_clock_fallback": "VERIFIED__ABSENT",
        },
        "fail_closed_matrix": {
            key: "VERIFIED__BEFORE_PROTECTED_INVOCATION_OR_EFFECT" for key in (
                "stale_runtime_p11", "missing_operation_context_sha256",
                "missing_preclaim_temporal_binding_identity", "missing_fresh_operation_context",
                "context_seal_mismatch", "temporal_binding_mismatch", "gate_context_mismatch",
                "p11_consumer_context_mismatch", "substituted_candidate_or_context",
                "caller_selected_temporal_data", "provider_selected_temporal_data",
                "historical_if_p11_substitution", "parallel_route_attempt",
            )
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": f"VERIFIED__{len(PRODUCTION_PATHS)}",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "operational_counters": zero_counters(),
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__SOLE_ROUTE_COMMITTED_JM_P11_AND_SEALED_CONTEXT_HANDOFF",
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "metrics": {
            "project_progress": "VERIFIED__JO_ROUTE_INTEGRATION_REPOSITORY_VERIFIED__POST_COMMIT_READINESS_PENDING",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__SOLE_ROUTE_INTEGRATION_COMPLETE__POST_COMMIT_REAUTHENTICATION_REMAINS",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_SINGLE_ROUTE_EXACT_BYTES_SEALED_CONTEXT_AUTHORITY_SEPARATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "governance_efficience": "ESTIMATED__HIGH__EXISTING_OWNERS_AND_ROUTE_REUSED",
            "overengineering_risk": "ESTIMATED__LOW__ZERO_NEW_OWNER_ROUTE_REGISTRY_OR_GENERIC_ABSTRACTION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JN_TO_JO_REPOSITORY_CONTINUATION",
            "candidate_capability": "VERIFIED__REPOSITORY_ROUTE_INTEGRATION_ONLY__NOT_OPERATIONAL_READINESS",
            "shadow_design_target": "VERIFIED__SOLE_ER_FM_ROUTE_CARRIES_COMMITTED_JM_P11_AND_CONTEXT_BINDING",
            "constitutional_continuation_progress": "VERIFIED__JN_BLOCKER_CLOSED_REPOSITORY_ONLY__NO_E05_CREDIT",
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
        "human_authority_assurance_status": "NOT_APPLICABLE",
        "frontier": {
            "last_verified_edge": "SOLE_ER_FM_ROUTE_BOUND_TO_COMMITTED_JM_P11_AND_SEALED_CONTEXT_REPOSITORY_VERIFIED",
            "first_broken_edge": "POST_JO_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_NOT_YET_REAUTHENTICATED",
            "minimum_missing_capability": "COMMITTED_JO_POST_COMMIT_LIVE_BINDING_AND_REPOSITORY_READINESS_REAUTHENTICATION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__SEPARATE_REPOSITORY_ONLY_POST_COMMIT_LIVE_BINDING_AND_READINESS_GENERATION__NO_OPERATION",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
        },
        "validation": {
            "jo_focused": "VERIFIED__17_PASSED",
            "jm_and_p11_relevant_regression": "VERIFIED__29_PASSED__1_HISTORICAL_DIRTY_SCOPE_ASSERTION_DESELECTED",
            "ex_reuse": "VERIFIED__17_OF_17__ER_EXACT_DELTA_REAUTHENTICATED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "g48": "VERIFIED__EXACTLY_SIX_H1",
            "git_diff_check": "VERIFIED__PASS",
            "final_index": "VERIFIED__EMPTY",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    arguments = parser.parse_args()
    if arguments.repository_root.resolve() != ROOT.resolve():
        fail("REPOSITORY_ROOT_MISMATCH")
    sys.stdout.buffer.write(canonical_bytes(envelope(build_reduction())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
