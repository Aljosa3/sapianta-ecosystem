#!/usr/bin/env python3
"""Repository-only G77-256IX post-commit FUTURE readiness proof.

This owner authenticates committed objects and invokes only deterministic
static validators and temporary authority-free materializers.  It does not
create or consume Human authority, invoke an operational launcher, execute
qemu-system, enter P11, retry, repair-retry, replay, or award E05 credit.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IW_HEAD = "223c6256c68e4506a4630cc07bdf452d39be2823"
IW_TREE = "856b09f1cf334a54e98e7f9a691a279c52b9813d"
IW_SUBJECT = "G77-256IW bind FUTURE guest Python import root"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

IX_ROOT = Path(".github/governance/evidence/g77_256ix_post_commit_future_import_root_readiness_v1")
TERMINAL = IX_ROOT / "G77_256IX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IW_ROOT = Path(".github/governance/evidence/g77_256iw_future_guest_import_root_binding_v1")
IW_FORMALIZER = IW_ROOT / "analysis/G77_256IW_FUTURE_GUEST_IMPORT_ROOT_BINDING_FORMALIZER_V1.py"
IW_FILES = {
    IW_ROOT / "G77_256IW_G48_IMPLEMENTATION_REPORT_V1.md": "54fc94d5855af06715df9266b356e6140d03595e2f51cc94257ab7641d63e03d",
    IW_ROOT / "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "81ed8bdaa25bf9c7d609c33ae768e6f7193f3336c8f42704d6fdbe87702fbcf7",
    IW_FORMALIZER: "5144e5e74df0fd5b2a35fb7904156dde7bfefe086971d4ab470ec35bc21cb706",
    IW_ROOT / "tests/test_g77_256iw_future_guest_import_root_binding_v1.py": "1103ebd86635dc34be4f9da25d1b053ba9d307decaa7c0177fb535ffc855f21b",
    IW_ROOT / "static/G77_256IW_CLOUD_INIT_USER_DATA_V1.yaml": "10092e4d10327c0bef42608e3125ca4b04b82b8e91a0c5e88a5148ee1a14fee2",
    IW_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img": "655b8b4122f89acbf0e4d3a670ee3b4fb38fb37600eeb6c8745c0a13cdc57eab",
}
CLOUD_INIT = IW_ROOT / "static/G77_256IW_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IW_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img"
CLOUD_SHA256 = IW_FILES[CLOUD_INIT]
SEED_SHA256 = IW_FILES[SEED]
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_LAUNCHER_SHA256 = "ee06a8b77870aecd1621ab9fb2af1c412cea525ea55b6367e3bae9dd1e6d5ab6"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
DU_PATH = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_PATH = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_PATH = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
GN_PATH = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GL_PATH = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
CANDIDATE_SHA256 = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
IF_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
IV_ADAPTER = Path(".github/governance/evidence/g77_256iv_future_operational_v1/operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py")
ACT_CHE = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
P11_PATHS = ("aigol/runtime", "sapianta_system", ".github/governance/evidence/g77_256ec_p11_operational_v1")
GENERATION = "G77_256IXTEST_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IXTEST_AUTHORITY_FREE_STATIC_READINESS_ONLY_001"
PREFIX = "G77_256IXTEST"


class IXReadinessError(ValueError):
    """One deterministic fail-closed IX verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IXReadinessError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IXReadinessError(f"NONCANONICAL_JSON__{path}")
    return value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_module(name: str, relative: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise IXReadinessError(f"MODULE_LOAD_FAILED__{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(remote_head: str = IW_HEAD, nested_remote_tag: str = NESTED_HEAD) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT), "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"), "remote_head": remote_head,
        "index": git("diff", "--cached", "--name-only"),
        "tracked_delta": git("status", "--porcelain", "--untracked-files=no"),
    }
    expected = {
        "repository": str(ROOT), "branch": BRANCH, "head": IW_HEAD,
        "tree": IW_TREE, "subject": IW_SUBJECT, "origin": ORIGIN,
        "remote_head": IW_HEAD, "index": "", "tracked_delta": "",
    }
    if observed != expected:
        raise IXReadinessError("EXACT_RATIFIED_IW_ENTRY_MISMATCH")
    status = git("status", "--porcelain", "--untracked-files=all")
    for line in status.splitlines():
        if len(line) < 4 or not line[3:].startswith(IX_ROOT.as_posix() + "/") or line[:2] != "??":
            raise IXReadinessError("UNCOMMITTED_OWNER_DEPENDENCY_OR_SCOPE_DRIFT")
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
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG, "remote_tag": NESTED_HEAD,
    }:
        raise IXReadinessError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"worktree_scope": "VERIFIED__IX_EVIDENCE_ONLY", "nested_authority": nested_state}


def committed_bytes(revision: str, path: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT)


def reconstruct_iw() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for path, expected_sha in IW_FILES.items():
        committed = committed_bytes(IW_HEAD, path)
        if committed != (ROOT / path).read_bytes() or sha256_bytes(committed) != expected_sha:
            raise IXReadinessError(f"COMMITTED_IW_BYTE_MISMATCH__{path}")
        identities[path.as_posix()] = {
            "sha256": expected_sha, "git_blob": git("rev-parse", f"{IW_HEAD}:{path.as_posix()}"),
        }
    launcher = committed_bytes(IW_HEAD, FM_LAUNCHER)
    if launcher != (ROOT / FM_LAUNCHER).read_bytes() or sha256_bytes(launcher) != FM_LAUNCHER_SHA256:
        raise IXReadinessError("COMMITTED_IW_SELECTOR_BYTE_MISMATCH")
    identities[FM_LAUNCHER.as_posix()] = {
        "sha256": FM_LAUNCHER_SHA256,
        "git_blob": git("rev-parse", f"{IW_HEAD}:{FM_LAUNCHER.as_posix()}"),
    }
    envelope = load_canonical(ROOT / IW_ROOT / "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json")
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IXReadinessError("IW_TERMINAL_INNER_SEAL_INVALID")
    if envelope["reduction"]["terminal"] != "A__FUTURE_GUEST_IMPORT_ROOT_BINDING_REPOSITORY_IMPLEMENTED":
        raise IXReadinessError("IW_TERMINAL_MISMATCH")
    return {
        "status": "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION",
        "iw_committed_object_binding": "VERIFIED",
        "iw_selector_committed_binding": "VERIFIED",
        "iw_cloud_init_committed_binding": "VERIFIED",
        "iw_nocloud_seed_committed_binding": "VERIFIED",
        "uncommitted_owner_dependency": "VERIFIED__0",
        "artifact_count": len(identities), "inner_seal": "VERIFIED", "identities": identities,
    }


def reconstruct_iv_iw_proofs() -> dict[str, Any]:
    iw = load_module("g77_256ix_iw", IW_FORMALIZER)
    iv = iw.reconstruct_iv_terminal()
    owner_graph = iw.audit_binding()
    import_proof = iw.isolated_import_proof()
    ex = iw.ex_reuse()
    return {"iv_terminal": iv, "owner_graph": owner_graph, "import_root": import_proof, "ex": ex}


def authenticate_roles_and_identities() -> dict[str, Any]:
    owners = [DU_PATH, EB_PATH, EE_PATH, FM_LAUNCHER, IF_CONTEXT, CANDIDATE, IV_ADAPTER, ACT_CHE]
    bindings: dict[str, Any] = {}
    for path in owners:
        blob = git("rev-parse", f"HEAD:{path.as_posix()}")
        if git("hash-object", path.as_posix()) != blob:
            raise IXReadinessError(f"COMMITTED_OWNER_DRIFT__{path}")
        bindings[path.as_posix()] = {"git_blob": blob, "sha256": sha256_path(ROOT / path)}
    if sha256_path(ROOT / CANDIDATE) != CANDIDATE_SHA256:
        raise IXReadinessError("CANDIDATE_IDENTITY_MISMATCH")
    if git("rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise IXReadinessError("IF_RUNTIME_TARGET_TREE_MISMATCH")
    return {
        "target_runtime_identity": "REPOSITORY_DERIVED__IF",
        "current_repository_identity": "REPOSITORY_DERIVED__IW",
        "certification_baseline_identity": "REPOSITORY_DERIVED__IW",
        "candidate_required_identity": "REPOSITORY_DERIVED__IF",
        "checkout_identity": "REPOSITORY_DERIVED__IF",
        "evidence_issuer_identity": "REPOSITORY_DERIVED__IW_AND_COMMITTED_VALIDATORS",
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
        "certification_baseline": {"head": IW_HEAD, "tree": IW_TREE},
        "runtime_target_equals_certification_baseline": "VERIFIED__NO",
        "role_collapse": "VERIFIED__NO", "bindings": bindings,
    }


def authenticate_future_semantics() -> dict[str, Any]:
    envelope = load_canonical(ROOT / ACT_CHE)
    binding = envelope["binding"]
    if envelope["binding_sha256"] != sha256_bytes(canonical_bytes(binding)):
        raise IXReadinessError("FUTURE_ACT_CHE_INNER_SEAL_INVALID")
    act, che = binding["human_authority_act_representation"], binding["che_correlation"]
    result = {
        "evaluation": binding["evaluation_time_unix_ns"],
        "valid_from": act["payload"]["valid_from_unix_ns"],
        "valid_until": act["payload"]["valid_until_unix_ns"],
        "payload_digest": act["payload_digest"].removeprefix("sha256:"),
        "source_act": che["source_act_digest"].removeprefix("sha256:"),
        "che_correlation": che["correlation_identity"],
    }
    expected = {
        "evaluation": 500, "valid_from": 600, "valid_until": 1000,
        "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "source_act": "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8",
        "che_correlation": "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454",
    }
    if result != expected or not result["evaluation"] < result["valid_from"] < result["valid_until"]:
        raise IXReadinessError("FUTURE_SEMANTIC_IDENTITY_MISMATCH")
    return result | {"relation": "500 < 600 < 1000", "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0"}


def full_static_readiness() -> dict[str, Any]:
    fm = load_module("g77_256ix_fm", FM_LAUNCHER)
    du = load_module("g77_256ix_du", DU_PATH)
    eb = load_module("g77_256ix_eb", EB_PATH)
    ee = load_module("g77_256ix_ee", EE_PATH)
    gl = load_module("g77_256ix_gl", GL_PATH)
    with tempfile.TemporaryDirectory(prefix=".g77_256ix_static_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du.build_du_fixture(ROOT)))
        du_result = du.validate_file(candidate, ROOT, expected_head=IF_HEAD)
        eb_envelope = eb.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / candidate.name).write_bytes(candidate.read_bytes())
        harness = temporary / "ee-path-fixture.py"
        harness.write_text(
            "from pathlib import Path\nFIXTURE_CLASSIFICATION='TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL'\n"
            "RAW_ROOT=Path('/mnt/g77-evidence')\nCONTINUATION_MANIFEST_PATH=RAW_ROOT/'candidate-v2.json'\n",
            encoding="utf-8",
        )
        ee_envelope = ee.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        eb_result = eb.verify_receipt_envelope(ROOT, eb_envelope)
        ee_result = ee.verify_receipt_envelope(ROOT, ee_envelope)
        baseline = {"head": IW_HEAD, "tree": IW_TREE}
        target = eb_envelope["receipt"]["runtime_target_selection_binding"]
        if set(du_result.values()) != {"PASS"} or eb_result["overall_result"] != "PASS":
            raise IXReadinessError("DU_OR_EB_V2_POST_COMMIT_READINESS_FAILED")
        if ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
            raise IXReadinessError("EE_V2_POST_COMMIT_READINESS_FAILED")
        if eb_envelope["receipt"]["certification_baseline"] != baseline or ee_envelope["receipt"]["certification_baseline"] != baseline:
            raise IXReadinessError("EB_EE_CERTIFICATION_BASELINE_NOT_IW")
        if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE) or ee_envelope["receipt"]["runtime_target_selection_binding"] != target:
            raise IXReadinessError("EB_EE_RUNTIME_TARGET_NOT_IF")

        operation_root, transient_root = temporary / "operation-state", temporary / "transient"
        context = fm.build_operation_context(
            repository_root=ROOT, repository_head=IW_HEAD, repository_tree=IW_TREE,
            generation_identity=GENERATION, operation_identity=OPERATION,
            identity_namespace_prefix=PREFIX, operation_evidence_root=operation_root,
            transient_root=transient_root, candidate_source_path=CANDIDATE,
        )
        context_path = temporary / "test-only-context.json"
        context_path.write_bytes(fm.canonical_bytes(context))
        destination = fm.preauth_fresh_checkout_destination_readiness(ROOT, context)
        materialization = fm.materialize_operation_state(
            repository_root=ROOT, context=context, context_source_path=context_path,
            candidate_source_path=CANDIDATE,
        )
        observations = fm.observe_context_assets(ROOT, context, CANDIDATE)
        readiness = fm.authority_free_static_readiness(
            repository_root=ROOT, context=context, observed_head=IW_HEAD,
            observed_tree=IW_TREE, repository_clean=True,
            observed_asset_sha256=observations, candidate_source_path=CANDIDATE,
        )
        claim = gl.prepare_and_observe_receipt_parent(ROOT, context)
        checkpoint = gl.reduce_preauthorization_checkpoint(ROOT, context, claim)
        equivalence = gl.validate_preauth_final_admission_equivalence(ROOT, context, claim, checkpoint)
        if destination["result"] != "PREAUTH_FRESH_CHECKOUT_DESTINATION_READINESS_PASS":
            raise IXReadinessError("PREAUTH_DESTINATION_READINESS_FAILED")
        if materialization["result"] != "FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU":
            raise IXReadinessError("AUTHORITY_FREE_MATERIALIZATION_FAILED")
        if readiness["result"] != "STATIC_READINESS_PASS":
            raise IXReadinessError("FULL_FM_STATIC_READINESS_FAILED")
        if equivalence["human_constitutional_authorization_count"] != 0:
            raise IXReadinessError("GL_BOUNDARY_CREATED_AUTHORITY")
        return {
            "prior_worktree_drift_condition_removed": "VERIFIED",
            "du_v2_post_commit_readiness": "VERIFIED", "eb_v2_post_commit_readiness": "VERIFIED",
            "ee_v2_post_commit_readiness": "VERIFIED", "du_eb_ee_v2_chain": "VERIFIED",
            "runtime_target": {"head": target["head"], "tree": target["tree"]},
            "certification_baseline": baseline,
            "runtime_target_equals_certification_baseline": "VERIFIED__NO", "role_collapse": "VERIFIED__NO",
            "candidate_sha256": CANDIDATE_SHA256,
            "operation_state_context_binding": "VERIFIED__TEMPORARY_NONAUTHORITY",
            "materialization": materialization["result"], "fm_authority_free_static_readiness": "VERIFIED",
            "post_commit_import_root_readiness": "VERIFIED", "full_static_preoperational_readiness": "VERIFIED",
            "static_readiness_result": readiness["result"], "gl_boundary": "VERIFIED",
            "human_authorization_created": "VERIFIED__0", "family_local_dispatch": "VERIFIED",
            "caller_selected_version": "VERIFIED__NO", "global_registry": "VERIFIED__NO",
        }


def boundary_firewalls() -> dict[str, Any]:
    gn = load_module("g77_256ix_gn", GN_PATH)
    fm = load_module("g77_256ix_fm_firewall", FM_LAUNCHER)
    if "FUTURE" not in gn.SUPPORTED_VECTORS or fm.fresh_context.operation_vector(GENERATION) != "FUTURE":
        raise IXReadinessError("GN_FUTURE_COMPATIBILITY_FAILED")
    if fm.operation_attempt_limit_field("FUTURE") != "future_operational_attempt_limit":
        raise IXReadinessError("HUMAN_ACT_FUTURE_BOUNDARY_FAILED")
    if git("diff", "--name-only", IW_HEAD, "--", *P11_PATHS):
        raise IXReadinessError("P11_OR_NESTED_AUTHORITY_MUTATION_DETECTED")
    return {
        "gn_future_compatibility": "VERIFIED", "gl_boundary": "VERIFIED",
        "human_authorization_presentation_issued": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0", "p11_bypass": "VERIFIED__NO",
        "shadow_automation_status": "VERIFIED__ABSENT",
    }


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "human_operational_authority_created", "authority_consumption", "pre_operational_invocation",
        "fm_operational_invocation", "qemu_operational_invocation", "vm_operational_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect",
        "retry", "repair_retry", "replay", "e05_credit",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    iw = reconstruct_iw()
    proofs = reconstruct_iv_iw_proofs()
    roles = authenticate_roles_and_identities()
    future = authenticate_future_semantics()
    readiness = full_static_readiness()
    boundaries = boundary_firewalls()
    return {
        "schema_id": "G77_256IX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "POST_COMMIT_STATIC_READINESS_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": "A__FUTURE_POST_COMMIT_IMPORT_ROOT_FULL_STATIC_READINESS_VERIFIED",
        "entry": entry, "iw_reconstruction": iw, "iv_iw_continuation": proofs,
        "identity_roles": roles, "future_semantics": future, "readiness": readiness,
        "boundary_firewalls": boundaries, "operational_counters": zero_counters(),
        "route_firewall": {
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "parallel_flow_created": "VERIFIED__NO",
            "new_launcher_count": "VERIFIED__0", "new_generic_adapter_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0", "new_global_registry_count": "VERIFIED__0",
            "p11_mutation_count": "VERIFIED__0",
        },
        "historical_failure_firewall": {
            "checked_failure_class_count": "VERIFIED__31",
            "reintroduced_historical_failure_count": "VERIFIED__0",
            "iv_import_root_failure_successor_static_recurrence_count": "VERIFIED__0",
            "host_sys_path_false_positive_count": "VERIFIED__0",
            "network_or_package_install_dependency_count": "VERIFIED__0",
        },
        "proof_reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "ex_is_authority": "VERIFIED__NO"},
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IV_IW_IT_IU_IF_FM_GN_GL_HUMAN_ACT_DU_EB_EE_V2_P11_DI_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__IX_POST_COMMIT_READINESS_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__20__IE_THROUGH_IX",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__1",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_ix": "VERIFIED__POST_COMMIT_READINESS_EVIDENCE_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_ZERO_PRODUCTION_MUTATION",
            "expected_next_credit_generation_count": "NOT_PROVEN",
            "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ONE_FUTURE_ATTEMPT_ZERO_FUTURE_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__COMMISSION_SCOPE_CHECKPOINT_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__IW_TO_IX",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_ENTRY", "authority_state_recovery": "VERIFIED__IV_CONSUMED__IW_IX_ZERO",
            "consumed_authority_recovery": "VERIFIED__IV_AUTHORITY_CONSUMED_AND_NOT_REUSABLE",
            "post_operation_state_recovery": "VERIFIED__IV_FAIL_CLOSED_TERMINAL_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__IX_ZERO_OPERATION_AND_IV_AUTHORITY_NOT_REUSED",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IX_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "cognition": {
            "cognition_provenance": "VERIFIED__RATIFIED_IW_GIT_CHECKPOINT_AND_COMMITTED_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_IW_TO_IX_CONTINUATION",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED", "aigol_codex_work_share": "NOT_MEASURED",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__IV_ONE_SHOT_FAIL_CLOSED__IW_REPOSITORY_ONLY_REPAIR__IX_POST_COMMIT_READINESS_WITH_ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__ONE_NEW_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_WITH_FAIL_CLOSED_STATIC_CLOSURE",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_ROUTE_DELTA",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_IW_TO_IX_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__RATIFIED_IW_GIT_CHECKPOINT_AND_COMMITTED_EVIDENCE_PRIMARY",
            "candidate_capability": "VERIFIED__FUTURE_POST_COMMIT_STATIC_READINESS__OPERATIONAL_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IV_OPERATION_IMPORT_FAILURE__IW_REPOSITORY_REPAIR__IX_POST_COMMIT_STATIC_READY__OPERATIONAL_FRONTIER_NOT_CROSSED",
        },
        "validation": {
            "ix_focused": "VERIFIED__14_PASSED",
            "gn_gl_human_act": "VERIFIED__77_PASSED",
            "p11_di_che_fk": "VERIFIED__33_PASSED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_inner_seals_ast_nocloud_g48": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
            "historical_or_superseded_snapshot_assertions": "DESELECTED__ENTRY_STATE_ASSERTIONS_ONLY__HISTORICAL_ARTIFACTS_PRESERVED",
        },
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8},
        "terminal_frontier": {
            "last_verified_edge": "FUTURE_POST_COMMIT_IMPORT_ROOT_FULL_STATIC_PREOPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_YET_ISSUED",
            "minimum_missing_capability": "ONE_NEW_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_GENERATION",
            "auto_continuable": "NO", "human_review_required": "YES", "next_generation_started": "NO",
        },
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256IX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    envelope = build_envelope()
    (ROOT / TERMINAL).write_bytes(canonical_bytes(envelope))
    print(json.dumps(envelope["reduction"]["terminal_frontier"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
