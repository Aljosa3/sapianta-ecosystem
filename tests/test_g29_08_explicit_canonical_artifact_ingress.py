"""Focused G29-08 explicit canonical artifact ingress tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
    INGRESS_COMPLETED,
    INGRESS_FAILED_CLOSED,
    link_explicit_canonical_artifact_ingress,
    reconstruct_explicit_canonical_artifact_ingress,
    run_explicit_canonical_artifact_ingress,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-14T00:00:00Z"
NORMALIZE_REQUEST = (
    "work_type: analysis. Review and normalize a repository implementation "
    "change into canonical change evidence."
)


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest_reference(tmp_path: Path, name: str = "ONE") -> Path:
    replay_dir = tmp_path / f"manifest-{name}"
    create_implementation_manifest(
        manifest_id=f"MANIFEST-G29-08-{name}",
        canonical_chain_id=f"CHAIN-G29-08-{name}",
        implementation_bundle_id=f"G29_08_INGRESS_{name}",
        source_candidate_reference=f"CANDIDATE-G29-08-{name}",
        source_candidate_hash=_hash(f"candidate-{name}"),
        implementation_handoff_reference=f"HANDOFF-G29-08-{name}",
        implementation_handoff_hash=_hash(f"handoff-{name}"),
        provider_generation_authorization_reference=f"AUTH-G29-08-{name}",
        provider_generation_authorization_hash=_hash(f"authorization-{name}"),
        provider_response_reference=f"RESPONSE-G29-08-{name}",
        provider_response_hash=_hash(f"response-{name}"),
        target_domain="PLATFORM_CORE",
        target_resource="EXPLICIT_CANONICAL_ARTIFACT_INGRESS",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G29-08-{name}",
                "target_path": f"bounded/ingress_{name.lower()}.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    return replay_dir / "000_implementation_manifest_recorded.json"


def _run(tmp_path: Path, references, name: str = "ingress") -> dict:
    return run_explicit_canonical_artifact_ingress(
        ingress_id=f"G29-08-{name}",
        session_id="SESSION-G29-08",
        opaque_artifact_references=references,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def _rewrite(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def test_successful_ingress_validates_and_snapshots_artifact(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    capture = _run(tmp_path, [str(reference)])

    assert capture["ingress_status"] == INGRESS_COMPLETED
    assert len(capture["validated_canonical_artifacts"]) == 1
    artifact = capture["validated_canonical_artifacts"][0]
    assert artifact["artifact_type"] == "IMPLEMENTATION_MANIFEST_ARTIFACT_V1"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["repository_mutated"] is False


def test_missing_reference_fails_closed(tmp_path: Path) -> None:
    capture = _run(tmp_path, ["missing/wrapper.json"])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "missing" in capture["failure_reason"]


def test_malformed_wrapper_fails_closed(tmp_path: Path) -> None:
    reference = tmp_path / "malformed.json"
    _rewrite(reference, {"artifact": {}})
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "wrapper" in capture["failure_reason"]


def test_unsupported_artifact_type_fails_closed(tmp_path: Path) -> None:
    artifact = {"artifact_type": "UNSUPPORTED_ARTIFACT_V1", "replay_visible": True}
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {"replay_index": 0, "replay_step": "unsupported", "artifact": artifact}
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    reference = tmp_path / "unsupported.json"
    _rewrite(reference, wrapper)
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "unsupported artifact type" in capture["failure_reason"]


def test_artifact_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    wrapper = json.loads(reference.read_text(encoding="utf-8"))
    wrapper["artifact"]["manifest_id"] = "TAMPERED"
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    _rewrite(reference, wrapper)
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "artifact hash mismatch" in capture["failure_reason"]


def test_wrapper_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    wrapper = json.loads(reference.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "tampered"
    _rewrite(reference, wrapper)
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "wrapper hash mismatch" in capture["failure_reason"]


def test_pinned_wrapper_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    capture = _run(
        tmp_path,
        [
            {
                "artifact_reference": str(reference),
                "expected_wrapper_hash": _hash("wrong-wrapper"),
            }
        ],
    )
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "wrapper hash mismatch" in capture["failure_reason"]


def test_duplicate_reference_fails_closed(tmp_path: Path) -> None:
    reference = str(_manifest_reference(tmp_path))
    capture = _run(tmp_path, [reference, reference])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "duplicate reference" in capture["failure_reason"]


def test_path_traversal_fails_closed(tmp_path: Path) -> None:
    capture = _run(tmp_path, ["../outside.json"])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "path traversal" in capture["failure_reason"]


def test_symlink_escape_fails_closed(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside.json"
    outside.write_text("{}", encoding="utf-8")
    reference = tmp_path / "escape.json"
    reference.symlink_to(outside)
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "outside allowed roots" in capture["failure_reason"] or "symlink" in capture["failure_reason"]


def test_mutable_manifest_declaration_fails_closed(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    wrapper = json.loads(reference.read_text(encoding="utf-8"))
    artifact = wrapper["artifact"]
    artifact["read_only"] = False
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    _rewrite(reference, wrapper)
    capture = _run(tmp_path, [str(reference)])
    assert capture["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "mutable manifest" in capture["failure_reason"]


def test_replay_reconstruction_verifies_ingress_chain(tmp_path: Path) -> None:
    capture = _run(tmp_path, [str(_manifest_reference(tmp_path))])
    resolution = capture["explicit_canonical_artifact_ingress_artifact"]
    context = {
        "artifact_type": "UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1",
        "replay_visible": True,
        "explicit_canonical_artifact_ingress": deepcopy(resolution),
        "explicit_canonical_artifact_ingress_reference": capture["replay_reference"],
    }
    context["artifact_hash"] = replay_hash(context)
    context_path = tmp_path / "project-context.json"
    _rewrite(context_path, context)
    link_explicit_canonical_artifact_ingress(
        replay_dir=capture["replay_reference"],
        project_context_reference=str(context_path),
        project_context_hash=context["artifact_hash"],
        downstream_route_reference=None,
        downstream_route_hash=None,
        downstream_route_status=None,
    )
    reconstructed = reconstruct_explicit_canonical_artifact_ingress(
        capture["replay_reference"]
    )
    assert reconstructed["ingress_status"] == INGRESS_COMPLETED
    assert reconstructed["project_context_hash"] == context["artifact_hash"]
    assert reconstructed["downstream_route_hash"] is None
    assert resolution["artifact_hash"]


def test_project_context_composes_ingress_with_existing_g29_06(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="SESSION-G29-08-CONTEXT",
        message=NORMALIZE_REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        explicit_canonical_artifact_references=[str(reference)],
    )

    ingress = context["explicit_canonical_artifact_ingress"]
    route = context["semantic_capability_runtime_route"]
    assert ingress["ingress_status"] == INGRESS_COMPLETED
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert route["bound_canonical_artifact_hash"] == ingress["resolved_artifacts"][0][
        "canonical_artifact_hash"
    ]
    reconstructed = reconstruct_explicit_canonical_artifact_ingress(
        context["explicit_canonical_artifact_ingress_reference"]
    )
    assert reconstructed["project_context_hash"] == context["artifact_hash"]
    assert reconstructed["downstream_route_hash"] == route["artifact_hash"]


def test_aicli_only_transports_reference_and_renders_platform_result(tmp_path: Path) -> None:
    reference = _manifest_reference(tmp_path)
    lines = iter([NORMALIZE_REQUEST, "/send", "/exit"])
    output: list[str] = []
    result = run_reference_uhi_session(
        session_id="SESSION-G29-08-AICLI",
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        artifact_references=[str(reference)],
        input_reader=lambda _: next(lines),
        output_writer=output.append,
    )

    assert "PRESENTATION_READY" in "\n".join(output)
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["provider_platform_preserved"] is True
    assert result["worker_platform_preserved"] is True


def test_reconstruction_rejects_tampered_ingress_replay(tmp_path: Path) -> None:
    capture = _run(tmp_path, [str(_manifest_reference(tmp_path))])
    context = {"artifact_type": "TEST_PROJECT_CONTEXT", "replay_visible": True}
    context["explicit_canonical_artifact_ingress"] = deepcopy(
        capture["explicit_canonical_artifact_ingress_artifact"]
    )
    context["explicit_canonical_artifact_ingress_reference"] = capture[
        "replay_reference"
    ]
    context["artifact_hash"] = replay_hash(context)
    context_path = tmp_path / "tamper-project-context.json"
    _rewrite(context_path, context)
    link_explicit_canonical_artifact_ingress(
        replay_dir=capture["replay_reference"],
        project_context_reference=str(context_path),
        project_context_hash=context["artifact_hash"],
        downstream_route_reference=None,
        downstream_route_hash=None,
        downstream_route_status=None,
    )
    resolution_path = Path(capture["replay_reference"]) / (
        "001_explicit_artifact_ingress_resolved.json"
    )
    wrapper = json.loads(resolution_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["resolved_artifact_count"] = 99
    _rewrite(resolution_path, wrapper)

    try:
        reconstruct_explicit_canonical_artifact_ingress(capture["replay_reference"])
    except Exception as exc:
        assert "wrapper" in str(exc).lower()
    else:
        raise AssertionError("tampered ingress Replay was accepted")
