"""Safe Codex CLI introspection probes."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

from .codex_contract_model import CodexCliContract


DISCOVERY_NAME = "CODEX_CLI_CONTRACT_DISCOVERY_V1"
SAFE_PROBES = (
    ("--help",),
    ("-h",),
    ("run", "--help"),
    ("run", "-h"),
    ("--version",),
)
KNOWN_SUBCOMMANDS = (
    "exec",
    "review",
    "login",
    "logout",
    "mcp",
    "plugin",
    "mcp-server",
    "app-server",
    "remote-control",
    "completion",
    "update",
    "sandbox",
    "debug",
    "apply",
    "resume",
    "fork",
    "cloud",
    "exec-server",
    "features",
    "help",
)


def _run_probe(codex_executable: str, args: tuple[str, ...], timeout_seconds: int) -> dict[str, Any]:
    completed = subprocess.run(
        (codex_executable, *args),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        shell=False,
        check=False,
    )
    return {
        "args": list(args),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "output": f"{completed.stdout}\n{completed.stderr}",
    }


def _supported_subcommands(help_output: str) -> tuple[str, ...]:
    found = [name for name in KNOWN_SUBCOMMANDS if f"  {name}" in help_output or f"  {name} " in help_output]
    return tuple(sorted(set(found)))


def _version_from_output(output: str) -> str:
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("codex-cli"):
            return stripped
    return ""


def probe_codex_cli_contract(
    *,
    codex_executable: str | None = None,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    executable = codex_executable if codex_executable is not None else shutil.which("codex")
    if not executable:
        contract = CodexCliContract(
            discovery_name=DISCOVERY_NAME,
            status="BLOCKED",
            codex_cli_detected=False,
            version_detected="",
            help_available=False,
            run_help_available=False,
            supported_subcommands=(),
            non_interactive_supported=False,
            file_input_supported=False,
            stdin_input_supported=False,
            recommended_invocation_vector=(),
            blocked_reason="codex CLI not detected",
        )
        return {"contract": contract.to_dict(), "probes": [], "shell_used": False, "task_executed": False}
    probes = []
    try:
        for args in SAFE_PROBES:
            probes.append(_run_probe(executable, args, timeout_seconds))
    except (OSError, subprocess.TimeoutExpired) as exc:
        contract = CodexCliContract(
            discovery_name=DISCOVERY_NAME,
            status="FAILED",
            codex_cli_detected=True,
            version_detected="",
            help_available=False,
            run_help_available=False,
            supported_subcommands=(),
            non_interactive_supported=False,
            file_input_supported=False,
            stdin_input_supported=False,
            recommended_invocation_vector=(),
            blocked_reason=f"safe probe failed: {exc.__class__.__name__}",
        )
        return {"contract": contract.to_dict(), "probes": probes, "shell_used": False, "task_executed": False}
    help_probe = next((probe for probe in probes if probe["args"] == ["--help"]), {})
    version_probe = next((probe for probe in probes if probe["args"] == ["--version"]), {})
    run_help_probe = next((probe for probe in probes if probe["args"] == ["run", "--help"]), {})
    help_output = help_probe.get("output", "")
    run_help_output = run_help_probe.get("output", "")
    subcommands = _supported_subcommands(help_output)
    non_interactive = "exec" in subcommands or "Run Codex non-interactively" in help_output
    run_is_supported = "run" in subcommands
    file_input_supported = "<FILE>" in help_output and "PROMPT" not in help_output
    stdin_input_supported = "stdin" in help_output.lower() or "standard input" in help_output.lower()
    recommended = ("codex", "exec", "<bounded_prompt>") if non_interactive else ()
    status = "DISCOVERED_PARTIAL" if non_interactive else "BLOCKED"
    blocked_reason = "" if non_interactive else "non-interactive execution not discoverable from safe probes"
    contract = CodexCliContract(
        discovery_name=DISCOVERY_NAME,
        status=status,
        codex_cli_detected=True,
        version_detected=_version_from_output(version_probe.get("output", "")),
        help_available=help_probe.get("exit_code") == 0,
        run_help_available=run_help_probe.get("exit_code") == 0 and run_is_supported,
        supported_subcommands=subcommands,
        non_interactive_supported=non_interactive,
        file_input_supported=file_input_supported,
        stdin_input_supported=stdin_input_supported,
        recommended_invocation_vector=recommended,
        blocked_reason=blocked_reason,
    )
    return {
        "contract": contract.to_dict(),
        "probes": [
            {
                "args": probe["args"],
                "exit_code": probe["exit_code"],
                "stdout_captured": isinstance(probe.get("stdout"), str),
                "stderr_captured": isinstance(probe.get("stderr"), str),
            }
            for probe in probes
        ],
        "shell_used": False,
        "task_executed": False,
    }
