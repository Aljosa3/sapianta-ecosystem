#!/usr/bin/env python3
"""Correct the namespace label in KA terminal evidence without replay."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KA = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1"
CONTEXT = KA / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
OBSERVATION_V1 = KA / "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V1.json"
TERMINAL_V1 = KA / "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
OBSERVATION_V2 = KA / "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V2.json"
TERMINAL_V2 = KA / "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json"
OBSERVATION_V1_FILE_SHA256 = "76937bbfe6ccf569bf79e006e2bf04e7b916ffebe76e469d2b715c05ac0ade06"
TERMINAL_V1_FILE_SHA256 = "1efc012aae6653cc300a2edead8f001dd556e9d07b05ac166384e017e8220692"
MARKER = (".github", "governance", "evidence")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    raw = path.read_bytes(); value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical input: {path.name}")
    return value


def validate_envelope(path: Path, key: str) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = load(path); value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"seal mismatch: {path.name}")
    return envelope, value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def write(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"correction collision: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(canonical_bytes(value)); os.fsync(handle.fileno())
    os.replace(temporary, path)


def operation_namespace(context: dict[str, Any]) -> str:
    parts = Path(context["operation_evidence_root"]).parts
    matches = [i for i in range(len(parts) - len(MARKER) + 1) if tuple(parts[i:i + len(MARKER)]) == MARKER]
    if len(matches) != 1:
        raise RuntimeError("operation evidence marker missing or ambiguous")
    suffix = parts[matches[0] + len(MARKER):]
    if len(suffix) != 2 or suffix[1] != "operation_state":
        raise RuntimeError("operation evidence root shape mismatch")
    return suffix[0]


def main() -> None:
    if sha256(OBSERVATION_V1) != OBSERVATION_V1_FILE_SHA256 or sha256(TERMINAL_V1) != TERMINAL_V1_FILE_SHA256:
        raise RuntimeError("superseded V1 evidence identity drift")
    observation_envelope, observation_v1 = validate_envelope(OBSERVATION_V1, "observation")
    terminal_envelope, terminal_v1 = validate_envelope(TERMINAL_V1, "reduction")
    context = load(CONTEXT)
    observed = operation_namespace(context)
    required = f"{context['identity_namespace_prefix'].lower()}_expired_"
    if observed != "g77_256ka_fresh_expired_operational_recommissioning_v1" or observed.startswith(required):
        raise RuntimeError("corrected namespace mismatch not reproduced")
    if observation_v1["operation_namespace_observed"] != "operation_state" or terminal_v1["failure"]["observed_namespace"] != "operation_state":
        raise RuntimeError("expected V1 reporting defect absent")

    correction = {
        "classification": "EVIDENCE_REDUCTION_FIELD_CORRECTION__NO_OPERATIONAL_REPLAY",
        "reason": "V1 used Path(operation_evidence_root).name instead of the repository-evidence suffix namespace evaluated by the guest owner",
        "superseded_observation_file_sha256": OBSERVATION_V1_FILE_SHA256,
        "superseded_observation_inner_sha256": observation_envelope["observation_sha256"],
        "superseded_terminal_file_sha256": TERMINAL_V1_FILE_SHA256,
        "superseded_terminal_inner_sha256": terminal_envelope["reduction_sha256"],
        "authority_action_count": 0, "fm_invocation_count": 0, "qemu_count": 0,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }
    observation_v2 = deepcopy(observation_v1)
    observation_v2["schema_id"] = "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V2"
    observation_v2["operation_namespace_observed"] = observed
    observation_v2["operation_namespace_required_lead"] = required
    observation_v2["correction"] = correction
    write(OBSERVATION_V2, seal("G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_ENVELOPE_V2", "observation", observation_v2))

    terminal_v2 = deepcopy(terminal_v1)
    terminal_v2["schema_id"] = "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2"
    terminal_v2["failure"]["observed_namespace"] = observed
    terminal_v2["failure"]["required_namespace_lead"] = required
    terminal_v2["operation"]["failure_observation_path"] = OBSERVATION_V2.relative_to(ROOT).as_posix()
    terminal_v2["operation"]["failure_observation_file_sha256"] = sha256(OBSERVATION_V2)
    terminal_v2["operation"]["failure_observation_inner_sha256"] = load(OBSERVATION_V2)["observation_sha256"]
    terminal_v2["correction"] = correction
    write(TERMINAL_V2, seal("G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V2", "reduction", terminal_v2))
    print(terminal_v2["terminal"])


if __name__ == "__main__":
    main()
