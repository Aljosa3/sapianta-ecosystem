#!/usr/bin/env python3
"""Run the sole same-generation KY Phase-B attempt through existing owners."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
from types import ModuleType


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KW_CONTROLLER = Path(
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KW_PHASE_B_RECOVERY_CONTROLLER_V1.py"
)
KW_CONTROLLER_SHA256 = (
    "26c76256f96ecaff46c482f160d5ba11a9c1f2e55e2b06f8f65c28cfa412bd55"
)
HEAD = "d19208af9d9633c764838399e5a86a441e9386ef"
TREE = "40207213a9359f536f9e6380c113c67f5ac6ab3f"
SUBJECT = "G77-256KX bind runtime export custody traversal"
SOURCE_SHA256 = "cca776c3b01cc45d31c572cff16e95d15193bd7318cdcaf3142485cc669c92b4"
CANDIDATE_SHA256 = "934af2544e313386b041f5be827c154eca9660b68c731e294ad8bdba69f6dd99"
CONTEXT_SHA256 = "cb36b379fc20937e905fe766db044f65e299d46b85d0fbc12af8b5be01ea9d7a"
CONTEXT_FILE_SHA256 = "d38691138b7eafb47eb568a98acde90879406abf82244c99507aa768d38aaec7"
ARGV_SHA256 = "46ca8e68c9269de3dbfc1713f69c3e60e23e5048b15a9318a46f88e632093462"
TEMPORAL_SHA256 = "13aef4d12026ee87d7fa3ccfa6350975a48faeb7a69adcf35b7b98b6fc8e7940"
REQUEST_SHA256 = "46fd5ef4ce7142667958f3f825364c9366551e75f07427ca866d41d1b2f5cbb1"
REQUEST_FILE_SHA256 = "484cfbd5389ab19b6e2920de774b0cb85a6d01d6bc9ec01d9f69f5c59a46f7a2"
PRESENTATION_SHA256 = "945e380145c3681494b9fb767a1afce4e736ce8dfa45fc3b83c02aeb19f2fea4"
DECISION_PRESENTATION_SHA256 = "04a3a51c1f0aab49bad06221457e32571c5f2a513dfa94569b7706967f691378"
PHASE_A_TERMINAL = (
    "A__KY_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__"
    "NO_HUMAN_AUTHORITY__NO_HANDOFF__NO_BINDING__NO_CONSUMPTION__"
    "NO_PHASE_B__NO_OPERATION"
)
PHASE_A_HASHES = {
    "G77_256KY_G48_IMPLEMENTATION_REPORT_V1.md": "6fc1f812b1efa3168cd1f1e771d83518b4dd0fe0dd0310b1a5cde76f1e36baaa",
    "G77_256KY_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "1cebf2f97363a9cd679397e686acbe13e20a49291181e418e0cbaefa9482cc75",
    "G77_256KY_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "e2a64bd3d9f39b094c0fe22a180598f3d3949ef0bda9555396c4c8f1f550c91c",
    "G77_256KY_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "e14bca1f7b829494e5064ffcb70d42d3eef49d8d3a04fa419b4a1d439d31306f",
    "G77_256KY_HUMAN_DECISION_PRESENTATION_V1.txt": DECISION_PRESENTATION_SHA256,
    "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": PRESENTATION_SHA256,
    "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": REQUEST_FILE_SHA256,
    "G77_256KY_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": "3a58740a5d7040a4ae480890f89dd9ff2b5b3688e8b272076af4c0bcdf2223f1",
    "G77_256KY_KB_NAMESPACE_PREFLIGHT_V1.json": "16641e2d7e02d54b7540bce394a73afa2de235387826de31b87a843c1515ce99",
    "G77_256KY_KD_INTERFACE_PREFLIGHT_V1.json": "9df8dd2431db7797ef8732568796abcbbdc2fe1720e867bc52e18df121802238",
    "G77_256KY_KF_PERMISSION_BINDING_PREFLIGHT_V1.json": "fa0be5d3fd10e0286ff89915dfdc2f191fbf874ff8165a8cb5a0f9eeac675874",
    "G77_256KY_KI_FRONTIER_PREFLIGHT_V1.json": "26ef3df7f7f2be322e9e64807b478edc68f48712c6e98dfd5a415ddfe4f66fef",
    "G77_256KY_KM_SCHEMA_BINDING_PREFLIGHT_V1.json": "b2c7d01f626c9dd4024865108711ce2c24b3981d4a182028ea199991bdd55533",
    "G77_256KY_PREAUTHORITY_STATIC_READINESS_V1.json": "49fc4809f201cf632daf878161da8540d764ba2b5a06531a8dba754cfde5ec02",
    "G77_256KY_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "347fe6fd65c5fda8494479c73fed6383633aaf1650e57feeb7fe781153d832a1",
    "G77_256KY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": "2374cf06f9c33e0d8a66553a70e942d7ed022a0a49128648bd2c8d1c1dc5981f",
    "G77_256KY_PREHUMAN_PHASE_A_REDUCTION_V1.json": "730e0f95a593c6cc176979f4b37860089670e87e0f83bb503a989f3795e6238c",
    "analysis/G77_256KY_PHASE_A_SUCCESS_VERIFIER_V1.py": "0897541260051b07279bd40b05f806c06de23247f7ae3bb49413b7d42b75d436",
    "candidate_source/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json": CANDIDATE_SHA256,
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/G77_256KY_EXPIRED_VECTOR_ADAPTER_V1.py": "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    "operation_state/runtime_export/G77_256KY_CONTINUATION_MANIFEST_V1.json": CANDIDATE_SHA256,
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE_SHA256,
    "orchestration/G77_256KY_PREAUTHORIZATION_MATERIALIZER_V1.py": "b1dcc5af25a0ce784920405f7e65ca979e4a856b3f15d503a1d159d63880ecdb",
    "tests/test_g77_256ky_phase_a_success_v1.py": "6ea2f2e935acf60b7711b8b423843a2961bd1b8937985e3a92cd9f85134ac1a1",
}


def load_controller() -> ModuleType:
    path = ROOT / KW_CONTROLLER
    raw = path.read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{HEAD}:{KW_CONTROLLER.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if raw != committed or hashlib.sha256(raw).hexdigest() != KW_CONTROLLER_SHA256:
        raise RuntimeError("COMMITTED_KW_PHASE_B_CONTROLLER_MISMATCH")
    source = raw.decode("utf-8").replace("KW", "KY").replace("kw", "ky")
    source = source.replace(
        "len(SOURCE.read_bytes()) != 1213", "len(SOURCE.read_bytes()) != 1208"
    )
    source = source.replace(
        "A__KY_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__NO_HUMAN_AUTHORITY__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION",
        PHASE_A_TERMINAL,
    )
    module = ModuleType("g77_256ky_authenticated_phase_b_controller")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.HEAD = HEAD
    module.TREE = TREE
    module.SUBJECT = SUBJECT
    module.SOURCE_SHA256 = SOURCE_SHA256
    module.CANDIDATE_SHA256 = CANDIDATE_SHA256
    module.CONTEXT_SHA256 = CONTEXT_SHA256
    module.CONTEXT_FILE_SHA256 = CONTEXT_FILE_SHA256
    module.ARGV_SHA256 = ARGV_SHA256
    module.TEMPORAL_SHA256 = TEMPORAL_SHA256
    module.REQUEST_SHA256 = REQUEST_SHA256
    module.REQUEST_FILE_SHA256 = REQUEST_FILE_SHA256
    module.PRESENTATION_SHA256 = PRESENTATION_SHA256
    module.DECISION_PRESENTATION_SHA256 = DECISION_PRESENTATION_SHA256
    module.PHASE_A_HASHES = dict(PHASE_A_HASHES)
    module.EXPECTED_SOURCE = module.SOURCE.read_text(encoding="utf-8")
    return module


C = load_controller()


if __name__ == "__main__":
    arguments = C.parse_args()
    if arguments.mode == "prepare":
        C.prepare(arguments)
    else:
        raise SystemExit(C.consume_and_operate(arguments))
