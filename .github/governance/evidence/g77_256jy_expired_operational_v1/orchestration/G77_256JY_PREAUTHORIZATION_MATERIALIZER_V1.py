#!/usr/bin/env python3
"""Materialize one nonauthority G77-256JY EXPIRED Phase-A package.

The generation reuses the authenticated JW acyclic preauthorization
construction, substitutes only JY-local identity and the committed JX entry,
and replaces the historical JT reconstruction with an exact JX repair
authentication.  No authority-consumption or operational-launch path exists
in this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "939d7eda8ff333b6cf0dfbd54d274aabefcba698"
TREE = "bce9f2863a7314a1e5e088066efeea52615d989d"
SUBJECT = "G77-256JX verify ER admission runtime checkout role separation"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
JX_TERMINAL = (
    "A__ER_DISTINCT_ADMISSION_AND_RUNTIME_CHECKOUT_ROLE_VALIDATION_"
    "REPOSITORY_VERIFIED"
)

BASE = Path(
    ".github/governance/evidence/g77_256jw_expired_operational_v1/"
    "orchestration/G77_256JW_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
BASE_SHA256 = "27016ddd429f231d6ec3c1dfe0222188a72eb85fbf57e6201d6ede58d35153ec"
JX_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1"
)
JX_REDUCTION = JX_ROOT / "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JX_REPORT = JX_ROOT / "G77_256JX_G48_IMPLEMENTATION_REPORT_V1.md"
JX_FORMALIZER = JX_ROOT / "analysis/G77_256JX_ER_ROLE_SEPARATION_FORMALIZER_V1.py"
JX_TEST = JX_ROOT / "tests/test_g77_256jx_er_role_separation_v1.py"
JX_CLOUD = JX_ROOT / "static/G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
JX_SEED = JX_ROOT / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img"
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")

JX_HASHES = {
    JX_REDUCTION: "db9309de5e3940d7547d887c869f080057cb96ca93200e77f73431d091731a59",
    JX_REPORT: "b34da3185fee567375e73bb5ee0fdb7efbc6d7e23fd2e49fc2316de8e425f25d",
    JX_FORMALIZER: "dfa04c8df095d472b210e6925e3a99ca45cce7cfbaea84dc39cdbdfe2398f4b6",
    JX_TEST: "4c4d74cdbca1ba8be1e4af11011eca2eaad7d85a2a29b7a112c7e52b511cca36",
    JX_CLOUD: "d427ea791a6a34412af12f6fb4b8f6d6597db120d037bd13e99c9cb64f52f859",
    JX_SEED: "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4",
    FM_PATH: "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469",
    ADAPTER: "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    P11: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}


class JYBarrierError(RuntimeError):
    """One deterministic fail-closed JY Phase-A error."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def load_base() -> ModuleType:
    path = ROOT / BASE
    source_bytes = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{BASE}"], cwd=ROOT)
    if source_bytes != committed or sha256_bytes(source_bytes) != BASE_SHA256:
        raise JYBarrierError("COMMITTED_JW_PREAUTHORIZATION_OWNER_MISMATCH")
    source = source_bytes.decode("utf-8")
    source = source.replace("JW", "JY")
    source = source.replace("jw", "jy")
    source = source.replace("authenticate_jt", "authenticate_jx")
    source = source.replace("jt = authenticate_jx()", "jx = authenticate_jx()")
    source = source.replace('"jt_reconstruction": jt', '"jx_reconstruction": jx')
    source = source.replace(
        '"jt_terminal_reconstruction": jt', '"jx_terminal_reconstruction": jx'
    )
    module = ModuleType("g77_256jy_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.HEAD = HEAD
    module.TREE = TREE
    module.SUBJECT = SUBJECT
    module.ANCHOR = HEAD
    module.JT_SEED = JX_SEED
    return module


M = load_base()


def authenticate_jx() -> dict[str, Any]:
    identities: dict[str, str] = {}
    for path, expected in JX_HASHES.items():
        current = (ROOT / path).read_bytes()
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{path}"], cwd=ROOT)
        if current != committed or sha256_bytes(current) != expected:
            raise JYBarrierError(f"COMMITTED_JX_DEPENDENCY_MISMATCH:{path}")
        identities[path.as_posix()] = expected

    envelope = M.load_canonical(ROOT / JX_REDUCTION)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(M.canonical_bytes(reduction))
    ):
        raise JYBarrierError("JX_TERMINAL_REDUCTION_SEAL_MISMATCH")
    role = reduction.get("role_separation", {})
    architecture = reduction.get("architecture", {})
    required_role_results = {
        "admission_repository_owner": "EXISTING_FM_FINAL_ADMISSION_AND_CONTEXT_SEAL_OWNER",
        "runtime_checkout_owner": "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER",
        "distinct_valid_roles_accepted": "VERIFIED__REPOSITORY_ONLY",
        "admission_corruption": "VERIFIED__HOST_ADMISSION_FAIL_CLOSED",
        "runtime_corruption": "VERIFIED__ER_AND_FM_FAIL_CLOSED",
        "unsealed_substitution": "VERIFIED__CONTEXT_SEAL_FAIL_CLOSED",
        "caller_provider_substitution": "VERIFIED__HOST_ADMISSION_AND_IMMUTABLE_BINDING_FAIL_CLOSED",
        "role_swap": "VERIFIED__FAIL_CLOSED",
        "missing_binding": "VERIFIED__FAIL_CLOSED",
        "stable_jr_checkout": "VERIFIED__PRESERVED",
    }
    if (
        reduction.get("terminal") != JX_TERMINAL
        or any(role.get(key) != value for key, value in required_role_results.items())
        or role.get("runtime_checkout") != {"head": JR_HEAD, "tree": JR_TREE}
        or role.get("route_count") != 1
        or reduction.get("implementation", {}).get("adapter_after_sha256")
        != JX_HASHES[ADAPTER]
        or reduction.get("implementation", {}).get("fm_after_sha256")
        != JX_HASHES[FM_PATH]
        or reduction.get("implementation", {}).get("cloud_sha256")
        != JX_HASHES[JX_CLOUD]
        or reduction.get("implementation", {}).get("seed_sha256")
        != JX_HASHES[JX_SEED]
        or architecture.get("p11_implementation_mutation_count") != "VERIFIED__0"
        or architecture.get("new_owner_count") != "VERIFIED__0"
        or architecture.get("new_route_count") != "VERIFIED__0"
        or architecture.get("production_route_before") != "VERIFIED__1"
        or architecture.get("production_route_after") != "VERIFIED__1"
        or architecture.get("production_route_delta") != "VERIFIED__0"
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
    ):
        raise JYBarrierError("JX_REPAIR_CONTRACT_MISMATCH")

    if M.FM.governed_checkout_identity(ROOT, "EXPIRED", HEAD, TREE) != (
        JR_HEAD,
        JR_TREE,
    ):
        raise JYBarrierError("JX_STABLE_RUNTIME_CHECKOUT_MISMATCH")
    adapter = M.load_module(ADAPTER, "g77_256jy_expired_adapter_authenticated")
    er = adapter.specialize_er_harness(ROOT)
    constants = set(er.load_authenticated_fresh_operation_context.__code__.co_consts)
    if "repository_head" in constants or "repository_tree" in constants:
        raise JYBarrierError("JX_ER_ADMISSION_RUNTIME_ROLE_COLLAPSE_RECURRED")
    if not {"head", "tree"}.issubset(constants):
        raise JYBarrierError("JX_ER_RUNTIME_OBSERVATION_BINDING_MISSING")
    return {
        "terminal": JX_TERMINAL,
        "artifact_hashes": identities,
        "role_separation": required_role_results,
        "stable_checkout": {"head": JR_HEAD, "tree": JR_TREE},
        "p11_implementation_sha256": JX_HASHES[P11],
        "production_route": "VERIFIED__1_TO_1",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


M.authenticate_jx = authenticate_jx
authenticate_entry = M.authenticate_entry
authenticate_jv = M.authenticate_jv
authenticate_ex = M.authenticate_ex


def finalize_jx_continuation_label() -> None:
    """Bind the reused Phase-A reduction to the actual JX predecessor."""

    path = M.JY / "G77_256JY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
    envelope = M.load_canonical(path)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(M.canonical_bytes(reduction))
    ):
        raise JYBarrierError("JY_PHASE_A_REDUCTION_SEAL_MISMATCH")
    dashboard = reduction.get("governance_dashboard", {})
    observed = dashboard.get("constitutional_continuation_progress")
    if observed not in {
        "VERIFIED__JV_TO_JY_PREAUTHORIZATION_STOP",
        "VERIFIED__JX_TO_JY_PREAUTHORIZATION_STOP",
    }:
        raise JYBarrierError("JY_CONTINUATION_LABEL_MISMATCH")
    dashboard["constitutional_continuation_progress"] = (
        "VERIFIED__JX_TO_JY_PREAUTHORIZATION_STOP"
    )
    envelope["reduction_sha256"] = sha256_bytes(M.canonical_bytes(reduction))
    path.write_bytes(M.canonical_bytes(envelope))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    M.materialize(parse_args())
    finalize_jx_continuation_label()
