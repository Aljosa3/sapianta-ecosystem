import json
import os
import stat
from pathlib import Path

from agol_bridge.native.native_host_registration import (
    NATIVE_HOST_NAME,
    generate_native_host_manifest,
    validate_native_host_registration,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"
SIDEPANEL = ROOT / "browser_companion" / "sidepanel.js"
EXTENSION_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _write_manifest(directory: Path, manifest: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{NATIVE_HOST_NAME}.json"
    path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return path


def _write_host(path: Path, shebang: str = "#!/usr/bin/env python3", executable: bool = True) -> Path:
    path.write_text(f"{shebang}\nprint('native host fixture')\n", encoding="utf-8")
    mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    if executable:
        mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(path, mode)
    return path


def _valid_manifest(tmp_path: Path) -> tuple[Path, dict]:
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    return _write_manifest(tmp_path, manifest), manifest


def test_valid_manifest_continuity(tmp_path):
    manifest_path, _ = _valid_manifest(tmp_path)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_manifest_exists"] is True
    assert diagnostics["native_host_manifest_readable"] is True
    assert diagnostics["native_host_manifest_json_valid"] is True
    assert diagnostics["native_host_allowed_origin_match"] is True
    assert diagnostics["chrome_runtime_launch_allowed"] is True
    assert diagnostics["chrome_runtime_launch_blocked"] is False


def test_invalid_manifest_path(tmp_path):
    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=tmp_path / "missing.json",
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_manifest_exists"] is False
    assert diagnostics["chrome_runtime_launch_allowed"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True
    assert "native host manifest missing" in diagnostics["chrome_runtime_launch_failure_reason"]


def test_invalid_allowed_origins(tmp_path):
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["allowed_origins"] = ["chrome-extension://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/"]
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_allowed_origin_match"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True
    assert "allowed_origins" in diagnostics["chrome_runtime_launch_failure_reason"]


def test_invalid_extension_id(tmp_path):
    manifest_path, _ = _valid_manifest(tmp_path)

    diagnostics = validate_native_host_registration(
        extension_id="invalid-extension",
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["extension_id_valid"] is False
    assert diagnostics["native_host_extension_id"] == "invalid-extension"
    assert diagnostics["chrome_runtime_launch_allowed"] is False


def test_invalid_executable_permissions(tmp_path):
    host = _write_host(tmp_path / "host.py", executable=False)
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(host)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_executable_exists"] is True
    assert diagnostics["native_host_executable_readable"] is True
    assert diagnostics["native_host_executable_executable"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True


def test_invalid_shebang(tmp_path):
    host = _write_host(tmp_path / "host.py", shebang="#!/bin/sh", executable=True)
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(host)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_shebang_valid"] is False
    assert diagnostics["native_host_python_runtime_found"] is False
    assert diagnostics["chrome_runtime_launch_allowed"] is False


def test_missing_python_runtime(tmp_path):
    host = _write_host(tmp_path / "host.py", shebang="#!/usr/bin/env python-not-real-aigol", executable=True)
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(host)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_shebang_valid"] is True
    assert diagnostics["native_host_python_runtime_found"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True


def test_chrome_launch_blocked(tmp_path):
    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["chrome_runtime_launch_attempted"] is True
    assert diagnostics["chrome_runtime_launch_allowed"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True
    assert diagnostics["chrome_runtime_launch_failure_reason"]


def test_chrome_launch_allowed(tmp_path):
    manifest_path, _ = _valid_manifest(tmp_path)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_launch_ready"] is True
    assert diagnostics["chrome_runtime_launch_allowed"] is True
    assert diagnostics["chrome_runtime_launch_failure_reason"] == ""


def test_manifest_permission_and_profile_diagnostics(tmp_path):
    profile = tmp_path / "google-chrome"
    registration_dir = profile / "NativeMessagingHosts"
    manifest_path, _ = _valid_manifest(registration_dir)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=registration_dir,
        manifest_path=manifest_path,
        chrome_profile_path=profile,
    )

    assert diagnostics["native_host_manifest_permissions"].startswith("0o")
    assert diagnostics["native_host_profile_path"] == str(profile.resolve())
    assert diagnostics["chrome_profile_detected"] is True


def test_service_worker_classifies_forbidden_launch_boundary():
    source = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "NATIVE_HOST_FORBIDDEN" in source
    assert "access to the specified native messaging host is forbidden" in source
    assert "chrome_runtime_launch_blocked" in source
    assert "chrome_runtime_launch_failure_reason" in source


def test_cockpit_renders_permission_continuity_diagnostics():
    source = SIDEPANEL.read_text(encoding="utf-8")

    assert "native_host_manifest_exists:" in source
    assert "native_host_manifest_readable:" in source
    assert "native_host_manifest_json_valid:" in source
    assert "native_host_executable_exists:" in source
    assert "native_host_executable_readable:" in source
    assert "native_host_executable_executable:" in source
    assert "native_host_shebang_valid:" in source
    assert "native_host_python_runtime_found:" in source
    assert "native_host_allowed_origin_match:" in source
    assert "chrome_runtime_launch_blocked:" in source


def test_no_execution_bypass_or_topology_expansion():
    registration_source = (ROOT / "agol_bridge" / "native" / "native_host_registration.py").read_text(encoding="utf-8").lower()

    assert "subprocess" not in registration_source
    assert "sendnativemessage" not in registration_source
    assert "codex" not in registration_source
    assert "retry" not in registration_source
    assert "fallback" not in registration_source
    assert "orchestrat" not in registration_source
    assert HOST.is_file()
