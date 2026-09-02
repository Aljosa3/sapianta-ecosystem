#!/usr/bin/env python3
"""Focused repository-only proofs for the HA WRONG_INPUT route binding."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HA = ROOT / ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1"
ADAPTER_PATH = HA / "adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
CONTEXT_PATH = HA / "static/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
TERMINAL_PATH = HA / "G77_256HA_SPCE_TERMINAL_REDUCTION_V1.json"
NEXT_SPEC_PATH = HA / "G77_256HA_NEXT_DEVELOPMENT_SPECIFICATION_V1.json"
REPORT_PATH = ROOT / "docs/governance/G77_256HA_WRONG_INPUT_OPERATION_CONTEXT_GUEST_ADAPTER_AND_GN_PRESENTATION_BINDING_V1.md"
LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_PATH = ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
SCHEMA_PATH = ROOT / (
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json"
)
GZ_CANDIDATE = ROOT / (
    ".github/governance/evidence/g77_256gz_wrong_input_post_commit_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
GV_RAW = ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/"
    "operation_state/runtime_export/G77_256GV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
GV_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/"
    "G77_256GV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
SUBSTRATE_PATH = ROOT / "tests/p11_da_disposable_substrate_v1.py"
PREFIX = "G77_256HA"
GENERATION = PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = PREFIX + "_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
HEAD = "20a435d36f84e99c90b872f892061a1dce86d151"
TREE = "72ed62c13f82c178635c27e4c21429cb21015ad1"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


LAUNCHER = load_module(LAUNCHER_PATH, "g77_256ha_existing_fm_route")
GN = load_module(GN_PATH, "g77_256ha_existing_gn_owner")
ADAPTER = load_module(ADAPTER_PATH, "g77_256ha_wrong_input_adapter")
SUBSTRATE = load_module(SUBSTRATE_PATH, "g77_256ha_p11_substrate")


def authorized_input_bytes() -> bytes:
    for line in GV_RAW.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("record_type") == "wrong_attempt_denial_complete":
            return SUBSTRATE.bind_record_identity(record["facts"]["authorized_input_record"])
    raise AssertionError("authenticated GV input baseline absent")


def build_context(root: Path) -> dict:
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HEAD,
        repository_tree=TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=root / "operation_state",
        transient_root=root / "transient",
        candidate_source_path=GZ_CANDIDATE.relative_to(ROOT),
    )


def wrong_input_request(context: dict, path: Path) -> Path:
    envelope = copy.deepcopy(json.loads(GV_REQUEST.read_bytes()))
    request = envelope["request"]
    envelope["schema_id"] = "G77_256HA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    request["schema_id"] = "G77_256HA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1"
    request["generation_identity"] = GENERATION
    request["operation_identity"] = OPERATION
    request["authorized_vector_requested"] = "WRONG_INPUT"
    request["repository"].update({
        "head": HEAD,
        "tree": TREE,
        "remote_head": HEAD,
    })
    request["live_binding"].update({
        "candidate_sha256": context["candidate_manifest_sha256"],
        "context_sha256": context["context_sha256"],
        "context_file_sha256": hashlib.sha256(LAUNCHER.canonical_bytes(context)).hexdigest(),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "receipt_parent": context["receipt_parent"],
    })
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(request)
    ).hexdigest()
    path.write_bytes(GN._canonical_bytes(envelope))
    return path


def test_exact_gz_entry_and_frontier_are_authenticated() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == HEAD
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == TREE
    reduction = json.loads((ROOT / (
        ".github/governance/evidence/g77_256gz_wrong_input_post_commit_readiness_v1/"
        "G77_256GZ_SPCE_TERMINAL_REDUCTION_V1.json"
    )).read_bytes())["reduction"]
    assert reduction["readiness_branch"]["branch"] == "TERMINAL_BRANCH_B__NOT_READY"
    assert reduction["capability_status"]["post_commit_live_binding_status"] == "VERIFIED"
    assert (reduction["capability_status"]["du_status"], reduction["capability_status"]["eb_status"], reduction["capability_status"]["ee_status"]) == ("PASS", "PASS", "PASS")
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"


def test_wrong_input_context_is_canonical_sealed_schema_valid_and_route_bound(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    assert LAUNCHER.context_vector(context) == "WRONG_INPUT"
    binding = context["guest_adapter_binding"]
    assert binding["source_path"] == ADAPTER_PATH.relative_to(ROOT).as_posix()
    assert binding["source_sha256"] == hashlib.sha256(ADAPTER_PATH.read_bytes()).hexdigest()
    assert binding["bootstrap_identity"] == "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    assert binding["guest_path"] == binding["bootstrap_guest_path"]
    assert context["candidate_manifest_sha256"] == hashlib.sha256(GZ_CANDIDATE.read_bytes()).hexdigest()
    assert context["repository_head"] == HEAD and context["repository_tree"] == TREE
    assert LAUNCHER.fresh_context.validate_context(context, repository_root=ROOT) == context
    schema = json.loads(SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(context, schema)


def test_static_context_artifact_reproduces_exactly() -> None:
    context = json.loads(CONTEXT_PATH.read_bytes())
    assert CONTEXT_PATH.read_bytes() == LAUNCHER.canonical_bytes(context)
    rebuilt = LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HEAD,
        repository_tree=TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=Path(context["operation_evidence_root"]),
        transient_root=Path(context["transient_root"]),
        candidate_source_path=GZ_CANDIDATE.relative_to(ROOT),
    )
    assert rebuilt == context


def test_guest_adapter_reuses_gy_mutation_and_existing_p11_request_type() -> None:
    projection = ADAPTER.construct_wrong_input_payload(
        repository_root=ROOT,
        authorized_input_canonical_bytes=authorized_input_bytes(),
        wrong_input_identity="G77_256HA_E05_SUPPLIED_WRONG_INPUT_002",
        request_identity="G77_256HA_WRONG_INPUT_CUSTODY_REQUEST_001",
    )
    assert projection["semantic_binding"]["target_mutated_coordinate"] == "input_identity"
    assert projection["semantic_binding"]["dependent_recomputation_fields"] == ["record_identity"]
    assert projection["semantic_binding"]["semantic_mutation_count"] == 1
    supplied = SUBSTRATE.validate_input_record_bytes(projection["canonical_payload_utf8"].encode())
    custody = ADAPTER.construct_existing_custody_request(
        repository_root=ROOT,
        authorized_input_canonical_bytes=authorized_input_bytes(),
        wrong_input_identity="G77_256HA_E05_SUPPLIED_WRONG_INPUT_002",
        request_identity="G77_256HA_WRONG_INPUT_CUSTODY_REQUEST_001",
    )
    assert custody.canonical_payload == projection["canonical_payload_utf8"].encode()
    assert supplied["input_identity"] == "G77_256HA_E05_SUPPLIED_WRONG_INPUT_002"
    assert projection["adapter_invoked_p11"] is False


def test_gn_presents_wrong_input_only_from_the_sealed_request(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    request_path = wrong_input_request(context, tmp_path / "request.json")
    presentation = GN.render_human_authorization_presentation(request_path)
    parsed = GN.parse_human_authorization_presentation(presentation)
    assert parsed["AUTHORIZED_VECTOR_REQUESTED"] == "WRONG_INPUT"
    assert parsed["CONTEXT_SHA256"] == context["context_sha256"]
    assert GN.validate_human_authorization_presentation(request_path, presentation)[
        "human_constitutional_authorization_count"
    ] == 0
    changed = presentation.replace(b'AUTHORIZED_VECTOR_REQUESTED "WRONG_INPUT"', b'AUTHORIZED_VECTOR_REQUESTED "WRONG_ATTEMPT"')
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(request_path, changed)


def test_fm_preauthority_serialization_is_vector_bound_and_non_authority(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    fixture = LAUNCHER.preauthority_serialization_fixture(context)
    assert fixture["authorized_vector"] == "WRONG_INPUT"
    assert fixture["wrong_input_operational_attempt_limit"] == 1
    assert "wrong_attempt_operational_attempt_limit" not in fixture
    assert fixture["authorization_present"] is False
    proof = LAUNCHER.prove_authority_handoff_canonicalization(context)
    assert proof["fixture_classification"] == "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL"
    assert proof["human_operational_authorization_count"] == 0
    assert proof["qemu_execution_count"] == 0


def test_wrong_attempt_firewall_and_single_route_remain_reachable(tmp_path: Path) -> None:
    generation = "G77_256HATEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
    context = LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=generation,
        operation_identity="G77_256HATEST_OPERATION_001",
        identity_namespace_prefix="G77_256HATEST",
        operation_evidence_root=tmp_path / "wrong_attempt_operation",
        transient_root=tmp_path / "wrong_attempt_transient",
    )
    assert LAUNCHER.context_vector(context) == "WRONG_ATTEMPT"
    assert context["guest_adapter_binding"]["source_path"] == LAUNCHER.WRAPPER
    fixture = LAUNCHER.preauthority_serialization_fixture(context)
    assert fixture["authorized_vector"] == "WRONG_ATTEMPT"
    assert fixture["wrong_attempt_operational_attempt_limit"] == 1
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    qemu_calls = [
        node for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(qemu_calls) == 1
    assert subprocess.check_output([
        "git", "diff", "--name-only", HEAD, "--",
        ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1",
        ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1",
    ], cwd=ROOT, text=True).strip() == ""


def test_no_operational_action_is_reachable_from_ha_adapter_api() -> None:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "claim_and_invoke_once(" not in source
    assert "subprocess.run" not in source
    assert "qemu-system" not in source
    assert "HA grants no authority and performs no operation" in source


def test_runtime_specialization_is_hash_bound_and_preserves_semantic_firewall(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    specialized = ADAPTER.specialize_fc_runtime_source(
        repository_root=ROOT,
        identity_namespace_prefix=PREFIX,
    )
    assert specialized.count('wrong_value["input_identity"] = WRONG_INPUT_ID') == 1
    assert 'wrong_value["attempt_identity"] = WRONG_INPUT_ID' not in specialized
    assert specialized.count("consumer.claim_and_invoke_once(") == 1
    assert '"semantic_mutation_field": "input_identity"' in specialized
    assert '"isolated_mutation_fields": ["input_identity", "record_identity"]' in specialized
    assert ADAPTER.EXPECTED_DENIAL_REASON in specialized

    monkeypatch.setattr(ADAPTER, "FC_ADAPTER_SHA256", "0" * 64)
    with pytest.raises(ADAPTER.WrongInputAdapterError, match="FC_FK_ADAPTER_HASH_MISMATCH"):
        ADAPTER.specialize_fc_runtime_source(
            repository_root=ROOT,
            identity_namespace_prefix=PREFIX,
        )
    monkeypatch.undo()

    monkeypatch.setattr(ADAPTER, "GY_PRODUCER_SHA256", "0" * 64)
    with pytest.raises(ADAPTER.WrongInputAdapterError, match="WRONG_INPUT_OWNER_HASH_MISMATCH"):
        ADAPTER.construct_wrong_input_payload(
            repository_root=ROOT,
            authorized_input_canonical_bytes=authorized_input_bytes(),
            wrong_input_identity="G77_256HA_E05_SUPPLIED_WRONG_INPUT_002",
            request_identity="G77_256HA_WRONG_INPUT_CUSTODY_REQUEST_001",
        )


def test_terminal_evidence_next_spec_and_g48_are_canonical_sealed_branch_b() -> None:
    terminal = json.loads(TERMINAL_PATH.read_bytes())
    assert TERMINAL_PATH.read_bytes() == LAUNCHER.canonical_bytes(terminal)
    assert hashlib.sha256(LAUNCHER.canonical_bytes(terminal["reduction"])).hexdigest() == terminal["reduction_sha256"]
    reduction = terminal["reduction"]
    assert reduction["terminal_branch"]["branch"] == "TERMINAL_BRANCH_B__STILL_NOT_READY"
    assert reduction["capability_status"]["preoperational_readiness_status"] == "NOT_PROVEN"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"
    assert reduction["reuse_impact"]["production_route_delta"] == 0

    specification = json.loads(NEXT_SPEC_PATH.read_bytes())
    assert NEXT_SPEC_PATH.read_bytes() == LAUNCHER.canonical_bytes(specification)
    assert hashlib.sha256(LAUNCHER.canonical_bytes(specification["specification"])).hexdigest() == specification["specification_sha256"]
    assert specification["specification"]["auto_continuable"] is False
    assert specification["specification"]["execution_authority"] is False

    report = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reduction["terminal_control"]["verdict"])
    assert report.count("Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?") == 1
