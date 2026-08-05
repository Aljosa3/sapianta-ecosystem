from __future__ import annotations

import ast
from collections.abc import Callable
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import pytest

from aigol.cli.clia import presentation, session, transport


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INITIAL_REQUEST_LINES = [
    "Create a governed documentation improvement.",
    (
        "The objective is to add one authenticated reference section to an "
        "existing constitutional document."
    ),
    "The exact implementation details will be clarified during conversation.",
]
INITIAL_REQUEST = "\n".join(INITIAL_REQUEST_LINES)
ACTION_ACT = "action: create"
SUBJECT_ACT = (
    "subject: one authenticated reference section in an existing "
    "constitutional document"
)


def _reader(values: list[str]) -> tuple[Callable[[str], str], list[str]]:
    iterator = iter(values)
    prompts: list[str] = []

    def read(prompt: str) -> str:
        prompts.append(prompt)
        return next(iterator)

    return read, prompts


def _new_session(tmp_path: Path, identity: str) -> session.CliaTransportSession:
    runtime_root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    runtime_root.mkdir(parents=True)
    workspace.mkdir(parents=True)
    return session.create_clia_transport_session_v1(
        transport_session_identity=identity,
        human_actor_reference="HUMAN-G68-03",
        workspace_reference=str(workspace),
        runtime_root_reference=str(runtime_root),
        created_at="2026-08-04T00:00:00Z",
    )


def _responses(output: list[str]) -> list[dict]:
    prefix = presentation.CLIA_RESPONSE_HEADING + "\n"
    return [json.loads(value[len(prefix) :]) for value in output if value.startswith(prefix)]


def _required_field(response: dict) -> str:
    return response["owner_transition"]["permitted_controls"][0]


def _binding(response: dict) -> dict:
    return response["owner_projection"]


def _repository_source_snapshot() -> dict[str, str]:
    paths = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        check=True,
    ).stdout.split(b"\0")
    snapshot: dict[str, str] = {}
    for raw_path in paths:
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8")
        path = REPOSITORY_ROOT / relative
        if path.is_file():
            snapshot[relative] = sha256(path.read_bytes()).hexdigest()
    return snapshot


def _run_real_interaction(
    *,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    identity: str,
    inputs: list[str],
) -> tuple[session.CliaTransportSession, list[dict], list[dict], list[str], list[str]]:
    exact_che = transport.run_human_interface_runtime_entry
    calls: list[dict] = []

    def observed_che(**kwargs):
        calls.append(
            {
                "request_envelope": kwargs["request_envelope"].to_dict(),
                "continuation_envelope": (
                    kwargs["continuation_envelope"].to_dict()
                    if kwargs["continuation_envelope"] is not None
                    else None
                ),
                "governed_runtime_runner": kwargs["governed_runtime_runner"],
            }
        )
        return exact_che(**kwargs)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    value = _new_session(tmp_path, identity)
    read, prompts = _reader(inputs)
    output: list[str] = []
    returned = transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=output.append,
    )
    return returned, _responses(output), calls, prompts, output


def test_real_clia_multiturn_conversation_advances_action_subject_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = _repository_source_snapshot()
    returned, responses, calls, prompts, _output = _run_real_interaction(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        identity="CLIA-G68-03-REAL",
        inputs=[
            *INITIAL_REQUEST_LINES,
            "/send",
            ACTION_ACT,
            "/send",
            SUBJECT_ACT,
            "/send",
            "/exit",
        ],
    )
    after = _repository_source_snapshot()

    assert before == after
    assert returned.status is session.CliaTransportStatus.CLOSED
    assert len(calls) == 3
    assert [call["request_envelope"]["source_payload"] for call in calls] == [
        INITIAL_REQUEST,
        ACTION_ACT,
        SUBJECT_ACT,
    ]
    assert all(
        call["request_envelope"]["session_identity"] == "CLIA-G68-03-REAL"
        for call in calls
    )
    assert calls[0]["continuation_envelope"] is None
    assert all(call["continuation_envelope"] is not None for call in calls[1:])
    assert all(
        call["governed_runtime_runner"] is transport.reject_hic_owned_workflow_v1
        for call in calls
    )
    for call in calls:
        exact_act = call["request_envelope"]["source_payload"]
        assert "clia>" not in exact_act
        assert "/send" not in exact_act
        assert presentation.CLIA_RESPONSE_HEADING not in exact_act

    assert len(responses) == 3
    assert [response["request_identity"] for response in responses] == [
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000001:CHE-REQUEST",
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000002:CHE-REQUEST",
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000003:CHE-REQUEST",
    ]
    assert all(
        response["continuation_envelope"]["session_identity"]
        == "CLIA-G68-03-REAL"
        for response in responses
    )

    bindings = [_binding(response) for response in responses]
    conversation_identities = {
        response["continuation_envelope"]["conversation_identity"]
        for response in responses
    }
    assert len(conversation_identities) == 1
    revisions = [binding["owner_revision"] for binding in bindings]
    assert revisions[0] < revisions[1] < revisions[2]
    assert [_required_field(response) for response in responses] == [
        "action: <value>",
        "subject: <value>",
        "outcome: <value>",
    ]
    clarification_ids = [
        response["continuation_envelope"]["expected_next_act_identity"]
        for response in responses
    ]
    assert len(set(clarification_ids)) == 3
    assert all(
        response["owner_transition"]["exact_human_act_required"] is True
        for response in responses
    )
    assert all(
        response["producing_owner"] == "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
        and response["common_failure"] is None
        for response in responses
    )
    assert all(
        binding["owner_terminal_state"]["terminal"] is False
        for binding in bindings
    )
    assert all("workflow" not in response for response in responses)
    assert all("semantic" not in response for response in responses)
    assert prompts == ["clia> ", "... ", "... ", "... ", "clia> ", "... ", "clia> ", "... ", "clia> "]


def test_malformed_continuation_is_refused_at_conversation_reply_consumption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    malformed = "action create"
    returned, responses, calls, _prompts, _output = _run_real_interaction(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        identity="CLIA-G68-03-MALFORMED",
        inputs=[*INITIAL_REQUEST_LINES, "/send", malformed, "/send", "/exit"],
    )

    assert returned.status is session.CliaTransportStatus.CLOSED
    assert [call["request_envelope"]["source_payload"] for call in calls] == [
        INITIAL_REQUEST,
        malformed,
    ]
    assert len(responses) == 2
    initial_binding = _binding(responses[0])
    malformed_binding = _binding(responses[1])
    assert malformed_binding["owner_state"] == initial_binding["owner_state"]
    assert malformed_binding["owner_revision"] == initial_binding["owner_revision"]
    assert _required_field(responses[1]) == "action: <value>"
    assert responses[1]["continuation_envelope"][
        "expected_next_act_identity"
    ] == responses[0]["continuation_envelope"]["expected_next_act_identity"]
    assert responses[1]["advancement_state"] == "REFUSED"


def test_clia_source_remains_transport_only_and_calls_che_only() -> None:
    package_root = REPOSITORY_ROOT / "aigol" / "cli" / "clia"
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(package_root.glob("*.py"))
    )
    transport_source = (package_root / "transport.py").read_text(encoding="utf-8")
    tree = ast.parse(transport_source)
    calls = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]

    assert calls.count("run_human_interface_runtime_entry") == 1
    assert "authenticated_human_interaction_runtime" not in calls
    for forbidden in (
        "action:",
        "subject:",
        "outcome:",
        "work-type:",
        "OPERATIVE_ACTION",
        "OPERATIVE_SUBJECT",
        "DESIRED_OUTCOME",
        "WORK_TYPE",
        "compose_production_conversation_flow_binding",
        "constitutional_runtime_observatory",
    ):
        assert forbidden not in source


def test_controlled_fixed_owner_responses_render_deterministically(
    tmp_path: Path,
) -> None:
    value = _new_session(tmp_path, "CLIA-G68-03-FIXED")
    read, _prompts = _reader(["same exact act", "/send", "/exit"])
    output: list[str] = []
    transport.run_clia_interactive_session_v1(
        session=value,
        input_reader=read,
        output_writer=output.append,
    )
    response = _responses(output)[0]
    first = presentation.render_clia_che_response_v1(response).encode("utf-8")
    second = presentation.render_clia_che_response_v1(response).encode("utf-8")
    assert first == second


def test_production_launchers_routes_and_development_classification_are_unchanged() -> None:
    for relative in (
        "aicli",
        "aigol/cli/aicli.py",
        "aigol/cli/aigol_cli.py",
        "aigol/acli_next/entrypoint.py",
        "clia",
    ):
        committed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=REPOSITORY_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        assert (REPOSITORY_ROOT / relative).read_text(encoding="utf-8") == committed
    assert session.CLIA_DEVELOPMENT_STATUS == (
        "CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER"
    )


def test_existing_g66_flow_evidence_is_statically_cro_addressable() -> None:
    catalog_source = (
        REPOSITORY_ROOT
        / "aigol"
        / "runtime"
        / "constitutional_runtime_observatory"
        / "catalog.py"
    ).read_text(encoding="utf-8")
    assert '"G66_FLOW_BINDING"' in catalog_source
    assert '"PRODUCTION_CONVERSATION_FLOW_BINDING_V1"' in catalog_source
    assert "reconstruct_production_conversation_flow_binding_v1" in catalog_source
