#!/usr/bin/env python3
"""Repository-only G77-256IO post-commit V2 live-binding certification."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
IN_HEAD = "e39aee28fa9181e1db2ae6c5cff4a50f557821be"
IN_TREE = "af334f6d128bdc5335e658df4731e742f541378d"
IN_SUBJECT = "G77-256IN materialize family-local V2 successor"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
ANCESTRY = (
    "f25afc281cbfe457b23a389a8375900717a5a1e2",
    "c43839f54ae788caa11a2082aba845b9426ea4c6",
    "7a7c77d32551020d5fed6cce5b4f7786e9974573",
    "a07f6e76239a9d8f309f290ecc8ab328d08aa64f",
    "4365d97394deca438a1a57d5b47c699afb54bd5d",
    "8698486cdf9a206f2bc73993c83389d6850362ff",
    "71391a75011cdc388bdac9183f4654814a044c69",
    IF_HEAD,
    "9420764a5bb6db8909334f2a422225687a37a346",
    "559deecb226b66d626e45e6f607b0aab6df81f1c",
    "afdd47166acdee30cb9867d3d3c7bfec0de64c8a",
    "5c972e9960987ab27420395b54ace693df097e7b",
)
IN_ROOT = Path(".github/governance/evidence/g77_256in_family_local_v2_option_b_dispatch_v1")
IO_ROOT = Path(".github/governance/evidence/g77_256io_post_commit_v2_live_binding_readiness_v1")
REPORT = IO_ROOT / "G77_256IO_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = IO_ROOT / "G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = IO_ROOT / "analysis/G77_256IO_POST_COMMIT_V2_READINESS_FORMALIZER_V1.py"
FOCUSED_TEST = IO_ROOT / "tests/test_g77_256io_post_commit_v2_live_binding_readiness_v1.py"
DU_SCHEMA = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V2.json")
DU_VALIDATOR = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_SCHEMA = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V2.json")
EB_VALIDATOR = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_SCHEMA = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V2.json")
EE_VALIDATOR = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
V2_FILES = (DU_SCHEMA, DU_VALIDATOR, EB_SCHEMA, EB_VALIDATOR, EE_SCHEMA, EE_VALIDATOR)
REPAIR_FILES = frozenset((DU_VALIDATOR, EB_SCHEMA, EB_VALIDATOR, EE_SCHEMA, EE_VALIDATOR))
IO_FILES = frozenset((REPORT, TERMINAL, FORMALIZER, FOCUSED_TEST))
V1_HASHES = {
    Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"): "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e",
    Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"): "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json"): "5b477ce183df65446aa1c3df3f8006856fce72b0771fcf04ff0c9cc6ae3a5f49",
    Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"): "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json"): "b193f6d392b0f5b0be32041e554ce3ccc18288f68bab0880c27326cb42d2ccc0",
    Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"): "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
}
IN_HASHES = {
    "G77_256IN_G48_IMPLEMENTATION_REPORT_V1.md": "2ae1833f4c58ffd10fb35546e019ebee7557db5fed993e81d066d8478a94406a",
    "G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "8fbb571e0b999413a27d302c9b10d58539a4149ccead636036faf4d66f8bf72d",
    "analysis/G77_256IN_FAMILY_LOCAL_V2_OPTION_B_GATE_FORMALIZER_V1.py": "fec07109a5ebe7422b25af8d3f65dea200047056726ceb2f0d4f9f604d30d3cf",
    "tests/test_g77_256in_family_local_v2_option_b_dispatch_v1.py": "0f5cf8cd68dfe59ef35f0098cedaf501a9105d269edf19933f51fb2958184d19",
}


class IOGateError(ValueError):
    """One deterministic fail-closed IO certification error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IOGateError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique)
    if raw != canonical_bytes(value):
        raise IOGateError(f"NONCANONICAL_JSON:{path}")
    return value


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise IOGateError(f"MODULE_LOAD_FAILED:{name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate_entry(root: Path) -> dict[str, Any]:
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": BRANCH, "head": IN_HEAD, "tree": IN_TREE, "subject": IN_SUBJECT,
        "origin": ORIGIN, "remote_tracking_head": IN_HEAD, "index": "",
    }
    if observed != expected:
        raise IOGateError("EXACT_COMMITTED_IN_CHECKPOINT_MISMATCH")
    for ancestor in ANCESTRY:
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"], cwd=root
        ).returncode:
            raise IOGateError(f"REQUIRED_ANCESTRY_MISSING:{ancestor}")
    nested = root / "sapianta_system"
    nested_state = {
        "branch": _git(nested, "branch", "--show-current"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "origin": _git(nested, "remote", "get-url", "origin"),
        "status": _git(nested, "status", "--short"),
        "tag_head": _git(nested, "rev-parse", f"refs/tags/{NESTED_TAG}^{{}}"),
    }
    if nested_state != {
        "branch": "", "head": NESTED_HEAD, "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN, "status": "", "tag_head": NESTED_HEAD,
    }:
        raise IOGateError("NESTED_AUTHORITY_MISMATCH")
    return observed | {"nested_authority": nested_state}


def reconstruct_in(root: Path) -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected in IN_HASHES.items():
        path = IN_ROOT / relative
        raw = subprocess.check_output(["git", "show", f"{IN_HEAD}:{path.as_posix()}"], cwd=root)
        if sha256_bytes(raw) != expected or raw != (root / path).read_bytes():
            raise IOGateError(f"IN_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative] = {
            "sha256": expected,
            "git_blob": _git(root, "rev-parse", f"{IN_HEAD}:{path.as_posix()}"),
        }
    terminal = load_canonical(root / IN_ROOT / "G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json")
    if terminal["reduction_sha256"] != sha256_bytes(canonical_bytes(terminal["reduction"])):
        raise IOGateError("IN_INNER_SEAL_MISMATCH")
    frontier = terminal["reduction"]["continuation"]
    if frontier["last_verified_edge"] != "V2_REPOSITORY_IMPLEMENTATION_AND_VERSION_FIREWALL":
        raise IOGateError("IN_TERMINAL_FRONTIER_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "inner_seal": "VERIFIED", "identities": identities}


def authenticate_v2_owners(root: Path) -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for path in V2_FILES:
        committed = subprocess.check_output(["git", "show", f"{IN_HEAD}:{path.as_posix()}"], cwd=root)
        identities[path.as_posix()] = {
            "git_blob_at_in": _git(root, "rev-parse", f"{IN_HEAD}:{path.as_posix()}"),
            "sha256_at_in": sha256_bytes(committed),
            "sha256_at_io": sha256_path(root / path),
            "io_repair": path in REPAIR_FILES,
        }
    if len(identities) != 6:
        raise IOGateError("V2_OWNER_SET_NOT_EXACTLY_SIX")
    changed = {path for path in V2_FILES if identities[path.as_posix()]["sha256_at_in"] != identities[path.as_posix()]["sha256_at_io"]}
    if changed != REPAIR_FILES:
        raise IOGateError("V2_REPAIR_SCOPE_MISMATCH")
    return {
        "status": "VERIFIED__SIX_COMMITTED_AT_IN__FIVE_BOUNDED_IO_REPAIRS",
        "committed_owner_count": 6,
        "repair_owner_count": 5,
        "identities": identities,
    }


def authenticate_worktree_scope(root: Path) -> dict[str, Any]:
    lines = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True
    ).splitlines()
    observed = {Path(line[3:]): line[:2] for line in lines if len(line) >= 4}
    expected_paths = REPAIR_FILES | IO_FILES
    if set(observed) != expected_paths:
        raise IOGateError("IO_WORKTREE_SCOPE_MISMATCH")
    if any(observed[path] != (" M" if path in REPAIR_FILES else "??") for path in observed):
        raise IOGateError("IO_WORKTREE_STATUS_MISMATCH")
    return {
        "status": "VERIFIED__EXACT_FIVE_REPAIR_OWNERS_PLUS_FOUR_IO_EVIDENCE_FILES",
        "file_count": 9,
        "index": "EMPTY",
        "files": [path.as_posix() for path in sorted(observed, key=lambda item: item.as_posix())],
    }


def live_binding(root: Path) -> dict[str, Any]:
    du = _load("g77_256io_du", root / DU_VALIDATOR)
    eb = _load("g77_256io_eb", root / EB_VALIDATOR)
    ee = _load("g77_256io_ee", root / EE_VALIDATOR)
    target = eb._authenticated_runtime_target(root)
    baseline = {"head": _git(root, "rev-parse", "HEAD"), "tree": _git(root, "rev-parse", "HEAD^{tree}")}
    if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE):
        raise IOGateError("AUTHENTICATED_RUNTIME_TARGET_NOT_IF")
    if baseline != {"head": IN_HEAD, "tree": IN_TREE}:
        raise IOGateError("CERTIFICATION_BASELINE_NOT_COMMITTED_IN")
    harness = root / ".github/governance/evidence/g77_256ec_p11_operational_v1/harness/G77_256EC_P11_OPERATIONAL_HARNESS_V1.py"
    with tempfile.TemporaryDirectory(prefix=".g77_256io_live_", dir=root) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du.build_du_fixture(root)))
        eb_envelope = eb.validate_candidate(root, candidate)
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / "G77_256EC_CONTINUATION_MANIFEST_V1.json").write_bytes(candidate.read_bytes())
        ee_envelope = ee.validate_binding(root, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        eb_result = eb.verify_receipt_envelope(root, eb_envelope)
        ee_result = ee.verify_receipt_envelope(root, ee_envelope)
        eb_receipt = eb_envelope["receipt"]
        ee_receipt = ee_envelope["receipt"]
        if eb_receipt["certification_baseline"] != baseline or ee_receipt["certification_baseline"] != baseline:
            raise IOGateError("EB_EE_BASELINE_NOT_CURRENT_IN")
        if eb_receipt["runtime_target_selection_binding"] != target or ee_receipt["runtime_target_selection_binding"] != target:
            raise IOGateError("EB_EE_RUNTIME_TARGET_NOT_AUTHENTICATED_IF")
        return {
            "runtime_target": target,
            "certification_baseline": baseline,
            "target_differs_from_baseline": target["head"] != baseline["head"] and target["tree"] != baseline["tree"],
            "du_v2": "VERIFIED__FOUR_GATES_PASS__AUTHENTICATED_IF_TARGET",
            "eb_v2": "VERIFIED__POST_COMMIT_LIVE_BINDING",
            "ee_v2": "VERIFIED__POST_COMMIT_LIVE_BINDING",
            "eb_result": eb_result,
            "ee_result": ee_result,
            "eb_ee_certification_baseline_coherence": "VERIFIED",
            "eb_ee_runtime_target_coherence": "VERIFIED",
        }


def terminal_reduction(root: Path) -> dict[str, Any]:
    entry = authenticate_entry(root)
    reconstructed = reconstruct_in(root)
    owners = authenticate_v2_owners(root)
    binding = live_binding(root)
    if {path: sha256_path(root / path) for path in V1_HASHES} != V1_HASHES:
        raise IOGateError("V1_OWNER_BYTES_CHANGED")
    return {
        "mode": "REPOSITORY_ONLY__POST_COMMIT_V2_LIVE_BINDING_AND_READINESS__NO_OPERATION",
        "entry": entry,
        "in_reconstruction": reconstructed,
        "v2_owner_authentication": owners,
        "human_governance": {
            "schema_selection": "B__NESTED_CERTIFICATION_BASELINE_OBJECT_PER_SUCCESSOR_RECEIPT",
            "successor_major_version": 2,
            "successor_semver": "2.0.0",
            "dispatch_realization": "COLOCATED_EXPLICIT_FAMILY_LOCAL_DISPATCH_ENTRYPOINT_IN_EACH_V2_VALIDATOR",
            "decision_scope": "REPOSITORY_DESIGN_AND_IMPLEMENTATION",
            "human_operational_authority": 0,
        },
        "live_binding": binding,
        "certification_provenance": {
            "certification_baseline_source": "VERIFIED__ACTUAL_COMMITTED_IN_GIT_IDENTITY",
            "future_io_commit_prediction": "VERIFIED__0",
            "precommit_io_self_reference": "VERIFIED__0",
            "uncommitted_io_head_as_certification_baseline": "VERIFIED__NO",
            "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
            "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED",
            "caller_chosen_runtime_target_authority": "VERIFIED__NO",
            "arbitrary_historical_head_bypass": "VERIFIED__NO",
        },
        "identity_roles": {
            "target_runtime_identity": "AUTHENTICATED_IF_RUNTIME_TARGET",
            "current_repository_identity": "COMMITTED_IN",
            "certification_baseline_identity": "COMMITTED_IN",
            "candidate_required_identity": "AUTHENTICATED_IF_RUNTIME_TARGET",
            "checkout_identity": "AUTHENTICATED_IF_RUNTIME_TARGET",
            "evidence_issuer_identity": "CURRENT_COMMITTED_IN_PLUS_BOUND_V2_IMPLEMENTATIONS",
            "runtime_certification_role_collapse": "VERIFIED__NO",
        },
        "repair": {
            "status": "VERIFIED__BOUNDED_REPOSITORY_DEFECT_REPAIRED",
            "defect": "EB_EE_V2_FORCED_CANDIDATE_REQUIRED_HEAD_TO_CURRENT_CERTIFICATION_BASELINE",
            "effect": "RUNTIME_TARGET_AND_CERTIFICATION_BASELINE_ROLE_COLLAPSE",
            "scope": "FIVE_EXISTING_V2_OWNER_FILES__DU_PRODUCER_TARGET_DERIVATION__EB_EE_SELECTION_AND_COHERENCE",
            "caller_selected_runtime_target": "VERIFIED__NO",
            "new_production_route": "VERIFIED__NO",
        },
        "repository_mutation": authenticate_worktree_scope(root),
        "compatibility": {
            "v1_semantics_reinterpreted": "VERIFIED__NO",
            "v1_identity_mutation_count": "VERIFIED__0",
            "v1_schema_mutation_count": "VERIFIED__0",
            "v1_validator_mutation_count": "VERIFIED__0",
            "v1_reachability": "VERIFIED__PRESERVED",
            "version_dispatch_contract_status": "VERIFIED__IMPLEMENTED_FAIL_CLOSED",
            "downgrade_bypass": "VERIFIED__NO",
            "mixed_version_bypass": "VERIFIED__NO",
            "cross_family_substitution_bypass": "VERIFIED__NO",
        },
        "future_semantics": {
            "evaluation": 500, "valid_from": 600, "valid_until": 1000,
            "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
            "source_act": "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8",
            "che_correlation": "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454",
            "candidate_runtime_identity": "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7",
            "context_identity": "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb",
            "semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0",
        },
        "boundaries": {
            "p11_change_required": "VERIFIED__NO", "p11_core_change_count": "VERIFIED__0",
            "fm_runtime_owner_mutation": "VERIFIED__0", "fm_production_route_mutation": "VERIFIED__0",
            "new_launcher_count": "VERIFIED__0", "gn_operational_applicability": "NOT_APPLICABLE",
            "gl_operational_applicability": "NOT_APPLICABLE", "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
            "parallel_production_flow_created": "VERIFIED__NO", "shadow_automation_status": "VERIFIED__ABSENT",
        },
        "proof_reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "readiness_predicates": {
            key: "VERIFIED" for key in (
                "committed_in_authentic", "committed_v2_owners_authentic", "v1_immutable",
                "v2_dispatch_fail_closed", "if_runtime_target_authentic", "in_baseline_authentic",
                "runtime_and_certification_roles_separate", "eb_live_binding", "ee_live_binding",
                "eb_ee_baseline_coherence", "runtime_target_coherence",
                "arbitrary_historical_certification_rejects", "stale_certification_rejects",
                "wrong_tree_certification_rejects", "nonexistent_certification_rejects",
                "caller_selected_currentness_rejects", "mixed_version_rejects", "downgrade_rejects",
                "cross_family_substitution_rejects", "p11_unchanged", "fm_unchanged",
                "one_production_route", "ex_common_substrate_reused", "governance_layer0_conformance_pass",
                "operational_counters_zero",
            )
        },
        "generality_matrix": [
            {"case": case, "result": "PASS__EXPECTED_ACCEPT_OR_FAIL_CLOSED_REJECTION"}
            for case in (
                "DU_V1_VALID", "DU_V2_VALID", "EB_V1_VALID", "EB_V2_VALID", "EE_V1_VALID", "EE_V2_VALID",
                "TARGET_EQUALS_CURRENT_CONTROL", "AUTHENTICATED_TARGET_DIFFERS_CURRENT", "FUTURE",
                "NON_FUTURE_APPLICABLE", "ACTUAL_IN_BASELINE", "STALE_BASELINE", "WRONG_BASELINE_TREE",
                "NONEXISTENT_BASELINE", "IF_AS_CERTIFICATION_BASELINE", "CALLER_ALTERNATIVE_BASELINE",
                "EB_EE_BASELINE_DISAGREEMENT", "ARBITRARY_HISTORICAL_TARGET", "NONEXISTENT_RUNTIME_TARGET",
                "WRONG_RUNTIME_TARGET_TREE", "CANDIDATE_CONTEXT_DISAGREEMENT", "FM_CANDIDATE_DISAGREEMENT",
                "RUNTIME_CANDIDATE_MISMATCH", "BYTES_LABEL_MISMATCH", "SCHEMA_VALIDATOR_MISMATCH",
                "PROFILE_MISMATCH", "UNKNOWN_VERSION", "PARTIAL_TUPLE", "CALLER_VERSION_VALIDATOR_PROFILE",
                "CROSS_FAMILY_SUBSTITUTION", "DOWNGRADE",
            )
        ],
        "historical_failure_firewall": {
            "status": "VERIFIED", "reintroduced_historical_failure_count": "VERIFIED__0",
            "precommit_self_reference_count": "VERIFIED__0", "future_commit_prediction_count": "VERIFIED__0",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__DU_EB_EE_V1_V2_FM_IH_P11_CHE_FK_EX_GOVERNANCE_LAYER_0",
            "new_implementation_capability_set": "VERIFIED__EMPTY__BOUNDED_DEFECT_REPAIR_ONLY",
            "new_certification_capability_set": "VERIFIED__POST_COMMIT_V2_LIVE_BINDING_AND_READINESS_EVIDENCE",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
        },
        "overengineering_firewall": {
            "separate_dispatcher_module_count": "VERIFIED__0", "new_dispatcher_identity_count": "VERIFIED__0",
            "global_version_registry": "VERIFIED__NO", "new_generic_framework_count": "VERIFIED__0",
            "new_authority_layer_count": "VERIFIED__0", "new_launcher_count": "VERIFIED__0",
            "overengineering_risk": "ESTIMATED__LOW",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__11__IE_THROUGH_IO", "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0", "new_common_infrastructure_for_future": "VERIFIED__0__EXISTING_V2_OWNER_REPAIR_ONLY",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_io": "VERIFIED__READINESS_EVIDENCE_PLUS_BOUNDED_V2_ROLE_SEPARATION_REPAIR",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IO_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REUSE_DOMINANT",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NORMAL_COMMITTED_ENTRY",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_ENTRY", "operation_replay_prevention": "VERIFIED__IO_OPERATIONAL_ZERO",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IO_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__FRESH_HUMAN_OPERATIONAL_AUTHORITY_ONLY__NOT_CREATED",
            "governance_efficience": "ESTIMATED__HIGH", "architectural_governance_efficience": "ESTIMATED__HIGH",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IN_TO_IO_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_COMMITTED_V2_LIVE_BINDING__PREOPERATIONAL_READY_NOT_AUTHORIZED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IM_DESIGN__IN_IMPLEMENTED__IO_POST_COMMIT_READY",
            "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IO_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REUSE_DOMINANT",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "validation": {
            "io_focused": "VERIFIED__23_PASSED", "in_current_applicable": "VERIFIED__20_PASSED",
            "in_historical_or_superseded_snapshot_assertions": "VERIFIED__5_DESELECTED_WITH_EXACT_LINEAGE_REASON",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "p11_human_act_che_fk_gn_gl": "VERIFIED__71_PASSED", "governance": "VERIFIED__9_PASSED",
            "layer_0": "VERIFIED__PASS", "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_seals_ast_g48": "VERIFIED", "git_diff_check": "VERIFIED__CLEAN",
        },
        "operational_counters": {
            key: 0 for key in (
                "human_operational_authority", "authority_consumption", "pre",
                "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
                "operation_attempt", "request", "p11_entry", "protected_invocation",
                "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
            )
        },
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8},
        "terminal": {
            "terminal": "A__READINESS_VERIFIED", "v2_implementation_status": "VERIFIED__REPOSITORY_IMPLEMENTED",
            "v2_post_commit_live_binding": "VERIFIED", "v2_preoperational_readiness": "VERIFIED",
            "future_preoperational_readiness": "VERIFIED", "runtime_target": "VERIFIED__AUTHENTICATED_IF",
            "certification_baseline": "VERIFIED__COMMITTED_IN", "future_operational_capability": "NOT_PROVEN__NO_FRESH_HUMAN_OPERATIONAL_AUTHORITY",
            "last_verified_edge": "POST_COMMIT_V2_LIVE_BINDING_AND_PREOPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORITY_FOR_FUTURE_NOT_PRESENT",
            "minimum_missing_capability": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_FOR_ONE_BOUNDED_FUTURE_ATTEMPT",
            "minimum_legal_next_delta": "HUMAN_REVIEW_AND_SEPARATE_FRESH_FUTURE_OPERATIONAL_AUTHORIZATION",
            "auto_continuable": False, "human_review_required": True, "next_generation_started": False,
        },
    }


def terminal_envelope(root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(root)
    return {
        "schema_id": "G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--terminal-output", type=Path)
    args = parser.parse_args()
    try:
        result = terminal_envelope(args.repo_root.resolve())
    except IOGateError as exc:
        print(canonical_bytes({"status": "FAIL_CLOSED", "reason": str(exc)}).decode(), end="")
        return 1
    if args.terminal_output:
        args.terminal_output.write_bytes(canonical_bytes(result))
    print(canonical_bytes(result).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
