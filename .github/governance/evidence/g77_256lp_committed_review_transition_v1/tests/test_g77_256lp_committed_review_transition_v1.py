"""Static fail-closed tests for the FM committed-review transition capability."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[5]
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LM_CONTEXT = ROOT / (
    ".github/governance/evidence/g77_256lm_wrong_scope_receipt_parent_phase_a_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
SPEC = importlib.util.spec_from_file_location("g77_256lp_fm", FM_PATH)
assert SPEC is not None and SPEC.loader is not None
FM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FM)


def git(repository: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository, text=True
    ).strip()


def commit(repository: Path, message: str) -> tuple[str, str]:
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", message)
    return git(repository, "rev-parse", "HEAD"), git(repository, "rev-parse", "HEAD^{tree}")


def context_bytes(context: dict) -> bytes:
    return FM.canonical_bytes(context)


def make_repository(tmp_path: Path) -> dict:
    repository = tmp_path / "repository"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    git(repository, "config", "user.name", "G77-256LP Static Test")
    git(repository, "config", "user.email", "g77-256lp@example.invalid")
    (repository / "baseline.txt").write_text("baseline\n")
    base_head, base_tree = commit(repository, "baseline")

    relative = Path(
        ".github/governance/evidence/g77_256lptest_wrong_scope_v1/"
        "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )
    context_path = repository / relative
    context_path.parent.mkdir(parents=True)
    context = {
        "generation_identity": (
            "G77_256LPTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        "operation_identity": "G77_256LPTEST_OPERATION_001",
        "repository_head": base_head,
        "repository_tree": base_tree,
        "operation_evidence_root": str(
            repository
            / ".github/governance/evidence/g77_256lptest_wrong_scope_v1/operation_state"
        ),
    }
    context["context_sha256"] = FM.hashlib.sha256(
        FM.canonical_bytes(context)
    ).hexdigest()
    context_path.write_bytes(context_bytes(context))
    review_head, review_tree = commit(repository, "commit exact review object")

    (repository / "G77_256LPTEST_REPORT.md").write_text("terminal evidence\n")
    copy_path = repository / "copied_context.json"
    copy_path.write_bytes(context_bytes(context))
    current_head, current_tree = commit(repository, "successor evidence")
    proof = FM.build_committed_review_transition(
        repository_root=repository,
        context=context,
        current_admission_head=current_head,
        current_admission_tree=current_tree,
    )
    return {
        "repository": repository,
        "context": context,
        "context_path": context_path,
        "base_head": base_head,
        "base_tree": base_tree,
        "review_head": review_head,
        "review_tree": review_tree,
        "current_head": current_head,
        "current_tree": current_tree,
        "proof": proof,
    }


def authenticate(fixture: dict, proofs=None, *, head=None, tree=None):
    return FM.authenticate_review_to_current_admission(
        repository_root=fixture["repository"],
        context=fixture["context"],
        observed_head=fixture["current_head"] if head is None else head,
        observed_tree=fixture["current_tree"] if tree is None else tree,
        committed_review_transitions=[fixture["proof"]] if proofs is None else proofs,
    )


def test_authenticated_lm_object_derives_one_exact_transition() -> None:
    context = FM.fresh_context.load_context(LM_CONTEXT, repository_root=ROOT)
    head = git(ROOT, "rev-parse", "HEAD")
    tree = git(ROOT, "rev-parse", "HEAD^{tree}")
    proof = FM.build_committed_review_transition(
        repository_root=ROOT,
        context=context,
        current_admission_head=head,
        current_admission_tree=tree,
    )
    assert proof["review_object_head"] == "7368af35f707f75f4d0951133995013211699126"
    assert proof["review_base_head"] == "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
    assert proof["current_admission_head"] == head
    assert proof["transition_is_authority"] is False
    assert proof["transition_consumable"] is False
    preauthority = FM.preauthority_serialization_fixture(
        context,
        current_admission_head=head,
        current_admission_tree=tree,
        committed_review_transition_sha256=proof["transition_sha256"],
    )
    assert preauthority["authorization_present"] is False
    assert preauthority["authorized_repository_head"] == head
    assert preauthority["authorized_repository_tree"] == tree
    FM.validate_preauthority_serialization_fixture(
        context,
        preauthority,
        current_admission_head=head,
        current_admission_tree=tree,
        committed_review_transition_sha256=proof["transition_sha256"],
    )
    assert authenticate(
        {"repository": ROOT, "context": context, "current_head": head,
         "current_tree": tree, "proof": proof}
    )["repository_identity_relation"].startswith("EXACT_COMMITTED_REVIEW")


def test_positive_exact_transition_and_deterministic_nonconsumable_replay(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    first = authenticate(fixture)
    second = authenticate(fixture)
    assert first == second
    assert first["committed_review_transition_sha256"] == fixture["proof"]["transition_sha256"]
    assert fixture["proof"]["transition_consumable"] is False


def test_canonical_transition_file_loader_binds_exact_bytes(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    path = tmp_path / "transition.json"
    raw = FM.canonical_bytes(fixture["proof"])
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    assert FM.load_committed_review_transition(path, digest) == fixture["proof"]
    with pytest.raises(RuntimeError, match="file hash mismatch"):
        FM.load_committed_review_transition(path, "0" * 64)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("review_object_head", "0" * 40),
        ("review_object_tree", "1" * 40),
        ("current_admission_head", "2" * 40),
        ("current_admission_tree", "3" * 40),
        ("review_context_sha256", "4" * 64),
        ("review_object_path", "copied_context.json"),
        ("review_object_sha256", "5" * 64),
        ("transition_state", "STALE"),
    ),
)
def test_wrong_bound_identity_copy_or_stale_state_fails_closed(
    tmp_path: Path, field: str, value: str
) -> None:
    fixture = make_repository(tmp_path)
    proof = copy.deepcopy(fixture["proof"])
    proof[field] = value
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [proof])


def test_missing_and_ambiguous_transition_proofs_fail_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    for proofs in ([], [fixture["proof"], copy.deepcopy(fixture["proof"])], {}, ["invalid"]):
        with pytest.raises(RuntimeError, match="missing or ambiguous"):
            authenticate(fixture, proofs)


def test_exact_delta_omission_and_unbound_mutation_fail_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    proof = copy.deepcopy(fixture["proof"])
    proof["exact_committed_delta"] = proof["exact_committed_delta"][:-1]
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [proof])

    (fixture["repository"] / "unbound.txt").write_text("not in prior proof\n")
    descendant_head, descendant_tree = commit(fixture["repository"], "unbound descendant")
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [fixture["proof"]], head=descendant_head, tree=descendant_tree)


def test_arbitrary_ancestor_and_same_branch_wrong_commit_fail_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    proof = copy.deepcopy(fixture["proof"])
    proof["review_object_head"] = fixture["base_head"]
    proof["review_object_tree"] = fixture["base_tree"]
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [proof])

    (fixture["repository"] / "later.txt").write_text("later\n")
    descendant_head, descendant_tree = commit(fixture["repository"], "later on same branch")
    with pytest.raises(RuntimeError, match="not observed Git"):
        authenticate(
            fixture,
            [fixture["proof"]],
            head=fixture["current_head"],
            tree=fixture["current_tree"],
        )
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [fixture["proof"]], head=descendant_head, tree=descendant_tree)


def test_sibling_commit_substitution_fails_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    git(fixture["repository"], "checkout", "-q", "-b", "sibling", fixture["review_head"])
    (fixture["repository"] / "sibling.txt").write_text("sibling\n")
    sibling_head, sibling_tree = commit(fixture["repository"], "sibling")
    with pytest.raises(RuntimeError, match="transition proof mismatch"):
        authenticate(fixture, [fixture["proof"]], head=sibling_head, tree=sibling_tree)


def test_post_review_rebinding_fails_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    fixture["context_path"].write_text("{}\n")
    rebound_head, rebound_tree = commit(fixture["repository"], "rebind reviewed object")
    with pytest.raises(RuntimeError, match="removed, rebound, or modified"):
        FM.build_committed_review_transition(
            repository_root=fixture["repository"],
            context=fixture["context"],
            current_admission_head=rebound_head,
            current_admission_tree=rebound_tree,
        )


def test_delete_and_readd_supersession_is_ambiguous_and_fails_closed(tmp_path: Path) -> None:
    fixture = make_repository(tmp_path)
    fixture["context_path"].unlink()
    commit(fixture["repository"], "delete review object")
    fixture["context_path"].write_bytes(context_bytes(fixture["context"]))
    superseded_head, superseded_tree = commit(fixture["repository"], "readd copied review object")
    with pytest.raises(RuntimeError, match="introduction missing or ambiguous"):
        FM.build_committed_review_transition(
            repository_root=fixture["repository"],
            context=fixture["context"],
            current_admission_head=superseded_head,
            current_admission_tree=superseded_tree,
        )


def test_same_head_path_remains_exact_and_rejects_transition_injection() -> None:
    context = {"repository_head": "a" * 40, "repository_tree": "b" * 40}
    result = FM.authenticate_review_to_current_admission(
        repository_root=None,
        context=context,
        observed_head="a" * 40,
        observed_tree="b" * 40,
    )
    assert result["repository_identity_relation"] == "EXACT_SAME_HEAD_TREE"
    with pytest.raises(RuntimeError, match="must not select"):
        FM.authenticate_review_to_current_admission(
            repository_root=None,
            context=context,
            observed_head="a" * 40,
            observed_tree="b" * 40,
            committed_review_transitions=[{"unexpected": True}],
        )
