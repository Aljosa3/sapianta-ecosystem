"""P1F1–P1F12 and F1–F13: real source binding and inspection-only consumers.

Temporary Git sources establish observation integrity, not production authority.
Existing owner validators, certification registry and legacy regressions remain real.
"""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import platform_core_project_services as p1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge, validate_platform_knowledge_response
from aigol.runtime.platform_project_objective_inference import infer_platform_project_objective, validate_platform_project_objective
from aigol.runtime.platform_capability_composition_coverage import discover_platform_capability_composition_coverage, validate_platform_capability_composition_coverage
from aigol.runtime import platform_implementation_turn_durable_work_binding as durable

QUERY = "Inspect quuxfixture."
SUBJECT = "quuxfixture"


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def _ref(root, path, pointer=""):
    return {"path": path, "content_hash": "sha256:" + hashlib.sha256((root / path).read_bytes()).hexdigest(), "pointer": pointer}


def _rehash(value, field="artifact_hash"):
    value.pop(field, None)
    value[field] = replay_hash(value)
    return value


@pytest.fixture
def source(tmp_path, monkeypatch):
    root = tmp_path / "source"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "fixture@example.invalid")
    _git(root, "config", "user.name", "P1 fixture")
    (root / "identity.json").write_text(json.dumps({"subject_id": SUBJECT}))
    (root / "audit.json").write_text(json.dumps([
        {"subject_id": SUBJECT, "status": "IMPLEMENTED"},
        {"subject_id": SUBJECT, "status": "PARTIAL"},
        {"subject_id": SUBJECT, "status": "IMPLEMENTED"},
        {"subject_id": SUBJECT, "status": "CERTIFIED"},
    ]))
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "P1 scoped observations")
    monkeypatch.setattr(p1, "P1_REPOSITORY_ROOT", root)
    ref = _ref(root, "audit.json", "/0")
    claim = {
        "claim_subject_id": SUBJECT, "claim_type": "DEVELOPMENT_STATE", "claim_value": "IMPLEMENTED",
        "source_owner": {"id": None, "authority_reference": None}, "source_artifact": ref,
        "source_version_or_digest": ref["content_hash"], "source_scope": ["audit.json#/0"],
        "source_authority_effect": "NONE", "claim_mode": "OBSERVATION", "observed_or_asserted_at": None,
        "currentness_status": "UNKNOWN", "invalidation_status": "UNKNOWN",
    }
    envelope = {"schema_version": p1.P1_SCHEMA,
                "subject_identity": {"subject_id": SUBJECT, "raw_subject_ids": [SUBJECT], "identity_evidence": [_ref(root, "identity.json")]},
                "source_claims": [claim],
                "admission_context": {"repository_checkpoint": _git(root, "rev-parse", "HEAD"), "baseline_id": None, "owner_context": None}}
    return root, envelope


def _workspace(envelope):
    return {"project_knowledge_index": {"d1_admission_inputs": [deepcopy(envelope)]}}


def test_p1f2_p1f12_exact_observation_without_authority(source):
    _, envelope = source
    candidate = p1.admit_p1_source_claims(envelope)
    assert candidate == p1.validate_d1_candidate(candidate)
    assert candidate["d1"]["disposition"] == "INSPECTION_ONLY"
    claim = candidate["d1"]["source_claims"][0]
    assert claim["source_owner"] == {"id": None, "authority_reference": None}
    assert claim["source_authority_effect"] == "NONE"
    assert claim["currentness_status"] == "CURRENT"
    assert candidate["certified_artifacts"] == []


@pytest.mark.parametrize("mutation", ["missing", "extra", "wrong_type", "authority", "owner", "digest", "scope", "future", "partial", "path", "bool", "claim_list"])
def test_p1f3_p1f8_p1f9_f13_malformed_live_admission(source, mutation):
    _, obj = source
    claim = obj["source_claims"][0]
    if mutation == "missing": del claim["source_scope"]
    elif mutation == "extra": claim["certified"] = True
    elif mutation == "wrong_type": obj["source_claims"] = "claims"
    elif mutation == "authority": claim["source_authority_effect"] = "AUTHORIZED"
    elif mutation == "owner": claim["source_owner"]["id"] = "SELF"
    elif mutation == "digest": claim["source_artifact"]["content_hash"] = "sha256:" + "0" * 64
    elif mutation == "scope": claim["source_scope"] = ["whole-capability"]
    elif mutation == "future": obj["schema_version"] = "P1_V2"
    elif mutation == "partial": obj["admission_context"] = {}
    elif mutation == "path": claim["source_artifact"]["path"] = "../audit.json"
    elif mutation == "bool": claim["claim_value"] = True
    elif mutation == "claim_list": claim["claim_value"] = []
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(obj)


def test_p1f3_duplicate_and_nonfinite_json(source):
    _, obj = source
    raw = json.dumps(obj)
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(raw.replace('"schema_version":', '"schema_version": "duplicate", "schema_version":', 1))
    for value in ("NaN", "Infinity", "1e999"):
        with pytest.raises(FailClosedRuntimeError): p1.parse_p1_admission_input(raw.replace('"baseline_id": null', '"baseline_id": ' + value))


def test_p1f4_f5_prior_changed_source_is_historical_only(source):
    root, obj = source
    prior = p1.admit_p1_source_claims(obj)
    (root / "audit.json").write_text("[]")
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(obj)
    historical = p1.admit_p1_source_claims(obj, prior_candidate=prior)
    assert historical["d1"]["currentness"] == "STALE"
    assert historical["d1"]["revalidation_required"] is True
    assert historical["p1_candidate_hash"] != prior["p1_candidate_hash"]
    assert p1.validate_d1_candidate(historical) == historical
    assert not durable._bounded_project_capability_gap_evidence(knowledge_reuse={"candidate": historical}, coverage={})


def test_p1f5_f6_unsupported_alias_collision(source):
    _, obj = source
    obj["subject_identity"]["raw_subject_ids"].append("quuxfixture_v2")
    with pytest.raises(FailClosedRuntimeError, match="identity"): p1.admit_p1_source_claims(obj)


def test_p1f6_p1f11_distinct_provenance_and_conflicts(source):
    _, obj = source
    first = obj["source_claims"][0]
    second = deepcopy(first)
    second["source_artifact"]["pointer"] = "/2"
    second["source_scope"] = ["audit.json#/2"]
    obj["source_claims"] = [first, deepcopy(first), second]
    candidate = p1.admit_p1_source_claims(obj)
    assert len(candidate["d1"]["source_claims"]) == 2
    assert candidate["d1"]["ambiguity"] is False
    second["source_artifact"]["pointer"] = "/1"
    second["source_scope"] = ["audit.json#/1"]
    second["claim_value"] = "PARTIAL"
    candidate = p1.admit_p1_source_claims(obj)
    assert len(candidate["d1"]["source_claims"]) == 2
    assert candidate["d1"]["ambiguity"] is True


def test_p1f7_unknown_baseline_applicability(source):
    _, obj = source
    obj["admission_context"]["baseline_id"] = "unestablished-baseline"
    assert p1.admit_p1_source_claims(obj)["d1"]["currentness"] == "UNKNOWN"


@pytest.mark.parametrize("field,value", [("certified_artifacts", ["forged"]), ("d1", None), ("confidence_score", 100)])
def test_p1f8_rehashed_candidate_tampering_rejected(source, field, value):
    candidate = p1.admit_p1_source_claims(source[1])
    candidate[field] = value
    _rehash(candidate, "p1_candidate_hash")
    with pytest.raises(FailClosedRuntimeError): p1.validate_d1_candidate(candidate)


def test_f4_certification_is_not_development(source):
    _, obj = source
    claim = obj["source_claims"][0]
    claim.update(claim_value="CERTIFIED", source_scope=["audit.json#/3"])
    claim["source_artifact"]["pointer"] = "/3"
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(obj)


def test_f1_f7_f9_f10_discovery_and_knowledge_preserve_inspection(source):
    workspace = _workspace(source[1])
    discovery = p1.discover_candidate_capabilities(message=QUERY, workspace_state=workspace)
    assert discovery["capability_resolution_decision"] == "INSPECTION_REQUIRED"
    selected = discovery["selected_candidate_capability"]
    assert selected["capability_id"] == SUBJECT
    assert selected["d1"]["disposition"] == "INSPECTION_ONLY"
    knowledge = p1.project_knowledge_context_from_workspace(message=QUERY, workspace_state=workspace, goal_target=SUBJECT, governed_request=QUERY, candidate_capability_discovery=discovery)
    assert knowledge["classification"] == "INSPECTION_REQUIRED"
    assert knowledge["reuse_recommended"] is False
    assert knowledge["new_work_required"] is None
    assert knowledge["relevant_certified_artifacts"] == []
    assert p1.d1_inspection_required(knowledge)


@pytest.mark.parametrize("certificate", [None, "REPLAY_CERTIFICATION_RUNTIME"])
def test_f2_f3_c4_independent_lookup_remains_unbound(source, certificate):
    response = query_platform_knowledge(query=QUERY, capability_identifier=certificate, workspace_state=_workspace(source[1]))
    binding = response["d1_certification_binding"]
    assert binding["binding_status"] == "UNBOUND"
    assert binding["candidate_certification_state"] == "UNKNOWN"
    assert (binding["lookup_result"] is not None) is (certificate is not None)
    if certificate: assert binding["lookup_result"]["capability_identifier"] == certificate
    assert response["certification_status"] == "UNKNOWN"
    assert response["is_certified"] is False
    assert response["recommended_platform_service"] is None
    assert validate_platform_knowledge_response(response) == response
    response["is_certified"] = True
    _rehash(response)
    with pytest.raises(FailClosedRuntimeError): validate_platform_knowledge_response(response)


def test_f8_f12_inspection_blocks_coverage_and_both_gap_branches(source):
    workspace = _workspace(source[1])
    coverage = discover_platform_capability_composition_coverage(query=QUERY, workspace_state=workspace)
    assert coverage["coverage_status"] == "CAPABILITY_COMPOSITION_COVERAGE_FAILED_CLOSED"
    assert coverage["uncovered_residual_gaps"] == []
    assert coverage["discovered_reusable_capabilities"] == []
    assert validate_platform_capability_composition_coverage(coverage) == coverage
    assert not durable._bounded_project_capability_gap_evidence(knowledge_reuse={"capability_resolution_decision": "NEW_CAPABILITY"}, coverage=coverage)
    with pytest.raises(FailClosedRuntimeError): durable._project_capability_gap_coverage_projection(coverage)
    with pytest.raises(FailClosedRuntimeError): durable._project_required_extension_gap(coverage, knowledge_reuse={"new_work_required": True})
    coverage["uncovered_residual_gaps"] = [{"gap_classification": "PROJECT_CAPABILITY_GAP"}]
    _rehash(coverage)
    with pytest.raises(FailClosedRuntimeError): validate_platform_capability_composition_coverage(coverage)


@pytest.mark.parametrize("with_intent", [False, True])
def test_f12_objective_retains_provenance_without_planning(source, with_intent):
    workspace = _workspace(source[1])
    intent = p1.resolve_development_intent(message="Implement quuxfixture to produce evidence.", workspace_state=workspace) if with_intent else None
    objective = infer_platform_project_objective(request="Implement quuxfixture to produce evidence.", development_intent=intent, workspace_state=workspace)
    assert objective["objective_sufficient"] is False
    assert objective["development_plan_composition_eligible"] is False
    assert p1.d1_inspection_required(objective)
    assert validate_platform_project_objective(objective) == objective
    objective["development_plan_composition_eligible"] = True
    _rehash(objective)
    with pytest.raises(FailClosedRuntimeError): validate_platform_project_objective(objective)


def test_f13_parent_admission_prevents_stripped_candidate_fallback(source):
    discovery = p1.discover_candidate_capabilities(message=QUERY, workspace_state=_workspace(source[1]))
    candidate = discovery["candidate_capabilities"][0]
    for key in ("d1", "p1_admission_input", "p1_candidate_hash", "reuse_decision_basis"): candidate.pop(key)
    discovery["selected_candidate_capability"] = deepcopy(candidate)
    _rehash(discovery)
    with pytest.raises(FailClosedRuntimeError): p1.d1_inspection_required(discovery)


def test_p1f10_f11_legacy_certified_lookup_unchanged():
    result = query_platform_knowledge(query="Where is replay certification runtime implemented?", capability_identifier="REPLAY_CERTIFICATION_RUNTIME")
    assert result["is_certified"] is True
    assert result["canonical_capability_identifier"] == "REPLAY_CERTIFICATION_RUNTIME"
    assert "d1_certification_binding" not in result
    assert validate_platform_knowledge_response(result) == result


def test_p1f1_existing_g47_owner_claim_retained_without_promotion(source, tmp_path):
    from test_g31_04_canonical_implementation_turn_durable_work_binding import _context
    from aigol.runtime.constitutional_development_governance_operational_integration import _evidence_reference
    root, obj = source
    stages = _context(tmp_path)["constitutional_development_governance"]["stage_outputs"]
    cdd, snapshot = deepcopy(stages[1]), deepcopy(stages[2])
    evidence = _evidence_reference(subject_id="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY", claim_type="REALIZATION_COMPLETENESS", claim_value="COMPLETE", covered_facets=(), realization_complete=True)
    target = root / evidence.source_reference
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((Path(p1.__file__).resolve().parents[2] / evidence.source_reference).read_bytes())
    (root / "identity.json").write_text(json.dumps({"subject_id": evidence.subject_id}))
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "Bind existing owner evidence")
    snapshot["evidence_items"] = [asdict(evidence)]
    obj["admission_context"] = {"repository_checkpoint": _git(root, "rev-parse", "HEAD"), "baseline_id": cdd["baseline_reference"], "owner_context": {"cdd_classification": cdd, "evidence_snapshot": snapshot}}
    obj["subject_identity"] = {"subject_id": evidence.subject_id, "raw_subject_ids": [evidence.subject_id], "identity_evidence": [_ref(root, "identity.json")]}
    claim = obj["source_claims"][0]
    claim.update(claim_subject_id=evidence.subject_id, claim_type=evidence.claim_type, claim_value=evidence.claim_value, claim_mode="OWNER_ASSERTION", source_owner={"id": evidence.canonical_owner, "authority_reference": evidence.evidence_id}, source_artifact=_ref(root, evidence.source_reference, None), source_version_or_digest=evidence.content_hash, source_scope=list(evidence.declared_responsibilities))
    obj = json.loads(json.dumps(obj))
    candidate = p1.admit_p1_source_claims(obj)
    assert candidate["d1"]["source_claims"][0]["claim_mode"] == "OWNER_ASSERTION"
    assert candidate["certified_artifacts"] == []
    assert candidate["p1_admission_input"]["admission_context"]["owner_context"]["evidence_snapshot"]["evidence_items"][0]["implemented_responsibilities"] == list(evidence.implemented_responsibilities)
    claim = obj["source_claims"][0]
    claim["source_owner"]["id"] = "FORGED_OWNER"
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(obj)
    claim["source_owner"]["id"] = evidence.canonical_owner
    obj["admission_context"]["owner_context"]["evidence_snapshot"]["evidence_items"][0]["certification_status"] = "NOT_CERTIFIED"
    with pytest.raises(FailClosedRuntimeError): p1.admit_p1_source_claims(obj)


def test_workspace_only_knowledge_retains_d1_provenance(source):
    knowledge = p1.project_knowledge_context_from_workspace(message=QUERY, workspace_state=_workspace(source[1]), goal_target=SUBJECT, governed_request=QUERY)
    assert p1.d1_inspection_required(knowledge)
    assert knowledge["candidate_capability_discovery"]["selected_candidate_capability"]["capability_id"] == SUBJECT


def test_c8_set_like_inputs_canonicalize_without_hash_drift(source):
    _, obj = source
    first = p1.admit_p1_source_claims(obj)
    obj["source_claims"].append(deepcopy(obj["source_claims"][0]))
    obj["subject_identity"]["identity_evidence"].append(deepcopy(obj["subject_identity"]["identity_evidence"][0]))
    assert p1.admit_p1_source_claims(obj) == first


def test_f13_empty_parent_list_cannot_hide_nested_candidate(source):
    candidate = p1.admit_p1_source_claims(source[1])
    wrapper = {"d1_admission_inputs": [], "nested_candidate": candidate}
    assert p1.d1_inspection_required(wrapper)
    candidate["d1"]["disposition"] = "APPROVED_FOR_REUSE"
    _rehash(candidate, "p1_candidate_hash")
    with pytest.raises(FailClosedRuntimeError): p1.d1_inspection_required(wrapper)


def test_c8_workspace_index_retains_admission_and_durable_entry_refuses(source):
    workspace = _workspace(source[1])
    index = p1.project_knowledge_index_model(prior_state=workspace, pending_summary=None, guidance={}, implementation_history=[])
    assert index["d1_admission_inputs"] == workspace["project_knowledge_index"]["d1_admission_inputs"]
    assert index["certified_artifacts_by_target"] == {}
    with pytest.raises(FailClosedRuntimeError, match="inspection"):
        durable.prepare_implementation_turn_capability_coverage(request=QUERY, knowledge_reuse_artifact={"candidate": p1.admit_p1_source_claims(source[1])}, workspace_state=workspace, workspace=source[0], created_at="2026-07-11T00:00:00Z")
