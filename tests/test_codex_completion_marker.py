from sapianta_bridge.provider_connectors.codex_completion_marker import (
    BOUNDED_COMPLETION_MARKER,
    detect_completion_marker,
    validate_completion_marker_detection,
)


def test_completion_marker_detects_literal_marker():
    detection = detect_completion_marker(stdout=f"done {BOUNDED_COMPLETION_MARKER}", stderr="")

    assert detection["marker_detected"] is True
    assert detection["stdout_contains_marker"] is True
    assert detection["arbitrary_text_success_inferred"] is False
    assert validate_completion_marker_detection(detection)["valid"] is True


def test_completion_marker_detects_structured_json_line():
    detection = detect_completion_marker(
        stdout='{"completion_marker":"AIGOL_TASK_COMPLETE","status":"ok"}',
        stderr="",
    )

    assert detection["marker_detected"] is True
    assert detection["json_completion_line_detected"] is True


def test_completion_marker_does_not_infer_success_from_plain_text():
    detection = detect_completion_marker(stdout="finished successfully", stderr="")

    assert detection["marker_detected"] is False
    assert detection["arbitrary_text_success_inferred"] is False
