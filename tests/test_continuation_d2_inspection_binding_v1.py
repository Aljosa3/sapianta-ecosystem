"""CN B1–B12/C1–C10: real typed ingress and owner evidence, no authority substitutes."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime import platform_core_project_services as services
from aigol.runtime import production_conversation_flow_binding as flow_owner
from aigol.runtime import human_interface_conversation_runtime_v2 as hir
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g66_13_canonical_typed_semantic_composition_convergence import _entry, _time, SESSION


def _hash(value):
    value.pop("artifact_hash", None)
    value["artifact_hash"] = replay_hash(value)
    return value


@pytest.fixture
def admitted(tmp_path, monkeypatch):
    root, workspace = tmp_path / "runtime", tmp_path / "workspace"
    saved = []
    original = services._objective_commitment_gate_project_context
    def gate(**kwargs):
        saved.append(deepcopy(kwargs))
        return original(**kwargs)
    monkeypatch.setattr(services, "_objective_commitment_gate_project_context", gate)
    initial = _entry(root, workspace, "Implement a validator.", second=1)
    first = _entry(root, workspace, "action: normalize", second=2)
    return root, workspace, initial, first, saved


def _context(capture):
    return capture["platform_core_project_services_context"]


def _extension(capture):
    return _context(capture)["knowledge_reuse"]["candidate_capability_discovery"]["structured_relevance"]


def test_b1_b6_b8_c6_real_ingress_and_insufficient_state(admitted):
    root, workspace, initial, first, _ = admitted
    assert "continuation_d2_binding" not in _context(initial)["knowledge_reuse"]
    assert _extension(first)["query_eligibility"] == "QUERY_INSUFFICIENT"
    assert services.validate_continuation_d2_inspection_context(_context(first), runtime_root=root) == _context(first)
    stored = sorted((root / SESSION / "uhi_project_services").glob("*_uhi_project_context_recorded.json"))
    assert json.loads(stored[-1].read_text()) == _context(first)


def test_b2_b3_b7_b12_c1_c2_c3_c4_c8_c10(admitted, monkeypatch):
    root, workspace, _, first, _ = admitted
    def forbidden(*args, **kwargs):
        raise AssertionError("continuation must not select or rescore a route")
    monkeypatch.setattr(flow_owner, "select_platform_query_route", forbidden)
    second = _entry(root, workspace, "subject: repository change", second=3)
    old = _context(first)["knowledge_reuse"]["continuation_d2_binding"]
    context = _context(second)
    binding = context["knowledge_reuse"]["continuation_d2_binding"]
    state = second["production_conversation_binding"]["conversation_state"]
    assert _extension(second)["query_eligibility"] == "SUFFICIENT_FOR_INSPECTION_QUERY"
    assert binding["post_transition_revision"] == state["revision"]
    assert binding["post_transition_revision"] > binding["pre_transition_revision"] + 1
    assert binding["semantic_revision"] > old["semantic_revision"]
    assert binding["binding_hash"] != old["binding_hash"]
    assert binding["original_request_hash"] != context["message_hash"]
    assert binding["source_turn_identity"] != old["source_turn_identity"]
    assert binding["original_request_identity"] == old["original_request_identity"]
    assert binding["snapshot_replay_hash"] == replay_hash(state)
    assert binding["continuation_predecessors"]
    assert second["production_conversation_binding"]["platform_query_router_reinvoked"] is False
    assert second["production_conversation_flow_binding"]["requested_target_flow_id"] == first["production_conversation_flow_binding"]["requested_target_flow_id"]
    assert any(c["outcome"] == "UNKNOWN" for a in _extension(second)["candidate_assessments"] for c in a["field_comparisons"])
    assert services.validate_continuation_d2_inspection_context(context, runtime_root=root) == services.validate_continuation_d2_inspection_context(context, runtime_root=root)
    assert {p.name for p in root.iterdir()} == {
        "production_conversation_cwm", "production_conversation_flow_binding",
        SESSION, "canonical_che_evidence_correlations_v1",
    }


def test_b8_c7_legacy_gate_projection_identical_outside_knowledge(admitted, monkeypatch):
    root, _, _, first, saved = admitted
    args = deepcopy(saved[-1])
    args["continuation_d2_input"] = None
    monkeypatch.setattr(services, "write_json_immutable", lambda *a, **k: None)
    assert services._objective_commitment_gate_project_context(**deepcopy(saved[-1])) == _context(first)
    assert services._objective_commitment_gate_project_context(**deepcopy(saved[-1])) == _context(first)
    baseline = services._objective_commitment_gate_project_context(**args)
    enriched = deepcopy(_context(first))
    for result in (baseline, enriched):
        result.pop("knowledge_reuse")
        result.pop("artifact_hash")
    assert baseline == enriched


@pytest.mark.parametrize("field", ["snapshot_checksum", "snapshot_replay_hash", "original_request_identity",
                                    "source_turn_digest", "pre_transition_revision", "post_transition_revision",
                                    "semantic_revision", "continuation_predecessors", "authority_effect", "extra"])
def test_b4_b5_c9_rehashed_metadata_rejected(admitted, field):
    root, _, _, first, _ = admitted
    context = deepcopy(_context(first))
    metadata = context["knowledge_reuse"]["continuation_d2_binding"]
    metadata[field] = "FORGED"
    metadata.pop("binding_hash")
    metadata["binding_hash"] = replay_hash(metadata)
    _hash(context)
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(context, runtime_root=root)


@pytest.mark.parametrize("field", ["project_objective_inference", "constitutional_development_governance",
                                    "reuse_proof_production_admission", "canonical_implementation_turn_binding",
                                    "execution_authorized", "authority_effect"])
def test_b9_rehashed_parent_promotion_rejected(admitted, field):
    context = deepcopy(_context(admitted[3]))
    context[field] = True
    _hash(context)
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(context)


def test_b9_gate_clarification_and_intent_tamper(admitted):
    for where, field, value in [("development_intent_resolution", "summary_admissible", True),
                                ("human_conversation_experience", "response_mode", "EXECUTE"),
                                ("knowledge_reuse", "reuse_recommended", True)]:
        context = deepcopy(_context(admitted[3]))
        context[where][field] = value
        _hash(context)
        with pytest.raises(FailClosedRuntimeError):
            services.validate_continuation_d2_inspection_context(context)


@pytest.mark.parametrize("bad", [{}, {"conversation_state": None}, {"conversation_state": {}, "schema": "FUTURE"}])
def test_asserted_missing_or_unsupported_input_fails_closed(admitted, bad):
    args = deepcopy(admitted[4][-1])
    args["continuation_d2_input"] = bad
    with pytest.raises(FailClosedRuntimeError):
        services._objective_commitment_gate_project_context(**args)


def test_asserted_input_outside_gate_fails_closed(tmp_path):
    with pytest.raises(FailClosedRuntimeError):
        services.prepare_unified_human_interface_project_context(
            interface_name="aicli", session_id=SESSION, message="hello",
            runtime_root=tmp_path, workspace=tmp_path, created_at=_time(1),
            continuation_d2_input={"conversation_state": {}})


@pytest.mark.parametrize("mutation", ["checksum", "session", "conversation", "revision"])
def test_b4_b5_snapshot_tamper_fails_closed(admitted, mutation):
    args = deepcopy(admitted[4][-1])
    state = args["continuation_d2_input"]["conversation_state"]
    if mutation == "checksum": state["integrity_checksum"] = "sha256:" + "0" * 64
    elif mutation == "session": state["envelope"]["session_identity"] = "other"
    elif mutation == "conversation": state["envelope"]["conversation_identity"] = "conversation-local-sha256:" + "0" * 64
    else: state["revision"] += 1
    with pytest.raises(FailClosedRuntimeError):
        services._objective_commitment_gate_project_context(**args)


def test_c5_live_advance_rejects_but_historical_integrity_remains(admitted):
    root, workspace, _, first, _ = admitted
    _entry(root, workspace, "subject: repository change", second=3)
    context = _context(first)
    with pytest.raises(FailClosedRuntimeError, match="stale"):
        services.validate_continuation_d2_inspection_context(context, runtime_root=root)
    assert services.validate_continuation_d2_inspection_context(context) == context


def test_c5_expiration_and_missing_owner_store_rejected(admitted):
    root, _, _, first, saved = admitted
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(_context(first), runtime_root=root / "missing")
    args = deepcopy(saved[-1])
    args["created_at"] = "2026-08-04T18:00:00Z"
    with pytest.raises(FailClosedRuntimeError, match="expired"):
        services._objective_commitment_gate_project_context(**args)


def test_c9_malformed_owner_predecessor_rejected(admitted):
    context = _context(admitted[3])
    ref = context["production_conversation_flow_binding"]["ordered_predecessor_references"][0]
    Path(ref["replay_reference"]).write_text("{}")
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(context)


def test_c5_owner_change_during_projection_prevents_persistence(admitted, monkeypatch):
    root, workspace, _, _, saved = admitted
    original = services.discover_candidate_capabilities
    advanced = False
    def discovery(**kwargs):
        nonlocal advanced
        result = original(**kwargs)
        if kwargs.get("structured_requirement_state") is not None and not advanced:
            advanced = True
            hir.admit_hir_semantic_turn_v2(
                runtime_root=root / "production_conversation_cwm", workspace_identity=workspace,
                session_identity=SESSION + ":production-conversation-v1",
                source_turn_text="subject: repository change", observed_at=_time(3))
        return result
    monkeypatch.setattr(services, "discover_candidate_capabilities", discovery)
    before = list((root / SESSION / "uhi_project_services").glob("*.json"))
    with pytest.raises(FailClosedRuntimeError, match="stale"):
        services._objective_commitment_gate_project_context(**deepcopy(saved[-1]))
    assert list((root / SESSION / "uhi_project_services").glob("*.json")) == before


def test_b10_independent_existing_registry_leaves_c4_unbound(admitted):
    from aigol.runtime.platform_capability_certification_registry import list_platform_capability_certifications
    assert list_platform_capability_certifications()
    binding = _context(admitted[3])["knowledge_reuse"]["continuation_d2_binding"]
    assert binding["c4_status"] == "UNBOUND"
    assert binding["authority_effect"] == "NONE"
    assert binding["inspection_only"] is True


def test_c5_valid_other_session_owner_state_substitution_rejected(admitted):
    root, workspace, _, first, _ = admitted
    state = first["production_conversation_binding"]["conversation_state"]
    other = cwm.create_conversation_working_memory_state_v2(
        runtime_root=root / "production_conversation_cwm", workspace_identity=workspace,
        session_identity="OTHER", created_at=_time(1),
        participants=state["envelope"]["participants"])
    store_root = cwm._conversation_root(root / "production_conversation_cwm")
    path = cwm._state_path(store_root, str(workspace), SESSION + ":production-conversation-v1")
    path.write_text(json.dumps(other))
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(_context(first), runtime_root=root)


@pytest.mark.parametrize("value", [None, [], "invalid", 1])
def test_malformed_context_root_fails_closed(value):
    with pytest.raises(FailClosedRuntimeError):
        services.validate_continuation_d2_inspection_context(value)


def test_s4_s5_s6_real_owner_handoff_activation(tmp_path, monkeypatch):
    from aigol.runtime import human_interface_runtime_entry_service as entry_owner
    root, workspace = tmp_path / "runtime", tmp_path / "workspace"
    calls = []
    original = entry_owner.prepare_unified_human_interface_project_context
    def record(**kwargs):
        calls.append(deepcopy(kwargs))
        return original(**kwargs)
    monkeypatch.setattr(entry_owner, "prepare_unified_human_interface_project_context", record)
    _entry(root, workspace, "Implement a validator.", second=1)
    assert calls[-1]["continuation_d2_input"] is None
    def forbidden(*args, **kwargs):
        raise AssertionError("handoff reinvoked router selection")
    monkeypatch.setattr(flow_owner, "select_platform_query_route", forbidden)
    _entry(root, workspace, "/reply subject: validator", second=2)
    assert calls[-1]["continuation_d2_input"] is None
    for second, text in enumerate(("action: normalize", "subject: repository change",
                                   "outcome: canonical change evidence", "work-type: ANALYSIS"), 3):
        capture = _entry(root, workspace, text, second=second)
        actual = calls[-1]["continuation_d2_input"]
        assert set(actual) == {"conversation_state"}
        assert actual["conversation_state"] == capture["production_conversation_binding"]["conversation_state"]
    confirmation = capture["canonical_typed_semantic_composition"]["expected_confirmation_action"]
    confirmed = _entry(root, workspace, confirmation, second=7)
    assert confirmed["canonical_typed_semantic_composition"]["control"] == "CANDIDATE_CONFIRMATION"
    assert calls[-1]["continuation_d2_input"] is None


def test_s5_other_selected_flow_does_not_forward(tmp_path, monkeypatch):
    from aigol.runtime import human_interface_runtime_entry_service as entry_owner
    calls = []
    original = entry_owner.prepare_unified_human_interface_project_context
    def record(**kwargs):
        calls.append(deepcopy(kwargs))
        return original(**kwargs)
    monkeypatch.setattr(entry_owner, "prepare_unified_human_interface_project_context", record)
    result = _entry(tmp_path / "runtime", Path(__file__).resolve().parents[1], "Show architecture.", second=1)
    assert result["production_conversation_flow_binding"]["objective_commitment_required"] is False
    assert calls[-1]["continuation_d2_input"] is None
