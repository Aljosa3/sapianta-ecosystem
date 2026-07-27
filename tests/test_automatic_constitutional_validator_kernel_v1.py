from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path

import pytest

from aigol.constitutional_validator_kernel import (
    ValidationStatus,
    ValidationTrustAnchors,
    validate_constitutional_evidence,
)
from aigol.constitutional_validator_kernel.canonical import canonical_hash
from aigol.constitutional_validator_kernel.rules import evaluate_rule
from aigol.runtime.constitutional_validator_replay import (
    record_constitutional_validator_result,
    reconstruct_constitutional_validator_replay,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / ".github/governance/specs/CERTIFIED_FILESYSTEM_ADAPTER_EXECUTABLE_CONSTITUTIONAL_CONTRACT_V1.json"
)
MANIFEST_SPECIFICATION_PATH = (
    ROOT
    / ".github/governance/specs/IMMUTABLE_CONSTITUTIONAL_EVIDENCE_MANIFEST_V1.json"
)


def _hashed(value: dict, field: str) -> dict:
    result = deepcopy(value)
    result.pop(field, None)
    result[field] = canonical_hash(result)
    return result


def _artifact(artifact_type: str, fields: dict) -> dict:
    return _hashed(
        {
            "artifact_type": artifact_type,
            "artifact_version": "1.0.0",
            **fields,
        },
        "artifact_hash",
    )


def _wrapper(reference: str, artifact_hash: str) -> dict:
    return _hashed(
        {
            "artifact_type": "IMMUTABLE_EVIDENCE_WRAPPER_V1",
            "artifact_reference": reference,
            "artifact_hash": artifact_hash,
        },
        "wrapper_hash",
    )


def _replay(reference: str, artifact_hash: str) -> dict:
    return _hashed(
        {
            "artifact_type": "IMMUTABLE_REPLAY_REFERENCE_V1",
            "artifact_reference": reference,
            "artifact_hash": artifact_hash,
        },
        "replay_hash",
    )


def _certified_filesystem_inputs() -> tuple[
    dict,
    dict,
    dict[str, dict],
    ValidationTrustAnchors,
]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    specification = json.loads(MANIFEST_SPECIFICATION_PATH.read_text(encoding="utf-8"))
    profile = specification["filesystem_evidence_profile"]
    contract_hash = contract["contract_hash"]
    authorization_reference = "evidence/external/authorization.json"
    authorization = _artifact(
        "AUTHENTICATED_AUTHORIZATION_LINEAGE_V1",
        {
            "authorization_id": "AUTH-FILESYSTEM-001",
            "chain_id": "CHAIN-FILESYSTEM-001",
            "session_id": "SESSION-FILESYSTEM-001",
        },
    )

    profile_artifact = _artifact(
        "CERTIFIED_FILESYSTEM_ADAPTER_CONSTITUTIONAL_PROFILE_V1",
        {
            "adapter_terminates_execution": False,
            "constitutional_owners_unchanged": True,
            "context_manager_routing_present": False,
            "cross_family_evidence_rejected": True,
            "cross_session_evidence_rejected": True,
            "deterministic_replay_preserved": True,
            "duplicate_certification_rejected": True,
            "duplicate_lifecycle_evidence_rejected": True,
            "future_worker_adapter_binding_supported": True,
            "generic_platform_core_unchanged": True,
            "generic_replay_review_unchanged": True,
            "historical_compatibility_preserved": True,
            "incomplete_evidence_rejected": True,
            "inconsistent_commitments_rejected": True,
            "independent_reconstruction_preserved": True,
            "invocation_scoped_dependencies": True,
            "mutable_globals_present": False,
            "production_orchestration_binds_dependencies": True,
            "reconstructor_invocation_scoped": True,
            "resolver_registry_present": False,
            "routing_state_present": False,
            "substituted_evidence_rejected": True,
            "unsupported_schema_rejected": True,
        },
    )
    selection = _artifact(
        "WORKER_SELECTION_LINEAGE_PROJECTION_V1",
        {
            "allowed_outputs": ["operation", "result", "target"],
            "artifact_type": "WORKER_SELECTION_LINEAGE_PROJECTION_V1",
            "authorization_hash": authorization["artifact_hash"],
            "authorization_reference": authorization_reference,
            "authority_flags": {
                "assigns_workers": False,
                "authorizes_execution": False,
                "dispatches_workers": False,
                "executes_commands": False,
                "invokes_providers": False,
                "invokes_workers": False,
                "mutates_governance": False,
                "mutates_replay": False,
                "mutates_repository": False,
                "selects_workers": False,
            },
            "chain_id": "CHAIN-FILESYSTEM-001",
            "execution_packet_hash": "sha256:" + ("1" * 64),
            "selected_authority_profile": "WORKER_AUTHORIZED_TASK_ONLY",
            "source_lineage": {
                "authorization_reference": authorization_reference,
                "worker_family": "FILESYSTEM",
            },
            "source_lineage_hash": "sha256:" + ("2" * 64),
        },
    )
    assignment = _artifact(
        "WORKER_ASSIGNMENT_ARTIFACT_V1",
        {
            "authorization_hash": authorization["artifact_hash"],
            "canonical_chain_id": "CHAIN-FILESYSTEM-001",
            "selected_worker_identity": "CODEX",
        },
    )
    invocation = _artifact(
        "WORKER_INVOCATION_ARTIFACT_V1",
        {
            "chain_id": "CHAIN-FILESYSTEM-001",
            "worker_assignment_hash": assignment["artifact_hash"],
        },
    )
    output = _artifact(
        "FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1",
        {
            "authorization_reference": authorization_reference,
            "chain_id": "CHAIN-FILESYSTEM-001",
            "produced_outputs": ["operation", "result", "target"],
            "replay_visible": True,
        },
    )
    capture = _artifact(
        "WORKER_RESULT_CAPTURE_ARTIFACT_V1",
        {
            "chain_id": "CHAIN-FILESYSTEM-001",
            "worker_output_hash": output["artifact_hash"],
        },
    )
    validation = _artifact(
        "WORKER_RESULT_VALIDATION_ARTIFACT_V1",
        {
            "authorization_hash": authorization["artifact_hash"],
            "authorization_reference": authorization_reference,
            "chain_id": "CHAIN-FILESYSTEM-001",
            "worker_assignment_hash": assignment["artifact_hash"],
            "worker_invocation_hash": invocation["artifact_hash"],
            "worker_result_capture_hash": capture["artifact_hash"],
        },
    )
    review = _artifact(
        "POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1",
        {
            "authority_integrity_assessment": "INTEGRITY_VERIFIED",
            "chain_id": "CHAIN-FILESYSTEM-001",
            "replay_integrity_assessment": "INTEGRITY_VERIFIED",
            "replay_visible": True,
            "validation_integrity_assessment": "INTEGRITY_VERIFIED",
            "worker_result_validation_hash": validation["artifact_hash"],
        },
    )
    termination = _artifact(
        "GOVERNED_TERMINATION_ARTIFACT_V1",
        {
            "chain_id": "CHAIN-FILESYSTEM-001",
            "post_execution_replay_review_hash": review["artifact_hash"],
            "replay_visible": True,
            "terminated_by": "AIGOL_GOVERNANCE",
        },
    )
    certification = _artifact(
        "REPLAY_CERTIFICATION_ARTIFACT_V1",
        {
            "certification_status": "REPLAY_CERTIFICATION_COMPLETED",
            "certified_by": "AIGOL_GOVERNANCE",
            "replay_lineage_preserved": True,
        },
    )

    artifacts = {
        "ADAPTER_PROFILE": profile_artifact,
        "WORKER_SELECTION_LINEAGE": selection,
        "WORKER_ASSIGNMENT": assignment,
        "WORKER_INVOCATION": invocation,
        "WORKER_OUTPUT": output,
        "RESULT_CAPTURE": capture,
        "RESULT_VALIDATION": validation,
        "REPLAY_REVIEW": review,
        "GOVERNED_TERMINATION": termination,
        "FINAL_CERTIFICATION": certification,
    }
    evidence_sources: dict[str, dict] = {authorization_reference: authorization}
    records: list[dict] = []
    previous_reference = ""
    previous_hash = ""
    for profile_record in profile["records"]:
        evidence_id = profile_record["evidence_id"]
        artifact = artifacts[evidence_id]
        reference = f"evidence/filesystem/{evidence_id.lower()}.json"
        evidence_sources[reference] = artifact
        if evidence_id == "ADAPTER_PROFILE":
            lineage_reference = specification["contract_binding"]["contract_reference"]
            lineage_hash = contract_hash
            relationship = "AUTHENTICATES"
        elif evidence_id == "WORKER_SELECTION_LINEAGE":
            lineage_reference = authorization_reference
            lineage_hash = authorization["artifact_hash"]
            relationship = "AUTHENTICATES"
        else:
            lineage_reference = previous_reference
            lineage_hash = previous_hash
            relationship = "CERTIFIES" if evidence_id == "FINAL_CERTIFICATION" else "CONTINUES"

        record = {
            "record_type": profile_record["record_type"],
            "evidence_id": evidence_id,
            "evidence_type": profile_record["evidence_type"],
            "evidence_class": profile_record["evidence_class"],
            "constitutional_owner": profile_record["constitutional_owner"],
            "authority_effect": profile_record["authority_effect"],
            "artifact_reference": reference,
            "artifact_hash": artifact["artifact_hash"],
            "artifact_version": "1.0.0",
            "lineage_commitments": [
                {
                    "lineage_id": f"LINEAGE-{evidence_id}",
                    "artifact_reference": lineage_reference,
                    "artifact_hash": lineage_hash,
                    "relationship": relationship,
                }
            ],
            "replay_binding": {
                "mode": profile_record["replay_binding"],
                "replay_visible": profile_record["replay_binding"] != "NOT_APPLICABLE",
                "replay_owner": "PLATFORM_CORE_REPLAY",
            },
        }
        if profile_record["record_type"] == "LIFECYCLE_EVIDENCE_RECORD_V1":
            record.update(
                {
                    "invocation_id": "INVOCATION-FILESYSTEM-001",
                    "session_id": "SESSION-FILESYSTEM-001",
                    "chain_id": "CHAIN-FILESYSTEM-001",
                }
            )
        elif profile_record["record_type"] == "CERTIFICATION_EVIDENCE_RECORD_V1":
            record.update(
                {
                    "invocation_id": "INVOCATION-FILESYSTEM-001",
                    "session_id": "SESSION-FILESYSTEM-001",
                    "derived_chain_id": "CHAIN-FILESYSTEM-001",
                }
            )
        if profile_record["wrapper_hash"] == "REQUIRED":
            wrapper_reference = f"evidence/filesystem/wrappers/{evidence_id.lower()}.json"
            wrapper = _wrapper(reference, artifact["artifact_hash"])
            evidence_sources[wrapper_reference] = wrapper
            record["wrapper_reference"] = wrapper_reference
            record["wrapper_hash"] = wrapper["wrapper_hash"]
        if profile_record["replay_binding"] in {
            "REQUIRED_REFERENCE",
            "DERIVED_REQUIRED_REFERENCE",
        }:
            replay_reference = f"evidence/filesystem/replay/{evidence_id.lower()}.json"
            replay = _replay(reference, artifact["artifact_hash"])
            evidence_sources[replay_reference] = replay
            record["replay_reference"] = replay_reference
            record["replay_hash"] = replay["replay_hash"]
        records.append(record)
        previous_reference = reference
        previous_hash = artifact["artifact_hash"]

    manifest = _hashed(
        {
            "artifact_type": "IMMUTABLE_CONSTITUTIONAL_EVIDENCE_MANIFEST_V1",
            "schema_id": "ICEM_V1",
            "schema_version": "1.0.0",
            "manifest_id": "FILESYSTEM-CONSTITUTIONAL-EVIDENCE-MANIFEST-001",
            "manifest_version": "1.0.0",
            "constitutional_version": "V31",
            "contract_binding": {
                "contract_reference": specification["contract_binding"]["contract_reference"],
                "contract_id": contract["contract_id"],
                "contract_version": contract["contract_version"],
                "contract_schema_id": contract["schema_id"],
                "contract_schema_version": contract["schema_version"],
                "contract_hash": contract_hash,
            },
            "validation_context": {
                "validation_id": "VALIDATION-FILESYSTEM-001",
                "validation_scope": "COMPLETE_CERTIFIED_FILESYSTEM_ADAPTER_LIFECYCLE",
                "invocation_id": "INVOCATION-FILESYSTEM-001",
                "session_id": "SESSION-FILESYSTEM-001",
                "chain_id": "CHAIN-FILESYSTEM-001",
                "platform_core_version": "V31",
                "adapter_id": "FILESYSTEM_ADAPTER",
                "adapter_version": "1.0.0",
            },
            "evidence_order": list(profile["evidence_order"]),
            "evidence_records": records,
        },
        "manifest_hash",
    )
    anchors = ValidationTrustAnchors(
        contract_id=contract["contract_id"],
        contract_hash=contract_hash,
        manifest_id=manifest["manifest_id"],
        manifest_hash=manifest["manifest_hash"],
    )
    return contract, manifest, evidence_sources, anchors


def _validate(inputs: tuple[dict, dict, dict[str, dict], ValidationTrustAnchors]):
    contract, manifest, evidence, anchors = inputs
    return validate_constitutional_evidence(
        contract_source=contract,
        manifest_source=manifest,
        evidence_sources=evidence,
        trust_anchors=anchors,
    )


def _rehash_manifest(manifest: dict) -> ValidationTrustAnchors:
    manifest.pop("manifest_hash", None)
    manifest["manifest_hash"] = canonical_hash(manifest)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return ValidationTrustAnchors(
        contract_id=contract["contract_id"],
        contract_hash=contract["contract_hash"],
        manifest_id=manifest["manifest_id"],
        manifest_hash=manifest["manifest_hash"],
    )


def test_certified_filesystem_ecc_and_manifest_pass_all_requirements_deterministically() -> None:
    inputs = _certified_filesystem_inputs()
    first = _validate(inputs)
    second = _validate(inputs)

    assert first == second
    assert first.status is ValidationStatus.PASS
    assert len(first.scheduled_requirements) == 33
    assert len(first.requirement_results) == 33
    assert all(item.status is ValidationStatus.PASS for item in first.requirement_results)
    assert len(first.evidence_results) == 10
    assert first.failure_codes == ()
    assert first.deterministic is True
    assert first.read_only is True
    assert first.authority_effect == "NONE"
    assert first.replay_persisted is False
    assert first.governance_assessed is False
    assert first.certification_performed is False
    result_body = first.to_dict()
    declared_hash = result_body.pop("result_hash")
    assert declared_hash == canonical_hash(result_body)


def test_result_model_is_frozen() -> None:
    result = _validate(_certified_filesystem_inputs())
    with pytest.raises(FrozenInstanceError):
        result.status = ValidationStatus.FAIL  # type: ignore[misc]


def test_contract_substitution_fails_before_evidence_authentication() -> None:
    contract, manifest, evidence, anchors = _certified_filesystem_inputs()
    contract["title"] = "SUBSTITUTED"

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("HASH_MISMATCH",)
    assert result.evidence_results == ()
    assert result.requirement_results == ()


def test_manifest_substitution_fails_against_invocation_trust_anchor() -> None:
    contract, manifest, evidence, anchors = _certified_filesystem_inputs()
    manifest["manifest_id"] = "SUBSTITUTED-MANIFEST"
    manifest.pop("manifest_hash")
    manifest["manifest_hash"] = canonical_hash(manifest)

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("AUTHENTICATION_MISMATCH",)
    assert result.requirement_results == ()


def test_substituted_evidence_fails_before_rule_evaluation() -> None:
    contract, manifest, evidence, anchors = _certified_filesystem_inputs()
    selection_reference = manifest["evidence_records"][1]["artifact_reference"]
    evidence[selection_reference]["chain_id"] = "SUBSTITUTED-CHAIN"

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("HASH_MISMATCH",)
    assert result.requirement_results == ()


def test_cross_session_record_fails_closed() -> None:
    contract, manifest, evidence, _anchors = _certified_filesystem_inputs()
    manifest["evidence_records"][2]["session_id"] = "OTHER-SESSION"
    anchors = _rehash_manifest(manifest)

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("AUTHENTICATION_MISMATCH",)
    assert result.requirement_results == ()


def test_missing_required_evidence_fails_closed() -> None:
    contract, manifest, evidence, anchors = _certified_filesystem_inputs()
    reference = manifest["evidence_records"][4]["artifact_reference"]
    evidence.pop(reference)

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("MISSING_EVIDENCE",)


def test_failed_requirement_blocks_dependents_without_evaluating_them() -> None:
    contract, manifest, evidence, _anchors = _certified_filesystem_inputs()
    profile_record = manifest["evidence_records"][0]
    profile_reference = profile_record["artifact_reference"]
    evidence[profile_reference]["generic_replay_review_unchanged"] = False
    evidence[profile_reference].pop("artifact_hash")
    evidence[profile_reference]["artifact_hash"] = canonical_hash(evidence[profile_reference])
    profile_record["artifact_hash"] = evidence[profile_reference]["artifact_hash"]
    anchors = _rehash_manifest(manifest)

    result = _validate((contract, manifest, evidence, anchors))
    by_id = {item.requirement_id: item for item in result.requirement_results}

    assert result.status is ValidationStatus.FAIL
    assert by_id["REPLAY-003"].status is ValidationStatus.FAIL
    assert by_id["COMPAT-001"].reason_code == "DEPENDENCY_FAILED"
    assert by_id["COMPAT-001"].evaluation_detail == "failed dependencies: REPLAY-003"


def test_unsupported_rule_operator_is_rejected_during_contract_authentication() -> None:
    contract, manifest, evidence, _anchors = _certified_filesystem_inputs()
    requirement = next(item for item in contract["requirements"] if item["requirement_id"] == "AUTH-001")
    requirement["rule"] = {"operator": "ANY", "rules": [requirement["rule"]]}
    contract.pop("contract_hash")
    contract["contract_hash"] = canonical_hash(contract)
    manifest["contract_binding"]["contract_hash"] = contract["contract_hash"]
    manifest["evidence_records"][0]["lineage_commitments"][0]["artifact_hash"] = contract["contract_hash"]
    manifest.pop("manifest_hash")
    manifest["manifest_hash"] = canonical_hash(manifest)
    anchors = ValidationTrustAnchors(
        contract_id=contract["contract_id"],
        contract_hash=contract["contract_hash"],
        manifest_id=manifest["manifest_id"],
        manifest_hash=manifest["manifest_hash"],
    )

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("UNSUPPORTED_RULE_OPERATOR",)
    assert result.evidence_results == ()


def test_duplicate_json_keys_fail_closed() -> None:
    contract, manifest, evidence, anchors = _certified_filesystem_inputs()
    duplicate_contract = b'{"artifact_type":"A","artifact_type":"B"}'

    result = validate_constitutional_evidence(
        contract_source=duplicate_contract,
        manifest_source=manifest,
        evidence_sources=evidence,
        trust_anchors=anchors,
    )

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("DUPLICATE_JSON_KEY",)


def test_invalid_trust_anchor_type_returns_immutable_fail_result() -> None:
    contract, manifest, evidence, _anchors = _certified_filesystem_inputs()

    result = validate_constitutional_evidence(
        contract_source=contract,
        manifest_source=manifest,
        evidence_sources=evidence,
        trust_anchors={"contract_hash": contract["contract_hash"]},  # type: ignore[arg-type]
    )

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("INVALID_TRUST_ANCHORS",)
    assert result.contract_hash == ""
    assert result.manifest_hash == ""


def test_forward_or_cyclic_internal_lineage_fails_closed() -> None:
    contract, manifest, evidence, _anchors = _certified_filesystem_inputs()
    selection_record = manifest["evidence_records"][1]
    assignment_record = manifest["evidence_records"][2]
    selection_record["lineage_commitments"][0] = {
        "lineage_id": "LINEAGE-WORKER_SELECTION_LINEAGE",
        "artifact_reference": assignment_record["artifact_reference"],
        "artifact_hash": assignment_record["artifact_hash"],
        "relationship": "CONTINUES",
    }
    anchors = _rehash_manifest(manifest)

    result = _validate((contract, manifest, evidence, anchors))

    assert result.status is ValidationStatus.FAIL
    assert result.failure_codes == ("LINEAGE_ORDER_VIOLATION",)
    assert result.requirement_results == ()


def test_inputs_are_not_mutated() -> None:
    inputs = _certified_filesystem_inputs()
    contract, manifest, evidence, _anchors = inputs
    before = deepcopy((contract, manifest, evidence))

    _validate(inputs)

    assert (contract, manifest, evidence) == before


def test_rule_equality_is_type_strict_and_subset_is_order_independent() -> None:
    evidence = {
        "E": {
            "boolean": True,
            "integer": 1,
            "left": ["target", "result"],
            "right": ["result", "operation", "target"],
        }
    }
    unequal = {
        "operator": "EQUALS",
        "left": {"kind": "REFERENCE", "source": "EVIDENCE", "evidence_id": "E", "pointer": "/boolean"},
        "right": {"kind": "REFERENCE", "source": "EVIDENCE", "evidence_id": "E", "pointer": "/integer"},
    }
    subset = {
        "operator": "SUBSET_OF",
        "left": {"kind": "REFERENCE", "source": "EVIDENCE", "evidence_id": "E", "pointer": "/left"},
        "right": {"kind": "REFERENCE", "source": "EVIDENCE", "evidence_id": "E", "pointer": "/right"},
    }

    assert evaluate_rule(unequal, evidence).passed is False
    assert evaluate_rule(subset, evidence).passed is True


def test_certified_validator_result_is_replay_visible_through_platform_replay(tmp_path: Path) -> None:
    result = _validate(_certified_filesystem_inputs())

    capture = record_constitutional_validator_result(
        validation_result=result,
        recorded_at="2026-07-27T12:00:00Z",
        replay_dir=tmp_path / "constitutional-validator-replay",
    )
    reconstructed = reconstruct_constitutional_validator_replay(
        tmp_path / "constitutional-validator-replay"
    )

    assert capture["replay_owner"] == "PLATFORM_CORE_REPLAY"
    assert capture["validator_replay_persisted"] is False
    assert reconstructed["validator_result"] == result.to_dict()
    assert reconstructed["contract"]["contract_hash"] == result.contract_hash
    assert reconstructed["evidence_manifest"]["manifest_hash"] == result.manifest_hash
    assert reconstructed["overall_status"] == "PASS"
    assert reconstructed["governance_assessed"] is False
    assert reconstructed["certification_performed"] is False
