"""Minimal operator CLI for the live governed runtime."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from aigol.runtime.first_real_operator_usage import OPERATOR_COMPLETED, run_first_real_operator_usage
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CLI_SUCCESS = "SUCCESS"
CLI_REJECTED = "REJECTED"
CLI_MODE = "MINIMAL_READONLY_OPERATOR_CLI"
DEFAULT_CREATED_AT = "1970-01-01T00:00:00+00:00"
DEFAULT_OPERATOR_ID = "operator-cli"
DEFAULT_CLI_INVOCATION_ID = "RUNTIME-OPERATOR-CLI-1"

ALLOWED_CLI_STATUSES = frozenset({CLI_SUCCESS, CLI_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _cli_hash_input(evidence: "RuntimeOperatorCLIEvidence") -> dict[str, Any]:
    return {
        "cli_invocation_id": evidence.cli_invocation_id,
        "operator_id": evidence.operator_id,
        "operator_prompt": evidence.operator_prompt,
        "cli_mode": evidence.cli_mode,
        "operator_usage_id": evidence.operator_usage_id,
        "operator_usage_evidence_hash": evidence.operator_usage_evidence_hash,
        "rendered_return": evidence.rendered_return,
        "cli_status": evidence.cli_status,
        "cli_reason": evidence.cli_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RuntimeOperatorCLIEvidence:
    """Immutable replay-visible operator CLI evidence."""

    cli_invocation_id: str
    operator_id: str
    operator_prompt: str
    cli_mode: str
    operator_usage_id: str
    operator_usage_evidence_hash: str
    rendered_return: str
    cli_status: str
    cli_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.cli_invocation_id, "cli_invocation_id")
        _require_string(self.operator_id, "operator_id")
        _require_string(self.operator_prompt, "operator_prompt")
        _require_string(self.cli_mode, "cli_mode")
        _require_string(self.operator_usage_id, "operator_usage_id")
        _require_string(self.rendered_return, "rendered_return")
        _require_string(self.cli_reason, "cli_reason")
        _require_string(self.created_at, "created_at")
        if self.cli_mode != CLI_MODE:
            raise FailClosedRuntimeError("operator CLI mode is not allowed")
        if self.cli_status not in ALLOWED_CLI_STATUSES:
            raise FailClosedRuntimeError("operator CLI status is not allowed")
        expected_hash = replay_hash(_cli_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("operator CLI evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cli_invocation_id": self.cli_invocation_id,
            "operator_id": self.operator_id,
            "operator_prompt": self.operator_prompt,
            "cli_mode": self.cli_mode,
            "operator_usage_id": self.operator_usage_id,
            "operator_usage_evidence_hash": self.operator_usage_evidence_hash,
            "rendered_return": self.rendered_return,
            "cli_status": self.cli_status,
            "cli_reason": self.cli_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "RuntimeOperatorCLIEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("operator CLI evidence must be a JSON object")
        required = {
            "cli_invocation_id",
            "operator_id",
            "operator_prompt",
            "cli_mode",
            "operator_usage_id",
            "operator_usage_evidence_hash",
            "rendered_return",
            "cli_status",
            "cli_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("operator CLI evidence has malformed structure")
        return cls(**evidence)


def run_runtime_operator_cli(
    *,
    cli_invocation_id: str,
    operator_id: str,
    operator_prompt: str,
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Run one prompt through the existing readonly governed operator path."""

    try:
        _require_string(cli_invocation_id, "cli_invocation_id")
        normalized_operator_id = " ".join(_require_string(operator_id, "operator_id").split())
        normalized_prompt = " ".join(_require_string(operator_prompt, "operator_prompt").split())
        _require_string(created_at, "created_at")
        operator_usage = run_first_real_operator_usage(
            operator_usage_id=f"{cli_invocation_id}:OPERATOR_USAGE",
            operator_id=normalized_operator_id,
            operator_request=normalized_prompt,
            created_at=created_at,
            timeout_seconds=timeout_seconds,
        )
        usage_evidence = operator_usage["operator_usage_evidence"]
        cli_status = CLI_SUCCESS if usage_evidence.operator_usage_status == OPERATOR_COMPLETED else CLI_REJECTED
        rendered_return = operator_usage["operator_return"]
        evidence = RuntimeOperatorCLIEvidence(
            cli_invocation_id=cli_invocation_id,
            operator_id=normalized_operator_id,
            operator_prompt=normalized_prompt,
            cli_mode=CLI_MODE,
            operator_usage_id=usage_evidence.operator_usage_id,
            operator_usage_evidence_hash=usage_evidence.evidence_hash,
            rendered_return=rendered_return,
            cli_status=cli_status,
            cli_reason=(
                "operator CLI request completed"
                if cli_status == CLI_SUCCESS
                else "operator CLI request failed closed"
            ),
            created_at=created_at,
        )
        rendered_output = _render_cli_output(evidence, operator_usage)
        return {
            "cli_evidence": evidence,
            "operator_usage": operator_usage,
            "rendered_output": rendered_output,
            "exit_code": 0 if cli_status == CLI_SUCCESS else 1,
            "cli_lineage": reconstruct_runtime_operator_cli_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        evidence = RuntimeOperatorCLIEvidence(
            cli_invocation_id=cli_invocation_id if isinstance(cli_invocation_id, str) and cli_invocation_id else "CLI-INVALID",
            operator_id=operator_id if isinstance(operator_id, str) and operator_id else "OPERATOR-INVALID",
            operator_prompt=operator_prompt if isinstance(operator_prompt, str) and operator_prompt else "PROMPT-INVALID",
            cli_mode=CLI_MODE,
            operator_usage_id="OPERATOR-USAGE-INVALID",
            operator_usage_evidence_hash="",
            rendered_return="operator CLI rejected",
            cli_status=CLI_REJECTED,
            cli_reason="operator CLI request failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else DEFAULT_CREATED_AT,
        )
        return {
            "cli_evidence": evidence,
            "operator_usage": None,
            "rendered_output": _render_cli_output(evidence, None),
            "exit_code": 1,
            "cli_lineage": reconstruct_runtime_operator_cli_lineage([evidence]),
            "governance_authority_separated": True,
        }


def reconstruct_runtime_operator_cli_lineage(
    invocations: list[RuntimeOperatorCLIEvidence | dict[str, Any]]
    | tuple[RuntimeOperatorCLIEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(invocations, list | tuple):
        raise FailClosedRuntimeError("operator CLI lineage must be a list")
    reconstructed = []
    seen_invocation_ids: set[str] = set()
    previous_created_at = ""
    for index, invocation in enumerate(invocations):
        invocation_obj = RuntimeOperatorCLIEvidence.from_dict(invocation) if isinstance(invocation, dict) else invocation
        if not isinstance(invocation_obj, RuntimeOperatorCLIEvidence):
            raise FailClosedRuntimeError("operator CLI lineage entry is invalid")
        artifact = invocation_obj.to_dict()
        if artifact["cli_invocation_id"] in seen_invocation_ids:
            raise FailClosedRuntimeError("operator CLI lineage contains duplicate cli_invocation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("operator CLI lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_invocation_ids.add(artifact["cli_invocation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "cli_index": index,
                "cli_invocation_id": artifact["cli_invocation_id"],
                "operator_id": artifact["operator_id"],
                "cli_status": artifact["cli_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "cli_invocation_count": len(reconstructed),
        "cli_invocations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m aigol.runtime.operator_cli")
    parser.add_argument("prompt")
    parser.add_argument("--operator-id", default=DEFAULT_OPERATOR_ID)
    parser.add_argument("--cli-id", default=DEFAULT_CLI_INVOCATION_ID)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args(argv)
    result = run_runtime_operator_cli(
        cli_invocation_id=args.cli_id,
        operator_id=args.operator_id,
        operator_prompt=args.prompt,
        created_at=args.created_at,
        timeout_seconds=args.timeout_seconds,
    )
    print(result["rendered_output"])
    return result["exit_code"]


def _render_cli_output(evidence: RuntimeOperatorCLIEvidence, operator_usage: dict[str, Any] | None) -> str:
    activation_hash = ""
    if operator_usage is not None and operator_usage.get("activation") is not None:
        activation_hash = operator_usage["activation"]["activation_evidence"].evidence_hash
    return "\n".join(
        [
            f"status={evidence.cli_status}",
            f"return={evidence.rendered_return}",
            f"cli_invocation_id={evidence.cli_invocation_id}",
            f"cli_evidence_hash={evidence.evidence_hash}",
            f"operator_usage_id={evidence.operator_usage_id}",
            f"operator_usage_evidence_hash={evidence.operator_usage_evidence_hash}",
            f"activation_evidence_hash={activation_hash}",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
