#!/usr/bin/env python3
"""Admit and execute the exact FM QEMU argv once after Human authorization."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
GENERATION_IDENTITY = "G77_256FM_FRESH_FL_FK_BOUND_WRONG_ATTEMPT_CANDIDATE_AND_PREBOOT_PREPARATION_V1"
CONSTITUTIONAL_ANCHOR_HEAD = "5c972e9960987ab27420395b54ace693df097e7b"
CANDIDATE_SHA256 = "a28d2c6d903ed0abafd6fecdc1979f763de4c79127018655370975d52fc05fb4"
MATERIALIZATION_SHA256 = "ad3b2d7924c0618cfd2dae12bd6a203001c83028249d9b8a42e649382e1c62c7"
CANONICAL_ARGV_SHA256 = "5f2de525656cf8e107aeb3d094193b3cfacf1d8b8200d86cb0c5762f94bac1d1"
ADAPTER_SHA256 = "b7d8f5b3478d7cfff2cadce7e36b3a12c9b4a1ac5054da867668086f84e866d7"
FK_ADAPTER_SHA256 = "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
ROOT = ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
VECTOR = f"{ROOT}/raw/G77_256FM_QEMU_ARGV_V1.json"
PRE_RECEIPT = f"{ROOT}/raw/G77_256FM_B1_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = f"{ROOT}/raw/G77_256FM_B1_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW_EXECUTION = f"{ROOT}/raw/G77_256FM_RAW_EXECUTION_EVIDENCE_V1.jsonl"
EXECUTION_SEAL = f"{ROOT}/raw/G77_256FM_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN_SEAL = f"{ROOT}/raw/G77_256FM_GUEST_TEARDOWN_SEAL_V1.json"
CANONICALIZER = ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"
CANONICALIZER_SHA256 = "00b2676f1c8360d7c1a3188095520f4592639e174f6b25e198e3036744d948ac"
AUTHORITY_SCHEMA = "G77_256FM_EXECUTION_TIME_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1"
AUTHORIZATION_SCHEMA = "G77_256FM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_V1"
FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256 = "84054b9a8840dd58450e4f0aa5b13e38f07a09a52c27b86c67b36eabcd9833f4"
FN_SPENT_AUTHORIZATION_SHA256 = "0fb64caf25be6abac9c0c1b8071e52527447163f4b1a72c2b1508dc9f5de9658"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")

CANDIDATE = f"{ROOT}/raw/G77_256FM_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json"
MATERIALIZATION = f"{ROOT}/G77_256FM_SPCE_PHASE_B_FRESH_MATERIALIZATION_V1.json"
WRAPPER = f"{ROOT}/harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
FK_ADAPTER = ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
CANONICAL_CHE = "aigol/runtime/canonical_che_evidence_correlation_contract_v1.py"
BASE_IMAGE = "/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img"
OVERLAY = "/tmp/g77_256fm/guest-overlay.qcow2"
SEED = "/tmp/g77_256fm/nocloud-seed.img"

EXPECTED_ASSET_SHA256 = {
    CANDIDATE: CANDIDATE_SHA256,
    MATERIALIZATION: "53f97bf5fca9b706b7f2c86888b3fd3d2ab3a2626b9a0468207aeb642ccf490e",
    VECTOR: "6fe66e009a0a03a2809bdfe8b7ec06162ea01cc01de9ea1f3a4249525f7014a4",
    WRAPPER: ADAPTER_SHA256,
    FK_ADAPTER: FK_ADAPTER_SHA256,
    CANONICAL_CHE: "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
    CANONICALIZER: CANONICALIZER_SHA256,
    BASE_IMAGE: "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733",
    OVERLAY: "6ea4eed169518c646774cfbe2c7b8c00646a9cdead8798f7c94c786c6b6ce8b2",
    SEED: "b36a1aac42f687fe3d6b71200b5b65ec93a8a6de59b7dce31d3e6bf2c3b93c2f",
}

AUTHORIZATION_FIELDS = {
    "schema_id",
    "authorization_present",
    "authorization_kind",
    "authorization_source_sha256",
    "authorized_generation_identity",
    "authorized_vector",
    "authorized_repository_head",
    "authorized_repository_tree",
    "authorized_constitutional_anchor_head",
    "authorized_candidate_sha256",
    "authorized_materialization_sha256",
    "authorized_canonical_argv_sha256",
    "authorized_wrapper_sha256",
    "authorized_fk_adapter_sha256",
    "vm_boot_limit",
    "qemu_system_execution_limit",
    "wrong_attempt_operational_attempt_limit",
    "retry_limit",
    "repair_limit",
    "replay_limit",
    "receipt_namespace_must_be_unconsumed",
    "network_authorized",
    "provider_authorized",
    "trusted_access_authorized",
    "authorization_reusable",
    "auto_continuable",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_atomic(path: Path, value: dict[str, Any]) -> str:
    payload = canonical_bytes(value)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def load_canonicalizer(repository_root: Path) -> ModuleType:
    path = repository_root / CANONICALIZER
    if sha256_path(path) != CANONICALIZER_SHA256:
        raise RuntimeError("canonical QEMU argv implementation hash mismatch")
    spec = importlib.util.spec_from_file_location("g77_256er_qemu_argv_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical QEMU argv implementation import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=repository_root, text=True).strip()


def authority_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_authority(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("execution authority handoff malformed") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError("execution authority handoff is not unique-key canonical JSON")
    return value, hashlib.sha256(raw).hexdigest()


def validate_execution_admission(
    *,
    authority: dict[str, Any],
    authority_file_sha256: str,
    supplied_authority_sha256: str,
    observed_head: str,
    observed_tree: str,
    anchor_is_ancestor: bool,
    repository_clean: bool,
    observed_asset_sha256: dict[str, str],
    argv: list[str],
    canonical_argv_sha256: str,
    receipt_namespace_consumed: bool,
) -> dict[str, str]:
    """Pure fail-closed admission; it performs no writes or process execution."""

    if set(authority) != {"schema_id", "authorization", "authorization_sha256"}:
        raise RuntimeError("execution authority envelope fields malformed or unknown")
    if authority.get("schema_id") != AUTHORITY_SCHEMA:
        raise RuntimeError("execution authority envelope schema mismatch")
    authorization = authority.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != AUTHORIZATION_FIELDS:
        raise RuntimeError("required execution authority field malformed, missing, or unknown")
    if not HEX_64.fullmatch(supplied_authority_sha256):
        raise RuntimeError("supplied execution authority hash malformed")
    if authority_file_sha256 != supplied_authority_sha256:
        raise RuntimeError("execution authority file hash mismatch")
    if authority.get("authorization_sha256") != authority_sha256(authorization):
        raise RuntimeError("execution authority inner seal mismatch")
    if authorization["schema_id"] != AUTHORIZATION_SCHEMA:
        raise RuntimeError("Human operational authorization schema mismatch")
    source_sha = authorization["authorization_source_sha256"]
    if not isinstance(source_sha, str) or not HEX_64.fullmatch(source_sha):
        raise RuntimeError("Human operational authorization source hash malformed")
    if source_sha in {FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256, FN_SPENT_AUTHORIZATION_SHA256}:
        raise RuntimeError("non-operational or already-spent Human authorization prohibited")
    expected_authorization = {
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorized_generation_identity": GENERATION_IDENTITY,
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_materialization_sha256": MATERIALIZATION_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": ADAPTER_SHA256,
        "authorized_fk_adapter_sha256": FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_attempt_operational_attempt_limit": 1,
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
    for field, expected in expected_authorization.items():
        if authorization[field] != expected:
            raise RuntimeError(f"execution authority binding mismatch: {field}")
    if not isinstance(observed_head, str) or not HEX_40.fullmatch(observed_head):
        raise RuntimeError("observed repository HEAD malformed")
    if not isinstance(observed_tree, str) or not HEX_40.fullmatch(observed_tree):
        raise RuntimeError("observed repository tree malformed")
    if authorization["authorized_repository_head"] != observed_head:
        raise RuntimeError("committed repository HEAD not authorized")
    if authorization["authorized_repository_tree"] != observed_tree:
        raise RuntimeError("committed repository tree not authorized")
    if not anchor_is_ancestor:
        raise RuntimeError("committed constitutional anchor not in repository ancestry")
    if not repository_clean:
        raise RuntimeError("repository state is not clean")
    if set(observed_asset_sha256) != set(EXPECTED_ASSET_SHA256):
        raise RuntimeError("asset observation set incomplete or unknown")
    for path, expected_sha in EXPECTED_ASSET_SHA256.items():
        if observed_asset_sha256[path] != expected_sha:
            raise RuntimeError(f"exact asset binding mismatch: {path}")
    if canonical_argv_sha256 != CANONICAL_ARGV_SHA256:
        raise RuntimeError("canonical QEMU argv binding mismatch")
    if not isinstance(argv, list) or not argv or argv[0] != "/usr/bin/qemu-system-x86_64":
        raise RuntimeError("exact QEMU argv invalid")
    if argv.count("-nic") != 1 or argv[argv.index("-nic") + 1] != "none":
        raise RuntimeError("no-network QEMU vector invalid")
    if receipt_namespace_consumed:
        raise RuntimeError("FM one-shot receipt namespace already consumed")
    return {
        "result": "ADMIT_TO_BOOT_BOUNDARY_ONLY",
        "authorized_repository_head": observed_head,
        "authorized_repository_tree": observed_tree,
        "constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "execution_authority_file_sha256": authority_file_sha256,
        "human_authorization_source_sha256": source_sha,
    }


def asset_observations(repository_root: Path) -> dict[str, str]:
    observations: dict[str, str] = {}
    for path in EXPECTED_ASSET_SHA256:
        target = Path(path) if Path(path).is_absolute() else repository_root / path
        observations[path] = sha256_path(target)
    return observations


def constitutional_anchor_is_ancestor(repository_root: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", CONSTITUTIONAL_ANCHOR_HEAD, "HEAD"],
        cwd=repository_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def receipt(*, phase: str, argv: list[str], digest: str, vector_sha256: str,
            executable_sha256: str, started_ns: int, completed_ns: int | None,
            exit_status: int | None, admission: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_id": f"G77_256FM_B1_{phase}_EXECUTED_QEMU_ARGV_RECEIPT_V1",
        "generation_identity": GENERATION_IDENTITY,
        "authorized_repository_head": admission["authorized_repository_head"],
        "authorized_repository_tree": admission["authorized_repository_tree"],
        "constitutional_anchor_head": admission["constitutional_anchor_head"],
        "execution_authority_file_sha256": admission["execution_authority_file_sha256"],
        "human_authorization_source_sha256": admission["human_authorization_source_sha256"],
        "candidate_sha256": CANDIDATE_SHA256,
        "adapter_sha256": ADAPTER_SHA256,
        "canonicalizer": {
            "path": CANONICALIZER,
            "sha256": CANONICALIZER_SHA256,
            "algorithm": "SHA256_DOMAIN_U64BE_ARGC_REPEATED_U64BE_UTF8_BYTE_LENGTH_AND_BYTES",
        },
        "vector": {
            "path": VECTOR,
            "file_sha256": vector_sha256,
            "canonical_argv_sha256": digest,
            "argv": argv,
        },
        "direct_call_site": "subprocess.run(argv, check=False)",
        "executable_path": argv[0],
        "executable_sha256": executable_sha256,
        "started_unix_ns": started_ns,
        "completed_unix_ns": completed_ns,
        "process_exit_status": exit_status,
        "execution_attempt_count": 1,
        "automatic_retry_count": 0,
        "receipt_is_authority": False,
        "auto_continuable": False,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-authority", required=True, type=Path)
    parser.add_argument("--execution-authority-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path.cwd().resolve()
    pre_path = repository_root / PRE_RECEIPT
    post_path = repository_root / POST_RECEIPT
    consumable_paths = [repository_root / path for path in (
        PRE_RECEIPT, POST_RECEIPT, RAW_EXECUTION, EXECUTION_SEAL, TEARDOWN_SEAL,
    )]
    argv = json.loads((repository_root / VECTOR).read_text(encoding="utf-8"))
    canonicalizer = load_canonicalizer(repository_root)
    digest = canonicalizer.argv_sha256(argv)
    vector_sha = sha256_path(repository_root / VECTOR)
    authority, authority_file_sha = load_authority(arguments.execution_authority.resolve())
    admission = validate_execution_admission(
        authority=authority,
        authority_file_sha256=authority_file_sha,
        supplied_authority_sha256=arguments.execution_authority_sha256,
        observed_head=git(repository_root, "rev-parse", "HEAD"),
        observed_tree=git(repository_root, "rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=constitutional_anchor_is_ancestor(repository_root),
        repository_clean=git(repository_root, "status", "--porcelain") == "",
        observed_asset_sha256=asset_observations(repository_root),
        argv=argv,
        canonical_argv_sha256=digest,
        receipt_namespace_consumed=any(path.exists() for path in consumable_paths),
    )
    executable_sha = sha256_path(Path(argv[0]))
    started = time.time_ns()
    write_atomic(pre_path, receipt(
        phase="PRE", argv=argv, digest=digest, vector_sha256=vector_sha,
        executable_sha256=executable_sha, started_ns=started,
        completed_ns=None, exit_status=None, admission=admission,
    ))
    status = 255
    try:
        result = subprocess.run(argv, check=False)
        status = result.returncode
    finally:
        completed = time.time_ns()
        write_atomic(post_path, receipt(
            phase="POST", argv=argv, digest=digest, vector_sha256=vector_sha,
            executable_sha256=executable_sha, started_ns=started,
            completed_ns=completed, exit_status=status, admission=admission,
        ))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
