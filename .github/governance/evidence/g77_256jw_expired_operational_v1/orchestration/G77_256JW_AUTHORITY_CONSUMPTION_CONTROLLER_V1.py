#!/usr/bin/env python3
"""Authenticate and consume the exact G77-256JW Human grant once.

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
JW = ROOT / (
    ".github/governance/evidence/"
    "g77_256jw_expired_operational_v1"
)
LIVE = JW / "live_binding"
CONTEXT_PATH = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE_PATH = LIVE / "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
REQUEST_PATH = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION_PATH = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT_PATH = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF_PATH = JW / "G77_256JW_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
SAFE_STOP_PATH = JW / "G77_256JW_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1.json"
CONSUMPTION_PATH = JW / "G77_256JW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
MATERIALIZER_PATH = JW / "orchestration/G77_256JW_PREAUTHORIZATION_MATERIALIZER_V1.py"
PHASE_A_SAFE_STOP_PATH = JW / "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"

HEAD = "98206cab55fb4201c3b60de48eb032cca196de7c"
TREE = "ab1a39d41553fc0296e65287782a36b1f20fb22b"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
GENERATION = "G77_256JW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
REQUEST_SHA256 = "97388bcba3da184e1dda04814cc8041644c58739b996f3accd646438f3597562"
REQUEST_FILE_SHA256 = "11c19016e3c72a58b7d2b5af8323eee2182d10278a7b2d52ef0d01ed6619122d"
PRESENTATION_SHA256 = "1b9438d48e8ae49ca9cea40424038f6a85931933a9b71ef3b33598ace35b403b"
PHASE_A_SAFE_STOP_SHA256 = "28231abf2ace90db790977bddd807c4f8bb9e2fe7340b803801eaf9961bf2eef"
PHASE_A_SAFE_STOP_FILE_SHA256 = "f3b1fc72817bab71d46ae2006305bdfe502bee147b6d2f3988dd90f66e172cef"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
CONTEXT_SHA256 = "7e427b49f46d4327e35fc889141d1c0889c5f2f43a1fbc6e9810c58ef1a670fd"
CONTEXT_FILE_SHA256 = "775898d0f5969837d936778455045aa88e0794b4e7c5a48b5061d279abb67306"
ARGV_SHA256 = "9248e3882d3027c53f85893c42a53a749a0281703408de71b2b3ab458e83eb37"
EXPIRED_ADAPTER_SHA256 = "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
TEMPORAL_BINDING_SHA256 = "20ee02f515ca5fd81f8f932b6361d22d0c10707d0ce16f6516fbff3b7e0b84b9"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"

EXPECTED_NORMALIZED_GRANT = (
    "I explicitly authorize G77-256JW request " + REQUEST_SHA256
    + " and safe-stop checkpoint " + PHASE_A_SAFE_STOP_SHA256
    + " for generation " + GENERATION
    + ", operation " + OPERATION
    + ", candidate " + CANDIDATE_SHA256
    + ", context " + CONTEXT_SHA256
    + ", context file " + CONTEXT_FILE_SHA256
    + ", canonical argv " + ARGV_SHA256
    + ", EXPIRED adapter " + EXPIRED_ADAPTER_SHA256
    + ", temporal binding " + TEMPORAL_BINDING_SHA256
    + ", JR runtime HEAD " + JR_HEAD
    + " and TREE " + JR_TREE
    + ", starting from E05 11/18, subject to exactly one authority consumption, "
      "PRE, FM invocation, no-network QEMU launch, VM operation, and EXPIRED operation "
      "attempt, with zero retry, repair retry, replay, P11 entry, protected invocation, "
      "or protected effect expected; I understand that EXPIRED denial before P11 entry "
      "is an expected result and is not proven until observed.\n"
)


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256jw_authority_fm")
GN = load_module(GN_PATH, "g77_256jw_authority_gn")
MATERIALIZER = load_module(MATERIALIZER_PATH, "g77_256jw_authority_materializer")


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
        "expired_operation": 0,
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
    entry = MATERIALIZER.authenticate_entry(args.remote_head, args.nested_remote_tag)
    MATERIALIZER.authenticate_jv()
    MATERIALIZER.authenticate_jt()
    MATERIALIZER.authenticate_ex()
    if (
        entry["branch"] != BRANCH
        or entry["head"] != HEAD
        or entry["tree"] != TREE
        or args.remote_head != HEAD
        or git("status", "--porcelain", "--untracked-files=no") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise RuntimeError("repository identity drift before authority consumption")
    grant = GRANT_PATH.read_text(encoding="utf-8")
    if grant.replace("\\_", "_") != EXPECTED_NORMALIZED_GRANT:
        raise RuntimeError("Human grant does not exactly match the presented JW request")
    grant_sha256 = sha256_path(GRANT_PATH)
    request = GN.load_validated_sealed_request(REQUEST_PATH)
    if request["request_sha256"] != REQUEST_SHA256 or sha256_path(REQUEST_PATH) != REQUEST_FILE_SHA256:
        raise RuntimeError("sealed authorization request identity drift")
    if sha256_path(PRESENTATION_PATH) != PRESENTATION_SHA256:
        raise RuntimeError("Human presentation identity drift")
    phase_a_safe_stop = json.loads(PHASE_A_SAFE_STOP_PATH.read_bytes())
    if (
        sha256_path(PHASE_A_SAFE_STOP_PATH) != PHASE_A_SAFE_STOP_FILE_SHA256
        or phase_a_safe_stop.get("checkpoint_sha256") != PHASE_A_SAFE_STOP_SHA256
        or phase_a_safe_stop.get("checkpoint", {}).get("request_identity") != REQUEST_SHA256
        or phase_a_safe_stop.get("checkpoint", {}).get("presentation_identity")
        != PRESENTATION_SHA256
    ):
        raise RuntimeError("Phase-A safe-stop correlation drift")
    if sha256_path(CANDIDATE_PATH) != CANDIDATE_SHA256:
        raise RuntimeError("candidate identity drift")
    context = FM.fresh_context.load_context(CONTEXT_PATH, repository_root=ROOT)
    if (
        sha256_path(CONTEXT_PATH) != CONTEXT_FILE_SHA256
        or context["context_sha256"] != CONTEXT_SHA256
        or context["canonical_argv_sha256"] != ARGV_SHA256
        or context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != HEAD
        or context["repository_tree"] != TREE
        or context["guest_adapter_binding"]["source_sha256"] != EXPIRED_ADAPTER_SHA256
        or hashlib.sha256(
            FM.canonical_bytes(context["preclaim_temporal_binding"])
        ).hexdigest() != TEMPORAL_BINDING_SHA256
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"]
        != JR_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"]
        != JR_TREE
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
        "authorized_vector": "EXPIRED",
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": ARGV_SHA256,
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": FM.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "expired_operational_attempt_limit": 1,
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
        "telemetry_source": "NOT_MEASURED__LOCAL_QEMU_OPERATION_DOES_NOT_REQUIRE_PROVIDER_INVOCATION",
        "provider_capability_is_execution_authority": False,
        "execution_capacity_sufficiency": "NOT_APPLICABLE__LOCAL_OPERATION",
    }
    safe_stop = sealed(
        "G77_256JW_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        {
            "schema_id": "G77_256JW_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1",
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
            "phase_a_safe_stop_inner_sha256": PHASE_A_SAFE_STOP_SHA256,
            "e05": "11/18",
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
        "G77_256JW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        {
            "schema_id": "G77_256JW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
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
            "phase_a_safe_stop_inner_sha256": PHASE_A_SAFE_STOP_SHA256,
            "e05": "11/18",
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    persist(CONSUMPTION_PATH, consumption)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
