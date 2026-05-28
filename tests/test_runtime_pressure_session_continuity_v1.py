from runtime_pressure_validation_helpers import validate_session_continuity


VALID_SESSIONS = [
    {"session_id": "SESSION-000001", "parent_session_id": None},
    {"session_id": "SESSION-000002", "parent_session_id": "SESSION-000001"},
    {"session_id": "SESSION-000003", "parent_session_id": "SESSION-000002"},
]


def test_valid_session_continuity_remains_replay_safe():
    result = validate_session_continuity(VALID_SESSIONS)

    assert result.status == "VALIDATED"
    assert result.append_only_preserved is True
    assert result.mutation_performed is False


def test_orphan_session_lineage_fails_closed():
    result = validate_session_continuity(
        [
            {"session_id": "SESSION-000001", "parent_session_id": None},
            {"session_id": "SESSION-000002", "parent_session_id": "SESSION-999999"},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("orphan_session_lineage",)


def test_invalid_session_transition_order_fails_closed():
    result = validate_session_continuity(
        [
            {"session_id": "SESSION-000002", "parent_session_id": "SESSION-000001"},
            {"session_id": "SESSION-000001", "parent_session_id": None},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("invalid_session_transition_order",)


def test_cross_session_ambiguity_fails_closed():
    result = validate_session_continuity(
        [
            {"session_id": "SESSION-000001", "parent_session_id": None},
            {"session_id": "SESSION-000002", "parent_session_id": "SESSION-000001", "ambiguous_transition": True},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("cross_session_continuity_ambiguity",)


def test_continuity_fragmentation_fails_closed():
    result = validate_session_continuity(
        [
            {"session_id": "SESSION-000001", "parent_session_id": None},
            {"session_id": "SESSION-000002", "parent_session_id": None},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("continuity_fragmentation",)


def test_multi_lineage_pressure_fails_closed():
    result = validate_session_continuity(
        [
            {"session_id": "SESSION-000001", "parent_session_id": None},
            {"session_id": "SESSION-000002", "parent_session_id": "SESSION-000001", "lineage_claims": 2},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("multi_lineage_continuity_pressure",)
