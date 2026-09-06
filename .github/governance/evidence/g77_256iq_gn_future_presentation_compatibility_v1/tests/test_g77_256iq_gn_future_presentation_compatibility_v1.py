#!/usr/bin/env python3
"""Focused positive, substitution, and constitutional firewall proofs for IQ."""

from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IQ_ROOT = ROOT / ".github/governance/evidence/g77_256iq_gn_future_presentation_compatibility_v1"
FORMALIZER = IQ_ROOT / "analysis/G77_256IQ_GN_FUTURE_PRESENTATION_COMPATIBILITY_FORMALIZER_V1.py"
TERMINAL = IQ_ROOT / "G77_256IQ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IQ_ROOT / "G77_256IQ_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


IQ = load_module(FORMALIZER, "g77_256iq_formalizer")
GN = load_module(ROOT / IQ.GN_PATH, "g77_256iq_test_gn")


def reseal(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(envelope["request"])
    ).hexdigest()


def write_envelope(tmp_path: Path, envelope: dict, name: str) -> Path:
    path = tmp_path / name
    path.write_bytes(GN._canonical_bytes(envelope))
    return path


def mutate_presentation(raw: bytes, field: str, value) -> bytes:
    lines = raw.decode().splitlines()
    index = next(index for index, line in enumerate(lines) if line.startswith(field + " "))
    lines[index] = f"{field} {json.dumps(value, ensure_ascii=False, allow_nan=False)}"
    return ("\n".join(lines) + "\n").encode()


def test_exact_ip_entry_terminal_c_nested_authority_and_gn_base_reconstruct() -> None:
    entry = IQ.authenticate_entry()
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (
        IQ.IP_HEAD, IQ.IP_TREE, IQ.IP_HEAD
    )
    assert entry["index"] == ""
    assert entry["nested_authority"]["head"] == IQ.NESTED_HEAD
    assert IQ.reconstruct_ip()["status"] == "VERIFIED"
    closure = IQ.authenticate_gn_and_closure()
    assert closure["gn_base_git_blob"] == IQ.GN_BASE_BLOB
    assert closure["gn_base_sha256"] == IQ.GN_BASE_SHA256
    assert closure["ambiguity_count"] == "VERIFIED__0"


def test_formalized_minimum_dependency_closure_and_version_firewall() -> None:
    closure = IQ.authenticate_gn_and_closure()
    assert closure["minimum_dependency_closure"] == (
        "VERIFIED__GN_SUPPORTED_VECTORS_AND_FUTURE_GENERATION_SUFFIX_BINDING_ONLY"
    )
    for field in (
        "existing_contract_family_expresses_future",
        "existing_profile_fields_sufficient",
        "membership_plus_existing_sealed_identity_recomputation",
        "generation_binding_generic_projection_plus_bounded_suffix_check",
    ):
        assert closure[field] == "VERIFIED__YES"
    for field in (
        "downstream_closed_vector_delta_required", "new_schema_major_required",
        "p11_change_required", "fm_change_required", "new_presentation_protocol_required",
    ):
        assert closure[field] == "VERIFIED__NO"


def test_future_semantics_runtime_target_and_no_wall_clock_drift() -> None:
    facts = IQ.authenticate_future_semantics()
    assert (facts["evaluation"], facts["valid_from"], facts["valid_until"]) == (500, 600, 1000)
    assert facts["evaluation"] < facts["valid_from"] < facts["valid_until"]
    assert facts["payload_digest"] == IQ.FUTURE_PAYLOAD
    assert facts["source_act"] == IQ.FUTURE_SOURCE_ACT
    assert facts["che_correlation"] == IQ.FUTURE_CHE
    assert facts["candidate_runtime_sha256"] == IQ.FUTURE_CANDIDATE_SHA
    assert facts["context_identity"] == IQ.FUTURE_CONTEXT_SHA
    assert (facts["runtime_target_head"], facts["runtime_target_tree"]) == (
        IQ.IF_HEAD, IQ.IF_TREE
    )
    assert facts["future_semantic_mutation_count"] == "VERIFIED__0"
    assert facts["wall_clock_dependency_count"] == "VERIFIED__0"


@pytest.mark.parametrize(
    "vector",
    ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"),
)
def test_closed_five_vector_set_preserves_positive_presentation(vector: str, tmp_path: Path) -> None:
    envelope = IQ.future_request_fixture()
    envelope["request"]["authorized_vector_requested"] = vector
    envelope["request"]["generation_identity"] = (
        f"G77_256IQTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1"
    )
    reseal(envelope)
    path = write_envelope(tmp_path, envelope, f"{vector}.json")
    presentation = GN.render_human_authorization_presentation(path)
    parsed = GN.parse_human_authorization_presentation(presentation)
    assert parsed["AUTHORIZED_VECTOR_REQUESTED"] == vector
    assert parsed["GENERATION_ID"] == envelope["request"]["generation_identity"]
    assert GN.validate_human_authorization_presentation(path, presentation)[
        "human_constitutional_authorization_count"
    ] == 0


def test_exact_future_generation_operation_request_runtime_context_and_argv_bind(tmp_path: Path) -> None:
    envelope = IQ.future_request_fixture()
    path = write_envelope(tmp_path, envelope, "future.json")
    presentation = GN.render_human_authorization_presentation(path)
    parsed = GN.parse_human_authorization_presentation(presentation)
    context = IQ.load_canonical(ROOT / IQ.IH_CONTEXT)
    assert parsed["GENERATION_ID"] == IQ.GENERATION
    assert parsed["OPERATION_ID"] == IQ.OPERATION
    assert parsed["AUTHORIZATION_REQUEST_SHA256"] == envelope["request_sha256"]
    assert parsed["CANDIDATE_SHA256"] == IQ.FUTURE_CANDIDATE_SHA
    assert parsed["CONTEXT_SHA256"] == IQ.FUTURE_CONTEXT_SHA
    assert parsed["CANONICAL_ARGV_SHA256"] == context["canonical_argv_sha256"]
    assert parsed["HEAD"] == IQ.IP_HEAD
    assert parsed["TREE"] == IQ.IP_TREE
    result = IQ.presentation_proof()
    assert result["gn_future_presentation_admission"] == "VERIFIED"
    assert result["gn_future_generation_binding"] == "VERIFIED"
    assert result["gn_future_operation_binding"] == "VERIFIED"


@pytest.mark.parametrize("vector", ("UNKNOWN", "future", "", None, "FUTURE_ALIAS"))
def test_unknown_malformed_and_alias_vectors_fail_closed(vector, tmp_path: Path) -> None:
    envelope = IQ.future_request_fixture()
    envelope["request"]["authorized_vector_requested"] = vector
    reseal(envelope)
    path = write_envelope(tmp_path, envelope, "unknown.json")
    with pytest.raises(GN.PresentationBindingError, match="SEALED_REQUEST_VECTOR_INVALID"):
        GN.render_human_authorization_presentation(path)


@pytest.mark.parametrize(
    ("vector", "generation"),
    (
        ("WRONG_INPUT", IQ.GENERATION),
        ("FUTURE", "G77_256IQTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"),
        ("FUTURE", "G77_256IQTEST_FUTURE"),
    ),
)
def test_cross_vector_and_cross_generation_substitution_fail_closed(
    vector: str, generation: str, tmp_path: Path
) -> None:
    envelope = IQ.future_request_fixture()
    envelope["request"]["authorized_vector_requested"] = vector
    envelope["request"]["generation_identity"] = generation
    reseal(envelope)
    path = write_envelope(tmp_path, envelope, "substitution.json")
    with pytest.raises(
        GN.PresentationBindingError,
        match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
    ):
        GN.render_human_authorization_presentation(path)


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("GENERATION_ID", "G77_256OTHER_GENERATION"),
        ("OPERATION_ID", "G77_256OTHER_OPERATION"),
        ("HEAD", "0" * 40),
        ("TREE", "1" * 40),
        ("CANDIDATE_SHA256", "2" * 64),
        ("CONTEXT_SHA256", "3" * 64),
        ("CANONICAL_ARGV_SHA256", "4" * 64),
        ("CHECKPOINT_SHA256", "5" * 64),
        ("AUTHORIZATION_REQUEST_SHA256", "6" * 64),
        ("AUTHORIZED_VECTOR_REQUESTED", "WRONG_INPUT"),
    ),
)
def test_presentation_identity_and_cross_request_substitution_fail_closed(
    field: str, wrong, tmp_path: Path
) -> None:
    path = write_envelope(tmp_path, IQ.future_request_fixture(), "future.json")
    presentation = GN.render_human_authorization_presentation(path)
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(
            path, mutate_presentation(presentation, field, wrong)
        )


def test_cross_operation_cross_request_and_replay_substitution_fail_closed(tmp_path: Path) -> None:
    original = IQ.future_request_fixture()
    original_path = write_envelope(tmp_path, original, "original.json")
    altered = deepcopy(original)
    altered["request"]["operation_identity"] = "G77_256IQ_OTHER_FUTURE_OPERATION_002"
    reseal(altered)
    altered_path = write_envelope(tmp_path, altered, "altered.json")
    stale = GN.render_human_authorization_presentation(altered_path)
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(original_path, stale)
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(
            altered_path, GN.render_human_authorization_presentation(original_path)
        )


@pytest.mark.parametrize(
    ("section", "field", "wrong"),
    (
        ("repository", "head", "0" * 40),
        ("live_binding", "candidate_sha256", "1" * 64),
        ("live_binding", "context_sha256", "2" * 64),
        ("live_binding", "canonical_argv_sha256", "3" * 64),
        ("preauthorization", "checkpoint_inner_sha256", "4" * 64),
    ),
)
def test_resealed_request_dependency_change_cannot_reuse_original_presentation(
    section: str, field: str, wrong: str, tmp_path: Path
) -> None:
    original = IQ.future_request_fixture()
    original_path = write_envelope(tmp_path, original, "original.json")
    presentation = GN.render_human_authorization_presentation(original_path)
    changed = deepcopy(original)
    changed["request"][section][field] = wrong
    if section == "repository" and field == "head":
        changed["request"]["repository"]["remote_head"] = wrong
    reseal(changed)
    changed_path = write_envelope(tmp_path, changed, "changed.json")
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(changed_path, presentation)


def test_missing_extra_duplicate_noncanonical_and_wrong_seal_fail_closed(tmp_path: Path) -> None:
    base = IQ.future_request_fixture()
    missing = deepcopy(base)
    del missing["request"]["operation_identity"]
    reseal(missing)
    extra = deepcopy(base)
    extra["request"]["caller_defined_vector_semantics"] = True
    reseal(extra)
    wrong_seal = deepcopy(base)
    wrong_seal["request"]["operation_identity"] = "G77_256IQ_MUTATED"
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(base, indent=2) + "\n")
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"schema_id":"x","schema_id":"y"}\n')
    paths = [
        write_envelope(tmp_path, missing, "missing.json"),
        write_envelope(tmp_path, extra, "extra.json"),
        write_envelope(tmp_path, wrong_seal, "wrong-seal.json"),
        pretty,
        duplicate,
    ]
    for path in paths:
        with pytest.raises(GN.PresentationBindingError):
            GN.load_validated_sealed_request(path)


def test_owner_delta_is_two_bounded_additions_and_no_runtime_or_p11_owner_changed() -> None:
    diff = subprocess.check_output(
        ["git", "diff", "--", IQ.GN_PATH.as_posix()], cwd=ROOT, text=True
    )
    added = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    removed = [line for line in diff.splitlines() if line.startswith("-") and not line.startswith("---")]
    assert added == [
        '+    "FUTURE",',
        '+    if (',
        '+        request["authorized_vector_requested"] == "FUTURE"',
        '+        and not request["generation_identity"].endswith(',
        '+            "_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"',
        '+        )',
        '+    ):',
        '+        _fail("SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID")',
    ]
    assert removed == []
    changed = subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines()
    assert changed == [IQ.GN_PATH.as_posix()]
    assert IQ.FM_PATH.as_posix() not in changed
    assert not any("p11" in path.lower() for path in changed)


def test_no_authority_operation_request_or_parallel_owner_artifact_created() -> None:
    forbidden = (
        "HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST",
        "HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE",
        "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF",
        "LAUNCHER",
        "ADAPTER",
    )
    material = [path.name for path in IQ_ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    assert all(not any(token in name for token in forbidden) for name in material)
    source = FORMALIZER.read_text()
    for forbidden_call in ("subprocess.run(argv", "validate_execution_admission(", "materialize_operation_state("):
        assert forbidden_call not in source


def test_terminal_is_canonical_duplicate_safe_inner_sealed_and_replayable() -> None:
    envelope = IQ.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == IQ.sha256_bytes(
        IQ.canonical_bytes(envelope["reduction"])
    )
    assert envelope == IQ.terminal_envelope()
    with pytest.raises(IQ.IQFormalizationError, match="DUPLICATE_KEY:schema_id"):
        IQ.unique_object([("schema_id", 1), ("schema_id", 2)])
    terminal = envelope["reduction"]["terminal"]
    assert terminal["terminal"] == "A__REPOSITORY_IMPLEMENTATION_SUCCESS"
    assert terminal["auto_continuable"] is False
    assert terminal["human_review_required"] is True
    assert set(envelope["reduction"]["operational_counters"].values()) == {0}
    assert envelope["reduction"]["e05"] == {
        "before": "10/18", "after": "10/18", "credit": 0, "remaining": 8
    }


def test_python_ast_and_g48_exact_six_headings_with_slovenian_reuse_answers() -> None:
    for path in (FORMALIZER, ROOT / IQ.GN_PATH, Path(__file__)):
        ast.parse(path.read_text(), filename=str(path))
    text = REPORT.read_text()
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in text
