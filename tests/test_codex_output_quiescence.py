from sapianta_bridge.provider_connectors.codex_output_quiescence import (
    classify_output_quiescence,
    validate_output_quiescence,
)


def test_quiescence_requires_marker_and_running_process():
    quiescence = classify_output_quiescence(
        stdout="AIGOL_TASK_COMPLETE",
        stderr="",
        marker_detected=True,
        process_running=True,
        idle_window_seconds=1,
    )

    assert quiescence["output_quiescent"] is True
    assert quiescence["bounded_result_available"] is True
    assert validate_output_quiescence(quiescence)["valid"] is True


def test_quiescence_rejects_missing_marker_as_result():
    quiescence = classify_output_quiescence(
        stdout="done",
        stderr="",
        marker_detected=False,
        process_running=True,
        idle_window_seconds=1,
    )

    assert quiescence["output_quiescent"] is False
    assert quiescence["bounded_result_available"] is False


def test_quiescence_requires_idle_window():
    quiescence = classify_output_quiescence(
        stdout="AIGOL_TASK_COMPLETE",
        stderr="",
        marker_detected=True,
        process_running=True,
        idle_window_seconds=0,
    )

    assert quiescence["output_quiescent"] is False
