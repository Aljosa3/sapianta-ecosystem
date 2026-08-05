from __future__ import annotations

import ast
from collections.abc import Callable
import inspect
import json
from pathlib import Path
import subprocess

from aigol.cli.clia import session, transport
from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    reject_hic_owned_workflow_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
    CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    DELIVERY_NOT_APPLICABLE,
    INFORMATIONAL_DISPOSITION,
    INFORMATIONAL_RESPONSE,
    NOT_ADVANCED,
    NOT_APPLICABLE,
    REFERENCE_NOT_APPLICABLE,
    CanonicalHumanEntryOwnerTransitionV1,
    CanonicalHumanEntryResponseEnvelopeV1,
)
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


def _che_response(
    arguments: dict, **extra: object
) -> CanonicalHumanEntryResponseEnvelopeV1:
    request = arguments["request_envelope"]
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="G68-02-TEST-OWNER",
        owner_state_identity=NOT_APPLICABLE,
        owner_revision_before=NOT_APPLICABLE,
        owner_revision_after=NOT_APPLICABLE,
        response_disposition=INFORMATIONAL_DISPOSITION,
        advancement_outcome=NOT_ADVANCED,
        next_act_identity=None,
        next_act_kind=None,
        next_act_target_identity=None,
        next_act_target_digest=None,
        next_act_expected_owner_revision=NOT_APPLICABLE,
        permitted_controls=(),
        payload_constraints={},
        exact_human_act_required=False,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=None,
        refusal_type=NOT_APPLICABLE,
        refusal_status=NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=NOT_APPLICABLE,
        recovery_requirement=NOT_APPLICABLE,
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity=request.request_identity + ":RESPONSE",
        request_identity=request.request_identity,
        response_type=INFORMATIONAL_RESPONSE,
        producing_owner=transition.producing_owner,
        owner_status="CHE_RUNTIME_ENTRY_VERIFIED",
        advancement_state=NOT_ADVANCED,
        presentation_payload=("Owner response available.",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
            **extra,
        },
        correlation_identity=request.request_identity + ":CORRELATION",
        evidence_references=(),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
    )


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
    assert calls[0]["governed_runtime_runner"] is reject_hic_owned_workflow_v1
    assert result.che_response["owner_status"] == (
        "CHE_RUNTIME_ENTRY_VERIFIED"
    )


def test_instrumented_human_clia_che_hir_conversation_chain_is_exact(monkeypatch) -> None:
    events: list[str] = []

    def observed_che(**kwargs) -> dict:
        events.append("CHE")
        assert kwargs["governed_runtime_runner"] is reject_hic_owned_workflow_v1
        return _che_response(kwargs, owner_chain_selected_by="CHE")

    monkeypatch.setattr(transport, "run_human_interface_runtime_entry", observed_che)
    result = transport.submit_clia_human_act_v1(
        session=_open_session(), human_act="exact Human act"
    )

    assert events == ["CHE"]
    assert result.che_response["presentation_metadata"][
        "owner_chain_selected_by"
    ] == "CHE"


def test_clia_invokes_only_the_canonical_human_entry_runtime_function() -> None:
    imports, calls = _transport_imports_and_calls()
    assert calls.count("run_human_interface_runtime_entry") == 1
    assert "authenticated_human_interaction_runtime" not in calls
    assert "aigol.cli.aigol_cli" not in imports
    assert "aigol.runtime.canonical_human_entry_contract_v1" in imports
    assert "aigol.runtime.human_interface_runtime_entry_service" in imports


def test_authenticated_binding_and_che_source_preserve_owner_order() -> None:
    transport_source = TRANSPORT_PATH.read_text(encoding="utf-8")
    che_source = Path(
        inspect.getsourcefile(run_human_interface_runtime_entry) or ""
    ).read_text(encoding="utf-8")

    assert "governed_runtime_runner=reject_hic_owned_workflow_v1" in (
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
        assert not any(fragment in value for fragment in forbidden_fragments)
    assert not any(
        any(fragment in call.lower() for fragment in forbidden_fragments)
        for call in calls
    )


def test_runtime_binding_transport_is_deterministic(monkeypatch) -> None:
    def observed_che(**kwargs):
        assert kwargs["governed_runtime_runner"] is reject_hic_owned_workflow_v1
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
