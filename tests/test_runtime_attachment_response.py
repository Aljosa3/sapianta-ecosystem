from sapianta_bridge.live_runtime_interaction_attachment.runtime_attachment_response import create_runtime_attachment_response


def test_runtime_attachment_response_preserves_return_id():
    response = create_runtime_attachment_response(binding={"runtime_attachment_session_id": "A-1", "response_return_id": "R-1"}).to_dict()
    assert response["response_return_id"] == "R-1"
