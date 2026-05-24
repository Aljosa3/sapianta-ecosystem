import json
import os
import stat
from pathlib import Path

from agol_bridge.native.native_host_registration import (
    NATIVE_HOST_NAME,
    allowed_origin_for_extension,
    generate_native_host_manifest,
    linux_native_host_registration_dir,
    manifest_to_canonical_json,
    native_host_executable_path,
    native_host_manifest_path,
    validate_native_host_registration,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"
EXTENSION_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _write_manifest(directory: Path, manifest: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{NATIVE_HOST_NAME}.json"
    path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return path


def test_manifest_json_generated_correctly():
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)

    assert manifest["name"] == NATIVE_HOST_NAME
    assert manifest["description"] == "SAPIANTA AiGOL local native messaging bridge"
    assert manifest["path"] == str(HOST)
    assert manifest["type"] == "stdio"
    assert manifest["allowed_origins"] == [f"chrome-extension://{EXTENSION_ID}/"]
    assert manifest_to_canonical_json(manifest).startswith('{"allowed_origins"')


def test_allowed_origins_contains_extension_id():
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)

    assert allowed_origin_for_extension(EXTENSION_ID) in manifest["allowed_origins"]


def test_manifest_path_deterministic(tmp_path):
    registration_dir = tmp_path / "NativeMessagingHosts"

    first = native_host_manifest_path(registration_dir=registration_dir)
    second = native_host_manifest_path(registration_dir=registration_dir)

    assert first == second
    assert first == registration_dir.resolve() / f"{NATIVE_HOST_NAME}.json"


def test_executable_path_deterministic():
    assert native_host_executable_path(ROOT) == HOST
    assert native_host_executable_path(ROOT) == native_host_executable_path(ROOT)


def test_executable_permission_validation_works(tmp_path):
    host = tmp_path / "native_messaging_host.py"
    host.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    os.chmod(host, stat.S_IRUSR | stat.S_IWUSR)
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(host)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
    )

    assert diagnostics["native_host_executable_found"] is True
    assert diagnostics["native_host_executable_executable"] is False
    assert diagnostics["native_host_registration_valid"] is False
    assert diagnostics["native_host_launch_ready"] is False


def test_registration_validation_detects_missing_manifest(tmp_path):
    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
    )

    assert diagnostics["native_host_manifest_found"] is False
    assert diagnostics["native_host_registration_valid"] is False
    assert diagnostics["native_host_launch_ready"] is False
    assert diagnostics["fail_closed"] is True


def test_registration_validation_detects_invalid_allowed_origins(tmp_path):
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["allowed_origins"] = ["chrome-extension://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/"]
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
    )

    assert diagnostics["native_host_allowed_origin_match"] is False
    assert diagnostics["native_host_registration_valid"] is False


def test_registration_validation_detects_invalid_executable_path(tmp_path):
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(tmp_path / "missing_native_host.py")
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
    )

    assert diagnostics["native_host_executable_found"] is False
    assert diagnostics["native_host_registration_valid"] is False


def test_registration_validation_detects_non_executable_host(tmp_path):
    host = tmp_path / "host.py"
    host.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    os.chmod(host, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest["path"] = str(host)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
    )

    assert diagnostics["native_host_executable_found"] is True
    assert diagnostics["native_host_executable_executable"] is False
    assert diagnostics["native_host_launch_ready"] is False


def test_valid_registration_reaches_native_host_launch_ready(tmp_path):
    manifest = generate_native_host_manifest(extension_id=EXTENSION_ID, repo_root=ROOT)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
    )

    assert HOST.is_file()
    assert os.access(HOST, os.X_OK)
    assert diagnostics["native_host_manifest_found"] is True
    assert diagnostics["native_host_executable_found"] is True
    assert diagnostics["native_host_executable_executable"] is True
    assert diagnostics["native_host_allowed_origin_match"] is True
    assert diagnostics["native_host_registration_valid"] is True
    assert diagnostics["native_host_launch_ready"] is True


def test_diagnostics_preserve_registration_state(tmp_path):
    registration_dir = tmp_path / "NativeMessagingHosts"
    diagnostics = validate_native_host_registration(
        extension_id=EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=registration_dir,
    )

    assert diagnostics["native_host_manifest_path"] == str(registration_dir.resolve() / f"{NATIVE_HOST_NAME}.json")
    assert diagnostics["native_host_registration_directory"] == str(registration_dir.resolve())
    assert diagnostics["expected_allowed_origin"] == f"chrome-extension://{EXTENSION_ID}/"
    assert diagnostics["generated_manifest_preview"]["name"] == NATIVE_HOST_NAME


def test_service_worker_diagnostics_preserve_host_registration_failures():
    source = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "nativeHostRegistrationDiagnostics" in source
    assert "native_host_manifest_found" in source
    assert "native_host_manifest_path" in source
    assert "native_host_executable_found" in source
    assert "native_host_executable_executable" in source
    assert "native_host_allowed_origin_match" in source
    assert "native_host_registration_valid" in source
    assert "native_host_launch_ready" in source
    assert "NATIVE_HOST_NOT_FOUND" in source


def test_fail_closed_behavior_preserved(tmp_path):
    diagnostics = validate_native_host_registration(
        extension_id="invalid-extension-id",
        repo_root=ROOT,
        registration_dir=tmp_path,
    )

    assert diagnostics["extension_id_valid"] is False
    assert diagnostics["native_host_registration_valid"] is False
    assert diagnostics["native_host_launch_ready"] is False
    assert diagnostics["fail_closed"] is True


def test_no_provider_bypass_introduced():
    source = (ROOT / "agol_bridge" / "native" / "native_host_registration.py").read_text(encoding="utf-8")

    assert "subprocess" not in source
    assert "codex" not in source.lower()
    assert "sendNativeMessage" not in source


def test_no_orchestration_introduced():
    source = (ROOT / "agol_bridge" / "native" / "native_host_registration.py").read_text(encoding="utf-8").lower()
    service_worker = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "retry" not in source
    assert "orchestrat" not in source
    assert "setInterval" not in service_worker
    assert "worker routing" not in source


def test_linux_registration_directory_model_is_deterministic(tmp_path):
    expected = tmp_path / ".config" / "google-chrome" / "NativeMessagingHosts"

    assert linux_native_host_registration_dir(home=tmp_path) == expected.resolve()
