#!/usr/bin/env python3
"""Recover and execute the sole Human-authorized KW Phase-B operation.

The controller is generation-local glue. Canonical Human handoff serialization,
JZ preconsumption binding, final FM admission, and operational execution remain
owned by the existing authenticated FM/GN/JZ implementation chain.
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
KW = ROOT / ".github/governance/evidence/g77_256kw_fresh_expired_operational_recommissioning_v1"
KN_SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
SOURCE = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
REQUEST = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
CONTEXT = KW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = KW / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
HANDOFF = KW / "G77_256KW_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KW / "G77_256KW_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = KW / "G77_256KW_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KW / "G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
BINDER_PATH = KW / "orchestration/G77_256KW_POSTHUMAN_INVOCATION_BINDER_V1.py"

HEAD = "681538ccd9b6faaeebff15d96881134eaef00d7e"
TREE = "53164b7f60d982727bebd9a5c77d5688ee283ade"
SUBJECT = "G77-256KV localize fresh current-head authority lifecycle"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
GENERATION = "G77_256KW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE_SHA256 = "61e497739a6f3ec809af2ecff457233af36207ce7f0587efe1ba694b8332cef2"
CONTEXT_SHA256 = "fc8dee9ba823be2859f13e620bea4599c194b4fab5f072e03391578acf5eef53"
CONTEXT_FILE_SHA256 = "aa29315205a28100c00f940d2aba9575e1b60cacb97b9e5a548cf451674295b2"
ARGV_SHA256 = "11c5070cbccf5ca21bd7d9e42b37667182c389c0a829cef47a0093c314dcc218"
TEMPORAL_SHA256 = "21ec53ad5930000096082e954f7e9fc7619bf31f2de245fe93aa7d8df30538fd"
REQUEST_SHA256 = "cc4022d34d3938e105c40923acbe7916a3cf6b5493c01a44358ec60a0aa7e207"
REQUEST_FILE_SHA256 = "e46520c50999a483f002548ed2ea2fa610e27d39a60e191c71bea8ca0a50c96e"
PRESENTATION_SHA256 = "684f3018aff0da82d1b9878744db9b2485956c603dae54735ee724dbd3ce6aec"
DECISION_PRESENTATION_SHA256 = "769e6eb4ac1ca47a901c252fe13c85ac081c7c3f829dc9608ab54d5d2378c524"
SOURCE_SHA256 = "692b106107c5959e55a727d19a1bb5cfda783b4ac91a4b6d525c1e6fee6a43bd"
KN_SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"

EXPECTED_SOURCE = """I authorize exactly one bounded G77_256KW SPCE Phase-B attempt for:

GENERATION G77_256KW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1
OPERATION G77_256KW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001
CANDIDATE_SHA256 61e497739a6f3ec809af2ecff457233af36207ce7f0587efe1ba694b8332cef2
HUMAN_DECISION_PRESENTATION_SHA256 769e6eb4ac1ca47a901c252fe13c85ac081c7c3f829dc9608ab54d5d2378c524
PURPOSE Perform exactly one fresh Human-authorized EXPIRED operational attempt in the same G77-256KW generation to observe whether EXPIRED is denied before P11 entry after the KF repair.
AUTHORITY_SCOPE ONE_KW_GENERATION__ONE_KW_OPERATION__ONE_AUTHORITY_CONSUMPTION_MAXIMUM__ONE_OPERATIONAL_ATTEMPT_MAXIMUM
NOT_AUTHORIZED NO_REPLAY__NO_REPAIR_RETRY__NO_SECOND_OPERATION__NO_ALTERNATE_AUTHORITY_PATH__NO_P11_BYPASS__NO_PARALLEL_ROUTE__NO_AUTHORITY_TRANSFER__NO_HISTORICAL_AUTHORITY_REUSE__NO_EXPANSION_OF_PRODUCTION_BEHAVIOR
EXPECTED_ROUTE FM_TO_ER_TO_P11
E05_BEFORE_OPERATION VERIFIED__11_OF_18
EXPIRED_BEFORE_OPERATION NOT_PROVEN_OPERATIONALLY

I understand that this file is my direct Human act, authority may be consumed at most once, and EXPIRED denial before P11 entry remains unproven until operationally observed.
"""

PHASE_A_HASHES = {
    "G77_256KW_G48_IMPLEMENTATION_REPORT_V1.md": "e586bf19f670f06dea14a4f1e6e3d7fbe85f01500bf3ffda867b2db9250093f9",
    "G77_256KW_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "0a3b880ef897d21afd1cd6cffe13665359a23cf1a5015e3d4c61788e80bcbca2",
    "G77_256KW_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "52dba0a04d5547100ea420961bd5eb67236efe684e4df28412bec500c6cefec3",
    "G77_256KW_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "284bb2f8a00f9f175380ab305ac202fb42046413a003ebb5a9b837627cba50b2",
    "G77_256KW_HUMAN_DECISION_PRESENTATION_V1.txt": DECISION_PRESENTATION_SHA256,
    "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KW_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": "6691972a5392f79847f87ab6e5665e42458108a79b7b691d4e6c06cb807dd4a8",
    "G77_256KW_KB_NAMESPACE_PREFLIGHT_V1.json": "744ab9e46be8f526071162f6ad76566ca1ddd8d26b9c908e5bb5550ddf903abe",
    "G77_256KW_KD_INTERFACE_PREFLIGHT_V1.json": "3a461493aaee7ce62d36c24bf7e7344d4bb12c1d6772d18ceefb555e690f2893",
    "G77_256KW_KF_PERMISSION_BINDING_PREFLIGHT_V1.json": "974b0a0eb4fd9826b5f970045f518197cd48f6e002164a69eb52d797c1fbf6b6",
    "G77_256KW_KI_FRONTIER_PREFLIGHT_V1.json": "7cb30deaddec4fe0a32917aa8a2e617e3a5f87526baf3f090f51331f5bd839dc",
    "G77_256KW_KM_SCHEMA_BINDING_PREFLIGHT_V1.json": "8e614ec6e9197f0510babaabdd05a3046d22eaf3b0d311c4ecd560a4ce70e53e",
    "G77_256KW_PREAUTHORITY_STATIC_READINESS_V1.json": "aae1ef9ac7d5a2797b7e959c0646e2b4008ba615e24d693db5a46a047522dcac",
    "G77_256KW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "c9254afc0b7b8aa5668ce347f4d6fd2e68583c941b5e7f0120b292a703af8ad3",
    "G77_256KW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": "196fb8b8ce25005f842f1ee4c1366a185a54beaef0c76769467c89589f582b1f",
    "G77_256KW_PREHUMAN_PHASE_A_REDUCTION_V1.json": "8867493539df573cd3bcf00fcfc435e4ba7a1d8c503a81135526958def52ac2a",
    "candidate_source/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/G77_256KW_EXPIRED_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256KW_CONTINUATION_MANIFEST_V1.json": CANDIDATE_SHA256,
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KW_PREAUTHORIZATION_MATERIALIZER_V1.py": "db8b64f59c291a4be12cc660ee2e624c1d50b253446fc0e2c7f07db7a79adca6",
}


class KWRecoveryError(RuntimeError):
    """Stable fail-closed recovery error."""


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise KWRecoveryError(f"authenticated owner unavailable: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256kw_recovery_fm")
GN = load_module(GN_PATH, "g77_256kw_recovery_gn")
BINDER = load_module(BINDER_PATH, "g77_256kw_recovery_binder")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != FM.canonical_bytes(value):
        raise KWRecoveryError(f"NONCANONICAL_JSON:{path.name}")
    return value


def verified_inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(FM.canonical_bytes(value)).hexdigest():
        raise KWRecoveryError(f"SEAL_MISMATCH:{path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(FM.canonical_bytes(value)).hexdigest()}


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise KWRecoveryError(f"ONE_SHOT_ARTIFACT_COLLISION:{path.name}")
    return FM.write_atomic(path, value)


def counters(**changes: int) -> dict[str, int]:
    value = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0,
        "fm_operational_invocation_count": 0,
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
    value.update(changes)
    return value


def authenticate_scope(remote_head: str, nested_remote_tag: str) -> dict[str, str]:
    if (
        git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("log", "-1", "--format=%s") != SUBJECT
        or remote_head != HEAD
        or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise KWRecoveryError("COMMITTED_AUTHORIZATION_BASE_OR_INDEX_MISMATCH")
    allowed_kn = KN_SOURCE.relative_to(ROOT).as_posix()
    kw_prefix = KW.relative_to(ROOT).as_posix() + "/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not line:
            continue
        status, name = line[:2], line[3:]
        if status != "??" or (name != allowed_kn and not name.startswith(kw_prefix)):
            raise KWRecoveryError(f"UNEXPECTED_WORKTREE_MUTATION:{line}")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("branch", "--show-current", cwd=nested)
        or git("status", "--short", cwd=nested)
        or git("describe", "--exact-match", "--tags", cwd=nested) != NESTED_TAG
        or nested_remote_tag != NESTED_HEAD
    ):
        raise KWRecoveryError("NESTED_AUTHORITY_MISMATCH")
    if SOURCE.read_bytes() != EXPECTED_SOURCE.encode("utf-8") or len(SOURCE.read_bytes()) != 1213 or sha256_path(SOURCE) != SOURCE_SHA256:
        raise KWRecoveryError("KW_HUMAN_SOURCE_BYTES_OR_SEMANTICS_MISMATCH")
    if len(KN_SOURCE.read_bytes()) != 1213 or sha256_path(KN_SOURCE) != KN_SOURCE_SHA256:
        raise KWRecoveryError("HISTORICAL_KN_SOURCE_MISMATCH")
    for relative, expected in PHASE_A_HASHES.items():
        if sha256_path(KW / relative) != expected:
            raise KWRecoveryError(f"KW_PHASE_A_IDENTITY_MISMATCH:{relative}")
    reduction = verified_inner(KW / "G77_256KW_PREHUMAN_PHASE_A_REDUCTION_V1.json", "reduction")
    if (
        reduction.get("terminal") != "A__KW_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__NO_HUMAN_AUTHORITY__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
        or reduction.get("authorization_base_head") != HEAD
        or reduction.get("authorization_base_tree") != TREE
        or reduction.get("phase_b_started") is not False
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KWRecoveryError("KW_PHASE_A_TERMINAL_MISMATCH")
    return {"head": HEAD, "tree": TREE, "remote_head": remote_head}


def validate_context() -> dict[str, Any]:
    request = GN.load_validated_sealed_request(REQUEST)
    GN.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    temporal = hashlib.sha256(FM.canonical_bytes(context["preclaim_temporal_binding"])).hexdigest()
    if (
        request["request_sha256"] != REQUEST_SHA256
        or sha256_path(REQUEST) != REQUEST_FILE_SHA256
        or sha256_path(PRESENTATION) != PRESENTATION_SHA256
        or sha256_path(CANDIDATE) != CANDIDATE_SHA256
        or sha256_path(CONTEXT) != CONTEXT_FILE_SHA256
        or context.get("context_sha256") != CONTEXT_SHA256
        or context.get("canonical_argv_sha256") != ARGV_SHA256
        or context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or context.get("repository_head") != HEAD
        or context.get("repository_tree") != TREE
        or temporal != TEMPORAL_SHA256
    ):
        raise KWRecoveryError("KW_CONTEXT_REQUEST_PRESENTATION_CORRELATION_MISMATCH")
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


def validate_final_admission(context: dict[str, Any], authority: dict[str, Any], digest: str) -> dict[str, str]:
    observed_assets = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    argv = context["canonical_argv"]
    argv_sha256 = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    return FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=authority,
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


def prepare(args: argparse.Namespace) -> None:
    authenticate_scope(args.remote_head, args.nested_remote_tag)
    if any(path.exists() or path.is_symlink() for path in (HANDOFF, BINDING, PRECONSUMPTION, CONSUMPTION, INVOCATION, RESULT)):
        raise KWRecoveryError("KW_PHASE_B_NAMESPACE_NOT_FRESH")
    context = validate_context()
    FM.write_authority_handoff(HANDOFF, build_authorization(context))
    authority, digest = FM.load_authority(HANDOFF)
    envelope = BINDER.bind_posthuman_invocation(
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    admission = validate_final_admission(context, authority, digest)
    persist(BINDING, envelope)
    binding = envelope["invocation_binding"]
    checkpoint = {
        "schema_id": "G77_256KW_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "human_source_sha256": SOURCE_SHA256,
        "human_decision_presentation_sha256": DECISION_PRESENTATION_SHA256,
        "canonical_authority_handoff_sha256": digest,
        "canonical_authority_handoff_inner_sha256": authority["authorization_sha256"],
        "authenticated_canonical_authority_digest": binding["authenticated_canonical_authority_digest"],
        "sealed_invocation_authority_digest": binding["sealed_invocation_authority_digest"],
        "final_fm_argv_authority_digest": binding["final_fm_argv_authority_digest"],
        "invocation_binding_sha256": envelope["invocation_binding_sha256"],
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state": "GRANTED_UNCONSUMED",
        "operational_counters": counters(),
        "recovery_branch": "R1",
        "auto_continuable": False,
        "human_review_required": True,
    }
    persist(PRECONSUMPTION, seal("G77_256KW_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_ENVELOPE_V1", "checkpoint", checkpoint))
    print("B__KW_PROVIDER_RECOVERY__AUTHORITY_UNCONSUMED__SAFE_TO_CONTINUE_FROM_AUTHENTICATED_PRECONSUMPTION_EDGE")


def consume_and_operate(args: argparse.Namespace) -> int:
    authenticate_scope(args.remote_head, args.nested_remote_tag)
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, INVOCATION, RESULT)):
        raise KWRecoveryError("KW_AUTHORITY_OR_OPERATION_ALREADY_USED")
    context = validate_context()
    authority, digest = FM.load_authority(HANDOFF)
    envelope = load_canonical(BINDING)
    checkpoint = verified_inner(PRECONSUMPTION, "checkpoint")
    rebuilt = BINDER.bind_posthuman_invocation(
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    if envelope != rebuilt or checkpoint.get("invocation_binding_sha256") != envelope.get("invocation_binding_sha256"):
        raise KWRecoveryError("SEALED_INVOCATION_BINDING_DRIFT")
    binding = FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=envelope,
    )
    digests = {
        digest,
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    }
    if len(digests) != 1:
        raise KWRecoveryError("PRECONSUMPTION_AUTHORITY_DIGEST_EQUALITY_FAILED")
    admission = validate_final_admission(context, authority, digest)
    consumed = {
        "schema_id": "G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "human_source_sha256": SOURCE_SHA256,
        "authority_handoff_file_sha256": digest,
        "authority_handoff_inner_sha256": authority["authorization_sha256"],
        "preconsumption_checkpoint_file_sha256": sha256_path(PRECONSUMPTION),
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state_before": "GRANTED_UNCONSUMED",
        "authority_state_after": "CONSUMED",
        "authority_reusable": False,
        "authority_transferable": False,
        "operational_counters": counters(authority_consumption_count=1),
        "auto_continuable": False,
        "human_review_required": True,
    }
    persist(CONSUMPTION, seal("G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", consumed))
    attempt = {
        "schema_id": "G77_256KW_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "route": "FM_TO_ER_TO_P11",
        "invocation_count": 1,
        "authority_state": "CONSUMED",
        "authority_handoff_file_sha256": digest,
        "final_fm_argv_sha256": binding["final_fm_argv_sha256"],
        "invocation_binding_sha256": envelope["invocation_binding_sha256"],
        "operational_counters": counters(authority_consumption_count=1, pre_operational_invocation_count=1, fm_operational_invocation_count=1, operation_attempt_count=1),
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    persist(INVOCATION, seal("G77_256KW_FM_OPERATIONAL_INVOCATION_ATTEMPT_ENVELOPE_V1", "attempt", attempt))
    completed = subprocess.run(binding["final_fm_argv"], cwd=ROOT, check=False)
    result = {
        "schema_id": "G77_256KW_FM_OPERATIONAL_INVOCATION_RESULT_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "invocation_count": 1,
        "process_exit_status": completed.returncode,
        "authority_state": "CONSUMED",
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    persist(RESULT, seal("G77_256KW_FM_OPERATIONAL_INVOCATION_RESULT_ENVELOPE_V1", "result", result))
    return completed.returncode


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
