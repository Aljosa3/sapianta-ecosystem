from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.stabilization.collection_audit import (
    blockers_from_pytest_output,
    build_collection_audit,
    classify_blocker,
)


def test_classifies_optional_dependency() -> None:
    blocker = classify_blocker(
        "sapianta_system/tests/runtime/test_replay_engine.py",
        "ModuleNotFoundError",
        "No module named 'numpy'",
    )

    assert blocker.classification == "OPTIONAL_DEPENDENCY"


def test_classifies_stale_generated_artifact() -> None:
    blocker = classify_blocker(
        "runtime/development/generated/test_llm_module.py",
        "NameError",
        "name 'asdasdasd' is not defined",
    )

    assert blocker.classification == "STALE_GENERATED_ARTIFACT"


def test_build_collection_audit_is_deterministic() -> None:
    output = """
_ ERROR collecting runtime/development/generated/test_llm_module.py _
E   NameError: name 'asdasdasd' is not defined
_ ERROR collecting sapianta_system/tests/runtime/test_replay_engine.py _
E   ModuleNotFoundError: No module named 'numpy'
"""

    first = build_collection_audit(False, output)
    second = build_collection_audit(False, output)

    assert first == second
    assert first["collection_status"] == "FAILED"
    assert first["total_blockers"] == 2


def test_blockers_from_pytest_output_extracts_errors() -> None:
    output = """
_ ERROR collecting tests/test_example.py _
E   ImportError: attempted relative import with no known parent package
"""

    blockers = blockers_from_pytest_output(output)

    assert len(blockers) == 1
    assert blockers[0].classification == "IMPORT_TOPOLOGY"
