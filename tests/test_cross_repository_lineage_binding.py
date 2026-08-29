import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = ROOT / ".github/governance/lineage/CROSS_REPOSITORY_LINEAGE_BINDING_V1.json"
CURRENT_BINDING_PATH = ROOT / ".github/governance/lineage/CROSS_REPOSITORY_LINEAGE_BINDING_V2.json"
LINEAGE_PATHS = (
    BINDING_PATH,
    ROOT / "runtime/lineage_evidence/CROSS_REPOSITORY_LINEAGE_BINDING_V1.json",
    ROOT / "runtime/lineage_evidence/CROSS_REPOSITORY_RUNTIME_IMPLEMENTATION_BINDING.json",
    ROOT / "runtime/lineage_evidence/CROSS_REPOSITORY_REPLAY_CERTIFICATION_BINDING.json",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def test_binding_json_artifacts_parse():
    assert all(_load(path) for path in LINEAGE_PATHS)


def test_binding_contains_required_repository_identity():
    payload = _load(BINDING_PATH)["canonical_payload"]
    assert payload["outer_repository"]["commit"]
    assert payload["outer_repository"]["branch"]
    assert payload["inner_repository"]["commit"]
    assert payload["inner_repository"]["repo_path"] == "sapianta_system"


def test_binding_hash_recomputes_deterministically():
    binding = _load(BINDING_PATH)
    payload = binding["canonical_payload"]
    pairing = binding["deterministic_pairing"]
    assert _hash(payload) == pairing["canonical_json_sha256"]
    expected_id = f"CROSS-REPOSITORY-LINEAGE-BINDING-{pairing['canonical_json_sha256'][:24]}"
    assert pairing["binding_id"] == expected_id
    material = {
        "binding_id": pairing["binding_id"],
        "outer_commit": pairing["outer_commit"],
        "inner_commit": pairing["inner_commit"],
        "canonical_json_sha256": pairing["canonical_json_sha256"],
    }
    assert _hash(material) == pairing["binding_hash"]


def test_binding_is_replay_safe_and_non_authorizing():
    binding = _load(BINDING_PATH)
    boundaries = binding["canonical_payload"]["mutation_boundaries"]
    assert binding["replay_safe"] is True
    assert boundaries == {
        "authorizes_execution": False,
        "changes_execution_behavior": False,
        "creates_runtime_authority": False,
        "read_only_after_creation": True,
    }


def test_binding_excludes_prohibited_capabilities():
    text = BINDING_PATH.read_text()
    prohibited = (
        '"shell_true": true',
        '"authorizes_execution": true',
        '"creates_runtime_authority": true',
        '"autonomous_execution": true',
        '"live_transport": true',
        '"orchestration": true',
    )
    assert not any(value in text for value in prohibited)


def test_current_binding_pins_ratified_nested_authority() -> None:
    binding = _load(CURRENT_BINDING_PATH)
    payload = binding["canonical_payload"]
    root = payload["root_repository"]
    nested = payload["nested_repository"]
    assert root["commit"] == "2fb0b645fd883faf53a08ab07c0311906fc4d4f2"
    assert root["tree"] == "bd32263838a11bc7143b1b5cb77da5c4afc94629"
    assert nested == {
        "checkout_policy": "DETACHED_EXACT_COMMIT_AND_TREE",
        "commit": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "immutable_acquisition_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1",
        "repo_path": "sapianta_system",
        "source": "git@github.com:Aljosa3/sapianta-core.git",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
    }
    assert payload["pinning_policy"] == (
        "PIN_EXACT_COMMIT_AND_TREE_DO_NOT_AUTOMATICALLY_ADVANCE_WITH_ANY_BRANCH"
    )
    assert all(
        value == "FAIL_CLOSED"
        for key, value in payload["mismatch_semantics"].items()
        if key.endswith("_mismatch")
    )
    assert payload["mismatch_semantics"]["automatic_branch_advancement"] is False


def test_current_binding_hash_recomputes_deterministically() -> None:
    binding = _load(CURRENT_BINDING_PATH)
    payload = binding["canonical_payload"]
    pairing = binding["deterministic_pairing"]
    assert _hash(payload) == pairing["canonical_json_sha256"]
    expected_id = f"CROSS-REPOSITORY-LINEAGE-BINDING-{pairing['canonical_json_sha256'][:24]}"
    assert pairing["binding_id"] == expected_id
    material = {
        "binding_id": pairing["binding_id"],
        "root_commit": pairing["root_commit"],
        "root_tree": pairing["root_tree"],
        "nested_commit": pairing["nested_commit"],
        "nested_tree": pairing["nested_tree"],
        "canonical_json_sha256": pairing["canonical_json_sha256"],
    }
    assert _hash(material) == pairing["binding_hash"]


def test_current_binding_is_non_authorizing_and_preserves_v1() -> None:
    payload = _load(CURRENT_BINDING_PATH)["canonical_payload"]
    assert payload["historical_binding"] == {
        "path": ".github/governance/lineage/CROSS_REPOSITORY_LINEAGE_BINDING_V1.json",
        "preserved_as_historical_evidence": True,
    }
    assert all(value is False for value in payload["mutation_boundaries"].values() if value is not True)
    assert payload["mutation_boundaries"]["read_only_after_creation"] is True
