#!/usr/bin/env python3
"""Authenticate and consume the exact G77-256HX Human grant once.

This controller performs no launcher or QEMU invocation. It persists the
canonical FM authority handoff, a GRANTED_UNCONSUMED safe-stop, revalidates
final admission, and atomically records the single authority consumption.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
HX = ROOT / ".github/governance/evidence/g77_256hx_wrong_contract_operational_v1"
LIVE = HX / "live_binding"
CONTEXT_PATH = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE_PATH = LIVE / "candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
REQUEST_PATH = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION_PATH = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT_PATH = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF_PATH = HX / "G77_256HX_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
SAFE_STOP_PATH = HX / "G77_256HX_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1.json"
CONSUMPTION_PATH = HX / "G77_256HX_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
MATERIALIZER_PATH = HX / "orchestration/G77_256HX_PREAUTHORIZATION_MATERIALIZER_V1.py"

HEAD = "0e2448cb0194d6182085a671ddb28729681a1e75"
TREE = "adc1453b964d05e3cf41deffcbbc0c856f99a81a"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
GENERATION = "G77_256HX_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HX_E05_WRONG_CONTRACT_DENIAL_BEFORE_ENTRY_001"
REQUEST_SHA256 = "3bec61cc181da3cdcac98d603249220348f1ceea43f927cb06f5cc6769a8b65f"
CANDIDATE_SHA256 = "d77facc60949333ee2f640c2c41f35f117e034772c3e84fb27e791d1db2accf2"
CONTEXT_SHA256 = "74ea3fcbf10b85277fca3934ee3283ab1ef271c8d503dfda6864eda903ff147b"
ARGV_SHA256 = "e0f8406ee9deec8ca022ea6d6f6720db712331a49445cf2631c9ec80d49f4502"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"

EXPECTED_NORMALIZED_GRANT = (
    "I explicitly authorize G77-256HX request " + REQUEST_SHA256
    + " for operation " + OPERATION
    + ", candidate " + CANDIDATE_SHA256
    + ", context " + CONTEXT_SHA256
    + ", and canonical argv " + ARGV_SHA256
    + ", starting from E05 8/18, subject to exactly one authority consumption, "
      "PRE, FM invocation, no-network QEMU, VM boot, and operation attempt, "
      "with zero retry, repair, replay, or protected effect.\n"
)


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256hx_authority_fm")
GN = load_module(GN_PATH, "g77_256hx_authority_gn")
MATERIALIZER = load_module(MATERIALIZER_PATH, "g77_256hx_authority_materializer")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sealed(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": hashlib.sha256(FM.canonical_bytes(value)).hexdigest(),
    }


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"one-shot authority artifact collision: {path.name}")
    return FM.write_atomic(path, value)


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def counters(human_authority: int, consumption: int) -> dict[str, int]:
    return {
        "human_operational_authority": human_authority,
        "authority_consumption": consumption,
        "pre": 0,
        "fm_operational_launcher_invocation": 0,
        "qemu": 0,
        "vm_creation": 0,
        "vm_boot": 0,
        "operation_attempt": 0,
        "wrong_contract_operation": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "e05_credit": 0,
    }


def main(args: argparse.Namespace) -> None:
    for path in (HANDOFF_PATH, SAFE_STOP_PATH, CONSUMPTION_PATH):
        if path.exists() or path.is_symlink():
            raise RuntimeError("authority namespace is not fresh")
    entry = MATERIALIZER.authenticate_entry(HEAD)
    MATERIALIZER.authenticate_hw()
    if (
        entry["branch"] != BRANCH
        or entry["head"] != HEAD
        or entry["tree"] != TREE
        or git("rev-parse", f"origin/{BRANCH}") != HEAD
        or git("status", "--porcelain", "--untracked-files=no") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise RuntimeError("repository identity drift before authority consumption")
    grant = GRANT_PATH.read_text(encoding="utf-8")
    if grant.replace("\\_", "_") != EXPECTED_NORMALIZED_GRANT:
        raise RuntimeError("Human grant does not exactly match the presented HX request")
    grant_sha256 = sha256_path(GRANT_PATH)
    request = GN.load_validated_sealed_request(REQUEST_PATH)
    if request["request_sha256"] != REQUEST_SHA256:
        raise RuntimeError("sealed authorization request identity drift")
    if sha256_path(CANDIDATE_PATH) != CANDIDATE_SHA256:
        raise RuntimeError("candidate identity drift")
    context = FM.fresh_context.load_context(CONTEXT_PATH, repository_root=ROOT)
    if (
        context["context_sha256"] != CONTEXT_SHA256
        or context["canonical_argv_sha256"] != ARGV_SHA256
        or context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != HEAD
        or context["repository_tree"] != TREE
    ):
        raise RuntimeError("operation context identity drift")
    GN.validate_human_authorization_presentation(REQUEST_PATH, PRESENTATION_PATH.read_bytes())

    authorization = {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": grant_sha256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "WRONG_CONTRACT",
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": ARGV_SHA256,
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": FM.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_contract_operational_attempt_limit": 1,
        "retry_limit": 0,
        "repair_limit": 0,
        "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False,
        "provider_authorized": False,
        "trusted_access_authorized": False,
        "authorization_reusable": False,
        "auto_continuable": False,
    }
    handoff_result = FM.write_authority_handoff(HANDOFF_PATH, authorization)
    handoff, handoff_file_sha256 = FM.load_authority(HANDOFF_PATH)
    if handoff_file_sha256 != handoff_result["authority_file_sha256"]:
        raise RuntimeError("authority handoff persistence mismatch")

    capacity = {
        "telemetry_source": "CODEX_APP_SERVER_ACCOUNT_RATE_LIMITS_READ",
        "read_at_utc": args.capacity_read_at_utc,
        "primary_used_percent": args.primary_used_percent,
        "primary_remaining_percent": 100 - args.primary_used_percent,
        "primary_window_duration_minutes": 300,
        "secondary_used_percent": args.secondary_used_percent,
        "secondary_remaining_percent": 100 - args.secondary_used_percent,
        "secondary_window_duration_minutes": 10080,
        "rate_limit_reached_type": None,
        "spend_control_reached": False,
        "provider_capability_is_execution_authority": False,
        "execution_capacity_sufficiency": "VERIFIED",
    }
    safe_stop = sealed(
        "G77_256HX_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        {
            "schema_id": "G77_256HX_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1",
            "recorded_at_utc": now(),
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "request_sha256": REQUEST_SHA256,
            "grant_source_sha256": grant_sha256,
            "authority_handoff_file_sha256": handoff_file_sha256,
            "authority_handoff_inner_sha256": handoff["authorization_sha256"],
            "authority_state": "GRANTED_UNCONSUMED",
            "authority_consumed": False,
            "provider_capacity": capacity,
            "operational_counters": counters(1, 0),
            "e05": "8/18",
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    safe_stop_file_sha256 = persist(SAFE_STOP_PATH, safe_stop)

    observed_assets = FM.observe_context_assets(ROOT, context, CANDIDATE_PATH.relative_to(ROOT))
    argv = context["canonical_argv"]
    argv_sha256 = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    admission = FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=handoff,
        authority_file_sha256=handoff_file_sha256,
        supplied_authority_sha256=handoff_file_sha256,
        observed_head=git("rev-parse", "HEAD"),
        observed_tree=git("rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT),
        repository_clean=git("status", "--porcelain", "--untracked-files=no") == "",
        observed_asset_sha256=observed_assets,
        argv=argv,
        canonical_argv_sha256=argv_sha256,
        receipt_namespace_consumed=any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)),
        candidate_source_path=CANDIDATE_PATH.relative_to(ROOT),
    )
    consumption = sealed(
        "G77_256HX_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        {
            "schema_id": "G77_256HX_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
            "recorded_at_utc": now(),
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "sealed_request_sha256": REQUEST_SHA256,
            "grant_source_sha256": grant_sha256,
            "authority_handoff_file_sha256": handoff_file_sha256,
            "authority_handoff_inner_sha256": handoff["authorization_sha256"],
            "postgrant_safe_stop_file_sha256": safe_stop_file_sha256,
            "human_grant_binding_status": "VERIFIED",
            "final_admission_validation": "PASS",
            "admission_result": admission["result"],
            "receipt_namespace_unused": admission["receipt_namespace_unused"],
            "authority_state_before": "GRANTED_UNCONSUMED",
            "authority_state_after": "CONSUMED",
            "authority_consumed": 1,
            "authority_reusable": False,
            "authority_transferable": False,
            "provider_capacity_at_consumption": capacity,
            "operational_counters": counters(1, 1),
            "e05": "8/18",
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    persist(CONSUMPTION_PATH, consumption)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-used-percent", required=True, type=int)
    parser.add_argument("--secondary-used-percent", required=True, type=int)
    parser.add_argument("--capacity-read-at-utc", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
