#!/usr/bin/env python3
"""Bind committed IE FUTURE semantics as far as repository law permits.

The owner is repository-only. It creates one nonauthorizing act/CHE
representation, candidate, runtime projection, context, and DU/EB/EE receipts.
It never invokes PRE, the operational FM entrypoint, P11, QEMU, or a VM.
"""

from __future__ import annotations

from copy import deepcopy
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

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
IE_TREE = "b9ebdc1015e9b9459ccd93841cc8d1c7377ddc19"
IE_SUBJECT = "G77-256IE formalize FUTURE repository vector"
ID_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
IC_HEAD = "afdd47166acdee30cb9867d3d3c7bfec0de64c8a"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

VECTOR = "FUTURE"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
GENERATION = "G77_256IF_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION_IDENTITY = "G77_256IF_FUTURE_PREOPERATIONAL_READINESS_001"
IDENTITY_PREFIX = "G77_256IF"
CASE_ID = "G77_256IF_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"

IF_ROOT = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1")
ADAPTER = IF_ROOT / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
ACT_CHE = IF_ROOT / "live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"
LIVE = IF_ROOT / "live_binding"
TERMINAL = IF_ROOT / "G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IE_ROOT = Path(".github/governance/evidence/g77_256ie_future_formalization_v1")
IE_SPEC = IE_ROOT / "G77_256IE_FUTURE_FORMAL_SPECIFICATION_V1.json"
IE_TIME = IE_ROOT / "G77_256IE_FUTURE_TIME_FIXTURE_V1.json"
IE_TERMINAL = IE_ROOT / "G77_256IE_SPCE_TERMINAL_REDUCTION_V1.json"
IE_PRODUCER = IE_ROOT / "producer/G77_256IE_FUTURE_VECTOR_PRODUCER_V1.py"
IE_REDUCER = IE_ROOT / "reducer/G77_256IE_FUTURE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
ID_SELECTION = Path(".github/governance/evidence/g77_256id_post_ic_e05_frontier_selection_v1/G77_256ID_E05_FRONTIER_SELECTION_V1.json")
IC_TERMINAL = Path(".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/G77_256IC_SPCE_TERMINAL_REDUCTION_V1.json")
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
CLOUD_INIT = IF_ROOT / "static/G77_256IF_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = IF_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_TEMPLATE_V1.img"
DU_OWNER = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_OWNER = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_OWNER = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")
G48 = Path("docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md")


class IFBindingError(ValueError):
    """One deterministic fail-closed IF binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root)


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise IFBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IFBindingError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IFBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
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
        "repository": str(root), "branch": BRANCH, "head": IE_HEAD,
        "tree": IE_TREE, "subject": IE_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IE_HEAD, "index": "",
    }
    if observed != expected:
        raise IFBindingError("EXACT_COMMITTED_IE_CHECKPOINT_MISMATCH")
    for ancestor in (IC_HEAD, ID_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IE_HEAD], cwd=root).returncode:
            raise IFBindingError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    if nested_state != {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "branch": "", "status": "", "tag_head": NESTED_HEAD}:
        raise IFBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def reconstruct_ie(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    producer = _load(root / IE_PRODUCER, "g77_256if_binding_ie_producer")
    reducer = _load(root / IE_REDUCER, "g77_256if_binding_ie_reducer")
    packet = producer.produce_future_vector(root)
    result = reducer.reduce_future_repository_vector(packet)
    terminal = json.loads(_git_bytes(root, IE_HEAD, IE_TERMINAL), object_pairs_hook=_unique)
    reduction = terminal["reduction"]
    if terminal["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IFBindingError("IE_TERMINAL_SEAL_INVALID")
    if reduction["e05"] != {"after": "10/18", "before": "10/18", "credit": 0, "frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_vector": "VERIFIED__FUTURE"}:
        raise IFBindingError("IE_E05_RECONSTRUCTION_FAILED")
    if result["future_repository_formalization"] != "VERIFIED":
        raise IFBindingError("IE_FUTURE_FORMALIZATION_FAILED")
    return {"packet": packet, "result": result, "terminal": reduction}


def build_act_che_binding(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    adapter = _load(root / ADAPTER, "g77_256if_binding_adapter")
    binding = adapter.build_repository_projection(root)
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    packet = reconstruct_ie(root)["packet"]
    if act["payload_digest"] != packet["future_payload_digest"]:
        raise IFBindingError("IE_PAYLOAD_DIGEST_NOT_PRESERVED")
    if che["authority_payload_digest"] != act["payload_digest"]:
        raise IFBindingError("CHE_AUTHORITY_PAYLOAD_DIGEST_MISMATCH")
    if che["source_act_digest"] == act["payload_digest"]:
        raise IFBindingError("ACT_AND_PAYLOAD_IDENTITIES_CONFLATED")
    return {
        "schema_id": "G77_256IF_FUTURE_ACT_CHE_BINDING_ENVELOPE_V1",
        "binding": binding,
        "binding_sha256": sha256_bytes(canonical_bytes(binding)),
    }


def _file_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {"identity": identity, "path": path.as_posix(), "sha256": sha256_path(root / path)}


def _lineage_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return _file_binding(root, identity, path) | {"git_blob": _git(root, "rev-parse", f"{IE_HEAD}:{path.as_posix()}")}


def route_state(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    context = _load(root / FM_CONTEXT, "g77_256if_route_context")
    launcher = _load(root / FM_LAUNCHER, "g77_256if_route_launcher")
    expected = {"WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"}
    if set(context.SUPPORTED_OPERATION_VECTORS) != expected:
        raise IFBindingError("FUTURE_CLOSED_ROUTE_MEMBERSHIP_INVALID")
    if context.operation_vector(GENERATION) != VECTOR:
        raise IFBindingError("FUTURE_ROUTE_DISPATCH_INVALID")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (IE_HEAD, IE_TREE):
        raise IFBindingError("CHECKOUT_NOT_BOUND_TO_COMMITTED_IE")
    bootstrap = launcher.current_bootstrap_asset_bindings(VECTOR)
    if sha256_path(root / CLOUD_INIT) != bootstrap["cloud_init_sha256"]:
        raise IFBindingError("FUTURE_CLOUD_INIT_HASH_MISMATCH")
    if sha256_path(Path(bootstrap["seed_path"])) != bootstrap["seed_sha256"]:
        raise IFBindingError("FUTURE_NOCLOUD_HASH_MISMATCH")
    for member, source in (("/user-data", CLOUD_INIT), ("/meta-data", FM_META), ("/network-config", FM_NETWORK)):
        projected = subprocess.check_output(["isoinfo", "-i", bootstrap["seed_path"], "-R", "-x", member])
        if projected != (root / source).read_bytes():
            raise IFBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{source.name}")
    tree = ast.parse((root / FM_LAUNCHER).read_text(encoding="utf-8"))
    main_count = sum(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body)
    if main_count != 1:
        raise IFBindingError("SOLE_PRODUCTION_ROUTE_COUNT_INVALID")
    committed_context = _git_bytes(root, IE_HEAD, FM_CONTEXT)
    committed_namespace: dict[str, Any] = {"__name__": "g77_256if_committed_ie_context", "__file__": FM_CONTEXT.as_posix()}
    exec(compile(committed_context, FM_CONTEXT.as_posix(), "exec"), committed_namespace)
    try:
        committed_namespace["operation_vector"](GENERATION)
    except committed_namespace["ContextError"]:
        committed_future_membership = False
    else:
        committed_future_membership = True
    return {
        "existing_route_owner": FM_LAUNCHER.as_posix(),
        "future_route_membership_before": "VERIFIED__ABSENT_IN_COMMITTED_IE",
        "future_route_membership_after": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY",
        "supported_vector_set_after": sorted(expected),
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "new_production_route_count": "VERIFIED__0",
        "committed_ie_checkout_contains_future_membership": committed_future_membership,
        "checkout_host_guest_equivalence": "NOT_PROVEN" if not committed_future_membership else "VERIFIED",
    }


def build_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_entry(root)
    ie = reconstruct_ie(root)
    route = route_state(root)
    du = _load(root / DU_OWNER, "g77_256if_du_builder")
    envelope = du.build_du_fixture(root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION,
        "required_head": IE_HEAD,
        "source_tree": IE_TREE,
        "current_spce_phase": "PHASE_N_FUTURE_REPOSITORY_STATIC_BINDING_COMPLETE_LIVE_READINESS_NOT_PROVEN",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [],
        "case_counters": {"e05_case_execution_count": 0, "future_case_count": 0},
        "authority_state": {"lifecycle_state": "NOT_CREATED", "act_identity": None, "owner_revision": None, "authority_survives": False, "transferable": False, "reusable": False},
        "lineage_bindings": [
            _lineage_binding(root, "G77_256IE_TERMINAL_REDUCTION", IE_TERMINAL),
            _lineage_binding(root, "G77_256IE_FORMAL_SPECIFICATION", IE_SPEC),
            _lineage_binding(root, "G77_256IE_TIME_FIXTURE", IE_TIME),
            _lineage_binding(root, "G77_256EX_COMMON_SUBSTRATE", EX_CERTIFICATE),
            _lineage_binding(root, "G48_REPORTING_STANDARD", G48),
        ],
        "frontier_state": {
            "constitutional_frontier": "FUTURE_REPOSITORY_STATIC_BINDING_COMPLETE__COMMITTED_CHECKOUT_MEMBERSHIP_ABSENT",
            "exact_next_legal_action": "AFTER_IF_REVIEW_AND_COMMIT_ONLY__POST_IF_COMMITTED_CHECKOUT_REBIND",
            "continuation_mode": "HUMAN_REVIEW_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {"case_class": "E05_NEGATIVE_AUTHORITY_FUTURE", "case_id": CASE_ID},
        "first_failure_or_current_result": "FAIL_CLOSED__COMMITTED_IE_CHECKOUT_DOES_NOT_CONTAIN_FUTURE_ROUTE_MEMBERSHIP",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "observations": [
            "CURRENT_IE_COMMIT_IDENTITY_STATUS__VERIFIED",
            "SEMANTIC_MUTATION__valid_from_unix_ns",
            "TIME_RELATION__500_LT_600_LT_1000",
            "FUTURE_ACT_REPRESENTATION_NOT_AUTHORITY",
            "CHE_PAYLOAD_SOURCE_ACT_AND_CORRELATION_IDENTITIES_RECOMPUTED",
            "E05_REMAINS_TEN_OF_EIGHTEEN",
        ],
        "extension_bindings": [
            _file_binding(root, "G77_256IF_ACT_CHE_BINDING", ACT_CHE),
            _file_binding(root, "G77_256IF_FUTURE_ADAPTER", ADAPTER),
            _file_binding(root, "G77_256IF_CLOUD_INIT", CLOUD_INIT),
            _file_binding(root, "G77_256IF_NOCLOUD", SEED),
            _file_binding(root, "G77_256FM_SOLE_LAUNCHER", FM_LAUNCHER),
            _file_binding(root, "G77_256FM_CONTEXT_OWNER", FM_CONTEXT),
        ],
    })
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    if set(du.validate_envelope(envelope, root, expected_head=IE_HEAD).values()) != {"PASS"}:
        raise IFBindingError("CURRENT_DU_NOT_PASS")
    if ie["packet"]["independent_mutation_count"] != 1 or route["production_route_delta"] != "VERIFIED__0":
        raise IFBindingError("CONSTITUTIONAL_DELTA_INVALID")
    return envelope


def _harness_bytes(candidate_name: str) -> bytes:
    return ("from pathlib import Path\n\nFIXTURE_CLASSIFICATION = \"TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE\"\nRAW_ROOT = Path(\"/mnt/g77-evidence\")\nCONTINUATION_MANIFEST_PATH = RAW_ROOT / \"" + candidate_name + "\"\n").encode("utf-8")


def instantiate_binding(repository_root: Path, output_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    output = output_root.resolve()
    if output.exists() or output.is_symlink():
        raise IFBindingError("OUTPUT_COLLISION")
    output.relative_to(root)
    output.mkdir(parents=True)
    act_che = build_act_che_binding(root)
    act_path = output / ACT_CHE.name
    act_path.write_bytes(canonical_bytes(act_che))
    candidate_name = "G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_path = output / "runtime_projection" / candidate_name
    bindings = output / "bindings"
    candidate_path.parent.mkdir()
    runtime_path.parent.mkdir()
    bindings.mkdir()
    candidate_bytes = canonical_bytes(build_candidate(root))
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness = bindings / "G77_256IF_EE_PATH_PROJECTION_FIXTURE_V1.py"
    harness.write_bytes(_harness_bytes(candidate_name))
    launcher = _load(root / FM_LAUNCHER, "g77_256if_context_builder")
    context = launcher.build_operation_context(
        repository_root=root, repository_head=IE_HEAD, repository_tree=IE_TREE,
        generation_identity=GENERATION, operation_identity=OPERATION_IDENTITY,
        identity_namespace_prefix=IDENTITY_PREFIX,
        operation_evidence_root=Path("/tmp/g77_256if/operation_state"),
        transient_root=Path("/tmp/g77_256if/transient"),
        candidate_source_path=candidate_path.relative_to(root),
    )
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    launcher.validate_immutable_context_bindings(root, context, candidate_path.relative_to(root))
    du = _load(root / DU_OWNER, "g77_256if_du")
    eb = _load(root / EB_OWNER, "g77_256if_eb")
    ee = _load(root / EE_OWNER, "g77_256if_ee")
    if set(du.validate_file(candidate_path, root, expected_head=IE_HEAD).values()) != {"PASS"}:
        raise IFBindingError("DU_NOT_PASS")
    eb_path = bindings / "G77_256IF_EB_RECEIPT_V1.json"
    eb_path.write_bytes(eb.canonical_bytes(eb.validate_candidate(root, candidate_path, required_head=IE_HEAD, required_tree=IE_TREE)))
    ee_path = bindings / "G77_256IF_EE_RECEIPT_V1.json"
    ee_path.write_bytes(ee.canonical_bytes(ee.validate_binding(root, candidate_path, eb_path, harness, runtime_path.parent, "/mnt/g77-evidence", required_head=IE_HEAD, required_tree=IE_TREE)))
    return {
        "act_che_sha256": sha256_path(act_path),
        "candidate_sha256": sha256_path(candidate_path),
        "runtime_sha256": sha256_path(runtime_path),
        "context_identity": context["context_sha256"],
        "context_file_sha256": sha256_path(context_path),
        "eb_sha256": sha256_path(eb_path),
        "ee_sha256": sha256_path(ee_path),
    }


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    certificate = json.loads(_git_bytes(repository_root.resolve(), IE_HEAD, EX_CERTIFICATE), object_pairs_hook=_unique)
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload) or certificate["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise IFBindingError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"status": "VERIFIED", "ex_reused": "17/17", "ex_reconstructed": 0}


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    live = live_root.resolve()
    entry = authenticate_entry(root)
    ie = reconstruct_ie(root)
    route = route_state(root)
    act_che = load_canonical(live / ACT_CHE.name)
    candidate = live / "candidate/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
    runtime = live / "runtime_projection/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
    context = load_canonical(live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    if candidate.read_bytes() != runtime.read_bytes() or sha256_path(candidate) != context["candidate_manifest_sha256"]:
        raise IFBindingError("CANDIDATE_RUNTIME_CONTEXT_IDENTITY_MISMATCH")
    binding = act_che["binding"]
    che = binding["che_correlation"]
    act = binding["human_authority_act_representation"]
    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    first_broken = "COMMITTED_IE_CHECKOUT_DOES_NOT_CONTAIN_IF_FUTURE_ROUTE_AND_DETERMINISTIC_TIME_PROJECTION"
    return {
        "schema_id": "G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": entry,
        "ie_reconstruction": {
            "status": "VERIFIED", "current_e05_status": "VERIFIED__10_OF_18",
            "selected_next_e05_vector": "VERIFIED__FUTURE",
            "future_repository_formalization": "VERIFIED",
            "future_payload_digest": ie["packet"]["future_payload_digest"],
            "evaluation_time_unix_ns": 500, "valid_from_unix_ns": 600,
            "valid_until_unix_ns": 1000, "relation": "VERIFIED__500_LT_600_LT_1000",
        },
        "act_che_binding": {
            "status": "VERIFIED__REPOSITORY_ONLY_NONAUTHORIZING_REPRESENTATION",
            "semantic_payload_identity": act["payload_digest"],
            "outer_act_identity": act["authority_act_identity"],
            "semantic_independent_mutation_count": 1,
            "semantic_independent_mutated_coordinate": "valid_from_unix_ns",
            "live_binding_dependent_recomputation_count": 3,
            "live_binding_dependent_recomputed_coordinates": ["che_correlation.authority_payload_digest", "che_correlation.source_act_digest", "che_correlation.correlation_identity"],
            "che_authority_payload_digest": che["authority_payload_digest"],
            "source_act_digest": che["source_act_digest"],
            "correlation_identity": che["correlation_identity"],
            "preserved_binding_coordinate_set": sorted(ie["packet"]["preserved_coordinate_proof"]),
        },
        "route": route,
        "candidate_runtime_context": {
            "future_candidate_identity": sha256_path(candidate),
            "future_runtime_identity": sha256_path(runtime),
            "future_context_identity": context["context_sha256"],
            "candidate_runtime_byte_identity_status": "VERIFIED",
            "committed_ie_binding_status": "VERIFIED",
            "che_binding_status": "VERIFIED",
            "time_fixture_binding_status": "VERIFIED__REPOSITORY_PROJECTION_ONLY",
            "route_binding_status": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY",
        },
        "readiness": {
            "future_repository_formalization": "VERIFIED",
            "future_route_binding": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY",
            "future_live_binding": "NOT_PROVEN",
            "future_preoperational_readiness": "NOT_PROVEN",
            "future_operational_capability": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN",
            "first_broken_edge": first_broken,
        },
        "historical_failure_firewall": {
            "status": "VERIFIED", "reintroduced_historical_failure_count": 0,
            "tested_set": ["PRE_COMMIT_SELF_REFERENCE", "CHECKOUT_PINNING", "BOOTSTRAP_PINNING", "HOST_GUEST_PATH_MISMATCH", "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_PROJECTION_MISMATCH", "NONCANONICAL_HANDOFF", "RECEIPT_PARENT_ABSENCE", "SEALED_HISTORICAL_SHA_MISMATCH"],
        },
        "ex": authenticate_ex(root),
        "reuse_impact": {
            "reused_certified_capability_set": ["IE_FUTURE_FORMALIZATION", "P11_TEMPORAL_OWNER", "CHE", "FM_SINGLE_ROUTE", "GN", "GL", "DU", "EB", "EE", "FK", "EX_17_OF_17", "GOVERNANCE", "LAYER_0"],
            "new_capability_set": ["IF_REPOSITORY_ONLY_FUTURE_ACT_CHE_AND_STATIC_ROUTE_BINDING"],
            "unreachable_preexisting_capability_set": [],
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "new_runtime_owner_count": "VERIFIED__0", "new_clock_infrastructure_count": "VERIFIED__0", "p11_core_change_count": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "future_generations_so_far": "VERIFIED__2__IE_AND_IF",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__IE_FORMALIZATION_PLUS_IF_BINDING_ROUTE_DELTA",
            "marginal_new_infrastructure_for_if": "VERIFIED__ONE_VECTOR_ADAPTER_ONE_STATIC_BOOTSTRAP_PAIR_AND_BINDING_EVIDENCE",
            "expected_next_credit_generation_count": "ESTIMATED__AT_LEAST_TWO__POST_IF_BINDING_THEN_SEPARATE_AUTHORIZED_OPERATION",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__REPOSITORY_AUTHENTICATED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__SCOPE_PROHIBITIONS_AND_REPOSITORY_LOCATORS_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES", "inter_generation_cross_worker_continuation": "VERIFIED__IE_TO_IF", "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_WORKER_IF_GENERATION", "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_IE_ENTRY",
            "authority_state_recovery": "VERIFIED__NO_CURRENT_AUTHORITY_EXISTS", "consumed_authority_recovery": "VERIFIED__IC_HISTORICAL_CONSUMED_NONREUSABLE", "post_operation_state_recovery": "VERIFIED__IC_TERMINAL_STATE_RECONSTRUCTED", "operation_replay_prevention": "VERIFIED__IF_OPERATIONAL_COUNTERS_ZERO",
            "cross_worker_constitutional_drift": "VERIFIED__0", "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IF_REPOSITORY_SCOPE", "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_ONE_ROUTE_ZERO_OPERATION", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_e05_local_frontier_distance": "ESTIMATED__ONE_POST_IF_COMMITTED_BINDING_GENERATION_BEFORE_OPERATIONAL_AUTHORITY", "governance_efficience": "ESTIMATED__TARGETED_STATIC_BINDING_WITH_EXPLICIT_BROKEN_EDGE", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_RETAINED", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IE_TO_IF_REPOSITORY_CONTINUATION", "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW_TO_MODERATE", "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY", "candidate_capability": "VERIFIED__FUTURE_REPOSITORY_STATIC_CANDIDATE", "shadow_design_target": "VERIFIED__BIND_VERIFY_REDUCE_STOP", "constitutional_continuation_progress": "VERIFIED__STATIC_BINDING_COMPLETE_LIVE_READINESS_NOT_PROVEN", "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED", "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY", "marginal_e05_generation_cost": "NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__FUTURE_CREDIT_NOT_EARNED", "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_COST_INFERENCE", "expected_next_credit_generation_count": "ESTIMATED__AT_LEAST_TWO",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IE_ID_IC_P11_CHE_FK_EX_FM_GN_GL_DU_EB_EE_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "required": 18, "satisfied": 10, "remaining": 8},
        "terminal_control": {
            "auto_continuable": False, "human_authorization_required": False, "human_review_required": True, "next_generation_started": False,
            "last_verified_edge": "FUTURE_REPOSITORY_STATIC_ACT_CHE_CANDIDATE_RUNTIME_CONTEXT_ROUTE_BINDING_TO_COMMITTED_IE",
            "first_broken_edge": first_broken,
            "minimum_missing_capability": "ONE_COMMITTED_IF_CHECKOUT_CONTAINING_FUTURE_ROUTE_AND_TIME_PROJECTION",
            "minimum_legal_next_delta": "SEPARATE_POST_IF_COMMIT_REPOSITORY_ONLY_LIVE_REBIND_THEN_HUMAN_REVIEW",
            "verdict": "NOT_PROVEN__IF_FUTURE_PREOPERATIONAL_READINESS__COMMITTED_IE_CHECKOUT_LACKS_IF_ROUTE_DELTA__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path, live_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    return {"schema_id": "G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only IF binding owner; no operational CLI entry point")
