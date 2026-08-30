from __future__ import annotations

import ast
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable

import pytest


sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[5]
BINDING_PATH = REPO_ROOT / (
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)


def load_module(path: Path, identity: str):
    spec = importlib.util.spec_from_file_location(identity, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GF = load_module(BINDING_PATH, "g77_256gf_binding_under_test")


def git(root: Path, *arguments: str, input_text: str | None = None) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=root, text=True, input=input_text
    ).strip()


def instantiate(root: Path, prefix: str, *, clean: bool) -> tuple[dict[str, Any], tempfile.TemporaryDirectory[str], tempfile.TemporaryDirectory[str]]:
    repository_temp = tempfile.TemporaryDirectory(
        dir=root, prefix=".g77_256gf_live_binding_test_"
    )
    transient_temp = tempfile.TemporaryDirectory(
        dir="/tmp", prefix="g77_256gf_live_binding_test_"
    )
    parent = Path(repository_temp.name)
    result = GF.instantiate_live_binding(
        repository_root=root,
        output_root=parent / "binding",
        operation_evidence_root=parent / "operation_state",
        transient_root=Path(transient_temp.name) / "transient_state",
        identity_namespace_prefix=prefix,
        require_tracked_clean=clean,
    )
    return result, repository_temp, transient_temp


@pytest.fixture()
def live_binding():
    result, repository_temp, transient_temp = instantiate(
        REPO_ROOT, "G77_256GFTEST", clean=False
    )
    try:
        output = REPO_ROOT / result["live_binding_output_root"]
        yield {
            "result": result,
            "output": output,
            "candidate": REPO_ROOT / result["candidate_path"],
            "context": REPO_ROOT / result["context_path"],
            "eb_receipt": output / "bindings/CANDIDATE_BOUND_EB_RECEIPT_V1.json",
            "ee_receipt": output / "bindings/RUNTIME_CONSUMER_EE_RECEIPT_V1.json",
            "du": load_module(REPO_ROOT / GF.DU_PATH, "g77_256gf_du_test"),
            "eb": load_module(REPO_ROOT / GF.EB_PATH, "g77_256gf_eb_test"),
            "ee": load_module(REPO_ROOT / GF.EE_PATH, "g77_256gf_ee_test"),
            "launcher": load_module(REPO_ROOT / GF.LAUNCHER_PATH, "g77_256gf_launcher_test"),
        }
    finally:
        repository_temp.cleanup()
        transient_temp.cleanup()


def commit_corrected_checkpoint(clone: Path, parent: str) -> str:
    for relative in (GF.LAUNCHER_PATH, BINDING_PATH.relative_to(REPO_ROOT)):
        target = clone / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, target)
    git(clone, "read-tree", parent)
    for relative in (GF.LAUNCHER_PATH, BINDING_PATH.relative_to(REPO_ROOT)):
        blob = git(clone, "hash-object", "-w", relative.as_posix())
        git(
            clone,
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},{relative.as_posix()}",
        )
    tree = git(clone, "write-tree")
    environment = os.environ.copy()
    environment.update({
        "GIT_AUTHOR_NAME": "G77-256GF",
        "GIT_AUTHOR_EMAIL": "g77-256gf@example.invalid",
        "GIT_AUTHOR_DATE": "2001-01-01T00:00:00+00:00",
        "GIT_COMMITTER_NAME": "G77-256GF",
        "GIT_COMMITTER_EMAIL": "g77-256gf@example.invalid",
        "GIT_COMMITTER_DATE": "2001-01-01T00:00:00+00:00",
    })
    checkpoint = subprocess.check_output(
        ["git", "commit-tree", tree, "-p", parent],
        cwd=clone,
        text=True,
        input="G77-256GF corrected checkpoint A\n",
        env=environment,
    ).strip()
    git(clone, "update-ref", "HEAD", checkpoint)
    assert git(clone, "status", "--porcelain", "--untracked-files=no") == ""
    return checkpoint


def empty_successor_checkpoint(clone: Path, parent: str) -> str:
    tree = git(clone, "rev-parse", "HEAD^{tree}")
    environment = os.environ.copy()
    environment.update({
        "GIT_AUTHOR_NAME": "G77-256GF",
        "GIT_AUTHOR_EMAIL": "g77-256gf@example.invalid",
        "GIT_AUTHOR_DATE": "2001-01-01T00:00:01+00:00",
        "GIT_COMMITTER_NAME": "G77-256GF",
        "GIT_COMMITTER_EMAIL": "g77-256gf@example.invalid",
        "GIT_COMMITTER_DATE": "2001-01-01T00:00:01+00:00",
    })
    checkpoint = subprocess.check_output(
        ["git", "commit-tree", tree, "-p", parent],
        cwd=clone,
        text=True,
        input="G77-256GF synthetic checkpoint B\n",
        env=environment,
    ).strip()
    git(clone, "update-ref", "HEAD", checkpoint)
    assert git(clone, "status", "--porcelain", "--untracked-files=no") == ""
    return checkpoint


def test_current_committed_checkpoint_du_eb_ee_pass(live_binding):
    result = live_binding["result"]
    assert result["live_execution_repository_head"] == git(REPO_ROOT, "rev-parse", "HEAD")
    assert result["live_execution_repository_tree"] == git(REPO_ROOT, "rev-parse", "HEAD^{tree}")
    assert (result["du"], result["eb"], result["ee"]) == ("PASS", "PASS", "PASS")
    assert result["candidate_semantics_changed"] is False
    assert result["no_future_commit_hash_self_reference"] is True


def test_two_distinct_committed_checkpoints_need_no_source_or_validator_edit():
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="g77_256gf_clone_") as raw_clone:
        clone = Path(raw_clone) / "repository"
        subprocess.run(
            ["git", "clone", "--shared", "--no-checkout", str(REPO_ROOT), str(clone)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        base = git(REPO_ROOT, "rev-parse", "HEAD")
        git(clone, "checkout", "--detach", base)
        checkpoint_a = commit_corrected_checkpoint(clone, base)
        result_a, repo_temp_a, transient_temp_a = instantiate(
            clone, "G77_256GFPROOF", clean=True
        )
        repo_temp_a.cleanup()
        transient_temp_a.cleanup()

        checkpoint_b = empty_successor_checkpoint(clone, checkpoint_a)
        result_b, repo_temp_b, transient_temp_b = instantiate(
            clone, "G77_256GFPROOF", clean=True
        )
        repo_temp_b.cleanup()
        transient_temp_b.cleanup()

        assert checkpoint_a != checkpoint_b
        assert result_a["live_execution_repository_head"] == checkpoint_a
        assert result_b["live_execution_repository_head"] == checkpoint_b
        assert result_a["candidate_sha256"] != result_b["candidate_sha256"]
        assert result_a["context_sha256"] != result_b["context_sha256"]
        assert (result_a["du"], result_a["eb"], result_a["ee"]) == ("PASS",) * 3
        assert (result_b["du"], result_b["eb"], result_b["ee"]) == ("PASS",) * 3


def rehash_candidate(value: dict[str, Any], module: Any) -> None:
    if isinstance(value.get("manifest"), dict):
        value["manifest_sha256"] = module.sha256_bytes(
            module.canonical_bytes(value["manifest"])
        )


def rejection_code(operation: Callable[[], None]) -> str:
    try:
        operation()
    except Exception as exc:
        return getattr(exc, "code", str(exc))
    return "NOT_REJECTED"


def test_required_negative_matrix_fails_closed(live_binding):
    candidate = live_binding["candidate"]
    context_path = live_binding["context"]
    output = live_binding["output"]
    du = live_binding["du"]
    eb = live_binding["eb"]
    ee = live_binding["ee"]
    launcher = live_binding["launcher"]
    head = git(REPO_ROOT, "rev-parse", "HEAD")
    tree = git(REPO_ROOT, "rev-parse", "HEAD^{tree}")

    case_root = output / "negative_matrix"
    case_root.mkdir()

    def du_case(name: str, mutator: Callable[[dict[str, Any]], None]) -> str:
        value = json.loads(candidate.read_bytes())
        mutator(value)
        rehash_candidate(value, du)
        path = case_root / f"{name}.json"
        path.write_bytes(du.canonical_bytes(value))
        return rejection_code(lambda: du.validate_file(path, REPO_ROOT, expected_head=head))

    stale_context = json.loads(context_path.read_bytes())
    stale_context["context_sha256"] = "0" * 64
    changed_semantics = json.loads(candidate.read_bytes())
    changed_semantics["manifest"]["selected_case"]["case_id"] += "_CHANGED"
    rehash_candidate(changed_semantics, du)
    template = json.loads((REPO_ROOT / GF.TEMPLATE_PATH).read_bytes())

    eb_stale = json.loads(live_binding["eb_receipt"].read_bytes())
    eb_stale["receipt"]["required_head"] = GF.CERTIFICATION_PROVENANCE_HEAD
    eb_stale["receipt_inner_sha256"] = eb.sha256_bytes(
        eb.canonical_bytes(eb_stale["receipt"])
    )
    eb_stale_path = case_root / "stale_eb.json"
    eb_stale_path.write_bytes(eb.canonical_bytes(eb_stale))

    ee_stale = json.loads(live_binding["ee_receipt"].read_bytes())
    ee_stale["receipt"]["git_binding"]["required_head"] = GF.CERTIFICATION_PROVENANCE_HEAD
    ee_stale["receipt_inner_sha256"] = ee.sha256_bytes(
        ee.canonical_bytes(ee_stale["receipt"])
    )
    ee_stale_path = case_root / "stale_ee.json"
    ee_stale_path.write_bytes(ee.canonical_bytes(ee_stale))

    eb_bypass = json.loads(live_binding["eb_receipt"].read_bytes())
    eb_bypass["receipt"]["validator_binding"]["file_sha256"] = "0" * 64
    eb_bypass["receipt_inner_sha256"] = eb.sha256_bytes(
        eb.canonical_bytes(eb_bypass["receipt"])
    )
    eb_bypass_path = case_root / "validator_bypass.json"
    eb_bypass_path.write_bytes(eb.canonical_bytes(eb_bypass))

    outcomes = {
        "stale_pre_commit_head": rejection_code(
            lambda: du.validate_file(REPO_ROOT / GF.TEMPLATE_PATH, REPO_ROOT, expected_head=head)
        ),
        "wrong_committed_head": rejection_code(
            lambda: eb.validate_candidate(
                REPO_ROOT, candidate, required_head="0" * 40, required_tree=tree
            )
        ),
        "wrong_tree": rejection_code(
            lambda: eb.validate_candidate(
                REPO_ROOT, candidate, required_head=head, required_tree="0" * 40
            )
        ),
        "stale_live_candidate_binding": rejection_code(
            lambda: launcher.validate_immutable_context_bindings(
                REPO_ROOT,
                json.loads(context_path.read_bytes()),
                candidate_source_path=GF.TEMPLATE_PATH,
            )
        ),
        "stale_du_binding": du_case(
            "stale_du",
            lambda value: value["manifest"]["consumer_binding"].update({"sha256": "0" * 64}),
        ),
        "stale_eb_receipt": rejection_code(
            lambda: eb.verify_receipt_file(REPO_ROOT, eb_stale_path)
        ),
        "stale_ee_receipt": rejection_code(
            lambda: ee.verify_receipt_file(REPO_ROOT, ee_stale_path)
        ),
        "wrong_context_sha": rejection_code(
            lambda: launcher.fresh_context.validate_context(
                stale_context, repository_root=REPO_ROOT
            )
        ),
        "wrong_candidate_semantic_identity": rejection_code(
            lambda: GF.validate_candidate_semantics(changed_semantics, template)
        ),
        "wrong_wrapper_source_identity": du_case(
            "wrong_wrapper",
            lambda value: next(
                item
                for item in value["manifest"]["extension_bindings"]
                if item["identity"] == "G77_256FM_WRONG_ATTEMPT_ADAPTER"
            ).update({"sha256": "0" * 64}),
        ),
        "historical_operation_binding_reuse": rejection_code(
            lambda: GF.instantiate_live_binding(
                repository_root=REPO_ROOT,
                output_root=output,
                operation_evidence_root=output.parent / "unused_operation",
                transient_root=Path("/tmp/g77_256gf_unused_transient"),
                identity_namespace_prefix="G77_256GFTEST",
                require_tracked_clean=False,
            )
        ),
        "future_head_placeholder": du_case(
            "future_head", lambda value: value["manifest"].update({"required_head": "f" * 40})
        ),
        "wildcard_head": du_case(
            "wildcard_head", lambda value: value["manifest"].update({"required_head": "*"})
        ),
        "missing_head": du_case(
            "missing_head", lambda value: value["manifest"].pop("required_head")
        ),
        "manual_alias_substitution": du_case(
            "manual_alias",
            lambda value: value["manifest"].update({"source_tree": template["manifest"]["source_tree"]}),
        ),
        "validator_bypass": rejection_code(
            lambda: eb.verify_receipt_file(REPO_ROOT, eb_bypass_path)
        ),
    }

    original = candidate.read_bytes()
    rewritten = json.loads(original)
    rewritten["manifest"]["observations"].append("POST_HOC_REWRITE")
    rehash_candidate(rewritten, du)
    try:
        candidate.write_bytes(du.canonical_bytes(rewritten))
        outcomes["post_hoc_evidence_rewriting"] = rejection_code(
            lambda: ee.verify_receipt_file(REPO_ROOT, live_binding["ee_receipt"])
        )
    finally:
        candidate.write_bytes(original)

    assert set(outcomes) == {
        "stale_pre_commit_head", "wrong_committed_head", "wrong_tree",
        "stale_live_candidate_binding", "stale_du_binding", "stale_eb_receipt",
        "stale_ee_receipt", "wrong_context_sha", "wrong_candidate_semantic_identity",
        "wrong_wrapper_source_identity", "historical_operation_binding_reuse",
        "future_head_placeholder", "wildcard_head", "missing_head",
        "manual_alias_substitution", "validator_bypass", "post_hoc_evidence_rewriting",
    }
    assert all(value != "NOT_REJECTED" for value in outcomes.values()), outcomes


def test_governed_launcher_requires_explicit_live_candidate_argument():
    source = (REPO_ROOT / GF.LAUNCHER_PATH).read_text(encoding="utf-8")
    assert 'parser.add_argument("--live-candidate-binding", required=True, type=Path)' in source
    assert "candidate_source_path=candidate_source_path" in source
    calls = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
        and node.args
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "argv"
    ]
    assert len(calls) == 1


def test_zero_operational_authority_and_effects(live_binding):
    result = live_binding["result"]
    assert result["artifact_class"] == "LIVE_BINDING__NON_AUTHORITY__NON_OPERATIONAL"
    for field in (
        "human_operational_authorization_count",
        "qemu_execution_count",
        "vm_boot_count",
        "request_count",
        "p11_entry_count",
        "protected_invocation_count",
        "protected_effect_count",
    ):
        assert result[field] == 0
    assert result["auto_continuable"] is False
    assert result["human_review_required"] is True
