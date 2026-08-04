from __future__ import annotations

import ast
from collections.abc import Callable
import inspect
import json
from pathlib import Path
import subprocess

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.cli.clia import session, transport
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TRANSPORT_PATH = REPOSITORY_ROOT / "aigol" / "cli" / "clia" / "transport.py"


def _open_session(identity: str = "CLIA-G68-02-SESSION") -> session.CliaTransportSession:
    value = session.create_clia_transport_session_v1(
        transport_session_identity=identity,
        human_actor_reference="HUMAN-G68-02",
        workspace_reference="/non-mutating-workspace-reference",
        runtime_root_reference="/non-mutating-runtime-reference",
        created_at="2026-08-04T00:00:00Z",
    )
    session.open_clia_transport_session_v1(value)
    return value


def _che_response(arguments: dict, **extra: object) -> dict:
    return {
        **arguments["presentation"],
        "canonical_runtime_entry_service_version": "CHE-G68-02-TEST",
        "canonical_runtime_entry_interface": arguments["interface_name"],
        "canonical_runtime_entry_session_id": arguments["session_id"],
        "canonical_runtime_entry_status": "CHE-RUNTIME-ENTRY-VERIFIED",
        **extra,
    }


def _transport_imports_and_calls() -> tuple[set[str], list[str]]:
    tree = ast.parse(TRANSPORT_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return imports, calls


def test_clia_passes_the_authenticated_runtime_binding_to_che_once(monkeypatch) -> None:
    calls: list[dict] = []

    def observed_che(**kwargs):
        calls.append(kwargs)
        return _che_response(kwargs)

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    result = transport.submit_clia_human_act_v1(
        session=_open_session(),
        human_act="action: inspect",
    )

    assert len(calls) == 1
    assert calls[0]["governed_runtime_runner"] is run_interactive_conversation
    assert result.che_response["canonical_runtime_entry_status"] == (
        "CHE-RUNTIME-ENTRY-VERIFIED"
    )


def test_instrumented_human_clia_che_hir_conversation_chain_is_exact(monkeypatch) -> None:
    events: list[str] = []

    def conversation_entry() -> dict:
        events.append("Conversation")
        return {
            "entered": True,
            "repository_mutation_reached": False,
            "worker_execution_reached": False,
            "provider_execution_reached": False,
            "replay_generation_reached": False,
            "certification_reached": False,
        }

    def observed_hir(*_args, **_kwargs) -> dict:
        events.append("HIR")
        return conversation_entry()

    def observed_che(**kwargs) -> dict:
        events.append("CHE")
        hir_result = kwargs["governed_runtime_runner"](
            object(), input_func=lambda: "", output_func=lambda _value: None
        )
        return _che_response(kwargs, hir_result=hir_result)

    monkeypatch.setattr(
        transport, "authenticated_human_interaction_runtime", observed_hir
    )
    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    result = transport.submit_clia_human_act_v1(
        session=_open_session(), human_act="exact Human act"
    )

    assert events == ["CHE", "HIR", "Conversation"]
    assert result.che_response["hir_result"] == {
        "entered": True,
        "repository_mutation_reached": False,
        "worker_execution_reached": False,
        "provider_execution_reached": False,
        "replay_generation_reached": False,
        "certification_reached": False,
    }


def test_clia_invokes_only_the_canonical_human_entry_runtime_function() -> None:
    imports, calls = _transport_imports_and_calls()
    assert calls.count("run_human_interface_runtime_entry") == 1
    assert "authenticated_human_interaction_runtime" not in calls
    assert "aigol.cli.aigol_cli" in imports
    assert "aigol.runtime.human_interface_runtime_entry_service" in imports


def test_authenticated_binding_and_che_source_preserve_owner_order() -> None:
    transport_source = TRANSPORT_PATH.read_text(encoding="utf-8")
    che_source = inspect.getsource(run_human_interface_runtime_entry)

    assert "governed_runtime_runner=authenticated_human_interaction_runtime" in (
        transport_source
    )
    assert "compose_production_conversation_flow_binding_v1(" in che_source
    assert "conversation_result = governed_runtime_runner(" in che_source


def test_no_direct_clia_downstream_owner_import_or_call_exists() -> None:
    imports, calls = _transport_imports_and_calls()
    forbidden_fragments = (
        "human_interface_conversation_runtime",
        "production_conversation_flow_binding",
        "proposal",
        "platform_core",
        "governance",
        "authorization",
        "worker",
        "provider",
        "replay",
        "certification",
        "constitutional_runtime_observatory",
    )
    for value in imports:
        if value == "aigol.cli.aigol_cli":
            continue
        assert not any(fragment in value for fragment in forbidden_fragments)
    assert not any(
        any(fragment in call.lower() for fragment in forbidden_fragments)
        for call in calls
    )


def test_runtime_binding_transport_is_deterministic(monkeypatch) -> None:
    def observed_che(**kwargs):
        assert kwargs["governed_runtime_runner"] is run_interactive_conversation
        return _che_response(kwargs, owner_payload={"ordered": [1, 2, 3]})

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    first = transport.submit_clia_human_act_v1(
        session=_open_session("CLIA-G68-02-DETERMINISTIC"), human_act="same"
    )
    second = transport.submit_clia_human_act_v1(
        session=_open_session("CLIA-G68-02-DETERMINISTIC"), human_act="same"
    )

    assert first.presentation.encode("utf-8") == second.presentation.encode("utf-8")
    assert json.loads(first.presentation.split("\n", 1)[1]) == first.che_response


def test_existing_aicli_and_current_production_route_sources_are_unchanged() -> None:
    for relative_path in (
        "aicli",
        "aigol/cli/aicli.py",
        "aigol/cli/aigol_cli.py",
        "aigol/acli_next/entrypoint.py",
    ):
        committed = subprocess.run(
            ["git", "show", f"HEAD:{relative_path}"],
            cwd=REPOSITORY_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        assert (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8") == committed


def test_development_classification_and_entry_points_remain_unchanged() -> None:
    assert session.CLIA_DEVELOPMENT_STATUS == (
        "CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER"
    )
    changed_paths = set(
        subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=REPOSITORY_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
    )
    assert not changed_paths.intersection(
        {
            "aicli",
            "aigol",
            "cro",
            "sapianta",
            "aigol/cli/aicli.py",
            "aigol/cli/aigol_cli.py",
            "aigol/acli_next/entrypoint.py",
        }
    )
    committed_clia = subprocess.run(
        ["git", "show", "HEAD:clia"],
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    assert (REPOSITORY_ROOT / "clia").read_text(encoding="utf-8") == committed_clia
    assert "aigol.cli.clia" not in (
        REPOSITORY_ROOT / "aigol" / "cli" / "aicli.py"
    ).read_text(encoding="utf-8")
