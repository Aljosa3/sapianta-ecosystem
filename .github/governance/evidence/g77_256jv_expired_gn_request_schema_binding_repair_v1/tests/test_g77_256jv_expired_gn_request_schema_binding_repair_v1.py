from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import io
import tarfile

import pytest


ROOT = Path(__file__).resolve().parents[5]
JV = ROOT / ".github/governance/evidence/g77_256jv_expired_gn_request_schema_binding_repair_v1"
FORMALIZER = JV / "analysis/G77_256JV_EXPIRED_GN_REQUEST_SCHEMA_BINDING_FORMALIZER_V1.py"
REPORT = JV / "G77_256JV_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jv_test_formalizer")


def write_canonical(tmp_path: Path, name: str, value: dict) -> Path:
    path = tmp_path / name
    path.write_bytes(F.canonical_bytes(value))
    return path


def test_exact_remote_ratified_ju_entry_nested_authority_and_dependencies() -> None:
    entry = F.authenticate_entry(F.JU_HEAD)
    assert entry["branch"] == F.BRANCH
    assert entry["head"] == F.JU_HEAD
    assert entry["tree"] == F.JU_TREE
    assert entry["subject"] == F.JU_SUBJECT
    assert entry["remote_head"] == F.JU_HEAD
    assert entry["index_empty"] is True
    assert entry["nested_authority"] == {
        "origin": F.NESTED_ORIGIN,
        "head": F.NESTED_HEAD,
        "tree": F.NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": F.NESTED_TAG,
        "pinned": True,
        "remote_tag_equal": "VERIFIED__READ_ONLY_LS_REMOTE",
    }
    assert F.authenticate_committed_dependencies() == {
        path.as_posix(): digest for path, digest in F.EXPECTED_HASHES.items()
    }


def test_ju_terminal_identities_and_exact_gn_blocker_reconstruct() -> None:
    proof = F.reconstruct_ju_blocker()
    assert proof["terminal"] == "M__FRESH_EXPIRED_PREAUTHORIZATION_GN_REQUEST_SCHEMA_MISMATCH"
    assert proof["phase"] == "FAIL_CLOSED_BEFORE_HUMAN_AUTHORIZATION_PRESENTATION"
    assert proof["gn_rejection"] == "SEALED_REQUEST_FIELDS_INVALID"
    assert proof["schema_difference"] == {
        "request_extra_fields": ["expired_execution_count"],
        "request_missing_fields": ["wrong_attempt_execution_count"],
        "live_binding_extra_fields": ["expired_adapter_sha256", "temporal_binding_sha256"],
        "live_binding_missing_fields": ["du", "eb", "ee"],
    }
    assert proof["identities"]["invalid_request_identity"] == (
        "8dd1eacf6d49a4b22314edf60dcd380203c020529e7654c88c40b7069834bbd6"
    )
    assert proof["identities"]["checkpoint_digest"] == (
        "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0"
    )
    assert set(proof["operational_counters"].values()) == {"VERIFIED__0"}
    assert proof["e05"]["before"] == proof["e05"]["after"] == "VERIFIED__11_OF_18"


def test_gn_contract_is_vector_independent_and_successful_histories_match() -> None:
    proof = F.authenticate_gn_contract_and_history()
    assert proof["contract_conclusion"] == (
        "A_AND_D__GN_V1_IS_VECTOR_INDEPENDENT__JU_USED_WRONG_PROJECTION"
    )
    assert set(proof["successful_vector_projections"]) == {
        "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"
    }
    assert all(
        item["wrong_attempt_execution_count"] == 0
        and (item["du"], item["eb"], item["ee"]) == ("PASS", "PASS", "PASS")
        for item in proof["successful_vector_projections"].values()
    )
    assert proof["field_semantics"]["expired_execution_count"] == (
        "NO_AUTHENTICATED_GN_V1_FIELD_OWNER"
    )
    assert F.authenticate_ju_du_eb_ee()["ju_static_readiness"] == "STATIC_READINESS_PASS"


def test_corrected_projection_changes_only_the_authenticated_schema_mapping() -> None:
    envelope = F.corrected_request_envelope()
    request = envelope["request"]
    proof = F.verify_projection(envelope)
    assert set(request) == F.GN.REQUEST_FIELDS
    assert set(request["live_binding"]) == F.GN.LIVE_BINDING_FIELDS
    assert request["wrong_attempt_execution_count"] == 0
    assert request["authorized_vector_requested"] == "EXPIRED"
    assert "expired_execution_count" not in request
    assert "expired_adapter_sha256" not in request["live_binding"]
    assert "temporal_binding_sha256" not in request["live_binding"]
    assert proof["nonprojection_field_mutation_count"] == 0
    assert proof["expired_semantic_information_discarded"] is False
    assert proof["expired_semantic_preservation"]["checkpoint_digest"] == (
        request["preauthorization"]["checkpoint_inner_sha256"]
    )


def test_corrected_request_and_deterministic_presentation_are_exactly_gn_accepted() -> None:
    envelope = F.GN.load_validated_sealed_request(ROOT / F.REQUEST)
    assert envelope == F.corrected_request_envelope()
    presentation = (ROOT / F.PRESENTATION).read_bytes()
    assert presentation == F.GN.render_human_authorization_presentation(ROOT / F.REQUEST)
    result = F.GN.validate_human_authorization_presentation(ROOT / F.REQUEST, presentation)
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )
    assert result["reviewed_field_count"] == 45
    assert result["human_constitutional_authorization_count"] == 0
    parsed = F.GN.parse_human_authorization_presentation(presentation)
    assert parsed["AUTHORIZED_VECTOR_REQUESTED"] == "EXPIRED"
    assert parsed["CHECKPOINT_SHA256"] == (
        "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0"
    )


def test_unknown_mismatched_and_substituted_requests_remain_fail_closed(tmp_path: Path) -> None:
    envelope = F.corrected_request_envelope()
    cases = F.negative_projection_proof(envelope)
    assert set(cases) == {
        "unknown_expired_counter", "missing_canonical_counter",
        "unknown_live_binding_field", "cross_vector_substitution",
        "cross_generation_substitution",
    }
    assert set(cases.values()) == {
        "SEALED_REQUEST_FIELDS_INVALID",
        "SEALED_REQUEST_LIVE_BINDING_INVALID",
        "SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
    }
    bad_seal = deepcopy(envelope)
    bad_seal["request"]["operation_identity"] = "G77_256JV_SUBSTITUTED_OPERATION"
    path = write_canonical(tmp_path, "bad-seal.json", bad_seal)
    with pytest.raises(F.GN.PresentationBindingError, match="SEALED_REQUEST_INNER_SEAL_INVALID"):
        F.GN.load_validated_sealed_request(path)


def test_stable_jr_checkout_jt_recurrence_fix_and_temporal_contract_are_exact() -> None:
    proof = F.temporal_and_stable_checkout_proof()
    temporal = proof["temporal_semantics"]
    stable = proof["stable_checkout"]
    assert temporal["valid_from_unix_ns"] == 100
    assert temporal["valid_until_unix_ns"] == 1000
    assert temporal["governed_preclaim_coordinate_unix_ns"] == 1000
    assert temporal["truth_table"] == {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"}
    assert temporal["wall_clock_is_governed_preclaim_authority"] is False
    assert stable["stable_checkout"] == {"head": F.JR_HEAD, "tree": F.JR_TREE}
    assert stable["recurrence_hazard"] == "VERIFIED__ELIMINATED"
    assert stable["production_route"] == "VERIFIED__1_TO_1"


def test_equivalence_and_reduction_are_canonical_unique_key_inner_sealed_and_replayable() -> None:
    artifacts = F.build_artifacts(F.JU_HEAD)
    for relative in (F.REQUEST, F.PRESENTATION, F.EQUIVALENCE, F.REDUCTION):
        assert (ROOT / relative).read_bytes() == artifacts[relative]
    for relative, inner in ((F.EQUIVALENCE, "proof"), (F.REDUCTION, "reduction")):
        raw = (ROOT / relative).read_bytes()
        envelope = json.loads(raw, object_pairs_hook=F.unique_object)
        assert raw == F.canonical_bytes(envelope)
        assert envelope[f"{inner}_sha256"] == hashlib.sha256(
            F.canonical_bytes(envelope[inner])
        ).hexdigest()
    with pytest.raises(F.JVFormalizationError, match="DUPLICATE_JSON_KEY__schema_id"):
        F.unique_object([("schema_id", 1), ("schema_id", 2)])


def test_terminal_preserves_authority_firewall_e05_ex_and_architecture_budget() -> None:
    reduction = F.load_canonical(F.REDUCTION)["reduction"]
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["authority_boundary"]["human_authority_present"] is False
    assert reduction["authority_boundary"]["authority_consumed"] is False
    assert reduction["authority_boundary"]["authorization_request_materialization_count"] == "VERIFIED__1"
    assert reduction["authority_boundary"]["authorization_presentation_materialization_count"] == "VERIFIED__1"
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert set(reduction["architecture"].values()) <= {
        "VERIFIED__0", "VERIFIED__1"
    }
    assert reduction["proof_yield"]["proof_reuse_count"] == "VERIFIED__17"


def test_ex_17_of_17_is_reused_from_immutable_certificate_without_reconstruction(
    tmp_path: Path,
) -> None:
    proof = F.authenticate_ex_reuse()
    assert proof["certified_component_count"] == 17
    assert proof["ex_reused"] == "VERIFIED__17_OF_17"
    assert proof["ex_reconstructed"] == "VERIFIED__0"
    archive = subprocess.check_output(
        ["git", "archive", "651168072f39d6cd0323efc23ed830445a05062b"], cwd=ROOT
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(tmp_path, filter="data")
    validator_path = tmp_path / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
    )
    validator = load(validator_path, "g77_256jv_ex_entry_validator")
    result = validator.validate(tmp_path / F.EX_CERTIFICATE)
    assert result["regression_total"] == result["regression_pass"] == 12
    assert result["regression_fail"] == 0


def test_no_production_owner_p11_route_or_layer_zero_mutation() -> None:
    changed = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=ROOT, text=True
    ).splitlines()
    assert changed
    assert all(line.startswith(f"?? {F.JV.as_posix()}/") for line in changed)
    assert hashlib.sha256((ROOT / F.GN_PATH).read_bytes()).hexdigest() == F.EXPECTED_HASHES[F.GN_PATH]
    assert hashlib.sha256((ROOT / F.P11_PATH).read_bytes()).hexdigest() == F.EXPECTED_HASHES[F.P11_PATH]
    source = FORMALIZER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(FORMALIZER))
    called_names = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not {"claim_and_invoke_once", "validate_execution_admission", "materialize_operation_state"} & called_names
    assert "qemu-system-x86_64" not in source
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_g48_has_exact_six_h1_and_five_exact_slovenian_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
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
        assert text.count(question) == 1
    assert text.rstrip().endswith(F.TERMINAL)
