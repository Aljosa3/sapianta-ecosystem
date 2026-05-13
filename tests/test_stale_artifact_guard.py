from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.stabilization.stale_artifact_guard import inspect_stale_artifacts


def test_stale_artifact_guard_detects_generated_tests_non_destructively(tmp_path: Path) -> None:
    generated = tmp_path / "runtime" / "development" / "generated"
    generated.mkdir(parents=True)
    artifact = generated / "test_generated_module.py"
    artifact.write_text("broken", encoding="utf-8")

    report = inspect_stale_artifacts(tmp_path)

    assert report["stale_artifacts_detected"] is True
    assert "runtime/development/generated/test_generated_module.py" in report["artifacts"]
    assert artifact.exists()
    assert report["requires_human_approval"] is True


def test_stale_artifact_guard_reports_pycache_safe_candidate(tmp_path: Path) -> None:
    pycache = tmp_path / "runtime" / "development" / "generated" / "__pycache__"
    pycache.mkdir(parents=True)
    pyc = pycache / "test_module.cpython-312.pyc"
    pyc.write_bytes(b"cache")

    report = inspect_stale_artifacts(tmp_path)

    assert str(pyc.relative_to(tmp_path)) in report["safe_to_remove"]
    assert pyc.exists()
