#!/usr/bin/env python3
"""Read-only validator for the bounded EX common-substrate certification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any, Callable


sys.dont_write_bytecode = True

EXPECTED_HEAD = "8295ddd2f2639e7130eaecf2520b6d0d8174f8c7"
EXPECTED_TREE = "db309e74925ea0a47365285d2a0a88316c742ddc"
EXPECTED_MANIFEST_OUTER_SHA256 = "42744ccb19767a9f90ed909f3d99b05622053fd00e97886d8a331bcadfe8675c"
EXPECTED_MANIFEST_INNER_SHA256 = "affea45b58f265c094a921b65932d9f9d69c95e6fe4d4359af07432482f6660f"
EXPECTED_ENVELOPE_SCHEMA = "G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_ENVELOPE_V1"
EXPECTED_CERTIFICATE_SCHEMA = "G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_V1"
CERTIFICATE_FILENAME = "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
REPO_ROOT = Path(__file__).resolve().parents[5]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_CLASSIFICATIONS = {
    "CERTIFIED",
    "EVIDENCE_SUPPORTED",
    "REQUIRES_HARDENING",
    "VECTOR_SPECIFIC",
}
MATRIX_FIELDS = {
    "component_id",
    "component",
    "current_classification",
    "evidence_source",
    "certification_source",
    "reusability",
    "vector_dependence",
    "freshness_requirement",
    "operational_evidence_requirement",
    "human_authority_requirement",
    "proposed_ex_classification",
    "rationale",
}
EXPECTED_UPGRADES = {1, 2, 7, 8, 9, 10, 12, 14, 15, 16, 18, 19, 22}
EXPECTED_INVALIDATION_TRIGGERS = {
    "SUBSTRATE_VERSION_CHANGE",
    "CONSTITUTION_CHANGE",
    "HASH_MISMATCH",
    "SEMANTIC_MODEL_CHANGE",
    "BASE_IMAGE_IDENTITY_CHANGE",
    "LAUNCHER_CHANGE",
    "RAW_SCHEMA_CHANGE",
    "DU_EB_EE_CONTRACT_CHANGE",
    "CHECKPOINT_PROTOCOL_CHANGE",
    "G48_VERSION_CHANGE",
    "CONTRADICTORY_EVIDENCE_OR_FAILED_REGRESSION",
    "HUMAN_REVOCATION",
    "EXCLUDED_PROOF_REUSED_AS_FRESH",
}
EXPECTED_FUTURE_STEPS = [
    "AUTHENTICATE_CERTIFIED_SUBSTRATE",
    "SELECT_ONE_UNSATISFIED_VECTOR",
    "GENERATE_VECTOR_DELTA",
    "SATISFY_REQUIRED_FRESHNESS",
    "MATERIALIZE_IF_SEPARATELY_AUTHORIZED",
    "EXECUTE_ONCE_IF_SEPARATELY_AUTHORIZED",
    "REDUCE_FRONTIER_FAIL_CLOSED",
    "TEARDOWN",
    "SEAL",
]


class CertificationValidationError(ValueError):
    """One fail-closed certification validation error."""


def _fail(token: str) -> None:
    raise CertificationValidationError(token)


def _object_no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _nonempty(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(token)
    return value


def _sha256(value: Any, token: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail(token)
    return value


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_no_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CertificationValidationError(f"NON_FINITE_JSON__{value}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CertificationValidationError(f"JSON_INVALID__{path}") from exc


def _repo_file(relative: str) -> Path:
    path_value = Path(relative)
    if path_value.is_absolute() or ".." in path_value.parts:
        _fail("PATH_NOT_REPOSITORY_RELATIVE")
    path = REPO_ROOT / path_value
    if path.is_symlink() or not path.is_file():
        _fail(f"BOUND_FILE_INVALID__{relative}")
    return path


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        _fail("MODULE_SPEC_INVALID")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_certificate(path: Path) -> dict[str, Any]:
    envelope = load_json(path)
    if not isinstance(envelope, dict) or set(envelope) != {
        "schema_id", "certificate", "certificate_sha256"
    }:
        _fail("CERTIFICATE_ENVELOPE_STRUCTURE_INVALID")
    if envelope["schema_id"] != EXPECTED_ENVELOPE_SCHEMA:
        _fail("CERTIFICATE_ENVELOPE_SCHEMA_INVALID")
    certificate = envelope["certificate"]
    if not isinstance(certificate, dict) or certificate.get("schema_id") != EXPECTED_CERTIFICATE_SCHEMA:
        _fail("CERTIFICATE_SCHEMA_INVALID")
    preimage = copy.deepcopy(envelope)
    preimage["certificate_sha256"] = ""
    calculated = sha256_bytes(canonical_bytes(preimage))
    if envelope["certificate_sha256"] != calculated:
        _fail("CERTIFICATE_INNER_HASH_INVALID")
    return envelope


def validate_source_manifest(certificate: dict[str, Any]) -> dict[str, Any]:
    source = certificate.get("source_manifest")
    if not isinstance(source, dict) or set(source) != {
        "path", "outer_sha256", "inner_sha256", "source_head", "source_tree",
        "validator_path", "validator_sha256"
    }:
        _fail("SOURCE_MANIFEST_BINDING_INVALID")
    if source["source_head"] != EXPECTED_HEAD or source["source_tree"] != EXPECTED_TREE:
        _fail("SOURCE_BASELINE_MISMATCH")
    manifest_path = _repo_file(source["path"])
    if source["outer_sha256"] != EXPECTED_MANIFEST_OUTER_SHA256:
        _fail("SOURCE_MANIFEST_OUTER_IDENTITY_INVALID")
    if sha256_bytes(manifest_path.read_bytes()) != source["outer_sha256"]:
        _fail("SOURCE_MANIFEST_OUTER_HASH_MISMATCH")
    if source["inner_sha256"] != EXPECTED_MANIFEST_INNER_SHA256:
        _fail("SOURCE_MANIFEST_INNER_IDENTITY_INVALID")
    validator_path = _repo_file(source["validator_path"])
    _sha256(source["validator_sha256"], "SOURCE_VALIDATOR_SHA256_INVALID")
    if sha256_bytes(validator_path.read_bytes()) != source["validator_sha256"]:
        _fail("SOURCE_VALIDATOR_HASH_MISMATCH")
    ew_module = _load_module(validator_path, "g77_256ew_validator_for_ex")
    try:
        result = ew_module.validate(manifest_path)
    except Exception as exc:
        raise CertificationValidationError(f"SOURCE_MANIFEST_VALIDATION_FAILED__{exc}") from exc
    if result.get("regression_total") != 17 or result.get("regression_pass") != 17 or result.get("regression_fail") != 0:
        _fail("SOURCE_MANIFEST_REGRESSION_RESULT_INVALID")
    if result.get("manifest_inner_sha256") != source["inner_sha256"]:
        _fail("SOURCE_MANIFEST_INNER_CROSS_BINDING_MISMATCH")
    return result


def validate_certification_bindings(certificate: dict[str, Any]) -> None:
    bindings = certificate.get("certification_artifact_bindings")
    if not isinstance(bindings, list) or len(bindings) != 2:
        _fail("CERTIFICATION_ARTIFACT_BINDINGS_INVALID")
    identities: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"identity", "path", "sha256"}:
            _fail("CERTIFICATION_ARTIFACT_BINDING_STRUCTURE_INVALID")
        identity = _nonempty(binding["identity"], "CERTIFICATION_ARTIFACT_IDENTITY_INVALID")
        if identity in identities:
            _fail("CERTIFICATION_ARTIFACT_IDENTITY_DUPLICATE")
        identities.add(identity)
        path = _repo_file(binding["path"])
        expected = _sha256(binding["sha256"], "CERTIFICATION_ARTIFACT_SHA256_INVALID")
        if sha256_bytes(path.read_bytes()) != expected:
            _fail(f"CERTIFICATION_ARTIFACT_HASH_MISMATCH__{identity}")
    if identities != {"EX_HUMAN_READABLE_CERTIFICATION_CONTRACT", "EX_CERTIFICATION_VALIDATOR"}:
        _fail("CERTIFICATION_ARTIFACT_IDENTITY_SET_INVALID")


def validate_authority_and_scope(certificate: dict[str, Any]) -> None:
    authority = certificate.get("human_authorization")
    if not isinstance(authority, dict) or authority.get("provided") is not True:
        _fail("HUMAN_CERTIFICATION_AUTHORITY_ABSENT")
    if authority.get("scope") != "EXACT_COMMITTED_EW_MANIFEST_COMMON_REPOSITORY_SUBSTRATE_WITH_EXPLICIT_EXCLUSIONS":
        _fail("HUMAN_CERTIFICATION_SCOPE_INVALID")
    if authority.get("origin") != "EXPLICIT_HUMAN_G77_256EX_AUTHORIZATION":
        _fail("HUMAN_CERTIFICATION_ORIGIN_INVALID")
    if certificate.get("certificate_is_execution_authority") is not False:
        _fail("CERTIFICATE_CANNOT_AUTHORIZE_EXECUTION")
    if certificate.get("certificate_is_credit_authority") is not False:
        _fail("CERTIFICATE_CANNOT_AUTHORIZE_CREDIT")
    if certificate.get("auto_continuable") is not False:
        _fail("CERTIFICATE_CANNOT_AUTO_CONTINUE")
    expected_decision = "CERTIFIED_COMMON_SUBSTRATE_WITH_EXPLICIT_FRESH_OPERATIONAL_BOUNDARIES"
    if certificate.get("freeze_decision") != expected_decision:
        _fail("FREEZE_DECISION_INVALID")
    expected_state = "CONSTITUTIONALLY_CERTIFIED__COMMON_REPOSITORY_SUBSTRATE_ONLY__FRESH_OPERATIONAL_AND_VECTOR_BOUNDARIES_EXCLUDED"
    if certificate.get("reusable_p11_spce_execution_substrate") != expected_state:
        _fail("CERTIFIED_SUBSTRATE_STATE_INVALID")
    exclusions = certificate.get("exclusions")
    required_exclusions = {
        "ACTUAL_QEMU_LAUNCH_AND_EXECUTED_ARGV",
        "PHYSICAL_BASE_IMAGE_CUSTODY_AND_INTEGRITY",
        "OPERATIONAL_COUNTER_PRODUCER_CONSUMER_ADOPTION",
        "ALL_VECTOR_SPECIFIC_FACTS",
        "ALL_FRESH_OPERATIONAL_RESULTS",
        "E05_CREDIT",
        "P12_AND_PRODUCTION",
        "CROSS_LLM_AND_CLREC_CERTIFICATION",
        "AUTOMATIC_CONTINUATION",
    }
    if set(exclusions or []) != required_exclusions:
        _fail("CERTIFICATION_EXCLUSION_SET_INVALID")


def validate_component_matrix(certificate: dict[str, Any]) -> dict[str, int]:
    matrix = certificate.get("component_certification_matrix")
    if not isinstance(matrix, list) or len(matrix) != 22:
        _fail("COMPONENT_MATRIX_COUNT_INVALID")
    if {item.get("component_id") for item in matrix if isinstance(item, dict)} != set(range(1, 23)):
        _fail("COMPONENT_MATRIX_IDENTIFIERS_INVALID")
    current_counts = {value: 0 for value in ALLOWED_CLASSIFICATIONS}
    proposed_counts = {value: 0 for value in ALLOWED_CLASSIFICATIONS}
    upgrades: set[int] = set()
    for item in matrix:
        if not isinstance(item, dict) or set(item) != MATRIX_FIELDS:
            _fail("COMPONENT_MATRIX_ITEM_STRUCTURE_INVALID")
        current = item["current_classification"]
        proposed = item["proposed_ex_classification"]
        if current not in ALLOWED_CLASSIFICATIONS or proposed not in ALLOWED_CLASSIFICATIONS:
            _fail(f"COMPONENT_CLASSIFICATION_INVALID__{item['component_id']}")
        for field in MATRIX_FIELDS - {"component_id"}:
            _nonempty(item[field], f"COMPONENT_FIELD_INVALID__{item['component_id']}__{field}")
        current_counts[current] += 1
        proposed_counts[proposed] += 1
        if current != proposed:
            upgrades.add(item["component_id"])
            if current != "EVIDENCE_SUPPORTED" or proposed != "CERTIFIED":
                _fail(f"UNAUTHORIZED_COMPONENT_TRANSITION__{item['component_id']}")
    if current_counts != {
        "CERTIFIED": 4, "EVIDENCE_SUPPORTED": 13,
        "REQUIRES_HARDENING": 2, "VECTOR_SPECIFIC": 3,
    }:
        _fail("CURRENT_COMPONENT_COUNTS_INVALID")
    if proposed_counts != {
        "CERTIFIED": 17, "EVIDENCE_SUPPORTED": 0,
        "REQUIRES_HARDENING": 2, "VECTOR_SPECIFIC": 3,
    }:
        _fail("PROPOSED_COMPONENT_COUNTS_INVALID")
    if upgrades != EXPECTED_UPGRADES:
        _fail("COMPONENT_UPGRADE_SET_INVALID")
    counts = certificate.get("component_counts")
    if counts != proposed_counts:
        _fail("DECLARED_COMPONENT_COUNTS_INVALID")
    b1 = next(item for item in matrix if item["component_id"] == 11)
    b2 = next(item for item in matrix if item["component_id"] == 13)
    if b1["proposed_ex_classification"] != "REQUIRES_HARDENING" or b2["proposed_ex_classification"] != "REQUIRES_HARDENING":
        _fail("B1_B2_OPERATIONAL_COMPONENTS_CANNOT_BE_CERTIFIED")
    if any(item["proposed_ex_classification"] != "VECTOR_SPECIFIC" for item in matrix if item["component_id"] in {17, 20, 21}):
        _fail("VECTOR_SPECIFIC_COMPONENT_CERTIFICATION_FORBIDDEN")
    return proposed_counts


def validate_blockers(certificate: dict[str, Any]) -> None:
    blockers = certificate.get("blocker_state_after")
    expected = {
        "B1": "OPEN__OPERATIONAL_EVIDENCE_REQUIRED",
        "B2": "PARTIALLY_CLOSED__REPOSITORY_CONTRACT_CERTIFIED__OPERATIONAL_CUSTODY_EVIDENCE_OPEN",
        "B3": "CLOSED__CERTIFIED",
        "B4": "CLOSED__CERTIFIED_CANONICAL_IDENTITY",
        "B5": "CLOSED__HUMAN_AUTHORITY_EXERCISED_BY_EX",
        "B6": "PARTIALLY_CLOSED__REPOSITORY_BINDING_CERTIFIED__OPERATIONAL_BINDING_OPEN",
    }
    if blockers != expected:
        _fail("BLOCKER_STATE_AFTER_INVALID")
    b2 = certificate.get("b2_repository_contract")
    if not isinstance(b2, dict):
        _fail("B2_REPOSITORY_CONTRACT_INVALID")
    required_b2 = {
        "base_image_identity", "base_image_sha256", "base_image_format",
        "backing_chain_rule", "read_only_expectation", "pre_execution_integrity_check",
        "post_execution_integrity_check", "qemu_img_check_requirement", "custody_boundary",
        "versioning_rule", "mutation_prohibition", "repository_contract_certified",
        "operational_custody_evidence_certified",
    }
    if set(b2) != required_b2:
        _fail("B2_REPOSITORY_CONTRACT_FIELD_SET_INVALID")
    if b2["repository_contract_certified"] is not True or b2["operational_custody_evidence_certified"] is not False:
        _fail("B2_CERTIFICATION_SPLIT_INVALID")
    if b2["read_only_expectation"] is not True:
        _fail("B2_READ_ONLY_POLICY_INVALID")
    b6 = certificate.get("b6_binding")
    if not isinstance(b6, dict) or b6.get("repository_binding_certified") is not True or b6.get("operational_binding_certified") is not False:
        _fail("B6_CERTIFICATION_SPLIT_INVALID")
    if b6.get("semantic_definition_id") != "P11_ENTRY_DEFINITION_V1":
        _fail("B6_SEMANTIC_IDENTITY_INVALID")
    required_counters = {
        "BOUNDARY_REQUEST_COUNT", "PRE_ATTEMPT_DENIAL_COUNT", "P11_ENTRY_COUNT",
        "P11_OPERATIONAL_INVOCATION_COUNT", "PROTECTED_EFFECT_COUNT",
        "SECOND_PROTECTED_EFFECT_COUNT",
    }
    if set(b6.get("counter_fields", [])) != required_counters:
        _fail("B6_COUNTER_FIELD_SET_INVALID")


def validate_proof_and_future_contract(certificate: dict[str, Any]) -> None:
    proofs = certificate.get("proof_obligations")
    if not isinstance(proofs, list) or not proofs:
        _fail("PROOF_OBLIGATIONS_ABSENT")
    identities: set[str] = set()
    classes: set[str] = set()
    for proof in proofs:
        if not isinstance(proof, dict) or set(proof) != {"proof", "class", "reuse_assurance"}:
            _fail("PROOF_OBLIGATION_STRUCTURE_INVALID")
        identity = _nonempty(proof["proof"], "PROOF_IDENTITY_INVALID")
        if identity in identities:
            _fail("PROOF_IDENTITY_DUPLICATE")
        identities.add(identity)
        if proof["class"] not in {"A", "B", "C", "D", "E"}:
            _fail("PROOF_CLASS_INVALID")
        classes.add(proof["class"])
        _nonempty(proof["reuse_assurance"], "PROOF_REUSE_ASSURANCE_INVALID")
    if classes != {"A", "B", "C", "D", "E"}:
        _fail("PROOF_CLASS_COVERAGE_INVALID")
    future = certificate.get("future_e05_contract")
    if not isinstance(future, dict) or future.get("steps") != EXPECTED_FUTURE_STEPS:
        _fail("FUTURE_E05_STEPS_INVALID")
    if set(future.get("invalidation_triggers", [])) != EXPECTED_INVALIDATION_TRIGGERS:
        _fail("INVALIDATION_TRIGGER_SET_INVALID")
    if future.get("regenerate_common_substrate_by_default") is not False:
        _fail("COMMON_SUBSTRATE_REGENERATION_POLICY_INVALID")
    if future.get("fresh_operational_evidence_required") is not True:
        _fail("FUTURE_FRESH_OPERATIONAL_EVIDENCE_POLICY_INVALID")


def validate_frontier_and_counters(certificate: dict[str, Any]) -> None:
    frontier = certificate.get("frontier")
    if frontier != {
        "e05_before": "5/18",
        "e05_after": "5/18",
        "e05_remaining": 13,
        "consumed_state": "UNSATISFIED",
        "g2_state": "OPEN",
        "g3_entry_authorized": False,
        "p12_entry_authorized": False,
        "production_route_authorized": False,
    }:
        _fail("FRONTIER_INVALID")
    counters = certificate.get("operational_counters")
    if not isinstance(counters, dict) or not counters or any(value != 0 for value in counters.values()):
        _fail("OPERATIONAL_COUNTER_NONZERO")


def validate_payload(certificate: dict[str, Any]) -> dict[str, Any]:
    source_result = validate_source_manifest(certificate)
    validate_certification_bindings(certificate)
    validate_authority_and_scope(certificate)
    counts = validate_component_matrix(certificate)
    validate_blockers(certificate)
    validate_proof_and_future_contract(certificate)
    validate_frontier_and_counters(certificate)
    return {"source_result": source_result, "component_counts": counts}


def _expect_failure(token: str, function: Callable[[], Any]) -> None:
    try:
        function()
    except CertificationValidationError as exc:
        if str(exc) != token:
            _fail(f"NEGATIVE_REASON_MISMATCH__EXPECTED_{token}__ACTUAL_{exc}")
    else:
        _fail(f"NEGATIVE_ACCEPTED__{token}")


def run_regressions(certificate: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, str]] = []

    def case(identity: str, function: Callable[[], Any]) -> None:
        try:
            function()
        except Exception as exc:
            results.append({"id": identity, "result": "FAIL", "reason": str(exc)})
        else:
            results.append({"id": identity, "result": "PASS", "reason": "EXPECTED_CERTIFICATION_BOUNDARY_OBSERVED"})

    case("X01_POSITIVE_CERTIFICATE", lambda: validate_payload(certificate))
    wrong = copy.deepcopy(certificate)
    wrong["source_manifest"]["outer_sha256"] = "0" * 64
    case("X02_SOURCE_MANIFEST_TAMPER", lambda: _expect_failure(
        "SOURCE_MANIFEST_OUTER_IDENTITY_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["exclusions"].remove("ACTUAL_QEMU_LAUNCH_AND_EXECUTED_ARGV")
    case("X03_B1_EXCLUSION_REQUIRED", lambda: _expect_failure(
        "CERTIFICATION_EXCLUSION_SET_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["component_counts"]["CERTIFIED"] = 18
    case("X04_COMPONENT_COUNT_TAMPER", lambda: _expect_failure(
        "DECLARED_COMPONENT_COUNTS_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["component_certification_matrix"][10]["proposed_ex_classification"] = "CERTIFIED"
    case("X05_B1_COMPONENT_CANNOT_CERTIFY", lambda: _expect_failure(
        "UNAUTHORIZED_COMPONENT_TRANSITION__11", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["future_e05_contract"]["invalidation_triggers"].remove("HASH_MISMATCH")
    case("X06_INVALIDATION_TRIGGER_REQUIRED", lambda: _expect_failure(
        "INVALIDATION_TRIGGER_SET_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["frontier"]["e05_after"] = "6/18"
    case("X07_E05_CREDIT_CANNOT_MOVE", lambda: _expect_failure(
        "FRONTIER_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["certificate_is_execution_authority"] = True
    case("X08_EXECUTION_AUTHORITY_FORBIDDEN", lambda: _expect_failure(
        "CERTIFICATE_CANNOT_AUTHORIZE_EXECUTION", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["blocker_state_after"]["B5"] = "OPEN__HUMAN_AUTHORITY_REQUIRED"
    case("X09_B5_MUST_BIND_HUMAN_DECISION", lambda: _expect_failure(
        "BLOCKER_STATE_AFTER_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["proof_obligations"] = [proof for proof in wrong["proof_obligations"] if proof["class"] != "E"]
    case("X10_FRESH_PROOF_CLASS_REQUIRED", lambda: _expect_failure(
        "PROOF_CLASS_COVERAGE_INVALID", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    wrong["component_certification_matrix"][16]["proposed_ex_classification"] = "CERTIFIED"
    case("X11_VECTOR_COMPONENT_CANNOT_CERTIFY", lambda: _expect_failure(
        "UNAUTHORIZED_COMPONENT_TRANSITION__17", lambda: validate_payload(wrong)
    ))
    wrong = copy.deepcopy(certificate)
    first_counter = next(iter(wrong["operational_counters"]))
    wrong["operational_counters"][first_counter] = 1
    case("X12_OPERATIONAL_COUNTER_MUST_STAY_ZERO", lambda: _expect_failure(
        "OPERATIONAL_COUNTER_NONZERO", lambda: validate_payload(wrong)
    ))
    passed = sum(item["result"] == "PASS" for item in results)
    return {
        "regression_total": len(results),
        "regression_pass": passed,
        "regression_fail": len(results) - passed,
        "results": results,
    }


def validate(path: Path) -> dict[str, Any]:
    envelope = load_certificate(path)
    certificate = envelope["certificate"]
    payload_result = validate_payload(certificate)
    regressions = run_regressions(certificate)
    if regressions["regression_fail"]:
        _fail("EX_CERTIFICATION_REGRESSION_FAILURE")
    return {
        "schema_id": "G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATION_RESULT_V1",
        "certificate_path": str(path),
        "certificate_inner_sha256": envelope["certificate_sha256"],
        "source_manifest_inner_sha256": EXPECTED_MANIFEST_INNER_SHA256,
        "freeze_decision": certificate["freeze_decision"],
        "reusable_p11_spce_execution_substrate": certificate["reusable_p11_spce_execution_substrate"],
        "component_counts": payload_result["component_counts"],
        "blocker_state_after": certificate["blocker_state_after"],
        **regressions,
        "operational_effect": 0,
        "authority_effect_beyond_certification_scope": 0,
        "credit_effect": 0,
    }


def main() -> int:
    default_certificate = Path(__file__).resolve().parent.parent / CERTIFICATE_FILENAME
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path, default=default_certificate)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.certificate.resolve())
    except (CertificationValidationError, OSError) as exc:
        print(f"FINAL_VALIDATION=FAIL_CLOSED__{exc}")
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print("FINAL_VALIDATION=PASS")
        print(f"FREEZE_DECISION={result['freeze_decision']}")
        print(f"REUSABLE_P11_SPCE_EXECUTION_SUBSTRATE={result['reusable_p11_spce_execution_substrate']}")
        for identity in sorted(result["blocker_state_after"]):
            print(f"{identity}_STATE_AFTER={result['blocker_state_after'][identity]}")
        for classification in sorted(result["component_counts"]):
            print(f"{classification}_COMPONENT_COUNT={result['component_counts'][classification]}")
        print(f"REGRESSION_TOTAL={result['regression_total']}")
        print(f"REGRESSION_PASS={result['regression_pass']}")
        print(f"REGRESSION_FAIL={result['regression_fail']}")
        print(f"CERTIFICATE_INNER_SHA256={result['certificate_inner_sha256']}")
        print("OPERATIONAL_EFFECT=0")
        print("CREDIT_EFFECT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
