#!/usr/bin/env python3
"""Verify JZ's repository-only FM authority-digest invocation binding.

The formalizer reads committed JY history and the JZ repository artifacts.  It
does not create or consume Human authority, invoke FM, write PRE, or start a
process, QEMU, a VM, ER, or P11.
"""

from __future__ import annotations

import argparse
import ast
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
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "673b8ce72c09252c9cf462ac4c96878a8dbad06c"
ENTRY_TREE = "3ca4f1f0a695edf97680e5ebc973a1a52029860d"
ENTRY_SUBJECT = "G77-256JY localize FM authority digest handoff blocker"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

JZ = Path(
    ".github/governance/evidence/"
    "g77_256jz_fm_authority_digest_handoff_repair_v1"
)
JY = Path(".github/governance/evidence/g77_256jy_expired_operational_v1")
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = JY / (
    "live_binding/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
JY_FAILURE = JY / "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1.json"
JY_CLOSURE = JY / "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_V1.json"
BINDING = JZ / "G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
REDUCTION = JZ / "G77_256JZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JZ / "G77_256JZ_G48_IMPLEMENTATION_REPORT_V1.md"

HUMAN_SOURCE_SHA256 = (
    "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
)
AUTHORITY_SHA256 = (
    "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"
)
TRUNCATED_SHA256 = (
    "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9"
)
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
FM_ENTRY_SHA256 = "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469"
TERMINAL = (
    "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_"
    "BINDING_REPOSITORY_VERIFIED"
)


class JZError(RuntimeError):
    """One deterministic fail-closed JZ verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise JZError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(relative: Path) -> dict[str, Any]:
    raw = (ROOT / relative).read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JZError(f"NONCANONICAL_JSON__{relative}")
    return value


def load_envelope(relative: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(relative)
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != hashlib.sha256(
        canonical_bytes(value)
    ).hexdigest():
        raise JZError(f"INNER_SEAL_INVALID__{relative}")
    return value


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JZError(f"MODULE_UNAVAILABLE__{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def sha256_path(relative: Path) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def authenticate_entry(remote_head: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "repository": str(ROOT),
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_head": ENTRY_HEAD,
        "index_empty": True,
    }
    if observed != expected:
        raise JZError("EXACT_REMOTE_RATIFIED_JY_ENTRY_MISMATCH")
    allowed_fm = f"M {FM.as_posix()}"
    allowed_jz = f"?? {JZ.as_posix()}/"
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        normalized = line.lstrip()
        if normalized != allowed_fm and not normalized.startswith(allowed_jz):
            raise JZError(f"JZ_BOUNDED_WORKTREE_SCOPE_VIOLATION__{line}")

    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--exact-match", "--tags", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
    }:
        raise JZError("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "worktree_clean_at_entry": True,
        "direct_remote_equality": "VERIFIED__READ_ONLY_LS_REMOTE_AT_ENTRY",
        "nested_authority": nested_state | {
            "pinned": True,
            "remote_tag_equal": "VERIFIED__READ_ONLY_LS_REMOTE_AT_ENTRY",
        },
    }


def authenticate_jy() -> dict[str, Any]:
    for relative in (HANDOFF, JY_FAILURE, JY_CLOSURE):
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != (ROOT / relative).read_bytes():
            raise JZError(f"JY_COMMITTED_BYTES_MISMATCH__{relative.name}")
    failure = load_envelope(JY_FAILURE, "failure")
    closure = load_envelope(JY_CLOSURE, "closure")
    expected_counters = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 1,
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
    localization = closure.get("failure_localization", {})
    finality = closure.get("authority_finality", {})
    if (
        closure.get("terminal")
        != "M__JY_TERMINAL_FAILURE_REDUCED_TO_CALLER_CONSTRUCTED_TRUNCATED_FM_AUTHORITY_DIGEST_ARGUMENT_BEFORE_PRE"
        or closure.get("operational_counters") != expected_counters
        or finality.get("human_source_sha256") != HUMAN_SOURCE_SHA256
        or finality.get("expected_authority_digest") != AUTHORITY_SHA256
        or not finality.get("consumed")
        or finality.get("reusable") is not False
        or finality.get("transferable") is not False
        or localization.get("expected_authority_digest") != AUTHORITY_SHA256
        or localization.get("supplied_authority_digest") != TRUNCATED_SHA256
        or localization.get("exact_difference") != "FINAL_HEX_CHARACTER_D_OMITTED"
        or localization.get("underlying_authority_artifact")
        != "VERIFIED__CORRECT_AND_CANONICAL"
        or localization.get("shell_cli_transport")
        != "VERIFIED__PRESERVED_CALLER_SUPPLIED_63_HEX_LITERAL"
        or localization.get("fm_validation")
        != "VERIFIED__CORRECT_FAIL_CLOSED_HEX_64_REJECTION"
        or failure.get("pre_receipt_exists") is not False
        or sha256_path(HANDOFF) != AUTHORITY_SHA256
    ):
        raise JZError("JY_TERMINAL_EVIDENCE_MISMATCH")
    return {
        "terminal": closure["terminal"],
        "human_source_sha256": HUMAN_SOURCE_SHA256,
        "expected_authority_digest": AUTHORITY_SHA256,
        "supplied_authority_digest": TRUNCATED_SHA256,
        "exact_difference": "FINAL_HEX_CHARACTER_D_OMITTED",
        "historical_operational_counters": expected_counters,
        "authority_state": "HISTORICAL__CONSUMED__NONREUSABLE__NONTRANSFERABLE",
    }


def verify_binding() -> dict[str, Any]:
    fm = load_module(FM, "g77_256jz_formalizer_fm")
    expected = fm.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    observed = load_canonical(BINDING)
    if observed != expected:
        raise JZError("JZ_PRECONSUMPTION_BINDING_MISMATCH")
    binding = fm.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=observed,
    )
    digests = {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
        binding["final_fm_argv"][
            binding["final_fm_argv"].index("--execution-authority-sha256") + 1
        ],
    }
    if digests != {AUTHORITY_SHA256}:
        raise JZError("JZ_AUTHORITY_DIGEST_EQUALITY_MISMATCH")
    return binding


def verify_repository_artifacts() -> None:
    reduction = load_envelope(REDUCTION, "reduction")
    if reduction.get("terminal") != TERMINAL:
        raise JZError("JZ_TERMINAL_MISMATCH")
    if any(reduction.get("operational_counters", {}).values()):
        raise JZError("JZ_OPERATIONAL_COUNTER_NONZERO")
    if reduction.get("bindings", {}).get("fm_jz_sha256") != sha256_path(FM):
        raise JZError("JZ_FM_BINDING_MISMATCH")
    if reduction.get("bindings", {}).get("p11_sha256") != sha256_path(P11):
        raise JZError("JZ_P11_BINDING_MISMATCH")
    if reduction.get("capability", {}).get("binding_file_sha256") != sha256_path(
        BINDING
    ):
        raise JZError("JZ_INVOCATION_BINDING_FILE_HASH_MISMATCH")
    if reduction.get("e05") != {
        "state": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
    }:
        raise JZError("JZ_E05_STATE_MISMATCH")
    if reduction.get("reuse") != {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }:
        raise JZError("JZ_EX_REUSE_MISMATCH")
    if reduction.get("architecture") != {
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "production_mutation_count": 1,
        "p11_implementation_mutation_count": 0,
        "production_route_before": 1,
        "production_route_after": 1,
        "production_route_delta": 0,
    }:
        raise JZError("JZ_ARCHITECTURAL_DELTA_MISMATCH")
    report = (ROOT / REPORT).read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]:
        raise JZError("G48_EXACT_SIX_H1_MISMATCH")
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    if any(report.count(question) != 1 for question in questions):
        raise JZError("G48_EXACT_FIVE_RIA_QUESTIONS_MISMATCH")
    ast.parse((ROOT / FM).read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    if sha256_path(P11) != P11_SHA256:
        raise JZError("P11_IMPLEMENTATION_MUTATED")
    committed_fm = subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{FM.as_posix()}"], cwd=ROOT
    )
    if hashlib.sha256(committed_fm).hexdigest() != FM_ENTRY_SHA256:
        raise JZError("FM_ENTRY_BYTES_MISMATCH")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", default=ENTRY_HEAD)
    arguments = parser.parse_args()
    authenticate_entry(arguments.remote_head)
    authenticate_jy()
    verify_binding()
    verify_repository_artifacts()
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
