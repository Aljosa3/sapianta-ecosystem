"""Minimal deterministic ECC V1 rule evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import canonical_json
from .errors import ConstitutionalValidationInputError

SUPPORTED_OPERATORS = frozenset({"ALL", "EQUALS", "EXISTS", "SUBSET_OF"})
_MISSING = object()


@dataclass(frozen=True)
class RuleEvaluation:
    passed: bool
    detail: str


def validate_rule_schema(rule: Any, *, depth: int = 0) -> None:
    if depth > 64:
        raise ConstitutionalValidationInputError(
            "RULE_DEPTH_EXCEEDED",
            "rule nesting exceeds the certified bound",
        )
    if not isinstance(rule, dict):
        raise ConstitutionalValidationInputError(
            "INVALID_RULE_SCHEMA",
            "rule must be an object",
        )
    operator = rule.get("operator")
    if operator not in SUPPORTED_OPERATORS:
        raise ConstitutionalValidationInputError(
            "UNSUPPORTED_RULE_OPERATOR",
            "contract contains an unsupported rule operator",
        )
    if operator == "ALL":
        if set(rule) != {"operator", "rules"}:
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_SCHEMA",
                "ALL rule has invalid fields",
            )
        rules = rule["rules"]
        if not isinstance(rules, list) or not rules:
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_SCHEMA",
                "ALL requires a non-empty rules array",
            )
        for child in rules:
            validate_rule_schema(child, depth=depth + 1)
        return
    if operator == "EXISTS":
        if set(rule) != {"operator", "operand"}:
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_SCHEMA",
                "EXISTS rule has invalid fields",
            )
        _validate_operand(rule["operand"])
        return
    if set(rule) != {"operator", "left", "right"}:
        raise ConstitutionalValidationInputError(
            "INVALID_RULE_SCHEMA",
            f"{operator} rule has invalid fields",
        )
    _validate_operand(rule["left"])
    _validate_operand(rule["right"])


def evaluate_rule(rule: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]) -> RuleEvaluation:
    operator = rule["operator"]
    if operator == "ALL":
        for index, child in enumerate(rule["rules"]):
            result = evaluate_rule(child, evidence)
            if not result.passed:
                return RuleEvaluation(False, f"ALL child {index} failed: {result.detail}")
        return RuleEvaluation(True, "all child rules passed")
    if operator == "EXISTS":
        value = _resolve_operand(rule["operand"], evidence)
        if value is _MISSING:
            return RuleEvaluation(False, "required operand does not exist")
        return RuleEvaluation(True, "required operand exists")
    left = _resolve_operand(rule["left"], evidence)
    right = _resolve_operand(rule["right"], evidence)
    if left is _MISSING or right is _MISSING:
        return RuleEvaluation(False, "rule operand is missing")
    if operator == "EQUALS":
        passed = _json_equal(left, right)
        return RuleEvaluation(passed, "operands are equal" if passed else "operands are not equal")
    if operator == "SUBSET_OF":
        if not isinstance(left, list) or not isinstance(right, list):
            return RuleEvaluation(False, "SUBSET_OF operands must both be arrays")
        right_values = {canonical_json(item) for item in right}
        passed = all(canonical_json(item) in right_values for item in left)
        return RuleEvaluation(passed, "left array is a subset" if passed else "left array is not a subset")
    raise ConstitutionalValidationInputError(
        "UNSUPPORTED_RULE_OPERATOR",
        "rule evaluator received an unsupported operator",
    )


def _validate_operand(operand: Any) -> None:
    if not isinstance(operand, dict):
        raise ConstitutionalValidationInputError(
            "INVALID_RULE_OPERAND",
            "rule operand must be an object",
        )
    kind = operand.get("kind")
    if kind == "LITERAL":
        if set(operand) != {"kind", "value"}:
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_OPERAND",
                "literal operand has invalid fields",
            )
        canonical_json(operand["value"])
        return
    if kind == "REFERENCE":
        if set(operand) != {"kind", "source", "evidence_id", "pointer"}:
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_OPERAND",
                "reference operand has invalid fields",
            )
        if operand["source"] != "EVIDENCE":
            raise ConstitutionalValidationInputError(
                "UNSUPPORTED_RULE_SOURCE",
                "only explicit evidence references are supported",
            )
        if not _non_empty_string(operand["evidence_id"]):
            raise ConstitutionalValidationInputError(
                "INVALID_RULE_OPERAND",
                "reference evidence_id must be non-empty",
            )
        pointer = operand["pointer"]
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            raise ConstitutionalValidationInputError(
                "INVALID_JSON_POINTER",
                "reference pointer is not a JSON Pointer",
            )
        _pointer_tokens(pointer)
        return
    raise ConstitutionalValidationInputError(
        "INVALID_RULE_OPERAND",
        "rule operand kind is unsupported",
    )


def _resolve_operand(operand: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]) -> Any:
    if operand["kind"] == "LITERAL":
        return operand["value"]
    artifact = evidence.get(operand["evidence_id"])
    if artifact is None:
        return _MISSING
    return _resolve_pointer(artifact, operand["pointer"])


def _resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    for token in _pointer_tokens(pointer):
        if isinstance(current, Mapping):
            if token not in current:
                return _MISSING
            current = current[token]
            continue
        if isinstance(current, list):
            if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                return _MISSING
            index = int(token)
            if index >= len(current):
                return _MISSING
            current = current[index]
            continue
        return _MISSING
    return current


def _pointer_tokens(pointer: str) -> tuple[str, ...]:
    if pointer == "":
        return ()
    tokens: list[str] = []
    for raw in pointer[1:].split("/"):
        index = 0
        decoded = ""
        while index < len(raw):
            if raw[index] != "~":
                decoded += raw[index]
                index += 1
                continue
            if index + 1 >= len(raw) or raw[index + 1] not in {"0", "1"}:
                raise ConstitutionalValidationInputError(
                    "INVALID_JSON_POINTER",
                    "JSON Pointer contains an invalid escape",
                )
            decoded += "~" if raw[index + 1] == "0" else "/"
            index += 2
        tokens.append(decoded)
    return tuple(tokens)


def _json_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if set(left) != set(right):
            return False
        return all(_json_equal(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right))
    return bool(left == right)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "RuleEvaluation",
    "SUPPORTED_OPERATORS",
    "evaluate_rule",
    "validate_rule_schema",
]
