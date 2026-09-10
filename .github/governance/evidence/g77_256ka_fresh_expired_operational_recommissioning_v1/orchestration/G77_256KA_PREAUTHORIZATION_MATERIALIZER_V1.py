#!/usr/bin/env python3
"""Materialize the nonauthority KA EXPIRED Phase-A Human barrier.

The existing JY/JW materializer remains the construction owner.  KA changes
only generation-local identities, authenticates committed JZ and binds a
future post-Human invocation to JZ's digest-deriving FM owner.  No Human
authority file is created, no authority is consumed, and no process starts.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KA = ROOT / (
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "128bb145969a7b9ccebb8812b24216e00c7db04c"
TREE = "47d09bc1d2ecf0529601ba65085651d01c325a7c"
SUBJECT = "G77-256JZ verify FM authority digest preconsumption binding"
JY_MATERIALIZER = Path(
    ".github/governance/evidence/g77_256jy_expired_operational_v1/"
    "orchestration/G77_256JY_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
JY_MATERIALIZER_SHA256 = (
    "969d2007e46d5bb22973a1c46651b2dc6e2904f288706024d68ed8419f493cfe"
)
JZ_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256jz_fm_authority_digest_handoff_repair_v1"
)
JZ_REDUCTION = JZ_ROOT / "G77_256JZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JZ_BINDING = JZ_ROOT / "G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
JZ_FORMALIZER = JZ_ROOT / "analysis/G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_FORMALIZER_V1.py"
JZ_TEST = JZ_ROOT / "tests/test_g77_256jz_preconsumption_invocation_binding_v1.py"
JY_ROOT = Path(".github/governance/evidence/g77_256jy_expired_operational_v1")
JY_HANDOFF = JY_ROOT / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
JY_CONTEXT = JY_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
JY_CANDIDATE = JY_ROOT / (
    "live_binding/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
JI_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/"
    "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JI_REDUCTION_SHA256 = "06acd7f7d76526fd8a5377be25d95a0897c1d53fe39fe0ce6417db258595678c"
BINDER = KA.relative_to(ROOT) / "orchestration/G77_256KA_POSTHUMAN_INVOCATION_BINDER_V1.py"
JZ_TERMINAL = (
    "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_"
    "BINDING_REPOSITORY_VERIFIED"
)
KA_TERMINAL = (
    "A__FRESH_KA_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)

EXPECTED_HASHES = {
    JZ_REDUCTION: "6d4fb0d2157fe3a75df67434a0c582863ca2a9063551b1d83aa56eef4de2e7a7",
    JZ_BINDING: "cbe77d8e611df7fc2505ac43bfdf5967360020ee8e70a3f919f210a71fc5bd9c",
    JZ_FORMALIZER: "3832d64c3e071bfe66926cd545c8fd13d133284fcfe7d40c568b1dfebb9340c5",
    JZ_TEST: "096716315cdebc19b006bf5eeb7a7400f1989534ede595b71c893452759db150",
    FM_PATH: "97f1cb4dc4e9da7fd70efcc2a2713defd71e7aa7152f5dfc81229d7b738cbe29",
}


class KABarrierError(RuntimeError):
    """One deterministic fail-closed KA Phase-A error."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KABarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KABarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KABarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_adapted_materializer() -> ModuleType:
    path = ROOT / JY_MATERIALIZER
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{JY_MATERIALIZER}"], cwd=ROOT)
    if raw != committed or sha256_bytes(raw) != JY_MATERIALIZER_SHA256:
        raise KABarrierError("COMMITTED_JY_PREAUTHORIZATION_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("JY", "KA").replace("jy", "ka")
    source = source.replace(
        "g77_256ka_expired_operational_v1",
        "g77_256ka_fresh_expired_operational_recommissioning_v1",
    )
    source = source.replace("939d7eda8ff333b6cf0dfbd54d274aabefcba698", HEAD)
    source = source.replace("bce9f2863a7314a1e5e088066efeea52615d989d", TREE)
    source = source.replace(
        "G77-256JX verify ER admission runtime checkout role separation", SUBJECT
    )
    # JX authenticates the prior FM identity while JZ authenticates its sole
    # bounded successor.  Preserve both identities rather than conflating the
    # historical repair checkpoint with the current owner bytes.
    source = source.replace(
        '"8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469"',
        '"97f1cb4dc4e9da7fd70efcc2a2713defd71e7aa7152f5dfc81229d7b738cbe29"',
    )
    source = source.replace(
        'reduction.get("implementation", {}).get("fm_after_sha256")\n        != JX_HASHES[FM_PATH]',
        'reduction.get("implementation", {}).get("fm_after_sha256")\n        != "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469"',
    )
    module = ModuleType("g77_256ka_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


A = load_adapted_materializer()
M = A.M
M.KA = KA
M.LIVE = KA / "live_binding"
M.OPERATION_ROOT = KA / "operation_state"
M.TRANSIENT_ROOT = Path("/tmp/g77_256ka_fresh_expired_operational_recommissioning_v1")
_inherited_zero_counters = M.zero_counters


def ka_zero_counters() -> dict[str, int]:
    counters = _inherited_zero_counters()
    counters["operational_request_count"] = 0
    counters["expired_denial_count"] = 0
    return counters


M.zero_counters = ka_zero_counters


def authenticate_jz() -> dict[str, Any]:
    identities: dict[str, str] = {}
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{relative}"], cwd=ROOT)
        if path.read_bytes() != committed or sha256_path(path) != expected:
            raise KABarrierError(f"COMMITTED_JZ_DEPENDENCY_MISMATCH:{relative}")
        identities[relative.as_posix()] = expected

    reduction_envelope = load_canonical(ROOT / JZ_REDUCTION)
    reduction = reduction_envelope.get("reduction", {})
    if reduction_envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise KABarrierError("JZ_REDUCTION_SEAL_MISMATCH")
    capability = reduction.get("capability", {})
    jy = reduction.get("jy_authentication", {})
    if (
        reduction.get("terminal") != JZ_TERMINAL
        or capability.get("digest_equality")
        != "VERIFIED__AUTHENTICATED_CANONICAL_EQUALS_SEALED_INVOCATION_EQUALS_FINAL_FM_ARGV"
        or capability.get("caller_digest_parameter") != "ABSENT"
        or capability.get("provider_digest_parameter") != "ABSENT"
        or jy.get("authority_state")
        != "HISTORICAL__CONSUMED__NONREUSABLE__NONTRANSFERABLE"
        or jy.get("pre_reached") is not False
        or reduction.get("e05", {}).get("state") != "VERIFIED__11_OF_18"
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
    ):
        raise KABarrierError("JZ_CONTRACT_MISMATCH")

    historical = M.FM.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=JY_CONTEXT,
        live_candidate_binding=JY_CANDIDATE,
        execution_authority=JY_HANDOFF,
    )
    if historical != load_canonical(ROOT / JZ_BINDING):
        raise KABarrierError("JZ_HISTORICAL_FIXTURE_BINDING_MISMATCH")
    M.FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=JY_CONTEXT,
        live_candidate_binding=JY_CANDIDATE,
        execution_authority=JY_HANDOFF,
        envelope=historical,
    )
    builder_parameters = list(
        inspect.signature(M.FM.build_preconsumption_invocation_binding).parameters
    )
    if builder_parameters != [
        "repository_root",
        "operation_context",
        "live_candidate_binding",
        "execution_authority",
    ]:
        raise KABarrierError("JZ_BUILDER_PARAMETER_SURFACE_MISMATCH")
    if "subprocess.run" in inspect.getsource(M.FM.build_preconsumption_invocation_binding):
        raise KABarrierError("JZ_BUILDER_PROCESS_START_PATH_DETECTED")
    ast.parse((ROOT / FM_PATH).read_text(encoding="utf-8"))
    return {
        "terminal": JZ_TERMINAL,
        "artifact_hashes": identities,
        "historical_binding_file_sha256": EXPECTED_HASHES[JZ_BINDING],
        "historical_binding_inner_sha256": historical["invocation_binding_sha256"],
        "historical_fixture_classification": "COMMITTED_JY_HISTORY_ONLY__NOT_AUTHORITY_FOR_KA",
        "fm_owner_sha256": EXPECTED_HASHES[FM_PATH],
        "fm_jz_implementation_sha256": reduction["bindings"]["fm_jz_sha256"],
        "builder_parameters": builder_parameters,
        "caller_digest_parameter": "ABSENT",
        "provider_digest_parameter": "ABSENT",
    }


def authenticate_e05_frontier() -> dict[str, Any]:
    path = ROOT / JI_REDUCTION
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{JI_REDUCTION}"], cwd=ROOT)
    if path.read_bytes() != committed or sha256_path(path) != JI_REDUCTION_SHA256:
        raise KABarrierError("COMMITTED_JI_E05_FRONTIER_MISMATCH")
    envelope = load_canonical(path)
    reduction = envelope.get("reduction", {})
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise KABarrierError("JI_E05_FRONTIER_SEAL_MISMATCH")
    e05 = reduction.get("e05", {})
    expected_remaining = [
        "AMBIGUOUS", "STALE", "EXPIRED", "REVOKED", "SUPERSEDED",
        "WRONG_SCOPE", "COHERENT_COPY",
    ]
    if (
        e05.get("after") != "VERIFIED__11_OF_18"
        or e05.get("credit") != "VERIFIED__0"
        or e05.get("remaining_set") != expected_remaining
        or reduction.get("selection", {}).get("selected_vector") != "EXPIRED"
    ):
        raise KABarrierError("JI_E05_FRONTIER_CONTRACT_MISMATCH")
    return {
        "source_path": JI_REDUCTION.as_posix(),
        "source_file_sha256": JI_REDUCTION_SHA256,
        "required_set": e05["required_set"],
        "satisfied_set": e05["satisfied_set"],
        "remaining_set": expected_remaining,
        "selected_vector": "EXPIRED",
        "selected_vector_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }


def materialize_jz_readiness(jz: dict[str, Any]) -> dict[str, Any]:
    context_path = KA / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    candidate_path = KA / (
        "live_binding/candidate/"
        "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
    )
    context = M.load_canonical(context_path)
    authority_path = KA / "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    if authority_path.exists() or authority_path.is_symlink():
        raise KABarrierError("KA_PHASE_A_AUTHORITY_ARTIFACT_PRESENT")
    prefix = [
        sys.executable,
        FM_PATH.as_posix(),
        "--operation-context",
        context_path.relative_to(ROOT).as_posix(),
        "--operation-context-sha256",
        sha256_path(context_path),
        "--live-candidate-binding",
        candidate_path.relative_to(ROOT).as_posix(),
        "--execution-authority",
        authority_path.relative_to(ROOT).as_posix(),
        "--execution-authority-sha256",
    ]
    proof = {
        "schema_id": "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1",
        "artifact_class": "PREHUMAN_INVOCATION_STRUCTURE__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": M.GENERATION,
        "operation_identity": M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "operation_context_path": context_path.relative_to(ROOT).as_posix(),
        "operation_context_file_sha256": sha256_path(context_path),
        "operation_context_sha256": context["context_sha256"],
        "candidate_path": candidate_path.relative_to(ROOT).as_posix(),
        "candidate_sha256": sha256_path(candidate_path),
        "future_execution_authority_path": authority_path.relative_to(ROOT).as_posix(),
        "future_execution_authority_state": "ABSENT__EXPLICIT_HUMAN_ACT_NOT_YET_SUPPLIED",
        "prospective_fm_argv_prefix_through_digest_flag": prefix,
        "authority_digest_slot": "UNMATERIALIZED__DERIVE_FROM_EXACT_CANONICAL_HANDOFF_BYTES_POST_HUMAN",
        "final_fm_argv_state": "NOT_MATERIALIZED__NO_HUMAN_AUTHORITY_EXISTS",
        "posthuman_binding_owner": (
            "FM.build_preconsumption_invocation_binding_THEN_"
            "FM.validate_preconsumption_invocation_binding"
        ),
        "posthuman_binding_adapter_path": BINDER.as_posix(),
        "digest_equality_required_posthuman": (
            "AUTHENTICATED_CANONICAL_AUTHORITY_DIGEST_EQUALS_"
            "SEALED_INVOCATION_AUTHORITY_DIGEST_EQUALS_FINAL_FM_ARGV_AUTHORITY_DIGEST"
        ),
        "digest_equality_phase_a_status": (
            "NOT_APPLICABLE__NO_FRESH_HUMAN_AUTHORITY_DIGEST_EXISTS"
        ),
        "caller_digest_input_count": 0,
        "provider_digest_input_count": 0,
        "binding_is_authority": False,
        "execution_authorized": False,
        "authority_consumption_count": 0,
        "fm_operational_invocation_count": 0,
        "process_started": False,
        "jz_authentication": jz,
    }
    envelope = {
        "schema_id": "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KA / "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "phase_a_digest_equality": proof["digest_equality_phase_a_status"],
        "posthuman_digest_equality": proof["digest_equality_required_posthuman"],
    }


def finalize_phase_a(
    jz: dict[str, Any], readiness: dict[str, Any], e05_frontier: dict[str, Any]
) -> None:
    checkpoint_path = KA / "G77_256KA_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KA / "G77_256KA_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KA / "G77_256KA_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KA / "G77_256KA_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    checkpoint = load_canonical(checkpoint_path)
    checkpoint["checkpoint"]["operational_counters"].update(
        {"operational_request_count": 0, "expired_denial_count": 0}
    )
    checkpoint["checkpoint"]["jz_preconsumption_invocation_readiness"] = readiness
    checkpoint["checkpoint"]["cross_account_recovery"] = {
        "status": "VERIFIED__YES",
        "source": "AUTHENTICATED_REPOSITORY_ONLY",
    }
    checkpoint["checkpoint"]["e05_frontier_authentication"] = e05_frontier
    reseal(checkpoint, "checkpoint")
    write_canonical(checkpoint_path, checkpoint)

    request = load_canonical(request_path)
    request["request"]["preauthorization"]["checkpoint_file_sha256"] = sha256_path(checkpoint_path)
    request["request"]["preauthorization"]["checkpoint_inner_sha256"] = checkpoint["checkpoint_sha256"]
    reseal(request, "request")
    write_canonical(request_path, request)

    presentation = M.GN.render_human_authorization_presentation(request_path)
    presentation_path.write_bytes(presentation)
    gn_result = M.GN.validate_human_authorization_presentation(request_path, presentation)

    equivalence = load_canonical(equivalence_path)
    equivalence["proof"].update(
        {
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn_result,
        }
    )
    reseal(equivalence, "proof")
    write_canonical(equivalence_path, equivalence)

    safe_stop = load_canonical(safe_stop_path)
    stop = safe_stop["checkpoint"]
    stop["operational_counters"].update(
        {"operational_request_count": 0, "expired_denial_count": 0}
    )
    stop.update(
        {
            "terminal": KA_TERMINAL,
            "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
            "readiness_checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_file_sha256": sha256_path(equivalence_path),
            "equivalence_inner_sha256": equivalence["proof_sha256"],
            "jz_preconsumption_invocation_readiness": readiness,
        }
    )
    reseal(safe_stop, "checkpoint")
    write_canonical(safe_stop_path, safe_stop)

    reduction = load_canonical(reduction_path)
    value = reduction["reduction"]
    value["operational_counters"].update(
        {"operational_request_count": 0, "expired_denial_count": 0}
    )
    value["terminal"] = KA_TERMINAL
    value["jz_reconstruction"] = jz
    value["jz_preconsumption_invocation_readiness"] = readiness
    value["e05_frontier_authentication"] = e05_frontier
    value["owner_results"]["jz_preconsumption_binding"] = (
        "PASS__PREHUMAN_STRUCTURE_BOUND__POSTHUMAN_DIGEST_DERIVATION_REQUIRED"
    )
    value["identities"].update(
        {
            "request_sha256": request["request_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "readiness_checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
            "checkpoint_sha256": safe_stop["checkpoint_sha256"],
            "checkpoint_file_sha256": sha256_path(safe_stop_path),
            "jz_invocation_readiness_sha256": readiness["inner_sha256"],
            "jz_invocation_readiness_file_sha256": readiness["file_sha256"],
        }
    )
    value["authority_boundary"].update(
        {
            "fresh_human_authority_digest": "NOT_MATERIALIZED",
            "posthuman_jz_digest_equality": "REQUIRED_BEFORE_AUTHORITY_CONSUMPTION",
        }
    )
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__1_PREAUTHORIZATION_CAPABILITY",
        "new_blocker_localized_count": "VERIFIED__0",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"].update(
        {
            "existing_certified_capabilities_reused": (
                "EX_17_OF_17__JZ__JY_FINALITY__JX__JT__JR__JV__FM__GL__GN__ER__P11"
            ),
            "new_capabilities": "VERIFIED__1__FRESH_KA_PREAUTHORIZATION_CAPABILITY__NONAUTHORITY",
        }
    )
    value["governance_dashboard"].update(
        {
            "project_progress": "VERIFIED__KA_FRESH_EXPIRED_PREAUTHORIZATION_BARRIER_MATERIALIZED",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_READY_FOR_ONE_EXPLICIT_HUMAN_DECISION",
            "cognition_assisted_handoff": "VERIFIED__CROSS_ACCOUNT_REPOSITORY_ONLY_HANDOFF",
            "constitutional_continuation_progress": "VERIFIED__JZ_TO_KA_PREAUTHORIZATION_STOP",
        }
    )
    value["ccwim"].update(
        {
            "cross_account_recovery": "VERIFIED__YES",
            "cross_account_recovery_source": "AUTHENTICATED_REPOSITORY_ONLY",
        }
    )
    value["frontier"] = {
        "last_verified_edge": "FRESH_KA_EXPIRED_PREAUTHORIZATION_AND_JZ_POSTHUMAN_BINDING_ROUTE_READY",
        "first_broken_edge": "EXACT_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_HUMAN_AUTHORIZATION_FOR_BOUND_KA_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "SEPARATE_EXPLICIT_HUMAN_ACT_THEN_SAME_GENERATION_PHASE_B_ONLY",
    }
    reseal(reduction, "reduction")
    write_canonical(reduction_path, reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    jz_result = authenticate_jz()
    e05_frontier_result = authenticate_e05_frontier()
    M.materialize(arguments)
    jz_readiness = materialize_jz_readiness(jz_result)
    finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    print(KA_TERMINAL)
