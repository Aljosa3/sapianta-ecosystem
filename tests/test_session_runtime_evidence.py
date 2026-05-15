from sapianta_bridge.live_governed_session_runtime.session_runtime_evidence import session_runtime_evidence


def test_session_runtime_evidence_marks_persistence():
    evidence = session_runtime_evidence(binding={}, valid=False, states=("BLOCKED",))
    assert evidence["persistent_across_turns"] is True
