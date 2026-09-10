#!/usr/bin/env python3
"""Reduce JX's ER admission/runtime-checkout role repair repository-only."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "e8346d2700fa459de546dde961e108706749581b"
ENTRY_TREE = "4bb2d25086390f49d3577500c650891e9ca4a652"
ENTRY_SUBJECT = "G77-256JW localize EXPIRED ER checkout role identity blocker"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
ADMISSION_HEAD = "98206cab55fb4201c3b60de48eb032cca196de7c"
ADMISSION_TREE = "ab1a39d41553fc0296e65287782a36b1f20fb22b"

JX = Path(
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1"
)
JW = Path(".github/governance/evidence/g77_256jw_expired_operational_v1")
JW_REDUCTION = JW / "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
JW_CONTEXT = JW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
OWNER = FM.with_name("sapianta_fresh_operation_context_v1.py")
ER = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
CLOUD = JX / "static/G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = JX / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img"
META = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK = META.with_name("G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml")
P11 = Path("tests/p11_da_operational_consumer_v1.py")
REPORT = JX / "G77_256JX_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JX / "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

ER_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
ADAPTER_BEFORE_SHA256 = "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
ADAPTER_AFTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
FM_AFTER_SHA256 = "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469"
CLOUD_SHA256 = "d427ea791a6a34412af12f6fb4b8f6d6597db120d037bd13e99c9cb64f52f859"
SEED_SHA256 = "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
TERMINAL = (
    "A__ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_"
    "REPOSITORY_VERIFIED"
)


class JXError(RuntimeError):
    """One fail-closed JX repository verification error."""


def fail(token: str) -> None:
    raise JXError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, ROOT / path)
    if specification is None or specification.loader is None:
        fail(f"MODULE_UNAVAILABLE__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_envelope(path: Path, inner: str, digest: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_bytes())
    body = value.get(inner)
    if not isinstance(body, dict) or value.get(digest) != hashlib.sha256(
        canonical_bytes(body)
    ).hexdigest():
        fail(f"INNER_SEAL_INVALID__{path.name}")
    return body


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    if observed != {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
        "index_empty": True,
    }:
        fail("EXACT_JW_ENTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--exact-match", "--tags", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return {
        **observed,
        "remote_head": ENTRY_HEAD,
        "direct_remote_equality": "VERIFIED__READ_ONLY_LS_REMOTE_AT_ENTRY",
        "entry_worktree_clean": True,
        "entry_index_empty": True,
        "nested_authority": nested_state,
        "nested_remote_tag_equality": "VERIFIED__READ_ONLY_LS_REMOTE_AT_ENTRY",
    }


def reconstruct_jw() -> dict[str, Any]:
    if subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{JW_REDUCTION}"], cwd=ROOT
    ) != (ROOT / JW_REDUCTION).read_bytes():
        fail("JW_REDUCTION_NOT_COMMITTED_EXACT_BYTES")
    jw = load_envelope(JW_REDUCTION, "reduction", "reduction_sha256")
    counters = jw.get("operational_counters", {})
    expected = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
        "expired_check_count": 0,
        "request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    role = jw.get("role_mismatch", {})
    if (
        jw.get("terminal")
        != "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_ER_CONTEXT_CHECKOUT_ROLE_IDENTITY_COLLAPSE_BEFORE_EXPIRED_CHECK"
        or any(counters.get(key) != value for key, value in expected.items())
        or role.get("admission_repository")
        != {"head": ADMISSION_HEAD, "tree": ADMISSION_TREE}
        or role.get("stable_runtime_checkout")
        != {"head": JR_HEAD, "tree": JR_TREE}
        or role.get("differing_sealed_fields")
        != ["repository_head", "repository_tree"]
        or jw["e05"]
        != {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        }
        or jw["reuse"]["ex_reused"] != "VERIFIED__17_OF_17"
        or jw["reuse"]["ex_reconstructed"] != "VERIFIED__0"
    ):
        fail("JW_TERMINAL_OR_COUNTERS_MISMATCH")
    context = json.loads((ROOT / JW_CONTEXT).read_bytes())
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if (context["repository_head"], context["repository_tree"]) != (
        ADMISSION_HEAD,
        ADMISSION_TREE,
    ) or (checkout["head"], checkout["tree"]) != (JR_HEAD, JR_TREE):
        fail("JW_EXACT_ROLE_MISMATCH_NOT_RECONSTRUCTED")
    return {
        "terminal": jw["terminal"],
        "exact_failure": jw["operation"]["exact_failure"],
        "historical_operational_counters": {
            key: f"VERIFIED__{value}" for key, value in expected.items()
        },
        "admission_repository": role["admission_repository"],
        "stable_runtime_checkout": role["stable_runtime_checkout"],
        "differing_fields": role["differing_sealed_fields"],
        "authority_state": "VERIFIED__HISTORICAL_CONSUMED_NONREUSABLE",
    }


def verify_solution() -> dict[str, Any]:
    expected_hashes = {
        ADAPTER: ADAPTER_AFTER_SHA256,
        FM: FM_AFTER_SHA256,
        ER: ER_SHA256,
        CLOUD: CLOUD_SHA256,
        SEED: SEED_SHA256,
        P11: P11_SHA256,
    }
    for path, expected in expected_hashes.items():
        if sha256(path) != expected:
            fail(f"IMPLEMENTATION_HASH_MISMATCH__{path.name}")
    committed_adapter = subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{ADAPTER}"], cwd=ROOT
    )
    if hashlib.sha256(committed_adapter).hexdigest() != ADAPTER_BEFORE_SHA256:
        fail("ADAPTER_ENTRY_BYTES_MISMATCH")

    fm = load_module(FM, "g77_256jx_formalizer_fm")
    adapter = load_module(ADAPTER, "g77_256jx_formalizer_adapter")
    with tempfile.TemporaryDirectory(prefix="g77_256jx_repository_only_") as temporary:
        root = Path(temporary)
        context = fm.build_operation_context(
            repository_root=ROOT,
            repository_head=ENTRY_HEAD,
            repository_tree=ENTRY_TREE,
            generation_identity=(
                "G77_256JX_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_"
                "OPERATIONAL_COMMISSIONING_V1"
            ),
            operation_identity="G77_256JX_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001",
            identity_namespace_prefix="G77_256JX",
            operation_evidence_root=root / "operation_state",
            transient_root=root / "transient",
        )
        fm.validate_immutable_context_bindings(ROOT, context)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if (
        (context["repository_head"], context["repository_tree"])
        != (ENTRY_HEAD, ENTRY_TREE)
        or (checkout["head"], checkout["tree"]) != (JR_HEAD, JR_TREE)
    ):
        fail("ROLE_SEPARATION_OUTPUT_MISMATCH")

    specialized = adapter.specialize_er_harness(ROOT)
    if (
        "repository_head"
        in specialized.load_authenticated_fresh_operation_context.__code__.co_consts
        or "repository_tree"
        in specialized.load_authenticated_fresh_operation_context.__code__.co_consts
        or "head"
        not in specialized.load_authenticated_fresh_operation_context.__code__.co_consts
        or "tree"
        not in specialized.load_authenticated_fresh_operation_context.__code__.co_consts
    ):
        fail("SPECIALIZED_ER_ROLE_COMPARISON_MISMATCH")
    if not {500, 100, 1000}.issubset(
        set(specialized.create_input_and_authority.__code__.co_consts)
    ):
        fail("EXPIRED_TEMPORAL_CONTRACT_CHANGED")

    command = fm.bootstrap_guest_command_arguments(
        (ROOT / CLOUD).read_text(encoding="utf-8"),
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
    )
    expected_command = (
        ADAPTER_AFTER_SHA256,
        "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        JR_HEAD,
        JR_TREE,
        "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
    )
    if command != expected_command:
        fail("JX_BOOTSTRAP_COMMAND_MISMATCH")
    for member, source in (
        ("/user-data", CLOUD),
        ("/meta-data", META),
        ("/network-config", NETWORK),
    ):
        if subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        ) != (ROOT / source).read_bytes():
            fail(f"JX_SEED_PROJECTION_MISMATCH__{member}")
    if fm.governed_checkout_identity(ROOT, "EXPIRED", ENTRY_HEAD, ENTRY_TREE) != (
        JR_HEAD,
        JR_TREE,
    ):
        fail("JT_STABLE_JR_CHECKOUT_REGRESSED")

    fm_tree = ast.parse((ROOT / FM).read_text(encoding="utf-8"))
    route_count = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
        for node in fm_tree.body
    )
    if route_count != 1:
        fail("PRODUCTION_ROUTE_COUNT_CHANGED")
    return {
        "authenticated_contract": "A_AND_C__EXISTING_FM_JT_ROLE_SEPARATION__ER_EXPIRED_SPECIALIZATION_WAS_STALE",
        "admission_repository_owner": "EXISTING_FM_FINAL_ADMISSION_AND_CONTEXT_SEAL_OWNER",
        "runtime_checkout_owner": "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER",
        "admission_repository": {"head": ENTRY_HEAD, "tree": ENTRY_TREE},
        "runtime_checkout": {"head": JR_HEAD, "tree": JR_TREE},
        "distinct_valid_roles_accepted": "VERIFIED__REPOSITORY_ONLY",
        "admission_corruption": "VERIFIED__HOST_ADMISSION_FAIL_CLOSED",
        "runtime_corruption": "VERIFIED__ER_AND_FM_FAIL_CLOSED",
        "unsealed_substitution": "VERIFIED__CONTEXT_SEAL_FAIL_CLOSED",
        "caller_provider_substitution": "VERIFIED__HOST_ADMISSION_AND_IMMUTABLE_BINDING_FAIL_CLOSED",
        "role_swap": "VERIFIED__FAIL_CLOSED",
        "missing_binding": "VERIFIED__FAIL_CLOSED",
        "historical_equal_role_compatibility": "VERIFIED__WHERE_APPLICABLE",
        "stable_jr_checkout": "VERIFIED__PRESERVED",
        "temporal_truth_table": {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"},
        "validity_interval": "valid_from <= preclaim < valid_until",
        "bootstrap_command": list(command),
        "route_count": route_count,
    }


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    jw = reconstruct_jw()
    solution = verify_solution()
    counters = {
        key: "VERIFIED__0"
        for key in (
            "operational_authorization_count",
            "authority_consumption_count",
            "pre_operational_count",
            "fm_operational_invocation_count",
            "qemu_count",
            "vm_count",
            "operation_attempt_count",
            "request_count",
            "p11_entry_count",
            "protected_invocation_count",
            "protected_effect_count",
            "retry_count",
            "repair_retry_count",
            "replay_count",
        )
    }
    return {
        "schema_id": "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JX",
        "mode": "REPOSITORY_ONLY__NO_HUMAN_AUTHORITY__NO_OPERATION",
        "terminal": TERMINAL,
        "continuation": {
            "recovery_type": "SAME_GENERATION_SAME_ACCOUNT_PROVIDER_LIMIT_CONTINUATION",
            "recovery_source_generation": "G77-256JX",
            "new_generation_created": "VERIFIED__NO",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
            "continuation_entry_index": "VERIFIED__EMPTY",
            "continuation_entry_diff_check": "VERIFIED__PASS",
            "continuation_entry_file_count": "VERIFIED__8__TWO_TRACKED_PRODUCTION_AND_SIX_JX_ARTIFACTS",
            "continuation_entry_sha256": {
                FM.as_posix(): "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469",
                ADAPTER.as_posix(): "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
                REPORT.as_posix(): "23ea626234046e4564826ff0024e9a7e5555bc5bbee7912ef1526601a5e529e2",
                REDUCTION.as_posix(): "00a8bcee7c0dd12f9e650c34e36178e899fb88c23d33d54bd541aed7981708c7",
                (JX / "analysis/G77_256JX_ER_ROLE_SEPARATION_FORMALIZER_V1.py").as_posix(): "f32cb88d8c67cbc5c2b8c976cce92205848ef31310887d8bba3db04d15866abb",
                CLOUD.as_posix(): CLOUD_SHA256,
                SEED.as_posix(): SEED_SHA256,
                (JX / "tests/test_g77_256jx_er_role_separation_v1.py").as_posix(): "8d511266c896eaede91e3de73ac1a08263b213a91a52caaf474c7bc05005b0bf",
            },
        },
        "entry": entry,
        "jw_reconstruction": jw,
        "role_separation": solution,
        "implementation": {
            "modified_files": [ADAPTER.as_posix(), FM.as_posix()],
            "created_production_assets": [CLOUD.as_posix(), SEED.as_posix()],
            "er_base_sha256": ER_SHA256,
            "er_base_mutated": False,
            "er_runtime_specialization_mutation_count": "VERIFIED__1",
            "adapter_before_sha256": ADAPTER_BEFORE_SHA256,
            "adapter_after_sha256": ADAPTER_AFTER_SHA256,
            "fm_after_sha256": FM_AFTER_SHA256,
            "cloud_sha256": CLOUD_SHA256,
            "seed_sha256": SEED_SHA256,
            "selected_delta": "EXISTING_EXPIRED_ADAPTER_EXACT_ER_ROLE_SPECIALIZATION_PLUS_FAMILY_LOCAL_BOOTSTRAP_REBIND",
        },
        "architecture": {
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__4",
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "operational_counters": counters,
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": "EX_17_OF_17__JL__JM__JN__JO__JP__JQ__JR__JS__JT__JU__JV__JW__FM__FC__ER__GN__P11",
            "new_capabilities": "VERIFIED__ONE__ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_REPOSITORY_ONLY",
            "existing_capability_became_unreachable": "VERIFIED__NO",
            "parallel_flow_created": "VERIFIED__NO",
            "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1",
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "metrics": {
            "project_progress": "VERIFIED__JX_ER_DISTINCT_ROLE_VALIDATION_REPOSITORY_ONLY",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ER_ROLE_BLOCKER_CLOSED__FRESH_OPERATIONAL_REPROOF_REMAINS",
            "constitutional_health_evidence": "VERIFIED__INDEPENDENT_SEALED_ROLES_FAIL_CLOSED_SINGLE_ROUTE_ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EXISTING_OWNERS_ER_ROUTE_AND_EX_REUSED",
            "overengineering_risk": "ESTIMATED__LOW__FAMILY_LOCAL_DELIVERY_DELTA_ONLY",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_SAME_ACCOUNT_PROVIDER_LIMIT_CONTINUATION",
            "candidate_capability": "VERIFIED__ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_REPOSITORY_ONLY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__JW_BLOCKER_TO_JX_REPOSITORY_REPAIR",
        },
        "human_authority_assurance_status": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": "ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_REPOSITORY_VERIFIED",
            "first_broken_edge": "FRESH_EXPIRED_OPERATIONAL_COMMISSIONING_NOT_YET_REPROVEN_AFTER_ER_REPAIR",
            "minimum_missing_capability": "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_GENERATION",
        },
        "validation": {
            "jx_focused": "VERIFIED__14_PASSED",
            "jw_reconstruction": "VERIFIED__COMMITTED_EXACT_BYTES_AND_COUNTERS",
            "supporting_regression": "VERIFIED__148_PASSED",
            "historical_state_bound_classification": "VERIFIED__37_EXPECTED_CURRENT_STATE_FAILURES__ENTRY_HASH_DELTA_SCOPE_OR_GENERATION_SYNTHETIC_IDENTITY_BOUND",
            "ex_reuse": "VERIFIED__HISTORICAL_CERTIFICATE_17_COMPONENTS__12_OF_12_REGRESSIONS_PASS__0_OPERATION__0_CREDIT",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "g48_h1_count": "VERIFIED__6",
            "reuse_question_count": "VERIFIED__5_EXACT",
            "git_diff_check": "VERIFIED__PASS",
            "final_index": "VERIFIED__EMPTY",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    (ROOT / REDUCTION).write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    write_reduction()
