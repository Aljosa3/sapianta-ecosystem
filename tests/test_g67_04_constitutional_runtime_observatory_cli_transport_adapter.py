from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import runpy

import pytest

from aigol.runtime.constitutional_runtime_observatory import build_journey
from aigol.runtime.constitutional_runtime_observatory.cli_transport import (
    CRO_CLI_TRANSPORT_ADAPTER_VERSION,
    SUPPORTED_CRO_COMMANDS,
    build_cro_cli_parser,
    render_cro_query_result,
    run_cro_cli_transport,
)
from aigol.runtime.models import FailClosedRuntimeError


_COMMAND_METHODS = {
    "summary": "get_summary",
    "current": "get_current_state",
    "timeline": "get_timeline",
    "events": "get_events",
    "decisions": "get_decisions",
    "states": "get_states",
    "gaps": "get_gaps",
    "owners": "get_owner_map",
    "metadata": "get_metadata",
    "validation": "get_validation_summary",
    "topology": "get_topology",
    "evidence": "get_evidence_references",
}


def _journey():
    helpers = runpy.run_path(
        str(
            Path(__file__).with_name(
                "test_g67_03_constitutional_runtime_observatory_query_interface.py"
            )
        )
    )
    return build_journey(journey_projection=helpers["_projection"]())


def _plain(result):
    if isinstance(result, tuple):
        return [item.as_dict() for item in result]
    return result.as_dict()


def test_closed_command_grammar_contains_exact_required_commands() -> None:
    assert CRO_CLI_TRANSPORT_ADAPTER_VERSION == (
        "G67_04_CONSTITUTIONAL_RUNTIME_OBSERVATORY_CLI_TRANSPORT_ADAPTER_V1"
    )
    assert SUPPORTED_CRO_COMMANDS == tuple(_COMMAND_METHODS)
    parser = build_cro_cli_parser()
    for command in SUPPORTED_CRO_COMMANDS:
        assert parser.parse_args([command]).command == command


@pytest.mark.parametrize("command", SUPPORTED_CRO_COMMANDS)
def test_every_command_renders_only_its_query_result(command: str) -> None:
    journey = _journey()
    expected = getattr(journey, _COMMAND_METHODS[command])()
    output = StringIO()

    assert run_cro_cli_transport(
        journey=journey,
        argv=[command],
        output=output,
    ) == 0
    assert json.loads(output.getvalue()) == _plain(expected)
    assert output.getvalue() == render_cro_query_result(expected) + "\n"


def test_rendering_is_ascii_text_and_deterministic() -> None:
    journey = _journey()
    result = journey.get_summary()

    first = render_cro_query_result(result)
    second = render_cro_query_result(result)

    assert first == second
    first.encode("ascii")
    assert "\x1b" not in first
    assert not first.endswith("\n")


def test_default_transport_destination_is_terminal_stdout(capsys) -> None:
    journey = _journey()
    expected = render_cro_query_result(journey.get_current_state()) + "\n"

    assert run_cro_cli_transport(journey=journey, argv=["current"]) == 0

    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


def test_command_syntax_fails_closed_before_query(monkeypatch) -> None:
    journey = _journey()
    called = False

    def forbidden_query():
        nonlocal called
        called = True
        raise AssertionError("query must not run")

    monkeypatch.setattr(type(journey), "get_summary", lambda self: forbidden_query())

    with pytest.raises(SystemExit) as unknown:
        run_cro_cli_transport(journey=journey, argv=["unknown"], output=StringIO())
    assert unknown.value.code == 2
    assert called is False

    with pytest.raises(SystemExit) as extra:
        run_cro_cli_transport(
            journey=journey,
            argv=["summary", "extra"],
            output=StringIO(),
        )
    assert extra.value.code == 2
    assert called is False


def test_adapter_requires_existing_g67_03_journey() -> None:
    with pytest.raises(FailClosedRuntimeError, match="existing G67-03 Journey"):
        run_cro_cli_transport(
            journey={},  # type: ignore[arg-type]
            argv=["summary"],
            output=StringIO(),
        )


def test_renderer_rejects_non_query_values() -> None:
    with pytest.raises(FailClosedRuntimeError, match="public query contracts"):
        render_cro_query_result({"invented": "value"})


def test_adapter_does_not_call_g67_02_or_forbidden_runtime_owners(monkeypatch) -> None:
    from aigol.runtime.constitutional_runtime_observatory import core

    journey = _journey()

    def forbidden(*_args, **_kwargs):
        raise AssertionError("forbidden responsibility invoked")

    monkeypatch.setattr(
        core,
        "build_constitutional_human_intent_journey_v1",
        forbidden,
    )
    output = StringIO()
    assert run_cro_cli_transport(
        journey=journey,
        argv=["events"],
        output=output,
    ) == 0
    assert json.loads(output.getvalue()) == _plain(journey.get_events())


def test_adapter_source_has_no_core_evidence_or_production_import() -> None:
    source = Path(
        "aigol/runtime/constitutional_runtime_observatory/cli_transport.py"
    ).read_text(encoding="utf-8")
    assert "from .query import" in source
    for forbidden_import in (
        "from .core import",
        "from .catalog import",
        "from .topology import",
        "transport.replay",
        "governance",
        "authorization",
        "worker",
        "platform_core",
        "conversation",
        "human_interface",
    ):
        assert forbidden_import not in source.lower()


def test_adapter_does_not_change_journey_or_write_repository_files(tmp_path) -> None:
    journey = _journey()
    before = journey.get_summary().as_dict()
    output = StringIO()

    run_cro_cli_transport(journey=journey, argv=["timeline"], output=output)

    assert journey.get_summary().as_dict() == before
    assert list(tmp_path.iterdir()) == []
