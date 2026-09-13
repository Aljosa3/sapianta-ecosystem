#!/usr/bin/env python3
"""Focused non-operational proof of G77-256LG existing-route admission."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
FM_ROOT = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
CONTEXT_OWNER_PATH = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
LAUNCHER_PATH = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
LG_ROOT = ROOT / (
    ".github/governance/evidence/"
    "g77_256lg_wrong_scope_existing_route_admission_v1"
)
ADAPTER_PATH = LG_ROOT / "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
CLOUD_INIT_PATH = LG_ROOT / "static/G77_256LG_CLOUD_INIT_USER_DATA_V1.yaml"
SEED_PATH = LG_ROOT / "static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V1.img"
TERMINAL_PATH = LG_ROOT / "G77_256LG_SPCE_TERMINAL_PHASE_A_REDUCTION_V1.json"
REPORT_PATH = LG_ROOT / "G77_256LG_G48_IMPLEMENTATION_REPORT_V1.md"
LE_REDUCTION = ROOT / (
    ".github/governance/evidence/g77_256le_wrong_scope_minimum_governed_delta_v1/"
    "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
HP_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
META_DATA = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
P11_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
ENTRY_HEAD = "5cdc56046b79b577842f1dedff1faedf6aaedfa0"
ENTRY_TREE = "687db58ac7e87ac9f03f445299e52de4480a8ed6"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
GENERATION = (
    "G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_"
    "OPERATIONAL_COMMISSIONING_V1"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


CONTEXT_OWNER = load_module(CONTEXT_OWNER_PATH, "g77_256lg_test_context_owner")
LAUNCHER = load_module(LAUNCHER_PATH, "g77_256lg_test_launcher")
GN = load_module(GN_PATH, "g77_256lg_test_gn")
ADAPTER = load_module(ADAPTER_PATH, "g77_256lg_test_adapter")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_context(tmp_path: Path, vector: str = "WRONG_SCOPE") -> dict:
    generation = (
        f"G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=generation,
        operation_identity=f"G77_256LGTEST_{vector}_PHASE_A_FIXTURE_001",
        identity_namespace_prefix="G77_256LGTEST",
        operation_evidence_root=tmp_path / vector.lower() / "operation_state",
        transient_root=tmp_path / vector.lower() / "transient",
        candidate_source_path=LE_REDUCTION.relative_to(ROOT),
    )


def project_adapter_and_owner(context: dict) -> None:
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True)
    source = (ROOT / binding["source_path"]).read_bytes()
    Path(binding["projected_path"]).write_bytes(source)
    Path(binding["bootstrap_projected_path"]).write_bytes(source)
    owner_source = CONTEXT_OWNER_PATH.read_bytes()
    (projection_root / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME).write_bytes(
        owner_source
    )
    projection_root.chmod(LAUNCHER.GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE)


def reseal_request(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(envelope["request"])
    ).hexdigest()


def test_lf_blocker_is_removed_only_for_wrong_scope() -> None:
    assert "WRONG_SCOPE" in CONTEXT_OWNER.SUPPORTED_OPERATION_VECTORS
    assert "WRONG_SCOPE" in GN.SUPPORTED_VECTORS
    assert CONTEXT_OWNER.operation_vector(GENERATION) == "WRONG_SCOPE"
    assert CONTEXT_OWNER.adapter_source_relative_path(GENERATION) == (
        ADAPTER_PATH.relative_to(ROOT).as_posix()
    )
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_SCOPE")
    assert bootstrap["cloud_init_path"] == CLOUD_INIT_PATH.relative_to(ROOT).as_posix()
    assert bootstrap["seed_path"] == str(SEED_PATH)
    fields = LAUNCHER.authorization_fields({"authorized_vector": "WRONG_SCOPE"})
    assert "wrong_scope_operational_attempt_limit" in fields
    assert LAUNCHER.operation_attempt_limit_field("WRONG_SCOPE") == (
        "wrong_scope_operational_attempt_limit"
    )
    assert sum(field.endswith("operational_attempt_limit") for field in fields) == 1


@pytest.mark.parametrize(
    "vector",
    (
        "WRONG_ATTEMPT",
        "WRONG_INPUT",
        "WRONG_CONTRACT",
        "WRONG_PROVENANCE",
        "FUTURE",
        "EXPIRED",
        "WRONG_SCOPE",
    ),
)
def test_existing_closed_vector_admissions_remain_reachable(vector: str) -> None:
    generation = (
        f"G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    assert CONTEXT_OWNER.operation_vector(generation) == vector
    assert vector in CONTEXT_OWNER.SUPPORTED_OPERATION_VECTORS
    assert vector in GN.SUPPORTED_VECTORS
    assert LAUNCHER.operation_attempt_limit_field(vector).startswith(vector.lower())


@pytest.mark.parametrize(
    "generation",
    (
        "G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_UNKNOWN_OPERATIONAL_COMMISSIONING_V1",
        "G77_256LGTEST_WRONG_SCOPE",
        "G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_wrong_scope_OPERATIONAL_COMMISSIONING_V1",
        "G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG-SCOPE_OPERATIONAL_COMMISSIONING_V1",
        "",
    ),
)
def test_unknown_alias_and_malformed_vectors_fail_closed(generation: str) -> None:
    with pytest.raises(CONTEXT_OWNER.ContextError, match="no exact supported operation vector"):
        CONTEXT_OWNER.operation_vector(generation)


def test_wrong_scope_context_adapter_bootstrap_and_projection_are_live_bound(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    binding = context["guest_adapter_binding"]
    assert binding["source_path"] == ADAPTER_PATH.relative_to(ROOT).as_posix()
    assert binding["source_sha256"] == sha256_path(ADAPTER_PATH)
    assert binding["adapter_identity"].endswith("_WRONG_SCOPE_VECTOR_ADAPTER_V1.py")
    assert binding["guest_path"] == (
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    )
    project_adapter_and_owner(context)
    proof = LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert proof["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert proof["source_sha256"] == sha256_path(ADAPTER_PATH)
    assert proof["guest_consumer_path"] == binding["guest_path"]


def test_wrong_scope_seed_is_exact_static_source_projection() -> None:
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_SCOPE")
    assert sha256_path(SEED_PATH) == bootstrap["seed_sha256"]
    assert subprocess.check_output(
        ["isoinfo", "-i", str(SEED_PATH), "-R", "-x", "/user-data"],
        stderr=subprocess.DEVNULL,
    ) == CLOUD_INIT_PATH.read_bytes()
    assert subprocess.check_output(
        ["isoinfo", "-i", str(SEED_PATH), "-R", "-x", "/meta-data"],
        stderr=subprocess.DEVNULL,
    ) == META_DATA.read_bytes()
    assert subprocess.check_output(
        ["isoinfo", "-i", str(SEED_PATH), "-R", "-x", "/network-config"],
        stderr=subprocess.DEVNULL,
    ) == NETWORK_CONFIG.read_bytes()


def test_adapter_authenticates_le_and_isolates_authority_scope() -> None:
    model = ADAPTER.authenticate_wrong_scope_semantics(ROOT)
    assert model["independent_semantic_mutation_count"] == 1
    assert model["preserved_non_target_dimensions"] == [
        "authority_kind",
        "authority_lifecycle_state",
        "attempt_identity",
        "input_identity",
        "contract_identity",
        "provenance_identity",
        "validity_interval_and_currentness",
        "target_owner_and_revision",
        "caller_identity",
    ]
    source = ADAPTER.specialize_fc_runtime_source(
        repository_root=ROOT,
        identity_namespace_prefix="G77_256LGTEST",
    )
    assert source.count('wrong_act_value["authority_scope"] = WRONG_SCOPE_ID') == 1
    assert 'wrong_value["attempt_identity"] = WRONG_SCOPE_ID' not in source
    assert 'authority_differing_fields == ["authority_scope"]' in source
    assert 'denial_error == "operational Human act scope is invalid"' in source
    assert '"semantic_mutation_field": "authority_scope"' in source


def test_preauthority_fields_and_handoff_are_materializable_without_authority(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    fixture = LAUNCHER.preauthority_serialization_fixture(context)
    LAUNCHER.validate_preauthority_serialization_fixture(context, fixture)
    assert fixture["authorization_present"] is False
    assert fixture["authorization_kind"] == (
        "TEST_ONLY_NON_AUTHORITY_SERIALIZATION_FIXTURE"
    )
    assert fixture["wrong_scope_operational_attempt_limit"] == 1
    assert "wrong_attempt_operational_attempt_limit" not in fixture
    proof = LAUNCHER.prove_authority_handoff_canonicalization(context)
    assert proof["result"] == (
        "PREAUTHORITY_CANONICAL_AUTHORITY_HANDOFF_PROOF_PASS"
    )
    assert proof["fixture_classification"] == (
        "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL"
    )


def test_gn_admits_exact_wrong_scope_generation_and_rejects_substitution(
    tmp_path: Path,
) -> None:
    base = json.loads(HP_REQUEST.read_bytes())
    valid = deepcopy(base)
    valid["request"]["authorized_vector_requested"] = "WRONG_SCOPE"
    valid["request"]["generation_identity"] = GENERATION
    reseal_request(valid)
    valid_path = tmp_path / "valid.json"
    valid_path.write_bytes(GN._canonical_bytes(valid))
    presentation = GN.render_human_authorization_presentation(valid_path)
    assert b'AUTHORIZED_VECTOR_REQUESTED "WRONG_SCOPE"' in presentation
    result = GN.validate_human_authorization_presentation(valid_path, presentation)
    assert result["human_constitutional_authorization_count"] == 0

    substituted = deepcopy(valid)
    substituted["request"]["generation_identity"] = (
        "G77_256LGTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    reseal_request(substituted)
    substituted_path = tmp_path / "substituted.json"
    substituted_path.write_bytes(GN._canonical_bytes(substituted))
    with pytest.raises(
        GN.PresentationBindingError,
        match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
    ):
        GN.render_human_authorization_presentation(substituted_path)


def test_p11_is_unchanged_and_scope_denial_precedes_owner_initialization() -> None:
    assert sha256_path(P11_PATH) == P11_SHA256
    source = P11_PATH.read_text(encoding="utf-8")
    scope_check = (
        "if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:"
    )
    initialization = "available = self._store.initialize_available(binding)"
    attempt_revalidation = "binding = self._validate_authority_sources("
    assert source.count(scope_check) == 1
    assert source.index(scope_check) < source.index(initialization)
    assert source.count(attempt_revalidation) == 2


def test_single_route_and_no_parallel_launcher_or_owner() -> None:
    assert list(LG_ROOT.rglob("*LAUNCHER*.py")) == []
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
    main_functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
    ]
    assert len(main_functions) == 1
    assert "P11BoundedConsumerV1" not in ADAPTER_PATH.read_text(encoding="utf-8")
    assert sha256_path(CONTEXT_OWNER_PATH) == (
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_SHA256
    )


def test_terminal_reduction_is_sealed_and_report_has_exact_g48_headings() -> None:
    raw = TERMINAL_PATH.read_bytes()
    envelope = json.loads(raw)
    canonical = (
        json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert raw == canonical
    inner = (
        json.dumps(
            envelope["reduction"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert hashlib.sha256(inner).hexdigest() == envelope["reduction_sha256"]
    assert set(envelope["reduction"]["operational_counters"].values()) == {0}
    assert envelope["reduction"]["e05"] == {
        "after": "12/18",
        "before": "12/18",
        "credit": 0,
        "remaining": 6,
        "required": 18,
        "satisfied": 12,
    }
    headings = [
        line
        for line in REPORT_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
