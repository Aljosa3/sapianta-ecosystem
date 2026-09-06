#!/usr/bin/env python3
"""Focused post-commit compatibility and Human-barrier tests for IR."""

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
IR_ROOT = ROOT / ".github/governance/evidence/g77_256ir_post_commit_gn_future_presentation_readiness_v1"
FORMALIZER = IR_ROOT / "analysis/G77_256IR_POST_COMMIT_GN_FUTURE_PRESENTATION_READINESS_FORMALIZER_V1.py"
TERMINAL = IR_ROOT / "G77_256IR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IR_ROOT / "G77_256IR_G48_IMPLEMENTATION_READINESS_REPORT_V1.md"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


IR = load_module(FORMALIZER, "g77_256ir_formalizer")
GN = load_module(ROOT / IR.GN_PATH, "g77_256ir_test_gn")


def reseal(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(GN._canonical_bytes(envelope["request"])).hexdigest()


def write_request(tmp_path: Path, envelope: dict, name: str = "request.json") -> Path:
    path = tmp_path / name
    path.write_bytes(GN._canonical_bytes(envelope))
    return path


def mutate_presentation(raw: bytes, field: str, value) -> bytes:
    lines = raw.decode().splitlines()
    index = next(index for index, line in enumerate(lines) if line.startswith(field + " "))
    lines[index] = f"{field} {json.dumps(value, ensure_ascii=False, allow_nan=False)}"
    return ("\n".join(lines) + "\n").encode()


def test_exact_iq_entry_nested_lineage_and_terminal_a_reconstruct() -> None:
    entry = IR.authenticate_entry()
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (IR.IQ_HEAD, IR.IQ_TREE, IR.IQ_HEAD)
    assert entry["index"] == ""
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["head"] == IR.NESTED_HEAD
    iq = IR.reconstruct_iq()
    assert iq["status"] == "VERIFIED"
    assert iq["terminal"] == "A__REPOSITORY_IMPLEMENTATION_SUCCESS"
    assert iq["artifact_count"] == 4


def test_committed_gn_owner_and_exact_eight_line_delta() -> None:
    owner = IR.authenticate_committed_gn()
    assert owner["git_blob"] == IR.GN_BLOB
    assert owner["sha256"] == IR.GN_SHA256
    assert (owner["insertions"], owner["deletions"]) == (8, 0)
    assert owner["gn_iq_committed_delta_bounded"] == "VERIFIED"
    assert owner["gn_vector_set_closed"] == "VERIFIED"


def test_future_semantics_if_target_and_current_v2_readiness() -> None:
    future = IR.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["evaluation"] < future["valid_from"] < future["valid_until"]
    assert future["candidate_runtime_sha256"] == IR.FUTURE_CANDIDATE_SHA
    assert future["context_identity"] == IR.FUTURE_CONTEXT_SHA
    readiness = IR.current_v2_readiness()
    assert (readiness["du"], readiness["eb"], readiness["ee"]) == ("PASS", "PASS", "PASS")
    assert readiness["certification_baseline"] == {"head": IR.IQ_HEAD, "tree": IR.IQ_TREE}
    assert readiness["runtime_target"]["head"] == IR.IF_HEAD


def test_fresh_identity_is_pattern_derived_collision_free_and_iq_bound() -> None:
    identity = IR.derive_fresh_identity()
    assert identity["operation_generation"] == IR.GENERATION
    assert identity["operation_identity"] == IR.OPERATION
    assert identity["repository_generation_equals_operation_generation"] == "VERIFIED__NO"
    assert identity["collision"] == "VERIFIED__NO"
    assert identity["repository_binding"] == {"head": IR.IQ_HEAD, "tree": IR.IQ_TREE}
    assert identity["precommit_self_reference_avoided"] == "VERIFIED"


@pytest.mark.parametrize("vector", ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"))
def test_committed_closed_five_vector_positive_matrix(vector: str, tmp_path: Path) -> None:
    envelope, _ = IR.fresh_request_fixture(IR.current_v2_readiness())
    envelope["request"]["authorized_vector_requested"] = vector
    envelope["request"]["generation_identity"] = f"G77_256IRTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1"
    reseal(envelope)
    path = write_request(tmp_path, envelope, f"{vector}.json")
    presentation = GN.render_human_authorization_presentation(path)
    parsed = GN.parse_human_authorization_presentation(presentation)
    assert parsed["AUTHORIZED_VECTOR_REQUESTED"] == vector
    assert GN.validate_human_authorization_presentation(path, presentation)["operational_execution_count"] == 0


@pytest.mark.parametrize("vector", ("UNKNOWN", "future", "", None, "FUTURE_ALIAS"))
def test_unknown_malformed_alias_vectors_fail_closed(vector, tmp_path: Path) -> None:
    envelope, _ = IR.fresh_request_fixture(IR.current_v2_readiness())
    envelope["request"]["authorized_vector_requested"] = vector
    reseal(envelope)
    path = write_request(tmp_path, envelope)
    with pytest.raises(GN.PresentationBindingError, match="SEALED_REQUEST_VECTOR_INVALID"):
        GN.render_human_authorization_presentation(path)


@pytest.mark.parametrize("generation", (
    "G77_256IR_FUTURE",
    "G77_256IR_FUTURE_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1",
    "G77_256IR_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1_TRAILING",
))
def test_weak_substring_and_wrong_generation_fail_closed(generation: str, tmp_path: Path) -> None:
    envelope, _ = IR.fresh_request_fixture(IR.current_v2_readiness())
    envelope["request"]["generation_identity"] = generation
    reseal(envelope)
    path = write_request(tmp_path, envelope)
    with pytest.raises(GN.PresentationBindingError, match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID"):
        GN.render_human_authorization_presentation(path)


def test_cross_vector_generation_operation_request_and_replay_substitution(tmp_path: Path) -> None:
    original, _ = IR.fresh_request_fixture(IR.current_v2_readiness())
    original_path = write_request(tmp_path, original, "original.json")
    presentation = GN.render_human_authorization_presentation(original_path)
    cross_vector = deepcopy(original)
    cross_vector["request"]["authorized_vector_requested"] = "WRONG_INPUT"
    reseal(cross_vector)
    with pytest.raises(GN.PresentationBindingError, match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID"):
        GN.render_human_authorization_presentation(write_request(tmp_path, cross_vector, "cross-vector.json"))
    changed = deepcopy(original)
    changed["request"]["operation_identity"] = "G77_256IR_OTHER_OPERATION_002"
    reseal(changed)
    changed_path = write_request(tmp_path, changed, "changed.json")
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(changed_path, presentation)
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(
            original_path, mutate_presentation(presentation, "AUTHORIZATION_REQUEST_SHA256", "0" * 64)
        )


def test_exact_ip_blocker_is_removed_by_committed_iq(tmp_path: Path) -> None:
    ip_terminal = IR.load_canonical(ROOT / ".github/governance/evidence/g77_256ip_future_operational_v1/G77_256IP_SPCE_TERMINAL_PREOPERATIONAL_BLOCKER_V1.json")
    assert ip_terminal["reduction"]["terminal"]["first_broken_edge"] == "EXISTING_GN_SEALED_REQUEST_VALIDATION_REJECTS_FUTURE_VECTOR"
    iq = load_module(ROOT / IR.IQ_FORMALIZER, "g77_256ir_iq_fixture")
    envelope = iq.future_request_fixture()
    path = write_request(tmp_path, envelope, "ip-input.json")
    assert GN.parse_human_authorization_presentation(GN.render_human_authorization_presentation(path))["AUTHORIZED_VECTOR_REQUESTED"] == "FUTURE"


def test_fresh_presentation_reaches_but_does_not_cross_human_barrier() -> None:
    result = IR.presentation_readiness(IR.current_v2_readiness())
    assert result["fresh_future_preauthorization_readiness"] == "VERIFIED"
    assert result["human_authorization_action_available"] == "VERIFIED__YES"
    assert result["human_operational_authority"] == "VERIFIED__0"
    assert result["authority_consumption"] == "VERIFIED__0"
    assert result["operational_execution_count"] == 0
    assert result["persisted_request_count"] == result["persisted_presentation_count"] == 0


def test_missing_extra_duplicate_noncanonical_and_wrong_seal_fail_closed(tmp_path: Path) -> None:
    base, _ = IR.fresh_request_fixture(IR.current_v2_readiness())
    missing = deepcopy(base)
    del missing["request"]["operation_identity"]
    reseal(missing)
    extra = deepcopy(base)
    extra["request"]["caller_defined_vector"] = True
    reseal(extra)
    wrong_seal = deepcopy(base)
    wrong_seal["request"]["operation_identity"] = "G77_256IR_WRONG"
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(base, indent=2) + "\n")
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"schema_id":"x","schema_id":"y"}\n')
    for path in (
        write_request(tmp_path, missing, "missing.json"),
        write_request(tmp_path, extra, "extra.json"),
        write_request(tmp_path, wrong_seal, "wrong-seal.json"),
        pretty, duplicate,
    ):
        with pytest.raises(GN.PresentationBindingError):
            GN.load_validated_sealed_request(path)


def test_terminal_canonical_duplicate_safe_inner_sealed_and_replayable() -> None:
    envelope = IR.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == IR.sha256_bytes(IR.canonical_bytes(envelope["reduction"]))
    assert envelope == IR.terminal_envelope()
    duplicate = TERMINAL.read_text().replace('{"reduction":', '{"schema_id":"duplicate","reduction":', 1)
    with pytest.raises(IR.IRFormalizationError, match="DUPLICATE_KEY"):
        json.loads(duplicate, object_pairs_hook=IR.unique_object)


def test_terminal_a_operational_zero_e05_and_exact_g48_scope() -> None:
    reduction = IR.terminal_reduction()
    assert reduction["terminal"]["terminal"] == "A__POST_COMMIT_COMPATIBILITY_AND_FRESH_PREAUTHORIZATION_READINESS"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8}
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    ast.parse(FORMALIZER.read_text(), filename=str(FORMALIZER))
    ast.parse(Path(__file__).read_text(), filename=__file__)


def test_ir_delta_is_evidence_only_and_index_empty() -> None:
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""
    changed = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
    assert changed and all("g77_256ir_post_commit_gn_future_presentation_readiness_v1" in line for line in changed)
