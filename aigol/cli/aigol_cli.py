"""Canonical deterministic AiGOL governance CLI foundation."""

from __future__ import annotations

import argparse
import json
from typing import Any

from aigol.cli.commands.cognition import (
    check_semantic_replay_continuity,
    inspect_cognition,
    inspect_integrity,
    inspect_lifecycle,
    inspect_registry,
    inspect_topology,
)
from aigol.cli.commands.continuity import continuity_preview_summary
from aigol.cli.commands.diagnostics import runtime_diagnostics
from aigol.cli.commands.dispatch import authorize_dispatch
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.governance import validate_governance_continuity
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cli.commands.replay import ledger_summary, verify_replay
from aigol.cli.commands.return_flow import inspect_return
from aigol.cli.commands.status import status_summary
from aigol.cognition.integrity_summary import render_cognition_integrity_summary
from aigol.cognition.lifecycle_model import render_cognition_lifecycle_summary
from aigol.cognition.registry import render_cognition_registry_summary
from aigol.cognition.semantic_replay import render_semantic_replay_report
from aigol.cognition.state_envelope import render_cognition_summary
from aigol.cognition.topology_report import render_cognition_topology_summary
from aigol.cli.render.status_renderer import render_status
from aigol.cli.render.terminal_cards import render_card


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _artifact_from_args(args: argparse.Namespace) -> dict:
    if getattr(args, "artifact_json", ""):
        loaded = json.loads(args.artifact_json)
        if not isinstance(loaded, dict):
            raise ValueError("artifact JSON must be an object")
        return loaded
    return generate_ingress_artifact(
        human_request=getattr(args, "human_request", ""),
        semantic_intent=getattr(args, "semantic_intent", ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aigol", description="Deterministic AiGOL governance CLI substrate")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("status")

    ingress = subcommands.add_parser("ingress")
    ingress_sub = ingress.add_subparsers(dest="ingress_command", required=True)
    ingress_generate = ingress_sub.add_parser("generate")
    ingress_generate.add_argument("--human-request", required=True)
    ingress_generate.add_argument("--semantic-intent", required=True)

    governance = subcommands.add_parser("governance")
    governance_sub = governance.add_subparsers(dest="governance_command", required=True)
    governance_validate = governance_sub.add_parser("validate")
    governance_validate.add_argument("--artifact-json", default="")
    governance_validate.add_argument("--human-request", default="Validate governed CLI continuity.")
    governance_validate.add_argument("--semantic-intent", default="Deterministic governance validation")

    continuity = subcommands.add_parser("continuity")
    continuity_sub = continuity.add_subparsers(dest="continuity_command", required=True)
    continuity_preview = continuity_sub.add_parser("preview")
    continuity_preview.add_argument("--artifact-json", default="")
    continuity_preview.add_argument("--human-request", default="Preview governed execution continuity.")
    continuity_preview.add_argument("--semantic-intent", default="Deterministic continuity preview")

    dispatch = subcommands.add_parser("dispatch")
    dispatch_sub = dispatch.add_subparsers(dest="dispatch_command", required=True)
    dispatch_authorize = dispatch_sub.add_parser("authorize")
    dispatch_authorize.add_argument("--artifact-json", default="")
    dispatch_authorize.add_argument("--human-request", default="Authorize governed dispatch continuity.")
    dispatch_authorize.add_argument("--semantic-intent", default="Deterministic dispatch authorization")

    execution = subcommands.add_parser("execution")
    execution_sub = execution.add_subparsers(dest="execution_command", required=True)
    execution_handoff = execution_sub.add_parser("handoff")
    execution_handoff.add_argument("--artifact-json", default="")
    execution_handoff.add_argument("--human-request", default="Run governed execution handoff.")
    execution_handoff.add_argument("--semantic-intent", default="Deterministic execution handoff")
    execution_handoff.add_argument("--workspace-path", default="")
    execution_handoff.add_argument("--timeout-seconds", type=int, default=600)
    execution_handoff.add_argument("--full-codex-exec", action="store_true")
    execution_handoff.add_argument("--runtime-root", default="")

    return_cmd = subcommands.add_parser("return")
    return_sub = return_cmd.add_subparsers(dest="return_command", required=True)
    return_inspect = return_sub.add_parser("inspect")
    return_inspect.add_argument("--replay-identity", required=True)
    return_inspect.add_argument("--runtime-root", default="")

    replay = subcommands.add_parser("replay")
    replay_sub = replay.add_subparsers(dest="replay_command", required=True)
    replay_ledger = replay_sub.add_parser("ledger")
    replay_ledger.add_argument("--runtime-root", default="")
    replay_ledger.add_argument("--limit", type=int, default=10)
    replay_verify = replay_sub.add_parser("verify")
    replay_verify.add_argument("--replay-identity", required=True)
    replay_verify.add_argument("--runtime-root", default="")

    diagnostics = subcommands.add_parser("diagnostics")
    diagnostics_sub = diagnostics.add_subparsers(dest="diagnostics_command", required=True)
    diagnostics_runtime = diagnostics_sub.add_parser("runtime")
    diagnostics_runtime.add_argument("--extension-id", default="")

    cognition = subcommands.add_parser("cognition")
    cognition_sub = cognition.add_subparsers(dest="cognition_command", required=True)
    cognition_inspect = cognition_sub.add_parser("inspect")
    cognition_inspect.add_argument("--input", default="")
    cognition_inspect.add_argument("--json", action="store_true")
    cognition_inspect.add_argument("--output", default="")
    cognition_continuity = cognition_sub.add_parser("continuity-check")
    cognition_continuity.add_argument("--input", default="")
    cognition_continuity.add_argument("--json", action="store_true")
    cognition_continuity.add_argument("--output", default="")
    cognition_registry = cognition_sub.add_parser("registry")
    cognition_registry.add_argument("--input", default="")
    cognition_registry.add_argument("--json", action="store_true")
    cognition_registry.add_argument("--output", default="")
    cognition_topology = cognition_sub.add_parser("topology")
    cognition_topology.add_argument("--input", default="")
    cognition_topology.add_argument("--json", action="store_true")
    cognition_topology.add_argument("--output", default="")
    cognition_lifecycle = cognition_sub.add_parser("lifecycle")
    cognition_lifecycle.add_argument("--json", action="store_true")
    cognition_lifecycle.add_argument("--output", default="")
    cognition_lifecycle.add_argument("--validate", action="store_true")
    cognition_integrity = cognition_sub.add_parser("integrity")
    cognition_integrity.add_argument("--input", default="")
    cognition_integrity.add_argument("--json", action="store_true")
    cognition_integrity.add_argument("--output", default="")
    cognition_integrity.add_argument("--validate", action="store_true")

    return parser


def run_command(args: argparse.Namespace) -> dict:
    if args.command == "status":
        return status_summary()
    if args.command == "ingress" and args.ingress_command == "generate":
        return {
            "command": "aigol ingress generate",
            "ingress_artifact": generate_ingress_artifact(
                human_request=args.human_request,
                semantic_intent=args.semantic_intent,
            ),
        }
    if args.command == "governance" and args.governance_command == "validate":
        return validate_governance_continuity(ingress_artifact=_artifact_from_args(args))
    if args.command == "continuity" and args.continuity_command == "preview":
        return continuity_preview_summary(ingress_artifact=_artifact_from_args(args))
    if args.command == "dispatch" and args.dispatch_command == "authorize":
        return authorize_dispatch(ingress_artifact=_artifact_from_args(args))
    if args.command == "execution" and args.execution_command == "handoff":
        return run_execution_handoff(
            ingress_artifact=_artifact_from_args(args),
            workspace_path=args.workspace_path or None,
            timeout_seconds=args.timeout_seconds,
            provider_success_proof=not args.full_codex_exec,
            runtime_root=args.runtime_root or None,
        )
    if args.command == "return" and args.return_command == "inspect":
        return inspect_return(replay_identity=args.replay_identity, runtime_root=args.runtime_root or None)
    if args.command == "replay" and args.replay_command == "ledger":
        return ledger_summary(runtime_root=args.runtime_root or None, limit=args.limit)
    if args.command == "replay" and args.replay_command == "verify":
        return verify_replay(replay_identity=args.replay_identity, runtime_root=args.runtime_root or None)
    if args.command == "diagnostics" and args.diagnostics_command == "runtime":
        return runtime_diagnostics(extension_id=args.extension_id)
    if args.command == "cognition" and args.cognition_command == "inspect":
        return inspect_cognition(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "continuity-check":
        return check_semantic_replay_continuity(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "registry":
        return inspect_registry(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "topology":
        return inspect_topology(
            input_path=args.input or None,
            output_path=args.output or None,
        )
    if args.command == "cognition" and args.cognition_command == "lifecycle":
        return inspect_lifecycle(
            output_path=args.output or None,
            validate=args.validate,
        )
    if args.command == "cognition" and args.cognition_command == "integrity":
        return inspect_integrity(
            input_path=args.input or None,
            output_path=args.output or None,
            validate=args.validate,
        )
    raise ValueError("unsupported command")


def render_command_result(result: dict) -> str:
    command = result.get("command", "")
    if command == "aigol status":
        return render_status(result)
    if command == "aigol ingress generate":
        artifact = result["ingress_artifact"]
        return render_card(
            "AIGOL INGRESS GENERATE",
            [
                f"artifact_type: {artifact.get('artifact_type')}",
                f"validation_status: {artifact.get('validation_status')}",
                f"replay_identity: {artifact.get('replay_identity')}",
                f"artifact_hash: {artifact.get('hashes', {}).get('artifact_hash')}",
                "execution_authority: false",
            ],
        )
    if command == "aigol governance validate":
        return render_card(
            "AIGOL GOVERNANCE VALIDATE",
            [
                f"governance_status: {result.get('governance_status')}",
                f"validation_status: {result.get('validation', {}).get('status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"hash_continuity: {_json(result.get('hash_continuity', {}))}",
            ],
        )
    if command == "aigol continuity preview":
        return render_card(
            "AIGOL CONTINUITY PREVIEW",
            [
                f"continuity_status: {result.get('continuity_status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"hash_continuity: {_json(result.get('hash_continuity', {}))}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"native_messaging_called: {result.get('native_messaging_called')}",
            ],
        )
    if command == "aigol dispatch authorize":
        return render_card(
            "AIGOL DISPATCH AUTHORIZE",
            [
                f"dispatch_status: {result.get('dispatch_status')}",
                f"dispatch_authorized: {result.get('dispatch_authorized')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"dispatch_authorization_hash: {result.get('dispatch_authorization_hash')}",
                "execution_performed: false",
            ],
        )
    if command == "aigol execution handoff":
        diagnostics = result.get("diagnostic_evidence", {})
        provider_state = "INVOKED" if result.get("provider_invoked") else "NOT_INVOKED"
        return_state = "GENERATED" if result.get("governed_return_hash") else "NOT_GENERATED"
        continuity_state = "VERIFIED" if result.get("continuity_verified") else "NOT_VERIFIED"
        return render_card(
            "AIGOL EXECUTION RESULT",
            [
                "Execution:",
                f"  {result.get('execution_status')}",
                "Provider:",
                f"  {provider_state}",
                "Command:",
                f"  {diagnostics.get('provider_command')}",
                "Replay:",
                f"  {result.get('replay_identity')}",
                "Governed Return:",
                f"  {return_state}",
                "Return Hash:",
                f"  {result.get('governed_return_hash')}",
                "Exit Code:",
                f"  {result.get('provider_exit_code')}",
                "Continuity:",
                f"  {continuity_state}",
                "Diagnostics:",
                f"  provider_executable_found: {diagnostics.get('provider_executable_found')}",
                f"  failure_stage: {diagnostics.get('failure_stage')}",
                f"  fail_closed: {result.get('fail_closed')}",
                f"  persistence: {result.get('persistence', {}).get('status')}",
            ],
        )
    if command == "aigol return inspect":
        return render_card(
            "AIGOL RETURN INSPECT",
            [
                f"status: {result.get('status')}",
                f"execution_status: {result.get('execution_status')}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"governed_return_hash: {result.get('governed_return_hash')}",
                f"continuity_verified: {result.get('continuity_verified')}",
                f"fail_closed: {result.get('fail_closed')}",
                f"evidence_path: {result.get('evidence_path', '')}",
            ],
        )
    if command == "aigol replay ledger":
        lines = []
        for entry in result.get("entries", []):
            lines.append(
                f"{entry.get('replay_identity')} | {entry.get('execution_status')} | {entry.get('governed_return_hash')}"
            )
        return render_card("AIGOL REPLAY LEDGER", lines or ["NO GOVERNED RETURNS"])
    if command == "aigol replay verify":
        return render_card(
            "AIGOL REPLAY VERIFY",
            [
                f"status: {result.get('status')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"governed_return_hash_valid: {result.get('governed_return_hash_valid')}",
                f"execution_result_hash_present: {result.get('execution_result_hash_present')}",
                f"evidence_files_exist: {result.get('evidence_files_exist')}",
                f"ledger_entry_exists: {result.get('ledger_entry_exists')}",
                f"lineage_continuity_exists: {result.get('lineage_continuity_exists')}",
                f"fail_closed: {result.get('fail_closed')}",
            ],
        )
    if command == "aigol diagnostics runtime":
        diagnostics = result.get("runtime_diagnostics", {})
        return render_card(
            "AIGOL DIAGNOSTICS RUNTIME",
            [
                f"native_host_launch_ready: {diagnostics.get('native_host_launch_ready')}",
                f"chrome_runtime_launch_allowed: {diagnostics.get('chrome_runtime_launch_allowed')}",
                f"failure_stage: {result.get('failure_stage')}",
            ],
        )
    if command == "aigol cognition inspect":
        envelope = result.get("cognition_state_envelope", {})
        return render_card(
            "AIGOL COGNITION INSPECT",
            render_cognition_summary(envelope).splitlines(),
        )
    if command == "aigol cognition continuity-check":
        check = result.get("semantic_replay_continuity_check", {})
        return render_card(
            "AIGOL COGNITION CONTINUITY CHECK",
            render_semantic_replay_report(check).splitlines(),
        )
    if command == "aigol cognition registry":
        registry = result.get("cognition_registry", {})
        validation = result.get("registry_validation", {})
        return render_card(
            "AIGOL COGNITION REGISTRY",
            render_cognition_registry_summary(registry, validation).splitlines(),
        )
    if command == "aigol cognition topology":
        report = result.get("cognition_topology_report", {})
        return render_card(
            "AIGOL COGNITION TOPOLOGY",
            render_cognition_topology_summary(report).splitlines(),
        )
    if command == "aigol cognition lifecycle":
        model = result.get("cognition_lifecycle_model", {})
        return render_card(
            "AIGOL COGNITION LIFECYCLE",
            render_cognition_lifecycle_summary(model).splitlines(),
        )
    if command == "aigol cognition integrity":
        summary = result.get("cognition_integrity_summary", {})
        return render_card(
            "AIGOL COGNITION INTEGRITY",
            render_cognition_integrity_summary(summary).splitlines(),
        )
    return render_card("AIGOL", [_json(result)])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_command(args)
    if getattr(args, "json", False):
        print(_json(result))
    else:
        print(render_command_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
