#!/usr/bin/env python3
"""Consume the exact existing HM grant after final admission, without execution."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CONTEXT = HM / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = HM / (
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
REQUEST = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
SAFE_STOP = HM / (
    "G77_256HM_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_V1.json"
)
AUTHORITY = HM / "G77_256HM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CHECKPOINT = HM / "G77_256HM_AUTHORITY_VALIDATION_CHECKPOINT_V1.json"

HEAD = "45495c09edf55cc201e3d146ea77e713f579166b"
TREE = "37ba96de335ee91851ff682f8cd97cf4e49ab5f5"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
REQUEST_SHA256 = "fa99566594f5efba7eb1c428a8551e74514f32797ee93343778f39b8a94749b6"
GRANT_SHA256 = "e21c8ea41df3c0bcc37bb5d80b64a8a648ac2725fdab9712ab0086cf097ac4b5"
SAFE_STOP_SHA256 = "9cf6d9d463d7338d3e6122d5c24c12962ad6da9b4967b3052edb92a325d2e949"
PRESENTATION_SHA256 = "d49cbefe23ca8301b5bddd6c9969d4683e568f45329b8cabbf466b4e521fc4f8"
CANDIDATE_SHA256 = "cd64ef475e32f974f52b444442ca4e2d2e57d6ce302f309f58d32dcbdbc7ff67"
CONTEXT_SHA256 = "6813f643bd0108267ca7835c1d37878aa58b34654e6c416423592708e244c7df"
CANONICAL_ARGV_SHA256 = "aff51e5bcc354af7ca1b7db8ac6a4e0cb7870e9912db153f02e0f65dd94cfd49"
CAPACITY_READ_AT_UTC = "2026-09-03T16:14:01Z"
CAPACITY_PRIMARY_USED_PERCENT = 16
CAPACITY_SECONDARY_USED_PERCENT = 71


def load_module(path: Path):
    specification = importlib.util.spec_from_file_location("g77_256hm_fm", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("FM owner import failed")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path) -> dict[str, Any]:
    value, raw = FM.load_json_without_duplicate_keys(path)
    if raw != FM.canonical_bytes(value):
        raise RuntimeError(f"non-canonical JSON: {path}")
    return value


def verify_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    expected = hashlib.sha256(FM.canonical_bytes(envelope[inner])).hexdigest()
    if envelope[f"{inner}_sha256"] != expected:
        raise RuntimeError(f"inner seal mismatch: {path}")
    return envelope


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True
    ).strip()


def main() -> int:
    if AUTHORITY.exists() or CHECKPOINT.exists():
        raise RuntimeError("HM authority consumption artifacts already exist")

    request = verify_envelope(REQUEST, "request")
    safe_stop = verify_envelope(SAFE_STOP, "checkpoint")
    if request["request_sha256"] != REQUEST_SHA256:
        raise RuntimeError("sealed authorization request identity mismatch")
    if safe_stop["checkpoint_sha256"] != SAFE_STOP_SHA256:
        raise RuntimeError("post-grant safe-stop identity mismatch")
    if sha256(GRANT) != GRANT_SHA256 or sha256(PRESENTATION) != PRESENTATION_SHA256:
        raise RuntimeError("grant or GN presentation identity mismatch")

    stopped = safe_stop["checkpoint"]
    grant = stopped["grant_authentication"]
    counters = stopped["operational_counters"]
    if (
        stopped["generation_identity"] != GENERATION
        or stopped["operation_identity"] != OPERATION
        or grant["sealed_authorization_request_sha256"] != REQUEST_SHA256
        or grant["human_grant_source_sha256"] != GRANT_SHA256
        or grant["human_grant_binding_status"] != "VERIFIED"
        or grant["authority_consumed"] is not False
        or counters["human_operational_authority"] != 1
        or any(value != 0 for key, value in counters.items() if key != "human_operational_authority")
    ):
        raise RuntimeError("safe-stop grant or zero-counter state mismatch")

    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    if (
        context["context_sha256"] != CONTEXT_SHA256
        or context["candidate_manifest_sha256"] != CANDIDATE_SHA256
        or context["canonical_argv_sha256"] != CANONICAL_ARGV_SHA256
        or context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or sha256(CANDIDATE) != CANDIDATE_SHA256
    ):
        raise RuntimeError("HM operation material identity mismatch")
    if git("rev-parse", "HEAD") != HEAD or git("rev-parse", "HEAD^{tree}") != TREE:
        raise RuntimeError("committed HM base mismatch")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked worktree drift")
    if git("diff", "--cached", "--name-only"):
        raise RuntimeError("index is not empty")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"],
        cwd=ROOT,
        check=False,
    ).returncode != 0:
        raise RuntimeError("constitutional anchor is not ancestral")

    _, pre_receipt, post_receipt = FM.receipt_namespace_paths(ROOT, context)
    if pre_receipt.exists() or post_receipt.exists():
        raise RuntimeError("receipt namespace already consumed")

    authorization = {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": GRANT_SHA256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "WRONG_INPUT",
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": context["wrapper_fc_er_che_schema_hashes"]["fc_fk_adapter"],
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_input_operational_attempt_limit": 1,
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
    handoff = FM.write_authority_handoff(AUTHORITY, authorization)
    authority, authority_file_sha256 = FM.load_authority(AUTHORITY)
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    admission = FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=authority,
        authority_file_sha256=authority_file_sha256,
        supplied_authority_sha256=authority_file_sha256,
        observed_head=HEAD,
        observed_tree=TREE,
        anchor_is_ancestor=True,
        repository_clean=True,
        observed_asset_sha256=observations,
        argv=context["canonical_argv"],
        canonical_argv_sha256=context["canonical_argv_sha256"],
        receipt_namespace_consumed=False,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    checkpoint = {
        "schema_id": "G77_256HM_AUTHORITY_VALIDATION_CHECKPOINT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "sealed_request_sha256": REQUEST_SHA256,
        "authorization_source_sha256": GRANT_SHA256,
        "gn_presentation_sha256": PRESENTATION_SHA256,
        "postgrant_safe_stop_checkpoint_sha256": SAFE_STOP_SHA256,
        "authorization_file_sha256": authority_file_sha256,
        "authorization_inner_sha256": handoff["authority_inner_sha256"],
        "authority_created_exists": 1,
        "authority_validated": 1,
        "authority_consumed": 1,
        "authority_reusable": False,
        "authority_transferable": False,
        "authority_validation": "PASS",
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "receipt_namespace_unused": "PASS",
        "provider_capacity_at_authority_consumption": {
            "read_at_utc": CAPACITY_READ_AT_UTC,
            "primary_used_percent": CAPACITY_PRIMARY_USED_PERCENT,
            "primary_remaining_percent": 100 - CAPACITY_PRIMARY_USED_PERCENT,
            "primary_window_duration_minutes": 300,
            "secondary_used_percent": CAPACITY_SECONDARY_USED_PERCENT,
            "secondary_remaining_percent": 100 - CAPACITY_SECONDARY_USED_PERCENT,
            "secondary_window_duration_minutes": 10080,
            "rate_limit_reached_type": None,
            "spend_control_reached": False,
            "capacity_reauthentication_status": "VERIFIED",
            "execution_capacity_sufficiency": "VERIFIED",
            "telemetry_source": "CODEX_APP_SERVER_ACCOUNT_RATE_LIMITS_READ",
            "telemetry_is_token_cost_or_billing_evidence": False,
        },
        "operational_counters": {
            "human_operational_authority": 1,
            "authority_consumption": 1,
            "pre": 0,
            "fm_operational_launcher_invocation": 0,
            "qemu": 0,
            "vm_creation": 0,
            "vm_boot": 0,
            "operation_attempt": 0,
            "wrong_input_operation": 0,
            "request": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
            "retry": 0,
            "repair_and_continue": 0,
            "operational_replay": 0,
            "e05_credit": 0,
        },
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    envelope = {
        "schema_id": "G77_256HM_AUTHORITY_VALIDATION_CHECKPOINT_ENVELOPE_V1",
        "checkpoint": checkpoint,
        "checkpoint_sha256": hashlib.sha256(FM.canonical_bytes(checkpoint)).hexdigest(),
    }
    FM.write_atomic(CHECKPOINT, envelope)
    print(json.dumps({
        "result": "HM_EXISTING_AUTHORITY_CONSUMED_AFTER_FINAL_ADMISSION",
        "authority_file_sha256": authority_file_sha256,
        "checkpoint_sha256": envelope["checkpoint_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
