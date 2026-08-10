"""Candidate H CJ1 canonical serialization.

This module owns only the closed byte representation and content-digest
operations fixed by the HFD-04/G77 lineage.  It performs no persistence,
authentication, authority resolution, or runtime orchestration.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from typing import TypeAlias


JsonScalar: TypeAlias = None | bool | int | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class CJ1Error(ValueError):
    """Raised when a value or byte sequence is outside the CJ1 domain."""


def _reject_constant(value: str) -> None:
    raise CJ1Error(f"non-finite numeric token is not CJ1: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CJ1Error(f"duplicate object key is not CJ1: {key!r}")
        result[key] = value
    return result


def _plain(value: object, *, path: str = "$") -> JsonValue:
    if is_dataclass(value) and not isinstance(value, type):
        value = {field.name: getattr(value, field.name) for field in fields(value)}
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise CJ1Error(f"floating-point value is not CJ1 at {path}")
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise CJ1Error(f"string is not NFC at {path}")
        try:
            value.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise CJ1Error(f"string is not valid Unicode at {path}") from exc
        return value
    if isinstance(value, Mapping):
        result: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CJ1Error(f"object key is not a string at {path}")
            canonical_key = _plain(key, path=f"{path}.<key>")
            assert isinstance(canonical_key, str)
            if canonical_key in result:
                raise CJ1Error(f"duplicate object key is not CJ1 at {path}")
            result[canonical_key] = _plain(item, path=f"{path}.{canonical_key}")
        return result
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray, memoryview)
    ):
        return [_plain(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    raise CJ1Error(f"unsupported CJ1 value at {path}: {type(value).__name__}")


def encode(value: object) -> bytes:
    """Return the sole CJ1 UTF-8 byte representation of *value*."""

    plain = _plain(value)
    try:
        text = json.dumps(
            plain,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return text.encode("utf-8", "strict")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise CJ1Error("value cannot be represented as CJ1") from exc


def decode(data: bytes | bytearray | memoryview) -> JsonValue:
    """Parse only already-canonical CJ1 bytes; non-canonical JSON fails closed."""

    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise CJ1Error("CJ1 input must be bytes")
    raw = bytes(data)
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise CJ1Error("CJ1 input is not valid UTF-8") from exc
    if text.startswith("\ufeff"):
        raise CJ1Error("CJ1 input must not contain a BOM")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        if isinstance(exc, CJ1Error):
            raise
        raise CJ1Error("invalid CJ1 input") from exc
    if encode(value) != raw:
        raise CJ1Error("input bytes are valid JSON but not canonical CJ1")
    return value


def sha256_hex(data: bytes | bytearray | memoryview) -> str:
    """Return lowercase SHA-256 hex for explicit bytes."""

    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise CJ1Error("SHA-256 byte input must be bytes")
    return hashlib.sha256(bytes(data)).hexdigest()


def digest(value: object) -> str:
    """Return the constitutional ``sha256:`` digest of ``CJ1(value)``."""

    return f"sha256:{sha256_hex(encode(value))}"


def identity(prefix: str, value: object) -> str:
    """Return a domain-separated content identity for ``CJ1(value)``."""

    if not isinstance(prefix, str) or not prefix or ":" in prefix:
        raise CJ1Error("identity prefix must be a non-empty colon-free string")
    if unicodedata.normalize("NFC", prefix) != prefix:
        raise CJ1Error("identity prefix must be NFC")
    return f"{prefix}:{sha256_hex(encode(value))}"


# Explicit names make call sites state which constitutional operation they use.
cj1_encode = encode
cj1_decode = decode
cj1_digest = digest
cj1_identity = identity


__all__ = [
    "CJ1Error",
    "JsonScalar",
    "JsonValue",
    "cj1_decode",
    "cj1_digest",
    "cj1_encode",
    "cj1_identity",
    "decode",
    "digest",
    "encode",
    "identity",
    "sha256_hex",
]
