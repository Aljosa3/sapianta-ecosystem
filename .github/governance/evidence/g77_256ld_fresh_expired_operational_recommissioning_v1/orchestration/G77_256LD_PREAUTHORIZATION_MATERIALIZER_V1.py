#!/usr/bin/env python3
"""Materialize the authority-free LD EXPIRED Phase-A Human barrier.

LD authenticates committed LC, adapts the established KN Phase-A owner to
fresh LD identities, and rebinds only repository-evidence expectations to the
current LC bootstrap chain.  It has no Phase-B or operational entrypoint and
cannot create, accept, consume, transfer, or reuse Human authority.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LD = ROOT / (
    ".github/governance/evidence/"
    "g77_256ld_fresh_expired_operational_recommissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "98d059beaa148746d397d48bad9e898b1f9c2297"
TREE = "d1aadf9da3f66b2699f9b4c32647a2fe65c060cc"
SUBJECT = "G77-256LC reissue EXPIRED bootstrap digest projection"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
KN_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KN_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KN_MATERIALIZER_SHA256 = (
    "191f96810dc4fbf0afd8851381b20e143aed2105a9b60a0b671d4f2468403022"
)
KM_COMMIT = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
LC_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256lc_expired_bootstrap_digest_projection_reissue_v1"
)
LC_REDUCTION = LC_ROOT / "G77_256LC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
LC_REPORT = LC_ROOT / "G77_256LC_G48_IMPLEMENTATION_REPORT_V1.md"
LC_FORMALIZER = LC_ROOT / (
    "analysis/G77_256LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_FORMALIZER_V1.py"
)
LC_TESTS = LC_ROOT / (
    "tests/test_g77_256lc_expired_bootstrap_digest_projection_v1.py"
)
LC_HASHES = {
    LC_REDUCTION: "545822c8bc151662a022c618b137d413d5f568ef9568f5b139f968a955b498f0",
    LC_REPORT: "d8ec4ebb3b2a6d77ede833e39410a61124bc0ad51fefb792bf6759ffe6ca97fa",
    LC_FORMALIZER: "b59935f3ed782a6a05ca29cae85846482ab529cb1d02c1bb228c40173a488017",
    LC_TESTS: "92f29d85e5db78c2965a765e884252eea751b4cce932822079a1f90a7e854cab",
}
LC_REDUCTION_INNER_SHA256 = (
    "b94f4e9fa3f76faeb72d14cc81956e3ceed3e50f7a18f555ce5e002514753b50"
)
LC_TERMINAL = (
    "A__LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_REISSUED__"
    "JR_CLOUD_INIT_NOCLOUD_FM_STATIC_BINDING_VERIFIED__"
    "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION__NO_E05_CREDIT"
)
LD_TERMINAL = (
    "A__FRESH_LD_EXPIRED_MATERIALIZED_PREAUTHORIZATION_"
    "READY_FOR_HUMAN_DECISION__NO_AUTHORITY__NO_OPERATION__NO_E05_CREDIT"
)
JR_SHA256 = "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344"
FM_SHA256 = "c5172208874cca022b638511e57f091eafa01ba3c7387b182cf65d4ee98764d0"
CLOUD_SHA256 = "fdad67efe32a70784600819404222abd7a7bcee4461854fba69651513b19664e"
SEED_SHA256 = "81011b08aabb7052a14dc4f81ec51536c551cad97441563f846edbe778728004"
META_DATA_SHA256 = "081885fe7f51b064148db23dff5f4af40f58ae693879b5cb05fae24c8f23838a"
NETWORK_CONFIG_SHA256 = "639b6f419a9ac49312b218e12395dc7e7d623d96202c3315a92dcd19d6fa02ba"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
PRE_KF_FM_SHA256 = "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36"
JX_HISTORICAL_FM_SHA256 = "8f6d8df4214a0122585cf31fcd8a52ac375f766145473e25fbbe63e1c4166469"
PRE_LC_JR_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
PRE_LC_CLOUD_SHA256 = "d427ea791a6a34412af12f6fb4b8f6d6597db120d037bd13e99c9cb64f52f859"
PRE_LC_SEED_SHA256 = "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4"


class LDBarrierError(RuntimeError):
    """One deterministic fail-closed LD Phase-A error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed(path: Path, revision: str = HEAD) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT
    )


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LDBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def load_adapted_kn_materializer() -> ModuleType:
    path = ROOT / KN_MATERIALIZER
    raw = path.read_bytes()
    if raw != committed(KN_MATERIALIZER) or sha256_bytes(raw) != KN_MATERIALIZER_SHA256:
        raise LDBarrierError("COMMITTED_KN_PHASE_A_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KN", "LD").replace("kn", "ld")
    source = source.replace(KM_COMMIT, HEAD)
    source = source.replace("70aa2a12af3d9806e0d6ddc73f7f751292413e52", TREE)
    source = source.replace(
        "G77-256KM preserve GN schema for KI preflight binding", SUBJECT
    )
    source = source.replace(
        'predecessor = committed(KJ_WRAPPER, f"{HEAD}^")',
        f'predecessor = committed(KJ_WRAPPER, "{KM_COMMIT}^")',
    )
    module = ModuleType("g77_256ld_authenticated_phase_a_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


A = load_adapted_kn_materializer()
P = A.P


def authenticate_current_lc_jx() -> dict[str, Any]:
    """Authenticate current owner bytes without rewriting JX history."""

    owner = P.E.K.K.A
    identities: dict[str, str] = {}
    for path, expected in owner.JX_HASHES.items():
        raw = (ROOT / path).read_bytes()
        if raw != committed(path) or sha256_bytes(raw) != expected:
            raise LDBarrierError(f"COMMITTED_CURRENT_JX_DEPENDENCY_MISMATCH:{path}")
        identities[path.as_posix()] = expected

    envelope = owner.M.load_canonical(ROOT / owner.JX_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256")
        != sha256_bytes(owner.M.canonical_bytes(reduction))
    ):
        raise LDBarrierError("JX_TERMINAL_REDUCTION_SEAL_MISMATCH")
    role = reduction.get("role_separation", {})
    architecture = reduction.get("architecture", {})
    required_role_results = {
        "admission_repository_owner": "EXISTING_FM_FINAL_ADMISSION_AND_CONTEXT_SEAL_OWNER",
        "runtime_checkout_owner": "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER",
        "distinct_valid_roles_accepted": "VERIFIED__REPOSITORY_ONLY",
        "admission_corruption": "VERIFIED__HOST_ADMISSION_FAIL_CLOSED",
        "runtime_corruption": "VERIFIED__ER_AND_FM_FAIL_CLOSED",
        "unsealed_substitution": "VERIFIED__CONTEXT_SEAL_FAIL_CLOSED",
        "caller_provider_substitution": "VERIFIED__HOST_ADMISSION_AND_IMMUTABLE_BINDING_FAIL_CLOSED",
        "role_swap": "VERIFIED__FAIL_CLOSED",
        "missing_binding": "VERIFIED__FAIL_CLOSED",
        "stable_jr_checkout": "VERIFIED__PRESERVED",
    }
    if (
        reduction.get("terminal") != owner.JX_TERMINAL
        or any(role.get(key) != value for key, value in required_role_results.items())
        or role.get("runtime_checkout") != {"head": owner.JR_HEAD, "tree": owner.JR_TREE}
        or role.get("route_count") != 1
        or reduction.get("implementation", {}).get("adapter_after_sha256")
        != PRE_LC_JR_SHA256
        or reduction.get("implementation", {}).get("fm_after_sha256")
        != JX_HISTORICAL_FM_SHA256
        or reduction.get("implementation", {}).get("cloud_sha256")
        != PRE_LC_CLOUD_SHA256
        or reduction.get("implementation", {}).get("seed_sha256")
        != PRE_LC_SEED_SHA256
        or architecture.get("p11_implementation_mutation_count") != "VERIFIED__0"
        or architecture.get("new_owner_count") != "VERIFIED__0"
        or architecture.get("new_route_count") != "VERIFIED__0"
        or architecture.get("production_route_before") != "VERIFIED__1"
        or architecture.get("production_route_after") != "VERIFIED__1"
        or architecture.get("production_route_delta") != "VERIFIED__0"
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
    ):
        raise LDBarrierError("JX_HISTORICAL_REPAIR_CONTRACT_MISMATCH")

    if owner.M.FM.governed_checkout_identity(ROOT, "EXPIRED", HEAD, TREE) != (
        owner.JR_HEAD,
        owner.JR_TREE,
    ):
        raise LDBarrierError("CURRENT_LC_STABLE_RUNTIME_CHECKOUT_MISMATCH")
    adapter = owner.M.load_module(
        owner.ADAPTER, "g77_256ld_expired_adapter_authenticated"
    )
    er = adapter.specialize_er_harness(ROOT)
    constants = set(er.load_authenticated_fresh_operation_context.__code__.co_consts)
    if "repository_head" in constants or "repository_tree" in constants:
        raise LDBarrierError("JX_ER_ADMISSION_RUNTIME_ROLE_COLLAPSE_RECURRED")
    if not {"head", "tree"}.issubset(constants):
        raise LDBarrierError("JX_ER_RUNTIME_OBSERVATION_BINDING_MISSING")
    return {
        "terminal": owner.JX_TERMINAL,
        "artifact_hashes": identities,
        "role_separation": required_role_results,
        "stable_checkout": {"head": owner.JR_HEAD, "tree": owner.JR_TREE},
        "p11_implementation_sha256": owner.JX_HASHES[owner.P11],
        "production_route": "VERIFIED__1_TO_1",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def authenticate_lc() -> dict[str, Any]:
    for relative, expected in LC_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if raw != committed(relative) or sha256_bytes(raw) != expected:
            raise LDBarrierError(f"COMMITTED_LC_ARTIFACT_MISMATCH:{relative}")
    envelope = load_canonical(ROOT / LC_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != LC_REDUCTION_INNER_SHA256
        or sha256_bytes(canonical_bytes(reduction)) != LC_REDUCTION_INNER_SHA256
        or reduction.get("terminal") != LC_TERMINAL
        or reduction.get("frontier", {}).get("static_pre_operational_chain_complete")
        != "VERIFIED__WITHIN_AUTHENTICATED_STATIC_SCOPE"
        or reduction.get("frontier", {}).get("fresh_operational_attempt_readiness")
        != "READY__REPOSITORY_ONLY"
        or reduction.get("frontier", {}).get("readiness_blocker")
        != "NONE_KNOWN_AT_AUTHENTICATED_STATIC_BOUNDARY"
        or reduction.get("e05", {}).get("state") != "VERIFIED__11_OF_18"
        or reduction.get("e05", {}).get("frontier")
        != "VERIFIED__7_UNSATISFIED_OF_18"
        or reduction.get("e05", {}).get("current_generation_credit")
        != "VERIFIED__0"
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise LDBarrierError("LC_TERMINAL_CONTRACT_MISMATCH")
    return {
        "terminal": LC_TERMINAL,
        "head": HEAD,
        "tree": TREE,
        "reduction_path": LC_REDUCTION.as_posix(),
        "reduction_file_sha256": LC_HASHES[LC_REDUCTION],
        "reduction_inner_sha256": LC_REDUCTION_INNER_SHA256,
        "static_pre_operational_chain_complete": "VERIFIED",
        "fresh_operational_attempt_readiness": "READY__REPOSITORY_ONLY",
        "e05_state": "VERIFIED__11_OF_18",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def rebind_current_lc_assets() -> dict[str, Any]:
    fm_bindings = (
        (P.E.K.KB_HASHES, P.E.K.FM_LAUNCHER, "KB_CURRENT_LAUNCHER"),
        (P.E.K.K.EXPECTED_HASHES, P.E.K.K.FM_PATH, "COMMISSIONING_FM_OWNER"),
        (P.E.K.K.A.JX_HASHES, P.E.K.K.A.FM_PATH, "JX_FM_LAUNCHER"),
    )
    rebound: list[str] = []
    for mapping, key, label in fm_bindings:
        if mapping.get(key) != PRE_KF_FM_SHA256:
            raise LDBarrierError(f"UNEXPECTED_INHERITED_FM_BINDING:{label}")
        mapping[key] = FM_SHA256
        rebound.append(label)
    jx = P.E.K.K.A.JX_HASHES
    assets = {
        "G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py": (PRE_LC_JR_SHA256, JR_SHA256),
        "G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml": (PRE_LC_CLOUD_SHA256, CLOUD_SHA256),
        "SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img": (PRE_LC_SEED_SHA256, SEED_SHA256),
    }
    for suffix, (before, after) in assets.items():
        keys = [key for key in jx if str(key).endswith(suffix)]
        if len(keys) != 1 or jx.get(keys[0]) != before:
            raise LDBarrierError(f"UNEXPECTED_INHERITED_ASSET_BINDING:{suffix}")
        jx[keys[0]] = after
        if sha256_path(ROOT / keys[0]) != after:
            raise LDBarrierError(f"CURRENT_LC_ASSET_HASH_MISMATCH:{suffix}")
        rebound.append(suffix)
    if sha256_path(ROOT / P.FM_LAUNCHER) != FM_SHA256:
        raise LDBarrierError("CURRENT_LC_FM_HASH_MISMATCH")
    P.E.K.K.A.authenticate_jx = authenticate_current_lc_jx
    P.E.K.K.A.M.authenticate_jx = authenticate_current_lc_jx
    return {
        "classification": "EVIDENCE_EXPECTATION_REBIND_TO_COMMITTED_LC_ASSETS",
        "rebound_expectation_count": len(rebound),
        "rebound_expectations": rebound,
        "fm_sha256": FM_SHA256,
        "jr_adapter_sha256": JR_SHA256,
        "cloud_init_sha256": CLOUD_SHA256,
        "nocloud_seed_sha256": SEED_SHA256,
        "production_mutation_count": 0,
        "new_owner": False,
        "new_route": False,
    }


def cross_vector_reuse_assessment() -> dict[str, Any]:
    expected = [
        "EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT",
        "WRONG_INPUT", "WRONG_PROVENANCE",
    ]
    supported = sorted(P.M.GN.SUPPORTED_VECTORS)
    if supported != expected:
        raise LDBarrierError("CROSS_VECTOR_OWNER_SET_MISMATCH")
    return {
        "cross_vector_reuse_scope": "COMMON_PHASE_A_FM_GN_ER_P11_EX_INFRASTRUCTURE",
        "shared_owner_or_vector_specific": "SHARED_OWNERS__LD_OPERATIONAL_PROOF_VECTOR_SPECIFIC",
        "shared_preoperational_infrastructure": "VERIFIED__YES",
        "shared_authority_mechanism": "VERIFIED__YES__NO_AUTHORITY_TRANSFER",
        "shared_binding_rules": "VERIFIED__COMMON__PER_GENERATION_REVALIDATION_REQUIRED",
        "shared_defect": "VERIFIED__NO",
        "shared_required_delta": "VERIFIED__NO__LD_CONCERNS_EXPIRED_ONLY",
        "affected_vectors": ["EXPIRED"],
        "unaffected_vectors": expected[1:],
        "reuse_preconditions": "COMMITTED_LC_IDENTITY__FRESH_LD_COORDINATES__EXACT_VECTOR_BINDING",
        "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR",
        "expected_future_proof_reduction": "STATIC_OWNER_PROOF_REUSABLE__NO_OPERATIONAL_OR_E05_CREDIT_TRANSFER",
    }


def materialize_lc_preflight(
    lc: dict[str, Any], rebinding: dict[str, Any], cross_vector: dict[str, Any]
) -> dict[str, Any]:
    context_path = LD / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = load_canonical(context_path)
    fm = P.M.FM
    cloud = ROOT / fm.EXPIRED_CLOUD_INIT
    seed = ROOT / fm.EXPIRED_SEED
    command = [
        shlex.split(line.strip())
        for line in cloud.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    ]
    if len(command) != 1 or command[0][2] != JR_SHA256:
        raise LDBarrierError("MATERIALIZED_CLOUD_BOOTSTRAP_DIGEST_MISMATCH")
    projections = {
        "/user-data": cloud,
        "/meta-data": ROOT / fm.CLOUD_INIT_META_DATA,
        "/network-config": ROOT / fm.CLOUD_INIT_NETWORK_CONFIG,
    }
    for member, source in projections.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(seed), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != source.read_bytes():
            raise LDBarrierError(f"MATERIALIZED_NOCLOUD_PROJECTION_MISMATCH:{member}")
    jr = (ROOT / P.M.JR_ADAPTER).read_text(encoding="utf-8")
    p11_path = ROOT / "tests/p11_da_operational_consumer_v1.py"
    p11 = p11_path.read_text(encoding="utf-8")
    static_bindings = (
        '"authorization_reference": ACT_ID' in jr
        and '"authorized_context_sha256": gate.operation_context_sha256' in jr
        and 'input_record["authorization_reference"]' in p11
        and 'validated_act.metadata.get("authorized_context_sha256") != (' in p11
        and 'temporal_decision == "EXPIRED"' in p11
        and '_fail("one-use Human act expired before PRECLAIM")' in p11
    )
    binding = context.get("qemu_executable_base_seed_checkout_bindings", {})
    if (
        context.get("repository_head") != HEAD
        or context.get("repository_tree") != TREE
        or context.get("generation_identity") != P.M.GENERATION
        or context.get("operation_identity") != P.M.OPERATION
        or context.get("guest_adapter_binding", {}).get("source_sha256") != JR_SHA256
        or binding.get("seed", {}).get("sha256") != SEED_SHA256
        or sha256_path(p11_path) != P11_SHA256
        or not static_bindings
    ):
        raise LDBarrierError("MATERIALIZED_CURRENT_CHAIN_MISMATCH")
    proof = {
        "schema_id": "G77_256LD_LC_MATERIALIZED_PREFLIGHT_V1",
        "artifact_class": "MATERIALIZED_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": P.M.GENERATION,
        "operation_identity": P.M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "lc_authentication": lc,
        "current_asset_rebinding": rebinding,
        "cross_vector_reuse_assessment": cross_vector,
        "source_to_asset_chain": {
            "jr_adapter_sha256": JR_SHA256,
            "fm_launcher_sha256": FM_SHA256,
            "cloud_init_sha256": CLOUD_SHA256,
            "cloud_init_projected_adapter_sha256": command[0][2],
            "nocloud_user_data_sha256": CLOUD_SHA256,
            "nocloud_meta_data_sha256": META_DATA_SHA256,
            "nocloud_network_config_sha256": NETWORK_CONFIG_SHA256,
            "nocloud_seed_sha256": SEED_SHA256,
            "p11_sha256": P11_SHA256,
        },
        "materialized_context": {
            "path": context_path.relative_to(ROOT).as_posix(),
            "file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
        },
        "canonical_human_act_construction_path": "VERIFIED__STATIC_ONLY__NO_ACT_CREATED",
        "authorization_reference_propagation": "VERIFIED__EXACT_ACT_ID_EXPRESSION",
        "authorized_context_sha256_propagation": "VERIFIED__EXACT_GATE_CONTEXT_EXPRESSION",
        "p11_exact_equality_guards": "VERIFIED__UNCHANGED",
        "temporal_target": {
            "submission_time_unix_ns": 500,
            "valid_from_unix_ns": 100,
            "valid_until_unix_ns": 1000,
            "preclaim_time_unix_ns": 1000,
            "expected_denial": "one-use Human act expired before PRECLAIM",
            "expected_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        },
        "failure_class": "PROOF_GAP",
        "ready_for_human_decision": "VERIFIED",
        "human_authority_present": False,
        "phase_b_started": False,
        "operational_counters": P.M.zero_counters(),
    }
    envelope = {
        "schema_id": "G77_256LD_LC_MATERIALIZED_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = LD / "G77_256LD_LC_MATERIALIZED_PREFLIGHT_V1.json"
    A.write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__CURRENT_LC_MATERIALIZED_PREOPERATIONAL_CHAIN",
    }


def bind_lc_into_phase_a(
    lc: dict[str, Any], preflight: dict[str, Any], cross_vector: dict[str, Any]
) -> None:
    readiness_path = LD / "G77_256LD_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = LD / "G77_256LD_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = LD / "G77_256LD_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = LD / "G77_256LD_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = A.load_canonical(readiness_path)
    readiness["checkpoint"]["lc_materialized_preflight"] = preflight
    readiness["checkpoint"]["current_lc_authentication"] = lc
    readiness["checkpoint"]["human_authority_present"] = False
    readiness["checkpoint"]["phase_b_started"] = False
    A.L.reseal(readiness, "checkpoint")
    A.L.write_canonical(readiness_path, readiness)

    request = A.load_canonical(request_path)
    request["request"]["preauthorization"].update(
        {
            "checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
        }
    )
    if set(request["request"]["preauthorization"]) != A.GN_FIELDS:
        raise LDBarrierError("LD_GN_EXACT_PREAUTHORIZATION_SCHEMA_MISMATCH")
    A.L.reseal(request, "request")
    A.L.write_canonical(request_path, request)

    presentation_path.write_bytes(
        P.M.GN.render_human_authorization_presentation(request_path)
    )
    gn = P.M.GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    equivalence = A.load_canonical(equivalence_path)
    equivalence["proof"].update(
        {
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn,
        }
    )
    A.L.reseal(equivalence, "proof")
    A.L.write_canonical(equivalence_path, equivalence)

    safe_stop = A.load_canonical(safe_stop_path)
    safe_stop["checkpoint"].update(
        {
            "terminal": LD_TERMINAL,
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "readiness_checkpoint_inner_sha256": readiness["checkpoint_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_file_sha256": sha256_path(equivalence_path),
            "equivalence_inner_sha256": equivalence["proof_sha256"],
            "lc_materialized_preflight": preflight,
            "human_authority_authentication_count": 0,
            "human_authority_present": False,
            "phase_b_started": False,
        }
    )
    A.L.reseal(safe_stop, "checkpoint")
    A.L.write_canonical(safe_stop_path, safe_stop)

    reduction = A.load_canonical(reduction_path)
    value = reduction["reduction"]
    value.update(
        {
            "terminal": LD_TERMINAL,
            "project_state": "PHASE_A_READY__STOPPED_AT_HUMAN_DECISION_BOUNDARY",
            "ready_for_human_decision": "VERIFIED",
            "lc_authentication": lc,
            "lc_materialized_preflight": preflight,
            "cross_vector_reuse_assessment": cross_vector,
            "human_authority_present": False,
            "phase_b_started": False,
            "auto_continuable": False,
            "human_review_required": True,
            "existing_ld_delta_reconstruction": "VERIFIED__NONE__CLEAN_COMMITTED_LC_ENTRY",
        }
    )
    value["failure_novelty_and_convergence_check"] = {
        "failure_class": "PROOF_GAP",
        "novelty": "VERIFIED__NO_KNOWN_STATIC_FAILURE__FRESH_OPERATIONAL_OBSERVATION_ABSENT",
        "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_DENIAL_BEFORE_ATTEMPT_WITH_ZERO_EFFECT",
        "previous_closest_edge": "LC_CURRENT_BOOTSTRAP_CHAIN_AUTHORITY_FREE_STATIC_READINESS",
        "semantic_difference": "MATERIALIZED_PHASE_A_READINESS_IS_NOT_FRESH_OPERATIONAL_OBSERVATION",
        "production_behavior_impact": "VERIFIED__NONE__PHASE_A_NONOPERATIONAL",
        "new_capability_required": "VERIFIED__NO",
        "new_proof_required": "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_OBSERVATION",
        "convergence_signal": "VERIFIED__KY_KZ_LA_LB_LC_STATIC_SEQUENCE_REACHES_HUMAN_DECISION_BOUNDARY",
        "repetition_pressure": "ESTIMATED__HIGH__PRIOR_ATTEMPTS_PRODUCED_ZERO_EXPIRED_CREDIT",
        "verification_amplification_risk": "ESTIMATED__HIGH_IF_PHASE_A_REPEATS_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
        "classification_confidence": "VERIFIED__HIGH",
    }
    value["phase_a_wrapper_defect_disposition"] = {
        "classification": "EVIDENCE_OR_REPORTING_DEFECT__HARNESS_OR_TEST_ARTIFACT",
        "jz_authentication_map_rebinding": "CORRECTED__CURRENT_COMMITTED_REPAIR_CONTRACT_AUTHENTICATED",
        "nocloud_filename_lookup": "CORRECTED__FM_OWNER_PATH_CONSTANTS_USED",
        "aggregate_current_chain_assertion": "CORRECTED__DECOMPOSED_INTO_INDIVIDUALLY_AUTHENTICATED_FACTS",
        "inherited_entry_label": "CORRECTED__CLEAN_COMMITTED_LC_ENTRY",
        "production_behavior_impact": "VERIFIED__NONE",
        "new_capability_required": "VERIFIED__NO",
    }
    value["frontier"] = {
        "previous_last_verified_edge": "LC_CURRENT_JR_CLOUD_INIT_NOCLOUD_FM_STATIC_READINESS",
        "current_last_verified_edge": "LD_CURRENT_MATERIALIZED_PREOPERATIONAL_CHAIN_AND_PRESENTATION_READY",
        "previous_first_broken_edge": "NONE_KNOWN_AT_LC_STATIC_BOUNDARY",
        "current_first_broken_edge": "NONE_KNOWN__HUMAN_AUTHORITY_NOT_YET_CREATED_IS_EXPECTED_BOUNDARY",
        "first_unverified_operational_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
        "constitutional_frontier_movement": "VERIFIED__LC_REPOSITORY_READINESS_TO_LD_MATERIALIZED_HUMAN_BARRIER",
        "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
        "minimum_missing_capability": "NO_NEW_CAPABILITY__FRESH_BOUND_HUMAN_AUTHORITY_AND_OBSERVATION_REQUIRED",
        "minimum_missing_proof": "ONE_FRESH_EXPIRED_DENIAL_BEFORE_P11_ENTRY_WITH_ZERO_EFFECT",
        "minimum_legal_next_delta": "ONLY_AFTER_FRESH_HUMAN_CREATED_LD_AUTHORIZATION_SOURCE__SAME_LD_PHASE_B__ONE_CONSUMPTION__ONE_ATTEMPT",
    }
    value["architecture"] = {
        "production_mutation_count": 0,
        "p11_implementation_mutation_count": 0,
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "production_route_before": 1,
        "production_route_after": 1,
        "parallel_flow": "NO",
    }
    value["owner_results"]["lc_materialized_preflight"] = preflight["result"]
    value["identities"].update(
        {
            "request_sha256": request["request_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "readiness_checkpoint_sha256": readiness["checkpoint_sha256"],
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_sha256": safe_stop["checkpoint_sha256"],
            "checkpoint_file_sha256": sha256_path(safe_stop_path),
            "lc_materialized_preflight_sha256": preflight["inner_sha256"],
            "lc_materialized_preflight_file_sha256": preflight["file_sha256"],
        }
    )
    value["operational_counters"] = P.M.zero_counters()
    value["e05"] = {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0",
        "expired_status": "NOT_PROVEN_OPERATIONALLY",
    }
    value["proof_yield"] = {
        "materialized_preflight_readiness": "VERIFIED",
        "new_operational_capability_count": 0,
        "new_blocker_localized_count": 0,
        "authority_spent": 0,
        "operation_spent": 0,
        "e05_credit": 0,
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "LC__EX_17_OF_17__KM__KI__JZ__KB__KD__KF__GN__FM__ER__P11__SOLE_ROUTE",
        "new_capabilities": "LD_MATERIALIZED_PHASE_A_READINESS_ONLY__NONAUTHORITY__NONOPERATIONAL",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__LD_PHASE_A_READY_AT_HUMAN_DECISION_BOUNDARY",
            "informal_project_progress_estimate": "ESTIMATED__MATERIALIZED_PREFLIGHT_COMPLETE__FRESH_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__CURRENT_LC_BINDINGS__MATERIALIZED_CHAIN__ALL_COUNTERS_ZERO__ONE_ROUTE",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__CURRENT_LC_AND_EXISTING_PHASE_A_OWNERS_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PHASE_A_REPEATED_BEFORE_HUMAN_DECISION",
            "cognition_provenance": "INDEPENDENTLY_HUMAN_AUTHENTICATED_LC_CHECKPOINT__DURABLE_DIRTY_LD_WORKSPACE__HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF__CURRENT_ACCOUNT_REAUTHENTICATION",
            "cognition_assisted_handoff": "VERIFIED__ONLY_INDEPENDENTLY_REAUTHENTICATED_DURABLE_FACTS__NO_HIDDEN_REASONING_CONTINUITY_CLAIMED",
            "candidate_capability": "VERIFIED__LD_MATERIALIZED_PHASE_A_READINESS__OPERATIONAL_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE__ONE_AUTHORITY__ONE_ATTEMPT_MAXIMUM",
            "constitutional_continuation_progress": "VERIFIED__LC_STATIC_READY_TO_LD_MATERIALIZED_HUMAN_BARRIER",
        }
    )
    value["ccwim"].update(
        {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "cross_account_continuation": "VERIFIED__SAME_G77_256LD_GENERATION",
            "predecessor_terminal_authenticated": "VERIFIED__YES",
            "predecessor_commit_authenticated": "VERIFIED__YES",
            "predecessor_remote_equality": "VERIFIED__YES",
            "nested_authority_authenticated": "VERIFIED__YES",
            "repository_evidence_primary": "VERIFIED__YES",
            "active_generation_reused": "VERIFIED__G77_256LD",
            "dirty_workspace_reauthenticated": "VERIFIED__AUTHORIZED_LD_SCOPE_ONLY",
            "previous_session_durable_evidence_reused": "VERIFIED__YES",
            "current_account_reauthentication": "VERIFIED__YES",
            "previous_generation_evidence_reused": "VERIFIED__YES",
            "current_generation_reauthentication": "VERIFIED__YES",
            "human_decision_boundary_preserved": "VERIFIED__YES",
            "human_authority_created": 0,
            "authority_consumed": 0,
            "operation_performed": 0,
            "handoff_ambiguity_count": 0,
            "binding_owner_ambiguity_count": 0,
            "authority_state_ambiguity_count": 0,
            "operational_attempt_ambiguity_count": 0,
            "cross_account_recovery": "VERIFIED",
            "cross_account_recovery_source": "DURABLE_DIRTY_LD_WORKSPACE__HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF__CURRENT_ACCOUNT_REAUTHENTICATION",
            "previous_worker_conversation_required": "VERIFIED__HUMAN_PROVIDED_HANDOFF_USED",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__DURABLE_ARTIFACT_REAUTHENTICATION_ONLY",
        }
    )
    value["periodic_metrics"] = {
        "aigol_codex_work_share": "NOT_MEASURED__NO_GOVERNED_ATTRIBUTION_DENOMINATOR",
        "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT",
        "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
        "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR",
        "full_ccwim": "NOT_MEASURED__NO_GOVERNED_FULL_CCWIM_DENOMINATOR_OR_SCHEMA",
    }
    value["hac_hai_hae"] = (
        "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
    )
    A.L.reseal(reduction, "reduction")
    A.L.write_canonical(reduction_path, reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


def complete_human_decision_presentation() -> None:
    """Append the exact bounded decision without constructing Human authority."""

    path = LD / "G77_256LD_HUMAN_DECISION_PRESENTATION_V1.txt"
    existing = path.read_text(encoding="utf-8").rstrip("\n")
    exact_boundary = "\n".join(
        [
            "BEGIN EXACT BOUNDED HUMAN DECISION",
            "GENERATION = G77-256LD",
            f"GENERATION_IDENTITY = {P.M.GENERATION}",
            f"OPERATION_IDENTITY = {P.M.OPERATION}",
            "VECTOR = EXPIRED",
            "TARGET_ACCEPTANCE_EDGE = EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
            "MAX_AUTHORITY_CONSUMPTION = 1",
            "MAX_OPERATION_ATTEMPT = 1",
            "SECOND_OPERATION = FORBIDDEN",
            "RETRY = FORBIDDEN",
            "REPLAY = FORBIDDEN",
            "REPAIR_RETRY = FORBIDDEN",
            "ALTERNATE_AUTHORITY_PATH = FORBIDDEN",
            "P11_BYPASS = FORBIDDEN",
            "PARALLEL_ROUTE = FORBIDDEN",
            "AUTHORITY_TRANSFER = FORBIDDEN",
            "HISTORICAL_AUTHORITY_REUSE = FORBIDDEN",
            "PRODUCTION_EXPANSION = FORBIDDEN",
            "CURRENT_E05_STATE = 11_OF_18",
            "POTENTIAL_E05_RESULT = AT_MOST_ONE_EXPIRED_ACCEPTANCE_CREDIT_IF_EXACT_AUTHENTICATED_ACCEPTANCE_IS_OBSERVED",
            "READY_FOR_HUMAN_DECISION = VERIFIED",
            "HUMAN_AUTHORITY_CREATED = 0",
            "AUTHORITY_CONSUMPTION_COUNT = 0",
            "QEMU_START_COUNT = 0",
            "VM_START_COUNT = 0",
            "OPERATION_ATTEMPT_COUNT = 0",
            "E05_CREDIT = 0",
            "DECISION_SOURCE_REQUIREMENT = FRESH_HUMAN_CREATED_BYTES_SUPPLIED_SEPARATELY_AFTER_REVIEW",
            "END EXACT BOUNDED HUMAN DECISION",
            "STOP. DO NOT GENERATE THE HUMAN ANSWER.",
        ]
    )
    path.write_bytes(f"{existing}\n{exact_boundary}\n".encode("utf-8"))


if __name__ == "__main__":
    arguments = parse_args()
    lc_result = authenticate_lc()
    cross_vector_result = cross_vector_reuse_assessment()
    km_result = A.authenticate_km()
    ki_result = A.L.authenticate_ki()
    kf_result = P.authenticate_kf()
    rebound_result = rebind_current_lc_assets()
    kd_proof = P.E.authenticate_kd_interface_before_presentation()
    kb_result = P.E.K.authenticate_kb()
    jz_result = P.E.K.K.authenticate_jz()
    e05_result = P.E.K.K.authenticate_e05_frontier()
    P.M.materialize(arguments)
    namespace_result = P.E.augment_namespace_preflight(
        P.E.K.materialize_namespace_preflight(kb_result)
    )
    jz_readiness = P.E.K.K.materialize_jz_readiness(jz_result)
    P.E.K.K.finalize_phase_a(jz_result, jz_readiness, e05_result)
    P.E.K.bind_namespace_into_phase_a(kb_result, namespace_result)
    kd_result = P.E.materialize_kd_preflight(kd_proof)
    P.E.bind_kd_preflight_into_phase_a(kd_result)
    kf_preflight = P.materialize_kf_preflight(kf_result, rebound_result)
    P.bind_kf_into_phase_a(kf_result, kf_preflight)
    ki_preflight = A.L.materialize_ki_preflight(ki_result)
    A.L.bind_ki_into_phase_a(ki_result, ki_preflight)
    km_preflight = A.materialize_km_preflight(km_result, cross_vector_result)
    A.bind_km_into_phase_a(km_result, km_preflight, cross_vector_result)
    lc_preflight = materialize_lc_preflight(
        lc_result, rebound_result, cross_vector_result
    )
    bind_lc_into_phase_a(lc_result, lc_preflight, cross_vector_result)
    P.E.materialize_human_decision_presentation()
    complete_human_decision_presentation()
    print(LD_TERMINAL)
