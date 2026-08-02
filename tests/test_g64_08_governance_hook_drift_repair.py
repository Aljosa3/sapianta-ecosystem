from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess

from runtime.governance.governance_conformance_engine import (
    GovernanceConformanceEngine,
)
from runtime.governance.conformance_models import ConformanceStatus
from test_governance_conformance import create_minimal_conformant_repo


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_installer_copies_exact_canonical_root_and_nested_hooks(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    root_expected = REPOSITORY_ROOT / "scripts/hooks/pre-commit"
    nested_expected = REPOSITORY_ROOT / "sapianta_system/scripts/hooks/pre-commit"
    shutil.copyfile(root_expected, tmp_path / "scripts/hooks/pre-commit")
    shutil.copyfile(
        nested_expected,
        tmp_path / "sapianta_system/scripts/hooks/pre-commit",
    )
    (tmp_path / ".git/hooks/pre-commit").unlink()
    (tmp_path / "sapianta_system/.git/hooks/pre-commit").unlink()

    result = subprocess.run(
        [str(REPOSITORY_ROOT / "scripts/install_governance_hooks.sh"), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".git/hooks/pre-commit").read_bytes() == root_expected.read_bytes()
    assert (
        tmp_path / "sapianta_system/.git/hooks/pre-commit"
    ).read_bytes() == nested_expected.read_bytes()
    assert os.access(tmp_path / ".git/hooks/pre-commit", os.X_OK)
    assert os.access(tmp_path / "sapianta_system/.git/hooks/pre-commit", os.X_OK)
    report = GovernanceConformanceEngine(tmp_path).run()
    assert report.status is ConformanceStatus.CONFORMANT
    assert report.checks_passed == 20
    assert report.checks_failed == 0


def test_installer_fails_closed_when_hook_target_is_unavailable(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    shutil.rmtree(tmp_path / ".git/hooks")

    result = subprocess.run(
        [str(REPOSITORY_ROOT / "scripts/install_governance_hooks.sh"), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "failed closed" in result.stderr


def test_root_hook_fails_closed_before_nested_hook_on_nonconformant_result(
    tmp_path: Path,
) -> None:
    hook = tmp_path / "scripts/hooks/pre-commit"
    hook.parent.mkdir(parents=True)
    shutil.copyfile(REPOSITORY_ROOT / "scripts/hooks/pre-commit", hook)
    _executable(hook)
    nested = tmp_path / "sapianta_system/scripts/hooks/pre-commit"
    nested.parent.mkdir(parents=True)
    marker = tmp_path / "nested-invoked"
    nested.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    _executable(nested)
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python3"
    fake_python.write_text(
        "#!/bin/sh\nprintf '%s\\n' '{\"status\": \"PARTIALLY_CONFORMANT\"}'\nexit 0\n",
        encoding="utf-8",
    )
    _executable(fake_python)
    environment = dict(os.environ)
    environment["PATH"] = f"{fake_bin}:/usr/bin:/bin"

    result = subprocess.run(
        [str(hook)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "not conformant" in result.stderr
    assert not marker.exists()
    hook_text = hook.read_text(encoding="utf-8")
    assert "promotion_gate_v02" in hook_text
    assert "check_layer_freeze" in hook_text
