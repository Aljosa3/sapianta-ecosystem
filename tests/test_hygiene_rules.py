from sapianta_bridge.hygiene.artifact_classifier import (
    CANONICAL_GOVERNANCE_ARTIFACT,
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
)
from sapianta_bridge.hygiene.hygiene_rules import (
    class_allowed_in_governance_lineage,
    hygiene_policy,
    validate_gitignore_text,
)


def test_hygiene_policy_blocks_transient_and_unknown_classes() -> None:
    policy = hygiene_policy()

    assert policy["allowed_artifact_classes"] == [CANONICAL_GOVERNANCE_ARTIFACT]
    assert TRANSIENT_RUNTIME_ARTIFACT in policy["forbidden_artifact_classes"]
    assert UNKNOWN_ARTIFACT in policy["forbidden_artifact_classes"]
    assert policy["automatic_deletion_allowed"] is False
    assert policy["history_rewrite_allowed"] is False


def test_gitignore_policy_requires_cache_patterns() -> None:
    result = validate_gitignore_text("__pycache__/\n*.pyc\n.pytest_cache/\n*.pyo\n")

    assert result["valid"] is True
    assert result["missing_patterns"] == []


def test_gitignore_policy_reports_missing_patterns() -> None:
    result = validate_gitignore_text("*.pyc\n")

    assert result["valid"] is False
    assert result["missing_patterns"] == ["__pycache__/", ".pytest_cache/", "*.pyo"]


def test_only_canonical_class_allowed_in_governance_lineage() -> None:
    assert class_allowed_in_governance_lineage(CANONICAL_GOVERNANCE_ARTIFACT) is True
    assert class_allowed_in_governance_lineage(TRANSIENT_RUNTIME_ARTIFACT) is False
    assert class_allowed_in_governance_lineage(UNKNOWN_ARTIFACT) is False
