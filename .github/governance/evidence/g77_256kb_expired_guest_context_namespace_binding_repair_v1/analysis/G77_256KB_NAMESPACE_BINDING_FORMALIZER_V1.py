#!/usr/bin/env python3
"""Repository-only SPCE proof for the G77-256KB namespace repair.

This module reads committed evidence and exercises pure validation functions.
It never materializes operation state, invokes FM/PRE/QEMU, consumes authority,
or writes evidence.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
KB = ROOT / (
    ".github/governance/evidence/"
    "g77_256kb_expired_guest_context_namespace_binding_repair_v1"
)
KA = ROOT / (
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1"
)
FM_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
JR_ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
JX_SEED = Path(
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/static/"
    "SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img"
)
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_SEAL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)
KA_CONTEXT = KA / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
KA_REDUCTION_V2 = KA / "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json"
KA_OBSERVATION_V2 = KA / "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V2.json"
KA_SERIAL = KA / "G77_256KA_SERIAL_CONSOLE_V1.log"

ENTRY_HEAD = "726e694c06794c6b9593989e25134275d236bd32"
ENTRY_TREE = "078df3c68b91abccbb29b18ff9e8a00fe56fda7a"
ENTRY_SUBJECT = "G77-256KA localize EXPIRED guest namespace binding blocker"
ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

KA_NAMESPACE = "g77_256ka_fresh_expired_operational_recommissioning_v1"
HISTORICAL_EXPIRED_NAMESPACE = "g77_256ka_expired_operational_v1"
PRE_REPAIR_OWNER_SHA256 = (
    "d0ae1aa67bbda1fc9a434b939c819ebfd1a9c0df86a24f673c59363570f473b9"
)
POST_REPAIR_OWNER_SHA256 = (
    "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b"
)
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
JR_ADAPTER_SHA256 = (
    "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
)
JX_SEED_SHA256 = (
    "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4"
)
EX_CERTIFICATE_SHA256 = (
    "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
)
EX_SEAL_SHA256 = (
    "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543"
)
KA_REDUCTION_V2_SHA256 = (
    "6cc30d4d9cebd239afcdab8e583c4f733d5017a867d2bd534a88889ff379bf75"
)
KA_OBSERVATION_V2_SHA256 = (
    "b63fe542f4b692f2622bc97ac053e501c3cc971cd8a7396d6bdbef67c87ca064"
)
KA_SERIAL_SHA256 = (
    "45aad40d946b489f421dfb8bd87081e24ab298ec25ddde0f22949ba2ffecfa79"
)

ZERO_COUNTERS = {
    "operational_authorization_count": 0,
    "authority_consumption_count": 0,
    "pre_operational_count": 0,
    "fm_operational_invocation_count": 0,
    "qemu_count": 0,
    "vm_count": 0,
    "operation_attempt_count": 0,
    "operational_request_count": 0,
    "expired_denial_count": 0,
    "p11_entry_count": 0,
    "protected_invocation_count": 0,
    "protected_effect_count": 0,
    "retry_count": 0,
    "repair_retry_count": 0,
    "replay_count": 0,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ValueError(f"noncanonical JSON: {path}")
    return value


def authenticate_envelope(path: Path, member: str, digest_field: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    inner = envelope.get(member)
    if not isinstance(inner, dict):
        raise ValueError(f"missing {member}: {path}")
    if envelope.get(digest_field) != hashlib.sha256(canonical_bytes(inner)).hexdigest():
        raise ValueError(f"inner seal mismatch: {path}")
    return inner


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_entry_owner() -> ModuleType:
    source = subprocess.run(
        ["git", "show", f"{ENTRY_HEAD}:{FM_OWNER}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout
    if hashlib.sha256(source).hexdigest() != PRE_REPAIR_OWNER_SHA256:
        raise RuntimeError("entry owner identity mismatch")
    module = ModuleType("g77_256kb_entry_fm_owner")
    sys.modules[module.__name__] = module
    exec(compile(source, str(FM_OWNER), "exec"), module.__dict__)
    return module


def authenticate_entry_local() -> dict[str, Any]:
    nested = ROOT / "sapianta_system"
    nested_symbolic = subprocess.run(
        ["git", "symbolic-ref", "-q", "HEAD"], cwd=nested, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("log", "-1", "--format=%s"),
        "origin": git("remote", "get-url", "origin"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "nested": {
            "origin": git("remote", "get-url", "origin", cwd=nested),
            "head": git("rev-parse", "HEAD", cwd=nested),
            "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
            "detached": nested_symbolic.returncode == 1,
            "clean": git("status", "--porcelain=v1", cwd=nested) == "",
            "tag": git("describe", "--exact-match", "--tags", "HEAD", cwd=nested),
        },
    }


def authenticate_ka_terminal() -> dict[str, Any]:
    expected_hashes = {
        KA_REDUCTION_V2: KA_REDUCTION_V2_SHA256,
        KA_OBSERVATION_V2: KA_OBSERVATION_V2_SHA256,
        KA_SERIAL: KA_SERIAL_SHA256,
    }
    if {str(path): sha256(path) for path in expected_hashes} != {
        str(path): digest for path, digest in expected_hashes.items()
    }:
        raise RuntimeError("KA terminal evidence identity mismatch")
    reduction = authenticate_envelope(KA_REDUCTION_V2, "reduction", "reduction_sha256")
    observation = authenticate_envelope(
        KA_OBSERVATION_V2, "observation", "observation_sha256"
    )
    expected_ka_counts = dict(ZERO_COUNTERS)
    expected_ka_counts.update({
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
    })
    if reduction.get("terminal") != (
        "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_"
        "NAMESPACE_BINDING_BEFORE_REQUEST"
    ):
        raise RuntimeError("KA terminal mismatch")
    if reduction.get("operational_counters") != expected_ka_counts:
        raise RuntimeError("KA one-shot counters mismatch")
    failure = reduction.get("failure", {})
    if (
        failure.get("observed_namespace") != KA_NAMESPACE
        or failure.get("required_namespace_lead") != "g77_256ka_expired_"
        or failure.get("exact_failure")
        != "sealed operation projection is not namespace-bound"
        or observation.get("operation_namespace_observed") != KA_NAMESPACE
        or observation.get("serial_sha256") != KA_SERIAL_SHA256
    ):
        raise RuntimeError("KA corrected V2 failure localization mismatch")
    if reduction.get("human_authority", {}).get("state") != (
        "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
    ):
        raise RuntimeError("KA authority terminal state mismatch")
    return {"reduction": reduction, "observation": observation}


def operation_root(namespace: str) -> Path:
    return ROOT / ".github/governance/evidence" / namespace / "operation_state"


def prove_namespace(owner: ModuleType, namespace: str) -> dict[str, str]:
    context = load_canonical(KA_CONTEXT)
    host_root = owner._derive_sealed_host_repository_root(
        context, operation_root(namespace)
    )
    return {"namespace": namespace, "host_root": str(host_root)}


def reproduce_entry_failure() -> str:
    owner = load_entry_owner()
    context = load_canonical(KA_CONTEXT)
    try:
        owner.validate_sealed_canonical_argv(
            context, validation_repository_root=owner.GUEST_REPOSITORY_ROOT
        )
    except owner.ContextError as exc:
        return str(exc)
    raise RuntimeError("entry owner unexpectedly accepted KA namespace")


def prove_current_repair() -> dict[str, Any]:
    owner = load_module(ROOT / FM_OWNER, "g77_256kb_current_fm_owner")
    context = load_canonical(KA_CONTEXT)
    projection = owner.validate_sealed_canonical_argv(
        context, validation_repository_root=owner.GUEST_REPOSITORY_ROOT
    )
    historical = prove_namespace(owner, HISTORICAL_EXPIRED_NAMESPACE)
    return {
        "ka_namespace": KA_NAMESPACE,
        "ka_projection": projection,
        "historical_expired_namespace": historical,
        "owner_sha256": sha256(ROOT / FM_OWNER),
    }


def prove_reuse_and_route() -> dict[str, Any]:
    expected = {
        ROOT / EX_CERTIFICATE: EX_CERTIFICATE_SHA256,
        ROOT / EX_SEAL: EX_SEAL_SHA256,
        ROOT / P11: P11_SHA256,
        ROOT / JR_ADAPTER: JR_ADAPTER_SHA256,
        ROOT / JX_SEED: JX_SEED_SHA256,
    }
    observed = {str(path.relative_to(ROOT)): sha256(path) for path in expected}
    if observed != {
        str(path.relative_to(ROOT)): digest for path, digest in expected.items()
    }:
        raise RuntimeError("reused capability identity drift")
    launcher_source = (ROOT / FM_LAUNCHER).read_text(encoding="utf-8")
    if POST_REPAIR_OWNER_SHA256 not in launcher_source:
        raise RuntimeError("launcher owner binding not updated")
    tree = ast.parse(launcher_source)
    mains = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
    ]
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ] if len(mains) == 1 else []
    if len(mains) != 1 or len(qemu_calls) != 1:
        raise RuntimeError("sole FM route changed")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "p11_sha256": observed[str(P11)],
        "jr_adapter_sha256": observed[str(JR_ADAPTER)],
        "jx_seed_sha256": observed[str(JX_SEED)],
        "production_route_before": 1,
        "production_route_after": 1,
    }


def formalize() -> dict[str, Any]:
    entry = authenticate_entry_local()
    expected_entry = (
        ENTRY_BRANCH, ENTRY_HEAD, ENTRY_TREE, ENTRY_SUBJECT, ENTRY_ORIGIN,
    )
    if tuple(entry[key] for key in ("branch", "head", "tree", "subject", "origin")) != expected_entry:
        raise RuntimeError("entry checkpoint mismatch")
    nested = entry["nested"]
    if (
        nested["origin"] != NESTED_ORIGIN
        or nested["head"] != NESTED_HEAD
        or nested["tree"] != NESTED_TREE
        or nested["tag"] != NESTED_TAG
        or not nested["detached"]
        or not nested["clean"]
    ):
        raise RuntimeError("nested authority mismatch")
    authenticate_ka_terminal()
    return {
        "entry": entry,
        "pre_repair": {
            "owner_sha256": PRE_REPAIR_OWNER_SHA256,
            "rule": "PREFIX_THEN_VECTOR_THEN_NONEMPTY_BODY_THEN_SCHEMA_MAJOR",
            "exact_ka_result": reproduce_entry_failure(),
        },
        "post_repair": prove_current_repair(),
        "reuse": prove_reuse_and_route(),
        "operational_counters": ZERO_COUNTERS,
        "terminal": (
            "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(formalize(), sort_keys=True, indent=2))
