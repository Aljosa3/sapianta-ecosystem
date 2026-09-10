#!/usr/bin/env python3
"""Prepare, consume, and invoke the sole sealed G77-256KA operation once."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KA = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1"
CONTEXT = KA / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = KA / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
SOURCE = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KA / "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KA / "G77_256KA_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CHECKPOINT = KA / "G77_256KA_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KA / "G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KA / "G77_256KA_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KA / "G77_256KA_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
REQUEST = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
SAFE_STOP = KA / "G77_256KA_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
JZ_READINESS = KA / "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
MATERIALIZER_PATH = KA / "orchestration/G77_256KA_PREAUTHORIZATION_MATERIALIZER_V1.py"
BINDER_PATH = KA / "orchestration/G77_256KA_POSTHUMAN_INVOCATION_BINDER_V1.py"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"

HEAD = "128bb145969a7b9ccebb8812b24216e00c7db04c"
TREE = "47d09bc1d2ecf0529601ba65085651d01c325a7c"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
SUBJECT = "G77-256JZ verify FM authority digest preconsumption binding"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
GENERATION = "G77_256KA_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KA_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
REQUEST_SHA256 = "88aff310a14eb13e369dbd55c74fc88b14d3764b4465d9b54712e498fd5d8c29"
REQUEST_FILE_SHA256 = "fa0c418d992d49f8bf8d48de39225b8b25e2f1a9632a7385949967c6438ac1b9"
PRESENTATION_SHA256 = "74664d92666a4164255377bb561f33e3ae00842ff85d708437cfafdc0401082b"
SAFE_STOP_SHA256 = "d002b9217bbf6aaf05b9e489b157aae320716b2543ee32fa711ee8d652ca057f"
SAFE_STOP_FILE_SHA256 = "0db96ebea869cdecae25163de1126af617d15bed29079cb487c1b3fbf9922973"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
CONTEXT_SHA256 = "3ac187d98b85a8bb04b2488e7c65391ab7f76a03a78f9dba21c908ca332c2a9c"
CONTEXT_FILE_SHA256 = "abefc8c493516b911ff458700a36cebb81dbd346d126bb809ad2032557169c6a"
ARGV_SHA256 = "9f5645b8ad33a16380d7fa288599b141f672143f79df5172d78b4cb5499e4bfb"
ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
TEMPORAL_SHA256 = "1e5fcd63e705e0a6849447736c57da9247d3a02803e620f3633405c9c486368c"
JZ_READINESS_INNER = "b000a004cba7cccfb2bf0f009782b8e59caf8e83fc3e7f095eb04663e4d1236d"
JZ_READINESS_FILE = "9d36097e86745fa2bd8319053c906397dc9a3dc87727f00bcbacc3f5e65699ff"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"

EXPECTED_GRANT = (
    "I explicitly authorize G77-256KA request " + REQUEST_SHA256
    + " and safe-stop checkpoint " + SAFE_STOP_SHA256
    + " for generation " + GENERATION + ", operation " + OPERATION
    + ", candidate " + CANDIDATE_SHA256 + ", context " + CONTEXT_SHA256
    + ", context file " + CONTEXT_FILE_SHA256 + ", canonical argv " + ARGV_SHA256
    + ", EXPIRED adapter " + ADAPTER_SHA256 + ", temporal binding " + TEMPORAL_SHA256
    + ", JZ preconsumption readiness " + JZ_READINESS_INNER
    + ", JR runtime HEAD " + JR_HEAD + " and TREE " + JR_TREE
    + ", starting from E05 11/18, subject to exactly one authority consumption, PRE, "
      "FM invocation, no-network QEMU launch, VM operation, and EXPIRED operation attempt, "
      "with zero retry, repair retry, replay, P11 entry, protected invocation, or protected "
      "effect expected; I understand that EXPIRED denial before P11 entry is an expected "
      "result and is not proven until observed.\n"
)

PHASE_A_HASHES = {
    "G77_256KA_G48_IMPLEMENTATION_REPORT_V1.md": "2c1e5badbd9c2598d6c66b176eb924e08e27a0a6f0133945239d7a4dc01b1b84",
    "G77_256KA_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "bcd13e548d0e94ce81a92d1027dd1296d8b9f5cde6b11d0314d789adcc0ddeaf",
    "G77_256KA_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "197ee604e5112ffadc3201b19b04a0d98390e72b36e19e4acd3c5f9604943aee",
    "G77_256KA_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "bba1adbf8a72416d78cccb7406f18377f0ae709478d1d1c0579d0c0bc91c7012",
    "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": JZ_READINESS_FILE,
    "G77_256KA_PREAUTHORITY_STATIC_READINESS_V1.json": "0b2c344d795afa0cb64270edcec8ed9c463821f3d6613e80c44c55d1224b4888",
    "G77_256KA_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "b5ea5a64d0076dbd6c7f6c09540521771e523c0ea111e88b14cecff2b2dff1ab",
    "G77_256KA_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
    "G77_256KA_PREHUMAN_PHASE_A_REDUCTION_V1.json": "cad5b01e8d906b4614985b9830f033c171bfd8c7b753fdd5c6dfb9efbae14531",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": ADAPTER_SHA256,
    "operation_state/guest_harness/G77_256KA_EXPIRED_VECTOR_ADAPTER_V1.py": ADAPTER_SHA256,
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "d0ae1aa67bbda1fc9a434b939c819ebfd1a9c0df86a24f673c59363570f473b9",
    "operation_state/runtime_export/G77_256KA_CONTINUATION_MANIFEST_V1.json": CANDIDATE_SHA256,
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KA_POSTHUMAN_INVOCATION_BINDER_V1.py": "458bf3511ab057a7f102e82f0bb13af7f0cdec0c06554b053b58b4aa6ee779d3",
    "orchestration/G77_256KA_PREAUTHORIZATION_MATERIALIZER_V1.py": "55063bb55944cf2a44874667c6d2cde6d18135754afa36071b88899cba718263",
    "tests/test_g77_256ka_preauthorization_barrier_v1.py": "e9f61cb42a8a4e27c7ce3f80bf4f0308a5454e3cad9d8c4f1765b164e6d6fe47",
}


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256ka_phase_b_fm")
GN = load_module(GN_PATH, "g77_256ka_phase_b_gn")
MATERIALIZER = load_module(MATERIALIZER_PATH, "g77_256ka_phase_b_materializer")
BINDER = load_module(BINDER_PATH, "g77_256ka_phase_b_binder")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def seal(schema: str, inner: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, inner: value, f"{inner}_sha256": hashlib.sha256(FM.canonical_bytes(value)).hexdigest()}


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"one-shot artifact collision: {path.name}")
    return FM.write_atomic(path, value)


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != FM.canonical_bytes(value):
        raise RuntimeError(f"noncanonical artifact: {path.name}")
    return value


def verify_seal(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != hashlib.sha256(FM.canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"seal mismatch: {path.name}")
    return value


def authenticate(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    entry = MATERIALIZER.A.authenticate_entry(remote_head, nested_remote_tag)
    MATERIALIZER.authenticate_jz()
    MATERIALIZER.authenticate_e05_frontier()
    if (
        entry["branch"] != BRANCH or entry["head"] != HEAD or entry["tree"] != TREE
        or remote_head != HEAD or git("log", "-1", "--format=%s") != SUBJECT
        or git("remote", "get-url", "origin") != ORIGIN
        or git("status", "--porcelain", "--untracked-files=no") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise RuntimeError("repository identity drift before authority consumption")
    for relative, expected in PHASE_A_HASHES.items():
        if sha256_path(KA / relative) != expected:
            raise RuntimeError(f"KA Phase-A identity mismatch: {relative}")
    safe_stop = verify_seal(SAFE_STOP, "checkpoint")
    readiness = verify_seal(JZ_READINESS, "proof")
    counters = safe_stop.get("operational_counters", {})
    if set(counters.values()) != {0} or safe_stop.get("checkpoint_sha256") is not None:
        raise RuntimeError("Phase-A zero-operation proof mismatch")
    if (
        safe_stop.get("terminal") != "A__FRESH_KA_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
        or safe_stop.get("request_identity") != REQUEST_SHA256
        or safe_stop.get("presentation_identity") != PRESENTATION_SHA256
        or readiness.get("proof_sha256") is not None
    ):
        raise RuntimeError("Phase-A terminal correlation mismatch")
    if verify_seal(JZ_READINESS, "proof") != readiness:
        raise RuntimeError("JZ readiness instability")
    return entry


def build_authorization(source_sha256: str, context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": source_sha256,
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


def validate_context() -> dict[str, Any]:
    request = GN.load_validated_sealed_request(REQUEST)
    GN.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    if (
        request["request_sha256"] != REQUEST_SHA256 or sha256_path(REQUEST) != REQUEST_FILE_SHA256
        or sha256_path(PRESENTATION) != PRESENTATION_SHA256 or sha256_path(SAFE_STOP) != SAFE_STOP_FILE_SHA256
        or sha256_path(CANDIDATE) != CANDIDATE_SHA256 or sha256_path(CONTEXT) != CONTEXT_FILE_SHA256
        or context["context_sha256"] != CONTEXT_SHA256 or context["canonical_argv_sha256"] != ARGV_SHA256
        or context["generation_identity"] != GENERATION or context["operation_identity"] != OPERATION
        or context["repository_head"] != HEAD or context["repository_tree"] != TREE
        or context["guest_adapter_binding"]["source_sha256"] != ADAPTER_SHA256
        or hashlib.sha256(FM.canonical_bytes(context["preclaim_temporal_binding"])).hexdigest() != TEMPORAL_SHA256
        or context["preclaim_temporal_binding"]["coordinate_unix_ns"] != 1000
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] != JR_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] != JR_TREE
    ):
        raise RuntimeError("Human request or operation context correlation drift")
    return context


def validate_final_admission(context: dict[str, Any], handoff: dict[str, Any], digest: str) -> dict[str, Any]:
    observed_assets = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    argv = context["canonical_argv"]
    argv_sha = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    return FM.validate_final_admission(
        repository_root=ROOT, context=context, authority=handoff,
        authority_file_sha256=digest, supplied_authority_sha256=digest,
        observed_head=git("rev-parse", "HEAD"), observed_tree=git("rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT), repository_clean=True,
        observed_asset_sha256=observed_assets, argv=argv, canonical_argv_sha256=argv_sha,
        receipt_namespace_consumed=any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)),
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )


def reseal(envelope: dict[str, Any]) -> dict[str, Any]:
    envelope["invocation_binding_sha256"] = hashlib.sha256(FM.canonical_bytes(envelope["invocation_binding"])).hexdigest()
    return envelope


def negative_binding_tests(envelope: dict[str, Any]) -> list[str]:
    cases = {
        "63_CHARACTER": lambda d: d[:-1], "65_CHARACTER": lambda d: d + "0",
        "WRONG_NIBBLE": lambda d: d[:-1] + ("0" if d[-1] != "0" else "1"),
        "NONHEX": lambda d: d[:-1] + "z", "WHITESPACE": lambda d: " " + d,
        "PREFIX_SUFFIX": lambda d: "sha256:" + d, "WRONG_UNRELATED": lambda d: "f" * 64,
    }
    rejected: list[str] = []
    for name, mutation in cases.items():
        trial = deepcopy(envelope); binding = trial["invocation_binding"]
        replacement = mutation(binding["authenticated_canonical_authority_digest"])
        for field in ("authenticated_canonical_authority_digest", "sealed_invocation_authority_digest", "final_fm_argv_authority_digest"):
            binding[field] = replacement
        argv = binding["final_fm_argv"]; argv[argv.index("--execution-authority-sha256") + 1] = replacement
        binding["final_fm_argv_sha256"] = hashlib.sha256(FM.canonical_bytes(argv)).hexdigest(); reseal(trial)
        try:
            BINDER.FM.validate_preconsumption_invocation_binding(repository_root=ROOT, operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF, envelope=trial)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError(f"negative digest substitution accepted: {name}")
    for name, mutate in (
        ("MISSING_DIGEST", lambda b: b["final_fm_argv"].__delitem__(slice(b["final_fm_argv"].index("--execution-authority-sha256"), b["final_fm_argv"].index("--execution-authority-sha256") + 2))),
        ("HANDOFF_SEAL_MISMATCH", lambda b: b.__setitem__("sealed_invocation_authority_digest", "f" * 64)),
        ("SEAL_ARGV_MISMATCH", lambda b: b["final_fm_argv"].__setitem__(b["final_fm_argv"].index("--execution-authority-sha256") + 1, "f" * 64)),
    ):
        trial = deepcopy(envelope); mutate(trial["invocation_binding"])
        trial["invocation_binding"]["final_fm_argv_sha256"] = hashlib.sha256(FM.canonical_bytes(trial["invocation_binding"]["final_fm_argv"])).hexdigest(); reseal(trial)
        try:
            BINDER.FM.validate_preconsumption_invocation_binding(repository_root=ROOT, operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF, envelope=trial)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError(f"negative binding mismatch accepted: {name}")
    parameters = inspect.signature(BINDER.bind_posthuman_invocation).parameters
    if set(parameters) != {"operation_context", "live_candidate_binding", "execution_authority"}:
        raise RuntimeError("caller/provider digest surface detected")
    for name, keyword in (("CALLER_SUBSTITUTION", "caller_digest"), ("PROVIDER_SUBSTITUTION", "provider_digest"), ("JY_MANUAL_RECONSTRUCTION", "execution_authority_sha256")):
        try:
            BINDER.bind_posthuman_invocation(operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF, **{keyword: "f" * 64})
        except TypeError:
            rejected.append(name)
        else:
            raise RuntimeError(f"forbidden digest input accepted: {name}")
    return rejected


def zero_counters(authority: int = 1, consumption: int = 0, fm: int = 0) -> dict[str, int]:
    return {
        "operational_authorization_count": authority, "authority_consumption_count": consumption,
        "pre_operational_count": 0, "fm_operational_invocation_count": fm, "qemu_count": 0,
        "vm_count": 0, "operation_attempt_count": 0, "operational_request_count": 0,
        "expired_denial_count": 0, "p11_entry_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }


def prepare(args: argparse.Namespace) -> None:
    authenticate(args.remote_head, args.nested_remote_tag)
    for path in (HANDOFF, BINDING, CHECKPOINT, CONSUMPTION, INVOCATION, RESULT):
        if path.exists() or path.is_symlink():
            raise RuntimeError("Phase-B namespace is not fresh")
    if SOURCE.read_text(encoding="utf-8").replace("\\_", "_") != EXPECTED_GRANT:
        raise RuntimeError("Human grant does not exactly match KA authority-bound fields")
    context = validate_context(); source_digest = sha256_path(SOURCE)
    FM.write_authority_handoff(HANDOFF, build_authorization(source_digest, context))
    handoff, handoff_digest = FM.load_authority(HANDOFF)
    envelope = BINDER.bind_posthuman_invocation(operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF)
    rejected = negative_binding_tests(envelope)
    admission = validate_final_admission(context, handoff, handoff_digest)
    persist(BINDING, envelope)
    binding = envelope["invocation_binding"]
    if len(rejected) != 13 or len(set(rejected)) != 13:
        raise RuntimeError("preconsumption negative matrix incomplete")
    checkpoint = seal("G77_256KA_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_ENVELOPE_V1", "checkpoint", {
        "schema_id": "G77_256KA_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1", "recorded_at_utc": now(),
        "generation_identity": GENERATION, "operation_identity": OPERATION, "repository_head": HEAD,
        "repository_tree": TREE, "request_identity": REQUEST_SHA256, "safe_stop_checkpoint": SAFE_STOP_SHA256,
        "human_source_sha256": source_digest, "canonical_authority_handoff_sha256": handoff_digest,
        "canonical_authority_handoff_inner_sha256": handoff["authorization_sha256"],
        "authenticated_canonical_authority_digest": binding["authenticated_canonical_authority_digest"],
        "sealed_invocation_authority_digest": binding["sealed_invocation_authority_digest"],
        "final_fm_argv_authority_digest": binding["final_fm_argv_authority_digest"],
        "final_fm_argv_sha256": binding["final_fm_argv_sha256"], "invocation_binding_sha256": envelope["invocation_binding_sha256"],
        "candidate_sha256": CANDIDATE_SHA256, "context_sha256": CONTEXT_SHA256,
        "context_file_sha256": CONTEXT_FILE_SHA256, "canonical_argv_sha256": ARGV_SHA256,
        "temporal_binding_sha256": TEMPORAL_SHA256, "preclaim_coordinate_unix_ns": 1000,
        "jz_readiness_inner_sha256": JZ_READINESS_INNER, "stable_runtime_head": JR_HEAD, "stable_runtime_tree": JR_TREE,
        "caller_digest_input_count": 0, "provider_digest_input_count": 0,
        "negative_binding_rejections": rejected, "negative_binding_rejection_count": len(rejected),
        "final_admission_validation": "PASS", "admission_result": admission["result"],
        "operational_counters": zero_counters(), "authority_state": "GRANTED_UNCONSUMED",
        "binding_is_authority": False, "auto_continuable": False, "human_review_required": True,
    })
    persist(CHECKPOINT, checkpoint)
    print("A__KA_PHASE_B_PRECONSUMPTION_BINDING_READY__AUTHORITY_UNCONSUMED")


def consume_and_operate(args: argparse.Namespace) -> int:
    authenticate(args.remote_head, args.nested_remote_tag)
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, INVOCATION, RESULT)):
        raise RuntimeError("KA authority or operation namespace already consumed")
    if SOURCE.read_text(encoding="utf-8").replace("\\_", "_") != EXPECTED_GRANT:
        raise RuntimeError("Human grant drift before consumption")
    context = validate_context(); handoff, digest = FM.load_authority(HANDOFF)
    envelope = load_canonical(BINDING); checkpoint = verify_seal(CHECKPOINT, "checkpoint")
    rebuilt = BINDER.bind_posthuman_invocation(operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF)
    if envelope != rebuilt or checkpoint["invocation_binding_sha256"] != envelope["invocation_binding_sha256"]:
        raise RuntimeError("sealed invocation binding drift before consumption")
    binding = BINDER.FM.validate_preconsumption_invocation_binding(repository_root=ROOT, operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF, envelope=envelope)
    if {binding["authenticated_canonical_authority_digest"], binding["sealed_invocation_authority_digest"], binding["final_fm_argv_authority_digest"], digest} != {digest}:
        raise RuntimeError("preconsumption authority digest equality failed")
    admission = validate_final_admission(context, handoff, digest)
    consumption = seal("G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", {
        "schema_id": "G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1", "recorded_at_utc": now(),
        "generation_identity": GENERATION, "operation_identity": OPERATION, "human_source_sha256": sha256_path(SOURCE),
        "authority_handoff_file_sha256": digest, "authority_handoff_inner_sha256": handoff["authorization_sha256"],
        "preconsumption_checkpoint_file_sha256": sha256_path(CHECKPOINT), "preconsumption_checkpoint_inner_sha256": hashlib.sha256(FM.canonical_bytes(checkpoint)).hexdigest(),
        "final_admission_validation": "PASS", "admission_result": admission["result"],
        "authority_state_before": "GRANTED_UNCONSUMED", "authority_state_after": "CONSUMED",
        "authority_reusable": False, "authority_transferable": False, "operational_counters": zero_counters(consumption=1),
        "auto_continuable": False, "human_review_required": True,
    })
    persist(CONSUMPTION, consumption)
    argv = binding["final_fm_argv"]
    invocation = seal("G77_256KA_FM_OPERATIONAL_INVOCATION_ATTEMPT_ENVELOPE_V1", "attempt", {
        "schema_id": "G77_256KA_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1", "recorded_at_utc": now(),
        "generation_identity": GENERATION, "operation_identity": OPERATION, "invocation_count": 1,
        "authority_state": "CONSUMED", "authority_handoff_file_sha256": digest,
        "final_fm_argv_sha256": binding["final_fm_argv_sha256"], "invocation_binding_sha256": envelope["invocation_binding_sha256"],
        "operational_counters": zero_counters(consumption=1, fm=1), "retry_count": 0, "replay_count": 0,
    })
    persist(INVOCATION, invocation)
    completed = subprocess.run(argv, cwd=ROOT, check=False)
    result = seal("G77_256KA_FM_OPERATIONAL_INVOCATION_RESULT_ENVELOPE_V1", "result", {
        "schema_id": "G77_256KA_FM_OPERATIONAL_INVOCATION_RESULT_V1", "recorded_at_utc": now(),
        "generation_identity": GENERATION, "operation_identity": OPERATION, "invocation_count": 1,
        "process_exit_status": completed.returncode, "authority_state": "CONSUMED", "retry_count": 0,
        "repair_retry_count": 0, "replay_count": 0,
    })
    persist(RESULT, result)
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
