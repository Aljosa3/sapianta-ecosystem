from sapianta_bridge.live_governed_runtime_serving.runtime_serving_evidence import runtime_serving_evidence


def test_runtime_serving_evidence_marks_attachable():
    assert runtime_serving_evidence(binding={}, valid=False, states=("BLOCKED",))["continuously_attachable"] is True
