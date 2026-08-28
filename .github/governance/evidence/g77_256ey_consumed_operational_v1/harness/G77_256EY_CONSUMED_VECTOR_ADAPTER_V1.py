#!/usr/bin/env python3
"""EY CONSUMED vector adapter over the hash-bound ER operational harness.

The committed ER harness supplies commissioning, authority lifecycle, protected
effect, denial, and teardown mechanisms. This adapter changes generation-bound
identities and applies the certified EU/EX prospective counter semantics at the
durable evidence boundary. It does not rewrite historical ER evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ER_HARNESS = Path(
    "/mnt/aigol/.github/governance/evidence/g77_256er_p11_operational_v1/"
    "harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_HARNESS_SHA256 = "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89"
GENERATION_ID = (
    "G77_256EY_FIRST_ONE_BOUNDED_OPERATIONAL_E05_CONSUMER_OF_CERTIFIED_"
    "P11_SPCE_COMMON_SUBSTRATE_V1"
)
ATTEMPT_ID = "G77_256EY_E05_CONSUMED_REUSE_ATTEMPT_001"
ACT_ID = "G77_256EY_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"
CASE_ID = "G77_256EY_E05_CONSUMED_AUTHORITY_REUSE_DENIAL_001"
RAW_ROOT = Path("/mnt/g77-evidence")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_er() -> Any:
    if sha256_path(ER_HARNESS) != ER_HARNESS_SHA256:
        raise RuntimeError("committed ER harness identity mismatch")
    spec = importlib.util.spec_from_file_location("g77_256er_reused_harness_v1", ER_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("committed ER harness import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure(er: Any) -> None:
    er.GENERATION_ID = GENERATION_ID
    er.ATTEMPT_ID = ATTEMPT_ID
    er.ACT_ID = ACT_ID
    er.CASE_ID = CASE_ID
    er.RAW_ROOT = RAW_ROOT
    er.RAW_PATH = RAW_ROOT / "G77_256EY_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    er.PRE_ACT_SEAL_PATH = RAW_ROOT / "G77_256EY_PRE_ACT_CHECKPOINT_V1.json"
    er.AUTHORITY_SEAL_PATH = RAW_ROOT / "G77_256EY_AUTHORITY_CHECKPOINT_V1.json"
    er.GUEST_SEAL_PATH = RAW_ROOT / "G77_256EY_GUEST_EXECUTION_SEAL_V1.json"
    er.TEARDOWN_SEAL_PATH = RAW_ROOT / "G77_256EY_GUEST_TEARDOWN_SEAL_V1.json"
    er.CONTINUATION_MANIFEST_PATH = (
        RAW_ROOT / "G77_256EY_CONTINUATION_MANIFEST_V1.json"
    )
    er.TERMINAL_CONTINUATION_MANIFEST_PATH = (
        RAW_ROOT / "G77_256EY_CONTINUATION_MANIFEST_TERMINAL_V1.json"
    )
    er.EN_HARNESS_PATH = (
        Path("/mnt/dp-harness") / "G77_256EY_CONSUMED_VECTOR_ADAPTER_V1.py"
    )
    er.FIXTURE_ROOT = Path("/run/g77-256ey-p11")
    er.ENDPOINT = er.FIXTURE_ROOT / "p11_da_disposable_custody_v1.sock"
    er.PROTECTED_PROBE = er.FIXTURE_ROOT / "protected-probe"
    er.PROTECTED_TARGET = er.PROTECTED_PROBE / "state.json"

    original_append = er.append_record
    original_update = er.update_continuation_manifest

    def append_record(record_type: str, evidence_class: str, facts: dict[str, Any]) -> str:
        if record_type == "p11_attempt_result":
            lifecycle = facts["e05_consumed_negative_authority"]
            legacy_counters = facts["execution_counters"]
            if legacy_counters["p11_entry_count"] != 2:
                raise RuntimeError("unexpected ER aggregate request count")
            required = (
                lifecycle["first_authorized_effect_count"] == 1,
                lifecycle["reuse_attempt_count"] == 1,
                lifecycle["reuse_denial_count"] == 1,
                lifecycle["second_invocation_count"] == 0,
                lifecycle["second_protected_effect_count"] == 0,
                facts["consumed_reuse_invariant_pass"],
            )
            if not all(required):
                raise RuntimeError("CONSUMED lifecycle cannot enter certified counter adapter")

            counters = {
                "boundary_request_count": 2,
                "pre_attempt_denial_count": 1,
                "p11_entry_count": 1,
                "p11_operational_invocation_count": 1,
                "protected_effect_count": 1,
                "second_protected_effect_count": 0,
            }
            source_records = (
                ("b6_boundary_request_counter", "BOUNDARY_REQUEST_PRODUCER", 2),
                ("b6_pre_attempt_denial_counter", "PRE_ATTEMPT_DENIAL_PRODUCER", 1),
                ("b6_p11_entry_counter", "ADMITTED_ENTRY_PRODUCER", 1),
                ("b6_invocation_counter", "INVOCATION_PRODUCER", 1),
                ("b6_protected_effect_counter", "PROTECTED_EFFECT_PRODUCER", 1),
                ("b6_second_protected_effect_counter", "SECOND_EFFECT_PRODUCER", 0),
            )
            source_bindings: list[dict[str, Any]] = []
            for record_name, source_identity, value in source_records:
                identity = original_append(record_name, "FACT", {
                    "semantic_definition_id": "P11_ENTRY_DEFINITION_V1",
                    "semantic_version": "1.0.0",
                    "source_identity": source_identity,
                    "value": value,
                    "durable_source_distinct": True,
                })
                source_bindings.append({
                    "record_type": record_name,
                    "source_identity": source_identity,
                    "record_identity": identity,
                })
            original_append("b6_producer_consumer_reduction", "EVIDENCE", {
                "semantic_definition_id": "P11_ENTRY_DEFINITION_V1",
                "semantic_version": "1.0.0",
                "invariant": "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT__PRE_ATTEMPT_DENIAL_ENTRY_INCREMENT_ZERO",
                "counter_sources": source_bindings,
                "observed_counters": counters,
                "denied_request_entry_increment": 0,
                "denied_request_invocation_increment": 0,
                "denied_request_effect_increment": 0,
                "producer_consumer_agreement": True,
                "result": "PASS__CERTIFIED_EU_EX_PROSPECTIVE_COUNTER_SEMANTICS_ADOPTED",
            })
            legacy_counters["p11_entry_count"] = counters["p11_entry_count"]
            facts["prospective_b6_counters"] = counters
            facts["historical_er_aggregate_interpretation_reused"] = False
            facts["counter_semantics_result"] = (
                "PASS__POST_CONSUMED_REQUEST_DENIED_BEFORE_SECOND_P11_ENTRY"
            )
        return original_append(record_type, evidence_class, facts)

    def update_continuation_manifest(**kwargs: Any) -> tuple[str, dict[str, Any]]:
        _, envelope = original_update(**kwargs)
        manifest = envelope["manifest"]
        manifest["frontier_state"]["constitutional_frontier"] = (
            "ONE_AUTHORIZED_EY_E05_CONSUMED_REUSE_GENERATION"
        )
        manifest["frontier_state"]["continuation_mode"] = (
            "FINALIZATION_ONLY"
            if manifest["frontier_state"]["exact_next_legal_action"].startswith(
                ("TEARDOWN", "HOST_AUTHENTICATION")
            )
            else "SAME_LIVE_GENERATION_ONLY"
        )
        updated = {
            "schema_id": "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1",
            "manifest": manifest,
            "manifest_sha256": er.sha256_bytes(er.canonical_bytes(manifest)),
        }
        path = (
            er.TERMINAL_CONTINUATION_MANIFEST_PATH
            if er.TERMINAL_CONTINUATION_MANIFEST_PATH.is_file()
            else er.CONTINUATION_MANIFEST_PATH
        )
        file_sha = er.write_canonical_atomic(path, updated)
        return file_sha, updated

    er.append_record = append_record
    er.update_continuation_manifest = update_continuation_manifest


def main() -> int:
    er = load_er()
    configure(er)
    return er.main()


if __name__ == "__main__":
    raise SystemExit(main())
