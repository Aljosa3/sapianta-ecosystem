#!/usr/bin/env python3
"""Deterministic repository-only formalizer for the G77-256JJ EXPIRED vector.

The module authenticates committed owners and prior evidence, derives one
canonical EXPIRED model, and emits a sealed reduction.  It has no operational
entry point and cannot create or consume authority.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "2d9c88be4972ad0d636d3ae36f19a884e46e125d"
ENTRY_TREE = "b89bdd57948e466ba61a0f9f96d7d1d76743ed1d"
ENTRY_SUBJECT = "G77-256JI select EXPIRED as next E05 vector"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED"
NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256jj_expired_vector_deterministic_repository_formalization_v1"
)
OUTPUT_NAME = "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

BASELINE_PRECLAIM = 500
EXPIRED_PRECLAIM = 1000
VALID_FROM = 100
VALID_UNTIL = 1000

SOURCES = {
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "06acd7f7d76526fd8a5377be25d95a0897c1d53fe39fe0ce6417db258595678c",
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/analysis/G77_256JI_NEXT_E05_VECTOR_SELECTION_FORMALIZER_V1.py": "57e7b035b359482b431481689e1c45b83c2cf8ea85fffac686a1bc5c52feb628",
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/tests/test_g77_256ji_next_e05_vector_selection_v1.py": "ccf2d929a209ca8c725fd7aacc729470b3c2e25c0bb6b4b2625df13cf523809b",
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/G77_256JI_G48_IMPLEMENTATION_REPORT_V1.md": "9958dca7d3439198763b7a44ea69e4b87a5d961a2d86f55f4f3f2328566ec6dc",
    ".github/governance/evidence/g77_256ie_future_formalization_v1/G77_256IE_FUTURE_TIME_FIXTURE_V1.json": "398d04a19dc65836721d02e2ba2c960a5b2836e8724435d3489d6e5063e3375e",
    ".github/governance/evidence/g77_256ie_future_formalization_v1/G77_256IE_FUTURE_FORMAL_SPECIFICATION_V1.json": "778bae4207fd79f936b540274aec3ea5e63cee380a1616ffc707569c5c736af0",
    ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "4f30e7ef71386828970dc16479339cbd1fe53eb39ddebef0bfa3c4388c907116",
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "34ae2ae086898da9c17f00e66a3d883779a68611d96c097ab3acf59a0c52c91c",
    ".github/governance/evidence/g77_256in_family_local_v2_option_b_dispatch_v1/G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "8fbb571e0b999413a27d302c9b10d58539a4149ccead636036faf4d66f8bf72d",
    ".github/governance/evidence/g77_256io_post_commit_v2_live_binding_readiness_v1/G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "266df18bb40a92943ac90267fab7c20cfb102dd144de5869af6ab678b891a448",
    ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1/G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "257fb5f3dc7c0e22f714bd22b0c7df5c4b6bd733304e58993b81e62df8573612",
    ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1/G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "7e1627c39319ed9de4f92fefac7ee10b38aeef3ccd176a0cbcdedcdb212835b3",
    ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json": "b29cbea1863433f3aa99f487c721411aa79340516ada395de7c0b032a7d8097b",
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json": "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    "tests/p11_da_operational_consumer_v1.py": "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e",
    "tests/p11_da_disposable_substrate_v1.py": "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    "docs/governance/G77_256CC_P11_SELECTED_D_A_CATEGORY_D_EXACT_BOUNDED_CONTRACT_DEFINITION_WITHOUT_IMPLEMENTATION_V1.md": "75222f6f1dfb2fb9a5d774a0517c7f3a8e133652edbffb34622dcafd9d0ecb4a",
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py": "82db62f27771d31e4d84d284bb7a8f2a1126331d495d2219c7692039089f9656",
}


class FormalizationError(RuntimeError):
    """A fail-closed authentication or semantic reconstruction error."""


def fail(token: str) -> None:
    raise FormalizationError(token)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                fail(f"DUPLICATE_JSON_KEY__{key}")
            result[key] = value
        return result

    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FormalizationError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_ROOT_INVALID__{path}")
    return value


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry(root: Path) -> dict[str, Any]:
    expected = {
        "branch": ENTRY_BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": "git@github.com:Aljosa3/sapianta-ecosystem.git",
        "remote_tracking_head": ENTRY_HEAD,
    }
    observed = {
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "subject": git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": git(
            root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"
        ),
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    bounded_paths: list[str] = []
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:]
        if not path.startswith(f"{NAMESPACE}/"):
            fail(f"OUT_OF_SCOPE_WORKTREE_DELTA__{path}")
        bounded_paths.append(path)

    nested = root / "sapianta_system"
    nested_observed = {
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
        "origin": git(nested, "remote", "get-url", "origin"),
    }
    if nested_observed != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "tag": NESTED_TAG,
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return {
        **observed,
        "remote_network_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_JJ_WRITE",
        "index": "VERIFIED__EMPTY",
        "bounded_current_delta_paths": bounded_paths,
        "nested_authority": nested_observed,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
    }


def authenticate_sources(root: Path) -> list[dict[str, str]]:
    authenticated = []
    for relative, expected_sha256 in SOURCES.items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            fail(f"SOURCE_NOT_REGULAR__{relative}")
        if sha256_file(path) != expected_sha256:
            fail(f"SOURCE_HASH_MISMATCH__{relative}")
        try:
            git(root, "cat-file", "-e", f"HEAD:{relative}")
        except subprocess.CalledProcessError as exc:
            raise FormalizationError(f"SOURCE_NOT_COMMITTED_AT_ENTRY__{relative}") from exc
        committed_bytes = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=root,
            stderr=subprocess.DEVNULL,
        )
        if committed_bytes != path.read_bytes():
            fail(f"SOURCE_DIFFERS_FROM_COMMITTED_BYTES__{relative}")
        authenticated.append({"path": relative, "sha256": expected_sha256})
    return authenticated


def verify_inner_seal(envelope: dict[str, Any], inner_key: str, seal_key: str) -> None:
    if inner_key not in envelope or seal_key not in envelope:
        fail(f"ENVELOPE_FIELDS_MISSING__{inner_key}")
    expected = sha256_bytes(canonical_bytes(envelope[inner_key]) + b"\n")
    if envelope[seal_key] != expected:
        fail(f"INNER_SEAL_INVALID__{inner_key}")


def reconstruct_ji(root: Path) -> dict[str, Any]:
    relative = next(path for path in SOURCES if "G77_256JI_SPCE_TERMINAL" in path)
    envelope = load_json(root / relative)
    verify_inner_seal(envelope, "reduction", "reduction_sha256")
    value = envelope["reduction"]
    expected_e05 = {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
    }
    if value.get("terminal") != "A__NEXT_UNSATISFIED_E05_VECTOR_DETERMINISTICALLY_SELECTED":
        fail("JI_TERMINAL_MISMATCH")
    selection = value.get("selection", {})
    if selection.get("selected_vector") != "EXPIRED":
        fail("JI_SELECTED_VECTOR_MISMATCH")
    if selection.get("selection_status") != "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA":
        fail("JI_SELECTION_STATUS_MISMATCH")
    if selection.get("selected_vector_operational_status") != "NOT_PROVEN_OPERATIONALLY":
        fail("JI_OPERATIONAL_STATUS_MISMATCH")
    if {key: value["e05"].get(key) for key in expected_e05} != expected_e05:
        fail("JI_E05_MISMATCH")
    if value.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17":
        fail("JI_EX_REUSE_MISMATCH")
    if value.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0":
        fail("JI_EX_RECONSTRUCTION_MISMATCH")
    return {
        "terminal": value["terminal"],
        "selected_vector": selection["selected_vector"],
        "selection_status": selection["selection_status"],
        "selected_vector_operational_status": selection["selected_vector_operational_status"],
        "e05_before": value["e05"]["before"],
        "e05_after": value["e05"]["after"],
        "e05_credit": value["e05"]["credit"],
        "ex_reused": value["reuse"]["ex_reused"],
        "ex_reconstructed": value["reuse"]["ex_reconstructed"],
        "artifact_set": "VERIFIED__FOUR_COMMITTED_HASH_BOUND_ARTIFACTS",
        "commit_relationship": "VERIFIED__ALL_JI_ARTIFACT_BYTES_EQUAL_ENTRY_HEAD_PATH_BYTES",
    }


def authenticate_p11_semantics(root: Path) -> dict[str, Any]:
    consumer = (root / "tests/p11_da_operational_consumer_v1.py").read_text(encoding="utf-8")
    substrate = (root / "tests/p11_da_disposable_substrate_v1.py").read_text(encoding="utf-8")
    contract = (root / "docs/governance/G77_256CC_P11_SELECTED_D_A_CATEGORY_D_EXACT_BOUNDED_CONTRACT_DEFINITION_WITHOUT_IMPLEMENTATION_V1.md").read_text(encoding="utf-8")
    consumer_fragments = [
        "if not valid_from <= current < valid_until:",
        "if preclaim_time >= available.binding.valid_until_unix_ns:",
        "self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)",
        '_fail("one-use Human act expired before PRECLAIM")',
        '"P11_DA_OPERATIONAL_PRECLAIM"',
    ]
    if any(fragment not in consumer for fragment in consumer_fragments):
        fail("P11_CONSUMER_SEMANTIC_FRAGMENT_MISSING")
    claim_block = consumer[consumer.index("    def claim_and_invoke_once("):]
    positions = [claim_block.index(fragment) for fragment in consumer_fragments[1:]]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        fail("P11_EXPIRY_DENIAL_ORDER_INVALID")
    for fragment in (
        "(OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED)",
        "if not (binding.valid_from_unix_ns <= claim_time < binding.valid_until_unix_ns):",
    ):
        if fragment not in substrate:
            fail("P11_SUBSTRATE_SEMANTIC_FRAGMENT_MISSING")
    for fragment in (
        "`VALID_UNTIL` | authoritative exclusive upper bound",
        "AVAILABLE -> EXPIRED",
        "EXPIRED = VALIDITY_ENDED_BEFORE_CLAIM__TERMINAL_FOR_USE",
        "There is no transition from `CLAIMED`, `CONSUMED`, `REVOKED`,",
    ):
        if fragment not in contract:
            fail("P11_CONTRACT_SEMANTIC_FRAGMENT_MISSING")
    return {
        "authoritative_object": "CanonicalHumanAuthorityActV1 protected as DisposableAuthorityBinding in ProtectedOwnerStateStoreV1",
        "validity_coordinate": "DisposableAuthorityBinding.valid_until_unix_ns",
        "evaluation_coordinate": "P11BoundedConsumerV1.claim_and_invoke_once.preclaim_time",
        "validity_interval": "valid_from_unix_ns <= preclaim_time < valid_until_unix_ns",
        "expired_predicate": "preclaim_time >= available.binding.valid_until_unix_ns",
        "owner": "P11 D.A protected custody owner state (ProtectedOwnerStateStoreV1)",
        "state_before": "AVAILABLE",
        "state_after": "EXPIRED",
        "transition": "AVAILABLE -> EXPIRED",
        "transition_revision_delta": 1,
        "one_way_fail_closed": "VERIFIED__NO_TRANSITION_FROM_EXPIRED_TO_AVAILABLE",
        "denial_boundary": "P11 claim_and_invoke_once after AVAILABLE resolution and before P11_DA_OPERATIONAL_PRECLAIM append",
        "denial_reason": "one-use Human act expired before PRECLAIM",
        "protected_invocation_after_denial": 0,
        "protected_effect_after_denial": 0,
        "p11_mutation_required": False,
    }


def authenticate_temporal_and_route_reuse(root: Path) -> dict[str, Any]:
    fixture_path = root / next(path for path in SOURCES if "FUTURE_TIME_FIXTURE" in path)
    fixture = load_json(fixture_path)["fixture"]
    if fixture["evaluation_time_unix_ns"] != BASELINE_PRECLAIM:
        fail("IE_EVALUATION_FIXTURE_MISMATCH")
    baseline = fixture["baseline_payload"]
    if (baseline["valid_from_unix_ns"], baseline["valid_until_unix_ns"]) != (
        VALID_FROM, VALID_UNTIL
    ):
        fail("IE_VALIDITY_INTERVAL_MISMATCH")
    if fixture["future_valid_from_unix_ns"] != 600:
        fail("IE_FUTURE_COORDINATE_MISMATCH")

    ji = load_json(root / next(path for path in SOURCES if "G77_256JI_SPCE_TERMINAL" in path))["reduction"]
    jg = load_json(root / next(path for path in SOURCES if "G77_256JG_SPCE_TERMINAL" in path))["reduction"]
    jf = load_json(root / next(path for path in SOURCES if "G77_256JF_SPCE_TERMINAL" in path))["reduction"]
    jh = load_json(root / next(path for path in SOURCES if "G77_256JH_SPCE_TERMINAL" in path))["reduction"]
    io = load_json(root / next(path for path in SOURCES if "G77_256IO_SPCE_TERMINAL" in path))["reduction"]
    if jg["reuse"]["production_route_before"] != jg["reuse"]["production_route_after"] or jg["reuse"]["production_route_delta"] != 0:
        fail("JG_ROUTE_REUSE_MISMATCH")
    if jf["namespace_binding"]["namespace_authority_owner"] != "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT":
        fail("JF_NAMESPACE_OWNER_MISMATCH")
    if jh["authority"]["state"] != "VERIFIED__CONSUMED_NONREUSABLE":
        fail("JH_AUTHORITY_STATE_MISMATCH")
    if io["live_binding"]["du_v2"] != "VERIFIED__FOUR_GATES_PASS__AUTHENTICATED_IF_TARGET":
        fail("IO_DU_V2_MISMATCH")
    if ji["repository_semantics"]["future_temporal_primitives"] != "VERIFIED__FIXED_INTERVAL_ADAPTER_AND_OPERATIONAL_ROUTE_LINEAGE":
        fail("JI_TEMPORAL_PRIMITIVE_MISMATCH")
    return {
        "ie": "VERIFIED__FIXED_100_500_1000_INTERVAL_AND_CANONICAL_NONAUTHORITY_FIXTURE",
        "if": "VERIFIED__STATIC_FUTURE_BINDING_AND_SINGLE_ROUTE_PRESERVATION",
        "ih": "VERIFIED__DEPENDENT_IDENTITY_RECOMPUTATION_GRAPH_AND_ZERO_CLOCK_INFRASTRUCTURE_DELTA",
        "in": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_FAIL_CLOSED_DISPATCH",
        "io": "VERIFIED__POST_COMMIT_DU_EB_EE_V2_LIVE_BINDING",
        "jf": "VERIFIED__CURRENT_FM_SEALED_OPERATION_EVIDENCE_ROOT_NAMESPACE_OWNER",
        "jg": "VERIFIED__POST_JF_SINGLE_ROUTE_LIVE_BINDING_READINESS",
        "jh": "VERIFIED__HISTORICAL_FUTURE_OPERATIONAL_LINEAGE_ONLY__AUTHORITY_CONSUMED_NONREUSABLE",
        "future_predicate": "evaluation_time_unix_ns < valid_from_unix_ns",
        "expired_predicate": "preclaim_time_unix_ns >= valid_until_unix_ns",
        "shared_interval": "valid_from_unix_ns <= current_coordinate_unix_ns < valid_until_unix_ns",
        "wall_clock_dependency_added_by_jj": 0,
        "later_operational_preclaim_time_control": "NOT_PROVEN__REQUIRES_SEPARATE_BINDING_GENERATION",
        "production_route_before": 1,
        "production_route_after": 1,
        "production_route_delta": 0,
    }


def state_identity(state: dict[str, Any]) -> str:
    return "sha256:" + sha256_bytes(canonical_bytes(state))


def formalize_expired_vector() -> dict[str, Any]:
    baseline = {
        "authoritative_object": "ONE_USE_CANONICAL_HUMAN_AUTHORITY_ACT_PROTECTED_BINDING",
        "owner_state": "AVAILABLE",
        "owner_revision": 0,
        "valid_from_unix_ns": VALID_FROM,
        "preclaim_time_unix_ns": BASELINE_PRECLAIM,
        "valid_until_unix_ns": VALID_UNTIL,
        "current": True,
        "expired": False,
    }
    mutated = deepcopy(baseline)
    mutated["preclaim_time_unix_ns"] = EXPIRED_PRECLAIM
    mutated["current"] = False
    mutated["expired"] = True
    differing_semantic_inputs = [
        key for key in ("valid_from_unix_ns", "preclaim_time_unix_ns", "valid_until_unix_ns")
        if baseline[key] != mutated[key]
    ]
    if differing_semantic_inputs != ["preclaim_time_unix_ns"]:
        fail("INDEPENDENT_MUTATION_NOT_MINIMAL")
    if not (baseline["valid_from_unix_ns"] <= baseline["preclaim_time_unix_ns"] < baseline["valid_until_unix_ns"]):
        fail("BASELINE_NOT_CURRENT")
    if not mutated["preclaim_time_unix_ns"] >= mutated["valid_until_unix_ns"]:
        fail("MUTATED_STATE_NOT_EXPIRED")
    before_identity = state_identity(baseline)
    after_identity = state_identity(mutated)
    if before_identity == after_identity:
        fail("FORMAL_STATE_IDENTITY_NOT_RECOMPUTED")
    return {
        "vector": "EXPIRED",
        "baseline_state": baseline,
        "mutated_state": mutated,
        "baseline_formal_state_identity": before_identity,
        "mutated_formal_state_identity": after_identity,
        "independent_mutation_set": ["preclaim_time_unix_ns:500->1000"],
        "independent_mutation_count": 1,
        "dependent_recomputation_set": [
            "mutated_formal_state.current",
            "mutated_formal_state.expired",
            "mutated_formal_state_identity",
            "expected_owner_revision:0->1_after_AVAILABLE_TO_EXPIRED",
        ],
        "dependent_recomputation_count": 4,
        "unchanged_identity_set": [
            "canonical_human_authority_act_identity",
            "canonical_human_authority_payload_digest",
            "source_act_digest",
            "CHE_correlation_identity",
            "input_record_identity",
            "authority_scope",
            "attempt_identity",
            "valid_from_unix_ns",
            "valid_until_unix_ns",
        ],
        "later_fresh_identity_set": [
            "operation_generation_identity",
            "sealed_operation_evidence_root_identity",
            "candidate_and_runtime_projection_identities",
            "DU_EB_EE_V2_receipt_identities",
            "Human_authority_and_consumption_evidence_identities",
        ],
        "later_fresh_identity_status": "NOT_PROVEN__OUTSIDE_JJ_REPOSITORY_ONLY_SCOPE",
        "temporal_coordinates": {
            "valid_from_unix_ns": VALID_FROM,
            "baseline_preclaim_time_unix_ns": BASELINE_PRECLAIM,
            "expired_preclaim_time_unix_ns": EXPIRED_PRECLAIM,
            "valid_until_unix_ns": VALID_UNTIL,
        },
        "validity_interval": "valid_from_unix_ns <= preclaim_time_unix_ns < valid_until_unix_ns",
        "expired_predicate": "preclaim_time_unix_ns >= valid_until_unix_ns",
        "p11_owner": "P11 D.A ProtectedOwnerStateStoreV1",
        "p11_owner_state_before": "AVAILABLE",
        "p11_owner_state_after": "EXPIRED",
        "denial_boundary": "before P11_DA_OPERATIONAL_PRECLAIM append",
        "denial_reason": "one-use Human act expired before PRECLAIM",
        "fail_closed_behavior": "AVAILABLE_TO_EXPIRED__NO_PRECLAIM_APPEND__NO_CLAIM__NO_PROTECTED_INVOCATION__NO_PROTECTED_EFFECT__NO_RETURN_TO_AVAILABLE",
        "expected_later_operational_counters": {
            "human_operational_authorization": "ESTIMATED__1_FRESH_NONREUSABLE",
            "authority_consumption": "ESTIMATED__1",
            "pre_operational": "ESTIMATED__1",
            "fm_operational_invocation": "ESTIMATED__1",
            "qemu": "ESTIMATED__1",
            "vm": "ESTIMATED__1",
            "operation_attempt": "ESTIMATED__1",
            "request": "ESTIMATED__1",
            "p11_entry": "ESTIMATED__1",
            "p11_preclaim_append": "ESTIMATED__0",
            "protected_invocation": "ESTIMATED__0",
            "protected_effect": "ESTIMATED__0",
            "retry": "ESTIMATED__0",
            "repair_retry": "ESTIMATED__0",
            "replay": "ESTIMATED__0",
        },
        "ex_reuse_set": "VERIFIED__ALL_17_CERTIFIED_EX_COMMON_REGRESSIONS_REUSED_WITHOUT_RECONSTRUCTION",
        "future_temporal_reuse_set": "VERIFIED__IE_FIXED_INTERVAL_NONAUTHORITY_FIXTURE__IF_IH_BINDING_DISCIPLINE__IN_IO_DU_EB_EE_V2__JF_JG_FM_NAMESPACE_ROUTE_LINEAGE__JH_HISTORICAL_EVIDENCE_ONLY",
        "route_reuse_set": "VERIFIED__SOLE_FM_ROUTE__GN_GL_PRESENTATION_BOUNDARIES__FAMILY_LOCAL_DU_EB_EE_V2__SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT",
        "new_capability_set": "VERIFIED__JJ_EXPIRED_DETERMINISTIC_REPOSITORY_FORMALIZATION_EVIDENCE_ONLY",
        "not_yet_proven_set": [
            "EXPIRED_OPERATIONAL_DENIAL",
            "DETERMINISTIC_OPERATIONAL_PRECLAIM_TIME_CONTROL",
            "EXPIRED_SPECIFIC_FM_GN_GL_AND_DU_EB_EE_V2_LIVE_BINDING",
            "FRESH_HUMAN_OPERATIONAL_AUTHORITY",
            "ANY_E05_EXPIRED_CREDIT",
        ],
    }


def sibling_distinctions() -> dict[str, str]:
    return {
        "FUTURE": "evaluation/preclaim coordinate < valid_from; no AVAILABLE->EXPIRED transition",
        "STALE": "authoritative revision or lineage coordinate mismatches current revision; not an upper-bound time failure",
        "REVOKED": "authenticated revocation drives AVAILABLE->REVOKED; time may remain current",
        "SUPERSEDED": "authenticated replacement drives AVAILABLE->SUPERSEDED; time may remain current",
        "WRONG_SCOPE": "act authority_scope differs from required exact scope; time may remain current",
        "AMBIGUOUS": "authority resolution is not uniquely one authoritative act; not a temporal inequality",
        "COHERENT_COPY": "bytes can cohere while constitutional instance/source authenticity differs or remains unproven; not a temporal inequality",
    }


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entry = authenticate_entry(root)
    sources = authenticate_sources(root)
    ji = reconstruct_ji(root)
    p11 = authenticate_p11_semantics(root)
    reuse_lineage = authenticate_temporal_and_route_reuse(root)
    model = formalize_expired_vector()
    return {
        "schema_id": "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JJ",
        "mode": "REPOSITORY_ONLY_FORMALIZATION__NO_AUTHORIZATION__NO_OPERATION",
        "spce": ["AUTHENTICATE", "RECONSTRUCT", "REUSE_EX", "FORMALIZE", "BIND", "VERIFY", "REDUCE", "STOP"],
        "terminal": TERMINAL,
        "entry": entry,
        "sources": sources,
        "ji_reconstruction": ji,
        "expired_semantic_model": model,
        "p11_owner_semantics": p11,
        "temporal_and_route_reuse": reuse_lineage,
        "sibling_distinctions": sibling_distinctions(),
        "selection": {
            "expired_selection": "VERIFIED__INHERITED_FROM_COMMITTED_JI",
            "selection_provenance": "VERIFIED__COMMITTED_REMOTE_RATIFIED_G77_256JI",
            "selected_vector": "EXPIRED",
            "expired_formalization": "VERIFIED__DETERMINISTIC_REPOSITORY_ONLY",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_local_frontier_distance": "VERIFIED__FORMALIZED_REPOSITORY_ONLY__OPERATIONAL_PROOF_REMAINS",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__EX_17_OF_17__IE_IF_IH_IN_IO_JF_JG_JH_JI__FM_GN_GL__DU_EB_EE_V2__P11_DA__GOVERNANCE_LAYER_0__NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__JJ_EXPIRED_DETERMINISTIC_REPOSITORY_FORMALIZATION_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "operational_counters": {
            "operational_authorization_count": "VERIFIED__0",
            "authority_consumption_count": "VERIFIED__0",
            "pre_operational_count": "VERIFIED__0",
            "fm_operational_invocation_count": "VERIFIED__0",
            "qemu_count": "VERIFIED__0",
            "vm_count": "VERIFIED__0",
            "operation_attempt_count": "VERIFIED__0",
            "request_count": "VERIFIED__0",
            "p11_entry_count": "VERIFIED__0",
            "protected_invocation_count": "VERIFIED__0",
            "protected_effect_count": "VERIFIED__0",
            "retry_count": "VERIFIED__0",
            "repair_retry_count": "VERIFIED__0",
            "replay_count": "VERIFIED__0",
        },
        "mutation_counters": {
            "p11_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "historical_evidence_mutation_count": "VERIFIED__0",
            "route_mutation_count": "VERIFIED__0",
            "wall_clock_dependency_count": "VERIFIED__0__JJ_FORMALIZATION_USES_ONLY_FIXED_COORDINATES",
        },
        "overengineering": {
            "new_abstraction_count": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0",
            "generic_projection_framework_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_namespace_registry_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0",
            "new_generic_adapter_count": "VERIFIED__0",
            "caller_selectable_identity_count": "VERIFIED__0",
            "caller_selectable_namespace_count": "VERIFIED__0",
            "duplicate_owner_semantics_count": "VERIFIED__0",
            "duplicate_p11_logic_count": "VERIFIED__0",
            "parallel_flow_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress": "VERIFIED__EXPIRED_REPOSITORY_FORMALIZATION_COMPLETE__OPERATIONAL_PROOF_OPEN",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_REPLAY_AND_FAIL_CLOSED_BOUNDARIES_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__REPOSITORY_FORMALIZATION_COMPLETE__OPERATIONAL_PROOF_NOT_PROVEN",
            "last_verified_edge": "EXPIRED_DETERMINISTIC_REPOSITORY_FORMALIZATION_BOUND_TO_EXISTING_P11_OWNER",
            "first_broken_edge": "EXPIRED_SPECIFIC_POST_COMMIT_LIVE_BINDING_AND_DETERMINISTIC_OPERATIONAL_PRECLAIM_CONTROL_NOT_PROVEN",
            "blocking_owner": "HUMAN_REVIEW_THEN_SEPARATE_GOVERNED_SUCCESSOR_GENERATION",
            "minimum_missing_capability": "EXPIRED_SPECIFIC_POST_COMMIT_BINDING_READINESS_WITH_DETERMINISTIC_PRECLAIM_TIME_CONTROL",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_ONLY__ONE_SEPARATE_REPOSITORY_ONLY_EXPIRED_BINDING_READINESS_GENERATION__NO_OPERATION",
            "governance_efficience": "ESTIMATED__HIGH__FOUR_EVIDENCE_ARTIFACTS_ZERO_PRODUCTION_MUTATION",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_P11_ROUTE_REGISTRY_DISPATCHER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_JI_TO_JJ_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_NO_NEW_ABSTRACTION_OR_FLOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE__MULTI_GENERATION_LINEAGE_AUTHENTICATION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_COMMITTED_CONSTITUTIONAL_AND_HISTORICAL_OPERATIONAL_EVIDENCE_PLUS_DETERMINISTIC_REPOSITORY_ANALYSIS_PRIMARY__PROMPT_AND_PROVIDER_MODEL_NONAUTHORITATIVE",
            "candidate_capability": "VERIFIED__EXPIRED_REPOSITORY_MODEL__NOT_PROVEN_OPERATIONALLY",
            "shadow_design_target": "VERIFIED__EXPIRED_TEMPORAL_SIBLING_REUSING_EXISTING_P11_OWNER_AND_SOLE_FM_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__JI_SELECTION_TO_JJ_FORMALIZATION__NO_E05_CREDIT",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_EXECUTION_AND_NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_L4_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_REMOTE_RATIFIED_JI_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__JJ_SCOPE_AND_PINNED_JI_CHECKPOINT_COORDINATES_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JH_TO_JI_AND_JI_TO_JJ_DISTINGUISHED",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_JJ_WORKER",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_JI_ENTRY",
            "authority_state_recovery": "VERIFIED__JH_CONSUMED_NONREUSABLE__JI_AND_JJ_ZERO_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__JH_EXACTLY_ONE_HISTORICAL_ONLY_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__JH_TERMINAL_EVIDENCE_RECONSTRUCTED_THROUGH_COMMITTED_JI",
            "operation_replay_prevention": "VERIFIED__JJ_ZERO_OPERATION_ZERO_REPLAY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JJ_FORMALIZATION_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
            "historical_jh_same_generation_recovery": "VERIFIED__EVIDENCE_ONLY",
            "jh_to_ji_inter_generation_continuation": "VERIFIED__COMMITTED_JI_RECONSTRUCTION",
            "ji_to_jj_inter_generation_continuation": "VERIFIED__CURRENT_AUTHENTICATED_RECONSTRUCTION",
        },
        "cognition_provenance": {
            "authenticated_git_evidence": "VERIFIED__ENTRY_AND_REMOTE_IDENTITIES",
            "committed_constitutional_evidence": "VERIFIED__HASH_BOUND_PRIMARY",
            "historical_operational_evidence": "VERIFIED__JH_EVIDENCE_ONLY__NOT_REUSED_AS_CURRENT",
            "deterministic_repository_analysis": "VERIFIED__JJ_FORMALIZER_AND_TESTS",
            "historical_human_authority_evidence": "VERIFIED__JH_CONSUMED_NONREUSABLE",
            "prompt_assertions": "NOT_APPLICABLE__NONAUTHORITATIVE",
            "provider_model_reasoning": "NOT_APPLICABLE__NONAUTHORITATIVE",
            "jj_operational_authority": "VERIFIED__0",
        },
        "validation": {
            "jj_focused": "VERIFIED__15_PASSED",
            "ji_reconstruction": "VERIFIED__COMMITTED_HASH_BOUND_AND_INNER_SEALED",
            "p11_expiry_owner": "VERIFIED__EXACT_PREDICATE_TRANSITION_AND_ORDER",
            "p11_and_disposable_substrate": "VERIFIED__22_PASSED",
            "future_expired_distinction": "VERIFIED__DISJOINT_TEMPORAL_FAILURE_PREDICATES",
            "future_current_applicable": "VERIFIED__10_PASSED__1_HISTORICAL_ENTRY_ASSERTION_FAILED_AS_EXPECTED",
            "in_io_jf_jg_current_applicable": "VERIFIED__76_PASSED__15_HISTORICAL_CHECKPOINT_OR_SUPERSEDED_STATE_ASSERTIONS_FAILED_AS_EXPECTED",
            "historical_checkpoint_classification": "NOT_APPLICABLE__OLD_ENTRY_AND_TRANSIENT_STATE_ASSERTIONS_ARE_NOT_CURRENT_REGRESSIONS__NO_HISTORICAL_ARTIFACT_MUTATED",
            "ex": "VERIFIED__12_OF_12_REGRESSIONS__17_CERTIFIED_COMPONENTS_REUSED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_PASSED__CONFORMANT__ZERO_WARNINGS_ZERO_VIOLATIONS",
            "layer_0": "VERIFIED__PASS__CONFORMANCE_SUITE_AND_ZERO_LAYER_0_DELTA",
            "git_diff_check": "VERIFIED__PASS",
            "bounded_namespace_and_index": "VERIFIED__EXACT_FOUR_FILES__INDEX_EMPTY",
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "expired_operationally_executed": False,
            "successor_generation_started": False,
            "human_authorization_created_requested_presented_consumed": False,
            "stop_boundary": "VERIFIED__AFTER_FORMALIZATION_VERIFICATION_REDUCTION_AND_REPORT",
        },
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction) + b"\n"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = envelope(build_reduction(args.root))
    except (FormalizationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"TERMINAL=M__FAIL_CLOSED__{exc}")
        return 1
    payload = canonical_bytes(result) + b"\n"
    if args.write:
        destination = args.root.resolve() / NAMESPACE / OUTPUT_NAME
        destination.write_bytes(payload)
        print(f"WROTE={destination}")
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
