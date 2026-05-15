from sapianta_bridge.live_runtime_interaction_attachment.runtime_attachment_request import create_runtime_attachment_request


def test_runtime_attachment_request_preserves_runtime_session():
    request = create_runtime_attachment_request(session={"runtime_attachment_session_id": "A-1", "live_runtime_session_id": "L-1"}).to_dict()
    assert request["live_runtime_session_id"] == "L-1"
