#!/usr/bin/env python3
"""Authenticate and execute the exact KG Human-authorized one-shot route.

The committed KE/KC controller chain remains the procedural owner. This
wrapper binds it to the exact KG Phase-A artifacts, exact Human-source bytes,
and committed KF launcher identity. It offers no retry or digest override.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KG = ROOT / (
    ".github/governance/evidence/"
    "g77_256kg_fresh_expired_operational_recommissioning_v1"
)
BASE = Path(
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KE_PHASE_B_CONTROLLER_V1.py"
)
BASE_SHA256 = "fbbf896c53d05330cd8ef8b8b1a1b3219ca0c3ffa6f6a5fa08b1ded22c4fc8b9"
HEAD = "3bcc78deaeb6821dd71ecdbc9de18628d3ff07de"
TREE = "eb06ab5d18fc99d648b7ba20d40269ccf3d0de40"
SUBJECT = "G77-256KF verify guest harness permission binding repair"
REQUEST_SHA256 = "339986a25c10c17eac02527372563f132eebb501c440ea5e49f14af17ab9dad0"
REQUEST_FILE_SHA256 = "03d46552fd2e7478c536b32abfd373185fc7b9af7ab27d9d064ba90d5fb8c56b"
PRESENTATION_SHA256 = "ce52477b12c222182d6be5879e35728292a76022a36fbbedde0d9805d5e875ae"
SAFE_STOP_SHA256 = "49484c90bcf86c3d57e665fffea463d89ff36c27251abee74d21db21e364f292"
SAFE_STOP_FILE_SHA256 = "b9893bb6c702a07fda2666afb954de089a0461f04a3740b62912069b1a7999bf"
CONTEXT_SHA256 = "72b9480fa22513f01cfd8d935efbfe44bed15c246f9d54ee5c0b3c78ed53c0bd"
CONTEXT_FILE_SHA256 = "8010391eae9d00175159549d9c1079ebf8a9cbb78213f089dc0120f34bed017b"
ARGV_SHA256 = "0bf7f3fda2af5dffab173baccee2dd683b737d871d69e9858d0bfa55cae8f786"
TEMPORAL_SHA256 = "52ecdbbb6c1b89a16f9b93d602686c231d67788331031c177643c4a35f6a866b"
JZ_READINESS_INNER = "8d6c2b5bd9773f92a1977cbec8e7623ca598487b9c50d1d786af0b54cfad43c2"
JZ_READINESS_FILE = "dd3562e660a85485c4544071a4116999a0213fc18b53b0a173a961aebaedd748"
HUMAN_SOURCE_SHA256 = "d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484"
GENERATION = "G77_256KG_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KG_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"

EXPECTED_HUMAN_ACT = """I authorize exactly one bounded G77_256KG SPCE Phase-B attempt for:

GENERATION G77_256KG_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1
OPERATION G77_256KG_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001
CANDIDATE_SHA256 8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a
CONTEXT 72b9480fa22513f01cfd8d935efbfe44bed15c246f9d54ee5c0b3c78ed53c0bd
CONTEXT_FILE_SHA256 8010391eae9d00175159549d9c1079ebf8a9cbb78213f089dc0120f34bed017b
CANONICAL_ARGV_SHA256 0bf7f3fda2af5dffab173baccee2dd683b737d871d69e9858d0bfa55cae8f786
TEMPORAL_BINDING 52ecdbbb6c1b89a16f9b93d602686c231d67788331031c177643c4a35f6a866b
REQUEST_IDENTITY 339986a25c10c17eac02527372563f132eebb501c440ea5e49f14af17ab9dad0
REQUEST_FILE_SHA256 03d46552fd2e7478c536b32abfd373185fc7b9af7ab27d9d064ba90d5fb8c56b
PRESENTATION_SHA256 ce52477b12c222182d6be5879e35728292a76022a36fbbedde0d9805d5e875ae
READINESS_CHECKPOINT de2036904c44cd5452df4e2d2aef3ffa49264f6b127392ba7cf8bd9aa129c22e
SAFE_STOP_CHECKPOINT 49484c90bcf86c3d57e665fffea463d89ff36c27251abee74d21db21e364f292
STARTING_E05_STATE VERIFIED__11_OF_18

Maximums: one authority consumption and one bounded KG operational attempt.
Retries, repair retries, replays, replacement authority, second KG attempt,
and successor-generation authority transfer are prohibited.

EXPIRED denial before P11 entry is expected but remains unproven until
operationally observed.
"""

PHASE_A_HASHES = {
    "G77_256KG_G48_IMPLEMENTATION_REPORT_V1.md": "4e076c717afb6232bc090de0d468672b6872a94a49a839dce90572c263ea8c5b",
    "G77_256KG_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "1d8a54c1b9ae2202bbf63284d082f777514cedc6d19be6af40565bb7e455cd6e",
    "G77_256KG_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "879ede24aba321ef09bcc93dd7f8bcec4b4d07671f4bc496038b9653635dc1ed",
    "G77_256KG_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "dadb8d5c2c2a6f6785ff33892717a55d72331b68ff9cd21b36531fc3d344e02f",
    "G77_256KG_HUMAN_DECISION_PRESENTATION_V1.txt": "236b9bc71f01a3a6c1c3e4ad080a6e2f168d7fbadf4477970ba926f844aec6fe",
    "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KG_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": JZ_READINESS_FILE,
    "G77_256KG_KB_NAMESPACE_PREFLIGHT_V1.json": "be8f8721b38991afd1594caf94cb407f044a6df5239a541cb67beeb310bfd8ef",
    "G77_256KG_KD_INTERFACE_PREFLIGHT_V1.json": "a19cc953aaa3926a446e24c5f0f77e0fa420b4ce4e9eae462dcc86449b1c3ef0",
    "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_V1.json": "431913293a34a47cc5086063bc5b184075681b910c11e14d3688c819e86125cc",
    "G77_256KG_PREAUTHORITY_STATIC_READINESS_V1.json": "7c5efa98b90b496712864e587cde5d02458d991a87dc7ffc005899bb16ac9f3f",
    "G77_256KG_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "2ce0fdb6a2bdbf923d35406b1885ddcba07594a26c3df21c25fb3cc7e103c2f0",
    "G77_256KG_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
    "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json": "a366f315d505f004b77cb6311b52ec542343d74893691b1f6e340d65009ed15f",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/G77_256KG_EXPIRED_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256KG_CONTINUATION_MANIFEST_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KG_POSTHUMAN_INVOCATION_BINDER_V1.py": "73269ff6b3ba0934db86fd97333703d56acc9ce40eeafbc5cb7d79dc9f244629",
    "orchestration/G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py": "b187e9e36e5a74aaa6836bfc2f3ae30ad7eacc190125aca07563af4aeaa84da6",
    "tests/test_g77_256kg_preauthorization_barrier_v1.py": "1dfa78ed54af1e7e87719f8ec0e07179205b2040c89906e100ea0f24c6aa15fb",
}


class KGPhaseBError(RuntimeError):
    """One deterministic fail-closed KG Phase-B error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load_adapted_ke_controller() -> ModuleType:
    path = ROOT / BASE
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{BASE}"], cwd=ROOT)
    if raw != committed or hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise KGPhaseBError("COMMITTED_KE_PHASE_B_CONTROLLER_MISMATCH")
    source = raw.decode("utf-8")
    source = source.replace('.replace("KC", "KE")', '.replace("KC", "KG")')
    source = source.replace('.replace("kc", "ke")', '.replace("kc", "kg")')
    source = source.replace("G77_256KE", "G77_256KG")
    source = source.replace("G77-256KE", "G77-256KG")
    source = source.replace("g77_256ke", "g77_256kg")
    source = source.replace("_ke_", "_kg_")
    source = source.replace("authenticate_ke", "authenticate_kg")
    source = source.replace("KEPhaseBError", "KGPhaseBError")
    source = source.replace("KE_", "KG_").replace("__KE", "__KG")
    source = re.sub(r"\bKE\b", "KG", source)
    replacements = {
        "ed4acdc4c132754d857d623e54783e54e4c96d52": HEAD,
        "be8967cad28c9149fb5e17b895e5c58ac119ef13": TREE,
        "G77-256KD verify KC Phase-B entry owner interface binding": SUBJECT,
        "ba27eaafd1c5f00acd6753bfae8f33f3189a744a6674de187ab8e943b78f58be": PHASE_A_HASHES["orchestration/G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py"],
        "93992dd0b846c1d3427136ebce7ea3cdcabd2adb586ecf4673d8ec431f64c009": REQUEST_SHA256,
        "b09920b988065ac993ce63dd33c942ac7c4ad7894fbc6f57e6dbdb214137a22d": REQUEST_FILE_SHA256,
        "f1e5db303ead13627949d7ec031ff0610ef673369765cb6c1bc59b7ee37a5b9f": PRESENTATION_SHA256,
        "ad8a7aef49f5ef37e2bb601e8240b4c96dba4a8f4892b9d161dbcc880ec60b0f": SAFE_STOP_SHA256,
        "0c4889163cdcc1467d92d88cc5949e081bde27b8b74b02bd1cdf19dfbc27d0df": SAFE_STOP_FILE_SHA256,
        "6e481f0d449a0f5912931a5dca5c6a40a235d13ebe0811c48801ceb5e877aa98": CONTEXT_SHA256,
        "1dea07f1ec4d848d749b9b43719e083269e8159815b9a86a13f618e97608af3d": CONTEXT_FILE_SHA256,
        "d2efbe459283933f52a4fc3b32cd22c682271684e823620afa1c46a7d9929cc0": ARGV_SHA256,
        "dca2908d31e03f39bbd34509243af1341050b4ee74230fc115e6539a77631e91": TEMPORAL_SHA256,
        "c0427849c8259c20f9c5d0f66cbadf6d508d89a792f29afda02be46908b02d1a": JZ_READINESS_INNER,
        "dbecb478d76f3b8bdb9ba954c915f1ce97bff6a39729fb58e617ae86b9666606": JZ_READINESS_FILE,
        "2a5b0f25fb9e9b0cca9a6bf1d6ee803f4c73f3b3415039fbaab9eae53ac25724": HUMAN_SOURCE_SHA256,
        "module.MATERIALIZER.K = module.MATERIALIZER.K.K": (
            "module.MATERIALIZER.K = module.MATERIALIZER.E.K.K"
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    module = ModuleType("g77_256kg_authenticated_phase_b_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.PHASE_A_HASHES = PHASE_A_HASHES
    module.HUMAN_SOURCE_SHA256 = HUMAN_SOURCE_SHA256
    module.EXPECTED_GRANT = EXPECTED_HUMAN_ACT
    module.C.PHASE_A_HASHES = PHASE_A_HASHES
    module.C.HUMAN_SOURCE_SHA256 = HUMAN_SOURCE_SHA256
    module.C.EXPECTED_GRANT = EXPECTED_HUMAN_ACT
    return module


W = load_adapted_ke_controller()
C = W.C
KG_MATERIALIZER = W.C.MATERIALIZER


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KGPhaseBError(f"NONCANONICAL_JSON:{path.name}")
    return value


def authenticate_kg_preflights() -> None:
    source = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    if source.read_bytes() != EXPECTED_HUMAN_ACT.encode():
        raise KGPhaseBError("EXACT_HUMAN_SOURCE_BYTES_MISMATCH")
    if hashlib.sha256(source.read_bytes()).hexdigest() != HUMAN_SOURCE_SHA256:
        raise KGPhaseBError("DERIVED_HUMAN_SOURCE_DIGEST_MISMATCH")
    W.authenticate_kg_preflights()
    kf = W.C.MATERIALIZER
    wrapper = sys.modules.get("g77_256kg_phase_b_materializer")
    if wrapper is None or not hasattr(wrapper, "authenticate_kf"):
        raise KGPhaseBError("KG_KF_PREFLIGHT_OWNER_UNAVAILABLE")
    authenticated = wrapper.authenticate_kf()
    if (
        authenticated.get("terminal")
        != "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED"
        or authenticated.get("presentation_mode") != "0701"
        or authenticated.get("read_only_projection") != "VERIFIED__PRESERVED"
        or authenticated.get("ex_assumption_invalidation_count") != 0
    ):
        raise KGPhaseBError("KG_KF_PREFLIGHT_MISMATCH")
    del kf
    wrapper.rebind_kf_launcher_identity()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "consume-and-operate"))
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    authenticate_kg_preflights()
    if arguments.mode == "prepare":
        C.prepare(arguments)
    else:
        raise SystemExit(C.consume_and_operate(arguments))
