#!/usr/bin/env python3
"""Bind, consume, and invoke the exact G77-256LD operation at most once.

The controller is generation-local evidence orchestration. Canonical authority
serialization, digest derivation, binding validation, final admission, and the
only operational route remain owned by the existing FM implementation.
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
LD = ROOT / (
    ".github/governance/evidence/"
    "g77_256ld_fresh_expired_operational_recommissioning_v1"
)
CONTEXT = LD / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = LD / (
    "live_binding/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
SOURCE = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = LD / "G77_256LD_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = LD / "G77_256LD_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CHECKPOINT = LD / "G77_256LD_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = LD / "G77_256LD_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = LD / "G77_256LD_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = LD / "G77_256LD_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
REQUEST = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
SAFE_STOP = LD / "G77_256LD_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
JZ_READINESS = LD / "G77_256LD_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
BINDER_PATH = LD / "orchestration/G77_256LD_POSTHUMAN_INVOCATION_BINDER_V1.py"
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_PATH = ROOT / (
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)

HEAD = "98d059beaa148746d397d48bad9e898b1f9c2297"
TREE = "d1aadf9da3f66b2699f9b4c32647a2fe65c060cc"
SUBJECT = "G77-256LC reissue EXPIRED bootstrap digest projection"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256LD_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LD_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
REQUEST_SHA256 = "c3a2bfaef3d7e29d14858e1ef4d3b6f07a94593b1cfa5f8bfcca0fdc02d29b03"
REQUEST_FILE_SHA256 = "d3c6f7cf27dda1f0a1e077ea19bccde9a3fe1eff975e4d2eea68e82a3ebc874f"
PRESENTATION_SHA256 = "fd08505db5a92691120c0ee524e7dc0cf28d32cde0e20e264668c4cf92b5e6c1"
DECISION_PRESENTATION_SHA256 = "8e8a930f63773ebe48ca3f1d982d64067f2e5039e9c4d84d5339e46796f35d4f"
SAFE_STOP_FILE_SHA256 = "713774b9dbd5a8fc98c81813c15a09bad6b59da943401b7bf3df5047ccce66cc"
READINESS_FILE_SHA256 = "2b8b5b859f2627951af7d8d265973857d68a9f528834814e7873e8e64440c493"
LC_PREFLIGHT_FILE_SHA256 = "ace68624326ec3ebefb0c27c68af2c10bf48bb137e54759c4513f0f882d73226"
CONTEXT_SHA256 = "5b68f72437d0b9c5bdbe94024f1c6d94a8e2f01364826862b982124651c21812"
CONTEXT_FILE_SHA256 = "913b17462f44c152058bb7418beafa21939083ac093e54a1242d78b73e2ef63a"
CANONICAL_ARGV_SHA256 = "fe9bd31f5935db6caa9142f5bbb57f8f64a42acec8d63c0455a305aa18d36ce4"
TEMPORAL_BINDING_SHA256 = "ba2c01e92ef18994c4ae8266ddae8e9a782a75e6d9e57512fb6235e4f6a2cdea"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
SOURCE_BYTE_COUNT = 1381
SOURCE_SHA256 = "1efca9d2575cd46756e820493e97ec6b737f20f056c9261c672e495279c0db5e"
FM_SHA256 = "c5172208874cca022b638511e57f091eafa01ba3c7387b182cf65d4ee98764d0"
GN_SHA256 = "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3"

PHASE_A_HASHES = {
    "G77_256LD_G48_IMPLEMENTATION_REPORT_V1.md": "d90d28f5a6dd54cbf0f8a6493523b3cb0940a49c16c816926cabdb1cc0f95c99",
    "G77_256LD_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "a76cf7259b9acf01ee556cc474e2d04e7b5804a380c44a1a15491cf5dbb5cd91",
    "G77_256LD_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "254130f80cca6b40d97099a941d60feb5d7b91b073495371d2c5f8761e01aa77",
    "G77_256LD_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "030181aa23b64956fc8a66ba1e5f74a9d68e651e04754d433dd2c39ce383147c",
    "G77_256LD_HUMAN_DECISION_PRESENTATION_V1.txt": DECISION_PRESENTATION_SHA256,
    "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256LD_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": "08fced14ed885691a0e774a71915e8751770a1aae01f61e5176ffcdfbb513fb9",
    "G77_256LD_KB_NAMESPACE_PREFLIGHT_V1.json": "a3446b92a8810a6cca32fb4390185b611352924b4cc2feef753f870daee75cf3",
    "G77_256LD_KD_INTERFACE_PREFLIGHT_V1.json": "827e86aca57ef10ce4d59b95e30c5597157d345b7bb953802da71fec8692e7a5",
    "G77_256LD_KF_PERMISSION_BINDING_PREFLIGHT_V1.json": "543240f4e588f309a7d53f40ffbb6eef1eb72cdfef4208da4523d936d4946aba",
    "G77_256LD_KI_FRONTIER_PREFLIGHT_V1.json": "61512471abe4eed4aa8be04ec4a6838c2d6ce1fe15e453f6810c8b3e9d08a601",
    "G77_256LD_KM_SCHEMA_BINDING_PREFLIGHT_V1.json": "7234fc9db4e52c164f4275f768aff4e5f8ed4ca1acf8068507709b44edb9c279",
    "G77_256LD_LC_MATERIALIZED_PREFLIGHT_V1.json": LC_PREFLIGHT_FILE_SHA256,
    "G77_256LD_PREAUTHORITY_STATIC_READINESS_V1.json": "f703d3270a11ba9ccd3f0d8994d5079a276f6a3ea2464fb3bbfd27feaa80acdf",
    "G77_256LD_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": READINESS_FILE_SHA256,
    "G77_256LD_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
    "G77_256LD_PREHUMAN_PHASE_A_REDUCTION_V1.json": "79a32c1e2b0b9e6aaac4e8ac71a072f5a182c5a94f338ee348e110109a76eeba",
    "analysis/G77_256LD_PHASE_A_SUCCESS_VERIFIER_V1.py": "d1756e9a2bce90e34d606f181f62a662de23d96db46ca8070a69b79175f4766c",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344",
    "operation_state/guest_harness/G77_256LD_EXPIRED_VECTOR_ADAPTER_V1.py": "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256LD_CONTINUATION_MANIFEST_V1.json": CANDIDATE_SHA256,
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256LD_PREAUTHORIZATION_MATERIALIZER_V1.py": "71137eeacf3c0e4b4f30680b441b77dd97cce04320d9ca2f0ff43a82fb8039e7",
    "tests/test_g77_256ld_phase_a_success_v1.py": "766571563a1416319ddf17c1dedb5493fd873e2ac609e0297854c3b0aa6dee7e",
}


def load_module(path: Path, name: str, expected: str | None = None) -> ModuleType:
    if expected is not None and sha256_path(path) != expected:
        raise RuntimeError(f"authenticated owner mismatch: {path}")
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FM = load_module(FM_PATH, "g77_256ld_phase_b_fm", FM_SHA256)
GN = load_module(GN_PATH, "g77_256ld_phase_b_gn", GN_SHA256)
BINDER = load_module(BINDER_PATH, "g77_256ld_phase_b_binder")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical JSON: {path.name}")
    return value


def verify_seal(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"seal mismatch: {path.name}")
    return value


def seal(schema: str, inner: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, inner: value, f"{inner}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"one-shot artifact collision: {path.name}")
    return FM.write_atomic(path, value)


def counters(*, authority: int, consumption: int = 0, pre: int = 0, fm: int = 0) -> dict[str, int]:
    return {
        "operational_authorization_count": authority,
        "authority_consumption_count": consumption,
        "pre_operational_invocation_count": pre,
        "fm_operational_invocation_count": fm,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def authenticate_source() -> None:
    raw = SOURCE.read_bytes()
    required = {
        "GENERATION = G77-256LD",
        f"GENERATION_IDENTITY = {GENERATION}",
        f"OPERATION_IDENTITY = {OPERATION}",
        "VECTOR = EXPIRED",
        "TARGET_ACCEPTANCE_EDGE = EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
        "MAX_AUTHORITY_CONSUMPTION = 1",
        "MAX_OPERATION_ATTEMPT = 1",
        "SECOND_OPERATION = FORBIDDEN",
        "RETRY = FORBIDDEN",
        "REPLAY = FORBIDDEN",
        "REPAIR_RETRY = FORBIDDEN",
        "ALTERNATE_AUTHORITY_PATH = FORBIDDEN",
        "P11_BYPASS = FORBIDDEN",
        "PARALLEL_ROUTE = FORBIDDEN",
        "AUTHORITY_TRANSFER = FORBIDDEN",
        "HISTORICAL_AUTHORITY_REUSE = FORBIDDEN",
        "PRODUCTION_EXPANSION = FORBIDDEN",
    }
    text = raw.decode("utf-8")
    if (
        len(raw) != SOURCE_BYTE_COUNT
        or hashlib.sha256(raw).hexdigest() != SOURCE_SHA256
        or not raw.endswith(b"\n")
        or raw.startswith(b"\xef\xbb\xbf")
        or not required.issubset(set(text.splitlines()))
        or "under the Phase-A decision presentation that I have reviewed" not in text
    ):
        raise RuntimeError("Human source authentication or semantics mismatch")


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    if (
        git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or remote_head != HEAD
        or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise RuntimeError("committed LC entry mismatch")
    if subprocess.run(["git", "merge-base", "--is-ancestor", HEAD, "HEAD"], cwd=ROOT, check=False).returncode:
        raise RuntimeError("stable LC ancestry mismatch")
    prefix = LD.relative_to(ROOT).as_posix() + "/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??" or not line[3:].startswith(prefix):
            raise RuntimeError(f"bounded LD workspace violation: {line}")
    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("branch", "--show-current", cwd=nested)
        or git("status", "--short", cwd=nested)
        or git("describe", "--exact-match", "--tags", "HEAD", cwd=nested) != NESTED_TAG
        or nested_remote_tag != NESTED_HEAD
    ):
        raise RuntimeError("nested authority mismatch")


def authenticate_phase_a() -> None:
    for relative, expected in PHASE_A_HASHES.items():
        if sha256_path(LD / relative) != expected:
            raise RuntimeError(f"durable LD Phase-A identity mismatch: {relative}")
    safe = verify_seal(SAFE_STOP, "checkpoint")
    jz = verify_seal(JZ_READINESS, "proof")
    reduction = verify_seal(LD / "G77_256LD_PREHUMAN_PHASE_A_REDUCTION_V1.json", "reduction")
    if (
        safe.get("terminal") != "A__FRESH_LD_EXPIRED_MATERIALIZED_PREAUTHORIZATION_READY_FOR_HUMAN_DECISION__NO_AUTHORITY__NO_OPERATION__NO_E05_CREDIT"
        or reduction.get("ready_for_human_decision") != "VERIFIED"
        or reduction.get("phase_b_started") is not False
        or any(safe.get("operational_counters", {}).values())
        or any(reduction.get("operational_counters", {}).values())
        or jz.get("authority_consumption_count") != 0
        or jz.get("fm_operational_invocation_count") != 0
        or jz.get("process_started") is not False
    ):
        raise RuntimeError("durable LD Phase-A terminal or zero-counter mismatch")


def validate_context() -> dict[str, Any]:
    request = GN.load_validated_sealed_request(REQUEST)
    GN.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    if (
        request.get("request_sha256") != REQUEST_SHA256
        or sha256_path(REQUEST) != REQUEST_FILE_SHA256
        or sha256_path(PRESENTATION) != PRESENTATION_SHA256
        or sha256_path(CONTEXT) != CONTEXT_FILE_SHA256
        or sha256_path(CANDIDATE) != CANDIDATE_SHA256
        or context.get("context_sha256") != CONTEXT_SHA256
        or context.get("canonical_argv_sha256") != CANONICAL_ARGV_SHA256
        or context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or context.get("repository_head") != HEAD
        or context.get("repository_tree") != TREE
        or context.get("constitutional_anchor_head") != ANCHOR
        or context.get("preclaim_temporal_binding", {}).get("coordinate_unix_ns") != 1000
        or hashlib.sha256(canonical_bytes(context["preclaim_temporal_binding"])).hexdigest() != TEMPORAL_BINDING_SHA256
        or context.get("canonical_argv", []).count("-nic") != 1
        or context["canonical_argv"][context["canonical_argv"].index("-nic") + 1] != "none"
    ):
        raise RuntimeError("Human-bound request or sealed context drift")
    return context


def build_authorization(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": SOURCE_SHA256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "EXPIRED",
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
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


def validate_final_admission(context: dict[str, Any], handoff: dict[str, Any], digest: str) -> dict[str, str]:
    observed_assets = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    argv = context["canonical_argv"]
    argv_sha256 = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    return FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=handoff,
        authority_file_sha256=digest,
        supplied_authority_sha256=digest,
        observed_head=git("rev-parse", "HEAD"),
        observed_tree=git("rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT),
        repository_clean=True,
        observed_asset_sha256=observed_assets,
        argv=argv,
        canonical_argv_sha256=argv_sha256,
        receipt_namespace_consumed=any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)),
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )


def authenticate_all(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    authenticate_entry(remote_head, nested_remote_tag)
    authenticate_source()
    authenticate_phase_a()
    return validate_context()


def prepare(args: argparse.Namespace) -> None:
    context = authenticate_all(args.remote_head, args.nested_remote_tag)
    for path in (HANDOFF, BINDING, CHECKPOINT, CONSUMPTION, INVOCATION, RESULT):
        if path.exists() or path.is_symlink():
            raise RuntimeError(f"Phase-B namespace collision: {path.name}")
    for relative in context.get("guest_output_relative_paths", []):
        if (LD / "operation_state/runtime_export" / relative).exists():
            raise RuntimeError(f"guest output namespace collision: {relative}")
    FM.write_authority_handoff(HANDOFF, build_authorization(context))
    handoff, digest = FM.load_authority(HANDOFF)
    envelope = BINDER.bind_posthuman_invocation(
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    binding = FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=envelope,
    )
    admission = validate_final_admission(context, handoff, digest)
    persist(BINDING, envelope)
    checkpoint = {
        "schema_id": "G77_256LD_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LD",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "vector": "EXPIRED",
        "target_acceptance_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
        "repository": {"head": HEAD, "tree": TREE, "remote_head": args.remote_head},
        "nested_authority": {"head": NESTED_HEAD, "tree": NESTED_TREE, "tag": NESTED_TAG, "remote_tag": args.nested_remote_tag},
        "human_source": {"path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": SOURCE_BYTE_COUNT, "sha256": SOURCE_SHA256},
        "bindings": {
            "request_identity": REQUEST_SHA256,
            "request_file_sha256": REQUEST_FILE_SHA256,
            "context_sha256": CONTEXT_SHA256,
            "context_file_sha256": CONTEXT_FILE_SHA256,
            "canonical_argv_sha256": CANONICAL_ARGV_SHA256,
            "authorization_presentation_sha256": PRESENTATION_SHA256,
            "human_decision_presentation_sha256": DECISION_PRESENTATION_SHA256,
            "readiness_checkpoint_file_sha256": READINESS_FILE_SHA256,
            "safe_stop_checkpoint_file_sha256": SAFE_STOP_FILE_SHA256,
            "lc_materialized_preflight_file_sha256": LC_PREFLIGHT_FILE_SHA256,
            "candidate_sha256": CANDIDATE_SHA256,
            "temporal_binding_sha256": TEMPORAL_BINDING_SHA256,
            "human_authority_handoff_sha256": digest,
            "human_authority_inner_sha256": handoff["authorization_sha256"],
            "authenticated_canonical_authority_digest": binding["authenticated_canonical_authority_digest"],
            "sealed_invocation_authority_digest": binding["sealed_invocation_authority_digest"],
            "final_fm_argv_authority_digest": binding["final_fm_argv_authority_digest"],
            "invocation_binding_sha256": envelope["invocation_binding_sha256"],
            "controller_sha256": sha256_path(Path(__file__)),
            "binder_sha256": sha256_path(BINDER_PATH),
            "fm_sha256": FM_SHA256,
            "gn_sha256": GN_SHA256,
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "NO_KNOWN_STATIC_FAILURE__FRESH_OPERATIONAL_OBSERVATION_ABSENT",
            "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_DENIAL_BEFORE_ATTEMPT_WITH_ZERO_EFFECT",
            "previous_closest_edge": "LD_CURRENT_MATERIALIZED_PREOPERATIONAL_CHAIN_AND_PRESENTATION_READY",
            "semantic_difference": "ONE_FRESH_OPERATIONAL_OBSERVATION_REMAINS_AFTER_AUTHENTICATED_STATIC_READINESS",
            "production_behavior_impact": "NONE_BEFORE_PHASE_B",
            "new_capability_required": "NO",
            "new_proof_required": "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_OBSERVATION",
            "convergence_signal": "KY_KZ_LA_LB_LC_LD_PHASE_A_SEQUENCE_REACHES_HUMAN_AUTHORITY_BOUNDARY",
            "repetition_pressure": "HIGH",
            "verification_amplification_risk": "HIGH_IF_PHASE_A_OR_OPERATIONAL_ATTEMPT_IS_REPEATED_WITHOUT_NEW_EVIDENCE",
            "classification_confidence": "HIGH",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "COMMON_PHASE_A_FM_GN_ER_P11_EX_INFRASTRUCTURE",
            "shared_owner_or_vector_specific": "SHARED_OWNERS__LD_OPERATIONAL_PROOF_VECTOR_SPECIFIC",
            "shared_preoperational_infrastructure": "VERIFIED__YES",
            "shared_authority_mechanism": "VERIFIED__YES__NO_AUTHORITY_TRANSFER",
            "shared_binding_rules": "VERIFIED__COMMON__PER_GENERATION_REVALIDATION_REQUIRED",
            "shared_defect": "VERIFIED__NO",
            "shared_required_delta": "VERIFIED__NO__LD_CONCERNS_EXPIRED_ONLY",
            "affected_vectors": ["EXPIRED"],
            "unaffected_vectors": ["FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "reuse_preconditions": "COMMITTED_LC_IDENTITY__FRESH_LD_COORDINATES__EXACT_VECTOR_BINDING",
            "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR",
            "expected_future_proof_reduction": "STATIC_OWNER_PROOF_REUSABLE__NO_OPERATIONAL_OR_E05_CREDIT_TRANSFER",
        },
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state": "GRANTED_UNCONSUMED",
        "authority_limits": {"maximum_consumption": 1, "maximum_operation_attempt": 1, "retry": 0, "repair_retry": 0, "replay": 0},
        "operational_counters": counters(authority=1),
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
    }
    persist(CHECKPOINT, seal("G77_256LD_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_ENVELOPE_V1", "checkpoint", checkpoint))
    print("A__LD_PHASE_B_PRECONSUMPTION_BINDING_READY__AUTHORITY_UNCONSUMED__NO_OPERATION")


def consume_and_operate(args: argparse.Namespace) -> int:
    context = authenticate_all(args.remote_head, args.nested_remote_tag)
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, INVOCATION, RESULT)):
        raise RuntimeError("LD authority or operation namespace already consumed")
    handoff, digest = FM.load_authority(HANDOFF)
    envelope = load_canonical(BINDING)
    checkpoint = verify_seal(CHECKPOINT, "checkpoint")
    if (
        checkpoint.get("authority_state") != "GRANTED_UNCONSUMED"
        or checkpoint.get("bindings", {}).get("controller_sha256") != sha256_path(Path(__file__))
        or checkpoint.get("bindings", {}).get("binder_sha256") != sha256_path(BINDER_PATH)
        or checkpoint.get("bindings", {}).get("human_authority_handoff_sha256") != digest
        or checkpoint.get("operational_counters") != counters(authority=1)
    ):
        raise RuntimeError("preconsumption checkpoint drift")
    rebuilt = BINDER.bind_posthuman_invocation(
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    if envelope != rebuilt or checkpoint["bindings"]["invocation_binding_sha256"] != envelope["invocation_binding_sha256"]:
        raise RuntimeError("sealed invocation binding drift before consumption")
    binding = FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=envelope,
    )
    if {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
        digest,
    } != {digest}:
        raise RuntimeError("preconsumption authority digest equality failed")
    admission = validate_final_admission(context, handoff, digest)
    consumption = {
        "schema_id": "G77_256LD_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "human_source_sha256": SOURCE_SHA256,
        "authority_handoff_file_sha256": digest,
        "authority_handoff_inner_sha256": handoff["authorization_sha256"],
        "preconsumption_checkpoint_file_sha256": sha256_path(CHECKPOINT),
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state_before": "GRANTED_UNCONSUMED",
        "authority_state_after": "CONSUMED",
        "authority_reusable": False,
        "authority_transferable": False,
        "operational_counters": counters(authority=1, consumption=1),
        "auto_continuable": False,
        "human_review_required": True,
    }
    persist(CONSUMPTION, seal("G77_256LD_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", consumption))
    attempt = {
        "schema_id": "G77_256LD_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "invocation_count": 1,
        "authority_state": "CONSUMED",
        "authority_handoff_file_sha256": digest,
        "final_fm_argv_sha256": binding["final_fm_argv_sha256"],
        "invocation_binding_sha256": envelope["invocation_binding_sha256"],
        "operational_counters": counters(authority=1, consumption=1, pre=1, fm=1),
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    persist(INVOCATION, seal("G77_256LD_FM_OPERATIONAL_INVOCATION_ATTEMPT_ENVELOPE_V1", "attempt", attempt))
    error: str | None = None
    try:
        completed = subprocess.run(binding["final_fm_argv"], cwd=ROOT, check=False)
        returncode = completed.returncode
    except Exception as exception:  # The consumed observation must still be preserved.
        returncode = 127
        error = f"{type(exception).__name__}: {exception}"
    result = {
        "schema_id": "G77_256LD_FM_OPERATIONAL_INVOCATION_RESULT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "invocation_count": 1,
        "process_exit_status": returncode,
        "process_exception": error,
        "authority_state": "CONSUMED",
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    persist(RESULT, seal("G77_256LD_FM_OPERATIONAL_INVOCATION_RESULT_ENVELOPE_V1", "result", result))
    return returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "consume-and-operate"))
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.mode == "prepare":
        prepare(arguments)
    else:
        raise SystemExit(consume_and_operate(arguments))
