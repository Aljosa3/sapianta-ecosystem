from sapianta_bridge.hygiene.artifact_classifier import (
    CANONICAL_GOVERNANCE_ARTIFACT,
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
    classify_artifact,
    classify_artifacts,
)


def test_classifies_governance_adr_as_canonical() -> None:
    result = classify_artifact(".github/governance/adr/ADR_GOVERNANCE_WORKTREE_HYGIENE_V1.md")

    assert result["classification"] == CANONICAL_GOVERNANCE_ARTIFACT
    assert result["allowed_in_governance_lineage"] is True


def test_classifies_pyc_as_transient_runtime_artifact() -> None:
    result = classify_artifact("sapianta_bridge/architecture/__pycache__/layer_model.pyc")

    assert result["classification"] == TRANSIENT_RUNTIME_ARTIFACT
    assert result["allowed_in_governance_lineage"] is False


def test_classifies_pycache_directory_artifact_as_transient() -> None:
    result = classify_artifact("tests/__pycache__/test_layer_model.cpython-312.pyc")

    assert result["classification"] == TRANSIENT_RUNTIME_ARTIFACT


def test_unknown_artifact_fails_closed() -> None:
    result = classify_artifact("notes/random-local-output.bin")

    assert result["classification"] == UNKNOWN_ARTIFACT
    assert result["allowed_in_governance_lineage"] is False


def test_classification_order_is_deterministic() -> None:
    first = classify_artifacts(["z.pyc", ".github/governance/evidence/REPORT.md"])
    second = classify_artifacts([".github/governance/evidence/REPORT.md", "z.pyc"])

    assert first == second
