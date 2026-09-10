#!/usr/bin/env python3
"""Authenticate and execute the exact KE Human-authorized one-shot route."""

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
KE = ROOT / (
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1"
)
BASE = Path(
    ".github/governance/evidence/"
    "g77_256kc_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KC_PHASE_B_CONTROLLER_V1.py"
)
BASE_SHA256 = "f950bb6ee2165169e1598c3d95ceff1cf719ed0a259421f48189ee9de4a14aad"
MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
MATERIALIZER_SHA256 = "ba27eaafd1c5f00acd6753bfae8f33f3189a744a6674de187ab8e943b78f58be"
HEAD = "ed4acdc4c132754d857d623e54783e54e4c96d52"
TREE = "be8967cad28c9149fb5e17b895e5c58ac119ef13"
SUBJECT = "G77-256KD verify KC Phase-B entry owner interface binding"
REQUEST_SHA256 = "93992dd0b846c1d3427136ebce7ea3cdcabd2adb586ecf4673d8ec431f64c009"
REQUEST_FILE_SHA256 = "b09920b988065ac993ce63dd33c942ac7c4ad7894fbc6f57e6dbdb214137a22d"
PRESENTATION_SHA256 = "f1e5db303ead13627949d7ec031ff0610ef673369765cb6c1bc59b7ee37a5b9f"
SAFE_STOP_SHA256 = "ad8a7aef49f5ef37e2bb601e8240b4c96dba4a8f4892b9d161dbcc880ec60b0f"
SAFE_STOP_FILE_SHA256 = "0c4889163cdcc1467d92d88cc5949e081bde27b8b74b02bd1cdf19dfbc27d0df"
CONTEXT_SHA256 = "6e481f0d449a0f5912931a5dca5c6a40a235d13ebe0811c48801ceb5e877aa98"
CONTEXT_FILE_SHA256 = "1dea07f1ec4d848d749b9b43719e083269e8159815b9a86a13f618e97608af3d"
ARGV_SHA256 = "d2efbe459283933f52a4fc3b32cd22c682271684e823620afa1c46a7d9929cc0"
TEMPORAL_SHA256 = "dca2908d31e03f39bbd34509243af1341050b4ee74230fc115e6539a77631e91"
JZ_READINESS_INNER = "c0427849c8259c20f9c5d0f66cbadf6d508d89a792f29afda02be46908b02d1a"
JZ_READINESS_FILE = "dbecb478d76f3b8bdb9ba954c915f1ce97bff6a39729fb58e617ae86b9666606"
GENERATION = "G77_256KE_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KE_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
HUMAN_SOURCE_SHA256 = "2a5b0f25fb9e9b0cca9a6bf1d6ee803f4c73f3b3415039fbaab9eae53ac25724"

PHASE_A_HASHES = {
    "G77_256KE_G48_IMPLEMENTATION_REPORT_V1.md": "3ebe0703157938146503c23ad40acbc5db35c22f9bea3e0a9242d699f3bf7ef5",
    "G77_256KE_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "5dfbd285050e160f4f591168e4e71507119cf497b7df382b5d34f8fa6e351264",
    "G77_256KE_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "af6b18768c4f332f9ffea48100c883c7bcf327b0b2d643ed3af4c42fc69f50d0",
    "G77_256KE_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "dd87f7051eb89144c23b606c02b8754361a0c3d3fbf7c32661e78e5196894f63",
    "G77_256KE_HUMAN_DECISION_PRESENTATION_V1.txt": "57e1ef3752e1e2dbe6a2ef65297908089c1362dd7dd1af6a82c82ca003b2f262",
    "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KE_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": JZ_READINESS_FILE,
    "G77_256KE_KB_NAMESPACE_PREFLIGHT_V1.json": "8f885a71054d5862e01c5f4dd494dcad5bc404b722c4b477d28c1aac8b212aa9",
    "G77_256KE_KD_INTERFACE_PREFLIGHT_V1.json": "45ca1e85c938180d8dd0edc2a6417ca51a4f037909b6ba1abf31774814890725",
    "G77_256KE_PREAUTHORITY_STATIC_READINESS_V1.json": "a34fc5f304224001ac63f1ce1aa09202e7d4ce9b7bff094ff17dc8dff7dab5b5",
    "G77_256KE_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "5534de2cb27b58583dfcd5facfffdfdcac4aa58948ac3826fe98817a5e50cbc4",
    "G77_256KE_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
    "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json": "faf271a3fed16ee92ede9f2a6585915df9420f53de20d7a85bb09a69980e2c1d",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/G77_256KE_EXPIRED_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256KE_CONTINUATION_MANIFEST_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KE_POSTHUMAN_INVOCATION_BINDER_V1.py": "51f0ff5e9cdb9471b8c12d1c063f997d2347bd017cfd415133f0abc307d11d11",
    "orchestration/G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py": MATERIALIZER_SHA256,
    "tests/test_g77_256ke_preauthorization_barrier_v1.py": "82f11608b76e6132a21fe3c48c3491f0cbe87173f9337ece488d68b0ed589628",
}


class KEPhaseBError(RuntimeError):
    """One deterministic fail-closed KE Phase-B error."""


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KEPhaseBError(f"NONCANONICAL_JSON:{path.name}")
    return value


def verified_inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KEPhaseBError(f"SEAL_MISMATCH:{path.name}")
    return value


def load_adapted_controller() -> ModuleType:
    path = ROOT / BASE
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{BASE}"], cwd=ROOT)
    if raw != committed or hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise KEPhaseBError("COMMITTED_KD_CORRECTED_KC_CONTROLLER_MISMATCH")
    source = raw.decode().replace("KC", "KE").replace("kc", "ke")
    replacements = {
        "2b0a1ff1d7bc3e071392a786dfb64c2eac392df3": HEAD,
        "2b7e42af265f20404ad467c6f1069df56cc388f8": TREE,
        "G77-256KB verify EXPIRED guest namespace binding repair": SUBJECT,
        "f41a7b9942a1de0b1825bdda3676d04968d857d01f7370551844abcde16de1d2": MATERIALIZER_SHA256,
        "bc1254111d1ea190df866f0530e9dd556f2741d38ca16bebf052f1d56d03513b": REQUEST_SHA256,
        "962c415d915390d78e60ba5a56ab3e652742a40ecd5fa1a3cd2201ebd0186bff": REQUEST_FILE_SHA256,
        "5b53e41fd97af4d2674d5252b62a87bb63cbf6bbb1eb5cc44decd41cc5cbaa73": PRESENTATION_SHA256,
        "7a5789bdb5fd7b92ffbd8a374a7c0e8c132547c9ffd54cdf80a5856e7b7e2afe": SAFE_STOP_SHA256,
        "33116554a27fbef0031278e1ec1c7037dbe80889b6020aedfdf82121f991f644": SAFE_STOP_FILE_SHA256,
        "d4686c4145c23e6f544c902825628075e1ea4d36b92fdd25c2ea6473dcc33855": CONTEXT_SHA256,
        "a88c61f5cb4c445707121f149baec957261dc08d7eb5a6ae937065aa467c6d31": CONTEXT_FILE_SHA256,
        "4580faf1e6096af5aaf7d3a52be5590829987bb3b7a910474662da36b0605564": ARGV_SHA256,
        "14a09e41caa84dce2376ccd5143812682660f3d0b3fa76dd904edecd8be7b428": TEMPORAL_SHA256,
        "6f161d3a45be2b03cf8eaf11731176102a90b1abd8faa5eeb033cddc47cc8000": JZ_READINESS_INNER,
        "cefaf85c4f3735294dac4f5274972c0b9ac0615340e2a8ae76bb2f7eed29b18c": JZ_READINESS_FILE,
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    source = source.replace(
        "    _bind_ke_phase_b_materializer_owner(module)\n",
        "    module.MATERIALIZER.K = module.MATERIALIZER.K.K\n"
        "    _bind_ke_phase_b_materializer_owner(module)\n",
    )
    module = ModuleType("g77_256ke_authenticated_kd_corrected_controller")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    controller = module.C
    for name, value in {
        "HEAD": HEAD, "TREE": TREE, "SUBJECT": SUBJECT,
        "GENERATION": GENERATION, "OPERATION": OPERATION,
        "REQUEST_SHA256": REQUEST_SHA256, "REQUEST_FILE_SHA256": REQUEST_FILE_SHA256,
        "PRESENTATION_SHA256": PRESENTATION_SHA256, "SAFE_STOP_SHA256": SAFE_STOP_SHA256,
        "SAFE_STOP_FILE_SHA256": SAFE_STOP_FILE_SHA256, "CONTEXT_SHA256": CONTEXT_SHA256,
        "CONTEXT_FILE_SHA256": CONTEXT_FILE_SHA256, "ARGV_SHA256": ARGV_SHA256,
        "TEMPORAL_SHA256": TEMPORAL_SHA256, "JZ_READINESS_INNER": JZ_READINESS_INNER,
        "JZ_READINESS_FILE": JZ_READINESS_FILE, "PHASE_A_HASHES": PHASE_A_HASHES,
        "EXPECTED_GRANT": module.EXPECTED_GRANT,
    }.items():
        setattr(controller, name, value)
    return module


W = load_adapted_controller()
C = W.C


def authenticate_ke_preflights() -> None:
    reduction = verified_inner(KE / "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json", "reduction")
    kb = verified_inner(KE / "G77_256KE_KB_NAMESPACE_PREFLIGHT_V1.json", "proof")
    kd = verified_inner(KE / "G77_256KE_KD_INTERFACE_PREFLIGHT_V1.json", "proof")
    if (
        reduction.get("terminal") != "A__FRESH_KE_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
        or set(reduction.get("operational_counters", {}).values()) != {0}
        or reduction.get("generation_identity") != GENERATION
        or reduction.get("operation_identity") != OPERATION
        or kb.get("negative_rejection_count") != 8
        or kb.get("exact_ke_result", {}).get("projection_status") != "EXACT_GUEST_PROJECTION"
        or kd.get("controller_materializer_binding") != "VERIFIED__CONTROLLER_MATERIALIZER_IS_K"
        or kd.get("resolved_interface") != "K.A.authenticate_entry(remote_head, nested_remote_tag)"
        or kd.get("fallback_selector_parallel_owner") != "VERIFIED__ABSENT"
    ):
        raise KEPhaseBError("KE_PHASE_A_PREFLIGHT_MISMATCH")
    if sha256_path(KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt") != HUMAN_SOURCE_SHA256:
        raise KEPhaseBError("KE_HUMAN_SOURCE_BYTES_MISMATCH")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "consume-and-operate"))
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    authenticate_ke_preflights()
    if arguments.mode == "prepare":
        C.prepare(arguments)
    else:
        raise SystemExit(C.consume_and_operate(arguments))
