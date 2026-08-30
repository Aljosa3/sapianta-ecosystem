#!/usr/bin/env python3
"""Context-aware FM specialization of committed FK-hardened FC semantics."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


FC_SOURCE = Path(
    "/mnt/aigol/.github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_SOURCE_SHA256 = "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
RAW_ROOT = Path("/mnt/g77-evidence")
OPERATION_CONTEXT_PATH = RAW_ROOT / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
SPECIALIZATION_FROM = "G77_256FC"
PREFIX_RE = re.compile(r"^G77_256[A-Z0-9]{2,32}$")
FORBIDDEN_PREFIXES = {
    "G77_256FC", "G77_256FM", "G77_256FW", "G77_256FY",
    "G77_256FZ", "G77_256GA", "G77_256GB", "G77_256GC",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def load_operation_context(path: Path = OPERATION_CONTEXT_PATH) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("fresh operation context absent or unsafe")
    raw = path.read_bytes()

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise RuntimeError("fresh operation context contains duplicate keys")
            value[key] = item
        return value

    try:
        context = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("fresh operation context malformed") from exc
    if not isinstance(context, dict) or raw != canonical_bytes(context):
        raise RuntimeError("fresh operation context is noncanonical")
    seal = context.get("context_sha256")
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    if seal != hashlib.sha256(canonical_bytes(unsealed)).hexdigest():
        raise RuntimeError("fresh operation context seal mismatch")
    prefix = context.get("identity_namespace_prefix")
    if (
        not isinstance(prefix, str)
        or PREFIX_RE.fullmatch(prefix) is None
        or prefix in FORBIDDEN_PREFIXES
    ):
        raise RuntimeError("fresh operation namespace prefix invalid or reused")
    expected_manifest = f"{RAW_ROOT}/{prefix}_CONTINUATION_MANIFEST_V1.json"
    if context.get("guest_context_path") != str(OPERATION_CONTEXT_PATH):
        raise RuntimeError("guest context path binding mismatch")
    runtime_manifest = context.get("runtime_manifest_path")
    if not isinstance(runtime_manifest, str) or Path(runtime_manifest).name != Path(expected_manifest).name:
        raise RuntimeError("runtime continuation manifest is not prefix-derived")
    expected_fixture = f"/run/{prefix.lower().replace('_', '-')}-p11"
    if context.get("guest_fixture_root") != expected_fixture:
        raise RuntimeError("guest fixture root is not prefix-derived")
    return context


def load_specialized_namespace(
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if context is None:
        context = load_operation_context()
    specialization_to = context["identity_namespace_prefix"]
    if sha256_path(FC_SOURCE) != FC_SOURCE_SHA256:
        raise RuntimeError("committed FK-hardened FC adapter identity mismatch")
    source = FC_SOURCE.read_text(encoding="utf-8")
    token_occurrences = re.findall(r"G77_256FC[A-Z0-9_]*", source)
    if len(set(token_occurrences)) != 39 or len(token_occurrences) != 41:
        raise RuntimeError("FC 39-token/41-occurrence identity closure mismatch")
    if source.count(SPECIALIZATION_FROM) < 1 or specialization_to in source:
        raise RuntimeError("FC specialization precondition invalid")
    specialized = source.replace(SPECIALIZATION_FROM, specialization_to)
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_wrong_attempt_specialization_v1",
        "__file__": str(FC_SOURCE),
        "__package__": None,
    }
    exec(compile(specialized, str(FC_SOURCE), "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise RuntimeError("context generation specialization failed")
    if namespace.get("RAW_ROOT") != RAW_ROOT:
        raise RuntimeError("context raw-root specialization failed")
    expected_manifest = RAW_ROOT / f"{specialization_to}_CONTINUATION_MANIFEST_V1.json"
    if namespace.get("CONTINUATION_MANIFEST_PATH") != expected_manifest:
        raise RuntimeError("context continuation-path specialization failed")
    derived = {
        token.replace(SPECIALIZATION_FROM, specialization_to)
        for token in token_occurrences
    }
    if len(derived) != 39 or any(not value.startswith(specialization_to) for value in derived):
        raise RuntimeError("context identity family derivation failed")
    return namespace


def main() -> int:
    namespace = load_specialized_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
