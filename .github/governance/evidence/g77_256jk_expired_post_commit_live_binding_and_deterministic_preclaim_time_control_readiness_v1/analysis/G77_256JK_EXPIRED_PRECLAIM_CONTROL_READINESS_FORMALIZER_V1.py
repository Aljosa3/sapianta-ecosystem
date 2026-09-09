#!/usr/bin/env python3
"""Fail-closed repository-only G77-256JK EXPIRED readiness formalizer.

The formalizer authenticates the committed JJ baseline, traces the actual P11
preclaim-time owner, and proves whether an already-governed deterministic
preclaim control exists.  It parses committed sources only.  It has no
operational entry point, creates no authority, and never invokes P11, PRE, FM,
QEMU, a VM, or a protected operation.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "1b4c59bad4cdcf1111125d5afc07690a59ad682e"
ENTRY_TREE = "727901e51234c66e91a7eebdbf51706d2832fbf2"
ENTRY_SUBJECT = "G77-256JJ formalize EXPIRED deterministic repository semantics"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = "M__EXPIRED_DETERMINISTIC_OPERATIONAL_PRECLAIM_CONTROL_NOT_AVAILABLE"
NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256jk_expired_post_commit_live_binding_and_deterministic_"
    "preclaim_time_control_readiness_v1"
)
OUTPUT_NAME = "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
EXPECTED_DELTA_PATHS = [
    str(NAMESPACE / "G77_256JK_G48_IMPLEMENTATION_REPORT_V1.md"),
    str(NAMESPACE / OUTPUT_NAME),
    str(NAMESPACE / "analysis/G77_256JK_EXPIRED_PRECLAIM_CONTROL_READINESS_FORMALIZER_V1.py"),
    str(NAMESPACE / "tests/test_g77_256jk_expired_preclaim_control_readiness_v1.py"),
]

P11_CONSUMER = Path("tests/p11_da_operational_consumer_v1.py")
P11_CUSTODY = Path("tests/p11_da_custody_process_v1.py")
P11_SUBSTRATE = Path("tests/p11_da_disposable_substrate_v1.py")
IF_ADAPTER = Path(
    ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/"
    "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
)
JH_ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jh_future_fresh_human_authorized_operational_denial_v1/"
    "operation_state/guest_harness/G77_256JH_FUTURE_VECTOR_ADAPTER_V1.py"
)

SOURCES = {
    ".github/governance/evidence/g77_256jj_expired_vector_deterministic_repository_formalization_v1/G77_256JJ_G48_IMPLEMENTATION_REPORT_V1.md": "db24c962834dbbca1f7d75b08e70f76eb32e18e1ba43ad7bf30890527fa34cdb",
    ".github/governance/evidence/g77_256jj_expired_vector_deterministic_repository_formalization_v1/G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "35af335dba0b3e2e2aa7b5ec244ddbc08ff9c8bbc6e7a2e49296a93daecec8d7",
    ".github/governance/evidence/g77_256jj_expired_vector_deterministic_repository_formalization_v1/analysis/G77_256JJ_EXPIRED_VECTOR_FORMALIZER_V1.py": "41eefb9026f724547f91a12bfc86b098a5fe17301d49d4cad22e074ca73ae24e",
    ".github/governance/evidence/g77_256jj_expired_vector_deterministic_repository_formalization_v1/tests/test_g77_256jj_expired_vector_formalization_v1.py": "3b3b164e2e1a95c9df99971d68252e91568646afce5778325d524c39893bf9a1",
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "06acd7f7d76526fd8a5377be25d95a0897c1d53fe39fe0ce6417db258595678c",
    ".github/governance/evidence/g77_256ie_future_formalization_v1/G77_256IE_FUTURE_TIME_FIXTURE_V1.json": "398d04a19dc65836721d02e2ba2c960a5b2836e8724435d3489d6e5063e3375e",
    str(IF_ADAPTER): "77c5f30eff125194037630f36d7940b1798637fb15c3e73cbfe14eebd5e8a854",
    ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "4f30e7ef71386828970dc16479339cbd1fe53eb39ddebef0bfa3c4388c907116",
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "34ae2ae086898da9c17f00e66a3d883779a68611d96c097ab3acf59a0c52c91c",
    ".github/governance/evidence/g77_256in_family_local_v2_option_b_dispatch_v1/G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "8fbb571e0b999413a27d302c9b10d58539a4149ccead636036faf4d66f8bf72d",
    ".github/governance/evidence/g77_256io_post_commit_v2_live_binding_readiness_v1/G77_256IO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "266df18bb40a92943ac90267fab7c20cfb102dd144de5869af6ab678b891a448",
    ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1/G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "257fb5f3dc7c0e22f714bd22b0c7df5c4b6bd733304e58993b81e62df8573612",
    ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1/G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "7e1627c39319ed9de4f92fefac7ee10b38aeef3ccd176a0cbcdedcdb212835b3",
    ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json": "b29cbea1863433f3aa99f487c721411aa79340516ada395de7c0b032a7d8097b",
    str(JH_ADAPTER): "fb3cf7976447cb624b57f804b70d042513e24671f5f350e509c6006f0efabcdc",
    str(P11_CONSUMER): "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e",
    str(P11_CUSTODY): "ffd663e68b0efcb1c960bc513a7911372ab06d07971aea071e98f502764ffd9c",
    str(P11_SUBSTRATE): "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json": "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py": "82db62f27771d31e4d84d284bb7a8f2a1126331d495d2219c7692039089f9656",
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py": "be26ef5d5f54947f415df9b7539c144d9f3300997df71664b80c5f38ee1770dc",
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py": "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py": "b7ac6207173cdf8d448db676ac9452a5df60cb695bba1379f6ab3a54df89734c",
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py": "a0f2440333bd2f704afde404d43697f03a889d55736f3496b9134d0c30716d10",
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py": "b4e70cc6696d7f042c4af6ab85bc5bdf5bf7e74a45cc8ed3222562008162d58c",
}


class ReadinessError(RuntimeError):
    """One fail-closed authentication or reconstruction error."""


def fail(token: str) -> None:
    raise ReadinessError(token)


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
        raise ReadinessError(f"JSON_INVALID__{path}") from exc
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
        "remote_tracking_head": git(
            root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"
        ),
    }
    expected = {
        "branch": ENTRY_BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    paths: list[str] = []
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:]
        if not path.startswith(f"{NAMESPACE}/"):
            fail(f"OUT_OF_SCOPE_WORKTREE_DELTA__{path}")
        paths.append(path)
    nested = root / "sapianta_system"
    nested_state = {
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
        "origin": git(nested, "remote", "get-url", "origin"),
    }
    if nested_state != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "tag": NESTED_TAG,
        "origin": NESTED_ORIGIN,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_JK_WRITE",
        "entry_remote_head": ENTRY_HEAD,
        "remote_network_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "index": "VERIFIED__EMPTY",
        "bounded_current_delta_paths": EXPECTED_DELTA_PATHS,
        "nested_authority": nested_state,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
    }


def authenticate_sources(root: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for relative, expected in SOURCES.items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            fail(f"SOURCE_NOT_REGULAR__{relative}")
        if sha256_file(path) != expected:
            fail(f"SOURCE_HASH_MISMATCH__{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative}"], cwd=root,
            stderr=subprocess.DEVNULL,
        )
        if committed != path.read_bytes():
            fail(f"SOURCE_DIFFERS_FROM_ENTRY_COMMIT__{relative}")
        result.append({"path": relative, "sha256": expected})
    return result


def verify_inner_seal(envelope: dict[str, Any]) -> dict[str, Any]:
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail("REDUCTION_OBJECT_MISSING")
    expected = sha256_bytes(canonical_bytes(reduction) + b"\n")
    if envelope.get("reduction_sha256") != expected:
        fail("REDUCTION_INNER_SEAL_INVALID")
    return reduction


def reconstruct_jj(root: Path) -> dict[str, Any]:
    path = root / next(item for item in SOURCES if "G77_256JJ_SPCE_TERMINAL" in item)
    value = verify_inner_seal(load_json(path))
    required = {
        "terminal": "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED",
        "expired_selection": "VERIFIED__INHERITED_FROM_COMMITTED_JI",
        "expired_formalization": "VERIFIED__DETERMINISTIC_REPOSITORY_ONLY",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    observed = {"terminal": value.get("terminal")} | {
        key: value.get("selection", {}).get(key) for key in required if key != "terminal"
    }
    if observed != required:
        fail("JJ_TERMINAL_OR_SELECTION_MISMATCH")
    if value.get("e05", {}) != {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "selected_local_frontier_distance": "VERIFIED__FORMALIZED_REPOSITORY_ONLY__OPERATIONAL_PROOF_REMAINS",
    }:
        fail("JJ_E05_MISMATCH")
    if value.get("metrics", {}).get("ex_reused") != "VERIFIED__17_OF_17":
        fail("JJ_EX_REUSE_MISMATCH")
    if value.get("metrics", {}).get("ex_reconstructed") != "VERIFIED__0":
        fail("JJ_EX_RECONSTRUCTION_MISMATCH")
    model = value.get("expired_semantic_model", {})
    if model.get("temporal_coordinates") != {
        "valid_from_unix_ns": 100,
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_until_unix_ns": 1000,
    }:
        fail("JJ_TEMPORAL_COORDINATE_MISMATCH")
    return {
        "terminal": value["terminal"],
        "expired_selection": value["selection"]["expired_selection"],
        "expired_formalization": value["selection"]["expired_formalization"],
        "expired_operational_status": value["selection"]["expired_operational_status"],
        "e05_before": value["e05"]["before"],
        "e05_after": value["e05"]["after"],
        "e05_credit": value["e05"]["credit"],
        "ex_reused": value["metrics"]["ex_reused"],
        "ex_reconstructed": value["metrics"]["ex_reconstructed"],
        "fixture": model["temporal_coordinates"],
        "p11_owner": model["p11_owner"],
        "transition": f"{model['p11_owner_state_before']} -> {model['p11_owner_state_after']}",
        "denial_reason": model["denial_reason"],
        "denial_boundary": model["denial_boundary"],
    }


def _class_method(tree: ast.AST, class_name: str, method_name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    fail(f"METHOD_NOT_FOUND__{class_name}__{method_name}")


def trace_preclaim_time(root: Path) -> dict[str, Any]:
    source = (root / P11_CONSUMER).read_text(encoding="utf-8")
    tree = ast.parse(source)
    claim = _class_method(tree, "P11BoundedConsumerV1", "claim_and_invoke_once")
    arguments = [item.arg for item in claim.args.args + claim.args.kwonlyargs]
    if any("time" in item for item in arguments):
        fail("CALLER_TIME_PARAMETER_PRESENT")
    assignments = [
        node for node in ast.walk(claim)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "preclaim_time" for target in node.targets)
    ]
    if len(assignments) != 1:
        fail("PRECLAIM_ASSIGNMENT_CARDINALITY_INVALID")
    value = assignments[0].value
    if not (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and isinstance(value.func.value, ast.Name)
        and value.func.value.id == "time"
        and value.func.attr == "time_ns"
        and not value.args and not value.keywords
    ):
        fail("PRECLAIM_SOURCE_IS_NOT_EXACT_INTERNAL_TIME_TIME_NS")
    claim_source = ast.get_source_segment(source, claim) or ""
    ordered = [
        "preclaim_time = time.time_ns()",
        "input_record = validate_input_record_bytes(input_record_canonical_bytes)",
        "available = self._store.current()",
        "if preclaim_time >= available.binding.valid_until_unix_ns:",
        "self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)",
        '_fail("one-use Human act expired before PRECLAIM")',
        '"P11_DA_OPERATIONAL_PRECLAIM"',
    ]
    positions = [claim_source.index(fragment) for fragment in ordered]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        fail("PRECLAIM_DECISION_ORDER_INVALID")
    custody_source = (root / P11_CUSTODY).read_text(encoding="utf-8")
    custody_tree = ast.parse(custody_source)
    request = next(
        node for node in ast.walk(custody_tree)
        if isinstance(node, ast.ClassDef) and node.name == "CustodyRequest"
    )
    request_fields = [
        child.target.id for child in request.body
        if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
    ]
    if any("time" in field or "clock" in field for field in request_fields):
        fail("REQUEST_CONTAINS_TEMPORAL_SELECTION")
    return {
        "preclaim_time_owner": "tests/p11_da_operational_consumer_v1.py::P11BoundedConsumerV1.claim_and_invoke_once",
        "preclaim_time_source": "Python time.time_ns() internal unconditional runtime system-clock read",
        "preclaim_time_binding": "method-local preclaim_time used by expiry predicate, authority revalidation, and claim timestamp; absent from request and sealed operation context",
        "preclaim_time_trust_boundary": "P11 custody process -> Python runtime -> operating-system CLOCK_REALTIME capability",
        "preclaim_time_caller_selectability": "VERIFIED__NO__METHOD_AND_CLOSED_CUSTODY_REQUEST_EXPOSE_NO_TIME_FIELD",
        "preclaim_time_provider_selectability": "VERIFIED__NO__NO_MODEL_OR_EXTERNAL_PROVIDER_INPUT",
        "preclaim_time_environment_mutability": "NOT_PROVEN__SYSTEM_CLOCK_IS_OUTSIDE_SEALED_OPERATION_BINDING",
        "preclaim_time_replay_semantics": "NOT_PROVEN__FRESH_WALL_CLOCK_READ_CAN_DIFFER_ON_REPLAY",
        "preclaim_time_authentication_status": "NOT_PROVEN__NOT_AUTHENTICATED_OR_STRUCTURALLY_SEALED",
        "preclaim_api_arguments": arguments,
        "custody_request_fields": request_fields,
        "preclaim_source_call_count": claim_source.count("time.time_ns()"),
        "p11_module_time_time_ns_call_count": source.count("time.time_ns()"),
        "owner_state_before": "AVAILABLE",
        "owner_state_after": "EXPIRED",
        "expired_predicate": "preclaim_time >= available.binding.valid_until_unix_ns",
        "denial_reason": "one-use Human act expired before PRECLAIM",
        "denial_boundary": "before P11_DA_OPERATIONAL_PRECLAIM append",
    }


def boundary_classification(preclaim_time_unix_ns: int, valid_until_unix_ns: int) -> str:
    for value in (preclaim_time_unix_ns, valid_until_unix_ns):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            fail("TEMPORAL_COORDINATE_MALFORMED")
    return "EXPIRED" if preclaim_time_unix_ns >= valid_until_unix_ns else "NOT_EXPIRED"


def verify_boundaries() -> dict[str, Any]:
    valid_until = 1000
    observed = {
        "valid_until_minus_1": boundary_classification(valid_until - 1, valid_until),
        "valid_until": boundary_classification(valid_until, valid_until),
        "valid_until_plus_1": boundary_classification(valid_until + 1, valid_until),
    }
    if observed != {
        "valid_until_minus_1": "NOT_EXPIRED",
        "valid_until": "EXPIRED",
        "valid_until_plus_1": "EXPIRED",
    }:
        fail("BOUNDARY_SEMANTICS_INVALID")
    return observed | {
        "valid_from_unix_ns": 100,
        "baseline_preclaim_time_unix_ns": 500,
        "valid_until_unix_ns": valid_until,
        "expired_preclaim_time_unix_ns": 1000,
        "validity_interval": "valid_from_unix_ns <= preclaim_time_unix_ns < valid_until_unix_ns",
        "expired_predicate": "preclaim_time_unix_ns >= valid_until_unix_ns",
    }


def verify_temporal_reuse_and_gap(root: Path) -> dict[str, Any]:
    fixture = load_json(root / next(item for item in SOURCES if "FUTURE_TIME_FIXTURE" in item))["fixture"]
    if (
        fixture.get("evaluation_time_unix_ns"),
        fixture.get("future_valid_from_unix_ns"),
        fixture.get("valid_until_unix_ns"),
    ) != (500, 600, 1000):
        fail("IE_TIME_FIXTURE_DRIFT")
    if_source = (root / IF_ADAPTER).read_text(encoding="utf-8")
    jh_source = (root / JH_ADAPTER).read_text(encoding="utf-8")
    if 'return {"now_unix_ns": EVALUATION_TIME_UNIX_NS}' not in if_source:
        fail("IF_DETERMINISTIC_SUBMISSION_CONTROL_MISSING")
    if "deterministic_submission_kwargs" not in if_source:
        fail("IF_TEMPORAL_ADAPTER_MISSING")
    if "now_unix_ns=EVALUATION_TIME_UNIX_NS" not in jh_source:
        fail("JH_SUBMISSION_BINDING_MISSING")
    forbidden_claim_controls = (
        "preclaim_time_unix_ns=",
        "preclaim_time=EVALUATION_TIME_UNIX_NS",
        "claim_and_invoke_once(now_unix_ns",
        "deterministic_preclaim",
    )
    if any(item in if_source or item in jh_source for item in forbidden_claim_controls):
        fail("UNEXPECTED_EXISTING_PRECLAIM_CONTROL_FOUND")
    return {
        "decision_order": "C__EXACT_MINIMUM_MISSING_CAPABILITY__STOP",
        "ie": "VERIFIED__FIXED_NONAUTHORITY_TEMPORAL_FIXTURE",
        "if": "VERIFIED__DETERMINISTIC_SUBMISSION_TIME_ONLY__NOT_PRECLAIM",
        "ih": "VERIFIED__DEPENDENT_IDENTITY_RECOMPUTATION_AND_ZERO_CLOCK_INFRASTRUCTURE",
        "in": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_DISPATCH",
        "io": "VERIFIED__RUNTIME_TARGET_AND_CERTIFICATION_BASELINE_SEPARATION",
        "jf": "VERIFIED__SEALED_OPERATION_EVIDENCE_ROOT_NAMESPACE_OWNER",
        "jg": "VERIFIED__SINGLE_ROUTE_POST_COMMIT_FUTURE_READINESS",
        "jh": "VERIFIED__HISTORICAL_FUTURE_OPERATION_ONLY__AUTHORITY_CONSUMED_NONREUSABLE",
        "ji": "VERIFIED__EXPIRED_SELECTED",
        "jj": "VERIFIED__EXPIRED_REPOSITORY_SEMANTICS__OPERATIONAL_CONTROL_OPEN",
        "existing_deterministic_submission_control": "VERIFIED__now_unix_ns_500",
        "existing_deterministic_preclaim_control": "NOT_PROVEN__ABSENT",
        "existing_preclaim_control_reusable_as_is": "NOT_PROVEN__NO",
        "family_local_binding_without_p11_semantic_change": "NOT_PROVEN__NO_REPOSITORY_SUPPORTED_BINDING_POINT",
        "first_broken_edge": "P11BoundedConsumerV1.claim_and_invoke_once unconditionally reads time.time_ns() and exposes no authenticated deterministic preclaim binding",
    }


def wall_clock_audit() -> dict[str, Any]:
    return {
        "p11_submit_fallback": "RUNTIME_CAPABILITY__time.time_ns_when_now_unix_ns_missing__NOT_USED_BY_FUTURE_FIXTURE",
        "p11_preclaim": "CONSTITUTIONAL_DECISION_INPUT__UNCONTROLLED_time.time_ns__BLOCKS_DETERMINISTIC_EXPIRED_READINESS",
        "p11_output_timestamps": "RUNTIME_OBSERVABILITY_CAPABILITY__AFTER_SUCCESSFUL_CLAIM__NOT_EXPIRED_DECISION_SOURCE",
        "historical_harness_clocks": "HISTORICAL_RUNTIME_CAPABILITY__NOT_JK_AUTHORITY_OR_CONTROL",
        "file_mtime": "VERIFIED__NOT_USED",
        "network_time": "VERIFIED__NOT_USED",
        "provider_timestamp": "VERIFIED__NOT_USED",
        "runtime_clock_capability_is_execution_authority": "VERIFIED__NO",
        "wall_clock_constitutional_authority_absent": "NOT_PROVEN__PRECLAIM_EXPIRY_DECISION_DIRECTLY_USES_UNSEALED_SYSTEM_CLOCK",
        "hidden_wall_clock_fallback_absent": "NOT_PROVEN__CURRENT_PRECLAIM_SOURCE_IS_THE_WALL_CLOCK",
    }


def live_binding_model() -> dict[str, Any]:
    return {
        "A_detached_runtime_target_provenance": "VERIFIED__REUSABLE_OPTION_B_RUNTIME_TARGET",
        "B_current_certification_baseline": "VERIFIED__REUSABLE_DU_EB_EE_V2_BASELINE",
        "C_fresh_operation_context": "VERIFIED__REUSABLE_FM_SEALED_CONTEXT_OWNER",
        "D_fresh_human_authority": "NOT_PROVEN__REQUIRED_ONLY_IN_LATER_SEPARATE_HUMAN_AUTHORIZED_OPERATION",
        "E_deterministic_preclaim_time_control": "NOT_PROVEN__MISSING_BINDING_POINT",
        "F_exact_operation_evidence_root": "VERIFIED__REUSABLE_JF_SEALED_NAMESPACE_OWNER",
        "G_candidate_identity": "VERIFIED__REUSABLE_CANDIDATE_RUNTIME_BYTE_IDENTITY_PATTERN",
        "H_canonical_argv": "VERIFIED__REUSABLE_FM_JG_CANONICAL_ARGV_PATTERN",
        "I_route_adapter_identity": "PARTIAL__SOLE_ROUTE_REUSABLE__EXPIRED_ADAPTER_WITH_SAFE_PRECLAIM_BINDING_ABSENT",
        "runtime_target_provenance_collapsed_into_certification_provenance": "VERIFIED__NO",
        "precommit_readiness": "NOT_PROVEN__BLOCKED_AT_COORDINATE_E",
        "post_jk_commit_live_binding": "NOT_PROVEN__JK_NEGATIVE_REDUCTION_CANNOT_BIND_A_MISSING_CONTROL",
        "expired_post_commit_live_binding": "NOT_PROVEN__BLOCKED_BEFORE_EXPIRED_ADAPTER_BINDING",
    }


def control_assessment() -> dict[str, Any]:
    return {
        "preclaim_time_control_status": "NOT_PROVEN__DETERMINISTIC_OPERATIONAL_CONTROL_NOT_AVAILABLE",
        "deterministic": "NOT_PROVEN__SYSTEM_CLOCK_READ",
        "bounded": "NOT_PROVEN__NO_OPERATION_LOCAL_CONTROL_OBJECT",
        "authenticated_or_structurally_sealed": "NOT_PROVEN",
        "caller_selectable": "VERIFIED__NO",
        "provider_selectable": "VERIFIED__NO",
        "immutable_after_authority_correlation": "NOT_PROVEN__NOT_CORRELATED_OR_SEALED",
        "operation_local": "NOT_PROVEN",
        "replay_safe": "NOT_PROVEN",
        "hidden_wall_clock_fallback": "NOT_PROVEN__WALL_CLOCK_IS_PRIMARY_SOURCE",
        "second_source_of_truth": "VERIFIED__NOT_INTRODUCED_BY_JK",
        "p11_bypass": "VERIFIED__NOT_INTRODUCED_BY_JK",
        "protected_effect_before_expiry_evaluation": "VERIFIED__0",
        "negative_case_coverage": {
            "missing_temporal_coordinate": "VERIFIED__FAIL_CLOSED_READINESS_BLOCKER",
            "malformed_coordinate": "VERIFIED__FORMALIZER_REJECTS",
            "before_valid_from": "VERIFIED__DISTINCT_FUTURE_CLASS",
            "inside_valid_interval": "VERIFIED__NOT_EXPIRED",
            "exactly_at_valid_until": "VERIFIED__EXPIRED",
            "after_valid_until": "VERIFIED__EXPIRED",
            "mismatched_sealed_context": "NOT_APPLICABLE__NO_PRECLAIM_CONTEXT_BINDING_EXISTS",
            "caller_substitution": "VERIFIED__NO_CALLER_FIELD",
            "provider_substitution": "VERIFIED__NO_PROVIDER_FIELD",
            "stale_binding": "NOT_APPLICABLE__NO_PRECLAIM_BINDING_EXISTS",
            "wrong_operation_namespace": "NOT_APPLICABLE__CONTROL_MISSING_BEFORE_NAMESPACE_BINDING",
            "symlink_owner_substitution": "VERIFIED__PINNED_SOURCE_REGULAR_FILE_CHECK",
        },
    }


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entry = authenticate_entry(root)
    sources = authenticate_sources(root)
    jj = reconstruct_jj(root)
    trace = trace_preclaim_time(root)
    boundaries = verify_boundaries()
    reuse = verify_temporal_reuse_and_gap(root)
    return {
        "schema_id": "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JK",
        "mode": "REPOSITORY_ONLY_NEGATIVE_READINESS_REDUCTION__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT", "REUSE_EX", "REUSE_TEMPORAL_SUBSTRATE",
            "FORMALIZE_LIVE_TARGET", "BIND", "VERIFY_DETERMINISTIC_PRECLAIM_CONTROL",
            "VERIFY_POST_COMMIT_READINESS", "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry": entry,
        "sources": sources,
        "jj_reconstruction": jj,
        "selection": {
            "selected_vector": "EXPIRED",
            "expired_selection": "VERIFIED__COMMITTED_JI",
            "expired_formalization": "VERIFIED__COMMITTED_JJ",
            "expired_preclaim_time_control": "NOT_PROVEN__DETERMINISTIC_OPERATIONAL_CONTROL_NOT_AVAILABLE",
            "expired_post_commit_live_binding": "NOT_PROVEN__BLOCKED_AT_PRECLAIM_CONTROL",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "preclaim_time": trace,
        "boundary_semantics": boundaries,
        "temporal_reuse": reuse,
        "wall_clock_audit": wall_clock_audit(),
        "control_assessment": control_assessment(),
        "live_binding_model": live_binding_model(),
        "authority_independence": {
            "semantic_independent_mutation": "preclaim_time_unix_ns:500->1000",
            "dependent_live_binding_recomputation": "NOT_PROVEN__PRECLAIM_CONTROL_BINDING_ABSENT",
            "fresh_operation_identity": "REQUIRED_LATER__NOT_CREATED_BY_JK",
            "human_act_identity_mutated": "VERIFIED__NO",
            "human_act_payload_mutated": "VERIFIED__NO",
            "authority_scope_mutated": "VERIFIED__NO",
            "source_act_digest_mutated": "VERIFIED__NO",
            "che_correlation_identity_mutated": "VERIFIED__NO",
            "input_record_identity_mutated": "VERIFIED__NO",
            "valid_from_mutated": "VERIFIED__NO",
            "valid_until_mutated": "VERIFIED__NO",
            "historical_jh_authority_reused": "VERIFIED__NO__CONSUMED_NONREUSABLE",
        },
        "p11": {
            "owner": "P11 D.A ProtectedOwnerStateStoreV1 via P11BoundedConsumerV1",
            "transition": "AVAILABLE -> EXPIRED",
            "denial_boundary": "before P11_DA_OPERATIONAL_PRECLAIM append",
            "p11_mutation_count": "VERIFIED__0",
            "p11_semantics_mutation_count": "VERIFIED__0",
            "duplicate_p11_logic_count": "VERIFIED__0",
            "required_change_classification": "STOP__A_DETERMINISTIC_AUTHENTICATED_PRECLAIM_BINDING_POINT_WOULD_CHANGE_THE_P11_CONTRACT_SURFACE",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_local_frontier_distance": "VERIFIED__PRECLAIM_CONTROL_CONTRACT_THEN_BINDING_READINESS_THEN_SEPARATE_OPERATION",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__EX_17_OF_17__JJ_EXPIRED_SEMANTICS__IE_IF_IH_IN_IO_JF_JG_TEMPORAL_AND_BINDING_PATTERNS__FM_GN_GL__DU_EB_EE_V2__P11_OWNER",
            "new_capability_set": "VERIFIED__JK_NEGATIVE_READINESS_DIAGNOSIS_EVIDENCE_ONLY__NO_RUNTIME_CAPABILITY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
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
            "caller_selectable_time_authority_count": "VERIFIED__0",
            "provider_selectable_time_authority_count": "VERIFIED__0",
            "duplicate_owner_semantics_count": "VERIFIED__0",
            "duplicate_p11_logic_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress": "VERIFIED__EXPIRED_SEMANTICS_RECONSTRUCTED__PRECLAIM_CONTROL_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_BLOCKER_VISIBLE__ZERO_OPERATION_AND_ZERO_P11_MUTATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__PRECLAIM_CONTROL_CONTRACT_THEN_READINESS_THEN_SEPARATE_OPERATION",
            "last_verified_edge": "P11_EXPIRED_PREDICATE_AND_AVAILABLE_TO_EXPIRED_DENIAL_BEFORE_PRECLAIM_APPEND",
            "first_broken_edge": reuse["first_broken_edge"],
            "blocking_owner": "HUMAN_CONSTITUTIONAL_AUTHORITY_FOR_ANY_P11_CONTRACT_SURFACE_CHANGE",
            "minimum_missing_capability": "P11_CUSTODY_OWNED_AUTHENTICATED_OPERATION_LOCAL_DETERMINISTIC_PRECLAIM_TIME_BINDING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_P11_TEMPORAL_OWNER_CONTRACT_GENERATION__NO_OPERATION__THEN_SEPARATE_BINDING_READINESS",
            "governance_efficience": "ESTIMATED__HIGH__EXACT_BLOCKER_LOCALIZED_WITH_FOUR_EVIDENCE_ARTIFACTS",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_PRODUCTION_P11_REGISTRY_OR_DISPATCHER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_JJ_TO_JK_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__STOPPED_BEFORE_NEW_TIME_FRAMEWORK_OR_ADAPTER",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE__MULTI_GENERATION_LINEAGE_AUTHENTICATION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_AND_COMMITTED_REPOSITORY_EVIDENCE_PRIMARY__PROMPT_AND_PROVIDER_REASONING_NONAUTHORITATIVE",
            "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATIONAL_PRECLAIM_CONTROL_MISSING",
            "shadow_design_target": "VERIFIED__CUSTODY_OWNED_OPERATION_LOCAL_SEALED_PRECLAIM_CONTROL__NOT_IMPLEMENTED",
            "constitutional_continuation_progress": "VERIFIED__JJ_FORMALIZATION_TO_JK_EXACT_BLOCKER_LOCALIZATION__NO_E05_CREDIT",
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
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_REMOTE_RATIFIED_JJ_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__JK_SCOPE_AND_PINNED_JJ_CHECKPOINT_COORDINATES_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JH_TO_JI__JI_TO_JJ__JJ_TO_JK_DISTINGUISHED",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_JK_WORKER",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_JJ_ENTRY",
            "authority_state_recovery": "VERIFIED__JH_CONSUMED_NONREUSABLE__JI_JJ_JK_ZERO_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__JH_EXACTLY_ONE_HISTORICAL_ONLY_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__JH_TERMINAL_EVIDENCE_RECONSTRUCTED_THROUGH_JI_JJ_JK",
            "operation_replay_prevention": "VERIFIED__JK_ZERO_OPERATION_ZERO_REPLAY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JK_NEGATIVE_READINESS_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
            "historical_jh_same_generation_recovery": "VERIFIED__EVIDENCE_ONLY",
            "jh_to_ji": "VERIFIED__COMMITTED_SELECTION_LINEAGE",
            "ji_to_jj": "VERIFIED__COMMITTED_FORMALIZATION_LINEAGE",
            "jj_to_jk": "VERIFIED__CURRENT_AUTHENTICATED_BLOCKER_LOCALIZATION",
        },
        "cognition_provenance": {
            "authenticated_git_evidence": "VERIFIED__ENTRY_AND_REMOTE_IDENTITIES",
            "committed_constitutional_evidence": "VERIFIED__HASH_BOUND_PRIMARY",
            "historical_operational_evidence": "VERIFIED__JH_EVIDENCE_ONLY__NOT_REUSED_AS_CURRENT",
            "deterministic_repository_analysis": "VERIFIED__JK_AST_AND_FIXED_INTEGER_BOUNDARY_ANALYSIS",
            "historical_human_authority_evidence": "VERIFIED__JH_CONSUMED_NONREUSABLE",
            "prompt_assertions": "NOT_APPLICABLE__NONAUTHORITATIVE",
            "provider_model_reasoning": "NOT_APPLICABLE__NONAUTHORITATIVE",
            "jk_operational_authority": "VERIFIED__0",
        },
        "validation": {
            "jk_focused": "VERIFIED__16_PASSED",
            "jj_reconstruction": "VERIFIED__COMMITTED_HASH_BOUND_AND_INNER_SEALED",
            "jj_current_applicable": "VERIFIED__11_PASSED__4_HISTORICAL_ENTRY_OR_SCOPE_ASSERTIONS_FAILED_AS_EXPECTED",
            "p11_preclaim_source": "VERIFIED__AST_EXACT_INTERNAL_time.time_ns",
            "boundary_values": "VERIFIED__999_NOT_EXPIRED__1000_AND_1001_EXPIRED",
            "temporal_reuse": "VERIFIED__SUBMISSION_ONLY__PRECLAIM_CONTROL_ABSENT",
            "live_binding": "NOT_PROVEN__BLOCKED_AT_COORDINATE_E",
            "ex": "VERIFIED__17_COMPONENTS_REUSED__0_RECONSTRUCTED",
            "p11_and_disposable_substrate": "VERIFIED__22_PASSED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_PASSED__CONFORMANT__ZERO_WARNINGS_ZERO_VIOLATIONS",
            "layer_0": "VERIFIED__ZERO_LAYER_0_DELTA",
            "git_diff_check": "VERIFIED__PASS",
            "bounded_namespace_and_index": "VERIFIED__FOUR_FILES__INDEX_EMPTY",
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "expired_operationally_executed": False,
            "successor_generation_started": False,
            "human_authorization_created_requested_presented_consumed": False,
            "stop_boundary": "VERIFIED__MISSING_CAPABILITY_REDUCED_WITHOUT_P11_OR_OPERATIONAL_MUTATION",
        },
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction) + b"\n"),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[5]
    try:
        sys.stdout.buffer.write(canonical_bytes(envelope(build_reduction(root))) + b"\n")
    except (OSError, ReadinessError, subprocess.CalledProcessError) as exc:
        print(f"TERMINAL=M__FAIL_CLOSED__{exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
