from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_validation_allowlist import (
    VALIDATION_ALLOWLIST_VERSION,
    get_validation_command_spec,
)
from aigol.runtime.platform_core_validation_candidate import VALIDATION_CANDIDATE_ARTIFACT_V1
from aigol.runtime.platform_core_validation_suite_candidate import VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1
from aigol.runtime.platform_validation_plan_candidate_composition_runtime import (
    FAILED_CLOSED,
    SINGLE_VALIDATION_CANDIDATE_COMPOSED,
    VALIDATION_SUITE_CANDIDATE_COMPOSED,
    compose_platform_validation_candidate,
    reconstruct_platform_validation_candidate_composition_replay,
    validate_platform_validation_candidate_composition_artifact,
)
from aigol.runtime.platform_validation_planning_runtime import (
    AUTHORITY_FLAGS as PLAN_AUTHORITY_FLAGS,
    PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
    PLATFORM_VALIDATION_PLANNING_RUNTIME_VERSION,
    VALIDATION_PLAN_COMPOSED,
)
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"


def _plan(*command_ids: str) -> dict:
    requirement = {
        "requirement_order": 0,
        "requirement_category": "CAPABILITY",
        "source_identifier": "PLATFORM_VALIDATION_PLANNING",
        "requirement_type": "CAPABILITY_REGRESSION_VERIFICATION",
        "requirement_owner": "PLATFORM_CORE_VALIDATION_PLANNING",
        "mapping_authority": "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1",
        "mapping_evidence": {"affected_paths": ["aigol/runtime/platform_validation_planning_runtime.py"]},
        "required": True,
        "requirement_index": 0,
        "requirement_id": "VALIDATION-REQUIREMENT-000",
    }
    requirement["requirement_hash"] = replay_hash(requirement)
    commands = []
    for index, command_id in enumerate(command_ids):
        spec = get_validation_command_spec(command_id)
        commands.append(
            {
                "command_id": command_id,
                "allowlist_version": spec["allowlist_version"],
                "command_spec_hash": spec["spec_hash"],
                "exact_mapping_basis": "DECLARED_COMMAND_TARGET_SET_EQUALS_AFFECTED_PATH_SET",
                "affected_paths": [f"aigol/runtime/exact-target-{index}.py"],
            }
        )
    artifact = {
        "artifact_type": PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
        "runtime_version": PLATFORM_VALIDATION_PLANNING_RUNTIME_VERSION,
        "validation_plan_id": "PLAN-G27-09",
        "planning_status": VALIDATION_PLAN_COMPOSED,
        "source_artifact_type": "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1",
        "platform_change_impact_reference": "IMPACT-G27-09",
        "platform_change_impact_hash": replay_hash({"impact": "G27-09"}),
        "platform_change_impact_artifact_hash": replay_hash({"impact-artifact": "G27-09"}),
        "validation_requirements": [requirement],
        "validation_requirement_count": 1,
        "allowlisted_command_references": commands,
        "allowlisted_command_reference_count": len(commands),
        "validation_allowlist_version": VALIDATION_ALLOWLIST_VERSION,
        "capability_registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
        "unresolved_mappings": [],
        "unresolved_mapping_count": 0,
        "mapping_policy": {
            "impact_to_requirement_mapping": "EXACT_TYPED_IMPACT_SURFACE_MAPPING",
            "command_mapping": "EXACT_DECLARED_TARGET_SET_ONLY",
            "command_synthesis_allowed": False,
            "allowlist_expansion_allowed": False,
            "deterministic_ordering": True,
        },
        "created_at": CREATED_AT,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "validation_candidates_constructed": False,
        "validation_executed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
        "authority_flags": deepcopy(PLAN_AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["platform_validation_plan_hash"] = _plan_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _compose(tmp_path, plan: dict, name: str = "composition") -> dict:
    return compose_platform_validation_candidate(
        composition_id=f"COMPOSITION-G27-09-{name}",
        session_id="SESSION-G27-09",
        validation_plan_artifact=plan,
        validation_plan_reference=plan["validation_plan_id"],
        validation_plan_artifact_hash=plan["artifact_hash"],
        validation_plan_hash=plan["platform_validation_plan_hash"],
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_composes_one_existing_single_command_candidate_and_reconstructs(tmp_path) -> None:
    capture = _compose(tmp_path, _plan("PY_COMPILE_G8_VALIDATION_TARGETS"))
    artifact = capture["platform_validation_candidate_composition_artifact"]
    candidate = capture["candidate_artifact"]
    reconstructed = reconstruct_platform_validation_candidate_composition_replay(tmp_path / "composition")

    assert capture["composition_status"] == SINGLE_VALIDATION_CANDIDATE_COMPOSED
    assert candidate["artifact_type"] == VALIDATION_CANDIDATE_ARTIFACT_V1
    assert candidate["command_id"] == "PY_COMPILE_G8_VALIDATION_TARGETS"
    assert candidate["associated_reference"]["validation_plan_id"] == "PLAN-G27-09"
    assert "VALIDATION-REQUIREMENT-000" in candidate["validation_purpose"]
    assert reconstructed["candidate_artifact_hash"] == candidate["artifact_hash"]
    assert validate_platform_validation_candidate_composition_artifact(artifact) == artifact


def test_composes_one_existing_suite_in_plan_order(tmp_path) -> None:
    plan = _plan("PY_COMPILE_G8_VALIDATION_TARGETS", "PYTHON_VALIDATION_FAILS_FOR_TEST")
    capture = _compose(tmp_path, plan)
    candidate = capture["candidate_artifact"]

    assert capture["composition_status"] == VALIDATION_SUITE_CANDIDATE_COMPOSED
    assert candidate["artifact_type"] == VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1
    assert candidate["command_ids"] == [
        "PY_COMPILE_G8_VALIDATION_TARGETS",
        "PYTHON_VALIDATION_FAILS_FOR_TEST",
    ]
    assert candidate["associated_reference"]["validation_plan_hash"] == plan["platform_validation_plan_hash"]
    assert all(record["single_command_candidate"]["associated_reference"]["replay_visible"] for record in candidate["commands"])


def test_mandatory_requirements_without_exact_commands_fail_closed(tmp_path) -> None:
    capture = _compose(tmp_path, _plan())

    assert capture["composition_status"] == FAILED_CLOSED
    assert capture["candidate_artifact"] is None
    assert "mandatory requirements lack exact allowlisted command mappings" in capture["failure_reason"]


def test_plan_reference_artifact_hash_and_plan_hash_are_bound(tmp_path) -> None:
    plan = _plan("PY_COMPILE_G8_VALIDATION_TARGETS")
    wrong_reference = compose_platform_validation_candidate(
        composition_id="COMPOSITION-WRONG-REFERENCE",
        session_id="SESSION-G27-09",
        validation_plan_artifact=plan,
        validation_plan_reference="OTHER-PLAN",
        validation_plan_artifact_hash=plan["artifact_hash"],
        validation_plan_hash=plan["platform_validation_plan_hash"],
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-reference",
    )
    wrong_artifact_hash = compose_platform_validation_candidate(
        composition_id="COMPOSITION-WRONG-ARTIFACT-HASH",
        session_id="SESSION-G27-09",
        validation_plan_artifact=plan,
        validation_plan_reference=plan["validation_plan_id"],
        validation_plan_artifact_hash=replay_hash({"wrong": "artifact"}),
        validation_plan_hash=plan["platform_validation_plan_hash"],
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-artifact-hash",
    )
    wrong_plan_hash = compose_platform_validation_candidate(
        composition_id="COMPOSITION-WRONG-PLAN-HASH",
        session_id="SESSION-G27-09",
        validation_plan_artifact=plan,
        validation_plan_reference=plan["validation_plan_id"],
        validation_plan_artifact_hash=plan["artifact_hash"],
        validation_plan_hash=replay_hash({"wrong": "plan"}),
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-plan-hash",
    )

    assert "plan reference mismatch" in wrong_reference["failure_reason"]
    assert "plan artifact hash mismatch" in wrong_artifact_hash["failure_reason"]
    assert "plan hash mismatch" in wrong_plan_hash["failure_reason"]


def test_non_exact_command_mapping_fails_closed(tmp_path) -> None:
    plan = _plan("PY_COMPILE_G8_VALIDATION_TARGETS")
    plan["allowlisted_command_references"][0]["exact_mapping_basis"] = "INFERRED"
    plan["platform_validation_plan_hash"] = _plan_hash(plan)
    plan.pop("artifact_hash")
    plan["artifact_hash"] = replay_hash(plan)

    capture = _compose(tmp_path, plan)

    assert capture["composition_status"] == FAILED_CLOSED
    assert "exact command mapping required" in capture["failure_reason"]


def test_composition_is_deterministic_and_non_authoritative(tmp_path) -> None:
    plan = _plan("PY_COMPILE_G8_VALIDATION_TARGETS")
    first = _compose(tmp_path, plan, "same")
    second = _compose(tmp_path, plan, "same-two")
    first_artifact = first["platform_validation_candidate_composition_artifact"]

    assert first["candidate_artifact"]["command_spec_hash"] == second["candidate_artifact"]["command_spec_hash"]
    assert first_artifact["validation_executed"] is False
    assert first_artifact["worker_invoked"] is False
    assert first_artifact["provider_invoked"] is False
    assert first_artifact["execution_authorized"] is False
    assert first_artifact["repository_mutated"] is False
    assert first_artifact["certification_performed"] is False
    assert first_artifact["commands_synthesized"] is False
    assert first_artifact["validation_allowlist_expanded"] is False
    assert all(value is False for value in first_artifact["authority_flags"].values())


def test_replay_tampering_fails_closed(tmp_path) -> None:
    _compose(tmp_path, _plan("PY_COMPILE_G8_VALIDATION_TARGETS"))
    replay_file = tmp_path / "composition" / "000_platform_validation_candidate_composition_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["candidate_artifact_hash"] = replay_hash({"tampered": True})
    replay_file.write_text(__import__("json").dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_platform_validation_candidate_composition_replay(tmp_path / "composition")


def test_capability_is_registered() -> None:
    capability_id = "PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["implementation_owner"].endswith("platform_validation_plan_candidate_composition_runtime")
    assert record["runtime_execution_authority"] is False


def _plan_hash(artifact: dict) -> str:
    return replay_hash(
        {
            key: deepcopy(artifact[key])
            for key in (
                "source_artifact_type",
                "platform_change_impact_reference",
                "platform_change_impact_hash",
                "platform_change_impact_artifact_hash",
                "validation_requirements",
                "allowlisted_command_references",
                "validation_allowlist_version",
                "capability_registry_version",
                "unresolved_mappings",
                "planning_status",
                "mapping_policy",
                "authority_flags",
                "failure_reason",
            )
        }
    )
