from runtime_pressure_validation_helpers import validate_replay_chain


VALID_CHAIN = [
    {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
    {"replay_id": "PRESSURE-REPLAY-000002", "parent_replay_id": "PRESSURE-REPLAY-000001"},
    {"replay_id": "PRESSURE-REPLAY-000003", "parent_replay_id": "PRESSURE-REPLAY-000002"},
]


def test_valid_replay_chain_preserves_append_only_continuity():
    result = validate_replay_chain(VALID_CHAIN)

    assert result.status == "VALIDATED"
    assert result.append_only_preserved is True
    assert result.mutation_performed is False


def test_duplicate_replay_ids_fail_closed():
    result = validate_replay_chain(
        [
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": "PRESSURE-REPLAY-000001"},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("duplicate_replay_identity",)
    assert result.append_only_preserved is True


def test_replay_gap_fails_closed_without_repair():
    result = validate_replay_chain(
        [
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
            {"replay_id": "PRESSURE-REPLAY-000003", "parent_replay_id": "PRESSURE-REPLAY-000001"},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("replay_gap",)
    assert result.mutation_performed is False


def test_invalid_replay_ordering_fails_closed():
    result = validate_replay_chain(
        [
            {"replay_id": "PRESSURE-REPLAY-000002", "parent_replay_id": "PRESSURE-REPLAY-000001"},
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("non_monotonic_replay_ordering",)


def test_corrupted_replay_ancestry_fails_closed():
    result = validate_replay_chain(
        [
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
            {"replay_id": "PRESSURE-REPLAY-000002", "parent_replay_id": "PRESSURE-REPLAY-999999"},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("corrupted_replay_ancestry",)


def test_replay_continuity_fragmentation_fails_closed():
    result = validate_replay_chain(
        [
            {"replay_id": "PRESSURE-REPLAY-000001", "parent_replay_id": None},
            {"replay_id": "PRESSURE-REPLAY-000002", "parent_replay_id": None},
        ]
    )

    assert result.status == "FAIL_CLOSED"
    assert result.reasons == ("replay_continuity_fragmentation",)
