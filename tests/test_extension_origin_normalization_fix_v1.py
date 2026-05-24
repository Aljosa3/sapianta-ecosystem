import json
from pathlib import Path

from agol_bridge.native.native_host_registration import (
    NATIVE_HOST_NAME,
    allowed_origin_for_extension,
    generate_native_host_manifest,
    normalize_extension_id,
    validate_extension_id,
    validate_native_host_registration,
)


ROOT = Path(__file__).resolve().parents[1]
REAL_EXTENSION_ID = "lolmjcbfjfoheleiohkjimoeioqagkcc"


def _write_manifest(directory: Path, manifest: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{NATIVE_HOST_NAME}.json"
    path.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return path


def test_valid_extension_id_normalization():
    assert normalize_extension_id(f"  {REAL_EXTENSION_ID.upper()}  ") == REAL_EXTENSION_ID
    assert normalize_extension_id(f"chrome-extension://{REAL_EXTENSION_ID}/") == REAL_EXTENSION_ID
    assert validate_extension_id(REAL_EXTENSION_ID) is True


def test_expected_allowed_origin_generation():
    assert allowed_origin_for_extension(REAL_EXTENSION_ID) == f"chrome-extension://{REAL_EXTENSION_ID}/"
    assert allowed_origin_for_extension(f"chrome-extension://{REAL_EXTENSION_ID}/") == f"chrome-extension://{REAL_EXTENSION_ID}/"


def test_allowed_origins_continuity_matching(tmp_path):
    manifest = generate_native_host_manifest(extension_id=REAL_EXTENSION_ID, repo_root=ROOT)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=REAL_EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["extension_id_valid"] is True
    assert diagnostics["expected_allowed_origin"] == f"chrome-extension://{REAL_EXTENSION_ID}/"
    assert diagnostics["native_host_allowed_origin_match"] is True


def test_invalid_extension_id_rejection():
    diagnostics = validate_native_host_registration(extension_id="invalid-extension-id", repo_root=ROOT)

    assert validate_extension_id("invalid-extension-id") is False
    assert diagnostics["extension_id_valid"] is False
    assert diagnostics["expected_allowed_origin"] == ""
    assert diagnostics["native_host_allowed_origin_match"] is False


def test_empty_extension_id_rejection():
    diagnostics = validate_native_host_registration(extension_id="", repo_root=ROOT)

    assert validate_extension_id("") is False
    assert diagnostics["extension_id_valid"] is False
    assert diagnostics["native_host_extension_id"] == ""
    assert diagnostics["chrome_runtime_launch_allowed"] is False


def test_invalid_origin_mismatch_detection(tmp_path):
    manifest = generate_native_host_manifest(extension_id=REAL_EXTENSION_ID, repo_root=ROOT)
    manifest["allowed_origins"] = ["chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/"]
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=REAL_EXTENSION_ID,
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["native_host_allowed_origin_match"] is False
    assert diagnostics["chrome_runtime_launch_allowed"] is False
    assert diagnostics["chrome_runtime_launch_blocked"] is True


def test_launch_readiness_continuity(tmp_path):
    manifest = generate_native_host_manifest(extension_id=REAL_EXTENSION_ID, repo_root=ROOT)
    manifest_path = _write_manifest(tmp_path, manifest)

    diagnostics = validate_native_host_registration(
        extension_id=f"chrome-extension://{REAL_EXTENSION_ID}/",
        repo_root=ROOT,
        registration_dir=tmp_path,
        manifest_path=manifest_path,
        chrome_runtime_launch_attempted=True,
    )

    assert diagnostics["normalized_extension_id"] == REAL_EXTENSION_ID
    assert diagnostics["extension_id_valid"] is True
    assert diagnostics["native_host_allowed_origin_match"] is True
    assert diagnostics["native_host_registration_valid"] is True
    assert diagnostics["native_host_launch_ready"] is True
    assert diagnostics["chrome_runtime_launch_allowed"] is True
