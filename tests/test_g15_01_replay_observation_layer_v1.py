from __future__ import annotations

from copy import deepcopy
import inspect
import importlib.util
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_certification_runtime import certify_validated_replay
from aigol.runtime.replay_observation_layer import (
    CERTIFICATION,
    ERROR,
    INFO,
    PROVIDER,
    REPLAY_OBSERVATION_LAYER_ARTIFACT_V1,
    REPLAY_OBSERVATION_LAYER_RECORDED,
    REPLAY_OBSERVATION_LAYER_VERSION,
    VALIDATION,
    generate_replay_observation_layer,
    observe_replay_directory,
    reconstruct_replay_observation_layer,
    replay_observation_artifact,
)
from aigol.runtime.result_validation_runtime import validate_governed_execution_result
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


CREATED_AT = "2026-07-06T00:00:00Z"


def _wrapper(index: int, step: str, artifact: dict) -> dict:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _provider_failure_artifact() -> dict:
    artifact = {
        "artifact_type": "PROVIDER_PROPOSAL_ARTIFACT_V1",
        "runtime_version": "TEST_PROVIDER_RUNTIME_V1",
        "event_type": "FAILED_CLOSED",
        "provider_id": "openai",
        "provider_status": "FAILED_CLOSED",
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": "OpenAI provider unavailable",
        "failure_diagnostics": {
            "failure_stage": "openai_http_request",
            "exception_type": "URLError",
            "transport_failure_category": "URL_ERROR",
            "http_status": None,
        },
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact() -> dict:
    artifact = {
        "artifact_type": "RESULT_VALIDATION_ARTIFACT_V1",
        "runtime_version": "AIGOL_RESULT_VALIDATION_RUNTIME_V1",
        "result_validation_id": "RESULT-VALIDATION-OBSERVATION-000001",
        "validation_status": "RESULT_VALIDATION_COMPLETED",
        "source_worker_execution": "WORKER-EXECUTION-000001",
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _load_result_validation_helper():
    helper_path = Path(__file__).with_name("test_result_validation_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("result_validation_helper_g15_01", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("result validation helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._worker_execution_result


_worker_execution_result = _load_result_validation_helper()


def _result_validation(tmp_path: Path) -> dict:
    result = _worker_execution_result(tmp_path)
    return validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-G15-OBSERVATION-000001",
        worker_execution_result_artifact=result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "result_validation",
    )["result_validation_artifact"]


def test_replay_observation_layer_classifies_provider_failure_without_invocation(tmp_path: Path) -> None:
    provider_failure = _wrapper(0, "provider_proposal_created", _provider_failure_artifact())

    capture = generate_replay_observation_layer(
        replay_identifier="REPLAY-G15-01-PROVIDER",
        source_replay_artifacts=[provider_failure],
        observed_at=CREATED_AT,
        replay_dir=tmp_path / "observations",
    )
    observation = capture["replay_observation_layer_artifact"]["observations"][0]

    assert capture["runtime_version"] == REPLAY_OBSERVATION_LAYER_VERSION
    assert capture["observation_layer_status"] == REPLAY_OBSERVATION_LAYER_RECORDED
    assert capture["replay_observation_layer_artifact"]["artifact_type"] == REPLAY_OBSERVATION_LAYER_ARTIFACT_V1
    assert observation["observation_category"] == PROVIDER
    assert observation["severity"] == ERROR
    assert observation["originating_component"] == "PROVIDER_PLATFORM"
    assert "OpenAI provider unavailable" in observation["deterministic_message"]
    assert observation["provider_invoked"] is False
    assert observation["worker_invoked"] is False
    assert observation["improvement_proposal_created"] is False
    assert observation["autonomous_decision_created"] is False


def test_replay_observation_layer_is_deterministic_and_reconstructable(tmp_path: Path) -> None:
    validation = _wrapper(1, "result_validation_artifact_recorded", _validation_artifact())

    first = generate_replay_observation_layer(
        replay_identifier="REPLAY-G15-01-DETERMINISTIC",
        source_replay_artifacts=[validation],
        observed_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = generate_replay_observation_layer(
        replay_identifier="REPLAY-G15-01-DETERMINISTIC",
        source_replay_artifacts=[validation],
        observed_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )
    reconstructed = reconstruct_replay_observation_layer(tmp_path / "first")

    assert (
        first["replay_observation_layer_artifact"]["observations"]
        == second["replay_observation_layer_artifact"]["observations"]
    )
    assert reconstructed["observation_count"] == 1
    assert reconstructed["category_counts"][VALIDATION] == 1
    assert reconstructed["severity_counts"][INFO] == 1
    assert reconstructed["read_only_interpretation"] is True
    assert reconstructed["source_replay_modified"] is False


def test_observe_replay_directory_reads_existing_replay_without_mutating_it(tmp_path: Path) -> None:
    source_dir = tmp_path / "source_replay"
    source_wrapper = _wrapper(0, "result_validation_artifact_recorded", _validation_artifact())
    write_json_immutable(source_dir / "001_result_validation_artifact_recorded.json", source_wrapper)
    before = (source_dir / "001_result_validation_artifact_recorded.json").read_text(encoding="utf-8")

    capture = observe_replay_directory(
        replay_identifier="REPLAY-G15-01-DIRECTORY",
        source_replay_dir=source_dir,
        observed_at=CREATED_AT,
        replay_dir=tmp_path / "observations",
    )
    after = (source_dir / "001_result_validation_artifact_recorded.json").read_text(encoding="utf-8")

    assert before == after
    assert capture["category_counts"][VALIDATION] == 1
    assert (tmp_path / "observations" / "000_replay_observation_layer_recorded.json").exists()


def test_replay_observation_layer_fails_closed_for_reused_observation_replay_dir(tmp_path: Path) -> None:
    validation = _wrapper(1, "result_validation_artifact_recorded", _validation_artifact())
    replay_dir = tmp_path / "observations"
    generate_replay_observation_layer(
        replay_identifier="REPLAY-G15-01-APPEND-ONLY",
        source_replay_artifacts=[validation],
        observed_at=CREATED_AT,
        replay_dir=replay_dir,
    )

    with pytest.raises(FailClosedRuntimeError, match="replay already exists"):
        generate_replay_observation_layer(
            replay_identifier="REPLAY-G15-01-APPEND-ONLY",
            source_replay_artifacts=[validation],
            observed_at=CREATED_AT,
            replay_dir=replay_dir,
        )


def test_replay_observation_reconstruction_detects_corruption(tmp_path: Path) -> None:
    validation = _wrapper(1, "result_validation_artifact_recorded", _validation_artifact())
    replay_dir = tmp_path / "observations"
    generate_replay_observation_layer(
        replay_identifier="REPLAY-G15-01-CORRUPT",
        source_replay_artifacts=[validation],
        observed_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    path = replay_dir / "000_replay_observation_layer_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["observations"][0]["severity"] = ERROR
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_observation_layer(replay_dir)


def test_replay_certification_generates_observation_layer_before_certification(tmp_path: Path) -> None:
    validation = _result_validation(tmp_path)

    capture = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-G15-OBSERVATION-000001",
        result_validation_artifact=validation,
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "replay_certification",
    )
    certification = capture["replay_certification_artifact"]
    observation_reconstruction = reconstruct_replay_observation_layer(
        tmp_path / "replay_certification" / "replay_observation_layer"
    )

    assert certification["replay_observation_generation_authority"] == "PLATFORM_CORE"
    assert certification["replay_observation_count"] == 2
    assert certification["replay_observation_layer_hash"].startswith("sha256:")
    assert capture["replay_observation_count"] == 2
    assert observation_reconstruction["category_counts"][VALIDATION] == 2
    assert observation_reconstruction["provider_invoked"] is False
    assert observation_reconstruction["worker_invoked"] is False


def test_replay_observation_layer_has_no_execution_provider_or_proposal_surfaces() -> None:
    import aigol.runtime.replay_observation_layer as observation_layer

    source = inspect.getsource(observation_layer)
    sample = replay_observation_artifact(
        replay_identifier="REPLAY-G15-01-SURFACE",
        source_replay_artifact=_wrapper(0, "certification", {"certification_status": "CERTIFIED"}),
        observed_at=CREATED_AT,
        sequence=0,
    )

    assert sample["observation_category"] == CERTIFICATION
    assert sample["improvement_proposal_created"] is False
    assert sample["autonomous_decision_created"] is False
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "OpenAIProviderAdapter" not in source
    assert "run_certified_provider_attachment" not in source
    assert "invoke_worker" not in source
    assert "execute_worker" not in source
