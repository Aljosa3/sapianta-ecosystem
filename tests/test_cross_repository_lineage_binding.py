import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = ROOT / ".github/governance/lineage/CROSS_REPOSITORY_LINEAGE_BINDING_V1.json"
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
