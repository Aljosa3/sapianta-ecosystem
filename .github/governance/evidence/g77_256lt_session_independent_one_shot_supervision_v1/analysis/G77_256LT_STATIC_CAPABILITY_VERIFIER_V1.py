#!/usr/bin/env python3
"""Read-only verifier for the bounded G77-256LT supervision capability."""

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
LT_REL = Path(
    ".github/governance/evidence/"
    "g77_256lt_session_independent_one_shot_supervision_v1"
)
LT = ROOT / LT_REL
HARNESS = LT / "harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py"
TEST = LT / "tests/test_g77_256lt_one_shot_supervision_v1.py"
DECISION = LT / "G77_256LT_TERMINAL_DECISION_V1.json"
REPORT = LT / "G77_256LT_G48_IMPLEMENTATION_REPORT_V1.md"
LS = ROOT / (
    ".github/governance/evidence/"
    "g77_256ls_wrong_scope_terminal_observation_gap_discovery_v1"
)
LS_DECISION = LS / "G77_256LS_TERMINAL_OBSERVATION_GAP_DISCOVERY_V1.json"
LS_REPORT = LS / "G77_256LS_G48_IMPLEMENTATION_REPORT_V1.md"
LR_CONTROLLER = ROOT / (
    ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1/"
    "orchestration/G77_256LR_ONE_SHOT_CONTROLLER_V1.py"
)
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
NESTED = ROOT / "sapianta_system"

LS_HEAD = "8b3bff5ee417333ebe97df3b42e62462b8e21f62"
LS_TREE = "830d6b462ba1fa9e3c54b6250576fe0016a31713"
LS_SUBJECT = "G77-256LS classify WRONG_SCOPE terminal observation gap"
LR_HEAD = "b738b0795b9d50b60819bbbf31e49fab6b47ed5d"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
LS_DECISION_SHA256 = "9684e6304d641c865405570c8af26060566bc0eda9cce2a7036a04dcf349db7d"
LS_REPORT_SHA256 = "f2f3bfbc4ab9a8b2bb46d7accce1e28946ba73f518765105e5d5e93b96672d9f"
LR_CONTROLLER_SHA256 = "89a7ebf2f6d7972e6899956b947c20a1614db2c9d53e5d3ac97816929a31b1b0"
FM_SHA256 = "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8"
CAPABILITY_ID = (
    "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_"
    "DURABLE_TERMINAL_HANDOFF_V1"
)
TERMINAL = (
    "A__G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_FM_SUPERVISION_AND_"
    "DURABLE_TERMINAL_HANDOFF_IMPLEMENTED_AND_STATICALLY_PROVEN__"
    "ZERO_AUTHORITY__ZERO_OPERATION__ZERO_PRODUCTION_MUTATION__"
    "READY_FOR_HUMAN_REVIEW"
)


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


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    head = git(ROOT, "rev-parse", "HEAD")
    if (
        git(ROOT, "branch", "--show-current") != BRANCH
        or git(ROOT, "rev-parse", f"{LS_HEAD}^{{tree}}") != LS_TREE
        or git(ROOT, "show", "-s", "--format=%s", LS_HEAD) != LS_SUBJECT
        or not is_ancestor(LR_HEAD, LS_HEAD)
        or not is_ancestor(LS_HEAD, head)
        or int(git(ROOT, "rev-list", "--count", f"{LS_HEAD}..{head}")) > 1
        or remote_head != head
    ):
        raise RuntimeError("LS_ENTRY_OR_SINGLE_LT_SUCCESSOR_CONFLICT")
    prefix = LT_REL.as_posix() + "/"
    for line in git(ROOT, "status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line and not line[3:].startswith(prefix):
            raise RuntimeError(f"UNRELATED_WORKTREE_MUTATION:{line}")
    if head != LS_HEAD:
        changed = git(ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", LS_HEAD, head)
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
    expected = {
        LS_DECISION: LS_DECISION_SHA256,
        LS_REPORT: LS_REPORT_SHA256,
        LR_CONTROLLER: LR_CONTROLLER_SHA256,
        FM: FM_SHA256,
    }
    if any(path.is_symlink() or not path.is_file() or sha256(path) != digest
           for path, digest in expected.items()):
        raise RuntimeError("PREDECESSOR_IDENTITY_CONFLICT")
    ls = json.loads(LS_DECISION.read_bytes())
    if (
        ls["decision"]["failure_class"] != "HARNESS_OR_TEST_ARTIFACT"
        or ls["decision"]["minimum_missing_capability"] != CAPABILITY_ID
        or ls["decision"]["operational_retry_authorized"] != "NO"
        or ls["discovery"]["e05"]["after"] != "12/18"
        or ls["discovery"]["e05"]["wrong_scope"]
        != "UNSAT__OPERATIONAL_PROOF_INCOMPLETE"
    ):
        raise RuntimeError("LS_CLASSIFICATION_CONFLICT")
    controller = LR_CONTROLLER.read_text(encoding="utf-8")
    fm = FM.read_text(encoding="utf-8")
    if (
        "status = subprocess.run(final_argv, cwd=ROOT, check=False).returncode"
        not in controller
        or "result = subprocess.run(argv, check=False)" not in fm
        or "start_new_session=True" in controller + fm
    ):
        raise RuntimeError("LS_SESSION_BOUND_SOURCE_ANALYSIS_CONFLICT")


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"MISSING_FUNCTION:{name}")


def attribute_calls(node: ast.AST, owner: str, name: str) -> list[ast.Call]:
    return [
        call
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == owner
        and call.func.attr == name
    ]


def keyword_constant(call: ast.Call, name: str) -> object:
    for keyword in call.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return None


def authenticate_harness_static_contract() -> None:
    if HARNESS.is_symlink() or TEST.is_symlink():
        raise RuntimeError("UNSAFE_LT_SOURCE")
    source = HARNESS.read_text(encoding="utf-8")
    tree = ast.parse(source)
    required_functions = {
        "load_binding", "build_binding", "write_binding_once", "append_event",
        "read_journal", "reserve_once", "launch_detached", "supervise",
        "reconcile_without_relaunch", "latest_state",
    }
    if not required_functions.issubset(
        {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    ):
        raise RuntimeError("LT_HARNESS_INTERFACE_INCOMPLETE")
    launch = function(tree, "launch_detached")
    supervise_node = function(tree, "supervise")
    reconcile = function(tree, "reconcile_without_relaunch")
    supervisor_popen = attribute_calls(launch, "subprocess", "Popen")
    if len(supervisor_popen) != 1 or keyword_constant(supervisor_popen[0], "start_new_session") is not True:
        raise RuntimeError("DETACHED_SUPERVISOR_NOT_STATICALLY_PROVEN")
    child_popen_calls = [
        call for call in ast.walk(supervise_node)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "popen_factory"
    ]
    if len(child_popen_calls) != 1 or keyword_constant(child_popen_calls[0], "start_new_session") is not False:
        raise RuntimeError("EXACTLY_ONE_CHILD_LAUNCH_SITE_NOT_PROVEN")
    if any(
        isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id in {"popen_factory", "launch_detached", "supervise"})
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "Popen")
        )
        for node in ast.walk(reconcile)
    ):
        raise RuntimeError("RECOVERY_RELAUNCH_PATH_PRESENT")
    required_tokens = (
        "os.O_EXCL", "os.fsync", "NOT_STARTED", "STARTED", "RUNNING",
        "TERMINATED_WITH_STATUS", "INTERRUPTED_OR_LOST__UNKNOWN",
        "PROCESS_IDENTITY_UNAVAILABLE", "NO_RELAUNCH", "retry_count",
        "NONAUTHORITY", "HOST_SUPERVISION_ONLY__NOT_FM_PRE_OR_POST",
        "OPERATIONAL_ROUTE_FORBIDDEN_IN_SYNTHETIC_BINDING",
    )
    if not all(token in source for token in required_tokens):
        raise RuntimeError("FAIL_CLOSED_DURABLE_CONTRACT_TOKEN_MISSING")
    if any(token in source for token in ("systemd", "job queue", "scheduler", "retry queue")):
        raise RuntimeError("OVERENGINEERED_PROCESS_MANAGER_SURFACE")


def authenticate_tests() -> None:
    source = TEST.read_text(encoding="utf-8")
    tree = ast.parse(source)
    tests = {
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
    required_fragments = {
        "case_a", "case_b", "case_c", "case_d", "case_e", "case_f",
        "case_g", "case_h", "case_i", "case_j", "state_flush",
        "write_failure", "malformed_state", "synthetic_binding_rejects_qemu",
    }
    if any(not any(fragment in name for name in tests) for fragment in required_fragments):
        raise RuntimeError("SYNTHETIC_MATRIX_INCOMPLETE")
    if "SYNTHETIC_NON_OPERATIONAL_TEST" not in source:
        raise RuntimeError("TEST_EXECUTION_CLASS_NOT_SYNTHETIC")
    if "FUTURE_SEPARATELY_AUTHORIZED_FM_INVOCATION" in source:
        raise RuntimeError("TEST_ATTEMPTS_FUTURE_OPERATIONAL_CLASS")
    # qemu-system appears only as the expected rejected argv fixture.
    if source.count('argv=["qemu-system-x86_64", "-version"]') != 1:
        raise RuntimeError("QEMU_REJECTION_FIXTURE_CONFLICT")


def authenticate_decision_and_report() -> None:
    raw = DECISION.read_bytes()
    envelope = json.loads(raw)
    decision = envelope.get("decision")
    evidence = envelope.get("evidence")
    if (
        raw != canonical_bytes(envelope)
        or not isinstance(decision, dict)
        or envelope.get("decision_sha256")
        != hashlib.sha256(canonical_bytes(decision)).hexdigest()
        or not isinstance(evidence, dict)
        or decision.get("FAILURE_CLASS") != "HARNESS_OR_TEST_ARTIFACT"
        or decision.get("CAPABILITY_ID") != CAPABILITY_ID
        or decision.get("CAPABILITY_IMPLEMENTED")
        != "YES__GENERATION_LOCAL_HARNESS_ONLY"
        or decision.get("PRODUCTION_CAPABILITY_CREATED") != "NO"
        or decision.get("AUTHORITY_EFFECT") != "NONE"
        or decision.get("CONSUMABILITY") != "NONAUTHORITY"
        or decision.get("OPERATIONAL_RETRY_AUTHORIZED") != "NO"
        or evidence.get("terminal") != TERMINAL
        or set(evidence["operational_counters_lt"].values()) != {0}
        or set(evidence["architecture"].values()) - {0, 1}
        or evidence["architecture"]["ROUTE_COUNT_BEFORE"] != 1
        or evidence["architecture"]["ROUTE_COUNT_AFTER"] != 1
        or evidence["e05"]
        != {
            "E05_AFTER": "12/18",
            "E05_BEFORE": "12/18",
            "LT_E05_CREDIT": 0,
            "WRONG_SCOPE_STATUS": "UNSAT",
        }
    ):
        raise RuntimeError("LT_DECISION_SEAL_OR_SEMANTICS_CONFLICT")
    report = REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
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
        "PRODUCTION SEMANTICS", "HARNESS CAPABILITY", "STATIC/SYNTHETIC PROOF",
        "OPERATIONAL PROOF", "UNKNOWN",
    )
    if any(term not in report for term in distinctions):
        raise RuntimeError("PROOF_LAYER_DISTINCTION_MISSING")


def active_qemu_processes() -> list[str]:
    output = subprocess.check_output(["ps", "-eo", "comm=,args="], text=True)
    return [line for line in output.splitlines() if line.split(None, 1)[0].startswith("qemu")]


def verify(remote_head: str, nested_remote_tag: str) -> str:
    authenticate_entry(remote_head, nested_remote_tag)
    authenticate_predecessors()
    authenticate_harness_static_contract()
    authenticate_tests()
    authenticate_decision_and_report()
    if active_qemu_processes():
        raise RuntimeError("QEMU_PROCESS_ACTIVE_DURING_LT_STATIC_VERIFICATION")
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
