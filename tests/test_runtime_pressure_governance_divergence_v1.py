from runtime_pressure_validation_helpers import validate_governance_alignment


VALID_ALIGNMENT = {
    "lineage_consistent": True,
    "topology_valid": True,
    "namespace_stable": True,
    "replay_matches_governance": True,
    "stabilization_boundary_preserved": True,
}


def test_valid_governance_alignment_remains_visibility_only():
    result = validate_governance_alignment(VALID_ALIGNMENT)

    assert result.status == "VALIDATED"
    assert result.mutation_performed is False
    assert result.governance_authority_expanded is False


def test_invalid_governance_lineage_reference_fails_closed():
    state = {**VALID_ALIGNMENT, "lineage_consistent": False}

    result = validate_governance_alignment(state)

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("invalid_governance_lineage_reference",)


def test_invalid_topology_reference_fails_closed():
    state = {**VALID_ALIGNMENT, "topology_valid": False}

    result = validate_governance_alignment(state)

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("invalid_governance_topology_reference",)


def test_namespace_continuity_divergence_fails_closed():
    state = {**VALID_ALIGNMENT, "namespace_stable": False}

    result = validate_governance_alignment(state)

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("namespace_continuity_divergence",)


def test_replay_governance_mismatch_fails_closed():
    state = {**VALID_ALIGNMENT, "replay_matches_governance": False}

    result = validate_governance_alignment(state)

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("replay_governance_mismatch",)


def test_stabilization_boundary_violation_fails_closed():
    state = {**VALID_ALIGNMENT, "stabilization_boundary_preserved": False}

    result = validate_governance_alignment(state)

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("stabilization_boundary_violation",)
