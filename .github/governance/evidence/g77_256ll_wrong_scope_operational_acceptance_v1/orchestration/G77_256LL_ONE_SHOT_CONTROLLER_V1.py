#!/usr/bin/env python3
"""Materialize, bind, consume, and invoke G77-256LL exactly once.

This is generation-local evidence orchestration.  It reuses the committed FM
launcher, LG WRONG_SCOPE adapter, canonical Human-authority handoff, ER, and
P11.  ``prepare`` is authority-free.  ``execute`` requires the exact Human
source, creates one handoff, records one consumption, and invokes FM once.
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
LL = ROOT / (
    ".github/governance/evidence/"
    "g77_256ll_wrong_scope_operational_acceptance_v1"
)
LIVE = LL / "live_binding"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
SOURCE = LL / "G77_256LL_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = LL / "G77_256LL_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = LL / "G77_256LL_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PREAUTH = LL / "G77_256LL_PREAUTHORITY_STATIC_READINESS_V1.json"
PRECONSUMPTION = LL / "G77_256LL_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = LL / "G77_256LL_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
ATTEMPT = LL / "G77_256LL_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = LL / "G77_256LL_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
DECISION = ROOT / (
    ".github/governance/evidence/"
    "g77_256lk_wrong_scope_fresh_phase_a_decision_v1/"
    "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_V1.json"
)
CANDIDATE = ROOT / (
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LG_PATH = ROOT / (
    ".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/"
    "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
LK_VERIFIER_PATH = ROOT / (
    ".github/governance/evidence/g77_256lk_wrong_scope_fresh_phase_a_decision_v1/"
    "analysis/G77_256LK_PHASE_A_DECISION_OBJECT_VERIFIER_V1.py"
)

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "584aa26914aa5a4547070bbf91bfedf2250d205c"
ENTRY_TREE = "b0c5083e3da47d23389d148c0f3bb8c776b6cbb0"
ENTRY_SUBJECT = "G77-256LK record terminal Human decision readiness"
LK_IMPLEMENTATION = "13b1979e0265ed105983a29f2983d3a8c6107491"
LJ_TERMINAL = "e3d046cd6ad2f9e4b5e808395d88f56cc03c5a52"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
DECISION_ID = "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
DECISION_FILE_SHA256 = "4e263a945d3ab5bd0e4eab398df232c891347396b3fd4f7c34b83d91bf5a4adc"
DECISION_INNER_SHA256 = "c50473b9089c66363b7a9310e55b382d8e95adebef36c7bf734e6adc39a305fc"
# The sealed LK object owns the canonical operation namespace.  LL is the
# evidence/provenance generation that executes and records that exact object.
GENERATION = "G77_256LK_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LK_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
PREFIX = "G77_256LK"
TRANSIENT = Path("/tmp/g77_256ll_wrong_scope_operational_acceptance_v1")
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256ll_fm")
LG = load_module(LG_PATH, "g77_256ll_lg")
LK = load_module(LK_VERIFIER_PATH, "g77_256ll_lk_verifier")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def seal(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"one-shot namespace collision: {path.name}")
    return FM.write_atomic(path, value)


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", "HEAD") != ENTRY_HEAD
        or git("rev-parse", "HEAD^{tree}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", "HEAD") != ENTRY_SUBJECT
        or remote_head != ENTRY_HEAD
        or not is_ancestor(LJ_TERMINAL, ENTRY_HEAD)
        or not is_ancestor(LK_IMPLEMENTATION, ENTRY_HEAD)
        or git("diff", "--cached", "--name-only")
        or git("status", "--porcelain", "--untracked-files=no")
    ):
        raise RuntimeError("G77_256LL_ENTRY_AUTHENTICATION_CONFLICT")
    prefix = LL.relative_to(ROOT).as_posix() + "/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??" or not line[3:].startswith(prefix):
            raise RuntimeError(f"G77_256LL_UNRELATED_MUTATION:{line}")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
        or nested_remote_tag != NESTED_HEAD
    ):
        raise RuntimeError("G77_256LL_NESTED_AUTHORITY_CONFLICT")


def authenticate_decision() -> dict[str, Any]:
    # LK permits only its own generation-local untracked scope.  At the LL
    # successor, preserve every LK verifier semantic while allowing only the
    # already bounded LL evidence prefix that authenticate_entry checks.
    LK.LK_REL = LL.relative_to(ROOT)
    verified = LK.verify()
    envelope = json.loads(DECISION.read_bytes())
    decision = envelope.get("decision_object")
    if (
        sha256_path(DECISION) != DECISION_FILE_SHA256
        or verified.get("decision_object_sha256") != DECISION_INNER_SHA256
        or envelope.get("decision_object_sha256") != DECISION_INNER_SHA256
        or not isinstance(decision, dict)
        or decision.get("DECISION_OBJECT_ID") != DECISION_ID
        or decision.get("CANONICAL_OPERATION_ID") != OPERATION
        or decision.get("VECTOR") != "WRONG_SCOPE"
        or decision.get("EXPECTED_SCOPE") != EXPECTED_SCOPE
        or decision.get("PRESENTED_SCOPE") != PRESENTED_SCOPE
        or decision.get("AUTHORITY_STATE") != "NONE"
        or decision.get("OPERATION_STATE") != "NOT_STARTED"
        or decision.get("P11_ENTRY_STATE") != "NOT_ENTERED"
        or decision.get("PROTECTED_EFFECT_STATE") != "NONE"
        or decision.get("HUMAN_DECISION_STATE") != "PENDING"
    ):
        raise RuntimeError("G77_256LL_DECISION_OBJECT_AUTHENTICATION_CONFLICT")
    return decision


def context_value() -> dict[str, Any]:
    return FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)


def prepare(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    decision = authenticate_decision()
    if SOURCE.exists() or SOURCE.is_symlink():
        raise RuntimeError("Human authority source must not exist during authority-free preparation")
    if CONTEXT.exists() or CONTEXT.is_symlink() or TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise RuntimeError("G77_256LL authority-free namespace is not fresh")
    LIVE.mkdir(mode=0o700, parents=True, exist_ok=False)
    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=LL / "operation_state",
        transient_root=TRANSIENT,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    FM.write_atomic(CONTEXT, context)
    materialization = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=CONTEXT,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=ENTRY_HEAD,
        observed_tree=ENTRY_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    checkpoint = {
        "schema_id": "G77_256LL_PREAUTHORITY_STATIC_READINESS_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "decision_object_id": DECISION_ID,
        "decision_object_file_sha256": DECISION_FILE_SHA256,
        "decision_object_canonical_inner_sha256": DECISION_INNER_SHA256,
        "decision_state": {
            "authority_state": decision["AUTHORITY_STATE"],
            "operation_state": decision["OPERATION_STATE"],
            "p11_entry_state": decision["P11_ENTRY_STATE"],
            "protected_effect_state": decision["PROTECTED_EFFECT_STATE"],
            "human_decision_state_in_immutable_lk_object": decision["HUMAN_DECISION_STATE"],
        },
        "repository": {"head": ENTRY_HEAD, "tree": ENTRY_TREE, "remote_head": args.remote_head},
        "nested_authority": {"head": NESTED_HEAD, "tree": NESTED_TREE, "tag": NESTED_TAG},
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(CONTEXT),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "materialization": materialization,
        "static_readiness": readiness,
        "human_authority_source_count": 0,
        "authority_creation_count": 0,
        "authority_consumption_count": 0,
        "operation_attempt_count": 0,
        "ready_for_exact_human_decision_binding": True,
    }
    persist(
        PREAUTH,
        seal("G77_256LL_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1", "checkpoint", checkpoint),
    )


def authority(context: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": source_sha256,
        "authorized_context_sha256": context["context_sha256"],
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "WRONG_SCOPE",
        "authorized_repository_head": ENTRY_HEAD,
        "authorized_repository_tree": ENTRY_TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": FM.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_scope_operational_attempt_limit": 1,
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


def counters(*, source: int, created: int, consumed: int, invocation: int) -> dict[str, int]:
    return {
        "human_authority_source_count": source,
        "authority_creation_count": created,
        "authority_consumption_count": consumed,
        "fm_operational_invocation_count": invocation,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "operational_replay_count": 0,
        "repair_retry_count": 0,
    }


def execute(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    decision = authenticate_decision()
    required_absent = (HANDOFF, BINDING, PRECONSUMPTION, CONSUMPTION, ATTEMPT, RESULT)
    if any(path.exists() or path.is_symlink() for path in required_absent):
        raise RuntimeError("G77_256LL one-shot authority or operation namespace already consumed")
    if not SOURCE.is_file() or SOURCE.is_symlink():
        raise RuntimeError("G77_256LL exact Human source absent")
    source_bytes = SOURCE.read_bytes()
    required_source_fragments = (
        b"HUMAN_DECISION = APPROVE_EXACTLY_THIS_SEALED_OBJECT",
        DECISION_ID.encode(),
        OPERATION.encode(),
        DECISION_FILE_SHA256.encode(),
        DECISION_INNER_SHA256.encode(),
        b"AUTHORIZED_VECTOR = WRONG_SCOPE",
        b"AUTHORIZED_OPERATION_ATTEMPT_MAXIMUM = 1",
        b"AUTHORIZED_RETRY_COUNT = 0",
        b"AUTHORIZED_OPERATIONAL_REPLAY_COUNT = 0",
        b"AUTHORIZED_REPAIR_RETRY_COUNT = 0",
        b"This Human decision does NOT authorize:",
    )
    if not all(fragment in source_bytes for fragment in required_source_fragments):
        raise RuntimeError("G77_256LL_HUMAN_DECISION_BINDING_CONFLICT")
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    context = context_value()
    if (
        context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != ENTRY_HEAD
        or context["repository_tree"] != ENTRY_TREE
        or FM.fresh_context.operation_vector(GENERATION) != "WRONG_SCOPE"
    ):
        raise RuntimeError("G77_256LL context binding conflict")
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    specialized = LG.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix=PREFIX
    )
    if (
        model.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_set")
        != [f"authority_scope:{EXPECTED_SCOPE}->{PRESENTED_SCOPE}"]
        or 'authority_differing_fields == ["authority_scope"]' not in specialized
        or 'differing_fields == []' not in specialized
        or 'denial_error == "operational Human act scope is invalid"' not in specialized
    ):
        raise RuntimeError("G77_256LL_MULTIPLE_SEMANTIC_MISMATCHES_DETECTED")
    created = authority(context, source_sha256)
    handoff_result = FM.write_authority_handoff(HANDOFF, created)
    handoff, authority_file_sha256 = FM.load_authority(HANDOFF)
    if authority_file_sha256 != handoff_result["authority_file_sha256"]:
        raise RuntimeError("G77_256LL authority persistence mismatch")
    binding_envelope = FM.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    binding = FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=binding_envelope,
    )
    observed = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    argv = context["canonical_argv"]
    argv_sha256 = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    admission = FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=handoff,
        authority_file_sha256=authority_file_sha256,
        supplied_authority_sha256=authority_file_sha256,
        observed_head=git("rev-parse", "HEAD"),
        observed_tree=git("rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT),
        repository_clean=git("status", "--porcelain", "--untracked-files=no") == "",
        observed_asset_sha256=observed,
        argv=argv,
        canonical_argv_sha256=argv_sha256,
        receipt_namespace_consumed=any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)),
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    persist(BINDING, binding_envelope)
    pre = {
        "schema_id": "G77_256LL_PRECONSUMPTION_READINESS_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "human_decision_present": True,
        "human_decision_exact": True,
        "decision_object_id": DECISION_ID,
        "decision_object_file_sha_match": True,
        "decision_object_inner_sha_match": True,
        "decision_object_file_sha256": DECISION_FILE_SHA256,
        "decision_object_canonical_inner_sha256": DECISION_INNER_SHA256,
        "operation_id_match": decision["CANONICAL_OPERATION_ID"] == OPERATION,
        "vector_match": decision["VECTOR"] == "WRONG_SCOPE",
        "caller_match": True,
        "attempt_match": True,
        "input_match": True,
        "contract_match": True,
        "provenance_match": True,
        "owner_match": True,
        "one_shot_limit": 1,
        "retry_limit": 0,
        "isolated_semantic_mismatch_count": 1,
        "isolated_semantic_mismatch_field": "authority_scope",
        "expected_scope": EXPECTED_SCOPE,
        "presented_scope": PRESENTED_SCOPE,
        "human_source_sha256": source_sha256,
        "authority_handoff_file_sha256": authority_file_sha256,
        "authority_handoff_inner_sha256": handoff["authorization_sha256"],
        "authenticated_canonical_authority_digest": binding["authenticated_canonical_authority_digest"],
        "sealed_invocation_authority_digest": binding["sealed_invocation_authority_digest"],
        "final_fm_argv_authority_digest": binding["final_fm_argv_authority_digest"],
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state": "GRANTED_UNCONSUMED",
        "operational_counters": counters(source=1, created=1, consumed=0, invocation=0),
    }
    pre_file_sha256 = persist(
        PRECONSUMPTION,
        seal("G77_256LL_PRECONSUMPTION_READINESS_CHECKPOINT_ENVELOPE_V1", "checkpoint", pre),
    )
    consumed = {
        "schema_id": "G77_256LL_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "decision_object_id": DECISION_ID,
        "preconsumption_checkpoint_file_sha256": pre_file_sha256,
        "human_source_sha256": source_sha256,
        "authority_handoff_file_sha256": authority_file_sha256,
        "authority_handoff_inner_sha256": handoff["authorization_sha256"],
        "authority_state_before": "GRANTED_UNCONSUMED",
        "authority_state_after": "CONSUMED",
        "authority_reusable": False,
        "authority_transferable": False,
        "final_admission_validation": "PASS",
        "operational_counters": counters(source=1, created=1, consumed=1, invocation=0),
    }
    persist(
        CONSUMPTION,
        seal("G77_256LL_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", consumed),
    )
    attempt = {
        "schema_id": "G77_256LL_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authority_state": "CONSUMED",
        "authority_handoff_file_sha256": authority_file_sha256,
        "invocation_binding_sha256": binding_envelope["invocation_binding_sha256"],
        "invocation_count": 1,
        "retry_count": 0,
        "operational_replay_count": 0,
        "repair_retry_count": 0,
        "operational_counters": counters(source=1, created=1, consumed=1, invocation=1),
    }
    persist(
        ATTEMPT,
        seal("G77_256LL_FM_OPERATIONAL_INVOCATION_ATTEMPT_ENVELOPE_V1", "attempt", attempt),
    )
    command = [
        sys.executable,
        str(FM_PATH),
        "--operation-context", str(CONTEXT),
        "--operation-context-sha256", sha256_path(CONTEXT),
        "--live-candidate-binding", str(CANDIDATE),
        "--execution-authority", str(HANDOFF),
        "--execution-authority-sha256", authority_file_sha256,
    ]
    status = 255
    process_exception: str | None = None
    try:
        status = subprocess.run(command, cwd=ROOT, check=False).returncode
    except BaseException as exc:
        process_exception = f"{type(exc).__name__}:{exc}"
    result = {
        "schema_id": "G77_256LL_FM_OPERATIONAL_INVOCATION_RESULT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authority_state": "CONSUMED",
        "invocation_count": 1,
        "process_exit_status": status,
        "process_exception": process_exception,
        "retry_count": 0,
        "operational_replay_count": 0,
        "repair_retry_count": 0,
    }
    persist(
        RESULT,
        seal("G77_256LL_FM_OPERATIONAL_INVOCATION_RESULT_ENVELOPE_V1", "result", result),
    )
    if process_exception is not None or status != 0:
        raise RuntimeError(
            "G77_256LL_ONE_SHOT_AUTHORITY_CONSUMED__"
            "OPERATIONAL_ACCEPTANCE_NOT_PROVEN__NO_RETRY__STOP"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "execute"))
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.phase == "prepare":
        prepare(arguments)
    else:
        execute(arguments)
