from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime import confirmed_grounded_execution_authorization_binding as binding
from aigol.runtime import worker_selection_certification_v1 as certification
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.unified_resource_selection_runtime import (
    FAILED_CLOSED,
    RESOURCE_SELECTION_SUCCEEDED,
    WORKER_ROLE,
    _registry_hash_input,
    default_resource_registry,
    reconstruct_unified_resource_selection_replay,
    select_unified_resource,
)
from test_g31_10_confirmed_grounded_execution_authorization_binding import _authorized


WORKER_ID = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
WORKER_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
CAPABILITY = "REPLACE_EXISTING_TEXT_FILE"


def _exact_resource(registry: dict) -> dict:
    matches = [item for item in registry["resources"] if item["resource_id"] == WORKER_ID]
    assert len(matches) == 1
    return matches[0]


def _rehash_registry(registry: dict) -> dict:
    result = deepcopy(registry)
    result["registry_hash"] = replay_hash(_registry_hash_input(result))
    return result


def _select(tmp_path: Path, *, registry: dict | None = None, suffix: str = "exact", **changes) -> dict:
    arguments = {
        "selection_id": f"R08B-{suffix}",
        "workflow_type": "NATIVE_DEVELOPMENT",
        "required_capability": CAPABILITY,
        "requested_role_type": WORKER_ROLE,
        "domain_id": "NATIVE_DEVELOPMENT",
        "created_at": "2026-07-22T00:00:00Z",
        "replay_dir": tmp_path / suffix,
        "worker_authorization_required": True,
        "min_trust_level": "HIGH",
        "preferred_resource_id": WORKER_ID,
        "registry": registry or default_resource_registry(),
    }
    arguments.update(changes)
    return select_unified_resource(**arguments)


def test_exact_canonical_entry_is_certified_selectable_and_stops(tmp_path: Path) -> None:
    registry = default_resource_registry()
    resource = _exact_resource(registry)
    role = resource["role_bindings"][0]
    report = load_json(binding.WORKER_SELECTION_CERTIFICATION_PATH)

    assert resource["resource_version"] == WORKER_VERSION
    assert resource["resource_category"] == "WORKER"
    assert resource["lifecycle_status"] == "AVAILABLE"
    assert resource["trust_level"] == "HIGH"
    assert len(resource["role_bindings"]) == 1
    assert role == {
        "role_type": WORKER_ROLE,
        "role_status": "AVAILABLE",
        "capability_ids": (CAPABILITY,),
        "authority_profile": "WORKER_AUTHORIZED_TASK_ONLY",
        "domain_scope": ("NATIVE_DEVELOPMENT",),
    }
    assert report["final_verdict"] == "WORKER_SELECTION_CERTIFIED"
    assert report["resource_registry_hash"] == registry["registry_hash"]
    assert report["certified_resource_hash"] == replay_hash(resource)
    assert replay_hash(report["certified_resource"]) == replay_hash(resource)

    capture = _select(tmp_path)
    artifact = capture["resource_selection_artifact"]
    reconstructed = reconstruct_unified_resource_selection_replay(tmp_path / "exact")
    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == WORKER_ID
    assert artifact["selected_resource_version"] == WORKER_VERSION
    assert artifact["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY"
    assert artifact["registry_hash"] == registry["registry_hash"]
    assert reconstructed["replay_artifact_count"] == 2
    for field in (
        "provider_invoked", "worker_invoked", "execution_requested", "dispatch_requested",
        "authorization_created",
    ):
        assert capture[field] is False


def test_incremental_generator_preserves_prior_certification(tmp_path: Path) -> None:
    base = tmp_path / "certification"
    first = certification.run_worker_selection_certification_v1(replay_base=base)
    first_report_path = Path(first["certification_report_path"])
    first_report = load_json(first_report_path)
    first_bytes = first_report_path.read_bytes()
    second = certification.run_worker_selection_certification_v1(replay_base=base)

    assert Path(first["cert_root"]).name == "CERT-000001"
    assert Path(second["cert_root"]).name == "CERT-000002"
    assert Path(first["certification_report_path"]).read_bytes() == first_bytes
    assert first_report["final_verdict"] == "WORKER_SELECTION_CERTIFIED"
    assert first_report["scenario_results"][-1]["scenario_id"] == "WSG-008"
    assert first_report["scenario_results"][-1]["assertions"][
        "canonical_registry_selection_succeeded"
    ] is True


@pytest.mark.parametrize(
    "field,value",
    (
        ("resource_id", "SUBSTITUTED_WORKER"),
        ("resource_version", "SUBSTITUTED_VERSION"),
        ("lifecycle_status", "SUSPENDED"),
        ("trust_level", "STANDARD"),
        ("certification_evidence", ("substituted",)),
    ),
)
def test_changed_resource_identity_or_lineage_blocks_certification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value
) -> None:
    registry = default_resource_registry()
    _exact_resource(registry)[field] = value
    registry = _rehash_registry(registry)
    monkeypatch.setattr(certification, "default_resource_registry", lambda: registry)

    with pytest.raises(FailClosedRuntimeError, match="registration"):
        certification.run_worker_selection_certification_v1(replay_base=tmp_path / field)
    assert not (tmp_path / field).exists()


@pytest.mark.parametrize(
    "field,value",
    (
        ("role_type", "PROVIDER_ROLE"),
        ("role_status", "SUSPENDED"),
        ("capability_ids", ("IMPLEMENTATION_ASSISTANCE",)),
        ("authority_profile", "PROVIDER_PROPOSAL_ONLY"),
        ("domain_scope", ("GOVERNANCE",)),
    ),
)
def test_changed_role_contract_blocks_certification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value
) -> None:
    registry = default_resource_registry()
    _exact_resource(registry)["role_bindings"][0][field] = value
    registry = _rehash_registry(registry)
    monkeypatch.setattr(certification, "default_resource_registry", lambda: registry)

    with pytest.raises(FailClosedRuntimeError, match="incompatible"):
        certification.run_worker_selection_certification_v1(replay_base=tmp_path / field)
    assert not (tmp_path / field).exists()


def test_duplicate_registration_blocks_certification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = default_resource_registry()
    registry["resources"].append(deepcopy(_exact_resource(registry)))
    registry = _rehash_registry(registry)
    monkeypatch.setattr(certification, "default_resource_registry", lambda: registry)

    with pytest.raises(FailClosedRuntimeError, match="not exact"):
        certification.run_worker_selection_certification_v1(replay_base=tmp_path / "duplicate")
    assert not (tmp_path / "duplicate").exists()


@pytest.mark.parametrize(
    "changes",
    (
        {"worker_authorization_required": False},
        {"requested_role_type": "PROVIDER_ROLE"},
        {"domain_id": "GOVERNANCE"},
        {"required_capability": "IMPLEMENTATION_ASSISTANCE"},
        {"preferred_resource_id": "CODEX"},
    ),
)
def test_broadened_or_unauthorized_selection_fails_closed(
    tmp_path: Path, changes: dict
) -> None:
    capture = _select(tmp_path, suffix=str(abs(hash(repr(changes)))), **changes)
    assert capture["selection_status"] == FAILED_CLOSED
    assert capture["selected_resource_id"] is None
    assert capture["worker_invoked"] is False
    assert capture["dispatch_requested"] is False


def test_stale_registry_hash_and_ambiguous_candidate_fail_closed(tmp_path: Path) -> None:
    stale = default_resource_registry()
    stale["registry_hash"] = "sha256:" + "0" * 64
    stale_capture = _select(tmp_path, registry=stale, suffix="stale")
    assert stale_capture["selection_status"] == FAILED_CLOSED
    assert "registry hash mismatch" in stale_capture["failure_reason"]

    ambiguous = default_resource_registry()
    competitor = deepcopy(_exact_resource(ambiguous))
    competitor["resource_id"] = "COMPETING_FILESYSTEM_REPLACE_WORKER"
    ambiguous["resources"].append(competitor)
    ambiguous = _rehash_registry(ambiguous)
    capture = _select(
        tmp_path, registry=ambiguous, suffix="ambiguous", preferred_resource_id=None
    )
    assert capture["selection_status"] == FAILED_CLOSED
    assert "ambiguous" in capture["failure_reason"]


@pytest.mark.parametrize("mode", ("false_verdict", "stale_registry", "lineage"))
def test_stale_false_or_substituted_certification_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    authorization, _, _, session_root = _authorized(tmp_path, f"R08B-CERT-{mode}")
    report = load_json(binding.WORKER_SELECTION_CERTIFICATION_PATH)
    if mode == "false_verdict":
        report["final_verdict"] = "WORKER_SELECTION_GAPS_FOUND"
    elif mode == "stale_registry":
        report["resource_registry_hash"] = "sha256:" + "1" * 64
    else:
        report["certified_resource"]["certification_evidence"][0] = "substituted"
        report["certified_resource_hash"] = replay_hash(report["certified_resource"])
    report = with_replay_hash(report, hash_field="artifact_hash")
    path = tmp_path / f"{mode}.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(binding, "WORKER_SELECTION_CERTIFICATION_PATH", path)

    with pytest.raises(FailClosedRuntimeError, match="certification is not valid"):
        binding.select_authorized_grounded_worker(
            execution_authorization_capture=authorization,
            session_root=session_root,
            replay_dir=session_root / "worker-selection",
        )
    assert not (session_root / "worker-selection").exists()


@pytest.mark.parametrize("mode", ("reordered", "substituted", "duplicated", "removed"))
def test_exact_selection_replay_tampering_fails_closed(tmp_path: Path, mode: str) -> None:
    root = tmp_path / mode
    _select(tmp_path, suffix=mode)
    recorded_path = root / "000_resource_selection_recorded.json"
    returned_path = root / "001_resource_selection_returned.json"
    if mode == "reordered":
        wrapper = load_json(recorded_path)
        wrapper["replay_index"] = 1
        recorded_path.write_text(
            json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8"
        )
    elif mode == "substituted":
        wrapper = load_json(recorded_path)
        wrapper["artifact"]["selected_resource_id"] = "CODEX"
        wrapper["artifact"] = with_replay_hash(wrapper["artifact"], hash_field="artifact_hash")
        recorded_path.write_text(
            json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8"
        )
    elif mode == "duplicated":
        (root / "002_resource_selection_recorded.json").write_bytes(recorded_path.read_bytes())
    else:
        returned_path.unlink()

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_unified_resource_selection_replay(root)
