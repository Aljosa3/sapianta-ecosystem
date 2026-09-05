#!/usr/bin/env python3
"""Repository-only validation for one G77-256IE FUTURE formalization."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[5]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

IE_ROOT = ROOT / ".github/governance/evidence/g77_256ie_future_formalization_v1"
SPEC = IE_ROOT / "G77_256IE_FUTURE_FORMAL_SPECIFICATION_V1.json"
FIXTURE = IE_ROOT / "G77_256IE_FUTURE_TIME_FIXTURE_V1.json"
REDUCTION = IE_ROOT / "G77_256IE_SPCE_TERMINAL_REDUCTION_V1.json"
PRODUCER_PATH = IE_ROOT / "producer/G77_256IE_FUTURE_VECTOR_PRODUCER_V1.py"
REDUCER_PATH = IE_ROOT / "reducer/G77_256IE_FUTURE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
REPORT = ROOT / "docs/governance/G77_256IE_REPOSITORY_ONLY_FUTURE_FORMALIZATION_V1.md"
ID_SELECTION = ROOT / ".github/governance/evidence/g77_256id_post_ic_e05_frontier_selection_v1/G77_256ID_E05_FRONTIER_SELECTION_V1.json"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
SUBSTRATE = ROOT / "tests/p11_da_disposable_substrate_v1.py"
HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
TREE = "2b7617318f402f5148e9ea8dd033870946d17ef7"
SPEC_SHA256 = "368894ef96e89b032f55216b3ee8a97bd3028da8391ae0fe31398d6f52b4a438"
FIXTURE_SHA256 = "6a3aee899acef667fadbc10db1fa70a58e536269917d720e168218bc30dbf00b"
REDUCTION_SHA256 = "158ae00958cd021b3df75a8008ec867d35a4c1d3b3c8432ec0da7eec919cbfd9"
VERDICT = (
    "VERIFIED__G77_256IE_REPOSITORY_ONLY_FUTURE_FORMALIZATION__"
    "ONE_VALID_FROM_MUTATION__DETERMINISTIC_TIME_FIXTURE__EX_17_OF_17_REUSED__"
    "ZERO_OPERATION_ZERO_CREDIT__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def canonical_document_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


PRODUCER = load_module(PRODUCER_PATH, "g77_256ie_test_producer")
REDUCER = load_module(REDUCER_PATH, "g77_256ie_test_reducer")


def test_exact_committed_id_entry_and_nested_authority() -> None:
    git = lambda cwd, *args: subprocess.check_output(
        ["git", *args], cwd=cwd, text=True
    ).strip()
    assert git(ROOT, "branch", "--show-current") == "g77-256fl-wrong-attempt-preboot-blocker"
    assert git(ROOT, "rev-parse", "HEAD") == HEAD
    assert git(ROOT, "rev-parse", "HEAD^{tree}") == TREE
    assert git(ROOT, "show", "-s", "--format=%s", "HEAD") == "G77-256ID select FUTURE as next E05 frontier"
    assert git(ROOT, "status", "--porcelain", "--untracked-files=no") == ""
    assert git(ROOT, "diff", "--cached", "--name-only") == ""
    nested = ROOT / "sapianta_system"
    assert git(nested, "rev-parse", "HEAD") == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert git(nested, "rev-parse", "HEAD^{tree}") == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert git(nested, "branch", "--show-current") == ""
    assert git(nested, "status", "--porcelain") == ""
    assert git(nested, "describe", "--tags", "--exact-match", "HEAD") == "sapianta-system-nested-authority-3183bab-v1"


def test_id_selection_reconstructs_future_at_ten_of_eighteen() -> None:
    envelope = load_unique(ID_SELECTION)
    selection = envelope["selection"]
    assert sha256(ID_SELECTION) == "86d222ecdd10b856ad30f9ab462a4f23c53b472f7021715d3ea8bc166781807b"
    assert selection["e05"]["status"] == "VERIFIED__10_OF_18"
    assert selection["e05"]["remaining"] == 8
    assert selection["selected_frontier"]["selected_next_e05_vector"] == "FUTURE"
    assert selection["selected_frontier"]["selection_status"].startswith("VERIFIED__UNIQUE")
    assert selection["terminal_control"]["future_repository_formalization"] == "NOT_PROVEN"
    assert selection["terminal_control"]["future_operational_capability"] == "NOT_PROVEN"
    assert set(selection["operational_counters"].values()) == {0}


@pytest.mark.parametrize(
    ("path", "inner_key", "seal_key", "seal"),
    [
        (SPEC, "specification", "specification_sha256", SPEC_SHA256),
        (FIXTURE, "fixture", "fixture_sha256", FIXTURE_SHA256),
        (REDUCTION, "reduction", "reduction_sha256", REDUCTION_SHA256),
    ],
)
def test_ie_json_is_unique_key_canonical_and_inner_sealed(
    path: Path, inner_key: str, seal_key: str, seal: str
) -> None:
    envelope = load_unique(path)
    assert path.read_bytes() == canonical_document_bytes(envelope)
    assert hashlib.sha256(canonical_bytes(envelope[inner_key])).hexdigest() == seal
    assert envelope[seal_key] == seal


def test_producer_is_deterministic_and_mutates_only_valid_from() -> None:
    first = PRODUCER.produce_future_vector(ROOT)
    second = PRODUCER.produce_future_vector(ROOT)
    assert PRODUCER.canonical_bytes(first) == PRODUCER.canonical_bytes(second)
    assert first["evaluation_time_unix_ns"] == 500
    assert first["baseline_payload"]["valid_from_unix_ns"] == 100
    assert first["future_payload"]["valid_from_unix_ns"] == 600
    assert first["future_payload"]["valid_until_unix_ns"] == 1000
    assert first["differing_payload_fields"] == ["valid_from_unix_ns"]
    assert first["independent_mutation_count"] == 1
    assert first["dependent_recomputed_coordinates"] == [
        "human_authority_act.payload_digest"
    ]
    assert first["baseline_payload_digest"] != first["future_payload_digest"]
    assert set(first["preserved_coordinate_proof"].values()) == {True}
    assert first["fixture_is_human_authority"] is False
    assert first["fixture_is_operational_request"] is False
    assert first["fixture_uses_wall_clock"] is False


def test_repository_reducer_accepts_and_negative_mutations_fail_closed() -> None:
    packet = PRODUCER.produce_future_vector(ROOT)
    result = REDUCER.reduce_future_repository_vector(packet)
    assert result["future_repository_formalization"] == "VERIFIED"
    assert result["future_route_binding"] == "NOT_PROVEN"
    assert result["future_preoperational_readiness"] == "NOT_PROVEN"
    assert result["future_operational_capability"] == "NOT_PROVEN"
    assert result["e05_status"] == "10/18" and result["e05_credit"] == 0
    for mutation in (
        lambda value: value["future_payload"].__setitem__("valid_until_unix_ns", 1200),
        lambda value: value.__setitem__("evaluation_time_unix_ns", 700),
        lambda value: value.__setitem__("fixture_is_human_authority", True),
        lambda value: value.__setitem__("expected_error_reason", "bad timestamp"),
    ):
        tampered = deepcopy(packet)
        mutation(tampered)
        with pytest.raises(REDUCER.FutureRepositoryReductionError):
            REDUCER.reduce_future_repository_vector(tampered)


def test_current_p11_owner_rejects_future_before_owner_state_initialization(
    tmp_path: Path,
) -> None:
    di = load_module(
        ROOT / "tests/test_g77_256di_p11_da_operational_consumer_v1.py",
        "g77_256ie_di_fixture_owner",
    )
    store = di._store(tmp_path)
    bindings = di.FixedPrincipalBindings(di.ISSUANCE_UID, di.CALLER_UID, di.CUSTODY_UID)
    gate = di._gate(store, bindings)
    _, input_record = di._input_record()
    payload = di._operational_payload(input_record, gate, bindings)
    future = dict(payload, valid_from_unix_ns=600)
    with pytest.raises(di.FailClosedRuntimeError, match="^operational Human act is not current$"):
        di.validate_operational_act_payload(
            future,
            input_record=input_record,
            gate=gate,
            bindings=bindings,
            owner_revision=0,
            now_unix_ns=500,
        )
    assert store.current(allow_missing=True) is None


def test_future_expired_and_stale_boundaries_are_distinct_and_ordered() -> None:
    source = P11.read_text(encoding="utf-8")
    assert "if not valid_from <= current < valid_until:" in source
    assert '_fail("operational Human act is not current")' in source
    assert "current_time = time.time_ns() if now_unix_ns is None else now_unix_ns" in source
    submit = source[source.index("    def submit_human_act("):source.index("    def terminate_human_act(")]
    assert submit.index("self._validate_authority_sources(") < submit.index("self._store.initialize_available(binding)")
    claim = source[source.index("    def claim_and_invoke_once("):]
    assert "preclaim_time >= available.binding.valid_until_unix_ns" in claim
    assert "OwnerStateName.EXPIRED" in claim
    assert '_fail("one-use Human act expired before PRECLAIM")' in claim
    assert "validated_act.target_revision != owner_revision" in source
    assert '_fail("operational Human act target revision is stale")' in source
    substrate = SUBSTRATE.read_text(encoding="utf-8")
    assert "(OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED)" in substrate


def test_no_clock_framework_route_authority_or_operational_entry_added() -> None:
    for path in (PRODUCER_PATH, REDUCER_PATH):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Attribute, ast.Name))
        }
        assert not calls.intersection({
            "time", "time_ns", "now", "sleep", "submit_human_act",
            "claim_and_invoke_once", "initialize_available", "main",
        })
    reduction = load_unique(REDUCTION)["reduction"]
    assert set(reduction["operational_counters"].values()) == {0}
    reuse = reduction["reuse_impact"]
    for key in (
        "new_authority_layer_count", "new_clock_infrastructure_count",
        "new_generic_framework_count", "new_production_route_count",
        "new_runtime_owner_count", "p11_core_change_count",
    ):
        assert reuse[key] == "VERIFIED__0"
    assert reuse["production_route_before"] == reuse["production_route_after"] == "VERIFIED__1"
    assert reduction["ex"]["reused"] == "17/17"
    assert reduction["ex"]["reconstructed"] == 0


def test_terminal_sources_report_and_verdict_are_exact() -> None:
    reduction = load_unique(REDUCTION)["reduction"]
    for source in reduction["sources"]:
        assert sha256(ROOT / source["path"]) == source["sha256"]
    assert reduction["terminal_control"]["verdict"] == VERDICT
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(VERDICT)
