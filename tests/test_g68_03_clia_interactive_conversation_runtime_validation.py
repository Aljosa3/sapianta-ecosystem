from __future__ import annotations

import ast
from collections.abc import Callable
from copy import deepcopy
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
    envelope = response["owner_bound_clarification_envelope"]
    return envelope["required_field_or_evidence_codes"][0]


def _binding(response: dict) -> dict:
    return response["production_conversation_flow_binding"]


def _slot_classes(value: object) -> set[str]:
    found: set[str] = set()

    def visit(item: object) -> None:
        if isinstance(item, dict):
            slot_class = item.get("slot_class")
            if isinstance(slot_class, str):
                found.add(slot_class)
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return found


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
        calls.append(deepcopy(kwargs))
        return exact_che(**kwargs)

    def forbidden_post_admission_runtime(*_args, **_kwargs):
        raise AssertionError("Worker/provider-capable governed runtime was reached")

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    monkeypatch.setattr(
        transport,
        "authenticated_human_interaction_runtime",
        forbidden_post_admission_runtime,
    )
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
    assert [call["human_requests"] for call in calls] == [
        [INITIAL_REQUEST],
        [ACTION_ACT],
        [SUBJECT_ACT],
    ]
    assert all(call["session_id"] == "CLIA-G68-03-REAL" for call in calls)
    for call in calls:
        exact_act = call["human_requests"][0]
        assert "clia>" not in exact_act
        assert "/send" not in exact_act
        assert presentation.CLIA_RESPONSE_HEADING not in exact_act

    assert len(responses) == 3
    assert [response["clia_submission_identity"] for response in responses] == [
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000001",
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000002",
        "CLIA-G68-03-REAL:CLIA-SUBMISSION:000003",
    ]
    assert [response["clia_transport_session_identity"] for response in responses] == [
        "CLIA-G68-03-REAL",
        "CLIA-G68-03-REAL",
        "CLIA-G68-03-REAL",
    ]

    bindings = [_binding(response) for response in responses]
    conversation_identities = {
        binding["conversation_identity"] for binding in bindings
    }
    assert len(conversation_identities) == 1
    revisions = [binding["cwm_revision"] for binding in bindings]
    assert revisions[0] < revisions[1] < revisions[2]
    assert [_required_field(response) for response in responses] == [
        "action: <value>",
        "subject: <value>",
        "outcome: <value>",
    ]
    assert "OPERATIVE_ACTION" in _slot_classes(responses[1])
    assert "OPERATIVE_ACTION" in _slot_classes(responses[2])
    assert "OPERATIVE_SUBJECT" in _slot_classes(responses[2])

    clarification_ids = [
        response["owner_bound_clarification_envelope"]["clarification_identity"]
        for response in responses
    ]
    assert len(set(clarification_ids)) == 3
    assert all(
        "OWNER_BOUND_CLARIFICATION_CONTINUATION"
        in {item["stage"] for item in binding["ordered_predecessor_references"]}
        for binding in bindings[1:]
    )
    assert all(
        response["committed_objective_admission"] is None
        and response["constitutional_execution_spine_completion"] is None
        and response["runtime_entered"] is False
        for response in responses
    )
    assert all(
        binding["authorization_created"] is False
        and binding["execution_invoked"] is False
        and binding["worker_invoked"] is False
        for binding in bindings
    )
    assert responses[1]["canonical_typed_semantic_composition"][
        "provider_assistance_invoked"
    ] is False
    assert responses[2]["canonical_typed_semantic_composition"][
        "provider_assistance_invoked"
    ] is False
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
    assert [call["human_requests"] for call in calls] == [[INITIAL_REQUEST], [malformed]]
    assert len(responses) == 2
    initial_binding = _binding(responses[0])
    malformed_binding = _binding(responses[1])
    assert malformed_binding["conversation_identity"] == initial_binding[
        "conversation_identity"
    ]
    assert malformed_binding["cwm_revision"] == initial_binding["cwm_revision"]
    assert malformed_binding["cwm_state_hash"] == initial_binding["cwm_state_hash"]
    assert _required_field(responses[1]) == "action: <value>"
    assert responses[1]["owner_bound_clarification_envelope"][
        "clarification_identity"
    ] == responses[0]["owner_bound_clarification_envelope"][
        "clarification_identity"
    ]
    assert responses[1]["canonical_typed_semantic_composition"] is None


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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixed_response = {
        "canonical_runtime_entry_service_version": "CHE-FIXED",
        "canonical_runtime_entry_interface": "CLIA",
        "canonical_runtime_entry_session_id": "CLIA-G68-03-FIXED",
        "canonical_runtime_entry_status": "CLARIFICATION",
        "owner_response": {"next_required": "action: <value>", "revision": 1},
    }

    def fixed_che(**kwargs):
        return {**kwargs["presentation"], **fixed_response}

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", fixed_che)
    presentations: list[bytes] = []
    for index in range(2):
        root = tmp_path / str(index)
        value = _new_session(root, "CLIA-G68-03-FIXED")
        read, _prompts = _reader(["same exact act", "/send", "/exit"])
        output: list[str] = []
        transport.run_clia_interactive_session_v1(
            session=value,
            input_reader=read,
            output_writer=output.append,
        )
        presentations.append(
            next(
                item.encode("utf-8")
                for item in output
                if item.startswith(presentation.CLIA_RESPONSE_HEADING)
            )
        )
    assert presentations[0] == presentations[1]


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
