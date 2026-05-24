"""Canonical deterministic AiGOL governance CLI foundation."""

from __future__ import annotations

import argparse
import json
from typing import Any

from aigol.cli.commands.continuity import continuity_preview_summary
from aigol.cli.commands.diagnostics import runtime_diagnostics
from aigol.cli.commands.dispatch import authorize_dispatch
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.governance import validate_governance_continuity
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cli.commands.status import status_summary
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

    diagnostics = subcommands.add_parser("diagnostics")
    diagnostics_sub = diagnostics.add_subparsers(dest="diagnostics_command", required=True)
    diagnostics_runtime = diagnostics_sub.add_parser("runtime")
    diagnostics_runtime.add_argument("--extension-id", default="")

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
        )
    if args.command == "diagnostics" and args.diagnostics_command == "runtime":
        return runtime_diagnostics(extension_id=args.extension_id)
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
        return render_card(
            "AIGOL EXECUTION HANDOFF",
            [
                f"execution_status: {result.get('execution_status')}",
                f"provider_invoked: {result.get('provider_invoked')}",
                f"replay_identity: {result.get('replay_identity')}",
                f"execution_result_hash: {result.get('execution_result_hash')}",
                f"execution_governance_hash: {result.get('execution_governance_hash')}",
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
    return render_card("AIGOL", [_json(result)])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_command(args)
    print(render_command_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
