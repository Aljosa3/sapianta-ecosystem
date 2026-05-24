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
from pathlib import Path
from typing import Any

NATIVE_HOST_NAME = "com.sapianta.aigol_bridge"
NATIVE_HOST_DESCRIPTION = "SAPIANTA AiGOL local native messaging bridge"
NATIVE_HOST_TYPE = "stdio"
DEFAULT_CHROME_VARIANT = "google-chrome"
_EXTENSION_ID_PATTERN = re.compile(r"^[a-p]{32}$")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def validate_extension_id(extension_id: str) -> bool:
    return bool(_EXTENSION_ID_PATTERN.fullmatch(str(extension_id or "")))


def allowed_origin_for_extension(extension_id: str) -> str:
    if not validate_extension_id(extension_id):
        raise ValueError("extension_id must be a 32-character Chrome extension id using letters a-p")
    return f"chrome-extension://{extension_id}/"


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


def validate_native_host_registration(
    *,
    extension_id: str,
    repo_root: str | Path | None = None,
    registration_dir: str | Path | None = None,
    manifest_path: str | Path | None = None,
    host_name: str = NATIVE_HOST_NAME,
) -> dict[str, Any]:
    errors: list[str] = []
    extension_id_valid = validate_extension_id(extension_id)
    expected_origin = ""
    if extension_id_valid:
        expected_origin = allowed_origin_for_extension(extension_id)
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

    manifest_found = resolved_manifest_path.is_file()
    manifest_readable = False
    manifest: dict[str, Any] = {}
    if manifest_found:
        try:
            loaded = json.loads(resolved_manifest_path.read_text(encoding="utf-8"))
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
    executable_executable = executable_found and os.access(executable_path, os.X_OK)
    if manifest_readable and not executable_found:
        errors.append("native host executable missing")
    if manifest_readable and executable_found and not executable_executable:
        errors.append("native host executable is not executable")

    registration_valid = bool(
        extension_id_valid
        and manifest_found
        and manifest_readable
        and manifest_name_match
        and manifest_type_match
        and allowed_origin_match
        and executable_found
        and executable_executable
    )

    try:
        manifest_preview = generate_native_host_manifest(extension_id=extension_id, repo_root=repo_root, host_name=host_name)
    except ValueError:
        manifest_preview = {}

    return {
        "native_host_name": host_name,
        "extension_id": extension_id,
        "extension_id_valid": extension_id_valid,
        "expected_allowed_origin": expected_origin,
        "native_host_manifest_found": manifest_found,
        "native_host_manifest_path": str(resolved_manifest_path),
        "native_host_manifest_readable": manifest_readable,
        "native_host_manifest_name_match": manifest_name_match,
        "native_host_manifest_type_match": manifest_type_match,
        "native_host_allowed_origin_match": allowed_origin_match,
        "native_host_executable_path": str(executable_path),
        "native_host_executable_found": executable_found,
        "native_host_executable_executable": executable_executable,
        "native_host_registration_directory": str(resolved_registration_dir),
        "native_host_registration_directory_found": resolved_registration_dir.is_dir(),
        "native_host_registration_valid": registration_valid,
        "native_host_launch_ready": registration_valid,
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
    "repository_root",
    "validate_extension_id",
    "validate_native_host_registration",
]
