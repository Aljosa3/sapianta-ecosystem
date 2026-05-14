from sapianta_bridge.no_copy_paste_loop.loop_binding import validate_loop_binding
from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop


def test_loop_binding_preserves_lineage_continuity() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    binding = output["loop_binding"]

    assert binding["loop_id"].startswith("NO-COPY-LOOP-")
    assert binding["bridge_id"] == output["bridge_output"]["bridge_binding"]["bridge_id"]
    assert binding["session_id"] == output["bridge_output"]["bridge_response"]["session_id"]
    assert binding["invocation_id"] == output["bridge_output"]["bridge_response"]["invocation_id"]
    assert validate_loop_binding(binding)["valid"] is True


def test_loop_binding_rejects_invalid_replay_binding() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    binding = output["loop_binding"]
    binding["binding_sha256"] = "bad-hash"

    assert validate_loop_binding(binding)["valid"] is False
