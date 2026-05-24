"""Runtime diagnostics command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from agol_bridge.native.native_host_registration import validate_native_host_registration


def runtime_diagnostics(*, extension_id: str = "") -> dict:
    registration = validate_native_host_registration(
        extension_id=extension_id,
        chrome_runtime_launch_attempted=bool(extension_id),
    )
    return {
        "command": "aigol diagnostics runtime",
        "provider_continuity": "BOUNDED_CODEX_CLI_PROVIDER",
        "native_messaging_continuity": "CHROME_NATIVE_MESSAGING",
        "runtime_diagnostics": registration,
        "failure_stage": "" if registration.get("chrome_runtime_launch_allowed") else "CHROME_NATIVE_HOST_LAUNCH_BOUNDARY",
    }


__all__ = ["runtime_diagnostics"]

