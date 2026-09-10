#!/usr/bin/env python3
"""Authenticate, bind, consume, and invoke the exact KC Human act once.

The committed KA Phase-B controller remains the procedural owner.  This
wrapper authenticates those committed bytes, adapts only the generation-local
namespace, and supplies the independently authenticated KC Phase-A identities
and the exact Human-source sentence.  No authority digest is caller supplied.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
from types import ModuleType


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BASE = Path(
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KA_PHASE_B_CONTROLLER_V1.py"
)
BASE_SHA256 = "44cde7913d6fef0a3c48cb7b96b82e7b79605c94a963f2acd0f36b0b0f80e34e"

HEAD = "2b0a1ff1d7bc3e071392a786dfb64c2eac392df3"
TREE = "2b7e42af265f20404ad467c6f1069df56cc388f8"
REQUEST_SHA256 = "bc1254111d1ea190df866f0530e9dd556f2741d38ca16bebf052f1d56d03513b"
REQUEST_FILE_SHA256 = "962c415d915390d78e60ba5a56ab3e652742a40ecd5fa1a3cd2201ebd0186bff"
PRESENTATION_SHA256 = "5b53e41fd97af4d2674d5252b62a87bb63cbf6bbb1eb5cc44decd41cc5cbaa73"
SAFE_STOP_SHA256 = "7a5789bdb5fd7b92ffbd8a374a7c0e8c132547c9ffd54cdf80a5856e7b7e2afe"
SAFE_STOP_FILE_SHA256 = "33116554a27fbef0031278e1ec1c7037dbe80889b6020aedfdf82121f991f644"
CONTEXT_SHA256 = "d4686c4145c23e6f544c902825628075e1ea4d36b92fdd25c2ea6473dcc33855"
CONTEXT_FILE_SHA256 = "a88c61f5cb4c445707121f149baec957261dc08d7eb5a6ae937065aa467c6d31"
ARGV_SHA256 = "4580faf1e6096af5aaf7d3a52be5590829987bb3b7a910474662da36b0605564"
TEMPORAL_SHA256 = "14a09e41caa84dce2376ccd5143812682660f3d0b3fa76dd904edecd8be7b428"
JZ_READINESS_INNER = "6f161d3a45be2b03cf8eaf11731176102a90b1abd8faa5eeb033cddc47cc8000"
JZ_READINESS_FILE = "cefaf85c4f3735294dac4f5274972c0b9ac0615340e2a8ae76bb2f7eed29b18c"

PHASE_A_HASHES = {
    "G77_256KC_G48_IMPLEMENTATION_REPORT_V1.md": "04f980c9f3734c4f6608e6606d8689f177aee0eb56af0940da31e3a76b68d3cb",
    "G77_256KC_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "02cc34be3117d8512478c913a4dc31fdb393fe8725ad758d620ad8eecd3c263a",
    "G77_256KC_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "63409c221d8c59d607e70052c4dad2fe0b3734563b5f39040237051340c64dbb",
    "G77_256KC_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "eb4767cad26b33a79ed7d348ffabda2b9b60bab6e95e3634148b6ac4d19f814c",
    "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KC_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": JZ_READINESS_FILE,
    "G77_256KC_KB_NAMESPACE_PREFLIGHT_V1.json": "bd3dd4d7e70a9344347bc0baff4ce49b8d207b109e8abc7815940cd1ed5b074c",
    "G77_256KC_PREAUTHORITY_STATIC_READINESS_V1.json": "de15ca9ccd947895e104a3489ce962825d19a760fe615447bc6d5631116c5617",
    "G77_256KC_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "1f90d162b0a00dc71940e2b641f26091c53587469669d78f4afcb984101ef6ec",
    "G77_256KC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": SAFE_STOP_FILE_SHA256,
    "G77_256KC_PREHUMAN_PHASE_A_REDUCTION_V1.json": "945b624738f54827d610f2aad15a9c7e656766d09725912b9f41e6bc90a03480",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/G77_256KC_EXPIRED_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256KC_CONTINUATION_MANIFEST_V1.json": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KC_POSTHUMAN_INVOCATION_BINDER_V1.py": "4c52e0ffd3b7e0ad76c76f1b81341a03fdcb4dd70a808ed4995808998c3fe5d2",
    "orchestration/G77_256KC_PREAUTHORIZATION_MATERIALIZER_V1.py": "f41a7b9942a1de0b1825bdda3676d04968d857d01f7370551844abcde16de1d2",
    "tests/test_g77_256kc_preauthorization_barrier_v1.py": "404d7fa8281fd02d553877661624ea7acd68acca06dc2133fa43abcaa972064d",
}

EXPECTED_GRANT = (
    "I explicitly authorize G77-256KC request " + REQUEST_SHA256
    + " and safe-stop checkpoint " + SAFE_STOP_SHA256
    + " for generation G77_256KC_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1, "
      "operation G77_256KC_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001, candidate "
      "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a, context "
    + CONTEXT_SHA256 + ", context file " + CONTEXT_FILE_SHA256
    + ", canonical argv " + ARGV_SHA256 + ", temporal binding " + TEMPORAL_SHA256
    + ", starting from E05 11/18, subject to exactly one authority consumption and one "
      "bounded KC Phase-B attempt, with zero retry, repair retry, replay, replacement "
      "authority, second attempt, or successor-generation authority; I understand that "
      "EXPIRED denial before P11 entry is an expected result and is not proven until observed.\n"
)


class KCPhaseBError(RuntimeError):
    """One deterministic fail-closed KC Phase-B controller error."""


def load_controller() -> ModuleType:
    path = ROOT / BASE
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{BASE}"], cwd=ROOT)
    if raw != committed or hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise KCPhaseBError("COMMITTED_KA_PHASE_B_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("G77_256KA", "G77_256KC")
    source = source.replace("G77-256KA", "G77-256KC")
    source = source.replace("g77_256ka", "g77_256kc")
    source = source.replace("KA", "KC")
    module = ModuleType("g77_256kc_authenticated_phase_b_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.HEAD = HEAD
    module.TREE = TREE
    module.SUBJECT = "G77-256KB verify EXPIRED guest namespace binding repair"
    module.REQUEST_SHA256 = REQUEST_SHA256
    module.REQUEST_FILE_SHA256 = REQUEST_FILE_SHA256
    module.PRESENTATION_SHA256 = PRESENTATION_SHA256
    module.SAFE_STOP_SHA256 = SAFE_STOP_SHA256
    module.SAFE_STOP_FILE_SHA256 = SAFE_STOP_FILE_SHA256
    module.CONTEXT_SHA256 = CONTEXT_SHA256
    module.CONTEXT_FILE_SHA256 = CONTEXT_FILE_SHA256
    module.ARGV_SHA256 = ARGV_SHA256
    module.TEMPORAL_SHA256 = TEMPORAL_SHA256
    module.JZ_READINESS_INNER = JZ_READINESS_INNER
    module.JZ_READINESS_FILE = JZ_READINESS_FILE
    module.PHASE_A_HASHES = PHASE_A_HASHES
    module.EXPECTED_GRANT = EXPECTED_GRANT
    return module


C = load_controller()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "consume-and-operate"))
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.mode == "prepare":
        C.prepare(arguments)
    else:
        raise SystemExit(C.consume_and_operate(arguments))
