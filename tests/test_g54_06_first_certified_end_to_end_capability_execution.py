"""Certification tests for the G54-06 first full capability execution."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.cli.aigol_cli import (
    build_parser,
    return_platform_change_normalization_completion_to_acli,
    run_command,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_runtime import EXECUTING, reconstruct_execution_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
    reconstruct_platform_change_normalization_execution_binding_replay,
)
from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
    FAILED_CLOSED,
    WORKER_CAPABILITY_COMPLETED,
    complete_platform_change_normalization_worker_capability,
    reconstruct_platform_change_normalization_worker_completion_replay,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_INVOCATION_REQUEST_CREATED,
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_result_capture_runtime import (
    WORKER_RESULT_CAPTURED,
    reconstruct_worker_result_capture_replay,
)
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    reconstruct_worker_result_validation_replay,
)
import test_g54_05_platform_change_normalization_worker_completion_adapter as g54_05


def _run_aicli_ingress(tmp_path, *, include_manifest: bool = True) -> dict:
    arguments = [
        "next",
        "--session-id",
        "SESSION-G54-06-INGRESS",
        "--prompt",
        g54_05.REQUEST,
        "--created-at",
        g54_05.CREATED_AT,
        "--runtime-root",
        str(tmp_path / "aicli_ingress"),
        "--workspace",
        str(tmp_path),
        "--json",
    ]
    if include_manifest:
        manifest = g54_05._manifest(tmp_path / "manifest_source")
        arguments.extend(
            ["--canonical-artifact-json", json.dumps(manifest, sort_keys=True)]
        )
    return run_command(build_parser().parse_args(arguments))


def test_first_capability_executes_and_reconstructs_through_the_complete_path(
    tmp_path,
) -> None:
    ingress = _run_aicli_ingress(tmp_path)
    governed_work = ingress["governed_read_only_work_result"]
    route = governed_work["semantic_capability_runtime_route"]
    route_replay = reconstruct_project_context_semantic_capability_route(
        route["replay_reference"]
    )
    repeated_route = _run_aicli_ingress(tmp_path / "repeated")[
        "governed_read_only_work_result"
    ]["semantic_capability_runtime_route"]

    completion_inputs, trace = g54_05._completion_inputs(
        tmp_path / "execution_path",
        semantic_route=route,
        semantic_route_replay_reference=route["replay_reference"],
        include_trace=True,
    )
    completion = complete_platform_change_normalization_worker_capability(
        **completion_inputs
    )
    aicli_return = return_platform_change_normalization_completion_to_acli(
        session_id="SESSION-G54-06-RETURN",
        human_request=g54_05.REQUEST,
        created_at=g54_05.CREATED_AT,
        replay_dir=tmp_path / "aicli_return",
        workspace=str(tmp_path),
        worker_capability_completion_capture=completion,
    )

    reconstructed = {
        "binding": reconstruct_platform_change_normalization_execution_binding_replay(
            trace["binding"]["capability_execution_binding_replay_reference"]
        ),
        "authorization": reconstruct_execution_authorization_replay(
            trace["authorization"]["execution_authorization_replay_reference"]
        ),
        "request": reconstruct_worker_invocation_request_replay(
            trace["request"]["worker_invocation_request_replay_reference"]
        ),
        "assignment": reconstruct_worker_assignment_runtime_replay(
            trace["assignment"]["worker_assignment_replay_reference"]
        ),
        "dispatch": reconstruct_worker_dispatch_replay(
            trace["dispatch"]["worker_dispatch_replay_reference"]
        ),
        "invocation": reconstruct_worker_invocation_replay(
            trace["invocation"]["worker_invocation_replay_reference"]
        ),
        "execution": reconstruct_execution_replay(tmp_path / "execution_path" / "execution"),
        "capture": reconstruct_worker_result_capture_replay(
            trace["capture"]["worker_result_capture_replay_reference"]
        ),
        "validation": reconstruct_worker_result_validation_replay(
            trace["validation"]["worker_result_validation_replay_reference"]
        ),
        "completion": reconstruct_platform_change_normalization_worker_completion_replay(
            completion["worker_capability_completion_replay_reference"]
        ),
    }

    assert governed_work["original_message"] == g54_05.REQUEST
    assert governed_work["selected_capability_identifier"] == "PLATFORM_CHANGE_NORMALIZATION"
    assert route["route_status"] == ROUTE_COMPLETED
    assert route["selection_treated_as_authorization"] is False
    assert route_replay["artifact_hash"] == route["artifact_hash"]
    assert repeated_route["selected_capability_identifier"] == route[
        "selected_capability_identifier"
    ]
    assert repeated_route["selection_hash"] == route["selection_hash"]
    assert repeated_route["bound_canonical_artifact_hash"] == route[
        "bound_canonical_artifact_hash"
    ]
    assert reconstructed["binding"]["binding_status"] == (
        CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION
    )
    assert reconstructed["authorization"]["authorization_status"] == EXECUTION_AUTHORIZED
    assert reconstructed["request"]["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert reconstructed["assignment"]["assignment_status"] == WORKER_ASSIGNED
    assert reconstructed["dispatch"]["dispatch_status"] == WORKER_DISPATCHED
    assert reconstructed["invocation"]["invocation_status"] == WORKER_INVOKED
    assert reconstructed["execution"]["execution_status"] == EXECUTING
    assert reconstructed["capture"]["result_capture_status"] == WORKER_RESULT_CAPTURED
    assert reconstructed["validation"]["validation_status"] == RESULT_VALIDATED
    assert reconstructed["completion"]["completion_status"] == WORKER_CAPABILITY_COMPLETED
    assert completion["completion_status"] == WORKER_CAPABILITY_COMPLETED
    assert aicli_return["human_interface_completion_returned"] is True
    assert aicli_return["acli_capability_completion_returned"] is True
    assert aicli_return["human_visible_completion_result"] == completion["human_visible_result"]
    assert aicli_return["acli_next_runtime_authorizes"] is False
    assert aicli_return["acli_next_runtime_executes"] is False


def test_aicli_ingress_fails_closed_without_required_canonical_evidence(
    tmp_path,
) -> None:
    ingress = _run_aicli_ingress(tmp_path, include_manifest=False)
    governed_work = ingress["governed_read_only_work_result"]

    assert governed_work["selected_capability_identifier"] is None
    assert governed_work["failure_reason"] == "NO_SEMANTICALLY_ADMISSIBLE_CAPABILITY"
    assert governed_work["worker_invoked"] is False
    assert governed_work["runtime_implementation_invoked"] is False


def test_aicli_ingress_rejects_malformed_canonical_artifact_json(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "next",
            "--session-id",
            "SESSION-G54-06-INVALID",
            "--prompt",
            g54_05.REQUEST,
            "--canonical-artifact-json",
            "[]",
            "--runtime-root",
            str(tmp_path),
        ]
    )

    with pytest.raises(FailClosedRuntimeError, match="must be a JSON object"):
        run_command(args)


def test_end_to_end_completion_rejects_substituted_worker_evidence(tmp_path) -> None:
    ingress = _run_aicli_ingress(tmp_path)
    route = ingress["governed_read_only_work_result"][
        "semantic_capability_runtime_route"
    ]
    completion_inputs = g54_05._completion_inputs(
        tmp_path / "execution_path",
        semantic_route=route,
        semantic_route_replay_reference=route["replay_reference"],
    )
    substituted = deepcopy(completion_inputs["worker_completion_evidence"])
    substituted["payload"]["normalized_change_artifact_hash"] = replay_hash(
        {"substitution": "G54-06"}
    )
    substituted["artifact_hash"] = replay_hash(
        {key: value for key, value in substituted.items() if key != "artifact_hash"}
    )
    completion_inputs["worker_completion_evidence"] = substituted
    completion_inputs["replay_dir"] = tmp_path / "substituted_completion"

    completion = complete_platform_change_normalization_worker_capability(
        **completion_inputs
    )

    assert completion["completion_status"] == FAILED_CLOSED
    assert completion["human_visible_result"] is None
