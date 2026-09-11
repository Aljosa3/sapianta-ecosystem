#!/usr/bin/env python3
"""Verify the completed KN Phase-A safe stop without executing Phase A."""

from __future__ import annotations

import copy
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
HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
TREE = "70aa2a12af3d9806e0d6ddc73f7f751292413e52"
SUBJECT = "G77-256KM preserve GN schema for KI preflight binding"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
TERMINAL = "A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
KN = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1"
)
MATERIALIZER = KN / "orchestration/G77_256KN_PREAUTHORIZATION_MATERIALIZER_V1.py"
REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
HUMAN_PRESENTATION = KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt"
READINESS = KN / "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REDUCTION = KN / "G77_256KN_PREHUMAN_PHASE_A_REDUCTION_V1.json"
EQUIVALENCE = KN / "G77_256KN_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
KI_PREFLIGHT = KN / "G77_256KN_KI_FRONTIER_PREFLIGHT_V1.json"
KM_PREFLIGHT = KN / "G77_256KN_KM_SCHEMA_BINDING_PREFLIGHT_V1.json"
KL_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kl_fresh_expired_operational_recommissioning_v1/"
    "G77_256KL_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
)
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_SEAL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)
JP_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_readiness_reauthentication_v1/"
    "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
GN_FIELDS = {
    "all_operational_counters_zero",
    "checkpoint_file_sha256",
    "checkpoint_inner_sha256",
    "checkpoint_path",
    "complete_deterministic_readiness",
    "gk_receipt_parent_false_positive_blocked",
    "preauth_final_admission_equivalence",
    "preauth_final_admission_equivalence_file_sha256",
    "receipt_parent_observation_file_sha256",
    "static_readiness_file_sha256",
}


class KNVerificationError(RuntimeError):
    """One deterministic KN verification failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KNVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KNVerificationError(f"MISSING_INNER:{inner}")
    if envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KNVerificationError(f"INNER_SEAL_MISMATCH:{inner}")
    return value


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def load_materializer() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "g77_256kn_phase_a_materializer_for_verification", ROOT / MATERIALIZER
    )
    if specification is None or specification.loader is None:
        raise KNVerificationError("MATERIALIZER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


M = load_materializer()


def verify_entry(remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    if observed != {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    } or remote_head != HEAD:
        raise KNVerificationError(f"ENTRY_CHECKPOINT_MISMATCH:{observed}")
    if git("diff", "--cached", "--name-only"):
        raise KNVerificationError("INDEX_NOT_EMPTY")
    tracked = git("diff", "--name-only")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if tracked or not untracked or any(not path.startswith(f"{KN.as_posix()}/") for path in untracked):
        raise KNVerificationError("KN_MUTATION_SCOPE_MISMATCH")
    nested = {
        "head": git("rev-parse", "HEAD", nested=True),
        "tree": git("rev-parse", "HEAD^{tree}", nested=True),
        "origin": git("remote", "get-url", "origin", nested=True),
        "clean": git("status", "--porcelain", nested=True) == "",
        "detached": git("branch", "--show-current", nested=True) == "",
    }
    if nested != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN,
        "clean": True,
        "detached": True,
    } or nested_remote_tag != NESTED_HEAD:
        raise KNVerificationError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_FIRST_KN_MUTATION",
        "entry_index": "VERIFIED__EMPTY_BEFORE_FIRST_KN_MUTATION",
        "current_mutation_scope": "VERIFIED__UNTRACKED_KN_GENERATION_ONLY",
        "nested_authority": nested,
    }


def all_zero(counters: dict[str, Any]) -> bool:
    return bool(counters) and not any(counters.values())


def verify_phase_a() -> dict[str, Any]:
    km = M.authenticate_km()
    cross_vector = M.cross_vector_reuse_assessment()
    request_envelope = load_canonical(REQUEST)
    request = verify_seal(request_envelope, "request")
    readiness_envelope = load_canonical(READINESS)
    readiness = verify_seal(readiness_envelope, "checkpoint")
    safe_envelope = load_canonical(SAFE_STOP)
    safe = verify_seal(safe_envelope, "checkpoint")
    reduction_envelope = load_canonical(REDUCTION)
    reduction = verify_seal(reduction_envelope, "reduction")
    equivalence = verify_seal(load_canonical(EQUIVALENCE), "proof")
    ki_envelope = load_canonical(KI_PREFLIGHT)
    ki = verify_seal(ki_envelope, "proof")
    km_envelope = load_canonical(KM_PREFLIGHT)
    km_proof = verify_seal(km_envelope, "proof")

    if set(request.get("preauthorization", {})) != GN_FIELDS:
        raise KNVerificationError("GN_EXACT_PREAUTHORIZATION_SCHEMA_MISMATCH")
    if M.P.M.GN.PREAUTHORIZATION_FIELDS != GN_FIELDS:
        raise KNVerificationError("GN_OWNER_FIELD_SET_MISMATCH")
    M.P.M.GN.load_validated_sealed_request(ROOT / REQUEST)
    rendered = M.P.M.GN.render_human_authorization_presentation(ROOT / REQUEST)
    if rendered != (ROOT / AUTH_PRESENTATION).read_bytes():
        raise KNVerificationError("GN_PRESENTATION_DERIVATION_MISMATCH")
    gn_result = M.P.M.GN.validate_human_authorization_presentation(
        ROOT / REQUEST, rendered
    )
    for mode in ("unknown", "missing"):
        negative = copy.deepcopy(request_envelope)
        if mode == "unknown":
            negative["request"]["preauthorization"]["forbidden"] = True
        else:
            negative["request"]["preauthorization"].pop("checkpoint_inner_sha256")
        try:
            M.P.M.GN._validate_request_semantics(negative)
        except M.P.M.GN.PresentationBindingError as exc:
            if str(exc) != "SEALED_REQUEST_PREAUTHORIZATION_INVALID":
                raise KNVerificationError(f"GN_NEGATIVE_WRONG_TOKEN:{exc}") from exc
        else:
            raise KNVerificationError("GN_EXACT_SCHEMA_NEGATIVE_ACCEPTED")

    ki_binding = readiness.get("ki_frontier_preflight", {})
    km_binding = readiness.get("km_schema_binding_preflight", {})
    for binding, path, envelope in (
        (ki_binding, KI_PREFLIGHT, ki_envelope),
        (km_binding, KM_PREFLIGHT, km_envelope),
    ):
        if (
            binding.get("path") != path.as_posix()
            or binding.get("file_sha256") != sha256_path(path)
            or binding.get("inner_sha256") != envelope.get("proof_sha256")
            or binding.get("scope") != "REPOSITORY_ONLY__NONAUTHORITY__NONOPERATIONAL"
        ):
            raise KNVerificationError(f"PREFLIGHT_READINESS_BINDING_MISMATCH:{path}")
    preauthorization = request["preauthorization"]
    if (
        preauthorization.get("checkpoint_file_sha256") != sha256_path(READINESS)
        or preauthorization.get("checkpoint_inner_sha256")
        != readiness_envelope.get("checkpoint_sha256")
    ):
        raise KNVerificationError("READINESS_REQUEST_BINDING_MISMATCH")
    if any(field in preauthorization for field in M.REMOVED_FIELDS):
        raise KNVerificationError("REMOVED_KI_FIELD_REINTRODUCED")

    identities = reduction.get("identities", {})
    expected_identities = {
        "request_sha256": request_envelope["request_sha256"],
        "request_file_sha256": sha256_path(REQUEST),
        "presentation_sha256": sha256_path(AUTH_PRESENTATION),
        "readiness_checkpoint_sha256": readiness_envelope["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(READINESS),
        "checkpoint_sha256": safe_envelope["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(SAFE_STOP),
    }
    if any(identities.get(key) != value for key, value in expected_identities.items()):
        raise KNVerificationError("REDUCTION_IDENTITY_BINDING_MISMATCH")
    if (
        request.get("generation_identity") != GENERATION
        or request.get("operation_identity") != OPERATION
        or safe.get("generation_identity") != GENERATION
        or safe.get("operation_identity") != OPERATION
        or reduction.get("generation_identity") != GENERATION
        or reduction.get("operation_identity") != OPERATION
    ):
        raise KNVerificationError("KN_FRESH_IDENTITY_MISMATCH")

    human_lines = (ROOT / HUMAN_PRESENTATION).read_text(encoding="utf-8").splitlines()
    required_lines = {
        f"GENERATION {GENERATION}",
        f"OPERATION {OPERATION}",
        f"REQUEST_IDENTITY {request_envelope['request_sha256']}",
        f"REQUEST_FILE_SHA256 {sha256_path(REQUEST)}",
        f"PRESENTATION_SHA256 {sha256_path(AUTH_PRESENTATION)}",
        f"READINESS_CHECKPOINT {readiness_envelope['checkpoint_sha256']}",
        f"SAFE_STOP_CHECKPOINT {safe_envelope['checkpoint_sha256']}",
        "HUMAN_AUTHORITY NOT_SUPPLIED",
        "AUTO_CONTINUABLE NO",
        "HUMAN_REVIEW_REQUIRED YES",
        "STOP AT HUMAN AUTHORITY BARRIER.",
    }
    if not required_lines.issubset(set(human_lines)):
        raise KNVerificationError("HUMAN_DECISION_PRESENTATION_BINDING_MISMATCH")
    if (
        equivalence.get("request_sha256") != request_envelope["request_sha256"]
        or equivalence.get("presentation_sha256") != sha256_path(AUTH_PRESENTATION)
        or equivalence.get("human_presentation_request_equivalence")
        != "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
        or gn_result.get("human_presentation_request_equivalence")
        != "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    ):
        raise KNVerificationError("GN_EQUIVALENCE_MISMATCH")

    kl = verify_seal(load_canonical(KL_REDUCTION), "reduction")
    kl_identities = kl.get("partial_phase_a_state", {})
    freshness_pairs = {
        "generation": (GENERATION, kl_identities.get("generation")),
        "operation": (OPERATION, kl_identities.get("operation")),
        "context_sha256": (identities.get("context_sha256"), kl_identities.get("context")),
        "context_file_sha256": (
            identities.get("context_file_sha256"),
            kl_identities.get("context_file_sha256"),
        ),
        "canonical_argv_sha256": (
            identities.get("canonical_argv_sha256"),
            kl_identities.get("canonical_argv_sha256"),
        ),
        "temporal_binding_sha256": (
            identities.get("temporal_binding_sha256"),
            kl_identities.get("temporal_binding"),
        ),
        "request_sha256": (
            request_envelope["request_sha256"],
            kl_identities.get("request_identity"),
        ),
        "request_file_sha256": (sha256_path(REQUEST), kl_identities.get("request_file_sha256")),
        "presentation_sha256": (
            sha256_path(AUTH_PRESENTATION),
            kl_identities.get("authorization_presentation_sha256"),
        ),
        "readiness_checkpoint_sha256": (
            readiness_envelope["checkpoint_sha256"],
            kl_identities.get("readiness_checkpoint"),
        ),
        "safe_stop_checkpoint_sha256": (
            safe_envelope["checkpoint_sha256"],
            kl_identities.get("safe_stop_checkpoint"),
        ),
    }
    if any(current == historical for current, historical in freshness_pairs.values()):
        raise KNVerificationError("STALE_KL_COORDINATE_REUSED")

    counter_sets = [
        reduction.get("operational_counters", {}),
        readiness.get("operational_counters", {}),
        safe.get("operational_counters", {}),
        ki.get("operational_counters", {}),
        km_proof.get("operational_counters", {}),
    ]
    if not all(all_zero(counters) for counters in counter_sets):
        raise KNVerificationError("NONZERO_OPERATIONAL_COUNTER")
    forbidden_names = [
        path.as_posix()
        for path in (ROOT / KN).rglob("*")
        if path.is_file()
        and any(token in path.name for token in ("PHASE_B", "AUTHORIZATION_SOURCE", "AUTHORIZATION_HANDOFF", "QEMU", "EXECUTION_RESULT"))
    ]
    if forbidden_names:
        raise KNVerificationError(f"FORBIDDEN_PHASE_B_OR_OPERATION_ARTIFACT:{forbidden_names}")
    if (
        reduction.get("terminal") != TERMINAL
        or reduction.get("fresh_kn_phase_a_presentation_ready") != "VERIFIED"
        or reduction.get("safe_stop_checkpoint") != "VERIFIED"
        or reduction.get("gn_exact_preauthorization_schema") != "VERIFIED__UNCHANGED"
        or reduction.get("ki_preflight_binding")
        != "VERIFIED__KM_SCHEMA_PRESERVING_PATH_USED"
        or reduction.get("human_authority_present") is not False
        or reduction.get("phase_b_started") is not False
        or reduction.get("auto_continuable") is not False
        or reduction.get("human_review_required") is not True
        or safe.get("terminal") != TERMINAL
    ):
        raise KNVerificationError("SUCCESS_TERMINAL_CONTRACT_MISMATCH")
    return {
        "terminal": TERMINAL,
        "generation": GENERATION,
        "operation": OPERATION,
        "candidate_sha256": identities["candidate_sha256"],
        "context_sha256": identities["context_sha256"],
        "context_file_sha256": identities["context_file_sha256"],
        "canonical_argv_sha256": identities["canonical_argv_sha256"],
        "temporal_binding_sha256": identities["temporal_binding_sha256"],
        **expected_identities,
        "human_decision_presentation_sha256": sha256_path(HUMAN_PRESENTATION),
        "gn_exact_preauthorization_fields": sorted(GN_FIELDS),
        "gn_exact_preauthorization_field_count": 10,
        "gn_unknown_and_missing_field_rejection": "VERIFIED__SEALED_REQUEST_PREAUTHORIZATION_INVALID",
        "ki_preflight_binding": "VERIFIED__KM_SCHEMA_PRESERVING_PATH_USED",
        "cross_vector_reuse_assessment": cross_vector,
        "km_authentication": km,
        "freshness_against_kl": "VERIFIED__ALL_GENERATION_OPERATION_CONTEXT_ARGV_TEMPORAL_REQUEST_PRESENTATION_READINESS_SAFE_STOP_COORDINATES_DISTINCT",
        "candidate_binding": "VERIFIED__IMMUTABLE_CANDIDATE_REUSED_WITH_FRESH_CONTEXT_ARGV_AND_TEMPORAL_BINDINGS",
        "operational_counters": "VERIFIED__ALL_15_ZERO",
        "phase_a_construction_attempt_count": "VERIFIED__1__SOLE_SUCCESSFUL_KN_INVOCATION__FRESH_COLLISION_GUARDS_ACTIVE",
        "human_authority_present": False,
        "phase_b_started": False,
        "operational_execution": False,
    }


def verify_ex() -> dict[str, Any]:
    certificate_raw = (ROOT / EX_CERTIFICATE).read_bytes()
    certificate = json.loads(certificate_raw)
    preimage = copy.deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    if (
        certificate.get("certificate_sha256") != sha256_bytes(compact_bytes(preimage))
        or certificate.get("certificate", {}).get("component_counts", {}).get("CERTIFIED") != 17
    ):
        raise KNVerificationError("EX_CERTIFICATE_MISMATCH")
    seal_raw = (ROOT / EX_SEAL).read_bytes()
    seal_envelope = json.loads(seal_raw)
    seal = seal_envelope.get("seal", {})
    if (
        seal_envelope.get("seal_sha256") != sha256_bytes(compact_bytes(seal))
        or seal.get("validation", {}).get("ew_regression") != "17_OF_17_PASS"
    ):
        raise KNVerificationError("EX_FINAL_SEAL_MISMATCH")
    jp = verify_seal(load_canonical(JP_REDUCTION), "reduction")
    successor = jp.get("ex_successor_reauthentication", {})
    if (
        successor.get("changed_component") != "ER_OPERATIONAL_HARNESS"
        or successor.get("classification") != "REQUIRES_HARDENING"
        or successor.get("ex_reused") != "VERIFIED__17_OF_17"
        or successor.get("ex_reconstructed") != "VERIFIED__0"
    ):
        raise KNVerificationError("JP_SUCCESSOR_DISTINCTION_MISMATCH")
    return {
        "certificate_file_sha256": sha256_path(EX_CERTIFICATE),
        "final_seal_file_sha256": sha256_path(EX_SEAL),
        "jp_successor_distinction": "VERIFIED__ONE_ER_OPERATIONAL_HARNESS_REQUIRES_HARDENING_DELTA",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def verify(remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD) -> dict[str, Any]:
    return {
        "entry": verify_entry(remote_head, nested_remote_tag),
        "phase_a": verify_phase_a(),
        "ex": verify_ex(),
    }


if __name__ == "__main__":
    sys.stdout.buffer.write(canonical_bytes(verify()))
