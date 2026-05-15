from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_state import LIVE_REQUEST_INGESTION_STATES, SUCCESS_PATH


def test_live_request_ingestion_states_are_bounded():
    assert SUCCESS_PATH == LIVE_REQUEST_INGESTION_STATES[:7]
    assert LIVE_REQUEST_INGESTION_STATES[-2:] == ("BLOCKED", "FAILED")
