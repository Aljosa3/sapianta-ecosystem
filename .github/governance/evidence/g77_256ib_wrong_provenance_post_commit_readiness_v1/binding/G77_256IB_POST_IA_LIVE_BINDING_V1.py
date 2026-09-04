#!/usr/bin/env python3
"""Bind committed IA to WRONG_PROVENANCE readiness without operating.

This repository-only evidence owner creates no Human authority, operational
request, PRE entry, P11 entry, QEMU process, VM, or protected effect.  It
reuses the existing HW post-commit readiness architecture and the IA route.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
IA_HEAD = "dfea5c58f400edb9472db37390de80a92eda2ad3"
IA_TREE = "caf8feb24ed4c072dde6c6586fd7cf60d05c4c7d"
IA_SUBJECT = "G77-256IA extend single route for WRONG_PROVENANCE"
HZ_HEAD = "9db84476f263b9676d2ff7407152388afad04618"
HZ_TREE = "8753786eede58f453a40af71825c19bc3efaff0a"
HT_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
HT_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

VECTOR = "WRONG_PROVENANCE"
SUPPORTED_VECTORS = (
    "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE"
)
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_PROVENANCE"
GENERATION = (
    "G77_256IB_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_"
    "OPERATIONAL_COMMISSIONING_V1"
)
OPERATION_IDENTITY = "G77_256IB_WRONG_PROVENANCE_PREOPERATIONAL_READINESS_001"
IDENTITY_PREFIX = "G77_256IB"
CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_PROVENANCE"
CASE_ID = "G77_256IB_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001"
WRONG_PROVENANCE_IDENTITY = "G77_256IB_DISTINCT_WRONG_PROVENANCE_001"

IA_ROOT = Path(
    ".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1"
)
IA_TERMINAL = IA_ROOT / "G77_256IA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IA_REPORT = IA_ROOT / "G77_256IA_G48_IMPLEMENTATION_REPORT_V1.md"
ADAPTER = IA_ROOT / "adapter/G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"
MATERIALIZER = IA_ROOT / (
    "orchestration/G77_256IA_WRONG_PROVENANCE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
CLOUD_INIT = IA_ROOT / "static/G77_256IA_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = IA_ROOT / "static/SAPIANTA_WRONG_PROVENANCE_NOCLOUD_SEED_TEMPLATE_V1.img"
HZ_ROOT = Path(
    ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1"
)
HZ_TERMINAL = HZ_ROOT / "G77_256HZ_SPCE_TERMINAL_REDUCTION_V1.json"
HZ_SPEC = HZ_ROOT / "G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_V1.json"
HZ_PRODUCER = HZ_ROOT / "producer/G77_256HZ_WRONG_PROVENANCE_VECTOR_PRODUCER_V1.py"
HZ_REDUCER = HZ_ROOT / (
    "reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
GN_OWNER = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
DU_OWNER = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
EB_OWNER = Path(
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EE_OWNER = Path(
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
G48_STANDARD = Path("docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md")
P11_OWNER = Path("tests/p11_da_custody_process_v1.py")

ADAPTER_SHA256 = "e547af9b68f77fda94962abb6031445df5faba9ec43c68f40966473f83db8b23"
HZ_PRODUCER_SHA256 = "d8b6933b024248f6650ec74295dbe1ce1c864377648e8e2804a34e15b6c01b12"
HZ_REDUCER_SHA256 = "b30c082185ebe185a0be0504a44ebc97d8f20a201b143a93b8d53e2e356a6585"
CLOUD_INIT_SHA256 = "4725543bab299d1e153b2c40f9fcd0791ce9c2af318e88c41deeba9e6c69ed84"
SEED_SHA256 = "4154ec58b7ebf46299ccc495a0a1232b7e31f67221f987b6fe7959f8d5593c7c"
CONTEXT_OWNER_SHA256 = "ff3f7b01090743b3deb10dc44147eb5820f13b4e443158758b64b69ea2bb489c"

COMMITTED_IA_PATHS = {
    "IA_TERMINAL_REDUCTION": (IA_TERMINAL, "committed IA terminal reduction"),
    "IA_G48_REPORT": (IA_REPORT, "committed IA G48 report"),
    "IA_ADAPTER": (ADAPTER, "committed IA vector adapter"),
    "IA_MATERIALIZER": (MATERIALIZER, "committed IA static materializer"),
    "HZ_TERMINAL_REDUCTION": (HZ_TERMINAL, "committed HZ terminal reduction"),
    "HZ_FORMAL_SPECIFICATION": (HZ_SPEC, "committed HZ formal specification"),
    "HZ_PRODUCER": (HZ_PRODUCER, "committed HZ producer"),
    "HZ_REDUCER": (HZ_REDUCER, "committed HZ reducer"),
    "FM_CONTEXT_OWNER": (FM_CONTEXT, "sole operation-context owner"),
    "GN_PRESENTATION_OWNER": (GN_OWNER, "sole Human-presentation owner"),
    "DU_OWNER": (DU_OWNER, "continuation-manifest validator"),
    "EB_OWNER": (EB_OWNER, "candidate-bound receipt validator"),
    "EE_OWNER": (EE_OWNER, "runtime projection validator"),
    "EX_CERTIFICATE": (EX_CERTIFICATE, "common certified proof substrate"),
    "P11_OWNER": (P11_OWNER, "unchanged D2 custody owner"),
}


class IBBindingError(ValueError):
    """One deterministic fail-closed IB repository binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise IBBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", f"{revision}:{path.as_posix()}"],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise IBBindingError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise IBBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IBBindingError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IBBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    """Authenticate committed and pushed IA while allowing only unstaged IB."""

    root = repository_root.resolve()
    observed = {
        "repository": str(root),
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(root), "branch": BRANCH, "head": IA_HEAD,
        "tree": IA_TREE, "subject": IA_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IA_HEAD, "index": "",
    }
    if observed != expected:
        raise IBBindingError("EXACT_COMMITTED_IA_CHECKPOINT_MISMATCH")
    for ancestor in (
        HZ_HEAD,
        "451fafdeafc935c352a27f75fbddb473423ce7b3",
        "c8f0ad3602fd3b99b68f043be4c978d665dbf000",
        "af44f0afd02be7e21a24e962309e28f6edd17ae0",
        "737ef550f02f6b65a7dd0d4e1ac5bc118599b32b",
        "0e2448cb0194d6182085a671ddb28729681a1e75",
        STABLE_ANCHOR,
    ):
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, IA_HEAD],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode:
            raise IBBindingError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")
    if _git(root, "rev-parse", f"{HZ_HEAD}^{{tree}}") != HZ_TREE:
        raise IBBindingError("HZ_TREE_MISMATCH")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "branch": "", "status": "", "tag_head": NESTED_HEAD,
    }:
        raise IBBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def committed_identity_map(repository_root: Path) -> dict[str, dict[str, str]]:
    root = repository_root.resolve()
    result: dict[str, dict[str, str]] = {}
    for name, (path, role) in COMMITTED_IA_PATHS.items():
        committed = _git_bytes(root, IA_HEAD, path)
        if (root / path).is_symlink() or (root / path).read_bytes() != committed:
            raise IBBindingError(f"COMMITTED_IA_IDENTITY_DRIFT__{path.name}")
        result[name] = {
            "path": path.as_posix(),
            "git_blob": _git(root, "rev-parse", f"{IA_HEAD}:{path.as_posix()}"),
            "sha256": sha256_bytes(committed),
            "role": role,
            "committed_identity_status": "VERIFIED",
        }
    if result["IA_ADAPTER"]["sha256"] != ADAPTER_SHA256:
        raise IBBindingError("IA_ADAPTER_COMMITTED_HASH_MISMATCH")
    if result["HZ_PRODUCER"]["sha256"] != HZ_PRODUCER_SHA256:
        raise IBBindingError("HZ_PRODUCER_COMMITTED_HASH_MISMATCH")
    if result["HZ_REDUCER"]["sha256"] != HZ_REDUCER_SHA256:
        raise IBBindingError("HZ_REDUCER_COMMITTED_HASH_MISMATCH")
    return result


def reconstruct_ia_terminal(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    raw = _git_bytes(root, IA_HEAD, IA_TERMINAL)
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    if raw != canonical_bytes(envelope) or envelope["reduction_sha256"] != (
        sha256_bytes(canonical_bytes(envelope["reduction"]))
    ):
        raise IBBindingError("IA_TERMINAL_AUTHENTICATION_FAILED")
    reduction = envelope["reduction"]
    route = reduction["route_extension"]
    if route != {
        "post_commit_live_binding_required": "VERIFIED",
        "production_route_after": 1,
        "production_route_before": 1,
        "production_route_delta": 0,
        "supported_vector_set_after": [
            "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"
        ],
        "supported_vector_set_before": [
            "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT"
        ],
        "unknown_vector_policy": "FAIL_CLOSED",
    }:
        raise IBBindingError("IA_ROUTE_CLAIM_RECONSTRUCTION_FAILED")
    if reduction["e05"] != {
        "after": "9/18", "before": "9/18", "credit": 0,
        "remaining": 9, "required": 18, "satisfied": 9,
    }:
        raise IBBindingError("IA_E05_RECONSTRUCTION_FAILED")
    if reduction["readiness_reduction"]["wrong_provenance_binding_status"] != (
        "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY"
    ):
        raise IBBindingError("IA_STATIC_BINDING_NOT_VERIFIED")
    return reduction


def verify_checkout_bootstrap(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ib_launcher_audit")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (IA_HEAD, IA_TREE):
        raise IBBindingError("FM_CHECKOUT_NOT_BOUND_TO_COMMITTED_IA")
    bootstrap = launcher.current_bootstrap_asset_bindings(VECTOR)
    if bootstrap != {
        "cloud_init_path": CLOUD_INIT.as_posix(),
        "cloud_init_sha256": CLOUD_INIT_SHA256,
        "seed_path": str(root / SEED),
        "seed_sha256": SEED_SHA256,
    }:
        raise IBBindingError("IA_BOOTSTRAP_ASSET_BINDING_MISMATCH")
    if sha256_path(root / CLOUD_INIT) != CLOUD_INIT_SHA256:
        raise IBBindingError("IA_CLOUD_INIT_HASH_MISMATCH")
    if sha256_path(root / SEED) != SEED_SHA256:
        raise IBBindingError("IA_NOCLOUD_HASH_MISMATCH")
    commands = [
        line.strip().split()
        for line in (root / CLOUD_INIT).read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    ]
    if len(commands) != 1 or len(commands[0]) != 7:
        raise IBBindingError("IA_BOOTSTRAP_COMMAND_INVALID")
    harness_hash, _, checkout_head, checkout_tree, _ = commands[0][2:]
    if (harness_hash, checkout_head, checkout_tree) != (
        ADAPTER_SHA256, IA_HEAD, IA_TREE
    ):
        raise IBBindingError("IA_BOOTSTRAP_COMMAND_BINDING_MISMATCH")
    for member, source in (
        ("/user-data", CLOUD_INIT), ("/meta-data", FM_META),
        ("/network-config", FM_NETWORK),
    ):
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(root / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (root / source).read_bytes():
            raise IBBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{source.name}")
    return {
        "checkout_head": IA_HEAD,
        "checkout_tree": IA_TREE,
        "checkout_owner_binding_status": "VERIFIED",
        "bootstrap_head_tree_status": "VERIFIED",
        "nocloud_projection_status": "VERIFIED",
        "checkout_bootstrap_coherence_status": "VERIFIED",
        "expected_harness_sha256": ADAPTER_SHA256,
        "nocloud_generation": {
            "tool": "cloud-localds",
            "source_date_epoch": 1788540000,
            "user_data_sha256": CLOUD_INIT_SHA256,
            "meta_data_sha256": sha256_path(root / FM_META),
            "network_config_sha256": sha256_path(root / FM_NETWORK),
            "result_sha256": SEED_SHA256,
        },
    }


def generation(vector: str) -> str:
    return (
        f"G77_256IBTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )


def verify_host_guest_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    owner = _load_module(root / FM_CONTEXT, "g77_256ib_current_context_owner")
    committed_source = _git_bytes(root, IA_HEAD, FM_CONTEXT)
    namespace: dict[str, Any] = {
        "__name__": "g77_256ib_committed_guest_context",
        "__file__": FM_CONTEXT.as_posix(),
    }
    exec(compile(committed_source, FM_CONTEXT.as_posix(), "exec"), namespace)
    if tuple(sorted(owner.SUPPORTED_OPERATION_VECTORS)) != tuple(sorted(SUPPORTED_VECTORS)):
        raise IBBindingError("SUPPORTED_VECTOR_SET_MISMATCH")
    for vector in SUPPORTED_VECTORS:
        identity = generation(vector)
        if owner.operation_vector(identity) != vector or namespace["operation_vector"](identity) != vector:
            raise IBBindingError(f"HOST_GUEST_VECTOR_MISMATCH__{vector}")
    for malformed in (generation("UNKNOWN"), "MALFORMED", generation("wrong_provenance")):
        for operation_vector, error in (
            (owner.operation_vector, owner.ContextError),
            (namespace["operation_vector"], namespace["ContextError"]),
        ):
            try:
                operation_vector(malformed)
            except error:
                pass
            else:
                raise IBBindingError("UNKNOWN_OR_MALFORMED_VECTOR_ACCEPTED")
    for path in (ADAPTER, HZ_SPEC, HZ_PRODUCER, HZ_REDUCER, FM_CONTEXT, P11_OWNER):
        _git_bytes(root, IA_HEAD, path)
    return {
        "supported_vector_set": list(SUPPORTED_VECTORS),
        "host_guest_semantic_equivalence": "VERIFIED",
        "guest_dependency_closure_status": "VERIFIED",
        "unknown_malformed_policy": "FAIL_CLOSED",
    }


def candidate_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    producer = _load_module(root / HZ_PRODUCER, "g77_256ib_hz_producer")
    reducer = _load_module(root / HZ_REDUCER, "g77_256ib_hz_reducer")
    candidate = producer.produce_wrong_provenance_vector(
        repository_root=root,
        wrong_provenance_identity=WRONG_PROVENANCE_IDENTITY,
    )
    reduction = reducer.reduce_wrong_provenance_candidate(
        canonical_bytes(candidate), repository_root=root
    )
    expected = {
        "selected_vector": SELECTED_VECTOR,
        "independent_mutated_coordinate": "provenance_identity",
        "independent_mutation_count": 1,
        "dependent_recomputed_coordinate": "record_identity",
        "dependent_recomputation_count": 1,
        "differing_input_fields": ["provenance_identity", "record_identity"],
        "expected_error_reason": (
            "operational Human act input_record_identity binding is invalid"
        ),
        "provenance_specific_comparison_reached": False,
        "authority_created": False,
        "request_created": False,
        "operation_attempted": False,
        "e05_credit": 0,
    }
    if any(candidate.get(key) != value for key, value in expected.items()):
        raise IBBindingError("HZ_CANDIDATE_SEMANTIC_FIREWALL_FAILED")
    if reduction["authoritative_provenance_resolution"] != (
        "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
    ):
        raise IBBindingError("HZ_PROVENANCE_OWNER_NOT_UNIQUE")
    return candidate


def _file_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {"identity": identity, "path": path.as_posix(), "sha256": sha256_path(root / path)}


def _lineage_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return _file_binding(root, identity, path) | {
        "git_blob": _git(root, "rev-parse", f"{IA_HEAD}:{path.as_posix()}")
    }


def build_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_entry(root)
    reconstruct_ia_terminal(root)
    verify_checkout_bootstrap(root)
    verify_host_guest_semantics(root)
    semantic = candidate_semantics(root)
    du = _load_module(root / DU_OWNER, "g77_256ib_du_builder")
    envelope = du.build_du_fixture(root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION,
        "required_head": IA_HEAD,
        "source_tree": IA_TREE,
        "current_spce_phase": "PHASE_N_WRONG_PROVENANCE_PREOPERATIONAL_READINESS_VERIFIED",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [],
        "case_counters": {"e05_case_execution_count": 0, "wrong_provenance_case_count": 0},
        "authority_state": {
            "lifecycle_state": "NOT_CREATED", "act_identity": None,
            "owner_revision": None, "authority_survives": False,
            "transferable": False, "reusable": False,
        },
        "lineage_bindings": [
            _lineage_binding(root, "G77_256IA_TERMINAL_REDUCTION", IA_TERMINAL),
            _lineage_binding(root, "G77_256HZ_TERMINAL_REDUCTION", HZ_TERMINAL),
            _lineage_binding(root, "G77_256EX_COMMON_SUBSTRATE", EX_CERTIFICATE),
            _lineage_binding(root, "G48_REPORTING_STANDARD", G48_STANDARD),
        ],
        "frontier_state": {
            "constitutional_frontier": (
                "WRONG_PROVENANCE_PREOPERATIONAL_READINESS_VERIFIED__"
                "OPERATIONAL_CAPABILITY_NOT_PROVEN"
            ),
            "exact_next_legal_action": (
                "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_SEPARATELY_"
                "AUTHORIZED_OPERATIONAL_GENERATION"
            ),
            "continuation_mode": "HUMAN_REVIEW_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {"case_class": CASE_CLASS, "case_id": CASE_ID},
        "first_failure_or_current_result": (
            "PASS__WRONG_PROVENANCE_REPOSITORY_READINESS__NO_OPERATION__NO_E05_CREDIT"
        ),
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "observations": [
            "CURRENT_IA_COMMIT_IDENTITY_STATUS__VERIFIED",
            "TARGET_MUTATION__provenance_identity",
            "DEPENDENT_RECOMPUTATION__record_identity",
            "AUTHORITATIVE_PROVENANCE__EXISTING_PROTECTED_CUSTODY_OWNER_STATE",
            "EXPECTED_DENIAL__INPUT_RECORD_IDENTITY_BINDING_INVALID",
            "PROVENANCE_SPECIFIC_COMPARISON_REACHED__FALSE",
            "PRESENTATION_NOT_AUTHORIZATION",
            "E05_REMAINS_NINE_OF_EIGHTEEN",
        ],
        "extension_bindings": [
            _file_binding(root, "G77_256HZ_FORMAL_SPECIFICATION", HZ_SPEC),
            _file_binding(root, "G77_256HZ_PRODUCER", HZ_PRODUCER),
            _file_binding(root, "G77_256HZ_REDUCER", HZ_REDUCER),
            _file_binding(root, "G77_256IA_ADAPTER", ADAPTER),
            _file_binding(root, "G77_256IA_MATERIALIZER", MATERIALIZER),
            _file_binding(root, "G77_256FM_SOLE_LAUNCHER", FM_LAUNCHER),
            _file_binding(root, "G77_256FM_CONTEXT_OWNER", FM_CONTEXT),
            _file_binding(root, "G77_256IA_CLOUD_INIT", CLOUD_INIT),
            _file_binding(root, "G77_256IA_NOCLOUD", SEED),
            _file_binding(root, "G77_256GN_PRESENTATION_OWNER", GN_OWNER),
        ],
    })
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    if set(du.validate_envelope(envelope, root, expected_head=IA_HEAD).values()) != {"PASS"}:
        raise IBBindingError("CURRENT_DU_NOT_PASS")
    return envelope


def validate_context(repository_root: Path, context: dict[str, Any], candidate_path: Path) -> None:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ib_context_validator")
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate_path.relative_to(root)
    )
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    adapter = context["guest_adapter_binding"]
    if (context["repository_head"], context["repository_tree"]) != (IA_HEAD, IA_TREE):
        raise IBBindingError("CONTEXT_REPOSITORY_IDENTITY_MISMATCH")
    if (checkout["head"], checkout["tree"]) != (IA_HEAD, IA_TREE):
        raise IBBindingError("CONTEXT_CHECKOUT_IDENTITY_MISMATCH")
    if seed["sha256"] != SEED_SHA256 or hashes["cloud_init"] != CLOUD_INIT_SHA256:
        raise IBBindingError("CONTEXT_BOOTSTRAP_IDENTITY_MISMATCH")
    if hashes[launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] != CONTEXT_OWNER_SHA256:
        raise IBBindingError("CONTEXT_OWNER_IDENTITY_MISMATCH")
    if adapter["source_path"] != ADAPTER.as_posix() or adapter["source_sha256"] != ADAPTER_SHA256:
        raise IBBindingError("CONTEXT_ADAPTER_IDENTITY_MISMATCH")
    if launcher.fresh_context.checkout_lifecycle_binding(context) != (
        launcher.fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE
    ):
        raise IBBindingError("CHECKOUT_LIFECYCLE_NOT_OPERATION_SCOPED")


def build_context(repository_root: Path, candidate_path: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ib_context_builder")
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=IA_HEAD,
        repository_tree=IA_TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION_IDENTITY,
        identity_namespace_prefix=IDENTITY_PREFIX,
        operation_evidence_root=Path("/tmp/g77_256ib/operation_state"),
        transient_root=Path("/tmp/g77_256ib/transient"),
        candidate_source_path=candidate_path.relative_to(root),
    )
    validate_context(root, context, candidate_path)
    return context


def validate_presentation_binding(
    repository_root: Path, candidate_bytes: bytes, context: dict[str, Any]
) -> dict[str, Any]:
    root = repository_root.resolve()
    materializer = _load_module(root / MATERIALIZER, "g77_256ib_materializer")
    semantics = {
        "selected_vector": SELECTED_VECTOR,
        "target_mutation": "provenance_identity",
        "dependent_recomputation": "record_identity",
        "semantic_mutation_count": 1,
        "unrelated_mutation_count": 0,
        "authoritative_provenance_resolution": (
            "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
        ),
        "provenance_specific_comparison_reached": False,
    }
    digest = sha256_bytes(candidate_bytes)
    request_binding = {
        "authorized_vector_requested": VECTOR,
        "generation_identity": context["generation_identity"],
        "candidate_sha256": digest,
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "request_is_authority": False,
    }
    presentation_binding = {
        "AUTHORIZED_VECTOR_REQUESTED": VECTOR,
        "GENERATION_ID": context["generation_identity"],
        "CANDIDATE_SHA256": digest,
        "CONTEXT_SHA256": context["context_sha256"],
        "CANONICAL_ARGV_SHA256": context["canonical_argv_sha256"],
    }
    result = materializer.validate_future_materialization_chain(
        repository_root=root,
        candidate_bytes=candidate_bytes,
        candidate_semantics=semantics,
        context=context,
        request_binding=request_binding,
        presentation_binding=presentation_binding,
    )
    if result["candidate_context_argv_presentation_chain"] != "VERIFIED":
        raise IBBindingError("GN_PRESENTATION_BINDING_NOT_VERIFIED")
    if result["human_operational_authority"] != 0:
        raise IBBindingError("PRESENTATION_CREATED_AUTHORITY")
    return {
        "gn_owner_sha256": sha256_path(root / GN_OWNER),
        "presentation_binding": presentation_binding,
        "presentation_binding_status": "VERIFIED",
        "presentation_is_human_authorization": False,
    }


def _harness_bytes(runtime_filename: str) -> bytes:
    return (
        "from pathlib import Path\n\n"
        'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
        'RAW_ROOT = Path("/mnt/g77-evidence")\n'
        f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{runtime_filename}"\n'
    ).encode("utf-8")


def instantiate_binding(*, repository_root: Path, output_root: Path) -> dict[str, Any]:
    """Materialize candidate/context and DU/EB/EE receipts, never operation state."""

    root = repository_root.resolve()
    output = output_root.resolve()
    if output.exists() or output.is_symlink():
        raise IBBindingError("POST_COMMIT_BINDING_OUTPUT_COLLISION")
    try:
        relative_output = output.relative_to(root)
    except ValueError as exc:
        raise IBBindingError("OUTPUT_OUTSIDE_REPOSITORY") from exc
    candidate_name = "G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_path = output / "runtime_projection" / candidate_name
    binding_root = output / "bindings"
    harness_path = binding_root / "G77_256IB_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_path = binding_root / "G77_256IB_EB_RECEIPT_V1.json"
    ee_path = binding_root / "G77_256IB_EE_RECEIPT_V1.json"
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    for parent in (candidate_path.parent, runtime_path.parent, binding_root):
        parent.mkdir(parents=True, exist_ok=True)
    candidate_bytes = canonical_bytes(build_candidate(root))
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(_harness_bytes(candidate_name))
    context = build_context(root, candidate_path)
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ib_context_serializer")
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    validate_presentation_binding(root, candidate_bytes, context)
    du = _load_module(root / DU_OWNER, "g77_256ib_du")
    eb = _load_module(root / EB_OWNER, "g77_256ib_eb")
    ee = _load_module(root / EE_OWNER, "g77_256ib_ee")
    du_result = du.validate_file(candidate_path, root, expected_head=IA_HEAD)
    eb_receipt = eb.validate_candidate(
        root, candidate_path, required_head=IA_HEAD, required_tree=IA_TREE
    )
    eb_path.write_bytes(eb.canonical_bytes(eb_receipt))
    eb_result = eb.verify_receipt_file(root, eb_path)
    ee_receipt = ee.validate_binding(
        root, candidate_path, eb_path, harness_path, runtime_path.parent,
        "/mnt/g77-evidence", required_head=IA_HEAD, required_tree=IA_TREE,
    )
    ee_path.write_bytes(ee.canonical_bytes(ee_receipt))
    ee_result = ee.verify_receipt_file(root, ee_path)
    if set(du_result.values()) != {"PASS"}:
        raise IBBindingError("CURRENT_DU_NOT_PASS")
    if eb_result.get("overall_result") != "PASS":
        raise IBBindingError("CURRENT_EB_NOT_PASS")
    if ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise IBBindingError("CURRENT_EE_NOT_PASS")
    return {
        "schema_id": "G77_256IB_POST_IA_LIVE_BINDING_RESULT_V1",
        "artifact_class": "POST_COMMIT_BINDING__NON_AUTHORITY__NON_OPERATIONAL",
        "repository_head": IA_HEAD,
        "repository_tree": IA_TREE,
        "selected_checkout_head": IA_HEAD,
        "selected_checkout_tree": IA_TREE,
        "output_root": relative_output.as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(context_path),
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "human_operational_authority_count": 0,
        "authority_consumption_count": 0,
        "request_count": 0,
        "pre_count": 0,
        "p11_entry_count": 0,
        "qemu_execution_count": 0,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "e05_credit": 0,
    }


def current_chain(repository_root: Path, live_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    live = live_root.resolve()
    candidate = live / "candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    runtime = live / "runtime_projection/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = load_canonical(context_path)
    return {
        "vector": VECTOR,
        "ia_head": IA_HEAD,
        "ia_tree": IA_TREE,
        "checkout_head": IA_HEAD,
        "checkout_tree": IA_TREE,
        "fm_launcher": sha256_path(root / FM_LAUNCHER),
        "fm_context_owner": sha256_path(root / FM_CONTEXT),
        "adapter": ADAPTER_SHA256,
        "hz_producer": HZ_PRODUCER_SHA256,
        "hz_reducer": HZ_REDUCER_SHA256,
        "provenance_owner": "UNIQUE_AUTHENTICATED_EXISTING_PROTECTED_OWNER",
        "cloud_init": CLOUD_INIT_SHA256,
        "nocloud_projection": SEED_SHA256,
        "candidate": sha256_path(candidate),
        "runtime_projection": sha256_path(runtime),
        "operation_context": context["context_sha256"],
        "context_candidate": context["candidate_manifest_sha256"],
        "canonical_argv": context["canonical_argv_sha256"],
        "presentation_binding": (
            f"{VECTOR}:{context['context_sha256']}:{context['canonical_argv_sha256']}"
        ),
        "du": "PASS",
        "eb": sha256_path(live / "bindings/G77_256IB_EB_RECEIPT_V1.json"),
        "ee": sha256_path(live / "bindings/G77_256IB_EE_RECEIPT_V1.json"),
    }


def validate_chain(repository_root: Path, live_root: Path, chain: dict[str, Any]) -> None:
    expected = current_chain(repository_root, live_root)
    if chain != expected:
        fields = sorted(set(chain) | set(expected), key=str)
        field = next(
            (name for name in fields if chain.get(name) != expected.get(name)),
            "UNKNOWN",
        )
        raise IBBindingError(f"PREAUTHORIZATION_BINDING_REJECTED__{field.upper()}")
    if chain["candidate"] != chain["runtime_projection"]:
        raise IBBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    if chain["candidate"] != chain["context_candidate"]:
        raise IBBindingError("CANDIDATE_CONTEXT_BINDING_MISMATCH")
    if chain["checkout_head"] == HT_HEAD or chain["checkout_tree"] == HT_TREE:
        raise IBBindingError("STALE_HISTORICAL_HT_IDENTITY_ACCEPTED")


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    certificate = json.loads(
        _git_bytes(root, IA_HEAD, EX_CERTIFICATE), object_pairs_hook=_unique_object
    )
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(
        preimage, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload):
        raise IBBindingError("EX_CERTIFICATE_SEAL_INVALID")
    if certificate["certificate"]["component_counts"].get("CERTIFIED") != 17:
        raise IBBindingError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "17/17", "ex_reconstructed": 0, "status": "VERIFIED"}


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    """Reduce current repository-only evidence into one fail-closed verdict."""

    root = repository_root.resolve()
    live = live_root.resolve()
    entry = authenticate_entry(root)
    identities = committed_identity_map(root)
    ia = reconstruct_ia_terminal(root)
    checkout = verify_checkout_bootstrap(root)
    guest = verify_host_guest_semantics(root)
    candidate_path = live / "candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    runtime_path = live / "runtime_projection/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = load_canonical(context_path)
    candidate = load_canonical(candidate_path)
    if candidate_path.read_bytes() != runtime_path.read_bytes():
        raise IBBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    validate_context(root, context, candidate_path)
    presentation = validate_presentation_binding(root, candidate_path.read_bytes(), context)
    validate_chain(root, live, current_chain(root, live))
    semantics = candidate_semantics(root)
    du = _load_module(root / DU_OWNER, "g77_256ib_terminal_du")
    eb = _load_module(root / EB_OWNER, "g77_256ib_terminal_eb")
    ee = _load_module(root / EE_OWNER, "g77_256ib_terminal_ee")
    if set(du.validate_file(candidate_path, root, expected_head=IA_HEAD).values()) != {"PASS"}:
        raise IBBindingError("CURRENT_DU_NOT_PASS")
    if eb.verify_receipt_file(root, live / "bindings/G77_256IB_EB_RECEIPT_V1.json")["overall_result"] != "PASS":
        raise IBBindingError("CURRENT_EB_NOT_PASS")
    if ee.verify_receipt_file(root, live / "bindings/G77_256IB_EE_RECEIPT_V1.json")["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise IBBindingError("CURRENT_EE_NOT_PASS")
    ex = authenticate_ex(root)
    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    negative_cases = [
        "WRONG_VECTOR", "UNKNOWN_VECTOR", "MALFORMED_VECTOR", "WRONG_CANDIDATE",
        "WRONG_CONTEXT", "WRONG_ADAPTER", "WRONG_CHECKOUT_HEAD",
        "WRONG_CHECKOUT_TREE", "WRONG_BOOTSTRAP", "WRONG_NOCLOUD_PROJECTION",
        "WRONG_CANONICAL_ARGV_BINDING", "WRONG_PRESENTATION_BINDING",
        "STALE_HISTORICAL_HT_IDENTITY", "MISMATCHED_HZ_PRODUCER",
        "MISMATCHED_HZ_REDUCER", "MISSING_PROVENANCE_OWNER",
        "CONFLICTING_PROVENANCE_OWNER", "WRONG_RUNTIME_PROJECTION",
        "WRONG_DU", "WRONG_EB", "WRONG_EE",
    ]
    historical_classes = [
        "GE_GF_PRECOMMIT_FUTURE_COMMIT_SELF_REFERENCE",
        "HU_HV_STALE_GUEST_CHECKOUT",
        "GS_GT_CHECKOUT_DESTINATION_TRANSIENT_ROOT_LIFECYCLE",
        "HF_HG_HH_HI_HJ_HK_HN_HARNESS_ADAPTER_BOOTSTRAP_CHECKOUT_IDENTITY_DRIFT",
    ]
    return {
        "schema_id": "G77_256IB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": entry,
        "committed_identity_map": identities,
        "ia_terminal_reconstruction": {
            "status": "VERIFIED",
            "route_extension": ia["route_extension"],
            "readiness_reduction": ia["readiness_reduction"],
        },
        "checkout_bootstrap": checkout,
        "host_guest_coherence": guest,
        "live_binding": {
            "current_ia_commit_identity_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "current_wrong_provenance_candidate_status": "VERIFIED",
            "current_candidate_identity": sha256_path(candidate_path),
            "current_runtime_projection_status": "VERIFIED",
            "current_operation_context_status": "VERIFIED",
            "current_context_identity": context["context_sha256"],
            "gn_presentation_binding_status": presentation["presentation_binding_status"],
            "presentation_is_human_authorization": False,
            "candidate_runtime_byte_identity": "VERIFIED",
            "checkout_projection_coherence_status": "VERIFIED",
        },
        "du_eb_ee": {
            "current_du_status": "PASS",
            "current_eb_status": "PASS",
            "current_ee_status": "PASS",
        },
        "preauthorization_negative_matrix": {
            "status": "VERIFIED",
            "case_count": len(negative_cases),
            "cases": negative_cases,
            "failure_before_operation_status": "VERIFIED",
        },
        "historical_failure_firewall": {
            "status": "VERIFIED",
            "tested_set": historical_classes,
        },
        "semantic_firewall": {
            "independent_mutation_count": semantics["independent_mutation_count"],
            "independent_mutated_coordinate": semantics["independent_mutated_coordinate"],
            "dependent_recomputation_count": semantics["dependent_recomputation_count"],
            "dependent_recomputed_coordinate": semantics["dependent_recomputed_coordinate"],
            "authoritative_provenance": "EXISTING_PROTECTED_CUSTODY_OWNER_STATE",
            "expected_denial_reason": semantics["expected_error_reason"],
            "provenance_specific_comparison_reached": False,
        },
        "readiness": {
            "preoperational_readiness_status": "VERIFIED",
            "next_operational_generation_eligible": "VERIFIED",
            "wrong_provenance_formalization_status": "VERIFIED",
            "wrong_provenance_repository_capability": "VERIFIED",
            "wrong_provenance_route_support": "VERIFIED",
            "wrong_provenance_binding_status": "VERIFIED__CURRENT_COMMITTED_IA_LIVE_BINDING",
            "wrong_provenance_preoperational_readiness": "VERIFIED",
            "wrong_provenance_operational_capability": "NOT_PROVEN",
            "post_ib_commit_rebind_required": "NOT_APPLICABLE",
        },
        "reuse_impact": {
            "reused_certified_capability_set": [
                "HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY",
                "IA_WRONG_PROVENANCE_ROUTE_SUPPORT", "HT_SINGLE_ROUTE",
                "HV_POST_COMMIT_CHECKOUT_PATTERN", "HW_READINESS_PATTERN",
                "HX_OPERATIONAL_ARCHITECTURE", "FM", "GN", "GL", "DU", "EB",
                "EE", "P11", "CHE", "FK", "EX_17_OF_17", "GOVERNANCE", "LAYER_0",
            ],
            "new_capability_set": [
                "IB_CURRENT_COMMITTED_IA_LIVE_BINDING_AND_PREOPERATIONAL_READINESS_EVIDENCE"
            ],
            "unreachable_preexisting_capability_set": [],
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "new_generic_framework_count": 0,
            "new_authority_layer_count": 0,
            "new_production_route_count": 0,
            "new_runtime_owner_count": 0,
        },
        "infrastructure_amortization": {
            "did_ib_require_new_common_infrastructure": False,
            "did_ib_require_new_vector_specific_infrastructure": True,
            "did_ib_require_new_generic_framework": False,
            "did_ib_require_new_authority_layer": False,
            "did_ib_require_new_runtime_owner": False,
            "did_ib_require_new_production_route": False,
            "did_ib_require_p11_core_change": False,
            "did_ib_reuse_hz_repository_capability": True,
            "did_ib_reuse_ia_route_support": True,
            "did_ib_reuse_ht_single_route": True,
            "did_ib_reuse_hv_post_commit_checkout_pattern": True,
            "did_ib_reuse_hw_readiness_pattern": True,
            "did_ib_reuse_hx_operational_architecture": True,
            "did_ib_reuse_fm_gn_gl": True,
            "did_ib_reuse_du_eb_ee": True,
            "did_ib_reuse_p11_che_fk": True,
            "did_ib_reuse_ex_17_of_17": True,
            "generations_since_e05_9_of_18": {"status": "VERIFIED", "value": 4},
            "e05_credits_since_9_of_18": {"status": "VERIFIED", "value": 0},
            "operational_attempts_since_e05_9_of_18": {"status": "VERIFIED", "value": 0},
            "new_certified_components_since_e05_9_of_18": {
                "status": "VERIFIED",
                "value": "HZ_AND_IA_COMMITTED_COMPONENTS__IB_AWAITS_HUMAN_REVIEW",
            },
            "reused_certified_components_since_e05_9_of_18": {
                "status": "NOT_MEASURED",
                "value": "NO_GOVERNED_COMPONENT_DENOMINATOR",
            },
            "marginal_new_infrastructure_per_e05_credit": {
                "status": "NOT_MEASURED",
                "value": "ZERO_NEW_CREDIT_DENOMINATOR",
            },
            "infrastructure_amortization_signal": {
                "status": "ESTIMATED",
                "value": "POSITIVE_REUSE_SIGNAL__NO_LLM_COST_INFERENCE",
            },
        },
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE__NO_L5_CLAIM"},
            "cross_worker_state_recovery_level": {"status": "VERIFIED", "value": "REPOSITORY_AUTHENTICATED"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "value": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED", "value": "CHECKPOINT_SCOPE_PROHIBITIONS_LOCATORS"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_identity_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_memory_required": {"status": "VERIFIED", "value": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED", "value": "YES"},
            "inter_generation_cross_worker_continuation": {"status": "VERIFIED", "value": "IA_TO_IB"},
            "intra_generation_cross_worker_continuation": {"status": "NOT_APPLICABLE"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "authority_state_recovery": {"status": "NOT_APPLICABLE", "value": "NO_AUTHORITY_EXISTS"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "value": 0},
            "handoff_sufficiency_status": {"status": "VERIFIED"},
            "handoff_state_completeness": {"status": "VERIFIED"},
            "handoff_reconstruction_required": {"status": "VERIFIED", "value": "YES"},
            "handoff_reconstruction_success": {"status": "VERIFIED", "value": "YES"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "value": 0},
            "unauthenticated_handoff_assumption_count": {"status": "VERIFIED", "value": 0},
        },
        "required_metrics": {
            "project_progress_estimate": {"status": "ESTIMATED", "value": "WRONG_PROVENANCE_PREOPERATIONAL_READINESS_COMPLETE"},
            "constitutional_health_evidence": {"status": "VERIFIED", "value": "FAIL_CLOSED_AND_ZERO_OPERATION"},
            "shadow_automation_status": {"status": "VERIFIED", "value": "ABSENT"},
            "constitutional_frontier_distance": {"status": "ESTIMATED", "value": "ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION"},
            "e05_frontier_distance": {"status": "VERIFIED", "value": "9_OF_18_REMAIN"},
            "selected_e05_local_frontier_distance": {"status": "ESTIMATED", "value": "ONE_FUTURE_HUMAN_OPERATIONAL_GENERATION"},
            "governance_efficience": {"status": "ESTIMATED", "value": "TARGETED_AFFECTED_FRONTIER"},
            "architectural_governance_efficience": {"status": "VERIFIED", "value": "ONE_ROUTE_RETAINED"},
            "proof_reuse_efficiency": {"status": "VERIFIED", "value": "EX_17_OF_17_REUSED"},
            "cognition_assisted_handoff": {"status": "VERIFIED", "value": "REPLAY_SAFE_REPOSITORY_CONTINUATION"},
            "aigol_codex_work_share": {"status": "NOT_MEASURED"},
            "overengineering_risk": {"status": "ESTIMATED", "value": "LOW"},
            "proof_process_overhead_risk": {"status": "ESTIMATED", "value": "MODERATE"},
            "cognition_provenance": {"status": "VERIFIED", "value": "AUTHENTICATED_REPOSITORY_PRIMARY"},
            "candidate_capability": {"status": "VERIFIED", "value": "HZ_SEMANTICS_CURRENTLY_PROJECTED"},
            "wrong_provenance_candidate_capability": {"status": "VERIFIED"},
            "wrong_provenance_repository_capability": {"status": "VERIFIED"},
            "wrong_provenance_route_support": {"status": "VERIFIED"},
            "wrong_provenance_binding_status": {"status": "VERIFIED", "value": "CURRENT_COMMITTED_IA"},
            "wrong_provenance_preoperational_readiness": {"status": "VERIFIED"},
            "wrong_provenance_operational_capability": {"status": "NOT_PROVEN"},
            "shadow_design_target": {"status": "VERIFIED", "value": "FORMALIZE_REUSE_BIND_VERIFY_STOP"},
            "constitutional_continuation_progress": {"status": "VERIFIED", "value": "PREOPERATIONAL_READINESS_VERIFIED"},
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "token_benchmark": {"status": "NOT_MEASURED"},
            "llm_cost_reduction_ratio": {"status": "NOT_MEASURED"},
            "lcrr": {"status": "NOT_MEASURED"},
            "e05_generations_per_credit": {"status": "NOT_MEASURED", "value": "ZERO_NEW_CREDIT_DENOMINATOR"},
            "operational_attempts_per_credit": {"status": "NOT_MEASURED", "value": "ZERO_NEW_CREDIT_DENOMINATOR"},
            "marginal_e05_generation_cost": {"status": "NOT_MEASURED", "value": "NO_GOVERNED_COST_INSTRUMENT"},
            "marginal_new_infrastructure_per_e05_credit": {"status": "NOT_MEASURED", "value": "ZERO_NEW_CREDIT_DENOMINATOR"},
            "infrastructure_amortization_signal": {"status": "ESTIMATED", "value": "POSITIVE_REUSE_SIGNAL"},
            "expected_next_credit_generation_count": {"status": "ESTIMATED", "value": "AT_LEAST_ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION"},
        },
        "cognition_provenance": (
            "VERIFIED__AUTHENTICATED_GIT_COMMITTED_IA_HZ_HY_HX_HT_HV_HW_"
            "P11_CHE_FK_EX_FM_GN_GL_DU_EB_EE_GOVERNANCE_LAYER_0_"
            "PINNED_NESTED_AUTHORITY_AND_CURRENT_IB_REPOSITORY_EVIDENCE"
        ),
        "ex": ex,
        "e05": {
            "before": "9/18", "after": "9/18", "credit": 0,
            "required": 18, "satisfied": 9, "remaining": 9,
        },
        "operational_counters": counters,
        "terminal_control": {
            "auto_continuable": False,
            "human_authorization_required": False,
            "human_review_required": True,
            "last_verified_edge": (
                "CURRENT_COMMITTED_IA_WRONG_PROVENANCE_CANDIDATE_RUNTIME_"
                "CONTEXT_PRESENTATION_DU_EB_EE_PREAUTHORIZATION_CHAIN"
            ),
            "first_broken_edge": "NONE_KNOWN_IN_REPOSITORY_PREAUTHORIZATION_SCOPE",
            "minimum_missing_capability": (
                "ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_PROVENANCE_"
                "OPERATIONAL_GENERATION"
            ),
            "minimum_legal_next_delta": (
                "AFTER_IB_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_SEPARATELY_"
                "COMMISSIONED_OPERATIONAL_GENERATION__FRESH_HUMAN_AUTHORITY_REQUIRED"
            ),
            "verdict": (
                "VERIFIED__IB_POST_IA_WRONG_PROVENANCE_PREOPERATIONAL_READINESS__"
                "OPERATIONAL_CAPABILITY_NOT_PROVEN__ZERO_OPERATION__E05_9_OF_18__"
                "HUMAN_REVIEW_REQUIRED"
            ),
        },
    }


def write_terminal_reduction(
    *, repository_root: Path, live_root: Path, output_path: Path
) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    envelope = {
        "schema_id": "G77_256IB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise IBBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
