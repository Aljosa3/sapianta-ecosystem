"""Focused G29-02 semantic capability selection tests."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

import aigol.runtime.semantic_capability_selection_runtime as selection_runtime
from aigol.runtime.certified_capability_invocation_binding_runtime import (
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
    PLATFORM_VALIDATION_PLANNING,
    certified_capability_invocation_adapters,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
    platform_capability_certification_registry,
)
from aigol.runtime.platform_project_objective_inference import infer_platform_project_objective
from aigol.runtime.platform_core_project_services import discover_candidate_capabilities
from aigol.runtime.semantic_capability_selection_runtime import (
    CAPABILITY_CLARIFICATION_REQUIRED,
    CAPABILITY_SELECTED,
    FAILED_CLOSED,
    reconstruct_semantic_capability_selection_replay,
    select_semantic_capability,
    validate_semantic_capability_selection_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"
MANIFEST = "IMPLEMENTATION_MANIFEST_ARTIFACT_V1"
NORMALIZED = "NORMALIZED_CHANGE_ARTIFACT_V1"
IMPACT = "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1"


def _objective(request: str, work_type: str = "ANALYSIS") -> dict:
    return infer_platform_project_objective(
        request=request,
        development_intent={
            "requested_work_type": work_type,
            "work_type": work_type,
            "candidate_capability_discovery": {},
        },
        created_at=CREATED_AT,
    )


def _registry() -> dict:
    return platform_capability_certification_registry()


def _select(
    tmp_path,
    *,
    request: str,
    inputs: list[str],
    name: str,
    registry: dict | None = None,
    adapters: dict | None = None,
    objective: dict | None = None,
    registry_fingerprint: str | None = None,
    adapter_fingerprint: str | None = None,
) -> dict:
    objective = objective or _objective(request)
    registry = registry or _registry()
    adapters = adapters or certified_capability_invocation_adapters()
    return select_semantic_capability(
        selection_id=f"SELECTION-G29-02-{name}",
        session_id="SESSION-G29-02",
        project_objective_artifact=objective,
        project_objective_reference=f"OBJECTIVE-G29-02-{name}",
        project_objective_hash=objective["artifact_hash"],
        certification_registry_state=registry,
        certification_registry_fingerprint=(
            registry_fingerprint or replay_hash(registry)
        ),
        invocation_adapter_metadata=adapters,
        invocation_adapter_metadata_fingerprint=(
            adapter_fingerprint or replay_hash(adapters)
        ),
        available_input_artifact_types=inputs,
        replay_dir=tmp_path / name,
        created_at=CREATED_AT,
    )


@pytest.mark.parametrize(
    ("prompt", "inputs", "expected"),
    [
        (
            "Review and normalize a repository implementation change into canonical change evidence.",
            [MANIFEST],
            PLATFORM_CHANGE_NORMALIZATION,
        ),
        (
            "Analyze platform change impact for an existing normalized change artifact.",
            [NORMALIZED],
            PLATFORM_CHANGE_IMPACT_ANALYSIS,
        ),
        (
            "Review and create a validation plan from an existing platform change impact artifact.",
            [IMPACT],
            PLATFORM_VALIDATION_PLANNING,
        ),
    ],
)
def test_valid_objective_uniquely_selects_each_g28_capability(
    tmp_path, prompt: str, inputs: list[str], expected: str
) -> None:
    capture = _select(
        tmp_path,
        request=prompt,
        inputs=inputs,
        name=expected.lower(),
    )
    artifact = capture["semantic_capability_selection_artifact"]

    assert capture["selection_status"] == CAPABILITY_SELECTED
    assert capture["selected_capability_identifier"] == expected
    assert capture["ready_for_g28_invocation"] is True
    assert artifact["capability_invoked"] is False
    assert artifact["selection_treated_as_authorization"] is False
    assert validate_semantic_capability_selection_artifact(artifact) == artifact


@pytest.mark.parametrize("state", ["uncertified", "superseded"])
def test_filters_uncertified_and_superseded_capability(
    tmp_path, monkeypatch, state: str
) -> None:
    registry = _registry()
    record = registry[PLATFORM_CHANGE_IMPACT_ANALYSIS]
    if state == "uncertified":
        record["certification_status"] = "DRAFT"
    else:
        record["superseded_by"] = "REPLACEMENT_CAPABILITY"
    record.pop("certification_record_hash")
    record["certification_record_hash"] = replay_hash(record)
    monkeypatch.setattr(
        selection_runtime,
        "platform_capability_certification_registry",
        lambda: deepcopy(registry),
    )

    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name=state,
        registry=registry,
    )
    candidates = capture["semantic_capability_selection_artifact"][
        "ordered_candidate_records"
    ]
    impact = next(
        item
        for item in candidates
        if item["capability_identifier"] == PLATFORM_CHANGE_IMPACT_ANALYSIS
    )

    assert capture["selected_capability_identifier"] is None
    assert impact["admissible"] is False
    assert impact["exclusion_evidence"] == [
        "CAPABILITY_NOT_CURRENTLY_CERTIFIED"
        if state == "uncertified"
        else "CAPABILITY_SUPERSEDED"
    ]


def test_filters_capability_without_g28_adapter(tmp_path, monkeypatch) -> None:
    adapters = certified_capability_invocation_adapters()
    adapters.pop(PLATFORM_CHANGE_IMPACT_ANALYSIS)
    monkeypatch.setattr(
        selection_runtime,
        "certified_capability_invocation_adapters",
        lambda: deepcopy(adapters),
    )

    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="no-adapter",
        adapters=adapters,
    )
    candidate = next(
        item
        for item in capture["semantic_capability_selection_artifact"][
            "ordered_candidate_records"
        ]
        if item["capability_identifier"] == PLATFORM_CHANGE_IMPACT_ANALYSIS
    )

    assert candidate["admissible"] is False
    assert "G28_INVOCATION_ADAPTER_NOT_AVAILABLE" in candidate["exclusion_evidence"]


def test_invalid_objective_artifact_hash_fails_closed(tmp_path) -> None:
    objective = _objective(
        "Analyze platform change impact for an existing normalized change artifact."
    )
    objective["objective_subject"] = "tampered"

    capture = _select(
        tmp_path,
        request="unused",
        inputs=[NORMALIZED],
        name="invalid-objective",
        objective=objective,
    )

    assert capture["selection_status"] == FAILED_CLOSED
    assert "project objective artifact hash mismatch" in capture["failure_reason"]


def test_candidate_discovery_lineage_is_validated_and_preserved(tmp_path) -> None:
    prompt = "Review and create a validation plan from an existing platform change impact artifact."
    discovery = discover_candidate_capabilities(message=prompt, workspace_state=None)
    objective = infer_platform_project_objective(
        request=prompt,
        development_intent={
            "requested_work_type": "ANALYSIS",
            "work_type": "ANALYSIS",
            "candidate_capability_discovery": discovery,
        },
        created_at=CREATED_AT,
    )
    registry = _registry()
    adapters = certified_capability_invocation_adapters()

    capture = select_semantic_capability(
        selection_id="SELECTION-G29-02-DISCOVERY-LINEAGE",
        session_id="SESSION-G29-02",
        project_objective_artifact=objective,
        project_objective_reference="OBJECTIVE-G29-02-DISCOVERY-LINEAGE",
        project_objective_hash=objective["artifact_hash"],
        candidate_discovery_evidence=discovery,
        candidate_discovery_reference="DISCOVERY-G29-02",
        candidate_discovery_hash=discovery["artifact_hash"],
        certification_registry_state=registry,
        certification_registry_fingerprint=replay_hash(registry),
        invocation_adapter_metadata=adapters,
        invocation_adapter_metadata_fingerprint=replay_hash(adapters),
        available_input_artifact_types=[IMPACT],
        replay_dir=tmp_path / "discovery-lineage",
        created_at=CREATED_AT,
    )
    artifact = capture["semantic_capability_selection_artifact"]

    assert capture["selected_capability_identifier"] == PLATFORM_VALIDATION_PLANNING
    assert artifact["candidate_discovery_reference"] == "DISCOVERY-G29-02"
    assert artifact["candidate_discovery_hash"] == discovery["artifact_hash"]


@pytest.mark.parametrize("invalid", ["registry", "adapter"])
def test_invalid_registry_or_adapter_fingerprint_fails_closed(tmp_path, invalid: str) -> None:
    kwargs = {
        "registry_fingerprint": replay_hash({"invalid": "registry"})
        if invalid == "registry"
        else None,
        "adapter_fingerprint": replay_hash({"invalid": "adapter"})
        if invalid == "adapter"
        else None,
    }
    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name=f"invalid-{invalid}",
        **kwargs,
    )

    assert capture["selection_status"] == FAILED_CLOSED
    assert "fingerprint mismatch" in capture["failure_reason"]


def test_missing_semantic_descriptor_fails_closed(tmp_path, monkeypatch) -> None:
    descriptors = selection_runtime.certified_capability_semantic_descriptors()
    descriptors.pop(PLATFORM_CHANGE_IMPACT_ANALYSIS)
    monkeypatch.setattr(
        selection_runtime,
        "certified_capability_semantic_descriptors",
        lambda: deepcopy(descriptors),
    )

    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="missing-descriptor",
    )

    assert capture["selection_status"] == FAILED_CLOSED
    assert "semantic descriptor scope invalid" in capture["failure_reason"]


def test_no_admissible_candidate_produces_one_deterministic_clarification(
    tmp_path, monkeypatch
) -> None:
    registry = _registry()
    for capability_id in (
        PLATFORM_CHANGE_NORMALIZATION,
        PLATFORM_CHANGE_IMPACT_ANALYSIS,
        PLATFORM_VALIDATION_PLANNING,
    ):
        registry.pop(capability_id)
    monkeypatch.setattr(
        selection_runtime,
        "platform_capability_certification_registry",
        lambda: deepcopy(registry),
    )

    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="no-admissible",
        registry=registry,
    )
    clarification = capture["semantic_capability_clarification_artifact"]

    assert capture["selected_capability_identifier"] is None
    assert capture["fail_closed"] is True
    assert clarification["clarification_question_count"] == 1
    assert clarification["asks_exactly_one_question"] is True
    assert clarification["platform_core_owns_clarification_semantics"] is True


def test_equal_score_ambiguity_never_uses_alphabetical_tie_resolution(tmp_path) -> None:
    capture = _select(
        tmp_path,
        request="Review and prepare repository change and platform validation.",
        inputs=[MANIFEST, IMPACT],
        name="equal-score",
    )
    artifact = capture["semantic_capability_selection_artifact"]
    admissible = [
        item for item in artifact["ordered_candidate_records"] if item["admissible"]
    ]

    assert len(admissible) == 2
    assert admissible[0]["score"] == admissible[1]["score"]
    assert capture["selection_status"] == CAPABILITY_CLARIFICATION_REQUIRED
    assert capture["selected_capability_identifier"] is None
    assert capture["semantic_capability_clarification_artifact"][
        "asks_exactly_one_question"
    ] is True


def test_missing_input_semantic_slot_requires_clarification(tmp_path) -> None:
    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[],
        name="missing-input",
    )
    artifact = capture["semantic_capability_selection_artifact"]
    impact = next(
        item
        for item in artifact["ordered_candidate_records"]
        if item["capability_identifier"] == PLATFORM_CHANGE_IMPACT_ANALYSIS
    )

    assert capture["selection_status"] == CAPABILITY_CLARIFICATION_REQUIRED
    assert "input_artifact_family" in impact["unresolved_semantic_slots"]
    assert capture["semantic_capability_clarification_artifact"][
        "selected_missing_slot"
    ] == "input_artifact_family"


def test_ordering_and_scores_are_reproducible(tmp_path) -> None:
    first = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="stable-first",
    )
    second = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="stable-second",
    )
    first_records = first["semantic_capability_selection_artifact"][
        "ordered_candidate_records"
    ]
    second_records = second["semantic_capability_selection_artifact"][
        "ordered_candidate_records"
    ]

    assert first_records == second_records
    assert [item["score"] for item in first_records] == [
        item["score"] for item in second_records
    ]


def test_replay_reconstruction_and_tamper_rejection(tmp_path) -> None:
    capture = _select(
        tmp_path,
        request="Analyze platform change impact for an existing normalized change artifact.",
        inputs=[NORMALIZED],
        name="replay",
    )
    reconstructed = reconstruct_semantic_capability_selection_replay(
        tmp_path / "replay"
    )

    assert reconstructed["selected_capability_identifier"] == (
        PLATFORM_CHANGE_IMPACT_ANALYSIS
    )
    assert reconstructed["replay_artifact_count"] == 6
    assert reconstructed["capability_invoked"] is False

    path = tmp_path / "replay" / "002_semantic_scoring_evidence_recorded.json"
    wrapper = load_json(path)
    wrapper["artifact"]["ordered_candidate_scores"][0]["score"] += 1
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_semantic_capability_selection_replay(tmp_path / "replay")


def test_runtime_has_no_execution_provider_worker_mutation_or_dynamic_import_surface(
    tmp_path,
) -> None:
    capture = _select(
        tmp_path,
        request="Review and normalize a repository implementation change into canonical change evidence.",
        inputs=[MANIFEST],
        name="boundaries",
    )
    source = inspect.getsource(selection_runtime)

    assert capture["capability_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["repository_mutated"] is False
    assert capture["human_interface_authority"] is False
    assert capture["dynamic_import_used"] is False
    assert "invoke_certified_capability(" not in source
    assert "importlib" not in source
    assert "implementation_owner]" not in source


def test_capability_registration_is_governance_metadata_only() -> None:
    record = lookup_platform_capability_certification(
        "CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING"
    )

    assert record["certification_milestone"] == "G29-02"
    assert record["implementation_owner"] == (
        "aigol.runtime.semantic_capability_selection_runtime"
    )
    assert record["runtime_execution_authority"] is False
