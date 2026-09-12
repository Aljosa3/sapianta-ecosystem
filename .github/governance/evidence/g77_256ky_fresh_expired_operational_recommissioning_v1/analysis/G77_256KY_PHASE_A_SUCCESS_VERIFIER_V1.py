#!/usr/bin/env python3
"""Independently verify the KY Phase-A Human-decision barrier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HEAD = "d19208af9d9633c764838399e5a86a441e9386ef"
TREE = "40207213a9359f536f9e6380c113c67f5ac6ab3f"
SUBJECT = "G77-256KX bind runtime export custody traversal"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCESTRY = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__KY_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__"
    "NO_HUMAN_AUTHORITY__NO_HANDOFF__NO_BINDING__NO_CONSUMPTION__"
    "NO_PHASE_B__NO_OPERATION"
)
GENERATION = "G77_256KY_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
COMMISSION = "G77-256KY_FRESH_CURRENT_HEAD_EXPIRED_OPERATIONAL_RECOMMISSIONING_V1"
OPERATION = "G77_256KY_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
PURPOSE = (
    "Perform exactly one future fresh Human-authorized EXPIRED operational "
    "attempt after the KX runtime-export custody repair, to observe whether "
    "EXPIRED is denied before P11 entry."
)
KY = Path(
    ".github/governance/evidence/"
    "g77_256ky_fresh_expired_operational_recommissioning_v1"
)
KW = Path(
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1"
)
MATERIALIZER = KY / "orchestration/G77_256KY_PREAUTHORIZATION_MATERIALIZER_V1.py"
BASE_VERIFIER = KW / "analysis/G77_256KW_PHASE_A_SUCCESS_VERIFIER_V1.py"
BASE_VERIFIER_SHA256 = "88f865b1c2d65e7b3b8f5149a5bc3ffc093b740590b2796e30da55afb294614d"
REQUEST = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
HUMAN_PRESENTATION = KY / "G77_256KY_HUMAN_DECISION_PRESENTATION_V1.txt"
READINESS = KY / "G77_256KY_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KY / "G77_256KY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REDUCTION = KY / "G77_256KY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
CONTEXT = KY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE_SOURCE = KY / (
    "candidate_source/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)


class KYVerificationError(RuntimeError):
    """One deterministic fail-closed KY verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def load_adapted_base_verifier() -> ModuleType:
    path = ROOT / BASE_VERIFIER
    raw = path.read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{HEAD}:{BASE_VERIFIER.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if raw != committed or sha256_bytes(raw) != BASE_VERIFIER_SHA256:
        raise KYVerificationError("COMMITTED_KW_VERIFIER_MISMATCH")
    source = raw.decode("utf-8").replace("KW", "KY").replace("kw", "ky")
    source = source.replace("681538ccd9b6faaeebff15d96881134eaef00d7e", HEAD)
    source = source.replace("53164b7f60d982727bebd9a5c77d5688ee283ade", TREE)
    source = source.replace("G77-256KV localize fresh current-head authority lifecycle", SUBJECT)
    source = source.replace("EVIDENCE_OR_REPORTING_DEFECT", "PROOF_GAP")
    source = source.replace(
        '"NO_HUMAN_AUTHORITY__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"',
        '"NO_HUMAN_AUTHORITY__NO_HANDOFF__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"',
    )
    module = ModuleType("g77_256ky_adapted_phase_a_verifier")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


A = load_adapted_base_verifier()


def verify_entry(
    remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD
) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    }
    if observed != expected or remote_head != HEAD:
        raise KYVerificationError(f"ENTRY_CHECKPOINT_MISMATCH:{observed}")
    if git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise KYVerificationError("TRACKED_OR_INDEX_MUTATION_PRESENT")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if not untracked or any(not path.startswith(KY.as_posix() + "/") for path in untracked):
        raise KYVerificationError("BOUNDED_MUTATION_SCOPE_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCESTRY, HEAD], cwd=ROOT
    ).returncode != 0:
        raise KYVerificationError("STABLE_ANCESTRY_MISMATCH")
    nested = {
        "origin": git("remote", "get-url", "origin", nested=True),
        "head": git("rev-parse", "HEAD", nested=True),
        "tree": git("rev-parse", "HEAD^{tree}", nested=True),
        "clean": git("status", "--porcelain", nested=True) == "",
        "detached": git("branch", "--show-current", nested=True) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", nested=True),
    }
    if nested != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
    } or nested_remote_tag != NESTED_HEAD:
        raise KYVerificationError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "stable_ancestry": "VERIFIED",
        "index_empty": True,
        "worktree_scope": "VERIFIED__ONLY_UNTRACKED_KY_PHASE_A_ARTIFACTS",
        "nested_authority": nested,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_TAG_LS_REMOTE",
    }


def verify_ky_phase_a() -> dict[str, Any]:
    phase = A.verify_phase_a()
    reduction = A.verify_seal(A.load_canonical(REDUCTION), "reduction")
    context = A.load_canonical(CONTEXT)
    request = A.verify_seal(A.load_canonical(REQUEST), "request")
    kx = A.M.authenticate_kx()
    if (
        reduction.get("kx_repair_authentication") != kx
        or reduction.get("failure_novelty_and_convergence_check", {}).get("failure_class") != "PROOF_GAP"
        or reduction.get("failure_novelty_and_convergence_check", {}).get("new_capability_required") != "VERIFIED__NO"
        or reduction.get("proof_yield", {}).get("new_human_decision_presentation_count") != "VERIFIED__1"
        or reduction.get("proof_yield", {}).get("ex_reconstruction_count") != "VERIFIED__0"
    ):
        raise KYVerificationError("KX_FRONTIER_OR_PROOF_YIELD_MISMATCH")
    kw_context = A.load_canonical(KW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    kw_request = A.verify_seal(
        A.load_canonical(KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"),
        "request",
    )
    current = {
        context["candidate_manifest_sha256"],
        context["context_sha256"],
        context["canonical_argv_sha256"],
        request["operation_identity"],
    }
    historical = {
        kw_context["candidate_manifest_sha256"],
        kw_context["context_sha256"],
        kw_context["canonical_argv_sha256"],
        kw_request["operation_identity"],
    }
    if current & historical:
        raise KYVerificationError("KW_IDENTITY_OR_DIGEST_REUSED")
    expected_lines = {
        f"PURPOSE {PURPOSE}",
        f"CONTEXT_SHA256 {context['context_sha256']}",
        f"CONTEXT_FILE_SHA256 {sha256_path(CONTEXT)}",
        f"CANONICAL_ARGV_SHA256 {context['canonical_argv_sha256']}",
        f"TEMPORAL_BINDING_SHA256 {sha256_bytes(canonical_bytes(context['preclaim_temporal_binding']))}",
        "REPAIR_RETRY_LIMIT 0",
        "KY_E05_CREDIT VERIFIED__0",
    }
    presentation_lines = set((ROOT / HUMAN_PRESENTATION).read_text(encoding="utf-8").splitlines())
    if not expected_lines.issubset(presentation_lines):
        raise KYVerificationError("KY_HUMAN_DECISION_PRESENTATION_MISMATCH")
    forbidden_tokens = (
        "AUTHORIZATION_SOURCE",
        "AUTHORIZATION_HANDOFF",
        "PRECONSUMPTION_INVOCATION_BINDING",
        "PHASE_B",
        "EXECUTION_RESULT",
    )
    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / KY).rglob("*")
        if path.is_file() and any(token in path.name for token in forbidden_tokens)
    ]
    if forbidden:
        raise KYVerificationError(f"FORBIDDEN_PHASE_B_ARTIFACT:{forbidden}")
    return {
        **phase,
        "commission": COMMISSION,
        "purpose": PURPOSE,
        "vector": "EXPIRED",
        "freshness_against_kw": "VERIFIED__ALL_REQUIRED_IDENTITIES_AND_DIGESTS_DISTINCT",
        "failure_class": "PROOF_GAP",
        "kx_repair_authentication": "VERIFIED",
        "human_decision_presentation_sha256": sha256_path(HUMAN_PRESENTATION),
    }


def verify(
    remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD
) -> dict[str, Any]:
    return {
        "entry": verify_entry(remote_head, nested_remote_tag),
        "successful_precedents": A.verify_successful_precedents(),
        "phase_a": verify_ky_phase_a(),
        "canonical_artifacts": A.verify_all_json(),
    }


if __name__ == "__main__":
    sys.stdout.buffer.write(canonical_bytes(verify()))
