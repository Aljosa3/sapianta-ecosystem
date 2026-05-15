from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_evidence import terminal_attachment_evidence


def test_terminal_attachment_evidence_records_bounded_terminal_continuity():
    evidence = terminal_attachment_evidence(
        binding={"terminal_attachment_session_id": "TERM-1", "stdin_binding_id": "STDIN-1", "stdout_binding_id": "STDOUT-1"},
        valid=True,
        states=("TERMINAL_ATTACHMENT_CREATED",),
    )
    assert evidence["stdin_bounded"] is True
    assert evidence["stdout_bounded"] is True
    assert evidence["continuity_fabricated"] is False
