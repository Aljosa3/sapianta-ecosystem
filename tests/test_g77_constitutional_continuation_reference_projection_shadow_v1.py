from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from aigol.runtime.constitutional_continuation_reference_projection_shadow_v1 import (
    CONTRACT_IDENTITY,
    CONTRACT_VERSION,
    EQUAL,
    FAILED_CLOSED,
    MISMATCH,
    compare_constitutional_continuation_reference_projection_shadow_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize


DOMAIN_PREFIX = (
    "SAPIANTA_CANONICAL_CONSTITUTIONAL_CONTINUATION_REFERENCE_"
    "PROJECTION_CONTRACT\nCONTRACT_VERSION=V1\n"
)
SOURCE_MODULE = (
    "aigol/runtime/constitutional_continuation_reference_projection_shadow_v1.py"
)


def _run_git(
    root: Path,
    *args: str,
    input_bytes: bytes | None = None,
    env: dict[str, str] | None = None,
) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_bytes,
        check=False,
        capture_output=True,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")
    return completed.stdout


def _git_text(root: Path, *args: str) -> str:
    return _run_git(root, *args).decode("utf-8").rstrip("\n")


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _projection_hash(payload: dict) -> str:
    body = DOMAIN_PREFIX.encode("utf-8") + canonical_serialize(payload).encode("utf-8")
    return _sha256(body)


def _blob_identity(root: Path, commit: str, path: str) -> str:
    line = _run_git(root, "ls-tree", "-r", commit, "--", path).decode("utf-8").strip()
    assert line
    return line.split()[2]


def _commit(root: Path, message: str) -> str:
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-q", "-m", message)
    return _git_text(root, "rev-parse", "HEAD")


def _fixture(tmp_path: Path) -> tuple[Path, dict, str, str]:
    root = tmp_path / "repository"
    root.mkdir()
    _run_git(root, "init", "-q")
    _run_git(root, "config", "user.name", "G77 Test")
    _run_git(root, "config", "user.email", "g77@example.invalid")

    evidence_path = "docs/evidence/EVIDENCE_1.md"
    evidence_bytes = b"AUTHENTICATED_EVIDENCE = PRESENT\n"
    (root / evidence_path).parent.mkdir(parents=True)
    (root / evidence_path).write_bytes(evidence_bytes)
    reference_commit = _commit(root, "G77 reference evidence")
    reference_blob = _blob_identity(root, reference_commit, evidence_path)

    predecessor_path = "docs/governance/G77_TEST.md"
    predecessor_bytes = (
        b"CURRENT_CONSTITUTIONAL_FRONTIER = TEST_FRONTIER\n"
        b"HUMAN_CONSTITUTIONAL_AUTHORITY_SHARE = 100_PERCENT\n"
        b"LLM_SEMANTIC_AUTHORITY_SHARE = 0_PERCENT\n"
    )
    (root / predecessor_path).parent.mkdir(parents=True, exist_ok=True)
    (root / predecessor_path).write_bytes(predecessor_bytes)
    head = _commit(root, "G77 test predecessor")

    payload = {
        "PREDECESSOR_ID": {
            "artifact_id": "G77-TEST",
            "repository_path": predecessor_path,
        },
        "PREDECESSOR_GIT_IDENTITY": {
            "commit": head,
            "parents": _git_text(root, "show", "-s", "--format=%P", head).split(),
            "subject": "G77 test predecessor",
            "tree": _git_text(root, "rev-parse", f"{head}^{{tree}}"),
        },
        "PREDECESSOR_SHA256": _sha256(predecessor_bytes),
        "CURRENT_CONSTITUTIONAL_FRONTIER": "TEST_FRONTIER",
        "CLOSED_COORDINATES": ["H01_E07", "H02_E09"],
        "OPEN_COORDINATE": "H03_E10_D1__REACHED_INCOMPLETE",
        "RELEVANT_INVARIANTS": sorted(
            [
                "HISTORY_REFERENCED_NOT_REPLACED",
                "HUMAN_ONLY_SEMANTIC_AUTHORITY",
                "TOPOLOGY_UNCHANGED",
            ]
        ),
        "HUMAN_AUTHORITY_STATE": {
            "constitutional_authority_owner": "HUMAN_CONSTITUTIONAL_AUTHORITY",
            "constitutional_authority_share": "100_PERCENT",
            "exact_human_act_required_for_semantic_advancement": True,
            "semantic_advancement_authorized_by_projection": False,
        },
        "COGNITION_PROVENANCE_STATE": {
            "admissible_provenance": sorted(
                ["AIGOL_MECHANICALLY_DERIVED", "AUTHENTICATED_REPOSITORY_EVIDENCE"]
            ),
            "llm_semantic_authority_share": "0_PERCENT",
            "unknown_provenance_admissible": False,
        },
        "ALLOWED_NEXT_OPERATION": "PRESERVE_EXACT_HUMAN_RESPONSE",
        "FORBIDDEN_OPERATIONS": sorted(
            ["ADVANCE_H03", "INVENT_STATE", "MUTATE_TOPOLOGY"]
        ),
        "TOPOLOGY_COMMITMENT": {
            "AUTHORITY_PATHS": 1,
            "HUMAN_ENTRY_PATHS": 1,
            "PARALLEL_PATHS": 0,
            "PRODUCTION_PATHS": 1,
        },
        "RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE": [
            {
                "artifact_id": "EVIDENCE-1",
                "git_blob": reference_blob,
                "git_commit": reference_commit,
                "repository_path": evidence_path,
                "sha256": _sha256(evidence_bytes),
            }
        ],
        "STOP_FAIL_CLOSED_CONDITIONS": sorted(
            ["AMBIGUOUS_FRONTIER", "EVIDENCE_MISMATCH", "TOPOLOGY_DRIFT"]
        ),
    }
    assert not _git_text(root, "status", "--porcelain")
    return root, payload, _projection_hash(payload), head


def _compare(
    root: Path,
    payload: dict,
    projection_hash: str,
    head: str,
    *,
    current: dict | None = None,
    serialized: str | None = None,
):
    return compare_constitutional_continuation_reference_projection_shadow_v1(
        serialized_projection=(
            canonical_serialize(payload) if serialized is None else serialized
        ),
        projection_hash=projection_hash,
        authenticated_current_payload=payload if current is None else current,
        repository_root=root,
        expected_head=head,
    )


def test_exact_v1_domain_hash_determinism_zero_authority_and_immutability(
    tmp_path: Path,
) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    serialized = canonical_serialize(payload)

    first = _compare(root, payload, projection_hash, head)
    second = _compare(root, payload, projection_hash, head)

    assert first == second
    assert first["outcome"] == EQUAL
    assert first["contract_identity"] == CONTRACT_IDENTITY
    assert first["contract_version"] == CONTRACT_VERSION
    assert first["projection_hash"] == projection_hash
    assert first["authenticated_current_hash"] == projection_hash
    assert projection_hash == _sha256(
        DOMAIN_PREFIX.encode("utf-8") + serialized.encode("utf-8")
    )
    for field in (
        "semantic_authority",
        "execution_authority",
        "production_authority",
        "human_authority",
        "routing_authority",
        "state_mutation_authority",
        "repair_performed",
        "state_invented",
        "semantic_advancement_performed",
    ):
        assert first[field] is False
    with pytest.raises(TypeError):
        first["outcome"] = MISMATCH


def test_ascii_safe_canonical_equality_is_byte_exact(tmp_path: Path) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    payload["RELEVANT_INVARIANTS"] = sorted(
        [*payload["RELEVANT_INVARIANTS"], "ČLOVEK_OHRANI_AVTORITETO"]
    )
    serialized = canonical_serialize(payload)
    projection_hash = _projection_hash(payload)

    assert "Č" not in serialized
    assert "\\u010c" in serialized
    assert _compare(root, payload, projection_hash, head)["outcome"] == EQUAL


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: value.pop("OPEN_COORDINATE"),
        lambda value: value.__setitem__("UNKNOWN_FIELD", "FORBIDDEN"),
        lambda value: value.__setitem__("OPEN_COORDINATE", None),
        lambda value: value.__setitem__("CURRENT_CONSTITUTIONAL_FRONTIER", ["A", "B"]),
        lambda value: value["RELEVANT_INVARIANTS"].append(
            value["RELEVANT_INVARIANTS"][0]
        ),
        lambda value: value["FORBIDDEN_OPERATIONS"].reverse(),
        lambda value: value["PREDECESSOR_ID"].__setitem__("extra", "FORBIDDEN"),
        lambda value: value["PREDECESSOR_ID"].__setitem__(
            "repository_path", "../outside"
        ),
    ],
)
def test_fourteen_field_and_nested_contract_is_closed(tmp_path: Path, mutator) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    mutator(payload)
    result = _compare(root, payload, _projection_hash(payload), head)
    assert result["outcome"] == FAILED_CLOSED
    assert result["manual_continuation_preserved"] is True


@pytest.mark.parametrize(
    "serialized",
    [
        '{"A":1,"A":2}',
        '{"A":1.5}',
        '{"A":NaN}',
        '["not-an-object"]',
        '',
    ],
)
def test_malformed_duplicate_float_and_non_object_input_fail_closed(
    tmp_path: Path, serialized: str
) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    result = _compare(
        root,
        payload,
        projection_hash,
        head,
        serialized=serialized,
    )
    assert result["outcome"] == FAILED_CLOSED


def test_noncanonical_serialization_and_tampered_hash_fail_closed(tmp_path: Path) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    noncanonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)

    assert _compare(
        root, payload, projection_hash, head, serialized=noncanonical
    )["outcome"] == FAILED_CLOSED
    assert _compare(
        root, payload, "sha256:" + "0" * 64, head
    )["outcome"] == FAILED_CLOSED


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("tree", "0" * 40),
        ("parents", []),
        ("subject", "wrong subject"),
    ],
)
def test_predecessor_git_identity_mismatch_fails_closed(
    tmp_path: Path, field: str, replacement
) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    payload["PREDECESSOR_GIT_IDENTITY"][field] = replacement
    result = _compare(root, payload, _projection_hash(payload), head)
    assert result["outcome"] == FAILED_CLOSED


def test_wrong_and_stale_head_fail_closed(tmp_path: Path) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    wrong = deepcopy(payload)
    wrong["PREDECESSOR_GIT_IDENTITY"]["commit"] = payload[
        "PREDECESSOR_GIT_IDENTITY"
    ]["parents"][0]
    assert _compare(
        root, wrong, _projection_hash(wrong), head
    )["outcome"] == FAILED_CLOSED

    (root / "later.txt").write_text("later\n", encoding="utf-8")
    later_head = _commit(root, "later commit")
    assert _compare(
        root, payload, projection_hash, later_head
    )["outcome"] == FAILED_CLOSED


def test_predecessor_and_evidence_tamper_rejection(tmp_path: Path) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)

    predecessor_tamper = deepcopy(payload)
    predecessor_tamper["PREDECESSOR_SHA256"] = "sha256:" + "1" * 64
    assert _compare(
        root,
        predecessor_tamper,
        _projection_hash(predecessor_tamper),
        head,
    )["outcome"] == FAILED_CLOSED

    blob_tamper = deepcopy(payload)
    blob_tamper["RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE"][0]["git_blob"] = "2" * 40
    assert _compare(
        root, blob_tamper, _projection_hash(blob_tamper), head
    )["outcome"] == FAILED_CLOSED

    digest_tamper = deepcopy(payload)
    digest_tamper["RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE"][0]["sha256"] = (
        "sha256:" + "3" * 64
    )
    assert _compare(
        root, digest_tamper, _projection_hash(digest_tamper), head
    )["outcome"] == FAILED_CLOSED


def test_divergent_evidence_lineage_fails_closed(tmp_path: Path) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    tree = _git_text(root, "rev-parse", f"{head}^{{tree}}")
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "G77 Test",
            "GIT_AUTHOR_EMAIL": "g77@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_NAME": "G77 Test",
            "GIT_COMMITTER_EMAIL": "g77@example.invalid",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        }
    )
    divergent = _run_git(
        root,
        "commit-tree",
        tree,
        input_bytes=b"divergent\n",
        env=env,
    ).decode("ascii").strip()
    payload["RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE"][0]["git_commit"] = divergent

    result = _compare(root, payload, _projection_hash(payload), head)
    assert result["outcome"] == FAILED_CLOSED
    assert result["failure_reason"] == "DIVERGENT_EVIDENCE_LINEAGE"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["TOPOLOGY_COMMITMENT"].__setitem__("PARALLEL_PATHS", 1),
        lambda value: value["TOPOLOGY_COMMITMENT"].__setitem__("AUTHORITY_PATHS", 2),
        lambda value: value["COGNITION_PROVENANCE_STATE"].__setitem__(
            "llm_semantic_authority_share", "1_PERCENT"
        ),
        lambda value: value["COGNITION_PROVENANCE_STATE"].__setitem__(
            "unknown_provenance_admissible", True
        ),
        lambda value: value["HUMAN_AUTHORITY_STATE"].__setitem__(
            "semantic_advancement_authorized_by_projection", True
        ),
    ],
)
def test_topology_authority_and_cognition_cannot_change_or_repair_state(
    tmp_path: Path, mutation
) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    mutation(payload)
    result = _compare(root, payload, _projection_hash(payload), head)
    assert result["outcome"] == FAILED_CLOSED
    assert result["repair_performed"] is False
    assert result["state_invented"] is False
    assert result["semantic_advancement_performed"] is False


def test_valid_current_mismatch_is_reported_without_authority(tmp_path: Path) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    current = deepcopy(payload)
    current["ALLOWED_NEXT_OPERATION"] = "DIFFERENT_AUTHENTICATED_OPERATION"

    result = _compare(root, payload, projection_hash, head, current=current)

    assert result["outcome"] == MISMATCH
    assert result["manual_continuation_preserved"] is True
    assert result["semantic_authority"] is False
    assert result["routing_authority"] is False


def test_failure_preserves_repository_inputs_and_all_fallbacks(tmp_path: Path) -> None:
    root, payload, _projection_hash_value, head = _fixture(tmp_path)
    payload_before = deepcopy(payload)
    head_before = _git_text(root, "rev-parse", "HEAD")
    status_before = _git_text(root, "status", "--porcelain")
    predecessor_path = root / payload["PREDECESSOR_ID"]["repository_path"]
    bytes_before = predecessor_path.read_bytes()

    result = _compare(root, payload, "sha256:" + "f" * 64, head)

    assert result["outcome"] == FAILED_CLOSED
    assert result["manual_continuation_preserved"] is True
    assert result["bounded_cognition_fallback_preserved"] is True
    assert result["broader_history_reconstruction_preserved"] is True
    assert result["repair_performed"] is False
    assert result["state_invented"] is False
    assert payload == payload_before
    assert predecessor_path.read_bytes() == bytes_before
    assert _git_text(root, "rev-parse", "HEAD") == head_before
    assert _git_text(root, "status", "--porcelain") == status_before


def test_dirty_repository_fails_closed_without_repair(tmp_path: Path) -> None:
    root, payload, projection_hash, head = _fixture(tmp_path)
    (root / "untracked.txt").write_text("not committed\n", encoding="utf-8")

    result = _compare(root, payload, projection_hash, head)

    assert result["outcome"] == FAILED_CLOSED
    assert result["failure_reason"] == "REPOSITORY_NOT_CLEAN"
    assert (root / "untracked.txt").read_text(encoding="utf-8") == "not committed\n"


def test_shadow_module_has_no_production_import_or_write_surface() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    import_token = "constitutional_continuation_reference_projection_shadow_v1"
    importers = []
    for path in (repository_root / "aigol").rglob("*.py"):
        relative = path.relative_to(repository_root).as_posix()
        if relative == SOURCE_MODULE:
            continue
        if import_token in path.read_text(encoding="utf-8"):
            importers.append(relative)

    source = (repository_root / SOURCE_MODULE).read_text(encoding="utf-8")
    assert importers == []
    assert "write_text(" not in source
    assert "write_bytes(" not in source
    assert "open(" not in source
    assert "shell=True" not in source
    assert "canonical_serialize" in source
    assert "json.dumps(" not in source
