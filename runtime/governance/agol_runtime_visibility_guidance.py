"""Bounded AGOL runtime visibility guidance.

This module detects likely preview/source divergence during Product 1
refinement work. It prepares restart guidance only; it never inspects live
processes, executes commands, restarts servers, or grants runtime authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .preview_runtime import PREVIEW_APP_TARGET
from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PRIMITIVE_ID = "AGOL_RUNTIME_VISIBILITY_GUIDANCE_V1"
SCOPE_ID = "PRODUCT_1_RUNTIME_VISIBILITY_GUIDANCE_ONLY"
RESTART_LIKELIHOOD_HIGH = "high"
RESTART_LIKELIHOOD_MEDIUM = "medium"
RESTART_LIKELIHOOD_LOW = "low"
NO_RESTART_REQUIRED = "none"
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/AGOL_REFINEMENT_GUIDANCE_WORKFLOW_V1.md",
    "docs/governance/GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1.md",
    "docs/governance/AGOL_RUNTIME_VISIBILITY_GUIDANCE_V1.md",
    "runtime/governance/preview_runtime.py",
    "runtime/governance/agol_runtime_visibility_guidance.py",
    "tests/test_agol_runtime_visibility_guidance.py",
)
RECOMMENDED_RESTART_COMMANDS = (
    "Stop the existing uvicorn preview process from the terminal where it is running.",
    f"uvicorn {PREVIEW_APP_TARGET} --host 127.0.0.1 --port 8010 --reload",
)

VISIBLE_PREVIEW_PATHS = (
    "sapianta_system/sapianta_product/demo_experience.py",
    "sapianta_system/sapianta_product/main.py",
)
VISIBLE_PREVIEW_PREFIXES = (
    "sapianta_system/sapianta_product/static/",
    "sapianta_system/sapianta_product/templates/",
    "static/",
)
VISIBLE_PREVIEW_SUFFIXES = (
    ".css",
    ".html",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".webp",
)


@dataclass(frozen=True)
class RuntimeVisibilityGuidanceRequest:
    modified_files: tuple[str, ...]
    preview_runtime: str = "uvicorn"
    app_target: str = PREVIEW_APP_TARGET
    reload_enabled: bool = False
    imported_template_cache_risk: bool = True
    localhost_preview_observed_stale: bool = False
    requested_output: str = "runtime_visibility_guidance"
    user_final_authority: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_target": self.app_target,
            "imported_template_cache_risk": self.imported_template_cache_risk,
            "localhost_preview_observed_stale": self.localhost_preview_observed_stale,
            "modified_files": sorted(_normalize_path(path) for path in self.modified_files),
            "preview_runtime": self.preview_runtime,
            "reload_enabled": self.reload_enabled,
            "requested_output": self.requested_output,
            "user_final_authority": self.user_final_authority,
        }


@dataclass(frozen=True)
class RuntimeVisibilityGuidanceResult:
    primitive_id: str
    status: str
    restart_required_likelihood: str
    affected_preview_scope: tuple[str, ...]
    runtime_visibility_explanation: str
    recommended_restart_commands: tuple[str, ...]
    user_confirmation_required: bool
    proposal_only: bool
    runtime_control_authority_granted: bool
    process_restarted: bool
    command_executed: bool
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "affected_preview_scope": list(self.affected_preview_scope),
            "command_executed": self.command_executed,
            "command_hash": self.command_hash,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "primitive_id": self.primitive_id,
            "process_restarted": self.process_restarted,
            "proposal_only": self.proposal_only,
            "recommended_restart_commands": list(self.recommended_restart_commands),
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "restart_required_likelihood": self.restart_required_likelihood,
            "runtime_control_authority_granted": self.runtime_control_authority_granted,
            "runtime_visibility_explanation": self.runtime_visibility_explanation,
            "scope_hash": self.scope_hash,
            "status": self.status,
            "user_confirmation_required": self.user_confirmation_required,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_runtime_visibility_guidance_scope() -> dict[str, object]:
    return {
        "allowed": [
            "detect likely preview/source visibility divergence",
            "explain why restart may be required",
            "prepare bounded restart guidance",
            "suggest user-executed restart commands",
            "preserve replay-visible guidance evidence",
        ],
        "forbidden": [
            "restart processes",
            "execute shell commands",
            "manage daemons",
            "own server lifecycle",
            "mutate deployment state",
            "grant runtime control authority",
        ],
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "runtime_control_authority_granted": False,
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
    }


def generate_runtime_visibility_guidance(
    request: RuntimeVisibilityGuidanceRequest,
) -> RuntimeVisibilityGuidanceResult:
    affected_scope = _affected_preview_scope(request.modified_files)
    likelihood = _restart_required_likelihood(request, affected_scope)
    commands = RECOMMENDED_RESTART_COMMANDS if likelihood != NO_RESTART_REQUIRED else ()
    forbidden = _forbidden_boundary_checks(request)
    status = (
        "RESTART_GUIDANCE_RECOMMENDED"
        if likelihood in {RESTART_LIKELIHOOD_HIGH, RESTART_LIKELIHOOD_MEDIUM}
        else "NO_RUNTIME_VISIBILITY_RESTART_GUIDANCE"
    )
    explanation = _runtime_visibility_explanation(request, affected_scope, likelihood)

    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=commands,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "affected_preview_scope": list(affected_scope),
        "command_executed": False,
        "command_hash": replay_identity["command_hash"],
        "forbidden_boundary_checks": list(forbidden),
        "primitive_id": replay_identity["primitive_id"],
        "process_restarted": False,
        "proposal_only": True,
        "recommended_restart_commands": list(commands),
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "restart_required_likelihood": likelihood,
        "runtime_control_authority_granted": False,
        "runtime_visibility_explanation": explanation,
        "scope_hash": replay_identity["scope_hash"],
        "status": status,
        "user_confirmation_required": True,
    }
    return RuntimeVisibilityGuidanceResult(
        primitive_id=str(replay_identity["primitive_id"]),
        status=status,
        restart_required_likelihood=likelihood,
        affected_preview_scope=affected_scope,
        runtime_visibility_explanation=explanation,
        recommended_restart_commands=commands,
        user_confirmation_required=True,
        proposal_only=True,
        runtime_control_authority_granted=False,
        process_restarted=False,
        command_executed=False,
        forbidden_boundary_checks=forbidden,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _affected_preview_scope(modified_files: tuple[str, ...]) -> tuple[str, ...]:
    affected = {
        _normalize_path(path)
        for path in modified_files
        if _likely_affects_visible_preview(path)
    }
    return tuple(sorted(affected))


def _likely_affects_visible_preview(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized in VISIBLE_PREVIEW_PATHS:
        return True
    if normalized.startswith(VISIBLE_PREVIEW_PREFIXES):
        return True
    return (
        normalized.startswith("sapianta_system/sapianta_product/")
        and normalized.endswith(VISIBLE_PREVIEW_SUFFIXES)
    )


def _restart_required_likelihood(
    request: RuntimeVisibilityGuidanceRequest,
    affected_scope: tuple[str, ...],
) -> str:
    if not affected_scope:
        return NO_RESTART_REQUIRED
    if request.localhost_preview_observed_stale:
        return RESTART_LIKELIHOOD_HIGH
    if request.preview_runtime == "uvicorn" and not request.reload_enabled:
        return RESTART_LIKELIHOOD_HIGH
    if request.imported_template_cache_risk:
        return RESTART_LIKELIHOOD_MEDIUM
    return RESTART_LIKELIHOOD_LOW


def _runtime_visibility_explanation(
    request: RuntimeVisibilityGuidanceRequest,
    affected_scope: tuple[str, ...],
    likelihood: str,
) -> str:
    if not affected_scope:
        return (
            "No modified file is classified as likely visible in the Product 1 preview, "
            "so restart guidance is not recommended by this helper."
        )
    if likelihood == RESTART_LIKELIHOOD_HIGH:
        return (
            "Modified Product 1 preview files may not be visible because uvicorn can keep "
            "already-imported Python and template content in memory when the preview is "
            "running without --reload. Restart is recommended for user-confirmed preview "
            "continuity; AGOL does not restart the process."
        )
    if likelihood == RESTART_LIKELIHOOD_MEDIUM:
        return (
            "Modified files affect visible preview scope and imported template state may "
            "remain stale. Restart guidance is prepared so the user can refresh runtime "
            "visibility while retaining final authority."
        )
    if request.reload_enabled:
        return (
            "Modified files affect visible preview scope, but reload is reported enabled. "
            "A manual restart is lower priority unless the browser still shows stale output."
        )
    return "Visible preview changes were detected with low restart likelihood."


def _forbidden_boundary_checks(
    request: RuntimeVisibilityGuidanceRequest,
) -> tuple[str, ...]:
    checks: set[str] = set()
    if not request.user_final_authority:
        checks.add("user_final_authority_required")
    if request.requested_output not in {
        "runtime_visibility_guidance",
        "restart_recommendation",
        "preview_continuity_guidance",
    }:
        checks.add("unsupported_guidance_output_requires_approval")
    if request.preview_runtime != "uvicorn":
        checks.add("unverified_runtime_requires_manual_review")
    if request.app_target != PREVIEW_APP_TARGET:
        checks.add("unapproved_app_target_requires_manual_review")
    return tuple(sorted(checks))


def _normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("./")


def _scope_hash() -> str:
    return str(
        build_replay_identity(
            primitive_id=PRIMITIVE_ID,
            request_payload={},
            command=RECOMMENDED_RESTART_COMMANDS,
            scope_payload=_scope_payload(),
            replay_lineage=REPLAY_LINEAGE,
        )["scope_hash"]
    )


def _scope_payload() -> dict[str, object]:
    return {
        "allowed_outputs": [
            "runtime_visibility_guidance",
            "restart_recommendation",
            "preview_continuity_guidance",
        ],
        "app_target": PREVIEW_APP_TARGET,
        "execution_authority_granted": False,
        "mutation_performed": False,
        "primitive_id": PRIMITIVE_ID,
        "process_restart_authority_granted": False,
        "scope_id": SCOPE_ID,
        "suggested_restart_commands": list(RECOMMENDED_RESTART_COMMANDS),
        "user_final_authority_required": True,
    }
