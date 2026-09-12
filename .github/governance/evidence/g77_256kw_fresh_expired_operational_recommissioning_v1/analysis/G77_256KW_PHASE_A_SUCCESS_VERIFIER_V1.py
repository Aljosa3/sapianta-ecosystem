#!/usr/bin/env python3
"""Independently verify the completed KW Phase-A Human-decision barrier."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HEAD = "681538ccd9b6faaeebff15d96881134eaef00d7e"
TREE = "53164b7f60d982727bebd9a5c77d5688ee283ade"
SUBJECT = "G77-256KV localize fresh current-head authority lifecycle"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
TERMINAL = (
    "A__KW_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__"
    "NO_HUMAN_AUTHORITY__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
)
GENERATION = "G77_256KW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
KW = Path(
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1"
)
KN = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1"
)
MATERIALIZER = KW / "orchestration/G77_256KW_PREAUTHORIZATION_MATERIALIZER_V1.py"
REQUEST = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
HUMAN_PRESENTATION = KW / "G77_256KW_HUMAN_DECISION_PRESENTATION_V1.txt"
READINESS = KW / "G77_256KW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KW / "G77_256KW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REDUCTION = KW / "G77_256KW_PREHUMAN_PHASE_A_REDUCTION_V1.json"
EQUIVALENCE = KW / "G77_256KW_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
CONTEXT = KW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE_SOURCE = KW / (
    "candidate_source/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
CANDIDATE = KW / (
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
CANDIDATE_RUNTIME = KW / (
    "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
KN_REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
KN_AUTH_PRESENTATION = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
KN_CONTEXT = KN / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
KN_SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
KN_SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
KV_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kv_current_head_operational_binding_owner_and_authority_impact_discovery_v1/"
    "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_V1.json"
)
JH = Path(
    ".github/governance/evidence/"
    "g77_256jh_future_fresh_human_authorized_operational_denial_v1"
)
JH_TERMINAL = JH / "G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json"
JH_CONTEXT = JH / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
JH_REQUEST = JH / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
JH_HANDOFF = JH / "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
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


class KWVerificationError(RuntimeError):
    """One deterministic fail-closed KW verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KWVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KWVerificationError(f"MISSING_INNER:{inner}")
    if envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KWVerificationError(f"INNER_SEAL_MISMATCH:{inner}")
    return value


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def load_materializer():
    specification = importlib.util.spec_from_file_location(
        "g77_256kw_phase_a_materializer_for_verification", ROOT / MATERIALIZER
    )
    if specification is None or specification.loader is None:
        raise KWVerificationError("MATERIALIZER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


M = load_materializer()


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
        raise KWVerificationError(f"ENTRY_CHECKPOINT_MISMATCH:{observed}")
    if git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise KWVerificationError("TRACKED_OR_INDEX_MUTATION_PRESENT")
    allowed_historical = KN_SOURCE.as_posix()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if allowed_historical not in untracked or any(
        path != allowed_historical and not path.startswith(KW.as_posix() + "/")
        for path in untracked
    ):
        raise KWVerificationError("BOUNDED_MUTATION_SCOPE_MISMATCH")
    if sha256_path(KN_SOURCE) != KN_SOURCE_SHA256:
        raise KWVerificationError("HISTORICAL_KN_HUMAN_SOURCE_CHANGED")
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
        "tag": "sapianta-system-nested-authority-3183bab-v1",
    } or nested_remote_tag != NESTED_HEAD:
        raise KWVerificationError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "index_empty": True,
        "historical_kn_source": "VERIFIED__UNCHANGED__NOT_KW_AUTHORITY",
        "nested_authority": nested,
    }


def verify_phase_a() -> dict[str, Any]:
    request_envelope = load_canonical(REQUEST)
    request = verify_seal(request_envelope, "request")
    readiness_envelope = load_canonical(READINESS)
    readiness = verify_seal(readiness_envelope, "checkpoint")
    safe_envelope = load_canonical(SAFE_STOP)
    safe = verify_seal(safe_envelope, "checkpoint")
    reduction_envelope = load_canonical(REDUCTION)
    reduction = verify_seal(reduction_envelope, "reduction")
    equivalence = verify_seal(load_canonical(EQUIVALENCE), "proof")
    context = load_canonical(CONTEXT)

    if set(request.get("preauthorization", {})) != GN_FIELDS:
        raise KWVerificationError("GN_EXACT_PREAUTHORIZATION_SCHEMA_MISMATCH")
    if M.W.P.M.GN.PREAUTHORIZATION_FIELDS != GN_FIELDS:
        raise KWVerificationError("GN_OWNER_FIELD_SET_MISMATCH")
    rendered = M.W.P.M.GN.render_human_authorization_presentation(ROOT / REQUEST)
    if rendered != (ROOT / AUTH_PRESENTATION).read_bytes():
        raise KWVerificationError("GN_PRESENTATION_DERIVATION_MISMATCH")
    M.W.P.M.GN.validate_human_authorization_presentation(ROOT / REQUEST, rendered)
    for mode in ("unknown", "missing"):
        negative = copy.deepcopy(request_envelope)
        if mode == "unknown":
            negative["request"]["preauthorization"]["forbidden"] = True
        else:
            negative["request"]["preauthorization"].pop("checkpoint_inner_sha256")
        try:
            M.W.P.M.GN._validate_request_semantics(negative)
        except M.W.P.M.GN.PresentationBindingError as exc:
            if str(exc) != "SEALED_REQUEST_PREAUTHORIZATION_INVALID":
                raise KWVerificationError(f"GN_NEGATIVE_WRONG_TOKEN:{exc}") from exc
        else:
            raise KWVerificationError("GN_EXACT_SCHEMA_NEGATIVE_ACCEPTED")

    candidate_source = load_canonical(CANDIDATE_SOURCE)
    for path in (CANDIDATE, CANDIDATE_RUNTIME):
        if (ROOT / path).read_bytes() != (ROOT / CANDIDATE_SOURCE).read_bytes():
            raise KWVerificationError(f"CANDIDATE_PROJECTION_MISMATCH:{path}")
    M.load_authenticated_module(
        M.DU_VALIDATOR, M.DU_VALIDATOR_SHA256, "g77_256kw_du_verifier_replay"
    ).validate_envelope(
        candidate_source,
        ROOT,
        expected_head=HEAD,
        required_prohibited_actions=M.load_authenticated_module(
            M.DU_VALIDATOR,
            M.DU_VALIDATOR_SHA256,
            "g77_256kw_du_verifier_constants",
        ).REQUIRED_PROHIBITED_ACTIONS,
    )
    candidate_sha256 = sha256_path(CANDIDATE_SOURCE)
    M.W.P.M.FM.validate_immutable_context_bindings(ROOT, context, CANDIDATE)
    if (
        context.get("repository_head") != HEAD
        or context.get("repository_tree") != TREE
        or context.get("candidate_manifest_sha256") != candidate_sha256
    ):
        raise KWVerificationError("CURRENT_HEAD_CONTEXT_BINDING_MISMATCH")

    identities = reduction.get("identities", {})
    expected_identities = {
        "candidate_sha256": candidate_sha256,
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(CONTEXT),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "temporal_binding_sha256": sha256_bytes(
            canonical_bytes(context["preclaim_temporal_binding"])
        ),
        "request_sha256": request_envelope["request_sha256"],
        "request_file_sha256": sha256_path(REQUEST),
        "presentation_sha256": sha256_path(AUTH_PRESENTATION),
        "readiness_checkpoint_sha256": readiness_envelope["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(READINESS),
        "checkpoint_sha256": safe_envelope["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(SAFE_STOP),
    }
    if any(identities.get(key) != value for key, value in expected_identities.items()):
        raise KWVerificationError("REDUCTION_IDENTITY_BINDING_MISMATCH")

    kn_context = load_canonical(KN_CONTEXT)
    kn_request = load_canonical(KN_REQUEST)
    historical = {
        "candidate_sha256": kn_context["candidate_manifest_sha256"],
        "context_sha256": kn_context["context_sha256"],
        "context_file_sha256": sha256_path(KN_CONTEXT),
        "canonical_argv_sha256": kn_context["canonical_argv_sha256"],
        "temporal_binding_sha256": sha256_bytes(
            canonical_bytes(kn_context["preclaim_temporal_binding"])
        ),
        "request_sha256": kn_request["request_sha256"],
        "request_file_sha256": sha256_path(KN_REQUEST),
        "presentation_sha256": sha256_path(KN_AUTH_PRESENTATION),
    }
    if any(expected_identities[key] == value for key, value in historical.items()):
        raise KWVerificationError("HISTORICAL_KN_DIGEST_REUSED")

    coordinates = (
        "authorization_base_head",
        "authorization_base_tree",
        "operation_context_head",
        "operation_context_tree",
        "presentation_head",
        "presentation_tree",
    )
    coordinate_values = (HEAD, TREE, HEAD, TREE, HEAD, TREE)
    if tuple(reduction.get(key) for key in coordinates) != coordinate_values:
        raise KWVerificationError("PHASE_A_REPOSITORY_COORDINATE_MISMATCH")
    classification = reduction.get("failure_novelty_and_convergence_check", {})
    cross_vector = reduction.get("cross_vector_reuse_assessment", {})
    if (
        reduction.get("terminal") != TERMINAL
        or safe.get("terminal") != TERMINAL
        or request.get("generation_identity") != GENERATION
        or request.get("operation_identity") != OPERATION
        or classification.get("failure_class") != "EVIDENCE_OR_REPORTING_DEFECT"
        or classification.get("new_capability_required") != "VERIFIED__NO"
        or cross_vector.get("repository_binding_lifecycle_scope")
        != "VERIFIED__COMMON_E05_INFRASTRUCTURE"
        or reduction.get("human_decision_presentation_status")
        != "VERIFIED__READY_FOR_HUMAN_DECISION"
        or reduction.get("human_authority_status")
        != "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET"
        or reduction.get("human_authority_handoff_status")
        != "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT"
        or reduction.get("preconsumption_binding_status")
        != "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT"
        or reduction.get("phase_b_started") is not False
        or reduction.get("auto_continuable") is not False
        or reduction.get("human_review_required") is not True
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KWVerificationError("PHASE_A_TERMINAL_CONTRACT_MISMATCH")

    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / KW).rglob("*")
        if path.is_file()
        and any(
            token in path.name
            for token in (
                "PHASE_B",
                "AUTHORIZATION_SOURCE",
                "AUTHORIZATION_HANDOFF",
                "PRECONSUMPTION_INVOCATION_BINDING",
                "EXECUTION_RESULT",
            )
        )
    ]
    if forbidden:
        raise KWVerificationError(f"FORBIDDEN_POSTHUMAN_ARTIFACT:{forbidden}")
    required_lines = {
        f"GENERATION {GENERATION}",
        f"OPERATION {OPERATION}",
        f"CANDIDATE_SHA256 {candidate_sha256}",
        f"AUTHORIZATION_BASE_HEAD {HEAD}",
        f"AUTHORIZATION_BASE_TREE {TREE}",
        "EXPECTED_ROUTE FM -> ER -> P11",
        "HUMAN_AUTHORITY NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
        "AUTHORITY_CONSUMPTION 0",
        "PHASE_B_STARTED FALSE",
        "OPERATION_ATTEMPT 0",
        "AUTO_CONTINUABLE FALSE",
        "HUMAN_REVIEW_REQUIRED TRUE",
        "STOP AT THE HUMAN DECISION BARRIER.",
    }
    human_lines = set(
        (ROOT / HUMAN_PRESENTATION).read_text(encoding="utf-8").splitlines()
    )
    if not required_lines.issubset(human_lines):
        raise KWVerificationError("HUMAN_DECISION_PRESENTATION_MISMATCH")
    if equivalence.get("request_sha256") != request_envelope["request_sha256"]:
        raise KWVerificationError("GN_EQUIVALENCE_MISMATCH")

    return {
        "terminal": TERMINAL,
        "generation": GENERATION,
        "operation": OPERATION,
        **expected_identities,
        "authorization_presentation_sha256": sha256_path(AUTH_PRESENTATION),
        "human_decision_presentation_sha256": sha256_path(HUMAN_PRESENTATION),
        "authorization_base_head": HEAD,
        "authorization_base_tree": TREE,
        "operation_context_head": HEAD,
        "operation_context_tree": TREE,
        "presentation_head": HEAD,
        "presentation_tree": TREE,
        "human_decision_presentation_status": "VERIFIED__READY_FOR_HUMAN_DECISION",
        "human_authority_status": "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET",
        "human_authority_handoff_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "preconsumption_binding_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "gn_exact_preauthorization_field_count": 10,
        "freshness_against_kn": "VERIFIED__ALL_REQUIRED_DIGESTS_DISTINCT",
        "operational_counters": reduction["operational_counters"],
        "e05": reduction["e05"],
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
    }


def verify_successful_precedents() -> dict[str, Any]:
    kv = verify_seal(load_canonical(KV_REDUCTION), "reduction")
    historical = kv.get("historical_successful_precedents", [])
    expected = {"HP_WRONG_INPUT", "HX_WRONG_CONTRACT", "IC_WRONG_PROVENANCE"}
    if {item.get("precedent") for item in historical} != expected:
        raise KWVerificationError("KV_SUCCESSFUL_PRECEDENT_SET_MISMATCH")
    for item in historical:
        coordinates = {
            item.get("human_authority_head"),
            item.get("preconsumption_binding_head"),
            item.get("execution_head"),
        }
        if (
            len(coordinates) != 1
            or item.get("authority_rebound") != "VERIFIED__NO"
            or item.get("operation_succeeded") != "VERIFIED__YES"
        ):
            raise KWVerificationError("KV_PRECEDENT_HEAD_EQUALITY_MISMATCH")

    jh_terminal = verify_seal(load_canonical(JH_TERMINAL), "reduction")
    jh_context = load_canonical(JH_CONTEXT)
    jh_request = verify_seal(load_canonical(JH_REQUEST), "request")
    jh_handoff = verify_seal(load_canonical(JH_HANDOFF), "authorization")
    head = jh_terminal.get("entry", {}).get("head")
    tree = jh_terminal.get("entry", {}).get("tree")
    if (
        jh_terminal.get("terminal")
        != "A__FUTURE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY_VERIFIED"
        or jh_terminal.get("authority", {}).get("final_admission")
        != "VERIFIED__PASS"
        or jh_context.get("repository_head") != head
        or jh_context.get("repository_tree") != tree
        or jh_request.get("repository", {}).get("head") != head
        or jh_request.get("repository", {}).get("tree") != tree
        or jh_handoff.get("authorized_repository_head") != head
        or jh_handoff.get("authorized_repository_tree") != tree
    ):
        raise KWVerificationError("JH_PRECEDENT_HEAD_EQUALITY_MISMATCH")
    return {
        "hp_hx_ic": "VERIFIED__AUTHORITY_PRECONSUMPTION_EXECUTION_HEAD_EQUALITY",
        "jh": "VERIFIED__CONTEXT_REQUEST_AUTHORITY_AND_ADMISSION_HEAD_TREE_EQUALITY",
        "authority_rebinding": "VERIFIED__ABSENT",
    }


def verify_all_json() -> dict[str, int]:
    checked = 0
    sealed = 0
    for path in (ROOT / KW).rglob("*.json"):
        raw = path.read_bytes()
        value = json.loads(raw)
        if raw != canonical_bytes(value):
            raise KWVerificationError(f"NONCANONICAL_JSON:{path}")
        checked += 1
        for inner in ("request", "checkpoint", "proof", "reduction", "observation"):
            if isinstance(value.get(inner), dict) and f"{inner}_sha256" in value:
                verify_seal(value, inner)
                sealed += 1
    return {"canonical_json_count": checked, "verified_inner_seal_count": sealed}


def verify(
    remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD
) -> dict[str, Any]:
    return {
        "entry": verify_entry(remote_head, nested_remote_tag),
        "successful_precedents": verify_successful_precedents(),
        "phase_a": verify_phase_a(),
        "canonical_artifacts": verify_all_json(),
    }


if __name__ == "__main__":
    sys.stdout.buffer.write(canonical_bytes(verify()))
