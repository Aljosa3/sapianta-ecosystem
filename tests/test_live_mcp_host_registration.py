from sapianta_system.runtime.mcp_wrapper.live_mcp_server import (
    LIVE_MCP_CONNECTOR_PATH,
    LIVE_MCP_SERVER_NAME,
    LIVE_MCP_TRANSPORT,
    build_live_mcp_server,
)


class _FakeFastMCP:
    def __init__(self, name, json_response):
        self.name = name
        self.json_response = json_response
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


def _returned_response():
    return {
        "status": "RETURNED",
        "closure": "PASS",
        "request_id": "REQ-1",
        "response_id": "RESP-1",
        "replay_identity": "REPLAY-1",
        "evidence": {"localhost_only": True, "response_returned": True, "replay_safe": True},
    }


def test_live_host_advertises_exactly_one_tool():
    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP, handler=lambda payload: _returned_response())
    assert server.name == LIVE_MCP_SERVER_NAME
    assert server.json_response is True
    assert list(server.tools) == ["sapianta_governed_invoke"]


def test_live_host_tool_name_is_sapianta_governed_invoke():
    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP, handler=lambda payload: _returned_response())
    assert "sapianta_governed_invoke" in server.tools


def test_valid_tool_call_uses_existing_bridge_handler_shape():
    seen = {}

    def handler(payload):
        seen.update(payload)
        return _returned_response()

    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP, handler=handler)
    result = server.tools["sapianta_governed_invoke"]("TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1")
    assert seen == {
        "artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        "host": "127.0.0.1",
        "port": 8110,
    }
    assert result == _returned_response()


def test_invalid_input_fails_closed_through_existing_handler():
    server = build_live_mcp_server(
        fastmcp_cls=_FakeFastMCP,
    )
    assert server.tools["sapianta_governed_invoke"]("")["status"] == "BLOCKED"


def test_non_localhost_target_is_rejected():
    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP)
    result = server.tools["sapianta_governed_invoke"]("ARTIFACT", host="0.0.0.0")
    assert result["status"] == "BLOCKED"


def test_response_shape_is_deterministic():
    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP, handler=lambda payload: _returned_response())
    first = server.tools["sapianta_governed_invoke"]("ARTIFACT")
    second = server.tools["sapianta_governed_invoke"]("ARTIFACT")
    assert first == second


def test_no_extra_tools_are_exposed():
    server = build_live_mcp_server(fastmcp_cls=_FakeFastMCP, handler=lambda payload: _returned_response())
    assert len(server.tools) == 1


def test_host_surface_has_no_retry_fallback_or_orchestration_contract():
    assert LIVE_MCP_TRANSPORT == "streamable-http"
    assert LIVE_MCP_CONNECTOR_PATH == "/mcp"
