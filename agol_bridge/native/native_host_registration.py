"""Deterministic Chrome Native Messaging host registration helpers.

These helpers generate and validate the local workstation registration state
for the AiGOL Native Messaging host. They do not install the host, mutate
system directories, invoke providers, or bypass Chrome's Native Messaging
security model.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
from pathlib import Path
from typing import Any

NATIVE_HOST_NAME = "com.sapianta.aigol_bridge"
NATIVE_HOST_DESCRIPTION = "SAPIANTA AiGOL local native messaging bridge"
NATIVE_HOST_TYPE = "stdio"
DEFAULT_CHROME_VARIANT = "google-chrome"
_EXTENSION_ID_PATTERN = re.compile(r"^[a-z]{32}$")
_CHROME_EXTENSION_ORIGIN_PREFIX = "chrome-extension://"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_extension_id(extension_id: str) -> str:
    value = str(extension_id or "").strip().lower()
    if value.startswith(_CHROME_EXTENSION_ORIGIN_PREFIX):
        value = value[len(_CHROME_EXTENSION_ORIGIN_PREFIX) :]
    return value.rstrip("/")


def validate_extension_id(extension_id: str) -> bool:
    return bool(_EXTENSION_ID_PATTERN.fullmatch(normalize_extension_id(extension_id)))


def allowed_origin_for_extension(extension_id: str) -> str:
    normalized_extension_id = normalize_extension_id(extension_id)
    if not validate_extension_id(normalized_extension_id):
        raise ValueError("extension_id must normalize to a 32-character Chrome extension id using lowercase letters")
    return f"chrome-extension://{normalized_extension_id}/"


def native_host_executable_path(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root).expanduser().resolve() if repo_root is not None else repository_root()
    return root / "agol_bridge" / "native" / "native_messaging_host.py"


def linux_native_host_registration_dir(
    *,
    chrome_variant: str = DEFAULT_CHROME_VARIANT,
    home: str | Path | None = None,
) -> Path:
    base_home = Path(home).expanduser().resolve() if home is not None else Path.home()
    variant_paths = {
        "google-chrome": base_home / ".config" / "google-chrome" / "NativeMessagingHosts",
        "chrome": base_home / ".config" / "google-chrome" / "NativeMessagingHosts",
        "chromium": base_home / ".config" / "chromium" / "NativeMessagingHosts",
    }
    if chrome_variant not in variant_paths:
        raise ValueError("chrome_variant must be one of: google-chrome, chrome, chromium")
    return variant_paths[chrome_variant]


def native_host_manifest_path(
    *,
    registration_dir: str | Path | None = None,
    host_name: str = NATIVE_HOST_NAME,
    chrome_variant: str = DEFAULT_CHROME_VARIANT,
    home: str | Path | None = None,
) -> Path:
    directory = (
        Path(registration_dir).expanduser().resolve()
        if registration_dir is not None
        else linux_native_host_registration_dir(chrome_variant=chrome_variant, home=home)
    )
    return directory / f"{host_name}.json"


def generate_native_host_manifest(
    *,
    extension_id: str,
    repo_root: str | Path | None = None,
    host_name: str = NATIVE_HOST_NAME,
    description: str = NATIVE_HOST_DESCRIPTION,
) -> dict[str, Any]:
    return {
        "name": host_name,
        "description": description,
        "path": str(native_host_executable_path(repo_root)),
        "type": NATIVE_HOST_TYPE,
        "allowed_origins": [allowed_origin_for_extension(extension_id)],
    }


def manifest_to_canonical_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"))


def _file_mode(path: Path) -> str:
    try:
        return oct(stat.S_IMODE(path.stat().st_mode))
    except OSError:
        return ""


def _file_owner(path: Path) -> dict[str, int | str]:
    try:
        stat_result = path.stat()
        return {"uid": stat_result.st_uid, "gid": stat_result.st_gid}
    except OSError:
        return {"uid": "", "gid": ""}


def _shebang_diagnostics(path: Path) -> dict[str, Any]:
    try:
        first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except (OSError, IndexError):
        first_line = ""
    shebang_valid = first_line.startswith("#!") and "python" in first_line.lower()
    runtime_found = False
    if shebang_valid:
        parts = first_line[2:].strip().split()
        if parts[:1] == ["/usr/bin/env"] and len(parts) > 1:
            runtime_found = shutil.which(parts[1]) is not None
        elif parts:
            runtime_found = Path(parts[0]).is_file()
    return {
        "native_host_shebang": first_line,
        "native_host_shebang_valid": shebang_valid,
        "native_host_python_runtime_found": runtime_found,
    }


def validate_native_host_registration(
    *,
    extension_id: str,
    repo_root: str | Path | None = None,
    registration_dir: str | Path | None = None,
    manifest_path: str | Path | None = None,
    chrome_profile_path: str | Path | None = None,
    chrome_runtime_launch_attempted: bool = False,
    host_name: str = NATIVE_HOST_NAME,
) -> dict[str, Any]:
    errors: list[str] = []
    normalized_extension_id = normalize_extension_id(extension_id)
    extension_id_valid = validate_extension_id(normalized_extension_id)
    expected_origin = ""
    if extension_id_valid:
        expected_origin = allowed_origin_for_extension(normalized_extension_id)
    else:
        errors.append("invalid extension id")

    resolved_registration_dir = (
        Path(registration_dir).expanduser().resolve()
        if registration_dir is not None
        else linux_native_host_registration_dir()
    )
    resolved_manifest_path = (
        Path(manifest_path).expanduser().resolve()
        if manifest_path is not None
        else native_host_manifest_path(registration_dir=resolved_registration_dir, host_name=host_name)
    )

    resolved_chrome_profile_path = (
        Path(chrome_profile_path).expanduser().resolve()
        if chrome_profile_path is not None
        else resolved_registration_dir.parent
    )
    chrome_profile_detected = resolved_chrome_profile_path.is_dir()
    manifest_found = resolved_manifest_path.is_file()
    manifest_readable_permission = manifest_found and os.access(resolved_manifest_path, os.R_OK)
    manifest_json_valid = False
    manifest_readable = False
    manifest: dict[str, Any] = {}
    if manifest_found:
        try:
            loaded = json.loads(resolved_manifest_path.read_text(encoding="utf-8"))
            manifest_json_valid = True
            if isinstance(loaded, dict):
                manifest = loaded
                manifest_readable = True
            else:
                errors.append("manifest is not a JSON object")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"manifest unreadable: {type(exc).__name__}")
    else:
        errors.append("native host manifest missing")

    manifest_name_match = manifest.get("name") == host_name
    manifest_type_match = manifest.get("type") == NATIVE_HOST_TYPE
    if manifest_readable and not manifest_name_match:
        errors.append("manifest name mismatch")
    if manifest_readable and not manifest_type_match:
        errors.append("manifest type must be stdio")

    allowed_origins = manifest.get("allowed_origins") if manifest_readable else []
    allowed_origin_match = bool(
        isinstance(allowed_origins, list)
        and expected_origin
        and expected_origin in allowed_origins
    )
    if manifest_readable and not allowed_origin_match:
        errors.append("allowed_origins does not include expected extension origin")

    manifest_executable_path = manifest.get("path") if manifest_readable else ""
    executable_path = (
        Path(manifest_executable_path).expanduser()
        if isinstance(manifest_executable_path, str) and manifest_executable_path.strip()
        else native_host_executable_path(repo_root)
    )
    try:
        executable_path = executable_path.resolve()
    except OSError:
        pass
    executable_found = executable_path.is_file()
    executable_readable = executable_found and os.access(executable_path, os.R_OK)
    executable_executable = executable_found and os.access(executable_path, os.X_OK)
    shebang = _shebang_diagnostics(executable_path) if executable_found else {
        "native_host_shebang": "",
        "native_host_shebang_valid": False,
        "native_host_python_runtime_found": False,
    }
    if manifest_readable and not executable_found:
        errors.append("native host executable missing")
    if manifest_readable and executable_found and not executable_executable:
        errors.append("native host executable is not executable")
    if manifest_readable and executable_found and not shebang["native_host_shebang_valid"]:
        errors.append("native host shebang is invalid")
    if manifest_readable and executable_found and shebang["native_host_shebang_valid"] and not shebang["native_host_python_runtime_found"]:
        errors.append("native host Python runtime was not found")

    registration_valid = bool(
        extension_id_valid
        and manifest_found
        and manifest_readable
        and manifest_json_valid
        and manifest_name_match
        and manifest_type_match
        and allowed_origin_match
        and executable_found
        and executable_readable
        and executable_executable
        and shebang["native_host_shebang_valid"]
        and shebang["native_host_python_runtime_found"]
    )
    chrome_runtime_launch_allowed = registration_valid
    chrome_runtime_launch_blocked = bool(chrome_runtime_launch_attempted and not chrome_runtime_launch_allowed)
    chrome_runtime_launch_failure_reason = "; ".join(errors) if chrome_runtime_launch_blocked else ""

    try:
        manifest_preview = generate_native_host_manifest(extension_id=extension_id, repo_root=repo_root, host_name=host_name)
    except ValueError:
        manifest_preview = {}

    return {
        "native_host_name": host_name,
        "extension_id": extension_id,
        "normalized_extension_id": normalized_extension_id,
        "extension_id_valid": extension_id_valid,
        "native_host_extension_id": normalized_extension_id,
        "expected_allowed_origin": expected_origin,
        "native_host_manifest_exists": manifest_found,
        "native_host_manifest_found": manifest_found,
        "native_host_manifest_path": str(resolved_manifest_path),
        "native_host_manifest_permissions": _file_mode(resolved_manifest_path),
        "native_host_manifest_readable_permission": manifest_readable_permission,
        "native_host_manifest_readable": manifest_readable,
        "native_host_manifest_json_valid": manifest_json_valid,
        "native_host_manifest_name_match": manifest_name_match,
        "native_host_manifest_type_match": manifest_type_match,
        "native_host_allowed_origins": allowed_origins if isinstance(allowed_origins, list) else [],
        "native_host_allowed_origin_match": allowed_origin_match,
        "native_host_executable_path": str(executable_path),
        "native_host_executable_exists": executable_found,
        "native_host_executable_found": executable_found,
        "native_host_executable_readable": executable_readable,
        "native_host_executable_executable": executable_executable,
        "native_host_executable_permissions": _file_mode(executable_path),
        "native_host_executable_owner": _file_owner(executable_path),
        **shebang,
        "native_host_profile_path": str(resolved_chrome_profile_path),
        "chrome_profile_detected": chrome_profile_detected,
        "native_host_registration_directory": str(resolved_registration_dir),
        "native_host_registration_directory_found": resolved_registration_dir.is_dir(),
        "native_host_registration_valid": registration_valid,
        "native_host_launch_ready": registration_valid,
        "chrome_runtime_launch_allowed": chrome_runtime_launch_allowed,
        "chrome_runtime_launch_attempted": chrome_runtime_launch_attempted,
        "chrome_runtime_launch_blocked": chrome_runtime_launch_blocked,
        "chrome_runtime_launch_failure_reason": chrome_runtime_launch_failure_reason,
        "generated_manifest_preview": manifest_preview,
        "errors": errors,
        "fail_closed": not registration_valid,
    }


__all__ = [
    "DEFAULT_CHROME_VARIANT",
    "NATIVE_HOST_DESCRIPTION",
    "NATIVE_HOST_NAME",
    "NATIVE_HOST_TYPE",
    "allowed_origin_for_extension",
    "generate_native_host_manifest",
    "linux_native_host_registration_dir",
    "manifest_to_canonical_json",
    "native_host_executable_path",
    "native_host_manifest_path",
    "normalize_extension_id",
    "repository_root",
    "validate_extension_id",
    "validate_native_host_registration",
]
