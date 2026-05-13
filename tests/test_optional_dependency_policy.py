from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.stabilization.optional_dependency_policy import (
    optional_dependency_action,
    optional_dependency_manifest,
)


def test_optional_dependency_policy_is_explicit() -> None:
    action = optional_dependency_action("numpy")

    assert action["known_optional"] is True
    assert action["broad_skip_allowed"] is False


def test_unknown_dependency_requires_review() -> None:
    action = optional_dependency_action("unknown_runtime")

    assert action["known_optional"] is False
    assert action["allowed_handling"] == "manual review required"


def test_manifest_does_not_make_core_governance_optional() -> None:
    manifest = optional_dependency_manifest()

    assert manifest["core_governance_tests_optional"] is False
    assert manifest["broad_skip_strategy_allowed"] is False
