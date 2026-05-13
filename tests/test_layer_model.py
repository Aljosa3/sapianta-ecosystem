from sapianta_bridge.architecture.layer_model import (
    STABILIZATION_BASELINE,
    canonical_layer_model,
    list_layers,
    replay_safe_layer_evidence,
)


def test_all_five_layers_are_formally_defined() -> None:
    model = canonical_layer_model()

    assert STABILIZATION_BASELINE == "STABILIZATION_CERTIFICATION_EPOCH_V1"
    assert list_layers() == (
        "INTERACTION_LAYER",
        "GOVERNANCE_LAYER",
        "EXECUTION_LAYER",
        "VALIDATION_LAYER",
        "REFLECTION_LAYER",
    )
    assert set(model["layers"]) == set(list_layers())
    assert model["agol_role"] == "GOVERNANCE_CONTROL_PLANE"
    assert model["agol_is_execution_intelligence"] is False
    assert model["permanent_invariant"] == "INTERACTION_LAYER != EXECUTION_LAYER"


def test_layer_model_is_provider_independent() -> None:
    provider_model = canonical_layer_model()["provider_independent_execution"]

    assert provider_model["providers_replaceable"] is True
    assert provider_model["providers_non_authoritative"] is True
    assert provider_model["provider_identity_affects_governance_semantics"] is False
    assert provider_model["replay_evidence_format_stable_across_providers"] is True


def test_replay_safe_layer_evidence_is_deterministic() -> None:
    first = replay_safe_layer_evidence(provider="codex")
    second = replay_safe_layer_evidence(provider="codex")

    assert first == second
    assert first["interaction_layer"]["execution_authority"] is False
    assert first["execution_layer"]["provider_authoritative"] is False
    assert first["reflection_layer"]["allowed_to_execute_automatically"] is False
