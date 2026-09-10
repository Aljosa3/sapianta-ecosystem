#!/usr/bin/env python3
"""Authenticate and consume the exact JY Human grant once, without launch."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
from types import ModuleType


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HEAD = "939d7eda8ff333b6cf0dfbd54d274aabefcba698"
TREE = "bce9f2863a7314a1e5e088066efeea52615d989d"
REQUEST_SHA256 = "ef16d1ed352e34ebde9e7280f920523daba139ed0a878a90ef0c700c84427201"
REQUEST_FILE_SHA256 = "4fe6e3664be8803a14137bcd28937d6368582fd7a23cd03aaae356bce7a9743d"
PRESENTATION_SHA256 = "8c9634888efe7b7493b18d53c6f6719f177185d19c7831486cca7c7400fc4094"
PHASE_A_SAFE_STOP_SHA256 = "d20e48c1a4f6f834ca814c6c86ae0d434bd09ed87e5ebd8effbfb2712f94d02e"
PHASE_A_SAFE_STOP_FILE_SHA256 = "9a6eb4b3d97f991fcb0a68839986a0003179f21ab92ae593237ffd17f7c7cd4c"
CONTEXT_SHA256 = "889069b1a29fa8ec7ace00881ee3de47fa096ecf2f9983d66a48b825b5f5513e"
CONTEXT_FILE_SHA256 = "59aa547f59866d071c4ce019348c6222b7eb6881a30bfb2085ef1f464ee93a1f"
ARGV_SHA256 = "841153f68722a5be36f8549e05a569c99276b604c3360b58015b9b2897144bb4"
EXPIRED_ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
TEMPORAL_BINDING_SHA256 = "0a9b0ad42ed50e33ad985ed1a1d9adbb387d207dedd415a0f20134dfd893c064"

BASE = Path(
    ".github/governance/evidence/g77_256jw_expired_operational_v1/"
    "orchestration/G77_256JW_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"
)
BASE_SHA256 = "38244d95882e76746072f77d69647623633dd64a9f20c7da5ceda8fcf21ed4a7"


class JYAuthorityError(RuntimeError):
    """One fail-closed JY authority-controller error."""


def load_controller() -> ModuleType:
    path = ROOT / BASE
    source_bytes = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{BASE}"], cwd=ROOT)
    if source_bytes != committed or hashlib.sha256(source_bytes).hexdigest() != BASE_SHA256:
        raise JYAuthorityError("COMMITTED_JW_AUTHORITY_OWNER_MISMATCH")
    source = source_bytes.decode("utf-8")
    source = source.replace("JW", "JY")
    source = source.replace("jw", "jy")
    source = source.replace("authenticate_jt", "authenticate_jx")
    module = ModuleType("g77_256jy_authenticated_authority_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.HEAD = HEAD
    module.TREE = TREE
    module.REQUEST_SHA256 = REQUEST_SHA256
    module.REQUEST_FILE_SHA256 = REQUEST_FILE_SHA256
    module.PRESENTATION_SHA256 = PRESENTATION_SHA256
    module.PHASE_A_SAFE_STOP_SHA256 = PHASE_A_SAFE_STOP_SHA256
    module.PHASE_A_SAFE_STOP_FILE_SHA256 = PHASE_A_SAFE_STOP_FILE_SHA256
    module.CONTEXT_SHA256 = CONTEXT_SHA256
    module.CONTEXT_FILE_SHA256 = CONTEXT_FILE_SHA256
    module.ARGV_SHA256 = ARGV_SHA256
    module.EXPIRED_ADAPTER_SHA256 = EXPIRED_ADAPTER_SHA256
    module.TEMPORAL_BINDING_SHA256 = TEMPORAL_BINDING_SHA256
    module.EXPECTED_NORMALIZED_GRANT = (
        "I explicitly authorize G77-256JY request " + REQUEST_SHA256
        + " and safe-stop checkpoint " + PHASE_A_SAFE_STOP_SHA256
        + " for generation " + module.GENERATION
        + ", operation " + module.OPERATION
        + ", candidate " + module.CANDIDATE_SHA256
        + ", context " + CONTEXT_SHA256
        + ", context file " + CONTEXT_FILE_SHA256
        + ", canonical argv " + ARGV_SHA256
        + ", EXPIRED adapter " + EXPIRED_ADAPTER_SHA256
        + ", temporal binding " + TEMPORAL_BINDING_SHA256
        + ", JR runtime HEAD " + module.JR_HEAD
        + " and TREE " + module.JR_TREE
        + ", starting from E05 11/18, subject to exactly one authority consumption, "
          "PRE, FM invocation, no-network QEMU launch, VM operation, and EXPIRED operation "
          "attempt, with zero retry, repair retry, replay, P11 entry, protected invocation, "
          "or protected effect expected; I understand that EXPIRED denial before P11 entry "
          "is an expected result and is not proven until observed.\n"
    )
    return module


C = load_controller()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    C.main(parse_args())
