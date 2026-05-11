from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.agol_runtime_visibility_guidance import (
    PRIMITIVE_ID,
    RESTART_LIKELIHOOD_HIGH,
    RESTART_LIKELIHOOD_LOW,
    RuntimeVisibilityGuidanceRequest,
    describe_runtime_visibility_guidance_scope,
    generate_runtime_visibility_guidance,
)


def test_demo_experience_change_recommends_bounded_restart_guidance() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("sapianta_system/sapianta_product/demo_experience.py",),
        reload_enabled=False,
    )

    result = generate_runtime_visibility_guidance(request)

    assert result.status == "RESTART_GUIDANCE_RECOMMENDED"
    assert result.restart_required_likelihood == RESTART_LIKELIHOOD_HIGH
    assert result.affected_preview_scope == (
        "sapianta_system/sapianta_product/demo_experience.py",
    )
    assert "--reload" in result.recommended_restart_commands[1]
    assert "AGOL does not restart the process" in result.runtime_visibility_explanation


def test_non_preview_file_does_not_prepare_restart_commands() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("docs/governance/CONSTITUTIONAL_INVARIANTS.md",),
        reload_enabled=False,
    )

    result = generate_runtime_visibility_guidance(request)

    assert result.status == "NO_RUNTIME_VISIBILITY_RESTART_GUIDANCE"
    assert result.restart_required_likelihood == "none"
    assert result.affected_preview_scope == ()
    assert result.recommended_restart_commands == ()


def test_reload_enabled_reduces_restart_likelihood_without_removing_guidance() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("sapianta_system/sapianta_product/static/site.css",),
        reload_enabled=True,
        imported_template_cache_risk=False,
    )

    result = generate_runtime_visibility_guidance(request)

    assert result.restart_required_likelihood == RESTART_LIKELIHOOD_LOW
    assert result.recommended_restart_commands
    assert "reload is reported enabled" in result.runtime_visibility_explanation


def test_stale_localhost_preview_elevates_restart_likelihood() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("sapianta_system/sapianta_product/templates/index.html",),
        reload_enabled=True,
        localhost_preview_observed_stale=True,
    )

    result = generate_runtime_visibility_guidance(request)

    assert result.restart_required_likelihood == RESTART_LIKELIHOOD_HIGH
    assert result.status == "RESTART_GUIDANCE_RECOMMENDED"


def test_guidance_preserves_user_authority_and_non_executing_semantics() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("sapianta_system/sapianta_product/demo_experience.py",),
    )

    result = generate_runtime_visibility_guidance(request)

    assert result.user_confirmation_required is True
    assert result.proposal_only is True
    assert result.runtime_control_authority_granted is False
    assert result.process_restarted is False
    assert result.command_executed is False


def test_missing_user_authority_is_visible_as_boundary_check() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=("sapianta_system/sapianta_product/demo_experience.py",),
        user_final_authority=False,
    )

    result = generate_runtime_visibility_guidance(request)

    assert "user_final_authority_required" in result.forbidden_boundary_checks
    assert result.runtime_control_authority_granted is False


def test_scope_declares_forbidden_runtime_control() -> None:
    description = describe_runtime_visibility_guidance_scope()

    assert description["primitive_id"] == PRIMITIVE_ID
    assert description["runtime_control_authority_granted"] is False
    assert "prepare bounded restart guidance" in description["allowed"]
    assert "restart processes" in description["forbidden"]
    assert "execute shell commands" in description["forbidden"]


def test_guidance_hash_is_stable_and_replay_visible() -> None:
    request = RuntimeVisibilityGuidanceRequest(
        modified_files=(
            "./sapianta_system/sapianta_product/demo_experience.py",
            "docs/notes.md",
        ),
        reload_enabled=False,
    )

    first = generate_runtime_visibility_guidance(request)
    second = generate_runtime_visibility_guidance(request)
    description = describe_runtime_visibility_guidance_scope()

    assert first.deterministic_hash == second.deterministic_hash
    assert first.request_hash == second.request_hash
    assert first.command_hash == second.command_hash
    assert first.scope_hash == description["scope_hash"]
    assert "runtime/governance/agol_runtime_visibility_guidance.py" in first.replay_lineage
