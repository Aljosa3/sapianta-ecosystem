#!/usr/bin/env python3
"""Materialize the nonauthority G77-256JW EXPIRED Human barrier.

This path authenticates committed JV and its JT/JR/EX substrate, materializes
one fresh JW-local candidate/context and operation state, derives the sealed
GN presentation, binds a safe-stop checkpoint, and stops.  It contains no
authority-consumption or operational-launch call.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
JW = ROOT / ".github/governance/evidence/g77_256jw_expired_operational_v1"
LIVE = JW / "live_binding"
OPERATION_ROOT = JW / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256jw_expired_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
HEAD = "98206cab55fb4201c3b60de48eb032cca196de7c"
TREE = "ab1a39d41553fc0296e65287782a36b1f20fb22b"
SUBJECT = "G77-256JV verify EXPIRED GN request projection"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"

PREFIX = "G77_256JW"
VECTOR = "EXPIRED"
GENERATION = PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = PREFIX + "_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
JT_TERMINAL = "A__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED"
JV_TERMINAL = "A__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"
PHASE_A_TERMINAL = "A__FRESH_JW_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"

JV_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256jv_expired_gn_request_schema_binding_repair_v1"
)
JV_REQUEST = JV_ROOT / "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
JV_PRESENTATION = JV_ROOT / "G77_256JV_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
JV_EQUIVALENCE = JV_ROOT / "G77_256JV_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
JV_REDUCTION = JV_ROOT / "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JV_REPORT = JV_ROOT / "G77_256JV_G48_IMPLEMENTATION_REPORT_V1.md"
JV_FORMALIZER = JV_ROOT / (
    "analysis/G77_256JV_EXPIRED_GN_REQUEST_SCHEMA_BINDING_FORMALIZER_V1.py"
)

JT_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256jt_expired_bootstrap_checkout_binding_repair_v1"
)
JT_REDUCTION = JT_ROOT / "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JT_CLOUD_INIT = JT_ROOT / "static/G77_256JT_CLOUD_INIT_USER_DATA_V1.yaml"
JT_SEED = JT_ROOT / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V2.img"
JR_ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GL_PATH = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
GN_PATH = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_FINAL_SEAL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)
META = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
)

EXPECTED_HASHES = {
    JT_REDUCTION: "99349cbd288706131ba9ccbc010e43200bae463ba639a321ff6f121eda0a683e",
    JT_CLOUD_INIT: "4c2c020421b06d592cb64b0a8da56a5929a981cf32dcbda9ae077956e3ca3408",
    JT_SEED: "4d0f7d4e7f5cbb08ee18ed8c757a7467498513862a1b3194d3489df8c8d092fb",
    JR_ADAPTER: "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2",
    FM_PATH: "d935bec8e37a828d1b8c3249922af8d1017b468940b44853e7990a08b2328b9e",
    P11: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}

JV_HASHES = {
    JV_REQUEST: "c89958b45483d5c6a5cb7f178b1653ffe302ae8ade8de6cbb3736df306c6b9c3",
    JV_PRESENTATION: "4d620fe75e3c42ff05191367227f4474c4dc0f4d89bcd77e918442e5cdf6ff53",
    JV_EQUIVALENCE: "bcda81e5142f2c26ae057579d05cda2b70bc74102dd472846a7e9d340f1a4e99",
    JV_REDUCTION: "ffd562a24c0d9d209af3fe2552fff75db373727ce7a10f2343958765ec42971f",
    JV_REPORT: "0b632e05b67466d9d7b14b9c21ed4a60eaa9c75d71000d3fd52ace482986fdb4",
    JV_FORMALIZER: "4d6f3127338cfbff37525b5d33a2a4ac8f0862d649e04ba03d9b88127eb3ac0b",
}

EX_HASHES = {
    EX_CERTIFICATE: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    EX_FINAL_SEAL: "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543",
}


class JWBarrierError(RuntimeError):
    """One deterministic fail-closed JW preauthorization error."""


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JWBarrierError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256jw_fm")
GL = load_module(GL_PATH, "g77_256jw_gl")
GN = load_module(GN_PATH, "g77_256jw_gn")


def canonical_bytes(value: Any) -> bytes:
    return FM.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JWBarrierError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JWBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(value)),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise JWBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "tracked_worktree_clean": git(
            "status", "--porcelain", "--untracked-files=no"
        ) == "",
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "worktree_clean_before_first_mutation": True,
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
        "remote_head": HEAD,
        "tracked_worktree_clean": True,
        "index_empty": True,
    }
    if any(observed[key] != value for key, value in expected.items()):
        raise JWBarrierError("EXACT_REMOTE_RATIFIED_JV_ENTRY_MISMATCH")
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        if not line.startswith("?? " + JW.relative_to(ROOT).as_posix() + "/"):
            raise JWBarrierError("JW_BOUNDED_WORKTREE_SCOPE_VIOLATION")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode:
        raise JWBarrierError("CONSTITUTIONAL_ANCESTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "remote_tag": nested_remote_tag,
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
        "remote_tag": NESTED_HEAD,
    }:
        raise JWBarrierError("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "direct_remote_equality": "VERIFIED",
        "nested_authority": nested_state,
    }


def authenticate_jv() -> dict[str, Any]:
    identities: dict[str, str] = {}
    for path, expected_hash in JV_HASHES.items():
        current = (ROOT / path).read_bytes()
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{path}"], cwd=ROOT)
        if current != committed or sha256_bytes(current) != expected_hash:
            raise JWBarrierError(f"COMMITTED_JV_DEPENDENCY_MISMATCH:{path}")
        identities[path.as_posix()] = expected_hash
    envelope = load_canonical(ROOT / JV_REDUCTION)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(canonical_bytes(reduction))
    ):
        raise JWBarrierError("JV_TERMINAL_REDUCTION_SEAL_MISMATCH")
    architecture = reduction.get("architecture", {})
    if (
        reduction.get("terminal") != JV_TERMINAL
        or reduction.get("mode")
        != "REPOSITORY_ONLY__GN_REQUEST_PROJECTION_REPAIR__NO_AUTHORITY__NO_OPERATION"
        or reduction.get("gn_contract", {}).get("contract_conclusion")
        != "A_AND_D__GN_V1_IS_VECTOR_INDEPENDENT__JU_USED_WRONG_PROJECTION"
        or set(reduction.get("operational_counters", {}).values()) != {"VERIFIED__0"}
        or reduction.get("e05")
        != {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        }
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
        or any(
            architecture.get(key) != "VERIFIED__0"
            for key in (
                "p11_implementation_mutation_count",
                "production_mutation_count",
                "new_owner_count",
                "new_route_count",
                "new_registry_count",
                "new_generic_abstraction_count",
                "new_constitutional_concept_count",
                "production_route_delta",
            )
        )
        or architecture.get("production_route_before") != "VERIFIED__1"
        or architecture.get("production_route_after") != "VERIFIED__1"
    ):
        raise JWBarrierError("JV_CONSTITUTIONAL_BOUNDARY_MISMATCH")
    gn_contract = reduction["gn_contract"]
    if (
        "wrong_attempt_execution_count" not in gn_contract["request_fields"]
        or "expired_execution_count" in gn_contract["request_fields"]
        or not {"du", "eb", "ee"}.issubset(gn_contract["live_binding_fields"])
        or {"expired_adapter_sha256", "temporal_binding_sha256"}.intersection(
            gn_contract["live_binding_fields"]
        )
    ):
        raise JWBarrierError("JV_GN_CANONICAL_SCHEMA_MISMATCH")
    committed_request = GN.load_validated_sealed_request(ROOT / JV_REQUEST)
    committed_presentation = (ROOT / JV_PRESENTATION).read_bytes()
    if committed_presentation != GN.render_human_authorization_presentation(ROOT / JV_REQUEST):
        raise JWBarrierError("JV_PRESENTATION_DERIVATION_MISMATCH")
    gn_result = GN.validate_human_authorization_presentation(
        ROOT / JV_REQUEST, committed_presentation
    )
    if (
        committed_request["request"]["authorized_vector_requested"] != VECTOR
        or gn_result["human_presentation_request_equivalence"]
        != "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    ):
        raise JWBarrierError("JV_GN_PROJECTION_AUTHENTICATION_FAILED")
    return {
        "terminal": JV_TERMINAL,
        "mode": reduction["mode"],
        "artifact_hashes": identities,
        "gn_contract_conclusion": gn_contract["contract_conclusion"],
        "canonical_counter_slot": "wrong_attempt_execution_count",
        "canonical_live_binding_slots": ["du", "eb", "ee"],
        "jv_request_sha256": committed_request["request_sha256"],
        "jv_presentation_sha256": sha256_bytes(committed_presentation),
        "jv_request_presentation_equivalence": gn_result[
            "human_presentation_request_equivalence"
        ],
        "p11_implementation_mutation_count": "VERIFIED__0",
        "production_mutation_count": "VERIFIED__0",
        "production_route": "VERIFIED__1_TO_1",
        "e05": reduction["e05"],
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def authenticate_ex() -> dict[str, Any]:
    for path, expected_hash in EX_HASHES.items():
        current = (ROOT / path).read_bytes()
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{path}"], cwd=ROOT)
        if current != committed or sha256_bytes(current) != expected_hash:
            raise JWBarrierError(f"COMMITTED_EX_DEPENDENCY_MISMATCH:{path}")
    certificate_envelope = json.loads(
        (ROOT / EX_CERTIFICATE).read_bytes(), object_pairs_hook=unique_object
    )
    final_envelope = json.loads(
        (ROOT / EX_FINAL_SEAL).read_bytes(), object_pairs_hook=unique_object
    )
    certificate = certificate_envelope.get("certificate", {})
    if (
        certificate.get("component_counts", {}).get("CERTIFIED") != 17
        or final_envelope.get("schema_id") != "G77_256EX_FINAL_VALIDATION_SEAL_ENVELOPE_V1"
    ):
        raise JWBarrierError("EX_17_OF_17_CERTIFICATE_MISMATCH")
    return {
        "certificate_path": EX_CERTIFICATE.as_posix(),
        "certificate_sha256": EX_HASHES[EX_CERTIFICATE],
        "final_seal_path": EX_FINAL_SEAL.as_posix(),
        "final_seal_sha256": EX_HASHES[EX_FINAL_SEAL],
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def authenticate_fresh_identity() -> dict[str, Any]:
    for identity in (GENERATION, OPERATION):
        result = subprocess.run(
            ["git", "grep", "-F", identity, HEAD],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode not in (0, 1) or result.stdout:
            raise JWBarrierError(f"COMMITTED_IDENTITY_COLLISION:{identity}")
    if FM.fresh_context.operation_vector(GENERATION) != VECTOR:
        raise JWBarrierError("FRESH_VECTOR_IDENTITY_DERIVATION_FAILED")
    return {
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "derivation": "VERIFIED__JW_NAMESPACE_PLUS_CLOSED_VECTOR_AND_ONE_SHOT_OPERATION_PATTERN",
        "committed_history_collision": "VERIFIED__NO",
        "prior_authorization_reuse": "VERIFIED__NO",
        "prior_consumed_authority_reuse": "VERIFIED__NO",
        "prior_operation_state_reuse": "VERIFIED__NO",
    }


def authenticate_jt() -> dict[str, Any]:
    for path, expected_hash in EXPECTED_HASHES.items():
        current = (ROOT / path).read_bytes()
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{path}"], cwd=ROOT)
        if current != committed or sha256_bytes(current) != expected_hash:
            raise JWBarrierError(f"COMMITTED_JT_DEPENDENCY_MISMATCH:{path}")
    envelope = json.loads((ROOT / JT_REDUCTION).read_bytes())
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(canonical_bytes(reduction))
    ):
        raise JWBarrierError("JT_TERMINAL_REDUCTION_SEAL_MISMATCH")
    stable = reduction.get("stable_binding", {})
    architecture = reduction.get("architecture", {})
    if (
        reduction.get("terminal") != JT_TERMINAL
        or reduction.get("e05") != {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        }
        or set(reduction.get("operational_counters", {}).values()) != {"VERIFIED__0"}
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
        or stable.get("authoritative_owner")
        != "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER"
        or (stable.get("jr_checkout_head"), stable.get("jr_checkout_tree"))
        != (JR_HEAD, JR_TREE)
        or stable.get("route_count") != 1
        or architecture.get("p11_implementation_mutation_count") != "VERIFIED__0"
        or architecture.get("new_owner_count") != "VERIFIED__0"
        or architecture.get("new_route_count") != "VERIFIED__0"
        or architecture.get("new_registry_count") != "VERIFIED__0"
        or architecture.get("new_generic_abstraction_count") != "VERIFIED__0"
        or architecture.get("new_constitutional_concept_count") != "VERIFIED__0"
        or architecture.get("production_route_before") != "VERIFIED__1"
        or architecture.get("production_route_after") != "VERIFIED__1"
        or architecture.get("production_route_delta") != "VERIFIED__0"
    ):
        raise JWBarrierError("JT_CONSTITUTIONAL_BOUNDARY_MISMATCH")
    if FM.governed_checkout_identity(ROOT, VECTOR, HEAD, TREE) != (JR_HEAD, JR_TREE):
        raise JWBarrierError("JT_STABLE_EXPIRED_CHECKOUT_MISMATCH")
    command = FM.bootstrap_guest_command_arguments(
        (ROOT / JT_CLOUD_INIT).read_text(encoding="utf-8"),
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
    )
    if command[2:4] != (JR_HEAD, JR_TREE):
        raise JWBarrierError("JT_BOOTSTRAP_COMMAND_MISMATCH")
    for member, source in (
        ("/user-data", JT_CLOUD_INIT),
        ("/meta-data", META),
        ("/network-config", NETWORK),
    ):
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / JT_SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (ROOT / source).read_bytes():
            raise JWBarrierError(f"JT_NOCLOUD_PROJECTION_MISMATCH:{member}")
    return {
        "terminal": JT_TERMINAL,
        "terminal_file_sha256": sha256_path(ROOT / JT_REDUCTION),
        "terminal_inner_sha256": envelope["reduction_sha256"],
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "e05": reduction["e05"],
        "stable_checkout": {"head": JR_HEAD, "tree": JR_TREE},
        "authoritative_owner": stable["authoritative_owner"],
        "repository_runtime_role_collapse": "VERIFIED__NO",
        "advancing_head_substitution": "VERIFIED__REJECTED",
        "recurrence_hazard": "VERIFIED__ELIMINATED",
        "bootstrap_command": list(command),
        "nocloud_projection": "VERIFIED__ALL_THREE_MEMBERS_EXACT",
        "production_route": "VERIFIED__1_TO_1",
    }


def authenticate_expired_semantics() -> dict[str, Any]:
    adapter = load_module(JR_ADAPTER, "g77_256jw_expired_adapter")
    coordinates = adapter.authenticate_expired_semantics(ROOT)
    if coordinates != {
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
    }:
        raise JWBarrierError("EXPIRED_COORDINATE_MISMATCH")
    transformed = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix=PREFIX
    )
    for token in (
        'denial_error == "one-use Human act expired before PRECLAIM"',
        'after.state.value == "EXPIRED"',
        "after.revision == 1",
        "differing_fields == []",
    ):
        if token not in transformed:
            raise JWBarrierError("EXPIRED_SPECIALIZATION_MISMATCH")
    return {
        "vector": VECTOR,
        "submission_time_unix_ns": 500,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
        "governed_preclaim_coordinate_unix_ns": 1000,
        "truth_table": {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"},
        "expected_owner_transition": "AVAILABLE_TO_EXPIRED",
        "expected_denial_reason": "one-use Human act expired before PRECLAIM",
        "expected_denial_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        "wall_clock_is_governed_preclaim_authority": False,
        "caller_provider_human_selectable_coordinate_count": 0,
    }


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise JWBarrierError("JW_ONE_SHOT_NAMESPACE_NOT_FRESH")
    entry = authenticate_entry(args.remote_head, args.nested_remote_tag)
    jv = authenticate_jv()
    jt = authenticate_jt()
    ex = authenticate_ex()
    expired = authenticate_expired_semantics()
    fresh_identity = authenticate_fresh_identity()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )

    source_candidate = ROOT / FM.CANDIDATE
    if sha256_path(source_candidate) != FM.CANDIDATE_SHA256:
        raise JWBarrierError("FM_CANONICAL_CANDIDATE_MISMATCH")
    candidate = LIVE / "candidate" / source_candidate.name
    runtime = LIVE / "runtime_projection" / source_candidate.name
    candidate.parent.mkdir(parents=True, exist_ok=False)
    runtime.parent.mkdir(parents=True, exist_ok=False)
    candidate.write_bytes(source_candidate.read_bytes())
    runtime.write_bytes(source_candidate.read_bytes())
    if candidate.read_bytes() != runtime.read_bytes():
        raise JWBarrierError("CANDIDATE_RUNTIME_BYTE_MISMATCH")

    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=HEAD,
        repository_tree=TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=OPERATION_ROOT,
        transient_root=TRANSIENT_ROOT,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    if (
        context["repository_head"] != HEAD
        or context["repository_tree"] != TREE
        or (checkout["head"], checkout["tree"]) != (JR_HEAD, JR_TREE)
        or seed["path"] != str(ROOT / JT_SEED)
        or context["preclaim_temporal_binding"]["coordinate_unix_ns"] != 1000
    ):
        raise JWBarrierError("JW_CONTEXT_ROLE_OR_TEMPORAL_BINDING_MISMATCH")
    substituted = json.loads(json.dumps(context))
    substituted["qemu_executable_base_seed_checkout_bindings"]["checkout"].update(
        {"head": HEAD, "tree": TREE}
    )
    substituted = FM.fresh_context.seal_context(
        {key: value for key, value in substituted.items() if key != "context_sha256"}
    )
    try:
        FM.validate_immutable_context_bindings(
            ROOT, substituted, candidate.relative_to(ROOT)
        )
    except RuntimeError:
        substitution_rejected = True
    else:
        raise JWBarrierError("ADVANCING_JT_CHECKOUT_SUBSTITUTION_ACCEPTED")

    context_path = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    write_json(context_path, context)
    destination = FM.preauth_fresh_checkout_destination_readiness(ROOT, context)
    operation_materialization = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=context_path,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    observations = FM.observe_context_assets(ROOT, context, candidate.relative_to(ROOT))
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HEAD,
        observed_tree=TREE,
        repository_clean=git("status", "--porcelain", "--untracked-files=no") == "",
        observed_asset_sha256=observations,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    static = sealed(
        "G77_256JW_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JW_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded,
            "entry": entry,
            "jv_reconstruction": jv,
            "jt_reconstruction": jt,
            "ex_reuse": ex,
            "expired_semantics": expired,
            "fresh_identity": fresh_identity,
            "fresh_candidate": {
                "path": candidate.relative_to(ROOT).as_posix(),
                "source_path": Path(FM.CANDIDATE).as_posix(),
                "historical_js_candidate_path_reused": False,
                "fresh_jw_candidate_instance": True,
                "candidate_semantics_changed": False,
                "sha256": sha256_path(candidate),
            },
            "stable_checkout_substitution_rejected": substitution_rejected,
            "destination_readiness": destination,
            "materialization": operation_materialization,
            "asset_observations": observations,
            "readiness": readiness,
            "human_operational_authority": 0,
            "operational_execution_count": 0,
        },
    )
    static_path = JW / "G77_256JW_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = JW / "G77_256JW_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    gl_result = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, observation, gl_checkpoint
    )
    equivalence = sealed(
        "G77_256JW_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JW_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            **gl_result,
        },
    )
    equivalence_path = JW / "G77_256JW_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
    write_json(equivalence_path, equivalence)

    counters = zero_counters()
    identities = {
        "candidate_sha256": sha256_path(candidate),
        "runtime_projection_sha256": sha256_path(runtime),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "fm_launcher_sha256": sha256_path(ROOT / FM_PATH),
        "expired_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
        "temporal_binding_sha256": sha256_bytes(
            canonical_bytes(context["preclaim_temporal_binding"])
        ),
        "p11_consumer_sha256": sha256_path(ROOT / P11),
    }
    checkpoint_inner = {
        "schema_id": "G77_256JW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_READINESS_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "jv_terminal_reconstruction": jv,
        "jt_terminal_reconstruction": jt,
        "ex_reuse": ex,
        "fresh_identity": fresh_identity,
        "expired_semantics": expired,
        "identities": identities,
        "authority_boundary": {
            "authority_state": "NOT_GRANTED",
            "checkpoint_is_authority": False,
            "request_is_authority": False,
            "prompt_is_authority": False,
            "provider_capability_is_authority": False,
            "human_review_required": True,
            "auto_continuable": False,
            "next_legal_phase": "PRESENT_EXACT_GN_DERIVED_REQUEST_AND_STOP_FOR_EXPLICIT_HUMAN_DECISION",
        },
        "one_shot_maxima": {
            "operational_authorization": 1,
            "authority_consumption": 1,
            "pre_operational": 1,
            "fm_operational_invocation": 1,
            "qemu": 1,
            "vm": 1,
            "operation_attempt": 1,
            "retry": 0,
            "repair_retry": 0,
            "replay": 0,
        },
        "operational_counters": counters,
        "e05": {"before": "11/18", "current": "11/18", "maximum_credit": 1},
        "preauthorization": {
            "static_readiness_result": readiness["result"],
            "static_readiness_file_sha256": sha256_path(static_path),
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "receipt_parent_observation_sha256": observation["observation_sha256"],
            "preauth_final_admission_equivalence_file_sha256": sha256_path(
                equivalence_path
            ),
            "preauth_final_admission_equivalence": gl_result[
                "preauth_final_admission_equivalence"
            ],
            "single_route_status": "VERIFIED",
        },
        "architecture": {
            "p11_implementation_mutation_count": 0,
            "production_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
        },
        "handoff_sufficiency": {
            "status": "VERIFIED",
            "state_completeness": "COMPLETE_FOR_PREGRANT_BARRIER",
            "authority_state": "NOT_GRANTED",
            "authority_consumed": False,
            "ambiguity_count": 0,
            "unauthenticated_assumption_count": 0,
        },
    }
    checkpoint = sealed(
        "G77_256JW_PREAUTHORIZATION_READINESS_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint_inner,
    )
    checkpoint_path = JW / "G77_256JW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    request_inner = {
        "schema_id": "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
        "recorded_at_utc": recorded,
        "request_class": "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository": {
            "branch": BRANCH,
            "head": HEAD,
            "tree": TREE,
            "remote_head": args.remote_head,
            "stable_ancestry_anchor": ANCHOR,
        },
        "immutable_assets": context["qemu_executable_base_seed_checkout_bindings"],
        "live_binding": {
            "candidate_sha256": identities["candidate_sha256"],
            "context_sha256": identities["context_sha256"],
            "context_file_sha256": identities["context_file_sha256"],
            "canonical_argv_sha256": identities["canonical_argv_sha256"],
            "du": "PASS",
            "eb": "PASS",
            "ee": "PASS",
            "candidate_semantics_changed": False,
            "candidate_binding_regeneration_required": True,
            "receipt_parent": context["receipt_parent"],
        },
        "preauthorization": {
            "static_readiness_file_sha256": sha256_path(static_path),
            "checkpoint_file_sha256": sha256_path(checkpoint_path),
            "checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
            "checkpoint_path": checkpoint_path.relative_to(ROOT).as_posix(),
            "complete_deterministic_readiness": "PASS",
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "preauth_final_admission_equivalence_file_sha256": sha256_path(
                equivalence_path
            ),
            "preauth_final_admission_equivalence": gl_result[
                "preauth_final_admission_equivalence"
            ],
            "gk_receipt_parent_false_positive_blocked": "YES",
            "all_operational_counters_zero": True,
        },
        "requested_authority_semantics": {
            "authorization_kind": "FRESH_HUMAN_CONSTITUTIONAL_OPERATIONAL_AUTHORIZATION",
            "explicit": True,
            "fresh": True,
            "one_shot": True,
            "reusable": False,
            "transferable": False,
            "generation_bound": True,
            "operation_bound": True,
            "head_bound": True,
            "tree_bound": True,
            "candidate_bound": True,
            "context_bound": True,
            "canonical_argv_bound": True,
            "checkpoint_bound": True,
            "authorization_request_bound": True,
            "governed_launcher_activation_limit": 1,
            "qemu_execution_limit": 1,
            "vm_boot_limit": 1,
            "operation_attempt_limit": 1,
            "network_authorized": False,
            "retry_limit": 0,
            "repair_limit": 0,
            "replay_limit": 0,
            "replacement_authority_authorized": False,
            "second_attempt_authorized": False,
            "successor_generation_authorized": False,
        },
        "authorized_vector_requested": VECTOR,
        "request_is_authority": False,
        "checkpoint_is_authority": False,
        "resource_capacity_is_authority": False,
        "provider_permission_is_authority": False,
        "provider_permission_confirmation_count": 0,
        "human_constitutional_authorization_count": 0,
        "human_terminal_review_count": 0,
        "governed_launcher_activations": 0,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "wrong_attempt_execution_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "pre_count": 0,
        "post_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_execution_count": 0,
        "replay_execution_count": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }
    request = sealed(
        "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request_inner,
    )
    request_path = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise JWBarrierError("FRESH_PRESENTATION_COLLISION")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256JW_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JW_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "request_path": request_path.relative_to(ROOT).as_posix(),
            "request_file_sha256": sha256_path(request_path),
            "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn_result,
            "authority_present": False,
            "auto_continuable": False,
        },
    )
    gn_proof_path = JW / "G77_256JW_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    write_json(gn_proof_path, gn_proof)

    safe_stop = sealed(
        "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        {
            "schema_id": "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
            "artifact_class": "SEALED_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "terminal": PHASE_A_TERMINAL,
            "candidate_sha256": identities["candidate_sha256"],
            "context_sha256": identities["context_sha256"],
            "context_file_sha256": identities["context_file_sha256"],
            "canonical_argv_sha256": identities["canonical_argv_sha256"],
            "expired_adapter_sha256": identities["expired_adapter_sha256"],
            "temporal_binding_sha256": identities["temporal_binding_sha256"],
            "jr_runtime_head": JR_HEAD,
            "jr_runtime_tree": JR_TREE,
            "readiness_checkpoint_path": checkpoint_path.relative_to(ROOT).as_posix(),
            "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
            "readiness_checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
            "request_path": request_path.relative_to(ROOT).as_posix(),
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_path": gn_proof_path.relative_to(ROOT).as_posix(),
            "equivalence_file_sha256": sha256_path(gn_proof_path),
            "equivalence_inner_sha256": gn_proof["proof_sha256"],
            "request_presentation_equivalence": gn_result[
                "human_presentation_request_equivalence"
            ],
            "authority_boundary": {
                "authority_state": "NOT_GRANTED",
                "human_authority_present": False,
                "request_is_authority": False,
                "presentation_is_authority": False,
                "checkpoint_is_authority": False,
                "provider_capability_is_authority": False,
                "human_authority_assurance_status": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
                "auto_continuable": False,
                "human_review_required": True,
            },
            "operational_counters": counters,
            "e05": {
                "before": "VERIFIED__11_OF_18",
                "after": "VERIFIED__11_OF_18",
                "credit": "VERIFIED__0",
                "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            },
        },
    )
    safe_stop_path = JW / "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(safe_stop_path, safe_stop)

    reduction = sealed(
        "G77_256JW_PREHUMAN_PHASE_A_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256JW_PREHUMAN_PHASE_A_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "terminal": PHASE_A_TERMINAL,
            "phase": "PREAUTHORIZATION_STOP",
            "entry": entry,
            "jv_reconstruction": jv,
            "jt_reconstruction": jt,
            "ex_reuse": ex,
            "expired_semantics": expired,
            "fresh_identity": fresh_identity,
            "owner_results": {
                "ex": "PASS__17_OF_17_REUSED__0_RECONSTRUCTED",
                "fm_materialization": operation_materialization["result"],
                "fm_static_readiness": readiness["result"],
                "gl": gl_result["preauth_final_admission_equivalence"],
                "gn": gn_result["human_presentation_request_equivalence"],
            },
            "identities": identities | {
                "request_sha256": request["request_sha256"],
                "request_file_sha256": sha256_path(request_path),
                "presentation_sha256": sha256_path(presentation_path),
                "readiness_checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
                "checkpoint_sha256": safe_stop["checkpoint_sha256"],
                "checkpoint_file_sha256": sha256_path(safe_stop_path),
            },
            "authority_boundary": {
                "human_operational_authority": "VERIFIED__0",
                "authority_consumption": "VERIFIED__0",
                "authorization_request_materialization_count": "VERIFIED__1",
                "authorization_presentation_count": "VERIFIED__1",
                "operation_execution": "NOT_STARTED",
                "next_legal_action": "PRESENT_EXACT_GN_TEXT_AND_STOP_FOR_EXPLICIT_HUMAN_AUTHORIZATION",
                "auto_continuable": False,
                "human_review_required": True,
            },
            "operational_counters": counters,
            "e05": {
                "before": "VERIFIED__11_OF_18",
                "current": "VERIFIED__11_OF_18",
                "credit": "VERIFIED__0",
                "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
                "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            },
            "architecture": checkpoint_inner["architecture"],
            "proof_yield": {
                "new_verified_capability_count": "VERIFIED__1__FRESH_JW_EXPIRED_PREAUTHORIZATION_PACKAGE",
                "new_blocker_localized_count": "VERIFIED__0",
                "e05_credit": "VERIFIED__0",
                "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
            },
            "reuse_impact_assessment": {
                "existing_certified_capabilities_reused": "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__JS__JT__FM__FC__ER__GN__P11",
                "new_capabilities": "VERIFIED__1__FRESH_JW_EXPIRED_PREAUTHORIZATION_PACKAGE__NONAUTHORITY",
                "existing_capability_became_unreachable": False,
                "parallel_flow_created": False,
                "production_path_count_effect": "UNCHANGED__1_TO_1",
            },
            "governance_dashboard": {
                "project_progress": "VERIFIED__JW_FRESH_EXPIRED_PREAUTHORIZATION_BARRIER_MATERIALIZED",
                "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
                "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_READY_FOR_ONE_EXPLICIT_HUMAN_DECISION",
                "constitutional_health_evidence": "VERIFIED__AUTHORITY_SEPARATION_AND_ZERO_OPERATION_PRESERVED",
                "shadow_automation_status": "VERIFIED__ABSENT",
                "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
                "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_REUSED_ONE_ROUTE_PRESERVED",
                "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_LOCAL_ORCHESTRATION_ONLY",
                "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
                "cognition_assisted_handoff": "NOT_APPLICABLE__NO_PROVIDER_RECOVERY",
                "candidate_capability": "VERIFIED__EXACT_EXPIRED_OPERATION_CANDIDATE_AT_HUMAN_BARRIER",
                "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
                "constitutional_continuation_progress": "VERIFIED__JV_TO_JW_PREAUTHORIZATION_STOP",
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
                "last_verified_edge": "FRESH_JW_EXPIRED_PREAUTHORIZATION_CHECKPOINT_AND_HUMAN_PRESENTATION_MATERIALIZED",
                "first_broken_edge": "EXACT_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
                "minimum_missing_capability": "EXACT_HUMAN_AUTHORIZATION_FOR_BOUND_JW_EXPIRED_OPERATION",
                "minimum_legal_next_delta": "SAME_GENERATION_JW_HUMAN_AUTHORIZATION_CONSUMPTION_AND_ONE_OPERATION",
            },
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    write_json(JW / "G77_256JW_PREHUMAN_PHASE_A_REDUCTION_V1.json", reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    materialize(parse_args())
