"""Canonical JSON loading and hashing with the ICEM V1 value domain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, TypeAlias
import unicodedata

from .errors import ConstitutionalValidationInputError

JsonSource: TypeAlias = Mapping[str, Any] | bytes | bytearray | str | Path

_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_ZERO_HASH = "sha256:" + ("0" * 64)


def canonical_json(value: Any) -> str:
    """Return the certified UTF-8 JSON canonical form."""

    _validate_json_domain(value, "$")
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:  # pragma: no cover - domain guard owns normal failures.
        raise ConstitutionalValidationInputError(
            "NON_CANONICAL_JSON",
            "input cannot be represented as canonical JSON",
        ) from exc


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def hash_without_field(value: Mapping[str, Any], field: str) -> str:
    body = dict(value)
    body.pop(field, None)
    return canonical_hash(body)


def validate_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise ConstitutionalValidationInputError(
            "INVALID_HASH_FORMAT",
            f"{label} must be a prefixed lowercase SHA-256 hash",
        )
    if value == _ZERO_HASH:
        raise ConstitutionalValidationInputError(
            "ZERO_HASH_REJECTED",
            f"{label} cannot be a zero hash",
        )
    return value


def verify_self_hash(value: Mapping[str, Any], field: str, label: str) -> str:
    declared = validate_hash(value.get(field), f"{label}.{field}")
    expected = hash_without_field(value, field)
    if declared != expected:
        raise ConstitutionalValidationInputError(
            "HASH_MISMATCH",
            f"{label} canonical hash mismatch",
        )
    return declared


def load_json_object(source: JsonSource, label: str) -> dict[str, Any]:
    """Load a detached JSON object from one explicitly supplied source."""

    if isinstance(source, Mapping):
        _validate_json_domain(source, "$")
        raw = canonical_json(source)
    elif isinstance(source, (bytes, bytearray)):
        try:
            raw = bytes(source).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConstitutionalValidationInputError(
                "INVALID_UTF8",
                f"{label} must be UTF-8 JSON",
            ) from exc
    elif isinstance(source, (str, Path)):
        path = Path(source)
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ConstitutionalValidationInputError(
                "SOURCE_UNAVAILABLE",
                f"{label} source is unavailable",
            ) from exc
    else:
        raise ConstitutionalValidationInputError(
            "UNSUPPORTED_SOURCE",
            f"{label} source type is unsupported",
        )

    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except ConstitutionalValidationInputError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ConstitutionalValidationInputError(
            "MALFORMED_JSON",
            f"{label} is not valid JSON",
        ) from exc
    if not isinstance(parsed, dict):
        raise ConstitutionalValidationInputError(
            "ROOT_NOT_OBJECT",
            f"{label} must be a JSON object",
        )
    _validate_json_domain(parsed, "$")
    return parsed


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConstitutionalValidationInputError(
                "DUPLICATE_JSON_KEY",
                f"duplicate JSON key rejected: {key}",
            )
        result[key] = value
    return result


def _reject_float(_value: str) -> Any:
    raise ConstitutionalValidationInputError(
        "FLOAT_REJECTED",
        "floating-point JSON values are prohibited",
    )


def _reject_constant(_value: str) -> Any:
    raise ConstitutionalValidationInputError(
        "NON_JSON_NUMBER_REJECTED",
        "non-JSON numeric constants are prohibited",
    )


def _validate_json_domain(value: Any, path: str) -> None:
    if value is None:
        raise ConstitutionalValidationInputError(
            "NULL_REJECTED",
            f"null value rejected at {path}",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise ConstitutionalValidationInputError(
            "FLOAT_REJECTED",
            f"floating-point value rejected at {path}",
        )
    if isinstance(value, str):
        if value != unicodedata.normalize("NFC", value):
            raise ConstitutionalValidationInputError(
                "NON_NFC_STRING",
                f"non-NFC string rejected at {path}",
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_domain(item, f"{path}/{index}")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ConstitutionalValidationInputError(
                    "NON_STRING_KEY",
                    f"non-string object key rejected at {path}",
                )
            if key != unicodedata.normalize("NFC", key):
                raise ConstitutionalValidationInputError(
                    "NON_NFC_STRING",
                    f"non-NFC object key rejected at {path}",
                )
            _validate_json_domain(item, f"{path}/{key}")
        return
    raise ConstitutionalValidationInputError(
        "NON_JSON_VALUE",
        f"non-JSON value rejected at {path}",
    )


__all__ = [
    "JsonSource",
    "canonical_hash",
    "canonical_json",
    "hash_without_field",
    "load_json_object",
    "validate_hash",
    "verify_self_hash",
]
