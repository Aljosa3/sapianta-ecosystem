#!/usr/bin/env python3
"""Focused repository-only proof for G77-256HG projection-aware validation."""

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


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
OWNER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FIXTURE_PATH = ROOT / (
    ".github/governance/evidence/g77_256hg_guest_projection_validation_v1/"
    "static/G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py"
)
HF = ROOT / ".github/governance/evidence/g77_256hf_wrong_input_operational_v1"
HF_CONTEXT = HF / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
HF_TERMINAL = HF / "G77_256HF_SPCE_TERMINAL_REDUCTION_V1.json"
HF_REPORT = ROOT / (
    "docs/governance/G77_256HF_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
    "OPERATIONAL_COMMISSIONING_V1.md"
)
HG_REPORT = ROOT / (
    "docs/governance/G77_256HG_PROJECTION_AWARE_GUEST_VALIDATION_"
    "CORRECTION_V1.md"
)
GY_PRODUCER = ROOT / (
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
HA_ADAPTER = ROOT / (
    ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/"
    "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


OWNER = load_module(OWNER_PATH, "g77_256hg_context_owner")
FIXTURE = load_module(FIXTURE_PATH, "g77_256hg_projection_fixture")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == OWNER.canonical_bytes(value)
    return value


def reseal_after_argv_mutation(context: dict[str, Any]) -> None:
    context["canonical_argv_sha256"] = OWNER.argv_sha256(context["canonical_argv"])
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    context["context_sha256"] = hashlib.sha256(
        OWNER.canonical_bytes(unsealed)
    ).hexdigest()


def projection_result(context: dict[str, Any], view: Path = FIXTURE.GUEST_PROJECTED_PATH):
    return OWNER.validate_sealed_canonical_argv(
        context,
        validation_repository_root=view,
    )


def test_exact_hf_frontier_and_valid_host_guest_projection_are_authenticated() -> None:
    context = load_canonical(HF_CONTEXT)
    terminal = load_canonical(HF_TERMINAL)["reduction"]
    assert terminal["last_verified_edge"] == (
        "ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__"
        "GUEST_CONTEXT_OWNER_LOADED__SEALED_CONTEXT_VALIDATION_ENTERED"
    )
    assert terminal["first_broken_edge"] == (
        "GUEST_CONTEXT_VALIDATION_REDERIVED_HOST_BOUND_DN_HARNESS_ARGV_PATH_"
        "FROM_GUEST_REPOSITORY_ROOT"
    )
    assert terminal["e05"] == {"after": "7/18", "before": "7/18", "credit": 0}

    result = projection_result(context)
    assert result == {
        "host_canonical_identity": str(FIXTURE.HOST_CANONICAL_IDENTITY),
        "guest_projected_path": str(FIXTURE.GUEST_PROJECTED_PATH),
        "guest_validation_view": str(FIXTURE.GUEST_PROJECTED_PATH),
        "projection_status": "EXACT_GUEST_PROJECTION",
        "sealed_host_qemu_argv_sha256": FIXTURE.SEALED_HOST_QEMU_ARGV_SHA256,
        "runtime_execution_identity": str(FIXTURE.RUNTIME_EXECUTION_IDENTITY),
    }
    assert OWNER.validate_context(
        context, repository_root=FIXTURE.HOST_CANONICAL_IDENTITY
    ) == context


def test_unauthorized_host_canonical_argv_mutation_is_rejected() -> None:
    context = deepcopy(load_canonical(HF_CONTEXT))
    index = next(
        index + 1
        for index, value in enumerate(context["canonical_argv"][:-1])
        if value == "-virtfs"
        and "mount_tag=g77_harness" in context["canonical_argv"][index + 1]
    )
    context["canonical_argv"][index] = context["canonical_argv"][index].replace(
        str(FIXTURE.HOST_CANONICAL_IDENTITY), "/srv/unauthorized-repository"
    )
    reseal_after_argv_mutation(context)
    with pytest.raises(OWNER.ContextError, match="canonical argv changed"):
        projection_result(context)


def test_wrong_guest_projection_is_rejected() -> None:
    with pytest.raises(OWNER.ContextError, match="validation view is not projection-bound"):
        projection_result(load_canonical(HF_CONTEXT), Path("/mnt/not-aigol"))


def test_missing_projection_binding_is_rejected() -> None:
    context = deepcopy(load_canonical(HF_CONTEXT))
    context["operation_evidence_root"] = "/tmp/g77_256hf/operation_state"
    with pytest.raises(OWNER.ContextError, match="projection missing or ambiguous"):
        projection_result(context)


def test_ambiguous_projection_binding_is_rejected() -> None:
    context = deepcopy(load_canonical(HF_CONTEXT))
    context["operation_evidence_root"] = (
        "/home/pisarna/work/sapianta-fl/.github/governance/evidence/outer/"
        ".github/governance/evidence/g77_256hf_wrong_input_operational_v1/"
        "operation_state"
    )
    with pytest.raises(OWNER.ContextError, match="projection missing or ambiguous"):
        projection_result(context)


def test_projection_cannot_change_non_path_canonical_argv() -> None:
    context = deepcopy(load_canonical(HF_CONTEXT))
    context["canonical_argv"][4] = "unauthorized-cpu"
    reseal_after_argv_mutation(context)
    with pytest.raises(OWNER.ContextError, match="canonical argv changed"):
        projection_result(context)


def test_projection_is_non_mutating_and_cannot_create_authority_or_effect() -> None:
    context = load_canonical(HF_CONTEXT)
    before = OWNER.canonical_bytes(context)
    result = projection_result(context)
    assert OWNER.canonical_bytes(context) == before
    assert set(result) == {
        "host_canonical_identity",
        "guest_projected_path",
        "guest_validation_view",
        "projection_status",
        "sealed_host_qemu_argv_sha256",
        "runtime_execution_identity",
    }
    source = ast.get_source_segment(
        OWNER_PATH.read_text(encoding="utf-8"),
        next(
            node
            for node in ast.parse(OWNER_PATH.read_text(encoding="utf-8")).body
            if isinstance(node, ast.FunctionDef)
            and node.name == "validate_sealed_canonical_argv"
        ),
    )
    assert source is not None
    assert "subprocess" not in source
    assert "authority" not in source.lower()
    assert "request" not in source.lower()
    assert "effect" not in source.lower()


def test_historical_hf_evidence_and_wrong_input_firewall_remain_unchanged() -> None:
    assert subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", str(HF.relative_to(ROOT)), str(HF_REPORT.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    assert hashlib.sha256((HF / "G77_256HF_SERIAL_CONSOLE_V1.log").read_bytes()).hexdigest() == (
        "401ce0a9d244e5b77bce6ee89f72b800d7804c54b3483e69f8b72260796821be"
    )
    assert hashlib.sha256(HF_CONTEXT.read_bytes()).hexdigest() == (
        "2da900cb4206d5365d97b76f7ea5b9f099968401ad2ebbf6db80fd29468e99ef"
    )
    assert hashlib.sha256(GY_PRODUCER.read_bytes()).hexdigest() == (
        "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
    )
    assert hashlib.sha256(HA_ADAPTER.read_bytes()).hexdigest() == (
        "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230"
    )
    ha_source = HA_ADAPTER.read_text(encoding="utf-8")
    assert 'TARGET_MUTATION = "input_identity"' in ha_source
    assert 'DEPENDENT_RECOMPUTATION = "record_identity"' in ha_source
    assert "SEMANTIC_MUTATION_COUNT = 1" in ha_source
    assert 'EXPECTED_DIFFERING_FIELDS = ["input_identity", "record_identity"]' in ha_source


def test_existing_owner_and_single_launcher_route_are_reused() -> None:
    owner_sha256 = hashlib.sha256(OWNER_PATH.read_bytes()).hexdigest()
    launcher_source = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert owner_sha256 == (
        "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
    )
    assert owner_sha256 in launcher_source
    tree = ast.parse(launcher_source)
    mains = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == len(qemu_calls) == 1
    owner_tree = ast.parse(OWNER_PATH.read_text(encoding="utf-8"))
    validator_calls = [
        node for node in ast.walk(owner_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "validate_sealed_canonical_argv"
    ]
    assert len(validator_calls) == 1


def test_g48_report_has_exact_structure_metrics_and_terminal_verdict() -> None:
    report = HG_REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    required = (
        "FRONTIER_RECONSTRUCTION_STATUS",
        "HOST_CANONICAL_BINDING_STATUS",
        "GUEST_PROJECTION_BINDING_STATUS",
        "PROJECTION_EQUIVALENCE_STATUS",
        "HOST_BINDING_PRESERVATION_STATUS",
        "UNAUTHORIZED_MUTATION_REJECTION_STATUS",
        "EX_REUSED = 17/17",
        "EX_RECONSTRUCTED = 0",
        "PROJECTION_AWARE_VALIDATION_OPERATIONAL_CAPABILITY",
        "WRONG_INPUT_OPERATIONAL_CAPABILITY",
        "POST_COMMIT_LIVE_BINDING_STATUS",
        "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)
    assert report.count(
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?"
    ) == 1
    assert report.rstrip().endswith(
        "VERIFIED__G77_256HG_PROJECTION_AWARE_VALIDATION_REPOSITORY_CAPABILITY__"
        "HF_FAILURE_CLASS_STATIC_BLOCKED__ZERO_OPERATION__E05_7_OF_18__"
        "POST_COMMIT_LIVE_BINDING_NOT_PROVEN__HUMAN_REVIEW_REQUIRED"
    )
