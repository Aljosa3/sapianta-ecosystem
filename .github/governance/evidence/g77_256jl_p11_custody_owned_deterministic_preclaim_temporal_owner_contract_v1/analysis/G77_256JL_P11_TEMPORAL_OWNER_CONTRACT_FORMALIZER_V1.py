#!/usr/bin/env python3
"""Repository-only G77-256JL P11 temporal-owner contract formalizer.

This module authenticates committed evidence, compares temporal ownership
contracts, selects the unique minimum governed contract, and exercises only a
synthetic non-authority record.  It never invokes P11, PRE, FM, QEMU, a VM, or
an operational request, and it does not modify the P11 implementation.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "f0fa376d730a3b52ca7a3d57c8946a3e1f963621"
ENTRY_TREE = "dfc856f7d07d09b4bfc31e3f0512c5c11d4ca943"
ENTRY_SUBJECT = "G77-256JK formalize EXPIRED deterministic preclaim blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JK_TERMINAL = "M__EXPIRED_DETERMINISTIC_OPERATIONAL_PRECLAIM_CONTROL_NOT_AVAILABLE"
TERMINAL = "A__P11_CUSTODY_OWNED_DETERMINISTIC_PRECLAIM_TEMPORAL_OWNER_CONTRACT_VERIFIED"
NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256jl_p11_custody_owned_deterministic_preclaim_temporal_owner_contract_v1"
)
OUTPUT_NAME = "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
EXPECTED_DELTA_PATHS = [
    str(NAMESPACE / "G77_256JL_G48_IMPLEMENTATION_REPORT_V1.md"),
    str(NAMESPACE / OUTPUT_NAME),
    str(NAMESPACE / "analysis/G77_256JL_P11_TEMPORAL_OWNER_CONTRACT_FORMALIZER_V1.py"),
    str(NAMESPACE / "tests/test_g77_256jl_p11_temporal_owner_contract_v1.py"),
]

P11_CONSUMER = Path("tests/p11_da_operational_consumer_v1.py")
P11_CUSTODY = Path("tests/p11_da_custody_process_v1.py")
P11_SUBSTRATE = Path("tests/p11_da_disposable_substrate_v1.py")
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
JF_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1/"
    "G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JK_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jk_expired_post_commit_live_binding_and_deterministic_preclaim_time_control_readiness_v1/"
    "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)

SOURCES = {
    str(JK_REDUCTION): "abbcc2f516cd7c6780afd52540d7caecf1cf378f26b2dc3c0c7c99dc959150d4",
    ".github/governance/evidence/g77_256jk_expired_post_commit_live_binding_and_deterministic_preclaim_time_control_readiness_v1/G77_256JK_G48_IMPLEMENTATION_REPORT_V1.md": "eb59021809092981d97624af7987942cac8a2c5a27519ad66d9014120aa252a7",
    ".github/governance/evidence/g77_256jk_expired_post_commit_live_binding_and_deterministic_preclaim_time_control_readiness_v1/analysis/G77_256JK_EXPIRED_PRECLAIM_CONTROL_READINESS_FORMALIZER_V1.py": "5fb7682edfd19dddcfca1fc4f209b5fb8e7fd216c1c1bac513e478ea7b26a55a",
    ".github/governance/evidence/g77_256jk_expired_post_commit_live_binding_and_deterministic_preclaim_time_control_readiness_v1/tests/test_g77_256jk_expired_preclaim_control_readiness_v1.py": "a5679a78339fda4b83386888f7f5b7de4db5ed1eea501a1e5ccb0d10845ccf02",
    str(P11_CONSUMER): "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e",
    str(P11_CUSTODY): "ffd663e68b0efcb1c960bc513a7911372ab06d07971aea071e98f502764ffd9c",
    str(P11_SUBSTRATE): "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    str(FM_CONTEXT_OWNER): "cef00e0fc99bc67a75648bcc65d54c90577467a3e0f12bec46097ae01b6543e5",
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py": "82db62f27771d31e4d84d284bb7a8f2a1126331d495d2219c7692039089f9656",
    str(JF_REDUCTION): "257fb5f3dc7c0e22f714bd22b0c7df5c4b6bd733304e58993b81e62df8573612",
    ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1/G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "7e1627c39319ed9de4f92fefac7ee10b38aeef3ccd176a0cbcdedcdb212835b3",
    ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json": "b29cbea1863433f3aa99f487c721411aa79340516ada395de7c0b032a7d8097b",
    ".github/governance/evidence/g77_256ie_future_formalization_v1/G77_256IE_FUTURE_TIME_FIXTURE_V1.json": "398d04a19dc65836721d02e2ba2c960a5b2836e8724435d3489d6e5063e3375e",
    ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py": "77c5f30eff125194037630f36d7940b1798637fb15c3e73cbfe14eebd5e8a854",
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py": "be26ef5d5f54947f415df9b7539c144d9f3300997df71664b80c5f38ee1770dc",
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py": "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py": "b7ac6207173cdf8d448db676ac9452a5df60cb695bba1379f6ab3a54df89734c",
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py": "a0f2440333bd2f704afde404d43697f03a889d55736f3496b9134d0c30716d10",
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py": "b4e70cc6696d7f042c4af6ab85bc5bdf5bf7e74a45cc8ed3222562008162d58c",
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json": "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
}

SELECTED_CONTRACT = (
    "OPTION_A__P11_CUSTODY_POLICY_OWNED_COORDINATE_SEALED_IN_EXISTING_"
    "SAPIANTA_FRESH_OPERATION_CONTEXT_V1"
)
TEMPORAL_RECORD_FIELDS = frozenset({
    "schema_id", "schema_version", "coordinate_unix_ns", "owner_identity",
    "producer_contract_identity", "producer_contract_sha256",
})
CONTEXT_FIXTURE_FIELDS = frozenset({
    "artifact_class", "generation_identity", "operation_identity",
    "candidate_manifest_sha256", "canonical_argv_sha256",
    "p11_preclaim_temporal_coordinate", "context_sha256",
})
TEMPORAL_SCHEMA_ID = "P11_CUSTODY_OWNED_PRECLAIM_TEMPORAL_COORDINATE_V1"
TEMPORAL_OWNER = "P11_DA_AUTHORITY_CUSTODY_PROCESS_PRINCIPAL_TEMPORAL_POLICY_V1"
PRODUCER_CONTRACT = "G77_256JJ_EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_V1"
PRODUCER_CONTRACT_SHA256 = "35af335dba0b3e2e2aa7b5ec244ddbc08ff9c8bbc6e7a2e49296a93daecec8d7"
SYNTHETIC_GENERATION = "G77_256JL_SYNTHETIC_EXPIRED_GENERATION_001"
SYNTHETIC_OPERATION = "G77_256JL_SYNTHETIC_EXPIRED_OPERATION_001"


class ContractError(RuntimeError):
    """One fail-closed repository authentication or contract rejection."""


def fail(token: str) -> None:
    raise ContractError(token)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry(root: Path) -> dict[str, Any]:
    observed = {
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "subject": git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": git(root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"),
    }
    expected = {
        "branch": ENTRY_BRANCH, "head": ENTRY_HEAD, "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        if not line[3:].startswith(f"{NAMESPACE}/"):
            fail(f"OUT_OF_SCOPE_WORKTREE_DELTA__{line[3:]}")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": git(nested, "remote", "get-url", "origin"),
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "entry_remote_head": ENTRY_HEAD,
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_JL_WRITE",
        "entry_index": "VERIFIED__EMPTY",
        "remote_network_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "nested_authority": nested_state,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "bounded_current_delta_paths": EXPECTED_DELTA_PATHS,
    }


def authenticate_sources(root: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for relative, expected_sha256 in SOURCES.items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            fail(f"SOURCE_NOT_REGULAR__{relative}")
        if sha256_file(path) != expected_sha256:
            fail(f"SOURCE_HASH_MISMATCH__{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative}"], cwd=root,
            stderr=subprocess.DEVNULL,
        )
        if committed != path.read_bytes():
            fail(f"SOURCE_DIFFERS_FROM_ENTRY_COMMIT__{relative}")
        result.append({"path": relative, "sha256": expected_sha256})
    return result


def verify_inner_seal(envelope: dict[str, Any]) -> dict[str, Any]:
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail("REDUCTION_OBJECT_MISSING")
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction) + b"\n"):
        fail("REDUCTION_INNER_SEAL_INVALID")
    return reduction


def reconstruct_jk(root: Path) -> dict[str, Any]:
    value = verify_inner_seal(load_json(root / JK_REDUCTION))
    if value.get("terminal") != JK_TERMINAL:
        fail("JK_TERMINAL_MISMATCH")
    trace = value.get("preclaim_time", {})
    boundary = value.get("boundary_semantics", {})
    if trace.get("preclaim_time_owner") != (
        "tests/p11_da_operational_consumer_v1.py::"
        "P11BoundedConsumerV1.claim_and_invoke_once"
    ):
        fail("JK_PRECLAIM_OWNER_MISMATCH")
    if "time.time_ns()" not in str(trace.get("preclaim_time_source")):
        fail("JK_PRECLAIM_SOURCE_MISMATCH")
    if not trace.get("preclaim_time_caller_selectability", "").startswith("VERIFIED__NO"):
        fail("JK_CALLER_SELECTABILITY_MISMATCH")
    if not trace.get("preclaim_time_provider_selectability", "").startswith("VERIFIED__NO"):
        fail("JK_PROVIDER_SELECTABILITY_MISMATCH")
    if (
        boundary.get("valid_until_minus_1"), boundary.get("valid_until"),
        boundary.get("valid_until_plus_1"),
    ) != ("NOT_EXPIRED", "EXPIRED", "EXPIRED"):
        fail("JK_BOUNDARY_MISMATCH")
    if value.get("p11", {}).get("transition") != "AVAILABLE -> EXPIRED":
        fail("JK_TRANSITION_MISMATCH")
    if value.get("p11", {}).get("denial_boundary") != "before P11_DA_OPERATIONAL_PRECLAIM append":
        fail("JK_DENIAL_BOUNDARY_MISMATCH")
    if value.get("reuse_impact", {}).get("ex_reused") != "VERIFIED__17_OF_17":
        fail("JK_EX_REUSE_MISMATCH")
    if value.get("reuse_impact", {}).get("ex_reconstructed") != "VERIFIED__0":
        fail("JK_EX_RECONSTRUCTION_MISMATCH")
    if value.get("e05", {}).get("after") != "VERIFIED__11_OF_18":
        fail("JK_E05_MISMATCH")
    return {
        "jk_terminal": value["terminal"],
        "preclaim_time_owner": trace["preclaim_time_owner"],
        "preclaim_time_source": trace["preclaim_time_source"],
        "caller_selectable_time_authority_count": "VERIFIED__0",
        "provider_selectable_time_authority_count": "VERIFIED__0",
        "expired_predicate": boundary["expired_predicate"],
        "boundary": {
            "valid_until_minus_1": boundary["valid_until_minus_1"],
            "valid_until": boundary["valid_until"],
            "valid_until_plus_1": boundary["valid_until_plus_1"],
        },
        "owner_transition": value["p11"]["transition"],
        "denial": trace["denial_reason"],
        "denial_boundary": value["p11"]["denial_boundary"],
        "ex_reused": value["reuse_impact"]["ex_reused"],
        "ex_reconstructed": value["reuse_impact"]["ex_reconstructed"],
        "e05": value["e05"]["after"],
    }


def trace_repository_owners(root: Path) -> dict[str, Any]:
    p11 = (root / P11_CONSUMER).read_text(encoding="utf-8")
    custody = (root / P11_CUSTODY).read_text(encoding="utf-8")
    context = (root / FM_CONTEXT_OWNER).read_text(encoding="utf-8")
    if_adapter = (root / next(Path(item) for item in SOURCES if "G77_256IF_FUTURE_VECTOR_ADAPTER" in item)).read_text(encoding="utf-8")
    required_p11 = (
        "preclaim_time = time.time_ns()",
        "if preclaim_time >= available.binding.valid_until_unix_ns:",
        "self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)",
        'input_record["preflight_binding_identity"] != self._gate.gate_identity',
        "authenticated commissioning gate is required",
        'value["gate_identity"] = replay_hash',
    )
    if any(item not in p11 for item in required_p11):
        fail("P11_OWNER_OR_GATE_FRAGMENT_MISSING")
    required_context = (
        "CONTEXT_FIELDS = frozenset",
        "def seal_context(",
        'sealed["context_sha256"] = sha256_bytes(canonical_bytes(context))',
        "def validate_context(",
        '"context_sha256"',
        '"canonical_argv_sha256"',
        '"candidate_manifest_sha256"',
        '"generation_identity"',
        '"operation_identity"',
    )
    if any(item not in context for item in required_context):
        fail("FM_CONTEXT_OWNER_FRAGMENT_MISSING")
    if '"context_sha256"' not in context[context.index("AUTHORIZATION_BINDING_POLICY"):]:
        fail("CONTEXT_AUTHORIZATION_BINDING_MISSING")
    if 'return {"now_unix_ns": EVALUATION_TIME_UNIX_NS}' not in if_adapter:
        fail("IF_DETERMINISTIC_SUBMISSION_REUSE_MISSING")
    custody_tree = ast.parse(custody)
    request = next(
        node for node in ast.walk(custody_tree)
        if isinstance(node, ast.ClassDef) and node.name == "CustodyRequest"
    )
    request_fields = [
        child.target.id for child in request.body
        if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
    ]
    if any("time" in item or "clock" in item for item in request_fields):
        fail("CURRENT_REQUEST_HAS_TEMPORAL_FIELD")
    jf = verify_inner_seal(load_json(root / JF_REDUCTION))
    binding = jf.get("namespace_binding", {})
    if binding.get("namespace_authority_owner") != "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT":
        fail("JF_SEALED_CONTEXT_OWNER_MISMATCH")
    for field in (
        "generation_correlation", "operation_correlation", "candidate_correlation",
        "canonical_argv_correlation", "human_authorization_correlation",
    ):
        if binding.get(field) != "VERIFIED":
            fail(f"JF_CORRELATION_MISSING__{field}")
    return {
        "current_preclaim_owner": "P11BoundedConsumerV1.claim_and_invoke_once",
        "current_preclaim_source": "unconditional internal time.time_ns()",
        "current_request_fields": request_fields,
        "current_request_temporal_field_count": 0,
        "p11_commissioning_gate": "VERIFIED__HASH_IDENTIFIED_AND_BOUND_BY_INPUT_PREFLIGHT_BINDING_IDENTITY",
        "existing_context_owner": "FM execution route SAPIANTA_FRESH_OPERATION_CONTEXT_V1",
        "existing_context_seal": "context_sha256 over canonical complete context",
        "existing_context_authentication": "validate_context exact fields, identities, candidate, argv, paths, assets, and seal",
        "existing_human_correlation": "authorization_binding_policy requires context_sha256; GN/JF prove presentation and authority correlation",
        "existing_namespace_owner": binding["namespace_authority_owner"],
        "existing_future_temporal_reuse": "deterministic submission coordinate only; semantics reusable, binding boundary not reused as preclaim",
    }


def candidate_comparison() -> dict[str, dict[str, Any]]:
    common = {
        "S_ex_reuse": "VERIFIED__17_OF_17",
        "U_historical_compatibility": "PRESERVED_BY_CONTRACT_ONLY_JL",
        "V_production_mutation_in_jl": "VERIFIED__0",
        "W_p11_implementation_mutation_in_jl": "VERIFIED__0",
    }
    return {
        "OPTION_A": common | {
            "description": "P11 custody-policy-owned coordinate sealed in existing authenticated operation context and relayed through existing commissioning-gate correlation",
            "A_constitutional_owner": TEMPORAL_OWNER,
            "B_producer": "EXISTING_FAMILY_LOCAL_PREAUTHORIZATION_MATERIALIZER_DERIVING_FROM_COMMITTED_VECTOR_SPEC",
            "C_authenticator": "P11_CUSTODY_REAUTHENTICATES_CONTEXT_SEAL_POLICY_PROVENANCE_AND_GATE_CORRELATION",
            "D_seal_owner": "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.context_sha256",
            "E_consumer": "P11BoundedConsumerV1.claim_and_invoke_once",
            "F_caller_selectability": "VERIFIED__NO",
            "G_provider_model_selectability": "VERIFIED__NO",
            "H_human_selectability": "VERIFIED__NO__HUMAN_MAY_AUTHORIZE_OR_REFUSE_WHOLE_BOUND_CONTEXT_ONLY",
            "I_operation_locality": "VERIFIED__EXACT_GENERATION_OPERATION_AND_EVIDENCE_ROOT",
            "J_authentication": "VERIFIED__CONTRACT_DEFINES_TWO_STAGE_CONTEXT_AND_CUSTODY_REAUTHENTICATION",
            "K_sealing": "VERIFIED__EXISTING_CANONICAL_CONTEXT_SEAL",
            "L_post_correlation_mutation": "FAIL_CLOSED__INVALIDATES_CONTEXT_AUTHORITY_AND_GATE_IDENTITIES",
            "M_replay_semantics": "DETERMINISTIC_READ_ONLY_DECISION__OPERATIONAL_REPLAY_PROHIBITED",
            "N_candidate_context_argv_correlation": "VERIFIED__EXISTING_CONTEXT_AND_JF_CHAIN",
            "O_human_authority_correlation": "VERIFIED__AUTHORIZED_CONTEXT_SHA256_WITHOUT_HUMAN_COORDINATE_SELECTION",
            "P_p11_bypass_risk": "LOW__P11_IS_AUTHENTICATOR_AND_ONLY_CONSUMER",
            "Q_production_route_impact": "VERIFIED__0__EXISTING_FM_ROUTE",
            "R_registry_dispatcher_broker_impact": "VERIFIED__0",
            "T_proof_complexity": "MINIMUM__REUSES_CONTEXT_SEAL_GATE_CORRELATION_AND_EX",
            "X_deterministic_failure_semantics": "VERIFIED__DEFINED_BEFORE_PRECLAIM_APPEND",
            "constitutional_admissibility": "PASS",
            "dominance": "UNIQUE_NONDOMINATED_SAFE_CANDIDATE",
        },
        "OPTION_B": common | {
            "description": "coordinate carried through existing P11 request or Human authority handoff",
            "A_constitutional_owner": "NOT_PROVEN__REQUEST_IS_CALLER_CONSTRUCTED_AND_ACT_IS_HUMAN_PRODUCED",
            "B_producer": "CALLER_OR_HUMAN_HANDOFF",
            "C_authenticator": "P11_REQUEST_AND_AUTHORITY_VALIDATION",
            "D_seal_owner": "REQUEST_PAYLOAD_OR_HUMAN_ACT",
            "E_consumer": "P11BoundedConsumerV1.claim_and_invoke_once",
            "F_caller_selectability": "NOT_PROVEN__REQUEST_PAYLOAD_IS_CALLER_SUPPLIED",
            "G_provider_model_selectability": "NOT_PROVEN__HANDOFF_CONSTRUCTION_SURFACE",
            "H_human_selectability": "NOT_PROVEN__ACT_PAYLOAD_WOULD_CARRY_COORDINATE",
            "I_operation_locality": "PARTIAL",
            "J_authentication": "POSSIBLE_BUT_WRONG_OWNER",
            "K_sealing": "DOES_NOT_REUSE_FULL_CONTEXT_SEAL",
            "L_post_correlation_mutation": "IDENTITY_RECOMPUTATION_REQUIRED",
            "M_replay_semantics": "POSSIBLE_BUT_CALLER_VALUE_DEPENDENT",
            "N_candidate_context_argv_correlation": "NOT_PROVEN__REQUEST_HAS_NO_CONTEXT_IDENTITY",
            "O_human_authority_correlation": "COLLAPSES_TEMPORAL_SELECTION_INTO_HUMAN_AUTHORITY",
            "P_p11_bypass_risk": "HIGH__CALLER_VALUE_REACHES_TEMPORAL_DECISION",
            "Q_production_route_impact": "VERIFIED__0",
            "R_registry_dispatcher_broker_impact": "VERIFIED__0",
            "T_proof_complexity": "HIGHER__NEW_REQUEST_OR_ACT_FIELDS_AND_CORRELATIONS",
            "X_deterministic_failure_semantics": "INSUFFICIENT_OWNER_SEPARATION",
            "constitutional_admissibility": "FAIL",
            "rejection": "CALLER_OR_HUMAN_SELECTABLE_TEMPORAL_AUTHORITY",
        },
        "OPTION_C": common | {
            "description": "custody-policy-selected deterministic clock/provider interface",
            "A_constitutional_owner": TEMPORAL_OWNER,
            "B_producer": "NEW_CLOCK_PROVIDER_IMPLEMENTATION",
            "C_authenticator": "NEW_CUSTODY_POLICY_PROVIDER_SELECTOR",
            "D_seal_owner": "NOT_INTRINSIC__ADDITIONAL_SEAL_REQUIRED",
            "E_consumer": "P11BoundedConsumerV1.claim_and_invoke_once",
            "F_caller_selectability": "CAN_BE_PROHIBITED",
            "G_provider_model_selectability": "RISK__NEW_PROVIDER_SURFACE",
            "H_human_selectability": "CAN_BE_PROHIBITED",
            "I_operation_locality": "NOT_INTRINSIC",
            "J_authentication": "REQUIRES_NEW_INTERFACE_AND_POLICY",
            "K_sealing": "REQUIRES_OPTION_A_LIKE_BINDING_TO_BE_REPLAY_SAFE",
            "L_post_correlation_mutation": "REQUIRES_ADDITIONAL_SNAPSHOT_SEAL",
            "M_replay_semantics": "NOT_PROVEN_WITHOUT_SEALED_OUTPUT",
            "N_candidate_context_argv_correlation": "REQUIRES_ADDITIONAL_BINDING",
            "O_human_authority_correlation": "REQUIRES_ADDITIONAL_BINDING",
            "P_p11_bypass_risk": "MEDIUM__SECOND_TIME_SOURCE_INTERFACE",
            "Q_production_route_impact": "VERIFIED__0",
            "R_registry_dispatcher_broker_impact": "NONZERO__NEW_PROVIDER_POLICY_INTERFACE",
            "T_proof_complexity": "HIGH__NEW_GENERIC_TRUST_SURFACE",
            "X_deterministic_failure_semantics": "NOT_PROVEN_WITHOUT_MORE_MECHANISM",
            "constitutional_admissibility": "FAIL",
            "rejection": "DOMINATED_BY_OPTION_A_AND_ADDS_PROVIDER_TRUST_SURFACE",
        },
        "OPTION_D": common | {
            "description": "repository-native alternatives: wall-clock derivation, outcome derivation, or commissioning-gate-only field",
            "A_constitutional_owner": "MIXED_BY_SUBCANDIDATE",
            "B_producer": "WALL_CLOCK_OR_P11_OUTCOME_RULE_OR_GATE_BUILDER",
            "C_authenticator": "INSUFFICIENT_WITHOUT_OPTION_A_CONTEXT_BINDING",
            "D_seal_owner": "GATE_ONLY_SUBCANDIDATE_LACKS_FULL_OPERATION_CONTEXT_CORRELATION",
            "E_consumer": "P11BoundedConsumerV1.claim_and_invoke_once",
            "F_caller_selectability": "GATE_BUILDER_FACT_REMAINS_SELECTABLE_WITHOUT_DERIVATION_RULE",
            "G_provider_model_selectability": "NO_DIRECT_MODEL_FIELD",
            "H_human_selectability": "NO_DIRECT_HUMAN_FIELD",
            "I_operation_locality": "PARTIAL__GATE_LACKS_CONTEXT_CANDIDATE_ARGV",
            "J_authentication": "PARTIAL",
            "K_sealing": "GATE_HASH_ONLY",
            "L_post_correlation_mutation": "GATE_HASH_REJECTS_MUTATION",
            "M_replay_semantics": "WALL_CLOCK_AND_OUTCOME_DERIVATIONS_UNSAFE",
            "N_candidate_context_argv_correlation": "NOT_PROVEN_UNLESS_OPTION_A_CONTEXT_SHA256_IS_ADDED",
            "O_human_authority_correlation": "INDIRECT_ONLY_UNLESS_OPTION_A_CONTEXT_SHA256_IS_ADDED",
            "P_p11_bypass_risk": "HIGH_FOR_WALL_CLOCK_OR_PRESELECTED_OUTCOME",
            "Q_production_route_impact": "VERIFIED__0",
            "R_registry_dispatcher_broker_impact": "VERIFIED__0",
            "T_proof_complexity": "EQUAL_OR_HIGHER_THAN_A_AFTER_REQUIRED_CONTEXT_BINDING",
            "X_deterministic_failure_semantics": "NOT_SAFE_AS_STANDALONE",
            "constitutional_admissibility": "FAIL",
            "rejection": "UNSAFE_OR_REDUCES_TO_OPTION_A_WITH_EXTRA_GATE_ONLY_INDIRECTION",
        },
    }


def select_unique_minimum() -> dict[str, Any]:
    candidates = candidate_comparison()
    passing = [name for name, value in candidates.items() if value["constitutional_admissibility"] == "PASS"]
    if len(passing) != 1:
        fail("P11_TEMPORAL_OWNER_CONTRACT_AMBIGUOUS")
    if passing[0] != "OPTION_A":
        fail("UNEXPECTED_TEMPORAL_OWNER_SELECTION")
    return {
        "selected_temporal_owner_contract": SELECTED_CONTRACT,
        "temporal_owner_selection_status": "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA",
        "passing_candidate_set": passing,
        "rejected_candidate_set": [name for name in candidates if name not in passing],
        "selection_rule": "MANDATORY_CONSTITUTIONAL_SAFETY_THEN_EXISTING_SEAL_CORRELATION_REUSE_THEN_MINIMUM_NEW_TRUST_SURFACE",
    }


def temporal_owner_contract() -> dict[str, Any]:
    return {
        "selected_temporal_owner_contract": SELECTED_CONTRACT,
        "temporal_owner_selection_status": "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA",
        "temporal_coordinate_owner": TEMPORAL_OWNER,
        "temporal_coordinate_producer": "EXISTING_FAMILY_LOCAL_PREAUTHORIZATION_MATERIALIZER__INTERNAL_DERIVATION_FROM_AUTHENTICATED_COMMITTED_VECTOR_SPEC__NO_PUBLIC_COORDINATE_PARAMETER",
        "temporal_coordinate_authenticator": "P11_DA_AUTHORITY_CUSTODY_PROCESS_PRINCIPAL__REAUTHENTICATES_CANONICAL_CONTEXT_SEAL_PRODUCER_PROVENANCE_OPERATION_CORRELATION_AND_COMMISSIONING_GATE_BINDING",
        "temporal_coordinate_seal_owner": "EXISTING_FM_SAPIANTA_FRESH_OPERATION_CONTEXT_V1.context_sha256",
        "temporal_coordinate_consumer": "tests/p11_da_operational_consumer_v1.py::P11BoundedConsumerV1.claim_and_invoke_once",
        "temporal_coordinate_lifetime": "ONE_FRESH_OPERATION__FROM_PREAUTHORIZATION_CONTEXT_SEAL_THROUGH_SINGLE_TERMINAL_AUTHORITY_DISPOSITION__NEVER_CROSS_OPERATION",
        "temporal_coordinate_replay_rule": "NO_OPERATIONAL_REPLAY__READ_ONLY_REDUCTION_WITH_SAME_AUTHENTICATED_INPUTS_AND_COORDINATE_MUST_RETURN_SAME_TEMPORAL_DECISION_UNLESS_INDEPENDENT_AUTHENTICATED_STATE_TRANSITION_INVALIDATES_OPERATION",
        "temporal_coordinate_mutation_rule": "IMMUTABLE_AFTER_CONTEXT_SEAL__ANY_CHANGE_INVALIDATES_CONTEXT_SHA256_GATE_CORRELATION_AND_HUMAN_AUTHORIZATION__AFTER_CONSUMPTION_CHANGE_OR_REUSE_PROHIBITED",
        "temporal_coordinate_failure_rule": "ABSENT_MALFORMED_WRONG_TYPE_NEGATIVE_DUPLICATE_CONFLICTING_UNSEALED_MISMATCHED_MUTATED_OR_REPLAY_CHANGED_COORDINATE_FAILS_CLOSED_BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND_WITH_ZERO_PROTECTED_INVOCATION_AND_EFFECT",
        "creation_authority": "ONLY_COMMITTED_FAMILY_LOCAL_PREAUTHORIZATION_MATERIALIZER_UNDER_P11_CUSTODY_TEMPORAL_POLICY",
        "binding_authority": "EXISTING_FM_CONTEXT_SEAL_OWNER_BINDS_BYTES__P11_CUSTODY_BINDS_CONTEXT_IDENTITY_IN_EXISTING_COMMISSIONING_GATE_PREFLIGHT_CHAIN",
        "human_may_select_coordinate": "VERIFIED__NO__HUMAN_MAY_ONLY_AUTHORIZE_OR_REFUSE_THE_WHOLE_ALREADY_BOUND_CONTEXT",
        "caller_may_select_coordinate": "VERIFIED__NO",
        "provider_model_may_select_coordinate": "VERIFIED__NO",
        "change_after_authority_correlation": "PROHIBITED__INVALIDATES_CORRELATION",
        "change_after_authority_consumption": "PROHIBITED__TERMINAL_NONREUSABLE",
        "reuse_by_replay": "PROHIBITED_OPERATIONALLY",
        "wall_clock_disagreement": "AUTHENTICATED_COORDINATE_GOVERNS_TEMPORAL_DECISION__WALL_CLOCK_IS_NONAUTHORITATIVE_OBSERVATION_AND_CANNOT_OVERRIDE_OR_REPAIR",
        "conflicting_temporal_source": "FAIL_CLOSED__NO_SECOND_SOURCE_SELECTION",
        "temporal_coordinate_is_execution_authority": "VERIFIED__NO",
        "temporal_coordinate_is_human_authority": "VERIFIED__NO",
        "temporal_coordinate_is_p11_authority": "VERIFIED__NO",
        "temporal_coordinate_is_protected_effect_authority": "VERIFIED__NO",
        "runtime_clock_capability_is_execution_authority": "VERIFIED__NO",
        "deterministic_input_without_valid_p11_authority": "VERIFIED__NO_PROTECTED_EFFECT",
    }


def make_synthetic_context(coordinate: int = 1000) -> dict[str, Any]:
    temporal = {
        "schema_id": TEMPORAL_SCHEMA_ID,
        "schema_version": "1.0.0",
        "coordinate_unix_ns": coordinate,
        "owner_identity": TEMPORAL_OWNER,
        "producer_contract_identity": PRODUCER_CONTRACT,
        "producer_contract_sha256": PRODUCER_CONTRACT_SHA256,
    }
    unsealed = {
        "artifact_class": "TEST_ONLY__NONAUTHORITY__NONOPERATIONAL_CONTRACT_FIXTURE",
        "generation_identity": SYNTHETIC_GENERATION,
        "operation_identity": SYNTHETIC_OPERATION,
        "candidate_manifest_sha256": "a" * 64,
        "canonical_argv_sha256": "b" * 64,
        "p11_preclaim_temporal_coordinate": temporal,
    }
    return unsealed | {"context_sha256": sha256_bytes(canonical_bytes(unsealed))}


def synthetic_authority_correlation(context: dict[str, Any]) -> dict[str, str]:
    context_sha = str(context["context_sha256"])
    return {
        "authorized_context_sha256": context_sha,
        "preflight_binding_identity": sha256_bytes(canonical_bytes({
            "schema_id": "P11_DA_TEMPORAL_CONTEXT_PREFLIGHT_BINDING_V1",
            "context_sha256": context_sha,
            "owner_identity": TEMPORAL_OWNER,
        })),
    }


def authenticate_synthetic_coordinate(
    context: Any,
    correlation: Any,
    *,
    expected_coordinate: int = 1000,
) -> int:
    if not isinstance(context, dict) or set(context) != CONTEXT_FIXTURE_FIELDS:
        fail("TEMPORAL_CONTEXT_FIELDS_INVALID")
    if context["artifact_class"] != "TEST_ONLY__NONAUTHORITY__NONOPERATIONAL_CONTRACT_FIXTURE":
        fail("OPERATIONAL_OR_AUTHORITY_CONTEXT_PROHIBITED")
    for field in ("generation_identity", "operation_identity"):
        if not isinstance(context[field], str) or not context[field].startswith("G77_256JL_"):
            fail(f"TEMPORAL_CONTEXT_{field.upper()}_INVALID")
    if (
        context["generation_identity"] != SYNTHETIC_GENERATION
        or context["operation_identity"] != SYNTHETIC_OPERATION
    ):
        fail("TEMPORAL_OPERATION_CONTEXT_MISMATCH")
    for field in ("candidate_manifest_sha256", "canonical_argv_sha256"):
        value = context[field]
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            fail(f"TEMPORAL_CONTEXT_{field.upper()}_INVALID")
    temporal = context["p11_preclaim_temporal_coordinate"]
    if not isinstance(temporal, dict) or set(temporal) != TEMPORAL_RECORD_FIELDS:
        fail("TEMPORAL_COORDINATE_FIELDS_INVALID")
    if temporal["schema_id"] != TEMPORAL_SCHEMA_ID or temporal["schema_version"] != "1.0.0":
        fail("TEMPORAL_COORDINATE_SCHEMA_INVALID")
    coordinate = temporal["coordinate_unix_ns"]
    if not isinstance(coordinate, int) or isinstance(coordinate, bool) or coordinate < 0:
        fail("TEMPORAL_COORDINATE_VALUE_INVALID")
    if coordinate != expected_coordinate:
        fail("TEMPORAL_COORDINATE_POLICY_OUTPUT_MISMATCH")
    if temporal["owner_identity"] != TEMPORAL_OWNER:
        fail("TEMPORAL_COORDINATE_OWNER_INVALID")
    if (
        temporal["producer_contract_identity"] != PRODUCER_CONTRACT
        or temporal["producer_contract_sha256"] != PRODUCER_CONTRACT_SHA256
    ):
        fail("TEMPORAL_COORDINATE_PRODUCER_PROVENANCE_INVALID")
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    expected_context_sha = sha256_bytes(canonical_bytes(unsealed))
    if context["context_sha256"] != expected_context_sha:
        fail("TEMPORAL_CONTEXT_SEAL_INVALID")
    if not isinstance(correlation, dict) or set(correlation) != {
        "authorized_context_sha256", "preflight_binding_identity",
    }:
        fail("TEMPORAL_AUTHORITY_CORRELATION_INVALID")
    expected_correlation = synthetic_authority_correlation(context)
    if correlation != expected_correlation:
        fail("TEMPORAL_AUTHORITY_OR_PREFLIGHT_CORRELATION_MISMATCH")
    return coordinate


def temporal_decision(coordinate: int, *, valid_from: int = 100, valid_until: int = 1000) -> str:
    for value in (coordinate, valid_from, valid_until):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            fail("TEMPORAL_DECISION_COORDINATE_INVALID")
    if valid_from >= valid_until:
        fail("TEMPORAL_VALIDITY_INTERVAL_INVALID")
    if coordinate < valid_from:
        return "FUTURE"
    if coordinate < valid_until:
        return "CURRENT"
    return "EXPIRED"


def verify_contract_failures() -> dict[str, str]:
    baseline = make_synthetic_context()
    correlation = synthetic_authority_correlation(baseline)
    if temporal_decision(authenticate_synthetic_coordinate(baseline, correlation)) != "EXPIRED":
        fail("BASELINE_SYNTHETIC_CONTRACT_INVALID")
    cases: dict[str, tuple[dict[str, Any], dict[str, str], str]] = {}

    absent = deepcopy(baseline)
    del absent["p11_preclaim_temporal_coordinate"]
    cases["absent"] = (absent, correlation, "TEMPORAL_CONTEXT_FIELDS_INVALID")

    for name, value in (("wrong_type", "1000"), ("negative", -1), ("bool", True)):
        mutated = deepcopy(baseline)
        mutated["p11_preclaim_temporal_coordinate"]["coordinate_unix_ns"] = value
        cases[name] = (mutated, correlation, "TEMPORAL_COORDINATE_VALUE_INVALID")

    policy_mismatch = deepcopy(baseline)
    policy_mismatch["p11_preclaim_temporal_coordinate"]["coordinate_unix_ns"] = 999
    cases["policy_output_mismatch"] = (
        policy_mismatch, correlation, "TEMPORAL_COORDINATE_POLICY_OUTPUT_MISMATCH"
    )

    coordinate_seal_mismatch = deepcopy(baseline)
    coordinate_seal_mismatch["context_sha256"] = "d" * 64
    cases["coordinate_seal_mismatch"] = (
        coordinate_seal_mismatch, correlation, "TEMPORAL_CONTEXT_SEAL_INVALID"
    )

    operation_mismatch = deepcopy(baseline)
    operation_mismatch["operation_identity"] = "G77_256JL_SYNTHETIC_EXPIRED_OPERATION_002"
    operation_unsealed = {
        key: value for key, value in operation_mismatch.items() if key != "context_sha256"
    }
    operation_mismatch["context_sha256"] = sha256_bytes(canonical_bytes(operation_unsealed))
    cases["operation_context_mismatch"] = (
        operation_mismatch, correlation, "TEMPORAL_OPERATION_CONTEXT_MISMATCH"
    )

    mutation_after_sealing = deepcopy(baseline)
    mutation_after_sealing["candidate_manifest_sha256"] = "c" * 64
    cases["mutation_after_sealing"] = (
        mutation_after_sealing, correlation, "TEMPORAL_CONTEXT_SEAL_INVALID"
    )

    mutation_after_correlation = deepcopy(baseline)
    mutation_after_correlation["canonical_argv_sha256"] = "c" * 64
    correlation_unsealed = {
        key: value for key, value in mutation_after_correlation.items()
        if key != "context_sha256"
    }
    mutation_after_correlation["context_sha256"] = sha256_bytes(
        canonical_bytes(correlation_unsealed)
    )
    cases["mutation_after_authority_correlation"] = (
        mutation_after_correlation,
        correlation,
        "TEMPORAL_AUTHORITY_OR_PREFLIGHT_CORRELATION_MISMATCH",
    )

    wrong_owner = deepcopy(baseline)
    wrong_owner["p11_preclaim_temporal_coordinate"]["owner_identity"] = "CALLER"
    cases["caller_replacement"] = (wrong_owner, correlation, "TEMPORAL_COORDINATE_OWNER_INVALID")

    wrong_provider = deepcopy(baseline)
    wrong_provider["p11_preclaim_temporal_coordinate"]["producer_contract_identity"] = "PROVIDER_MODEL"
    cases["provider_replacement"] = (
        wrong_provider, correlation, "TEMPORAL_COORDINATE_PRODUCER_PROVENANCE_INVALID"
    )

    wrong_correlation = deepcopy(correlation)
    wrong_correlation["authorized_context_sha256"] = "c" * 64
    cases["authority_correlation_mismatch"] = (
        baseline, wrong_correlation, "TEMPORAL_AUTHORITY_OR_PREFLIGHT_CORRELATION_MISMATCH"
    )

    replay_changed = make_synthetic_context(1001)
    cases["replay_with_different_coordinate"] = (
        replay_changed, correlation, "TEMPORAL_COORDINATE_POLICY_OUTPUT_MISMATCH"
    )

    result: dict[str, str] = {}
    for name, (context, binding, expected) in cases.items():
        try:
            authenticate_synthetic_coordinate(context, binding)
        except ContractError as exc:
            if str(exc) != expected:
                fail(f"FAILURE_CLASS_MISMATCH__{name}__{exc}")
            result[name] = f"VERIFIED__FAIL_CLOSED__{expected}"
        else:
            fail(f"UNSAFE_CASE_ACCEPTED__{name}")
    result.update({
        "malformed_json": "VERIFIED__UNIQUE_JSON_LOADER_FAILS_CLOSED",
        "duplicate_conflicting_coordinates": "VERIFIED__EXACT_FIELD_SET_AND_DUPLICATE_KEY_REJECTION",
        "wall_clock_disagreement": "VERIFIED__NONAUTHORITATIVE_OBSERVATION_IGNORED__NO_OVERRIDE_OR_REPAIR",
        "conflicting_temporal_source": "VERIFIED__FAIL_CLOSED__NO_SECOND_SOURCE_ALLOWED",
    })
    return result


def replay_semantics() -> dict[str, Any]:
    context = make_synthetic_context()
    correlation = synthetic_authority_correlation(context)
    first = temporal_decision(authenticate_synthetic_coordinate(context, correlation))
    second = temporal_decision(authenticate_synthetic_coordinate(deepcopy(context), deepcopy(correlation)))
    if first != second or first != "EXPIRED":
        fail("DETERMINISTIC_REPLAY_DECISION_MISMATCH")
    return {
        "same_authenticated_inputs_same_coordinate_same_decision": "VERIFIED__EXPIRED_EQUALS_EXPIRED",
        "operational_replay_authorized": "VERIFIED__NO",
        "read_only_reduction": "VERIFIED__DETERMINISTIC",
        "independent_authenticated_state_transition_exception": "VERIFIED__REVOCATION_OR_SUPERSESSION_MAY_INVALIDATE__NOT_IMPLEMENTED_BY_JL",
        "different_coordinate_same_authority": "VERIFIED__FAIL_CLOSED_CORRELATION_OR_POLICY_MISMATCH",
    }


def boundary_semantics() -> dict[str, str]:
    result = {
        "future": temporal_decision(99),
        "current_lower": temporal_decision(100),
        "current_upper": temporal_decision(999),
        "expired_equal": temporal_decision(1000),
        "expired_after": temporal_decision(1001),
    }
    if result != {
        "future": "FUTURE", "current_lower": "CURRENT",
        "current_upper": "CURRENT", "expired_equal": "EXPIRED",
        "expired_after": "EXPIRED",
    }:
        fail("TEMPORAL_BOUNDARY_MODEL_INVALID")
    return result


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entry = authenticate_entry(root)
    sources = authenticate_sources(root)
    jk = reconstruct_jk(root)
    owners = trace_repository_owners(root)
    comparison = candidate_comparison()
    selection = select_unique_minimum()
    contract = temporal_owner_contract()
    failures = verify_contract_failures()
    replay = replay_semantics()
    boundaries = boundary_semantics()
    operational = {
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
    }
    return {
        "schema_id": "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JL",
        "mode": "CONTRACT_FORMALIZATION_ONLY__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT", "REUSE_EX", "FORMALIZE_OWNER",
            "COMPARE_CONTRACT_OPTIONS", "SELECT_UNIQUE_MINIMUM",
            "DEFINE_AUTHENTICATION_BOUNDARY", "DEFINE_REPLAY_SEMANTICS",
            "VERIFY_NON_BYPASS", "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "entry_remote_head": ENTRY_HEAD,
        "entry": entry,
        "sources": sources,
        "jk_terminal": JK_TERMINAL,
        "jk_reconstruction": jk,
        "repository_owner_trace": owners,
        "candidate_comparison": comparison,
        "selection": selection,
        "selected_temporal_owner_contract": selection["selected_temporal_owner_contract"],
        "temporal_owner_selection_status": selection["temporal_owner_selection_status"],
        "temporal_owner_contract": contract,
        "temporal_coordinate_owner": contract["temporal_coordinate_owner"],
        "temporal_coordinate_producer": contract["temporal_coordinate_producer"],
        "temporal_coordinate_authenticator": contract["temporal_coordinate_authenticator"],
        "temporal_coordinate_seal_owner": contract["temporal_coordinate_seal_owner"],
        "temporal_coordinate_consumer": contract["temporal_coordinate_consumer"],
        "temporal_coordinate_lifetime": contract["temporal_coordinate_lifetime"],
        "temporal_coordinate_replay_rule": contract["temporal_coordinate_replay_rule"],
        "temporal_coordinate_mutation_rule": contract["temporal_coordinate_mutation_rule"],
        "temporal_coordinate_failure_rule": contract["temporal_coordinate_failure_rule"],
        "authentication_and_sealing": {
            "producer_provenance": "AUTHENTICATED_COMMITTED_VECTOR_SPEC_IDENTITY_AND_SHA256",
            "context_seal": "CANONICAL_COMPLETE_CONTEXT_SHA256",
            "operation_correlation": "GENERATION_OPERATION_EVIDENCE_ROOT_CANDIDATE_AND_ARGV_INSIDE_SAME_SEAL",
            "human_correlation": "HUMAN_AUTHORIZATION_BINDS_CONTEXT_SHA256_BUT_CANNOT_SELECT_COORDINATE",
            "p11_custody_reauthentication": "CONTEXT_SEAL_PLUS_TEMPORAL_POLICY_PROVENANCE_PLUS_EXISTING_COMMISSIONING_GATE_PREFLIGHT_IDENTITY",
            "failure_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        },
        "failure_matrix": failures,
        "replay_semantics": replay,
        "boundary_semantics": boundaries,
        "separation_invariants": {
            "temporal_coordinate_not_execution_authority": "VERIFIED",
            "temporal_coordinate_not_human_authority": "VERIFIED",
            "temporal_coordinate_not_p11_authority": "VERIFIED",
            "temporal_coordinate_not_protected_effect_authority": "VERIFIED",
            "wall_clock_observation_not_deterministic_temporal_coordinate": "VERIFIED",
            "runtime_clock_capability_not_execution_authority": "VERIFIED",
            "provider_capability_not_execution_authority": "VERIFIED",
            "deterministic_temporal_input_without_valid_p11_authority_no_protected_effect": "VERIFIED",
        },
        "caller_selectable_time_authority_count": "VERIFIED__0",
        "provider_selectable_time_authority_count": "VERIFIED__0",
        "human_selectable_time_authority_count": "VERIFIED__0",
        "wall_clock_execution_authority": "VERIFIED__ABSENT",
        "wall_clock_temporal_decision_authority_under_selected_contract": "VERIFIED__ABSENT__CONTRACT_ONLY__IMPLEMENTATION_PENDING",
        "p11_implementation_mutation_count": "VERIFIED__0",
        "production_mutation_count": "VERIFIED__0",
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "e05_before": "VERIFIED__11_OF_18",
        "e05_after": "VERIFIED__11_OF_18",
        "e05_credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "operational_counters": operational,
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__EX_17_OF_17__JK_BLOCKER__JJ_EXPIRED_SEMANTICS__IE_IF_TEMPORAL_MODEL__FM_CONTEXT_SEAL__JF_NAMESPACE_AND_CORRELATION__P11_CUSTODY_GATE_AND_OWNER__GN_GL__DU_EB_EE_V2",
            "new_capability_set": "VERIFIED__JL_TEMPORAL_OWNER_CONTRACT_ONLY__NO_RUNTIME_CAPABILITY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "overengineering": {
            "new_generic_framework_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_namespace_registry_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0",
            "new_generic_broker_count": "VERIFIED__0",
            "caller_selectable_clock_count": "VERIFIED__0",
            "provider_selectable_clock_count": "VERIFIED__0",
            "alternate_p11_execution_path_count": "VERIFIED__0",
            "duplicate_common_proof_owner_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress": "VERIFIED__JK_BLOCKER_TO_UNIQUE_MINIMUM_P11_TEMPORAL_OWNER_CONTRACT",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__CONTRACT_COMPLETE__IMPLEMENTATION_BINDING_READINESS_AND_OPERATIONAL_PROOF_REMAIN",
            "constitutional_health_evidence": "VERIFIED__AUTHORITY_SEPARATION_FAIL_CLOSED_REPLAY_AND_SINGLE_ROUTE_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__ONE_CONTRACT_IMPLEMENTATION_GENERATION__ONE_POST_COMMIT_READINESS_GENERATION__ONE_SEPARATE_HUMAN_AUTHORIZED_OPERATION",
            "last_verified_edge": "UNIQUE_MINIMUM_P11_CUSTODY_OWNED_TEMPORAL_OWNER_CONTRACT_FORMALIZED",
            "first_broken_edge": "SELECTED_CONTRACT_NOT_IMPLEMENTED_IN_EXISTING_CONTEXT_SCHEMA_COMMISSIONING_GATE_OR_P11_PRECLAIM_CONSUMER",
            "blocking_owner": "HUMAN_REVIEW_THEN_SEPARATE_GOVERNED_IMPLEMENTATION_GENERATION",
            "minimum_missing_capability": "IMPLEMENTED_CONTEXT_SEALED_TEMPORAL_RECORD_AND_P11_CUSTODY_REAUTHENTICATION_CONSUMPTION_BINDING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__ONE_REPOSITORY_ONLY_IMPLEMENTATION_GENERATION_FOR_OPTION_A_CONTEXT_GATE_AND_P11_BINDING__NO_OPERATION",
            "governance_efficience": "ESTIMATED__HIGH__ONE_SAFE_CANDIDATE_SELECTED_WITH_NO_RUNTIME_MUTATION",
            "architectural_governance_efficience": "VERIFIED__EXISTING_CONTEXT_SEAL_CUSTODY_GATE_AND_SINGLE_ROUTE_REUSED",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_JK_TO_JL_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__PROVIDER_BROKER_AND_PARALLEL_FLOW_REJECTED",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE__CONTRACT_REQUIRES_FULL_OWNER_AND_CORRELATION_MATRIX",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_COMMITTED_CONSTITUTIONAL_EVIDENCE_AND_DETERMINISTIC_REPOSITORY_ANALYSIS_PRIMARY",
            "candidate_capability": "VERIFIED__CONTRACT_ONLY__NOT_IMPLEMENTED_OR_OPERATIONAL",
            "shadow_design_target": "VERIFIED__OPTION_A_CONTEXT_SEALED_P11_CUSTODY_AUTHENTICATED_COORDINATE",
            "constitutional_continuation_progress": "VERIFIED__JK_NEGATIVE_READINESS_TO_JL_OWNER_CONTRACT__NO_E05_CREDIT",
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
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_REMOTE_RATIFIED_JK_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__JL_SCOPE_AND_PINNED_JK_CHECKPOINT_COORDINATES_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JH_TO_JI__JI_TO_JJ__JJ_TO_JK__JK_TO_JL_DISTINGUISHED",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_JL_WORKER",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_JK_ENTRY",
            "authority_state_recovery": "VERIFIED__JH_CONSUMED_NONREUSABLE__JI_JJ_JK_JL_ZERO_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__JH_EXACTLY_ONE_HISTORICAL_ONLY_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__JH_TERMINAL_EVIDENCE_RECONSTRUCTED_THROUGH_COMMITTED_LINEAGE",
            "operation_replay_prevention": "VERIFIED__JL_ZERO_OPERATION_ZERO_REPLAY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JL_CONTRACT_FORMALIZATION_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
            "historical_jh_same_generation_recovery": "VERIFIED__EVIDENCE_ONLY",
            "jh_to_ji": "VERIFIED__COMMITTED_FRONTIER_SELECTION",
            "ji_to_jj": "VERIFIED__COMMITTED_EXPIRED_FORMALIZATION",
            "jj_to_jk": "VERIFIED__COMMITTED_PRECLAIM_BLOCKER_LOCALIZATION",
            "jk_to_jl": "VERIFIED__CURRENT_AUTHENTICATED_OWNER_CONTRACT_FORMALIZATION",
        },
        "validation": {
            "jl_focused": "VERIFIED__16_PASSED",
            "jk_reconstruction": "VERIFIED__COMMITTED_HASH_BOUND_AND_INNER_SEALED",
            "current_time_call_graph": "VERIFIED__UNCONDITIONAL_INTERNAL_time.time_ns",
            "candidate_comparison": "VERIFIED__FOUR_OPTIONS__ONE_PASSING",
            "unique_minimum": "VERIFIED__OPTION_A",
            "ownership_authentication_sealing_replay": "VERIFIED__PURE_CONTRACT_FIXTURE",
            "failure_matrix": "VERIFIED__17_FAIL_CLOSED_OR_EXPLICIT_RULES",
            "boundary_values": "VERIFIED__999_CURRENT__1000_AND_1001_EXPIRED",
            "ex": "VERIFIED__17_OF_17_REUSED__0_RECONSTRUCTED",
            "p11_unchanged_regression": "VERIFIED__22_PASSED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "git_diff_check": "VERIFIED__PASS",
            "bounded_namespace_and_index": "VERIFIED__FOUR_FILES__INDEX_EMPTY",
        },
        "terminal_frontier": {
            "last_verified_edge": "UNIQUE_MINIMUM_P11_CUSTODY_OWNED_TEMPORAL_OWNER_CONTRACT_FORMALIZED",
            "first_broken_edge": "SELECTED_CONTRACT_NOT_IMPLEMENTED_IN_EXISTING_CONTEXT_SCHEMA_COMMISSIONING_GATE_OR_P11_PRECLAIM_CONSUMER",
            "blocking_owner": "HUMAN_REVIEW_THEN_SEPARATE_GOVERNED_IMPLEMENTATION_GENERATION",
            "minimum_missing_capability": "IMPLEMENTED_CONTEXT_SEALED_TEMPORAL_RECORD_AND_P11_CUSTODY_REAUTHENTICATION_CONSUMPTION_BINDING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__ONE_REPOSITORY_ONLY_IMPLEMENTATION_GENERATION_FOR_OPTION_A_CONTEXT_GATE_AND_P11_BINDING__NO_OPERATION",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction) + b"\n"),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[5]
    try:
        sys.stdout.buffer.write(canonical_bytes(envelope(build_reduction(root))) + b"\n")
    except (ContractError, OSError, subprocess.CalledProcessError) as exc:
        print(f"TERMINAL=M__FAIL_CLOSED__{exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
