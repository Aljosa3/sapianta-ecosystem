"""STEP78CK D2F1–D2F15: source-bound inspection relevance, never authority."""
from copy import deepcopy

import pytest

from aigol.runtime import platform_core_project_services as services
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge, validate_platform_knowledge_response
from aigol.runtime.platform_project_objective_inference import infer_platform_project_objective, validate_platform_project_objective
from aigol.runtime import platform_implementation_turn_durable_work_binding as durable
from aigol.runtime.transport.serialization import replay_hash
from test_g59_06_conversation_objective_readiness_runtime_v2 import _create, _apply, _conversation, _time
from test_project_services_p1_source_claim_admission_v1 import source, _workspace

TARGET = "PLATFORM_CHANGE_NORMALIZATION"


def _state(tmp_path, *, outcome="canonical change evidence", scope=None, constraint=None,
           only_hint=False, subject="repository change", outcome_role="PRIMARY"):
    state = None if outcome_role == "SECONDARY" else _create(tmp_path)
    values = [("SEMANTIC_REFERENCE", "CAPABILITY_HINT", TARGET)] if only_hint else [
        ("OPERATIVE_ACTION", "PRIMARY", "normalize"),
        ("OPERATIVE_SUBJECT", "PRIMARY", subject),
        ("DESIRED_OUTCOME", outcome_role, outcome),
        ("WORK_TYPE", "ANALYSIS", "ANALYSIS"),
    ]
    if scope is not None:
        values.append(("SEMANTIC_REFERENCE", "SCOPE", scope))
    if constraint is not None:
        values.append(("GOVERNING_QUALIFIER", "PRESERVATION", constraint))
    initial_slots = []
    for revision, (kind, role, value) in enumerate(values, 1):
        slot = slots.create_semantic_slot_v2(
            conversation_identity=_conversation(), slot_class=kind, slot_role=role,
            cardinality_key="PRIMARY" if kind not in {"SEMANTIC_REFERENCE", "GOVERNING_QUALIFIER"} else role,
            surface_value=value, canonical_value=value, status="ASSERTED", completeness="COMPLETE",
            confidence_class="HUMAN_ASSERTED",
            materiality="CONDITIONAL" if kind in {"SEMANTIC_REFERENCE", "GOVERNING_QUALIFIER"} else "REQUIRED",
            provenance=[{"source_kind": "HUMAN_TURN", "turn_number": revision,
                         "source_revision": 0 if outcome_role == "SECONDARY" else revision, "source_span": value,
                         "content_digest": cwm._checksum(value), "normalization_rule_ids": [],
                         "human_disposition": "ASSERTED"}],
            created_at=_time(0 if outcome_role == "SECONDARY" else revision),
        )
        if outcome_role == "SECONDARY":
            initial_slots.append(slot)
        else:
            state = _apply(state, slot, revision)
    return _create(tmp_path, semantic_slots=initial_slots) if initial_slots else state


def _discover(state, workspace=None, **kwargs):
    return services.discover_candidate_capabilities(
        message="Inspect this structured requirement.", workspace_state=workspace,
        structured_requirement_state=state, **kwargs)


def _assessment(result, identifier=TARGET):
    return next(a for a in result["structured_relevance"]["candidate_assessments"]
                if a["candidate_identity"] == identifier)


def _rehash(obj, field="artifact_hash"):
    obj.pop(field, None)
    obj[field] = replay_hash(obj)
    return obj


def test_d2f1_d2f3_deterministic_relevance_without_internal_name(tmp_path):
    state = _state(tmp_path)
    first, second = _discover(state), _discover(state)
    assert first == second
    assert TARGET not in str(state)
    assert _assessment(first)["classification"] == "RELEVANT_FOR_INSPECTION"
    assert first["selected_candidate_capability"] is None
    assert services.validate_structured_discovery_relevance(first) == first
    assert services.d1_inspection_required(first)


def test_d2f2_requirement_revision_and_digest_are_bound(tmp_path):
    first = _discover(_state(tmp_path / "one"))
    second = _discover(_state(tmp_path / "two", outcome="validation plan"))
    assert first["structured_relevance"]["relevance_binding_hash"] != second["structured_relevance"]["relevance_binding_hash"]
    assert first["artifact_hash"] != second["artifact_hash"]


def test_d2f4_explicit_outcome_exclusion_beats_shared_words(tmp_path):
    result = _discover(_state(tmp_path, outcome="validation plan"))
    assessment = _assessment(result)
    assert assessment["classification"] == "NOT_RELEVANT_WITHIN_PROVEN_SCOPE"
    assert any(c["outcome"] == "CONTRADICTION" for c in assessment["field_comparisons"])


@pytest.mark.parametrize("extra", [{"scope": "an incompatible operational scope"}, {"constraint": "preserve external state"}])
def test_d2f5_supplied_unsupported_qualifier_is_unknown(tmp_path, extra):
    assessment = _assessment(_discover(_state(tmp_path, **extra)))
    assert assessment["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION"
    assert any(c["outcome"] == "UNKNOWN" for c in assessment["field_comparisons"])


def test_d2f6_d2f12_observation_is_not_semantic_proof_and_provenance_survives(tmp_path, source):
    workspace = _workspace(source[1])
    original = services.admit_p1_source_claims(source[1])
    result = _discover(_state(tmp_path), workspace)
    assert _assessment(result, "quuxfixture")["classification"] == "UNKNOWN_RELEVANCE"
    assert result["d1_admission_inputs"] == workspace["project_knowledge_index"]["d1_admission_inputs"]
    assert original in result["candidate_capabilities"]
    assert services.validate_structured_discovery_relevance(result) == result


def test_d2f7_stale_source_stays_historical(tmp_path, source):
    root, envelope = source
    prior = services.admit_p1_source_claims(envelope)
    state = _state(tmp_path)
    (root / "audit.json").write_text("[]")
    with pytest.raises(FailClosedRuntimeError):
        _discover(state, _workspace(envelope))
    result = _discover(state, _workspace(envelope), prior_d1_candidates=[prior])
    assessment = _assessment(result, "quuxfixture")
    assert assessment["currentness"] == "STALE"
    assert assessment["classification"] == "UNKNOWN_RELEVANCE"
    assert assessment["revalidation_required"] is True
    assert services.validate_structured_discovery_relevance(result) == result


def test_d2f8_partial_requirement_does_not_create_positive_relevance(tmp_path):
    state = _state(tmp_path, subject="two possible subject meanings")
    assessment = _assessment(_discover(state))
    assert assessment["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION"
    assert next(c for c in assessment["field_comparisons"] if c["slot_class"] == "OPERATIVE_SUBJECT")["outcome"] == "UNKNOWN"


def test_d2f9_independent_certificate_remains_unbound(tmp_path, source):
    response = query_platform_knowledge(
        query="Inspect this structured requirement.", capability_identifier=TARGET,
        workspace_state=_workspace(source[1]), structured_requirement_state=_state(tmp_path))
    binding = response["d1_certification_binding"]
    assert binding["binding_status"] == "UNBOUND"
    assert binding["lookup_result"]["capability_identifier"] == TARGET
    assert response["is_certified"] is False
    assert response["recommended_platform_service"] is None
    assert validate_platform_knowledge_response(response) == response
    response["is_certified"] = True
    _rehash(response)
    with pytest.raises(FailClosedRuntimeError):
        validate_platform_knowledge_response(response)


@pytest.mark.parametrize("decision", ["NEW_CAPABILITY", "EXTENDS_EXISTING_CAPABILITY", "PROJECT_CAPABILITY_GAP"])
def test_d2f10_rehashed_promotion_rejected(tmp_path, decision):
    result = _discover(_state(tmp_path))
    result["capability_resolution_decision"] = decision
    _rehash(result)
    with pytest.raises(FailClosedRuntimeError):
        services.d1_inspection_required(result)


def test_d2f11_existing_objective_and_gap_guards_refuse_authority(tmp_path):
    result = _discover(_state(tmp_path))
    objective = infer_platform_project_objective(
        request="Implement a normalized change to produce canonical change evidence.",
        development_intent={"candidate_capability_discovery": result, "work_type": "IMPLEMENTATION",
                            "runtime_implementation": True, "mutation_allowed": True})
    assert objective["objective_sufficient"] is False
    assert objective["development_plan_composition_eligible"] is False
    assert validate_platform_project_objective(objective) == objective
    objective["development_plan_composition_eligible"] = True
    _rehash(objective)
    with pytest.raises(FailClosedRuntimeError): validate_platform_project_objective(objective)
    with pytest.raises(FailClosedRuntimeError): durable._project_capability_gap_coverage_projection({"candidate_capability_discovery": result})
    with pytest.raises(FailClosedRuntimeError): durable._project_required_extension_gap({}, knowledge_reuse={"discovery": result})


def test_d2f13_unsupported_alias_does_not_join_descriptor(tmp_path, source):
    # An opaque audit identity remains distinct even when the query names a real descriptor subject.
    result = _discover(_state(tmp_path, subject="quuxfixture"), _workspace(source[1]))
    assessment = _assessment(result, "quuxfixture")
    assert assessment["classification"] == "UNKNOWN_RELEVANCE"
    assert all(e["kind"] != "G28_DESCRIPTOR" for e in assessment["evidence"])


def test_d2f14_equal_unknown_candidates_remain_visible_and_ordered(tmp_path):
    state = _state(tmp_path, only_hint=True)
    result = _discover(state)
    extension = result["structured_relevance"]
    assert extension["query_eligibility"] == "QUERY_INSUFFICIENT"
    assert len(extension["candidate_assessments"]) >= 5
    assert all(a["classification"] == "UNKNOWN_RELEVANCE" for a in extension["candidate_assessments"])
    keys = [(a["candidate_identity"], a["candidate_key"]) for a in extension["candidate_assessments"]]
    assert keys == sorted(keys)
    assert result["selected_candidate_capability"] is None


@pytest.mark.parametrize("mutation", ["schema", "forged", "missing", "extra", "stripped", "source"])
def test_d2f15_malformed_or_rehashed_forgery_fails_closed(tmp_path, mutation):
    result = _discover(_state(tmp_path))
    extension = result["structured_relevance"]
    if mutation == "schema": extension["schema_version"] = "FUTURE"
    elif mutation == "forged": extension["candidate_assessments"][-1]["classification"] = "RELEVANT_FOR_INSPECTION"
    elif mutation == "missing": del extension["candidate_assessments"]
    elif mutation == "extra": extension["authorized"] = True
    elif mutation == "stripped": del result["structured_relevance"]
    elif mutation == "source": extension["requirement_binding"]["source_state"]["semantic_revision"] += 1
    _rehash(extension, "relevance_binding_hash")
    _rehash(result)
    with pytest.raises(FailClosedRuntimeError): services.d1_inspection_required(result)


def test_d2f8_explicit_semantic_conflict_is_preserved(tmp_path):
    from test_g59_06_conversation_objective_readiness_runtime_v2 import _slot, machine_v2
    state = _state(tmp_path)
    incoming = _slot("another subject", source_revision=5, slot_class="OPERATIVE_SUBJECT")
    state = machine_v2.prepare_conversation_semantic_update_v2(
        state, expected_revision=state["revision"], operation=slots.MERGE,
        incoming_slot=incoming, observed_at=_time(5))["replacement_state"]
    result = _discover(state)
    assessment = _assessment(result)
    assert assessment["ambiguity"] is True
    assert assessment["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION"
    assert result["structured_relevance"]["ambiguity"] is True


def test_d2f14_two_real_owner_responsibility_matches_remain_multiple(tmp_path, source):
    import json
    from dataclasses import asdict
    from pathlib import Path
    from test_g31_04_canonical_implementation_turn_durable_work_binding import _context
    from test_project_services_p1_source_claim_admission_v1 import _git, _ref
    from aigol.runtime.constitutional_development_governance_operational_integration import _evidence_reference
    root, template = source
    stages = _context(tmp_path)["constitutional_development_governance"]["stage_outputs"]
    cdd, snapshot = deepcopy(stages[1]), deepcopy(stages[2])
    ids = ["CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY", "CANONICAL_PLATFORM_PRESENTATION_LAYER"]
    records = [_evidence_reference(subject_id=identifier, claim_type="REALIZATION_COMPLETENESS", claim_value="COMPLETE", covered_facets=(), realization_complete=True) for identifier in ids]
    for record in records:
        target = root / record.source_reference
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((Path(services.__file__).resolve().parents[2] / record.source_reference).read_bytes())
    (root / "owners.json").write_text(json.dumps([{"subject_id": identifier} for identifier in ids]))
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "Existing owner responsibility sources")
    snapshot["evidence_items"] = [asdict(record) for record in records]
    envelopes = []
    for index, record in enumerate(records):
        envelope = deepcopy(template)
        envelope["subject_identity"] = {"subject_id": record.subject_id, "raw_subject_ids": [record.subject_id], "identity_evidence": [_ref(root, "owners.json", "/" + str(index))]}
        envelope["admission_context"] = {"repository_checkpoint": _git(root, "rev-parse", "HEAD"), "baseline_id": cdd["baseline_reference"], "owner_context": {"cdd_classification": cdd, "evidence_snapshot": snapshot}}
        envelope["source_claims"][0].update(claim_subject_id=record.subject_id, claim_type=record.claim_type, claim_value=record.claim_value, claim_mode="OWNER_ASSERTION", source_owner={"id": record.canonical_owner, "authority_reference": record.evidence_id}, source_artifact=_ref(root, record.source_reference, None), source_version_or_digest=record.content_hash, source_scope=list(record.declared_responsibilities))
        envelopes.append(json.loads(json.dumps(envelope)))
    state = _state(tmp_path / "query", subject="CERTIFIED_CAPABILITY_RUNTIME")
    result = _discover(state, {"project_knowledge_index": {"d1_admission_inputs": envelopes}})
    assessments = [_assessment(result, identifier) for identifier in ids]
    assert all(a["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION" for a in assessments)
    assert all(any(c["slot_class"] == "OPERATIVE_SUBJECT" and c["outcome"] == "MATCH" for c in a["field_comparisons"]) for a in assessments)
    ordered = [a["candidate_identity"] for a in result["structured_relevance"]["candidate_assessments"] if a["candidate_identity"] in ids]
    assert ordered == sorted(ids)
    assert result["structured_relevance"]["ambiguity"] is True
    assert result["selected_candidate_capability"] is None
    assert services.validate_structured_discovery_relevance(result) == result


def _rename_observation(source, identifier):
    from test_project_services_p1_source_claim_admission_v1 import _git, _ref
    root, original = source
    envelope = deepcopy(original)
    for name in ("audit.json", "identity.json"):
        path = root / name
        path.write_text(path.read_text().replace("quuxfixture", identifier))
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "Bind explicit observation identity")
    envelope["subject_identity"] = {"subject_id": identifier, "raw_subject_ids": [identifier], "identity_evidence": [_ref(root, "identity.json")]}
    envelope["admission_context"]["repository_checkpoint"] = _git(root, "rev-parse", "HEAD")
    claim = envelope["source_claims"][0]
    claim["claim_subject_id"] = identifier
    claim["source_artifact"] = _ref(root, "audit.json", "/0")
    claim["source_version_or_digest"] = claim["source_artifact"]["content_hash"]
    return envelope


def test_d2f7_stale_d1_with_positive_descriptor_is_only_possibly_relevant(tmp_path, source):
    envelope = _rename_observation(source, TARGET)
    prior = services.admit_p1_source_claims(envelope)
    (source[0] / "audit.json").write_text("[]")
    result = _discover(_state(tmp_path), _workspace(envelope), prior_d1_candidates=[prior])
    assessment = _assessment(result)
    assert assessment["currentness"] == "STALE"
    assert assessment["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION"
    assert services.validate_structured_discovery_relevance(result) == result


def test_d2f13_version_like_name_does_not_inherit_descriptor(tmp_path, source):
    identifier = TARGET + "_V2"
    envelope = _rename_observation(source, identifier)
    assessment = _assessment(_discover(_state(tmp_path), _workspace(envelope)), identifier)
    assert assessment["classification"] == "UNKNOWN_RELEVANCE"
    assert all(e["kind"] != "G28_DESCRIPTOR" for e in assessment["evidence"])


def test_d2f11_g20_and_durable_validators_reject_rehashed_authority(tmp_path):
    from aigol.runtime.platform_capability_composition_coverage import discover_platform_capability_composition_coverage, validate_platform_capability_composition_coverage
    discovery = _discover(_state(tmp_path))
    coverage = discover_platform_capability_composition_coverage(query="Observe replay through the replay observation layer.")
    coverage["candidate_capability_discovery"] = discovery
    coverage["candidate_capability_discovery_hash"] = discovery["artifact_hash"]
    _rehash(coverage)
    with pytest.raises(FailClosedRuntimeError, match="inspection"):
        validate_platform_capability_composition_coverage(coverage)
    with pytest.raises(FailClosedRuntimeError, match="inspection"):
        durable.validate_implementation_turn_durable_work_binding({"candidate_capability_discovery": discovery})


def test_d2f15_live_options_and_source_types_do_not_coerce(tmp_path):
    state = _state(tmp_path)
    with pytest.raises(FailClosedRuntimeError):
        _discover(state, generic_capability_catalog_allowed=1)
    invalid = deepcopy(state)
    invalid["unknown_field"] = True
    with pytest.raises(FailClosedRuntimeError):
        _discover(invalid)
    with pytest.raises(FailClosedRuntimeError):
        _discover(state, prior_d1_candidates="not-an-array")


def test_d2f12_consumer_repeated_candidate_forgery_is_rejected(tmp_path):
    discovery = _discover(_state(tmp_path))
    consumer = {"candidate_capability_discovery": discovery,
                "candidate_capabilities_received": deepcopy(discovery["candidate_capabilities"])}
    assert services.d1_inspection_required(consumer)
    consumer["candidate_capabilities_received"][0]["confidence_score"] = 999
    with pytest.raises(FailClosedRuntimeError):
        services.d1_inspection_required(consumer)


def test_d2f15_malformed_d1_identity_fails_closed(tmp_path, source):
    envelope = deepcopy(source[1])
    envelope["subject_identity"]["subject_id"] = []
    with pytest.raises(FailClosedRuntimeError):
        _discover(_state(tmp_path), _workspace(envelope))


def test_d2f8_secondary_outcome_does_not_supply_primary_comparison(tmp_path):
    assessment = _assessment(_discover(_state(tmp_path, outcome_role="SECONDARY")))
    assert assessment["classification"] == "POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION"
    assert any(c["slot_class"] == "DESIRED_OUTCOME" and c["reason_code"] == "REQUIRED_COMPARISON_MISSING"
               for c in assessment["field_comparisons"])
