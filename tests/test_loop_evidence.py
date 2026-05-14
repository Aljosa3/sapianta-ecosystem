from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop
from sapianta_bridge.no_copy_paste_loop.loop_evidence import validate_loop_evidence


def test_loop_evidence_is_replay_safe_and_valid() -> None:
    evidence = run_no_copy_paste_loop("Inspect governance evidence")["loop_evidence"]

    assert evidence["replay_safe"] is True
    assert evidence["lineage_continuity_valid"] is True
    assert evidence["copy_paste_removed_for_single_pass"] is True
    assert validate_loop_evidence(evidence)["valid"] is True


def test_loop_evidence_rejects_boundary_violations() -> None:
    evidence = run_no_copy_paste_loop("Inspect governance evidence")["loop_evidence"]
    evidence["loop_is_orchestration"] = True

    assert validate_loop_evidence(evidence)["valid"] is False
