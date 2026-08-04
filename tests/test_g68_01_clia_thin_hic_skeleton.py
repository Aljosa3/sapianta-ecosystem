from __future__ import annotations

import ast
from collections.abc import Callable
import importlib
import json
from pathlib import Path
import subprocess

import pytest

from aigol.cli.clia import presentation, session, transport
from aigol.runtime.models import FailClosedRuntimeError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _open_session(identity: str = "CLIA-TEST-SESSION") -> session.CliaTransportSession:
    value = session.create_clia_transport_session_v1(
        transport_session_identity=identity,
        human_actor_reference="HUMAN-TEST",
        workspace_reference="/workspace",
        runtime_root_reference="/runtime",
        created_at="2026-08-04T00:00:00Z",
    )
    session.open_clia_transport_session_v1(value)
    return value


def _che_response(arguments: dict, **extra) -> dict:
    return {
        **arguments["presentation"],
        "canonical_runtime_entry_service_version": "CHE-V1",
        "canonical_runtime_entry_interface": arguments["interface_name"],
        "canonical_runtime_entry_session_id": arguments["session_id"],
        "canonical_runtime_entry_status": "CHE-RETURNED",
        **extra,
    }


def _reader(values: list[str]) -> tuple[Callable[[str], str], list[str]]:
    iterator = iter(values)
    prompts: list[str] = []

    def read(prompt: str) -> str:
        prompts.append(prompt)
        return next(iterator)

    return read, prompts


def test_executable_identity_and_transport_only_help() -> None:
    result = subprocess.run(
        [str(REPOSITORY_ROOT / "clia"), "--help"],
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert "Development-only thin CLI Human Interaction Channel transport" in result.stdout
    assert "Canonical Human Entry" in result.stdout
    for forbidden in (
        "/approve",
        "/confirm",
        "/satisfied",
        "/attach",
        "provider command",
        "CRO command",
    ):
        assert forbidden not in result.stdout


def test_one_exact_human_act_calls_only_che_once(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_che(**kwargs):
        calls.append(kwargs)
        return _che_response(kwargs, owner_message="exact owner response")

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    result = transport.submit_clia_human_act_v1(
        session=value,
        human_act="action: create",
    )

    assert len(calls) == 1
    assert calls[0]["interface_name"] == session.CLIA_INTERFACE_NAME
    assert calls[0]["session_id"] == value.transport_session_identity
    assert calls[0]["human_requests"] == ["action: create"]
    assert calls[0]["g31_human_actor_id"] == "HUMAN-TEST"
    assert callable(calls[0]["governed_runtime_runner"])
    assert result.che_response["owner_message"] == "exact owner response"
    assert value.next_submission_sequence == 2
    assert value.status is session.CliaTransportStatus.OPEN


def test_terminal_prompt_and_send_control_are_not_part_of_human_act(monkeypatch) -> None:
    acts: list[list[str]] = []

    def fake_che(**kwargs):
        acts.append(kwargs["human_requests"])
        return _che_response(kwargs)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    read, prompts = _reader(["action: create", "/send", "/exit"])
    output: list[str] = []
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=output.append,
    )

    assert acts == [["action: create"]]
    assert prompts == ["clia> ", "... ", "clia> "]
    assert all("clia>" not in act and "/send" not in act for act in acts[0])
    assert value.status is session.CliaTransportStatus.CLOSED


def test_multiline_human_act_preserves_exact_order_and_content(monkeypatch) -> None:
    acts: list[str] = []

    def fake_che(**kwargs):
        acts.extend(kwargs["human_requests"])
        return _che_response(kwargs)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    read, _ = _reader(["first line", "  second line  ", "third: value", "/send", "/exit"])
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=lambda _value: None,
    )
    assert acts == ["first line\n  second line  \nthird: value"]


def test_empty_submission_rejected_without_che_invocation(monkeypatch) -> None:
    calls = 0

    def fake_che(**_kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("CHE must not be called")

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    read, _ = _reader(["/send", "/exit"])
    output: list[str] = []
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=output.append,
    )
    assert calls == 0
    assert any("empty submission rejected" in line for line in output)


def test_cancel_clears_only_unsent_buffer_and_invokes_no_runtime(monkeypatch) -> None:
    monkeypatch.setattr(
        transport,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected CHE call")),
    )
    value = _open_session()
    read, _ = _reader(["unsent", "/cancel", "/exit"])
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=lambda _value: None,
    )
    assert value.pending_input_lines == []
    assert value.last_submission_identity is None
    assert value.status is session.CliaTransportStatus.CLOSED


def test_exit_closes_transport_without_runtime_invocation(monkeypatch) -> None:
    monkeypatch.setattr(
        transport,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected CHE call")),
    )
    value = _open_session()
    read, _ = _reader(["/exit"])
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=lambda _value: None,
    )
    assert value.status is session.CliaTransportStatus.CLOSED


def test_keyboard_interrupt_is_deterministic_and_fabricates_no_result(monkeypatch) -> None:
    monkeypatch.setattr(
        transport,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected CHE call")),
    )
    value = _open_session()
    output: list[str] = []

    def interrupt(_prompt: str) -> str:
        raise KeyboardInterrupt

    returned = transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=interrupt,
        output_writer=output.append,
    )
    assert returned is value
    assert value.status is session.CliaTransportStatus.INTERRUPTED
    assert value.last_submission_identity is None
    assert output[-1] == "CLIA transport interrupted; no Human act was submitted."


def test_main_returns_interrupted_terminal_status() -> None:
    clia_main = importlib.import_module("aigol.cli.clia.main")

    def interrupt(_prompt: str) -> str:
        raise KeyboardInterrupt

    assert clia_main.main([], input_reader=interrupt, output_writer=lambda _value: None) == 130


def test_end_of_file_closes_without_submitting_unsent_input(monkeypatch) -> None:
    monkeypatch.setattr(
        transport,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected CHE call")),
    )
    value = _open_session()
    read, _ = _reader(["unsent input"])
    output: list[str] = []
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=output.append,
    )
    assert value.status is session.CliaTransportStatus.CLOSED
    assert value.last_submission_identity is None
    assert output[-1] == "CLIA transport closed on end-of-file; unsent input was discarded."


def test_one_send_creates_one_invocation_and_second_empty_send_does_not(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_che(**kwargs):
        calls.append(kwargs)
        return _che_response(kwargs)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    read, _ = _reader(["one act", "/send", "/send", "/exit"])
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=lambda _value: None,
    )
    assert len(calls) == 1
    assert calls[0]["human_requests"] == ["one act"]


def test_unknown_delivery_fails_closed_and_never_retries(monkeypatch) -> None:
    calls = 0

    def uncertain_che(**_kwargs):
        nonlocal calls
        calls += 1
        raise TimeoutError("outcome unknown")

    monkeypatch.setattr(
        transport, "run_human_interface_runtime_entry", uncertain_che
    )
    value = _open_session()
    with pytest.raises(transport.CliaDeliveryUncertainError):
        transport.submit_clia_human_act_v1(session=value, human_act="one act")
    assert calls == 1
    assert value.status is session.CliaTransportStatus.TRANSPORT_FAILED_CLOSED
    assert value.active_submission_identity is not None

    with pytest.raises(FailClosedRuntimeError):
        transport.submit_clia_human_act_v1(session=value, human_act="one act")
    assert calls == 1


def test_main_returns_failed_closed_terminal_status(monkeypatch) -> None:
    clia_main = importlib.import_module("aigol.cli.clia.main")

    def uncertain_che(**_kwargs):
        raise TimeoutError("outcome unknown")

    monkeypatch.setattr(
        transport, "run_human_interface_runtime_entry", uncertain_che
    )
    read, _ = _reader(["one act", "/send"])
    assert clia_main.main([], input_reader=read, output_writer=lambda _value: None) == 2


def test_response_fidelity_preserves_all_che_data(monkeypatch) -> None:
    exact_payload = {
        "owner_message": "REFUSED: exact owner text",
        "pending": True,
        "nested": {"values": [3, 2, 1], "next": None},
    }

    def fake_che(**kwargs):
        return _che_response(kwargs, **exact_payload)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    result = transport.submit_clia_human_act_v1(
        session=_open_session(), human_act="request"
    )
    heading, body = result.presentation.split("\n", 1)
    assert heading == presentation.CLIA_RESPONSE_HEADING
    assert json.loads(body) == result.che_response
    assert {key: result.che_response[key] for key in exact_payload} == exact_payload


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        [],
        {},
        {"canonical_runtime_entry_status": "SUCCESS"},
    ],
)
def test_malformed_che_response_fails_closed(monkeypatch, malformed) -> None:
    monkeypatch.setattr(
        transport,
        "run_human_interface_runtime_entry",
        lambda **_kwargs: malformed,
    )
    value = _open_session()
    with pytest.raises(FailClosedRuntimeError):
        transport.submit_clia_human_act_v1(session=value, human_act="request")
    assert value.status is session.CliaTransportStatus.TRANSPORT_FAILED_CLOSED


def test_identical_inputs_and_che_responses_render_byte_identically(monkeypatch) -> None:
    def fake_che(**kwargs):
        return _che_response(kwargs, owner_message="same", sequence=[1, 2])

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    first = transport.submit_clia_human_act_v1(
        session=_open_session("SAME-SESSION"), human_act="same act"
    )
    second = transport.submit_clia_human_act_v1(
        session=_open_session("SAME-SESSION"), human_act="same act"
    )
    assert first.presentation.encode("utf-8") == second.presentation.encode("utf-8")
    assert first.che_response == second.che_response


def test_malformed_local_transport_state_fails_before_che(monkeypatch) -> None:
    calls = 0

    def fake_che(**_kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("CHE must not be called")

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fake_che)
    value = _open_session()
    value.pending_input_lines = [object()]  # type: ignore[list-item]
    with pytest.raises(FailClosedRuntimeError):
        session.append_clia_input_line_v1(value, "new")
    assert calls == 0
    assert value.status is session.CliaTransportStatus.TRANSPORT_FAILED_CLOSED


def test_import_and_owner_isolation() -> None:
    package_root = REPOSITORY_ROOT / "aigol" / "cli" / "clia"
    imported_modules: set[str] = set()
    source = ""
    for path in sorted(package_root.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        source += text
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

    runtime_imports = {
        name for name in imported_modules if name.startswith("aigol.runtime")
    }
    assert runtime_imports == {
        "aigol.runtime.human_interface_runtime_entry_service",
        "aigol.runtime.models",
    }
    for forbidden in (
        "aigol.cli.aicli",
        "aigol.cli.aigol_cli",
        "aigol.acli_next",
        "sapianta_bridge",
        "conversation_interpreter",
        "platform_core",
        "governance",
        "authorization",
        "worker",
        "provider",
        "replay",
        "certification",
        "constitutional_runtime_observatory",
    ):
        assert forbidden not in imported_modules
    assert source.count("run_human_interface_runtime_entry(") == 1


def test_existing_cli_defaults_are_not_redirected_to_clia() -> None:
    existing_sources = [
        REPOSITORY_ROOT / "aicli",
        REPOSITORY_ROOT / "aigol" / "cli" / "aicli.py",
        REPOSITORY_ROOT / "aigol" / "cli" / "aigol_cli.py",
    ]
    for path in existing_sources:
        source = path.read_text(encoding="utf-8")
        assert "aigol.cli.clia" not in source
        assert "from .clia" not in source
    assert transport.CLIA_DEVELOPMENT_STATUS == (
        "CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER"
    )
    assert (REPOSITORY_ROOT / "clia").exists()
    assert (REPOSITORY_ROOT / "aicli").exists()


def test_development_executable_adds_no_certified_production_path() -> None:
    assert session.CLIA_DEVELOPMENT_STATUS.endswith("NOT_PRODUCTION_CUTOVER")
    assert session.CLIA_INTERFACE_NAME == "CLIA"
    source = (REPOSITORY_ROOT / "aigol" / "cli" / "clia" / "transport.py").read_text(
        encoding="utf-8"
    )
    assert "_development_only_governed_runtime_runner" in source
    assert "run_human_interface_runtime_entry(" in source
    assert "run_hir_conversation" not in source
    assert "compose_production_conversation" not in source
