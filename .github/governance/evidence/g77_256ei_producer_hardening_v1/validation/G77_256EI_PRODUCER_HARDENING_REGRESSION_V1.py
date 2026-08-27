#!/usr/bin/env python3
"""Repository-only regression matrix for the EI producer hardening."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from jsonschema import Draft202012Validator


REQUIRED_HEAD = "da84f3e5c732c5467ea4f56db0338217f0929022"
REQUIRED_TREE = "dbf4bfab2e3d90160998036042396b25491e6841"
EVIDENCE_ROOT = ".github/governance/evidence/g77_256ei_producer_hardening_v1"
PRODUCER_PATH = f"{EVIDENCE_ROOT}/producer/G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_V1.py"
RUNNER_PATH = f"{EVIDENCE_ROOT}/validation/G77_256EI_PRODUCER_HARDENING_REGRESSION_V1.py"
PHASE_A_PATH = f"{EVIDENCE_ROOT}/G77_256EI_SPCE_PHASE_A_CHECKPOINT_V1.json"
FIXTURE_PATH = f"{EVIDENCE_ROOT}/fixtures/G77_256EI_POSITIVE_CANONICAL_V1_CANDIDATE_V1.json"
EB_RECEIPT_PATH = f"{EVIDENCE_ROOT}/G77_256EI_POSITIVE_EB_VALIDATION_RECEIPT_V1.json"
DU_SCHEMA_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
)
EB_VALIDATOR_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
HISTORICAL_EG_CANDIDATE = (
    ".github/governance/evidence/g77_256eg_p11_operational_v1/raw/"
    "G77_256EG_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json"
)
HISTORICAL_EG_SHA256 = "d4e58b1c6f11d7617993ac6c559a7d29ffb96c6aaf034b71f9911a651111ebd4"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module import failed: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def rehash(du: ModuleType, envelope: dict[str, Any]) -> None:
    envelope["manifest_sha256"] = du.sha256_bytes(
        du.canonical_bytes(envelope["manifest"])
    )


def case(name: str, action: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        detail = action()
    except Exception as exc:
        return {
            "case": name,
            "result": "FAIL",
            "unexpected_exception": type(exc).__name__,
            "message": str(exc),
        }
    return {"case": name, "result": "PASS", **detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    producer = load_module(repository_root / PRODUCER_PATH, "g77_256ei_producer_v1")
    producer.authenticate_baseline(repository_root)
    du = producer.load_du(repository_root)
    eb = load_module(repository_root / EB_VALIDATOR_PATH, "g77_256eb_validator_v1")
    schema = load_json(repository_root / DU_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    schema_validator = Draft202012Validator(schema)
    fixture_path = repository_root / FIXTURE_PATH
    fixture = load_json(fixture_path)
    expected_fixture = producer.build(repository_root)
    if fixture_path.read_bytes() != du.canonical_bytes(expected_fixture):
        raise RuntimeError("persisted positive fixture differs from deterministic producer output")
    required = frozenset(du.REQUIRED_PROHIBITED_ACTIONS)
    expected_sorted = sorted(required)
    if fixture["manifest"]["prohibited_actions"] != expected_sorted:
        raise RuntimeError("positive fixture does not contain exact canonical DU vocabulary")

    cases: list[dict[str, Any]] = []

    def rejection(candidate: dict[str, Any]) -> dict[str, Any]:
        schema_errors = list(schema_validator.iter_errors(candidate))
        if not schema_errors:
            raise AssertionError("candidate unexpectedly passed DU schema")
        try:
            du.validate_envelope(
                candidate,
                repository_root,
                expected_head=REQUIRED_HEAD,
            )
        except du.CompatibilityError as exc:
            if exc.code != "CONSTITUTIONAL_ADMISSIBILITY_FAILED":
                raise AssertionError(f"unexpected DU failure: {exc.code}") from exc
            return {
                "expected_schema_result": "FAIL",
                "schema_error_count": len(schema_errors),
                "expected_du_failure": exc.code,
                "qualified_replacement_admitted": False,
            }
        raise AssertionError("inadmissible candidate unexpectedly passed DU")

    missing_names = {
        "VM_CREATION": "MISSING_VM_CREATION",
        "VM_BOOT": "MISSING_VM_BOOT",
        "HUMAN_OPERATIONAL_ACT_CREATION": "MISSING_HUMAN_OPERATIONAL_ACT_CREATION",
        "P11_ENTRY": "MISSING_P11_ENTRY",
        "E05_EXECUTION": "MISSING_E05_EXECUTION",
        "P12_ENTRY": "MISSING_P12_ENTRY",
        "PRODUCTION_ROUTE": "MISSING_PRODUCTION_ROUTE",
        "EXECUTION_REPLAY": "MISSING_EXECUTION_REPLAY",
    }
    for token, name in missing_names.items():
        candidate = deepcopy(fixture)
        candidate["manifest"]["prohibited_actions"].remove(token)
        rehash(du, candidate)
        cases.append(case(name, lambda candidate=candidate: rejection(candidate)))

    substitutions = {
        "VM_CREATION": ("VM_CREATION_AFTER_ADMISSION", "QUALIFIED_VM_CREATION_SUBSTITUTION"),
        "VM_BOOT": ("VM_BOOT_AFTER_MATERIALIZATION", "QUALIFIED_VM_BOOT_SUBSTITUTION"),
        "HUMAN_OPERATIONAL_ACT_CREATION": (
            "HUMAN_OPERATIONAL_ACT_CREATION_AFTER_COMMISSIONING",
            "QUALIFIED_HUMAN_OPERATIONAL_ACT_CREATION_SUBSTITUTION",
        ),
        "P11_ENTRY": ("P11_ENTRY_AFTER_COMMISSIONING", "QUALIFIED_P11_ENTRY_SUBSTITUTION"),
        "E05_EXECUTION": ("E05_EXECUTION_AFTER_ADMISSION", "QUALIFIED_E05_EXECUTION_SUBSTITUTION"),
    }
    for exact, (qualified, name) in substitutions.items():
        candidate = deepcopy(fixture)
        candidate["manifest"]["prohibited_actions"].remove(exact)
        candidate["manifest"]["prohibited_actions"].append(qualified)
        candidate["manifest"]["prohibited_actions"].sort()
        rehash(du, candidate)
        cases.append(case(name, lambda candidate=candidate: rejection(candidate)))

    candidate = deepcopy(fixture)
    for exact in ("VM_CREATION", "VM_BOOT", "E05_EXECUTION"):
        candidate["manifest"]["prohibited_actions"].remove(exact)
    candidate["manifest"]["prohibited_actions"].extend([
        "VM_CREATION_AFTER_ADMISSION",
        "VM_BOOT_AFTER_MATERIALIZATION",
        "E05_EXECUTION_AFTER_ADMISSION",
        "E05_EXECUTION_BEFORE_EB_EE_ADMISSION",
    ])
    candidate["manifest"]["prohibited_actions"].sort()
    rehash(du, candidate)
    cases.append(case(
        "MULTIPLE_QUALIFIED_ALIASES_WITHOUT_EXACT_TOKEN",
        lambda candidate=candidate: rejection(candidate),
    ))

    candidate = deepcopy(fixture)
    candidate["manifest"]["prohibited_actions"].remove("VM_CREATION")
    rehash(du, candidate)

    def structurally_valid_schema_invalid() -> dict[str, Any]:
        parsed = json.loads(du.canonical_bytes(candidate))
        if parsed != candidate:
            raise AssertionError("candidate JSON round-trip changed")
        result = rejection(candidate)
        result["json_structure"] = "VALID"
        return result

    cases.append(case(
        "STRUCTURALLY_VALID_JSON_DU_SCHEMA_INVALID",
        structurally_valid_schema_invalid,
    ))

    def schema_valid_but_additional_requirement_missing() -> dict[str, Any]:
        if list(schema_validator.iter_errors(fixture)):
            raise AssertionError("positive fixture unexpectedly fails schema")
        try:
            du.validate_envelope(
                fixture,
                repository_root,
                expected_head=REQUIRED_HEAD,
                required_prohibited_actions=frozenset({
                    "G77_256EI_ADDITIONAL_REQUIRED_PROHIBITION"
                }),
            )
        except du.CompatibilityError as exc:
            if exc.code != "CONSTITUTIONAL_ADMISSIBILITY_FAILED":
                raise AssertionError(f"unexpected DU failure: {exc.code}") from exc
            return {
                "schema_result": "PASS",
                "expected_du_failure": exc.code,
                "additional_profile_requirement_admitted": False,
            }
        raise AssertionError("additional required prohibition was silently dropped")

    cases.append(case(
        "SCHEMA_VALID_ADDITIONAL_DU_REQUIREMENT_INADMISSIBLE",
        schema_valid_but_additional_requirement_missing,
    ))

    candidate = deepcopy(fixture)
    candidate["manifest"]["prohibited_actions"].remove("P11_ENTRY")
    rehash(du, candidate)
    cases.append(case(
        "REQUIRED_TOKEN_REMOVED_AFTER_GENERATION",
        lambda candidate=candidate: rejection(candidate),
    ))

    def reinterpretation_forbidden() -> dict[str, Any]:
        proposed = set(required)
        proposed.remove("VM_CREATION")
        proposed.add("VM_CREATION_AFTER_ADMISSION")
        try:
            producer.refuse_vocabulary_reinterpretation(du, proposed)
        except producer.ProducerHardeningError as exc:
            if exc.code != "DU_VOCABULARY_REINTERPRETATION_FORBIDDEN":
                raise AssertionError(f"unexpected producer failure: {exc.code}") from exc
            return {"expected_producer_failure": exc.code}
        raise AssertionError("producer accepted reinterpreted DU vocabulary")

    cases.append(case(
        "PRODUCER_DU_VOCABULARY_REINTERPRETATION",
        reinterpretation_forbidden,
    ))

    def historical_eg_rejected() -> dict[str, Any]:
        historical_path = repository_root / HISTORICAL_EG_CANDIDATE
        if sha256_path(historical_path) != HISTORICAL_EG_SHA256:
            raise AssertionError("historical EG candidate bytes changed")
        historical = load_json(historical_path)
        errors = list(schema_validator.iter_errors(historical))
        if len(errors) != 5:
            raise AssertionError(f"expected five historical schema errors, got {len(errors)}")
        try:
            du.validate_file(
                historical_path,
                repository_root,
                expected_head=historical["manifest"]["required_head"],
            )
        except du.CompatibilityError as exc:
            if exc.code != "CONSTITUTIONAL_ADMISSIBILITY_FAILED":
                raise AssertionError(f"unexpected historical failure: {exc.code}") from exc
            return {
                "historical_sha256": HISTORICAL_EG_SHA256,
                "schema_error_count": len(errors),
                "historical_first_failure_preserved": exc.code,
            }
        raise AssertionError("historical EG candidate unexpectedly passed")

    cases.append(case(
        "HISTORICAL_EG_CANDIDATE_REMAINS_REJECTED",
        historical_eg_rejected,
    ))

    def positive_passes() -> dict[str, Any]:
        errors = list(schema_validator.iter_errors(fixture))
        if errors:
            raise AssertionError(f"positive fixture schema errors: {len(errors)}")
        result = du.validate_file(
            fixture_path,
            repository_root,
            expected_head=REQUIRED_HEAD,
        )
        if set(result.values()) != {"PASS"}:
            raise AssertionError(f"DU positive result is not all PASS: {result}")
        return {
            "schema_result": "PASS",
            "du_gate_results": result,
            "operational_authority_created": False,
        }

    cases.append(case(
        "POSITIVE_HARDENED_FIXTURE_PASSES_DU_CHAIN",
        positive_passes,
    ))

    def duplicates_canonicalized() -> dict[str, Any]:
        supplied = list(required) + ["VM_CREATION", "VM_CREATION", "E05_EXECUTION"]
        canonical = producer.canonicalize_prohibitions(du, supplied)
        if canonical != expected_sorted:
            raise AssertionError("duplicates changed canonical prohibition meaning")
        return {
            "input_count": len(supplied),
            "canonical_count": len(canonical),
            "semantic_set_unchanged": True,
        }

    cases.append(case(
        "DUPLICATE_INPUT_CANONICALIZED_WITHOUT_SEMANTIC_CHANGE",
        duplicates_canonicalized,
    ))

    if len(cases) != 21 or any(item["result"] != "PASS" for item in cases):
        raise RuntimeError("EI regression matrix did not complete with 21 PASS cases")

    eb_receipt_path = repository_root / EB_RECEIPT_PATH
    eb_result = eb.verify_receipt_file(repository_root, eb_receipt_path)
    if eb_result.get("overall_result") != "PASS":
        raise RuntimeError("EB receipt reauthentication did not return PASS")

    phase_a = load_json(repository_root / PHASE_A_PATH)
    evidence = {
        "schema_id": "G77_256EI_PRODUCER_HARDENING_VALIDATION_EVIDENCE_V1",
        "generation_identity": (
            "G77_256EI_REPOSITORY_ONLY_EXACT_DU_PROHIBITION_VOCABULARY_"
            "PRODUCER_HARDENING_V1"
        ),
        "required_head": REQUIRED_HEAD,
        "required_tree": REQUIRED_TREE,
        "phase_a_binding": {
            "path": PHASE_A_PATH,
            "file_sha256": sha256_path(repository_root / PHASE_A_PATH),
            "inner_sha256": phase_a["checkpoint_sha256"],
        },
        "producer_binding": {
            "path": PRODUCER_PATH,
            "sha256": sha256_path(repository_root / PRODUCER_PATH),
        },
        "regression_runner_binding": {
            "path": RUNNER_PATH,
            "sha256": sha256_path(repository_root / RUNNER_PATH),
        },
        "du_bindings": {
            "contract_sha256": "e2fc8ddff0376f2e6acbd01f2cefb714dbd299baf1013d055d5ceeae251fed9e",
            "schema_sha256": producer.DU_SCHEMA_SHA256,
            "validator_sha256": producer.DU_VALIDATOR_SHA256,
            "contract_changed": False,
            "schema_changed": False,
            "validator_changed": False,
        },
        "exact_du_prohibition_vocabulary": expected_sorted,
        "positive_fixture": {
            "path": FIXTURE_PATH,
            "file_sha256": sha256_path(fixture_path),
            "manifest_inner_sha256": fixture["manifest_sha256"],
            "schema_result": "PASS",
            "du_result": "PASS__FOUR_GATES",
            "non_operational": True,
        },
        "eb_receipt": {
            "path": EB_RECEIPT_PATH,
            "file_sha256": sha256_path(eb_receipt_path),
            "receipt_inner_sha256": load_json(eb_receipt_path)["receipt_inner_sha256"],
            "verification_result": eb_result,
            "operational_authorization": False,
        },
        "ee_validation": {
            "result": "NOT_RUN__NOT_NECESSARY_FOR_EXACT_PRODUCER_DEFECT_CLOSURE",
            "operational_authorization": False,
        },
        "producer_determinism": {
            "persisted_bytes_equal_fresh_in_memory_build": True,
            "canonical_serialization": "PASS",
            "canonical_prohibition_order": expected_sorted,
            "duplicates_change_semantic_meaning": False,
        },
        "regression_matrix": {
            "required_case_count": 20,
            "additional_case_count": 1,
            "total_case_count": len(cases),
            "cases": cases,
            "result": "PASS",
        },
        "historical_immutability": {
            "eg_candidate_sha256": HISTORICAL_EG_SHA256,
            "eg_candidate_changed": False,
            "historical_eg_rejection_preserved": True,
            "eh_report_changed": False,
        },
        "operational_counters": {
            "vm_creation_count": 0,
            "vm_boot_count": 0,
            "second_vm_count": 0,
            "automatic_retry_count": 0,
            "repair_and_continue_count": 0,
            "commissioning_execution_count": 0,
            "commissioning_pass_count": 0,
            "human_operational_act_created_count": 0,
            "human_operational_act_submitted_count": 0,
            "human_operational_act_claimed_count": 0,
            "human_operational_act_invoked_count": 0,
            "human_operational_act_terminally_bound_count": 0,
            "human_operational_act_permanently_exhausted_count": 0,
            "p11_entry_count": 0,
            "p11_operational_invocation_count": 0,
            "e05_case_execution_count": 0,
            "p12_entry_count": 0,
            "production_route_count": 0,
            "full_history_reconstruction_count": 0,
            "execution_replay_count": 0,
            "materialization_replay_count": 0,
        },
        "e05_frontier": {
            "wrong_caller_state": "UNSATISFIED",
            "e05_total_obligation_count": 18,
            "e05_satisfied_obligation_count": 4,
            "e05_remaining_obligation_count": 14,
            "p11_e05_completion_state": "INCOMPLETE",
            "g2_state": "OPEN",
            "g3_entry_authorized": False,
        },
        "producer_hardening_result": "PASS",
        "exact_du_prohibition_vocabulary_preserved": True,
        "auto_continuable": False,
    }
    envelope = {
        "schema_id": "G77_256EI_PRODUCER_HARDENING_VALIDATION_EVIDENCE_ENVELOPE_V1",
        "evidence": evidence,
        "evidence_sha256": hashlib.sha256(canonical_bytes(evidence)).hexdigest(),
    }
    expected_output = repository_root / (
        f"{EVIDENCE_ROOT}/G77_256EI_PRODUCER_HARDENING_VALIDATION_EVIDENCE_V1.json"
    )
    if args.evidence_output.resolve() != expected_output.resolve():
        raise RuntimeError("validation evidence output is outside authorized EI scope")
    args.evidence_output.write_bytes(canonical_bytes(envelope))
    print(canonical_bytes({
        "producer_hardening_result": "PASS",
        "positive_fixture_result": "PASS",
        "negative_regression_matrix_result": "PASS",
        "case_count": len(cases),
        "eb_receipt_result": "PASS__REAUTHENTICATED",
        "wrong_caller_state": "UNSATISFIED",
        "e05_satisfied_obligation_count": 4,
    }).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
