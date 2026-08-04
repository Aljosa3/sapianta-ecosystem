from __future__ import annotations

import hashlib
from io import StringIO
import json
from pathlib import Path
import runpy
import subprocess

import pytest

from aigol.runtime.constitutional_runtime_observatory import composition
from aigol.runtime.models import FailClosedRuntimeError


@pytest.fixture(scope="module")
def evidence(tmp_path_factory: pytest.TempPathFactory) -> dict:
    helpers = runpy.run_path(
        str(
            Path(__file__).with_name(
                "test_g67_02_constitutional_runtime_observatory_core.py"
            )
        )
    )
    base = tmp_path_factory.mktemp("g67_05_passive_composition")
    return helpers["_build_source"](
        base / "runtime",
        base / "workspace",
        base / "artifact",
    )


def _compose_arguments(evidence: dict, command: str = "summary") -> dict:
    return {
        "evidence_scope_root": evidence["scope"],
        "evidence_roots": evidence["roots"],
        "selector": evidence["selector"],
        "command": command,
    }


def _cli_arguments(evidence: dict, command: str = "summary") -> list[str]:
    arguments = ["--evidence-scope-root", str(evidence["scope"])]
    for descriptor in evidence["roots"]:
        arguments.extend(
            [
                "--evidence-root",
                f"{descriptor['adapter_id']}={descriptor['path']}",
            ]
        )
    for key in composition.REQUIRED_SELECTOR_KEYS:
        arguments.extend(["--selector", f"{key}={evidence['selector'][key]}"])
    arguments.append(command)
    return arguments


def _byte_snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_version_and_explicit_terminal_grammar() -> None:
    assert composition.CRO_PASSIVE_COMPOSITION_VERSION == (
        "G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_V1"
    )
    parser = composition.build_cro_composition_parser()
    parsed = parser.parse_args(
        [
            "--evidence-scope-root",
            "/bounded",
            "--evidence-root",
            "G66_FLOW_BINDING=/bounded/flow",
            "--selector",
            "session_id=SESSION-1",
            "--selector",
            "commitment_identity=COMMITMENT-1",
            "--selector",
            "human_actor=HUMAN_OPERATOR",
            "summary",
        ]
    )
    assert parsed.evidence_scope_root == "/bounded"
    assert parsed.evidence_root == ["G66_FLOW_BINDING=/bounded/flow"]
    assert parsed.command == "summary"


def test_composition_calls_only_g67_02_then_g67_03_then_g67_04(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls = []
    projection = {"projection": "G67-02"}
    journey = object()
    output = StringIO()

    def g67_02(**kwargs):
        calls.append(("G67-02", kwargs))
        return projection

    def g67_03(*, journey_projection):
        calls.append(("G67-03", journey_projection))
        return journey

    def g67_04(*, journey: object, argv: list[str], output):
        calls.append(("G67-04", journey, argv, output))
        return 0

    monkeypatch.setattr(
        composition,
        "build_constitutional_human_intent_journey_v1",
        g67_02,
    )
    monkeypatch.setattr(composition, "build_journey", g67_03)
    monkeypatch.setattr(composition, "run_cro_cli_transport", g67_04)

    evidence_path = tmp_path / "flow"
    assert composition.compose_passive_cro_observation(
        evidence_scope_root=tmp_path,
        evidence_roots=[
            {"adapter_id": "G66_FLOW_BINDING", "path": evidence_path}
        ],
        selector={
            "session_id": "SESSION-1",
            "commitment_identity": "COMMITMENT-1",
            "human_actor": "HUMAN_OPERATOR",
        },
        command="summary",
        output=output,
    ) == 0

    assert [call[0] for call in calls] == ["G67-02", "G67-03", "G67-04"]
    assert calls[0][1] == {
        "evidence_scope_root": str(tmp_path),
        "evidence_roots": (
            {
                "adapter_id": "G66_FLOW_BINDING",
                "path": str(evidence_path),
            },
        ),
        "selector": {
            "session_id": "SESSION-1",
            "commitment_identity": "COMMITMENT-1",
            "human_actor": "HUMAN_OPERATOR",
        },
    }
    assert calls[1] == ("G67-03", projection)
    assert calls[2] == ("G67-04", journey, ["summary"], output)


@pytest.mark.parametrize(
    ("scope", "roots", "selector", "match"),
    [
        (
            "relative",
            [{"adapter_id": "A", "path": "/bounded/a"}],
            {
                "session_id": "S",
                "commitment_identity": "C",
                "human_actor": "H",
            },
            "explicit absolute path",
        ),
        (
            "/bounded",
            [{"adapter_id": "A", "path": "/bounded/*"}],
            {
                "session_id": "S",
                "commitment_identity": "C",
                "human_actor": "H",
            },
            "wildcard syntax",
        ),
        (
            "/bounded",
            [],
            {
                "session_id": "S",
                "commitment_identity": "C",
                "human_actor": "H",
            },
            "explicit evidence-root descriptors",
        ),
        (
            "/bounded",
            [
                {"adapter_id": "A", "path": "/bounded/a"},
                {"adapter_id": "A", "path": "/bounded/b"},
            ],
            {
                "session_id": "S",
                "commitment_identity": "C",
                "human_actor": "H",
            },
            "adapter identities must be unique",
        ),
        (
            "/bounded",
            [{"adapter_id": "A", "path": "/bounded/a"}],
            {"session_id": "S", "commitment_identity": "C"},
            "exact session, Commitment, and Human selectors",
        ),
        (
            "/bounded",
            [{"adapter_id": "A", "path": "/bounded/a"}],
            {
                "session_id": "S*",
                "commitment_identity": "C",
                "human_actor": "H",
            },
            "must not contain wildcard syntax",
        ),
    ],
)
def test_implicit_or_ambiguous_input_fails_before_g67_02(
    monkeypatch,
    scope,
    roots,
    selector,
    match: str,
) -> None:
    def forbidden(**_kwargs):
        raise AssertionError("G67-02 must not run")

    monkeypatch.setattr(
        composition,
        "build_constitutional_human_intent_journey_v1",
        forbidden,
    )
    with pytest.raises(FailClosedRuntimeError, match=match):
        composition.compose_passive_cro_observation(
            evidence_scope_root=scope,
            evidence_roots=roots,
            selector=selector,
            command="summary",
            output=StringIO(),
        )


def test_real_pipeline_is_deterministic_and_preserves_evidence(
    evidence: dict,
    monkeypatch,
) -> None:
    original_builder = composition.build_constitutional_human_intent_journey_v1
    original_query = composition.build_journey
    intermediate_identities = []

    def observed_builder(**kwargs):
        projection = original_builder(**kwargs)
        intermediate_identities.append(("journey", projection["projection_hash"]))
        return projection

    def observed_query(*, journey_projection):
        journey = original_query(journey_projection=journey_projection)
        intermediate_identities.append(
            ("query", journey.get_metadata()["source_projection_hash"])
        )
        return journey

    monkeypatch.setattr(
        composition,
        "build_constitutional_human_intent_journey_v1",
        observed_builder,
    )
    monkeypatch.setattr(composition, "build_journey", observed_query)

    before = _byte_snapshot(evidence["scope"])
    first = StringIO()
    second = StringIO()
    assert composition.compose_passive_cro_observation(
        **_compose_arguments(evidence),
        output=first,
    ) == 0
    assert composition.compose_passive_cro_observation(
        **_compose_arguments(evidence),
        output=second,
    ) == 0

    assert first.getvalue() == second.getvalue()
    assert intermediate_identities[0] == intermediate_identities[2]
    assert intermediate_identities[1] == intermediate_identities[3]
    assert intermediate_identities[0][1] == intermediate_identities[1][1]
    rendered = json.loads(first.getvalue())
    assert rendered["event_count"] == 35
    assert rendered["decision_count"] == 14
    assert rendered["terminal_classification"] == "FINAL_EXECUTION_CERTIFIED"
    assert _byte_snapshot(evidence["scope"]) == before


def test_main_composes_explicit_arguments(evidence: dict) -> None:
    output = StringIO()
    assert composition.main(_cli_arguments(evidence, "current"), output=output) == 0
    rendered = json.loads(output.getvalue())
    assert rendered["stage"] == "FINAL_EXECUTION_CERTIFICATION"
    assert rendered["stage_state"] == "REACHED"


@pytest.mark.parametrize(
    "arguments",
    [
        [
            "--evidence-scope-root",
            "/bounded",
            "--evidence-root",
            "A=/bounded/a",
            "--selector",
            "session_id=S-1",
            "--selector",
            "session_id=S-2",
            "--selector",
            "commitment_identity=C",
            "--selector",
            "human_actor=H",
            "summary",
        ],
        [
            "--evidence-scope-root",
            "/bounded",
            "--evidence-root",
            "MALFORMED",
            "--selector",
            "session_id=S",
            "--selector",
            "commitment_identity=C",
            "--selector",
            "human_actor=H",
            "summary",
        ],
    ],
)
def test_terminal_assignment_errors_fail_before_g67_02(
    arguments: list[str],
    monkeypatch,
) -> None:
    def forbidden(**_kwargs):
        raise AssertionError("G67-02 must not run")

    monkeypatch.setattr(
        composition,
        "build_constitutional_human_intent_journey_v1",
        forbidden,
    )
    with pytest.raises(SystemExit) as failure:
        composition.main(arguments, output=StringIO())
    assert failure.value.code == 2


def test_repository_cro_launcher_executes_passive_pipeline(evidence: dict) -> None:
    repository = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [str(repository / "cro"), *_cli_arguments(evidence, "validation")],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert completed.stderr == ""
    rendered = json.loads(completed.stdout)
    assert rendered["query_rebuilt_journey"] is False
    assert rendered["query_invoked_runtime"] is False
    assert rendered["source_validation_summary"]["runtime_events_projected"] == 35


def test_composition_source_contains_only_certified_layer_imports() -> None:
    source = Path(
        "aigol/runtime/constitutional_runtime_observatory/composition.py"
    ).read_text(encoding="utf-8")
    assert "from .core import build_constitutional_human_intent_journey_v1" in source
    assert "from .query import build_journey" in source
    assert "from .cli_transport import run_cro_cli_transport" in source
    for forbidden in (
        "glob(",
        "rglob(",
        "os.walk",
        "transport.replay",
        "governance",
        "authorization",
        "worker",
        "provider",
        "platform_core",
        "conversation",
        "human_interface",
    ):
        assert forbidden not in source.lower()
