#!/usr/bin/env python3
"""Future-only binding of both host lifecycle checkpoints to the ER owner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
GV_ROOT = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1"
)
OWNER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/checkpoint/"
    "G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py"
)
OWNER_SHA256 = "74047ee7b3bf219fa70491536d9a5e75eb98d92d06763a17d2783d8882a3ee1e"
SERIAL_SHA256 = "3a5e53d9bc913aae8b17593de7cf0a77043006cc9aedb5261d3fe22d88d0e390"

HISTORICAL_CASES = (
    {
        "identity": "HOST_PRE_TEARDOWN",
        "path": GV_ROOT / "G77_256GV_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json",
        "file_sha256": "ca34f81889dd6502fde039b8e8a67256d7ded92a4a273ee3a02d942a3c498fec",
        "recorded_inner_sha256": "8ead3ad53c1470e33e492e32c4bc21df0edc17f7dabf5f2fe3ddc2a5c0be17da",
        "canonical_inner_sha256": "a0fea946eb22412283af6f1d22574c251ec74ddddc8cf08f82996d5b01f047e9",
    },
    {
        "identity": "HOST_TEARDOWN",
        "path": GV_ROOT / "G77_256GV_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json",
        "file_sha256": "059d21fc6ea9310fc1ceb485cca26d1833b031b7d0f7d02aac92e419196339d6",
        "recorded_inner_sha256": "aaaae6b5fb795548b6793fc20dbf74e40190a9c5da8cb80a2cdd36485a1ddca8",
        "canonical_inner_sha256": "4d03aa48afbe22d84a6db8f37ca2e654eed7c81fda8747d3039f3df7862f094c",
    },
)

SAME_CLASS_PREDECESSORS = (
    REPOSITORY_ROOT / ".github/governance/evidence/g77_256ep_p11_operational_v1/G77_256EP_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json",
    REPOSITORY_ROOT / ".github/governance/evidence/g77_256ep_p11_operational_v1/G77_256EP_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json",
    REPOSITORY_ROOT / ".github/governance/evidence/g77_256fa_consumed_operational_v1/G77_256FA_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json",
    REPOSITORY_ROOT / ".github/governance/evidence/g77_256fa_consumed_operational_v1/G77_256FA_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_owner():
    specification = importlib.util.spec_from_file_location("g77_256gw_er_owner", OWNER_PATH)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load_unique(raw: bytes) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    result = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(result, dict)
    return result


def test_existing_atomic_checkpoint_owner_identity_and_same_class_review() -> None:
    owner = load_owner()
    assert sha256_bytes(OWNER_PATH.read_bytes()) == OWNER_SHA256
    for path in SAME_CLASS_PREDECESSORS:
        result = owner.authenticate_path(path)
        assert result["authentication_result"] == "PASS"
        assert result["sentinel_count"] == 0


@pytest.mark.parametrize("case", HISTORICAL_CASES, ids=lambda case: case["identity"])
def test_historical_gv_exact_single_byte_boundary_cause(case: dict[str, Any]) -> None:
    owner = load_owner()
    raw = case["path"].read_bytes()
    envelope = load_unique(raw)
    payload = envelope["checkpoint"]
    defective_bytes = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    canonical_payload_bytes = owner.canonical_bytes(payload)

    assert set(envelope) == {"schema_id", "checkpoint", "checkpoint_sha256"}
    assert raw == owner.canonical_bytes(envelope)
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert sha256_bytes(raw) == case["file_sha256"]
    assert canonical_payload_bytes == defective_bytes + b"\n"
    assert canonical_payload_bytes[:-1] == defective_bytes
    assert envelope["checkpoint_sha256"] == case["recorded_inner_sha256"]
    assert sha256_bytes(defective_bytes) == case["recorded_inner_sha256"]
    assert sha256_bytes(canonical_payload_bytes) == case["canonical_inner_sha256"]
    assert envelope["checkpoint_sha256"] != sha256_bytes(canonical_payload_bytes)

    with pytest.raises(
        owner.CheckpointError,
        match="checkpoint embedded and computed inner hashes differ",
    ):
        owner.authenticate_bytes(raw)


def future_payload(checkpoint_class: str) -> dict[str, Any]:
    return {
        "auto_continuable": False,
        "checkpoint_class": checkpoint_class,
        "checkpoint_is_authority": False,
        "generation_identity": "G77_256GW_SYNTHETIC_FUTURE_REPOSITORY_ONLY_FIXTURE_V1",
        "host_lifecycle": {
            "persistent_evidence_preserved": True,
            "state": "PRE_TEARDOWN_OBSERVED" if checkpoint_class == "HOST_PRE_TEARDOWN" else "TEARDOWN_COMPLETE",
        },
        "operational_counters": {
            "human_operational_authority_count": 0,
            "p11_entry_count": 0,
            "protected_effect_count": 0,
            "qemu_execution_count": 0,
            "vm_boot_count": 0,
            "vm_creation_count": 0,
        },
        "schema_id": f"G77_256GW_FUTURE_{checkpoint_class}_FIXTURE_V1",
    }


@pytest.mark.parametrize("checkpoint_class", ("HOST_PRE_TEARDOWN", "HOST_TEARDOWN"))
def test_future_host_checkpoint_class_uses_existing_owner(
    tmp_path: Path, checkpoint_class: str
) -> None:
    owner = load_owner()
    payload = future_payload(checkpoint_class)
    payload_path = tmp_path / f"{checkpoint_class}_PAYLOAD.json"
    output_path = tmp_path / f"{checkpoint_class}_CHECKPOINT.json"
    payload_path.write_bytes(owner.canonical_bytes(payload))

    persisted = owner.persist(
        payload_path,
        output_path,
        f"G77_256GW_FUTURE_{checkpoint_class}_ENVELOPE_V1",
    )
    raw = output_path.read_bytes()
    envelope = load_unique(raw)

    assert persisted["authentication_result"] == "PASS"
    assert persisted["independent_reread"] == "PASS"
    assert persisted["durable_atomic_persistence"] == (
        "PASS__FILE_FSYNC__ATOMIC_REPLACE__DIRECTORY_FSYNC"
    )
    assert raw == owner.canonical_bytes(envelope)
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert envelope["checkpoint"] == payload
    assert envelope["checkpoint_sha256"] == sha256_bytes(
        owner.canonical_bytes(payload)
    )
    assert owner.authenticate_path(output_path)["checkpoint_sha256"] == envelope[
        "checkpoint_sha256"
    ]


def test_duplicate_key_and_non_finite_payloads_remain_fail_closed(tmp_path: Path) -> None:
    owner = load_owner()
    cases = (
        (b'{"duplicate":1,"duplicate":2}\n', "duplicate JSON key"),
        (b'{"non_finite":NaN}\n', "non-finite JSON value"),
    )
    for index, (raw, expected) in enumerate(cases):
        payload_path = tmp_path / f"invalid-{index}.json"
        output_path = tmp_path / f"invalid-{index}-output.json"
        payload_path.write_bytes(raw)
        with pytest.raises(owner.CheckpointError, match=expected):
            owner.persist(payload_path, output_path, "G77_256GW_INVALID_FIXTURE_V1")
        assert not output_path.exists()


def test_historical_serial_console_is_byte_identical() -> None:
    serial = GV_ROOT / "G77_256GV_SERIAL_CONSOLE_V1.log"
    assert sha256_bytes(serial.read_bytes()) == SERIAL_SHA256
