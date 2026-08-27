#!/usr/bin/env python3
"""Read-only fail-closed validator for P11_ENTRY_DEFINITION_V1.

This module is an evidence oracle. It does not import, wrap, or invoke the
operational P11 consumer and creates no execution, authority, or credit effect.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


MODEL_FILENAME = "G77_256EU_P11_ENTRY_SEMANTIC_MODEL_AND_REGRESSION_MATRIX_V1.json"
EXPECTED_ENVELOPE_SCHEMA = "G77_256EU_P11_ENTRY_SEMANTIC_MODEL_ENVELOPE_V1"
EXPECTED_MODEL_SCHEMA = "G77_256EU_P11_ENTRY_SEMANTIC_MODEL_V1"
EXPECTED_HEAD = "34a6343e229042ab1d435444687fe5d665b90724"
EXPECTED_TREE = "6c042e3fe1ccbab3389d4cab401e4598f6479adf"
EXPECTED_EVENT_FIELDS = {
    "boundary_request",
    "pre_attempt_gate_evaluation",
    "pre_attempt_gates_pass",
    "p11_attempt_authorized",
    "p11_attempt_start",
    "p11_operational_invocation_increment",
    "protected_effect_increment",
    "second_protected_effect_increment",
    "denial_evidence_present",
    "semantic_state_classifiable",
}
COUNTER_FIELDS = (
    "boundary_request_count",
    "pre_attempt_denial_count",
    "p11_entry_count",
    "p11_operational_invocation_count",
    "protected_effect_count",
    "second_protected_effect_count",
    "denial_evidence_count",
    "unclassifiable_request_count",
)


class FailClosedSemanticError(ValueError):
    """Raised when an event or model cannot be constitutionally classified."""


def _fail(token: str) -> None:
    raise FailClosedSemanticError(token)


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
    ).encode("utf-8")


def load_model(path: Path) -> dict[str, Any]:
    try:
        envelope = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_no_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedSemanticError("MODEL_JSON_INVALID") from exc
    if not isinstance(envelope, dict) or set(envelope) != {
        "schema_id",
        "model",
        "model_sha256",
    }:
        _fail("MODEL_ENVELOPE_STRUCTURE_INVALID")
    if envelope["schema_id"] != EXPECTED_ENVELOPE_SCHEMA:
        _fail("MODEL_ENVELOPE_SCHEMA_INVALID")
    model = envelope["model"]
    if not isinstance(model, dict) or model.get("schema_id") != EXPECTED_MODEL_SCHEMA:
        _fail("MODEL_SCHEMA_INVALID")
    preimage = dict(envelope)
    preimage["model_sha256"] = ""
    calculated = hashlib.sha256(canonical_bytes(preimage)).hexdigest()
    if envelope["model_sha256"] != calculated:
        _fail("MODEL_INNER_HASH_INVALID")
    baseline = model.get("required_baseline")
    if not isinstance(baseline, dict):
        _fail("REQUIRED_BASELINE_INVALID")
    if baseline.get("head") != EXPECTED_HEAD or baseline.get("tree") != EXPECTED_TREE:
        _fail("REQUIRED_BASELINE_MISMATCH")
    if set(model.get("event_record_fields", [])) != EXPECTED_EVENT_FIELDS:
        _fail("EVENT_RECORD_FIELD_SET_INVALID")
    regression = model.get("semantic_regression_matrix")
    if not isinstance(regression, list) or not regression:
        _fail("REGRESSION_MATRIX_ABSENT")
    identifiers = [case.get("id") for case in regression if isinstance(case, dict)]
    if len(identifiers) != len(regression) or len(set(identifiers)) != len(identifiers):
        _fail("REGRESSION_IDENTIFIERS_INVALID")
    return envelope


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        _fail(f"EVENT_BOOLEAN_INVALID__{field}")
    return value


def _bit(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value not in (0, 1):
        _fail(f"EVENT_INCREMENT_INVALID__{field}")
    return value


def evaluate_event(event: Any) -> dict[str, int]:
    if not isinstance(event, dict) or set(event) != EXPECTED_EVENT_FIELDS:
        _fail("EVENT_STRUCTURE_INVALID")

    boundary = _bool(event["boundary_request"], "boundary_request")
    gate_evaluation = _bool(
        event["pre_attempt_gate_evaluation"],
        "pre_attempt_gate_evaluation",
    )
    gates_pass = event["pre_attempt_gates_pass"]
    if gates_pass is not None and not isinstance(gates_pass, bool):
        _fail("EVENT_GATE_RESULT_INVALID")
    authorized = _bool(event["p11_attempt_authorized"], "p11_attempt_authorized")
    started = _bool(event["p11_attempt_start"], "p11_attempt_start")
    denial_visible = _bool(event["denial_evidence_present"], "denial_evidence_present")
    classifiable = _bool(
        event["semantic_state_classifiable"],
        "semantic_state_classifiable",
    )
    invocation = _bit(
        event["p11_operational_invocation_increment"],
        "p11_operational_invocation_increment",
    )
    effect = _bit(event["protected_effect_increment"], "protected_effect_increment")
    second_effect = _bit(
        event["second_protected_effect_increment"],
        "second_protected_effect_increment",
    )

    if started and not (
        boundary
        and classifiable
        and gate_evaluation
        and gates_pass is True
        and authorized
    ):
        _fail("ATTEMPT_START_REQUIRES_GATES_PASS_AND_AUTHORIZATION")
    if authorized and not (
        boundary and classifiable and gate_evaluation and gates_pass is True
    ):
        _fail("ATTEMPT_AUTHORIZATION_REQUIRES_GATES_PASS")
    if not classifiable:
        if gate_evaluation or gates_pass is not None or authorized or started:
            _fail("UNCLASSIFIABLE_STATE_MUST_FAIL_CLOSED")
        if invocation or effect or second_effect:
            _fail("UNCLASSIFIABLE_STATE_HAS_OPERATIONAL_EFFECT")
    if gate_evaluation and gates_pass is False:
        if authorized or started:
            _fail("PRE_ATTEMPT_DENIAL_CANNOT_AUTHORIZE_OR_START")
        if not denial_visible:
            _fail("PRE_ATTEMPT_DENIAL_EVIDENCE_REQUIRED")
    if gates_pass is True and denial_visible:
        _fail("PASSING_GATE_CANNOT_BE_DENIAL")

    entry = int(
        boundary
        and classifiable
        and gate_evaluation
        and gates_pass is True
        and authorized
        and started
    )
    denial = int(
        boundary
        and classifiable
        and gate_evaluation
        and gates_pass is False
        and not authorized
        and not started
        and denial_visible
    )
    if invocation > entry:
        _fail("INVOCATION_REQUIRES_P11_ENTRY")
    if effect > invocation:
        _fail("PROTECTED_EFFECT_REQUIRES_INVOCATION")
    if second_effect > effect:
        _fail("SECOND_PROTECTED_EFFECT_REQUIRES_PROTECTED_EFFECT")

    return {
        "boundary_request_count": int(boundary),
        "pre_attempt_denial_count": denial,
        "p11_entry_count": entry,
        "p11_operational_invocation_count": invocation,
        "protected_effect_count": effect,
        "second_protected_effect_count": second_effect,
        "denial_evidence_count": int(denial_visible),
        "unclassifiable_request_count": int(boundary and not classifiable),
    }


def aggregate_events(events: Any) -> dict[str, int]:
    if not isinstance(events, list) or not events:
        _fail("EVENT_LIST_INVALID")
    aggregate = {field: 0 for field in COUNTER_FIELDS}
    for event in events:
        result = evaluate_event(event)
        for field in COUNTER_FIELDS:
            aggregate[field] += result[field]
    return aggregate


def _resolve(model: dict[str, Any], path: Any) -> Any:
    if not isinstance(path, list) or not path or not all(
        isinstance(item, str) and item for item in path
    ):
        _fail("POLICY_PATH_INVALID")
    value: Any = model
    for item in path:
        if not isinstance(value, dict) or item not in value:
            _fail("POLICY_PATH_UNRESOLVED")
        value = value[item]
    return value


def run_regressions(model: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, str]] = []
    for case in model["semantic_regression_matrix"]:
        case_id = case["id"]
        kind = case.get("kind")
        try:
            if kind == "event":
                actual = aggregate_events(case.get("events"))
                expected = case.get("expected")
                if not isinstance(expected, dict) or any(
                    actual.get(field) != value for field, value in expected.items()
                ):
                    _fail(f"REGRESSION_EXPECTATION_MISMATCH__{case_id}")
            elif kind == "policy":
                if _resolve(model, case.get("path")) != case.get("expected_value"):
                    _fail(f"POLICY_EXPECTATION_MISMATCH__{case_id}")
            elif kind == "rejected_event":
                expected_error = case.get("expected_error")
                try:
                    aggregate_events(case.get("events"))
                except FailClosedSemanticError as exc:
                    if str(exc) != expected_error:
                        _fail(f"REJECTION_REASON_MISMATCH__{case_id}")
                else:
                    _fail(f"ADVERSARIAL_EVENT_ACCEPTED__{case_id}")
            else:
                _fail(f"REGRESSION_KIND_INVALID__{case_id}")
        except FailClosedSemanticError as exc:
            results.append({"id": case_id, "result": "FAIL", "reason": str(exc)})
        else:
            results.append({"id": case_id, "result": "PASS", "reason": "EXPECTED_SEMANTICS_OBSERVED"})

    canonical_case = next(
        (case for case in model["semantic_regression_matrix"] if case["id"] == "T06"),
        None,
    )
    if canonical_case is None:
        _fail("CANONICAL_LIFECYCLE_REGRESSION_ABSENT")
    canonical_actual = aggregate_events(canonical_case["events"])
    normative = model.get("normative_expected_model")
    if not isinstance(normative, dict) or any(
        canonical_actual.get(field) != value for field, value in normative.items()
    ):
        _fail("NORMATIVE_COUNTER_MODEL_MISMATCH")

    passed = sum(result["result"] == "PASS" for result in results)
    return {
        "regression_total": len(results),
        "regression_pass": passed,
        "regression_fail": len(results) - passed,
        "results": results,
        "normative_counter_model": normative,
    }


def validate(path: Path) -> dict[str, Any]:
    envelope = load_model(path)
    regression = run_regressions(envelope["model"])
    if regression["regression_fail"]:
        _fail("SEMANTIC_REGRESSION_FAILURE")
    return {
        "schema_id": "G77_256EU_P11_ENTRY_SEMANTICS_VALIDATION_RESULT_V1",
        "model_path": str(path),
        "model_sha256": envelope["model_sha256"],
        "p11_entry_semantics_result": "PASS__P11_ENTRY_DEFINITION_V1_FORMALIZED",
        "p11_counter_model_result": "PASS__EXPLICIT_DISTINCT_COUNTER_MODEL_COHERENT",
        **regression,
        "operational_effect": 0,
        "authority_effect": 0,
        "credit_effect": 0,
    }


def main() -> int:
    default_model = Path(__file__).resolve().parent.parent / MODEL_FILENAME
    parser = argparse.ArgumentParser()
    parser.add_argument("model", nargs="?", type=Path, default=default_model)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.model.resolve())
    except FailClosedSemanticError as exc:
        print(f"FINAL_VALIDATION=FAIL_CLOSED__{exc}")
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print("FINAL_VALIDATION=PASS")
        print(f"P11_ENTRY_SEMANTICS_RESULT={result['p11_entry_semantics_result']}")
        print(f"P11_COUNTER_MODEL_RESULT={result['p11_counter_model_result']}")
        print(f"REGRESSION_TOTAL={result['regression_total']}")
        print(f"REGRESSION_PASS={result['regression_pass']}")
        print(f"REGRESSION_FAIL={result['regression_fail']}")
        print(f"MODEL_SHA256={result['model_sha256']}")
        print("OPERATIONAL_EFFECT=0")
        print("AUTHORITY_EFFECT=0")
        print("CREDIT_EFFECT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
