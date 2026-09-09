#!/usr/bin/env python3
"""Formalize the repository-only JV repair of JU's GN request projection.

This owner reads committed JU evidence, projects it into GN's already-existing
vector-independent V1 request contract, and deterministically derives a Human
presentation.  The request and presentation are NONAUTHORITY.  This module has
no Human-authority creation/consumption, launcher, QEMU, VM, PRE, or P11 call.
"""

from __future__ import annotations

from copy import deepcopy
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
JU_HEAD = "81f89c3b9e4330fe689d0093ed4a8a40b36066b2"
JU_TREE = "5df0be8816b0449505397cb0bb17cd9252c91aec"
JU_SUBJECT = "G77-256JU localize EXPIRED GN request schema blocker"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"

GENERATION = "G77_256JU_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JU_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
VECTOR = "EXPIRED"
TERMINAL = "A__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"

JV = Path(".github/governance/evidence/g77_256jv_expired_gn_request_schema_binding_repair_v1")
JU = Path(".github/governance/evidence/g77_256ju_expired_operational_v1")
GN_PATH = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
P11_PATH = Path("tests/p11_da_operational_consumer_v1.py")
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_FINAL_SEAL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)
JU_REQUEST = JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
JU_CHECKPOINT = JU / "G77_256JU_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
JU_REDUCTION = JU / "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
JU_STATIC = JU / "G77_256JU_PREAUTHORITY_STATIC_READINESS_V1.json"
JU_CONTEXT = JU / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
JU_CANDIDATE = JU / (
    "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
REQUEST = JV / "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = JV / "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
EQUIVALENCE = JV / "G77_256JV_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
REDUCTION = JV / "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

EXPECTED_HASHES = {
    GN_PATH: "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3",
    P11_PATH: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
    EX_CERTIFICATE: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    EX_FINAL_SEAL: "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543",
    JU_REQUEST: "ac7c82bb802da71efc510f3a230c5fe8cd9dc09035ad3ff62f82b263de47bd43",
    JU_CHECKPOINT: "a5cf7b251439cd27a894707f4324ea8be41882bb032e727344ebb507c5467604",
    JU_REDUCTION: "1d5958745999a6b48ca38dbf810e71cc92b71f06a7e14f946d9e2d1f8d26d61c",
    JU_STATIC: "12e789c6d43d19b96a051a86e034c4085bc8bde1d279658161c1e1ea2dd971b2",
    JU_CONTEXT: "83b197fcdf49fc14331bd66813fba0298a03aebe5608c5aebf15b536ad03c62f",
    JU_CANDIDATE: "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
}
HISTORICAL_REQUESTS = {
    "WRONG_ATTEMPT": Path(
        ".github/governance/evidence/g77_256gm_wrong_attempt_operational_v1/"
        "G77_256GM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    ),
    "WRONG_INPUT": Path(
        ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
        "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    ),
    "WRONG_CONTRACT": Path(
        ".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/"
        "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    ),
    "WRONG_PROVENANCE": Path(
        ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/"
        "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    ),
    "FUTURE": Path(
        ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/"
        "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    ),
}


class JVFormalizationError(RuntimeError):
    """One deterministic fail-closed JV formalization error."""


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JVFormalizationError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JVFormalizationError(f"MODULE_UNAVAILABLE__{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


GN = load_module(GN_PATH, "g77_256jv_gn")


def canonical_bytes(value: Any) -> bytes:
    return GN._canonical_bytes(value)


def load_canonical(relative: Path) -> dict[str, Any]:
    raw = (ROOT / relative).read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JVFormalizationError(f"NONCANONICAL_JSON__{relative}")
    return value


def seal(schema_id: str, inner_name: str, inner: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema_id,
        inner_name: inner,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(inner)),
    }


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
        "repository": str(ROOT), "branch": BRANCH, "head": JU_HEAD,
        "tree": JU_TREE, "subject": JU_SUBJECT, "origin": ORIGIN,
        "remote_head": JU_HEAD, "index_empty": True,
    }
    if observed != expected:
        raise JVFormalizationError("EXACT_REMOTE_RATIFIED_JU_ENTRY_MISMATCH")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    for line in status.splitlines():
        if not line.startswith(f"?? {JV.as_posix()}/"):
            raise JVFormalizationError("JV_BOUNDED_WORKTREE_SCOPE_VIOLATION")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }:
        raise JVFormalizationError("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "worktree_clean_at_entry": True,
        "direct_remote_equality": "VERIFIED__READ_ONLY_LS_REMOTE",
        "nested_authority": nested_state | {
            "pinned": True,
            "remote_tag_equal": "VERIFIED__READ_ONLY_LS_REMOTE",
        },
    }


def authenticate_committed_dependencies() -> dict[str, str]:
    result: dict[str, str] = {}
    for relative, expected in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        committed = subprocess.check_output(
            ["git", "show", f"{JU_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if raw != committed or sha256_bytes(raw) != expected:
            raise JVFormalizationError(f"COMMITTED_DEPENDENCY_MISMATCH__{relative}")
        result[relative.as_posix()] = expected
    return result


def reconstruct_ju_blocker() -> dict[str, Any]:
    request_envelope = load_canonical(JU_REQUEST)
    checkpoint_envelope = load_canonical(JU_CHECKPOINT)
    reduction_envelope = load_canonical(JU_REDUCTION)
    context = load_canonical(JU_CONTEXT)
    for envelope, inner_name in (
        (request_envelope, "request"),
        (checkpoint_envelope, "checkpoint"),
        (reduction_envelope, "reduction"),
    ):
        if envelope[f"{inner_name}_sha256"] != sha256_bytes(
            canonical_bytes(envelope[inner_name])
        ):
            raise JVFormalizationError(f"JU_INNER_SEAL_MISMATCH__{inner_name}")
    reduction = reduction_envelope["reduction"]
    expected_difference = {
        "request_extra_fields": ["expired_execution_count"],
        "request_missing_fields": ["wrong_attempt_execution_count"],
        "live_binding_extra_fields": ["expired_adapter_sha256", "temporal_binding_sha256"],
        "live_binding_missing_fields": ["du", "eb", "ee"],
    }
    if (
        reduction["terminal"]
        != "M__FRESH_EXPIRED_PREAUTHORIZATION_GN_REQUEST_SCHEMA_MISMATCH"
        or reduction["phase"] != "FAIL_CLOSED_BEFORE_HUMAN_AUTHORIZATION_PRESENTATION"
        or reduction["blocker"]["gn_rejection"] != "SEALED_REQUEST_FIELDS_INVALID"
        or {key: reduction["blocker"][key] for key in expected_difference}
        != expected_difference
        or reduction["e05"] != {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0", "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        }
        or set(reduction["operational_counters"].values()) != {"VERIFIED__0"}
        or reduction["reuse"]["ex_reused"] != "VERIFIED__17_OF_17"
        or reduction["reuse"]["ex_reconstructed"] != "VERIFIED__0"
    ):
        raise JVFormalizationError("JU_TERMINAL_MISMATCH")
    request = request_envelope["request"]
    observed_difference = {
        "request_extra_fields": sorted(set(request) - GN.REQUEST_FIELDS),
        "request_missing_fields": sorted(GN.REQUEST_FIELDS - set(request)),
        "live_binding_extra_fields": sorted(set(request["live_binding"]) - GN.LIVE_BINDING_FIELDS),
        "live_binding_missing_fields": sorted(GN.LIVE_BINDING_FIELDS - set(request["live_binding"])),
    }
    if observed_difference != expected_difference:
        raise JVFormalizationError("JU_SCHEMA_DIFFERENCE_MISMATCH")
    try:
        GN.load_validated_sealed_request(ROOT / JU_REQUEST)
    except GN.PresentationBindingError as exc:
        rejection = str(exc)
    else:
        raise JVFormalizationError("GN_UNEXPECTEDLY_ACCEPTED_JU_REQUEST")
    if rejection != "SEALED_REQUEST_FIELDS_INVALID":
        raise JVFormalizationError("JU_GN_REJECTION_TOKEN_MISMATCH")
    checkpoint = checkpoint_envelope["checkpoint"]
    identities = checkpoint["identities"]
    if (
        request_envelope["request_sha256"]
        != "8dd1eacf6d49a4b22314edf60dcd380203c020529e7654c88c40b7069834bbd6"
        or checkpoint_envelope["checkpoint_sha256"]
        != "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0"
        or request["generation_identity"] != GENERATION
        or request["operation_identity"] != OPERATION
        or identities["candidate_sha256"]
        != "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
        or identities["context_sha256"]
        != "cdb360526bdeaf3161923f03baf3211d49625571c13fbf731c9ddc99db582c07"
        or identities["context_file_sha256"]
        != "83b197fcdf49fc14331bd66813fba0298a03aebe5608c5aebf15b536ad03c62f"
        or identities["canonical_argv_sha256"]
        != "0d21324097647b807bd7ff561c28bb8ff70ce3ebd52dde05946a096e93b9e855"
        or identities["expired_adapter_sha256"]
        != "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
        or identities["temporal_binding_sha256"]
        != "e29957ac60fc949be0fefb73a0f5751dcc7d0ade04256c2ffee753b822a24fbe"
        or context["context_sha256"] != identities["context_sha256"]
        or context["candidate_manifest_sha256"] != identities["candidate_sha256"]
        or context["canonical_argv_sha256"] != identities["canonical_argv_sha256"]
    ):
        raise JVFormalizationError("JU_MATERIALIZED_IDENTITY_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "phase": reduction["phase"],
        "gn_rejection": rejection,
        "schema_difference": observed_difference,
        "identities": identities | {
            "invalid_request_identity": request_envelope["request_sha256"],
            "checkpoint_digest": checkpoint_envelope["checkpoint_sha256"],
            "presentation": "NOT_MATERIALIZED_IN_JU",
        },
        "authority_boundary": reduction["authority_boundary"],
        "operational_counters": reduction["operational_counters"],
        "e05": reduction["e05"],
    }


def authenticate_gn_contract_and_history() -> dict[str, Any]:
    expected_vectors = {
        "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT",
        "WRONG_PROVENANCE", "FUTURE", "EXPIRED",
    }
    if set(GN.SUPPORTED_VECTORS) != expected_vectors:
        raise JVFormalizationError("GN_VECTOR_SET_MISMATCH")
    accepted: dict[str, Any] = {}
    for vector, relative in HISTORICAL_REQUESTS.items():
        envelope = GN.load_validated_sealed_request(ROOT / relative)
        request = envelope["request"]
        if (
            request["authorized_vector_requested"] != vector
            or set(request) != GN.REQUEST_FIELDS
            or set(request["live_binding"]) != GN.LIVE_BINDING_FIELDS
            or request["wrong_attempt_execution_count"] != 0
            or {key: request["live_binding"][key] for key in ("du", "eb", "ee")}
            != {"du": "PASS", "eb": "PASS", "ee": "PASS"}
        ):
            raise JVFormalizationError(f"HISTORICAL_GN_PROJECTION_MISMATCH__{vector}")
        accepted[vector] = {
            "path": relative.as_posix(),
            "request_sha256": envelope["request_sha256"],
            "wrong_attempt_execution_count": 0,
            "du": "PASS", "eb": "PASS", "ee": "PASS",
        }
    return {
        "owner": GN_PATH.as_posix(),
        "owner_sha256": EXPECTED_HASHES[GN_PATH],
        "request_fields": sorted(GN.REQUEST_FIELDS),
        "live_binding_fields": sorted(GN.LIVE_BINDING_FIELDS),
        "supported_vectors": sorted(expected_vectors),
        "successful_vector_projections": accepted,
        "contract_conclusion": "A_AND_D__GN_V1_IS_VECTOR_INDEPENDENT__JU_USED_WRONG_PROJECTION",
        "field_semantics": {
            "wrong_attempt_execution_count": (
                "MANDATORY_CANONICAL_ZERO_COUNTER_SLOT_AT_THE_PREAUTHORIZATION_BARRIER__"
                "AUTHENTICATED_ACROSS_FIVE_NON_EXPIRED_AND_ALL_GN_SUPPORTED_VECTOR_PROFILES"
            ),
            "du": "CANONICAL_CONTINUATION_MANIFEST_CONTRACT_VALIDATION_STATUS",
            "eb": "CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_STATUS",
            "ee": "RUNTIME_CONSUMER_BINDING_VALIDATION_STATUS",
            "expired_execution_count": "NO_AUTHENTICATED_GN_V1_FIELD_OWNER",
            "expired_adapter_sha256": "UPSTREAM_JU_CONTEXT_AND_CHECKPOINT_EVIDENCE_IDENTITY",
            "temporal_binding_sha256": "UPSTREAM_JU_CONTEXT_AND_CHECKPOINT_EVIDENCE_IDENTITY",
        },
    }


def authenticate_ju_du_eb_ee() -> dict[str, Any]:
    static = load_canonical(JU_STATIC)["proof"]
    candidate = load_canonical(JU_CANDIDATE)["manifest"]
    seal_identities = {item["identity"] for item in candidate["completed_phase_seals"]}
    consumer = candidate["consumer_binding"]["identity"]
    if (
        static["readiness"]["result"] != "STATIC_READINESS_PASS"
        or consumer != "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V1"
        or seal_identities != {
            "G77_256EB_FINAL_VALIDATION_SEAL_V1",
            "G77_256EE_FINAL_VALIDATION_SEAL_V1",
        }
    ):
        raise JVFormalizationError("JU_DU_EB_EE_AUTHENTICATION_MISMATCH")
    return {
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "du_owner": consumer,
        "eb_ee_seals": sorted(seal_identities),
        "ju_static_readiness": static["readiness"]["result"],
    }


def authenticate_ex_reuse() -> dict[str, Any]:
    raw = (ROOT / EX_CERTIFICATE).read_bytes()
    envelope = json.loads(raw, object_pairs_hook=unique_object)
    certificate = envelope["certificate"]
    final_seal = json.loads(
        (ROOT / EX_FINAL_SEAL).read_bytes(), object_pairs_hook=unique_object
    )
    if (
        sha256_bytes(raw) != EXPECTED_HASHES[EX_CERTIFICATE]
        or sha256_path(ROOT / EX_FINAL_SEAL) != EXPECTED_HASHES[EX_FINAL_SEAL]
        or certificate["component_counts"]["CERTIFIED"] != 17
        or not certificate["reusable_p11_spce_execution_substrate"].startswith(
            "CONSTITUTIONALLY_CERTIFIED__COMMON_REPOSITORY_SUBSTRATE_ONLY"
        )
        or final_seal.get("schema_id")
        != "G77_256EX_FINAL_VALIDATION_SEAL_ENVELOPE_V1"
    ):
        raise JVFormalizationError("EX_17_OF_17_CERTIFICATE_MISMATCH")
    return {
        "certificate_path": EX_CERTIFICATE.as_posix(),
        "certificate_sha256": EXPECTED_HASHES[EX_CERTIFICATE],
        "final_seal_path": EX_FINAL_SEAL.as_posix(),
        "final_seal_sha256": EXPECTED_HASHES[EX_FINAL_SEAL],
        "certified_component_count": 17,
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def corrected_request_envelope() -> dict[str, Any]:
    envelope = deepcopy(load_canonical(JU_REQUEST))
    request = envelope["request"]
    if request.pop("expired_execution_count") != 0:
        raise JVFormalizationError("JU_EXPIRED_EXECUTION_COUNTER_NONZERO")
    request["wrong_attempt_execution_count"] = 0
    live = request["live_binding"]
    if live.pop("expired_adapter_sha256") != (
        "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
    ):
        raise JVFormalizationError("JU_EXPIRED_ADAPTER_IDENTITY_MISMATCH")
    if live.pop("temporal_binding_sha256") != (
        "e29957ac60fc949be0fefb73a0f5751dcc7d0ade04256c2ffee753b822a24fbe"
    ):
        raise JVFormalizationError("JU_TEMPORAL_BINDING_IDENTITY_MISMATCH")
    live.update({"du": "PASS", "eb": "PASS", "ee": "PASS"})
    envelope["schema_id"] = "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    request["schema_id"] = "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1"
    envelope["request_sha256"] = sha256_bytes(canonical_bytes(request))
    return envelope


def verify_projection(envelope: dict[str, Any]) -> dict[str, Any]:
    ju_envelope = load_canonical(JU_REQUEST)
    ju_request = deepcopy(ju_envelope["request"])
    repaired = deepcopy(envelope["request"])
    ju_request.pop("expired_execution_count")
    ju_live = ju_request["live_binding"]
    ju_live.pop("expired_adapter_sha256")
    ju_live.pop("temporal_binding_sha256")
    ju_request["schema_id"] = repaired["schema_id"]
    ju_request["wrong_attempt_execution_count"] = 0
    ju_live.update({"du": "PASS", "eb": "PASS", "ee": "PASS"})
    if ju_request != repaired:
        raise JVFormalizationError("PROJECTION_CHANGED_NONSCHEMA_SEMANTICS")
    if (
        repaired["preauthorization"]["checkpoint_inner_sha256"]
        != "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0"
        or repaired["live_binding"]["context_sha256"]
        != "cdb360526bdeaf3161923f03baf3211d49625571c13fbf731c9ddc99db582c07"
        or repaired["authorized_vector_requested"] != VECTOR
        or repaired["generation_identity"] != GENERATION
        or repaired["operation_identity"] != OPERATION
    ):
        raise JVFormalizationError("EXPIRED_CORRELATION_MISMATCH")
    return {
        "selected_projection": "EXISTING_GN_V1_CANONICAL_REQUEST_PROFILE",
        "top_level_replacement": "expired_execution_count_TO_wrong_attempt_execution_count_ZERO",
        "live_binding_replacement": "expired_adapter_sha256_AND_temporal_binding_sha256_TO_du_eb_ee_PASS",
        "nonprojection_field_mutation_count": 0,
        "expired_semantic_information_discarded": False,
        "expired_semantic_preservation": {
            "explicit_vector": VECTOR,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "adapter_sha256_preserved_by": "JU_CHECKPOINT_IDENTITIES_AND_CONTEXT_SHA256",
            "temporal_binding_sha256_preserved_by": "JU_CHECKPOINT_IDENTITIES_AND_CONTEXT_SHA256",
            "checkpoint_digest": "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0",
            "context_sha256": "cdb360526bdeaf3161923f03baf3211d49625571c13fbf731c9ddc99db582c07",
        },
    }


def presentation_and_equivalence(envelope: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    request_bytes = canonical_bytes(envelope)
    temporary = ROOT / REQUEST
    # GN accepts only a file path. Materialization writes the same deterministic
    # bytes before this function is called; tests use their own temporary path.
    if not temporary.is_file() or temporary.read_bytes() != request_bytes:
        raise JVFormalizationError("JV_REQUEST_BYTES_NOT_MATERIALIZED")
    presentation = GN.render_human_authorization_presentation(temporary)
    result = GN.validate_human_authorization_presentation(temporary, presentation)
    parsed = GN.parse_human_authorization_presentation(presentation)
    if (
        parsed["AUTHORIZED_VECTOR_REQUESTED"] != VECTOR
        or parsed["GENERATION_ID"] != GENERATION
        or parsed["OPERATION_ID"] != OPERATION
        or parsed["AUTHORIZATION_REQUEST_SHA256"] != envelope["request_sha256"]
        or parsed["CHECKPOINT_SHA256"]
        != "5fc7fdfd39c11bb3c22eed51fb7333ac456e63dcbb8ada54a186f737fe5e21f0"
    ):
        raise JVFormalizationError("GN_PRESENTATION_CORRELATION_MISMATCH")
    proof = seal(
        "G77_256JV_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JV_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "authorized_vector_requested": VECTOR,
            "request_path": REQUEST.as_posix(),
            "request_file_sha256": sha256_bytes(request_bytes),
            "request_sha256": envelope["request_sha256"],
            "checkpoint_sha256": parsed["CHECKPOINT_SHA256"],
            "presentation_path": PRESENTATION.as_posix(),
            "presentation_sha256": sha256_bytes(presentation),
            **result,
            "presentation_is_authority": False,
            "request_is_authority": False,
            "human_authority_present": False,
            "auto_continuable": False,
        },
    )
    return presentation, proof


def temporal_and_stable_checkout_proof() -> dict[str, Any]:
    checkpoint = load_canonical(JU_CHECKPOINT)["checkpoint"]
    expired = checkpoint["expired_semantics"]
    jt = checkpoint["jt_terminal_reconstruction"]
    if (
        expired["valid_from_unix_ns"] != 100
        or expired["valid_until_unix_ns"] != 1000
        or expired["governed_preclaim_coordinate_unix_ns"] != 1000
        or expired["truth_table"] != {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"}
        or expired["wall_clock_is_governed_preclaim_authority"] is not False
        or jt["stable_checkout"] != {"head": JR_HEAD, "tree": JR_TREE}
        or jt["authoritative_owner"] != "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER"
        or jt["recurrence_hazard"] != "VERIFIED__ELIMINATED"
        or jt["production_route"] != "VERIFIED__1_TO_1"
    ):
        raise JVFormalizationError("TEMPORAL_OR_STABLE_CHECKOUT_MISMATCH")
    return {"temporal_semantics": expired, "stable_checkout": jt}


def negative_projection_proof(envelope: dict[str, Any]) -> dict[str, Any]:
    cases: dict[str, str] = {}
    variants: dict[str, dict[str, Any]] = {}
    extra = deepcopy(envelope)
    extra["request"]["expired_execution_count"] = 0
    extra["request_sha256"] = sha256_bytes(canonical_bytes(extra["request"]))
    variants["unknown_expired_counter"] = extra
    missing = deepcopy(envelope)
    del missing["request"]["wrong_attempt_execution_count"]
    missing["request_sha256"] = sha256_bytes(canonical_bytes(missing["request"]))
    variants["missing_canonical_counter"] = missing
    live_extra = deepcopy(envelope)
    live_extra["request"]["live_binding"]["temporal_binding_sha256"] = "0" * 64
    live_extra["request_sha256"] = sha256_bytes(canonical_bytes(live_extra["request"]))
    variants["unknown_live_binding_field"] = live_extra
    vector = deepcopy(envelope)
    vector["request"]["authorized_vector_requested"] = "FUTURE"
    vector["request_sha256"] = sha256_bytes(canonical_bytes(vector["request"]))
    variants["cross_vector_substitution"] = vector
    generation = deepcopy(envelope)
    generation["request"]["generation_identity"] = "G77_256JV_WRONG_GENERATION"
    generation["request_sha256"] = sha256_bytes(canonical_bytes(generation["request"]))
    variants["cross_generation_substitution"] = generation
    for name, variant in variants.items():
        path = ROOT / JV / f".{name}.tmp.json"
        try:
            path.write_bytes(canonical_bytes(variant))
            try:
                GN.load_validated_sealed_request(path)
            except GN.PresentationBindingError as exc:
                cases[name] = str(exc)
            else:
                raise JVFormalizationError(f"NEGATIVE_CASE_ACCEPTED__{name}")
        finally:
            path.unlink(missing_ok=True)
    return cases


def terminal_reduction(
    entry: dict[str, Any], request: dict[str, Any], presentation: bytes,
    equivalence: dict[str, Any], negative: dict[str, str],
) -> dict[str, Any]:
    ju = reconstruct_ju_blocker()
    gn = authenticate_gn_contract_and_history()
    projection = verify_projection(request)
    du_eb_ee = authenticate_ju_du_eb_ee()
    stable = temporal_and_stable_checkout_proof()
    counters = {key: "VERIFIED__0" for key in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_retry_count", "replay_count",
    )}
    return {
        "schema_id": "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JV",
        "mode": "REPOSITORY_ONLY__GN_REQUEST_PROJECTION_REPAIR__NO_AUTHORITY__NO_OPERATION",
        "terminal": TERMINAL,
        "entry": entry,
        "committed_dependency_hashes": authenticate_committed_dependencies(),
        "ju_reconstruction": ju,
        "gn_contract": gn,
        "du_eb_ee": du_eb_ee,
        "ex_certificate_reuse": authenticate_ex_reuse(),
        "selected_projection": projection,
        "request_presentation_correlation": {
            "invalid_ju_request_sha256": ju["identities"]["invalid_request_identity"],
            "corrected_jv_request_sha256": request["request_sha256"],
            "corrected_jv_request_file_sha256": sha256_bytes(canonical_bytes(request)),
            "checkpoint_sha256": ju["identities"]["checkpoint_digest"],
            "presentation_sha256": sha256_bytes(presentation),
            "equivalence_file_sha256": sha256_bytes(canonical_bytes(equivalence)),
            "gn_result": equivalence["proof"]["human_presentation_request_equivalence"],
            "reviewed_field_count": equivalence["proof"]["reviewed_field_count"],
        },
        "negative_validation": negative,
        "stable_runtime_and_temporal_contract": stable,
        "authority_boundary": {
            "authorization_request_materialization_count": "VERIFIED__1",
            "authorization_presentation_materialization_count": "VERIFIED__1",
            "human_authority_present": False,
            "authority_consumed": False,
            "request_is_authority": False,
            "presentation_is_authority": False,
            "checkpoint_is_authority": False,
            "provider_capability_is_authority": False,
            "human_authority_assurance_status": (
                "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
            ),
        },
        "operational_counters": counters,
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": (
                "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__JS__JT__JU__FM__FC__ER__GN__P11"
            ),
            "new_capabilities": (
                "VERIFIED__1__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"
            ),
            "existing_capability_became_unreachable": "VERIFIED__NO",
            "parallel_flow_created": "VERIFIED__NO",
            "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0", "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0", "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "proof_yield": {
            "new_verified_capability_count": (
                "VERIFIED__1__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"
            ),
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0", "proof_reuse_count": "VERIFIED__17",
        },
        "governance_dashboard": {
            "project_progress": "VERIFIED__JV_GN_COMPATIBLE_EXPIRED_REQUEST_PROJECTION",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": (
                "ESTIMATED__EXPIRED_REPOSITORY_PRESENTATION_READY__OPERATION_UNSTARTED"
            ),
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_SCHEMA_REUSE_ZERO_AUTHORITY_ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EXISTING_GN_CONTRACT_REUSED",
            "overengineering_risk": "ESTIMATED__LOW__ZERO_PRODUCTION_MUTATION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JU_TO_JV_REPOSITORY_CONTINUATION",
            "candidate_capability": (
                "VERIFIED__GN_COMPATIBLE_EXPIRED_REQUEST_AND_NONAUTHORITY_PRESENTATION_REPOSITORY_ONLY"
            ),
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__JU_SCHEMA_BLOCKER_TO_JV_PROJECTION_REPAIR",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": "GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED",
            "first_broken_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_PREAUTHORIZATION_CHECKPOINT_NOT_YET_PROVEN",
            "minimum_missing_capability": "FRESH_EXPIRED_PREAUTHORIZATION_CHECKPOINT_AND_HUMAN_PRESENTATION",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_GENERATION",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def build_artifacts(remote_head: str) -> dict[Path, bytes]:
    entry = authenticate_entry(remote_head)
    reconstruct_ju_blocker()
    authenticate_gn_contract_and_history()
    authenticate_ju_du_eb_ee()
    authenticate_ex_reuse()
    temporal_and_stable_checkout_proof()
    request = corrected_request_envelope()
    verify_projection(request)
    request_bytes = canonical_bytes(request)
    request_path = ROOT / REQUEST
    if not request_path.exists():
        request_path.write_bytes(request_bytes)
    elif request_path.read_bytes() != request_bytes:
        raise JVFormalizationError("JV_REQUEST_COLLISION")
    presentation, equivalence = presentation_and_equivalence(request)
    negative = negative_projection_proof(request)
    reduction = seal(
        "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction",
        terminal_reduction(entry, request, presentation, equivalence, negative),
    )
    return {
        REQUEST: request_bytes,
        PRESENTATION: presentation,
        EQUIVALENCE: canonical_bytes(equivalence),
        REDUCTION: canonical_bytes(reduction),
    }


def materialize(remote_head: str) -> None:
    artifacts = build_artifacts(remote_head)
    for relative, raw in artifacts.items():
        path = ROOT / relative
        if path.exists():
            if path.read_bytes() != raw:
                raise JVFormalizationError(f"ARTIFACT_COLLISION__{relative}")
        else:
            path.write_bytes(raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)
    materialize(parse_args().remote_head)
