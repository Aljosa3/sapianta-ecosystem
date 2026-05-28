from runtime_pressure_validation_helpers import validate_bounded_refinement_pressure


def test_bounded_refinement_accepts_evidence_backed_non_expansion_pressure():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "semantic_hardening",
            "bounded_refinement_evidence": True,
            "replay_safe": True,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "VALIDATED"
    assert result.governance_authority_expanded is False


def test_orchestration_injection_pressure_fails_closed():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "orchestration",
            "bounded_refinement_evidence": False,
            "replay_safe": True,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("bounded_refinement_required_before_expansion",)
    assert result.orchestration_requested is True


def test_adaptive_runtime_pressure_fails_closed():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "adaptive_runtime",
            "bounded_refinement_evidence": True,
            "replay_safe": True,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("adaptive_or_semantic_activation_rejected",)
    assert result.adaptive_runtime_requested is True


def test_semantic_amplification_pressure_fails_closed():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "semantic_amplification",
            "bounded_refinement_evidence": True,
            "replay_safe": True,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("adaptive_or_semantic_activation_rejected",)
    assert result.cognition_requested is True


def test_subsystem_multiplication_pressure_requires_refinement_evidence():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "subsystem_multiplication",
            "bounded_refinement_evidence": False,
            "replay_safe": True,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("bounded_refinement_required_before_expansion",)


def test_recursive_governance_expansion_requires_replay_safe_continuity():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "recursive_governance_expansion",
            "bounded_refinement_evidence": True,
            "replay_safe": False,
            "stabilization_before_expansion": True,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("replay_safe_governance_continuity_required",)


def test_stabilization_before_expansion_is_required():
    result = validate_bounded_refinement_pressure(
        {
            "pressure_type": "semantic_hardening",
            "bounded_refinement_evidence": True,
            "replay_safe": True,
            "stabilization_before_expansion": False,
        }
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("stabilization_before_expansion_required",)
