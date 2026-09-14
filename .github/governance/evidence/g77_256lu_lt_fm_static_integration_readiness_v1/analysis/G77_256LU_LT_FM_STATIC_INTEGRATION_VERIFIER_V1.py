#!/usr/bin/env python3
"""Read-only verifier for the G77-256LU LT-to-FM static binding relation."""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LU_REL = Path(
    ".github/governance/evidence/"
    "g77_256lu_lt_fm_static_integration_readiness_v1"
)
LU = ROOT / LU_REL
MANIFEST = LU / "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_V1.json"
DECISION = LU / "G77_256LU_TERMINAL_DECISION_V1.json"
REPORT = LU / "G77_256LU_G48_IMPLEMENTATION_REPORT_V1.md"
TEST = LU / "tests/test_g77_256lu_lt_fm_static_integration_v1.py"
LT = ROOT / (
    ".github/governance/evidence/"
    "g77_256lt_session_independent_one_shot_supervision_v1"
)
LT_HARNESS = LT / "harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py"
LT_VERIFIER = LT / "analysis/G77_256LT_STATIC_CAPABILITY_VERIFIER_V1.py"
LT_DECISION = LT / "G77_256LT_TERMINAL_DECISION_V1.json"
LT_REPORT = LT / "G77_256LT_G48_IMPLEMENTATION_REPORT_V1.md"
LR = ROOT / (
    ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1"
)
LR_CONTROLLER = LR / "orchestration/G77_256LR_ONE_SHOT_CONTROLLER_V1.py"
LR_BINDING = LR / "G77_256LR_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
LR_RECONSTRUCTION = LR / "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json"
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CONTEXT_OWNER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
NESTED = ROOT / "sapianta_system"

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
LT_HEAD = "f22fae2529de35eaf8093776c04a6a8e05a097f6"
LT_TREE = "921382a2b0f852150037db4c7eff4d9884693211"
LT_SUBJECT = "G77-256LT add session-independent one-shot supervision harness"
LS_HEAD = "8b3bff5ee417333ebe97df3b42e62462b8e21f62"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
FM_REL = FM.relative_to(ROOT).as_posix()
EXPECTED_HASHES = {
    LT_DECISION: "f0a6acfc31c72b1b1e890cf2e3c587b4f5ccf179ecf2da9c6e2ad724a27aae9f",
    LT_REPORT: "652fb6f61d1fd34fb1d6eaa99f5cdae523ac8476214d35d25e5bfd3848f3f8ae",
    LT_VERIFIER: "42fa6ff535e63e64bf92512757e96ea305004c2f5d14651a7182134ab513b6d3",
    LT_HARNESS: "5d1e54acd3e37390e3c0077c1f480b6008f849e569ced8889e6aacc04fbccf6f",
    LR_CONTROLLER: "89a7ebf2f6d7972e6899956b947c20a1614db2c9d53e5d3ac97816929a31b1b0",
    LR_BINDING: "80a54e4dc39936ebea042cfbc8a1c354c26c94c39a96e3184b2a19216c16742d",
    LR_RECONSTRUCTION: "429123ec1ddef737060de182e712cb1a6091318a69345ca720764f91977b126b",
    FM: "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8",
    CONTEXT_OWNER: "a3e22af7793063d1482e4e59deb114005bcba6c4b07f914a329c0a3b843db618",
}
CAPABILITY_ID = (
    "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_"
    "DURABLE_TERMINAL_HANDOFF_V1"
)
TERMINAL = (
    "A__G77_256LU_LT_TO_EXISTING_FM_STATIC_INTEGRATION_READINESS_PROVEN__"
    "ZERO_AUTHORITY__ZERO_OPERATION__ZERO_PRODUCTION_MUTATION__"
    "FRESH_PHASE_A_IS_MINIMUM_NEXT_GOVERNED_DELTA__READY_FOR_HUMAN_REVIEW"
)
TERMINAL_STATES = {
    "STARTED",
    "RUNNING",
    "TERMINATED_WITH_STATUS",
    "INTERRUPTED_OR_LOST__UNKNOWN",
}


class StaticBindingError(RuntimeError):
    """A fail-closed rejection of a proposed static composition."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def git(repository: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise RuntimeError(f"NON_OBJECT_JSON:{path.name}")
    return value


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    head = git(ROOT, "rev-parse", "HEAD")
    if (
        git(ROOT, "branch", "--show-current") != BRANCH
        or git(ROOT, "rev-parse", f"{LT_HEAD}^{{tree}}") != LT_TREE
        or git(ROOT, "show", "-s", "--format=%s", LT_HEAD) != LT_SUBJECT
        or not is_ancestor(LS_HEAD, LT_HEAD)
        or not is_ancestor(LT_HEAD, head)
        or int(git(ROOT, "rev-list", "--count", f"{LT_HEAD}..{head}")) > 1
        or remote_head != head
    ):
        raise RuntimeError("LT_ENTRY_OR_SINGLE_LU_SUCCESSOR_CONFLICT")
    prefix = LU_REL.as_posix() + "/"
    for line in git(ROOT, "status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line and not line[3:].startswith(prefix):
            raise RuntimeError(f"UNRELATED_WORKTREE_MUTATION:{line}")
    if head != LT_HEAD:
        changed = git(ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", LT_HEAD, head)
        if any(path and not path.startswith(prefix) for path in changed.splitlines()):
            raise RuntimeError("PRODUCTION_OR_OUT_OF_SCOPE_COMMITTED_MUTATION")
    if (
        git(NESTED, "rev-parse", "HEAD") != NESTED_HEAD
        or git(NESTED, "rev-parse", "HEAD^{tree}") != NESTED_TREE
        or git(NESTED, "branch", "--show-current")
        or git(NESTED, "status", "--porcelain=v1", "--untracked-files=all")
        or git(NESTED, "rev-parse", f"{NESTED_TAG}^{{}}") != NESTED_HEAD
        or nested_remote_tag != NESTED_HEAD
    ):
        raise RuntimeError("NESTED_AUTHORITY_CONFLICT")


def authenticate_predecessors() -> None:
    if any(
        path.is_symlink() or not path.is_file() or sha256(path) != expected
        for path, expected in EXPECTED_HASHES.items()
    ):
        raise RuntimeError("AUTHENTICATED_PREDECESSOR_IDENTITY_CONFLICT")
    lt = load_json(LT_DECISION)
    decision = lt.get("decision", {})
    evidence = lt.get("evidence", {})
    if (
        decision.get("CAPABILITY_ID") != CAPABILITY_ID
        or decision.get("CAPABILITY_IMPLEMENTED")
        != "YES__GENERATION_LOCAL_HARNESS_ONLY"
        or decision.get("AUTHORITY_EFFECT") != "NONE"
        or decision.get("OPERATIONAL_RETRY_AUTHORIZED") != "NO"
        or evidence.get("e05", {}).get("E05_AFTER") != "12/18"
        or evidence.get("architecture", {}).get("ROUTE_COUNT_BEFORE") != 1
        or evidence.get("architecture", {}).get("ROUTE_COUNT_AFTER") != 1
    ):
        raise RuntimeError("LT_AUTHENTICATED_CAPABILITY_CONFLICT")
    reconstruction = load_json(LR_RECONSTRUCTION).get("reconstruction", {})
    if (
        reconstruction.get("authority", {}).get("reusable") is not False
        or reconstruction.get("cardinality", {}).get("human_decision_count") != 1
        or reconstruction.get("cardinality", {}).get("operation_attempt_count") != 1
        or reconstruction.get("cardinality", {}).get("retry_count") != 0
    ):
        raise RuntimeError("LR_TERMINAL_NONREUSE_CONFLICT")


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"MISSING_FUNCTION:{name}")


def authenticate_code_relation() -> None:
    lt_source = LT_HARNESS.read_text(encoding="utf-8")
    fm_source = FM.read_text(encoding="utf-8")
    controller_source = LR_CONTROLLER.read_text(encoding="utf-8")
    context_source = CONTEXT_OWNER.read_text(encoding="utf-8")
    lt_tree = ast.parse(lt_source)
    fm_tree = ast.parse(fm_source)
    supervise = function(lt_tree, "supervise")
    child_launches = [
        node
        for node in ast.walk(supervise)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "popen_factory"
    ]
    if len(child_launches) != 1:
        raise RuntimeError("LT_EXACTLY_ONE_CHILD_LAUNCH_SITE_CONFLICT")
    for required in (
        'binding["argv"]',
        'cwd=str(working_directory)',
        '"authority_effect": "NONE"',
        '"receipt_semantics": "NONAUTHORITY_SUPERVISION_ONLY__NO_SYNTHETIC_POST"',
        '"relaunch_permitted": False',
    ):
        if required not in lt_source:
            raise RuntimeError(f"LT_BINDING_CONTRACT_MISSING:{required}")
    if any(token in lt_source for token in ("PRE_EXECUTED_QEMU_ARGV_RECEIPT", "POST_EXECUTED_QEMU_ARGV_RECEIPT")):
        raise RuntimeError("LT_RECEIPT_OWNERSHIP_INTRUSION")

    pre = fm_source.find("write_atomic(pre_path, receipt(")
    qemu = fm_source.find("result = subprocess.run(argv, check=False)")
    post = fm_source.find("write_atomic(post_path, receipt(")
    if min(pre, qemu, post) < 0 or not pre < qemu < post:
        raise RuntimeError("FM_PRE_OPERATION_POST_ORDER_CONFLICT")
    if fm_source.count("result = subprocess.run(argv, check=False)") != 1:
        raise RuntimeError("FM_OPERATIONAL_CALL_SITE_CARDINALITY_CONFLICT")
    for required in (
        "def build_preconsumption_invocation_binding(",
        "def validate_preconsumption_invocation_binding(",
        '"binding_is_authority": False',
        '"execution_authorized_by_binding": False',
        '"authority_consumption_count": 0',
        '"fm_operational_invocation_count": 0',
    ):
        if required not in fm_source:
            raise RuntimeError(f"FM_INVOCATION_CONTRACT_MISSING:{required}")
    if controller_source.count(
        "status = subprocess.run(final_argv, cwd=ROOT, check=False).returncode"
    ) != 1:
        raise RuntimeError("EXISTING_CONTROLLER_TO_FM_HANDOFF_CONFLICT")
    for field in (
        '"serial_path"',
        '"pre_receipt_path"',
        '"post_receipt_path"',
        '"runtime_export_root"',
        '"guest_output_relative_paths"',
    ):
        if field not in context_source:
            raise RuntimeError(f"FM_CONTEXT_EVIDENCE_BINDING_MISSING:{field}")

    historical = load_json(LR_BINDING).get("binding", {})
    argv = historical.get("final_fm_argv")
    if (
        not isinstance(argv, list)
        or argv[:2] != ["/usr/bin/python", FM_REL]
        or historical.get("final_fm_argv_sha256") != digest(argv)
        or historical.get("authority_consumption_count") != 0
        or historical.get("fm_operational_invocation_count") != 0
        or historical.get("binding_phase")
        != "BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION"
    ):
        raise RuntimeError("HISTORICAL_EXACT_FM_INVOCATION_CONTRACT_CONFLICT")


def synthetic_candidate() -> dict[str, Any]:
    """Return static fixture values only; the returned argv is never executed."""
    context_sha = "1" * 64
    authority_sha = "2" * 64
    admission_head = "3" * 40
    admission_tree = "4" * 40
    fm_binding_sha = "5" * 64
    argv = [
        "/usr/bin/python",
        FM_REL,
        "--operation-context",
        "SYNTHETIC_FUTURE_CONTEXT.json",
        "--operation-context-sha256",
        context_sha,
        "--live-candidate-binding",
        "SYNTHETIC_FUTURE_CANDIDATE.json",
        "--execution-authority",
        "SYNTHETIC_FUTURE_AUTHORITY.json",
        "--execution-authority-sha256",
        authority_sha,
        "--committed-review-transition",
        "SYNTHETIC_FUTURE_TRANSITION.json",
        "--committed-review-transition-sha256",
        "6" * 64,
    ]
    return {
        "fixture_class": "STATIC_SYNTHETIC_NONOPERATIONAL",
        "lifecycle_id": "SYNTHETIC_FUTURE_LIFECYCLE_001",
        "phase_a_object_identity": "SYNTHETIC_PHASE_A_OBJECT_SHA256:" + "7" * 64,
        "authority_binding_sha256": authority_sha,
        "authority_created_by_supervisor": False,
        "authority_consumed_by_supervisor": False,
        "authority_consumed_before_supervisor_reservation": True,
        "admission_head": admission_head,
        "admission_tree": admission_tree,
        "admission_identity": f"HEAD:{admission_head}__TREE:{admission_tree}",
        "expected_admission_identity": f"HEAD:{admission_head}__TREE:{admission_tree}",
        "fm_input_identity": "CONTEXT_FILE_SHA256:" + context_sha,
        "expected_fm_input_identity": "CONTEXT_FILE_SHA256:" + context_sha,
        "fm_invocation_binding_sha256": fm_binding_sha,
        "lt_invocation_binding_identity": "FM_BINDING_SHA256:" + fm_binding_sha,
        "argv": argv,
        "argv_sha256": digest(argv),
        "working_directory": str(ROOT),
        "receipt_namespace": "SYNTHETIC_FUTURE_OPERATION_STATE/receipts",
        "serial_path": "SYNTHETIC_FUTURE_TRANSIENT/serial.log",
        "guest_evidence_path": "SYNTHETIC_FUTURE_OPERATION_STATE/runtime_export",
        "pre_owner": "EXISTING_FM",
        "post_owner": "EXISTING_FM",
        "supervisor_writes_pre": False,
        "supervisor_writes_post": False,
        "wrong_scope_inference_from_supervision": False,
        "scope_metadata_delta": 0,
        "attempt_limit": 1,
        "retry_limit": 0,
        "reservation_exists": False,
        "supervision_state": "UNRESERVED",
        "lr_authority_or_lifecycle_reused": False,
        "route_count_before": 1,
        "route_count_after": 1,
    }


def validate_static_candidate(candidate: dict[str, Any]) -> str:
    """Validate relation only. This function cannot launch or mutate anything."""
    if candidate.get("fixture_class") != "STATIC_SYNTHETIC_NONOPERATIONAL":
        raise StaticBindingError("NONSTATIC_FIXTURE_FORBIDDEN")
    if candidate.get("lr_authority_or_lifecycle_reused") is not False:
        raise StaticBindingError("LR_TERMINAL_LIFECYCLE_REUSE_FORBIDDEN")
    if candidate.get("reservation_exists") is not False:
        raise StaticBindingError("DUPLICATE_SUPERVISOR_RESERVATION__NO_RELAUNCH")
    if candidate.get("supervision_state") in TERMINAL_STATES:
        raise StaticBindingError("EXISTING_SUPERVISION_STATE__NO_RELAUNCH")
    if candidate.get("supervision_state") != "UNRESERVED":
        raise StaticBindingError("UNKNOWN_SUPERVISION_STATE__NO_RELAUNCH")
    if candidate.get("lt_invocation_binding_identity") != (
        "FM_BINDING_SHA256:" + str(candidate.get("fm_invocation_binding_sha256"))
    ):
        raise StaticBindingError("MISMATCHED_INVOCATION_BINDING")
    if candidate.get("admission_identity") != candidate.get("expected_admission_identity"):
        raise StaticBindingError("MISMATCHED_ADMISSION_HEAD_TREE")
    if candidate.get("fm_input_identity") != candidate.get("expected_fm_input_identity"):
        raise StaticBindingError("MISMATCHED_FM_INPUT_IDENTITY")
    argv = candidate.get("argv")
    if (
        not isinstance(argv, list)
        or len(argv) < 2
        or argv[0] != "/usr/bin/python"
        or argv[1] != FM_REL
    ):
        raise StaticBindingError("FM_EXECUTABLE_OR_ROUTE_SUBSTITUTION")
    if candidate.get("argv_sha256") != digest(argv):
        raise StaticBindingError("MISMATCHED_ARGV_HASH")
    if candidate.get("working_directory") != str(ROOT):
        raise StaticBindingError("WRONG_WORKING_DIRECTORY")
    if (
        candidate.get("pre_owner") != "EXISTING_FM"
        or candidate.get("post_owner") != "EXISTING_FM"
        or candidate.get("supervisor_writes_pre") is not False
        or candidate.get("supervisor_writes_post") is not False
    ):
        raise StaticBindingError("FM_PRE_POST_OWNERSHIP_SUBSTITUTION")
    if candidate.get("wrong_scope_inference_from_supervision") is not False:
        raise StaticBindingError("HOST_SUPERVISION_PROOF_INFLATION")
    if candidate.get("scope_metadata_delta") != 0:
        raise StaticBindingError("SCOPE_BROADENING_THROUGH_INTEGRATION_METADATA")
    if (
        candidate.get("authority_created_by_supervisor") is not False
        or candidate.get("authority_consumed_by_supervisor") is not False
        or candidate.get("authority_consumed_before_supervisor_reservation") is not True
    ):
        raise StaticBindingError("AUTHORITY_BOUNDARY_OR_ORDER_CONFLICT")
    if candidate.get("attempt_limit") != 1 or candidate.get("retry_limit") != 0:
        raise StaticBindingError("ONE_SHOT_CARDINALITY_CONFLICT")
    if (
        candidate.get("route_count_before") != 1
        or candidate.get("route_count_after") != 1
    ):
        raise StaticBindingError("PRODUCTION_ROUTE_COUNT_CONFLICT")
    for field in (
        "lifecycle_id",
        "phase_a_object_identity",
        "authority_binding_sha256",
        "receipt_namespace",
        "serial_path",
        "guest_evidence_path",
    ):
        if not isinstance(candidate.get(field), str) or not candidate[field]:
            raise StaticBindingError(f"MISSING_EXACT_IDENTITY:{field}")
    return "STATIC_INTEGRATION_READY"


def mutated_candidate(**changes: Any) -> dict[str, Any]:
    candidate = deepcopy(synthetic_candidate())
    candidate.update(changes)
    return candidate


def authenticate_manifest_decision_report() -> None:
    manifest = load_json(MANIFEST)
    relation = manifest.get("relation")
    if (
        manifest.get("schema_id")
        != "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_ENVELOPE_V1"
        or not isinstance(relation, dict)
        or manifest.get("relation_sha256") != digest(relation)
        or relation.get("artifact_class")
        != "STATIC_NONAUTHORITY_NONCONSUMABLE_NONEXECUTABLE_INTEGRATION_PROOF"
        or relation.get("capability_id") != CAPABILITY_ID
        or relation.get("integration_readiness") != "PROVEN"
        or relation.get("production_route_count") != "1 -> 1"
        or relation.get("new_capability_required") != "NO"
        or relation.get("operational_retry_authorized") != "NO"
        or set(relation.get("lu_execution_counters", {}).values()) != {0}
        or relation.get("failure_matrix")
        != {letter: "REJECT" if letter != "A" else "INTEGRATION_READY" for letter in "ABCDEFGHIJKLMN"}
    ):
        raise RuntimeError("STATIC_RELATION_SEAL_OR_SEMANTICS_CONFLICT")

    envelope = load_json(DECISION)
    decision = envelope.get("decision")
    evidence = envelope.get("evidence")
    if (
        envelope.get("schema_id") != "G77_256LU_TERMINAL_DECISION_ENVELOPE_V1"
        or not isinstance(decision, dict)
        or envelope.get("decision_sha256") != digest(decision)
        or not isinstance(evidence, dict)
        or decision.get("FAILURE_CLASS") != "PROOF_GAP"
        or decision.get("INTEGRATION_READINESS") != "PROVEN"
        or decision.get("NEW_CAPABILITY_REQUIRED") != "NO"
        or decision.get("NEW_CAPABILITY_CREATED") != "NO"
        or decision.get("PRODUCTION_BEHAVIOR_IMPACT") != "NONE"
        or decision.get("OPERATIONAL_RETRY_AUTHORIZED") != "NO"
        or evidence.get("terminal") != TERMINAL
        or set(evidence.get("operational_counters_lu", {}).values()) != {0}
        or evidence.get("e05")
        != {
            "E05_BEFORE": "12/18",
            "LU_E05_CREDIT": 0,
            "E05_AFTER": "12/18",
            "WRONG_SCOPE_STATUS": "UNSAT",
        }
    ):
        raise RuntimeError("LU_DECISION_SEAL_OR_SEMANTICS_CONFLICT")

    report = REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Static Integration Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]:
        raise RuntimeError("G48_EXACTLY_SIX_H1_CONFLICT")
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    if any(report.count(question) != 1 for question in questions):
        raise RuntimeError("G48_REUSE_QUESTION_CARDINALITY_CONFLICT")
    distinctions = (
        "PRODUCTION SEMANTICS",
        "LT HARNESS CAPABILITY",
        "STATIC INTEGRATION READINESS",
        "SYNTHETIC/STATIC PROOF",
        "OPERATIONAL PROOF",
        "UNKNOWN",
    )
    if any(term not in report for term in distinctions):
        raise RuntimeError("PROOF_LAYER_DISTINCTION_MISSING")


def active_qemu_processes() -> list[str]:
    output = subprocess.check_output(["ps", "-eo", "comm=,args="], text=True)
    return [line for line in output.splitlines() if line.split(None, 1)[0].startswith("qemu")]


def verify(remote_head: str, nested_remote_tag: str) -> str:
    authenticate_entry(remote_head, nested_remote_tag)
    authenticate_predecessors()
    authenticate_code_relation()
    authenticate_manifest_decision_report()
    if validate_static_candidate(synthetic_candidate()) != "STATIC_INTEGRATION_READY":
        raise RuntimeError("SYNTHETIC_STATIC_BINDING_NOT_READY")
    if active_qemu_processes():
        raise RuntimeError("QEMU_PROCESS_ACTIVE_DURING_LU_STATIC_VERIFICATION")
    print(TERMINAL)
    return TERMINAL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    verify(arguments.remote_head, arguments.nested_remote_tag)
