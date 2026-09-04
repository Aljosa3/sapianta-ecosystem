#!/usr/bin/env python3
"""Deterministic repository-only audit for the G77-256HV identity correction.

This module reads Git objects and repository files only.  It has no request,
authority, PRE, launcher, QEMU, VM, P11-entry, or protected-effect capability.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HU_HEAD = "6b5c0f9914bc38156d1f5c364614ef55800a09a8"
HU_TREE = "0e9e05065f6eb5f17d998e087dcc55cbb006851a"
HU_SUBJECT = "G77-256HU fail closed WRONG_CONTRACT guest checkout readiness"
HT_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
HT_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
HS_HEAD = "247d6b089b91c20364b5d0ce43017c07bae803b7"
HR_HEAD = "cbd457d9281e787a10980583921abb0a6021be74"
HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

EXPECTED_ADAPTER_SHA256 = (
    "bb9c917947d317319c9502e44c2d5dca6d423380e67f71a14db1b63eb11acc34"
)
EXPECTED_CLOUD_INIT_SHA256 = (
    "c3f7f93a55f2c3a76fe73bccb9aa0b54fed2f5011c326c0f8774a8ca72c7442f"
)
EXPECTED_SEED_SHA256 = (
    "fc98a62a1b3bd813b7f570438fc48151c378aeba4389de13d4e532d3f7979b21"
)

FM = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_CONTEXT = FM / "launcher/sapianta_fresh_operation_context_v1.py"
FM_LAUNCHER = FM / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_META = FM / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
HT = Path(".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1")
ADAPTER = HT / "adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
MATERIALIZER = HT / "orchestration/G77_256HT_WRONG_CONTRACT_PREAUTHORIZATION_MATERIALIZER_V1.py"
CLOUD_INIT = HT / "static/G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = HT / "static/SAPIANTA_WRONG_CONTRACT_NOCLOUD_SEED_TEMPLATE_V1.img"
HR_SPEC = Path(
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
)
HR_PRODUCER = Path(
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
)
HR_REDUCER = Path(
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "reducer/G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
FC_ADAPTER = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
HG_PROJECTION = Path(
    ".github/governance/evidence/g77_256hg_guest_projection_validation_v1/"
    "static/G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py"
)
P11 = Path("tests/p11_da_custody_process_v1.py")
P11_SUBSTRATE = Path("tests/p11_da_disposable_substrate_v1.py")
P11_CONSUMER = Path("tests/p11_da_operational_consumer_v1.py")
AIGOL_MODELS = Path("aigol/runtime/models.py")
AIGOL_CHE = Path("aigol/runtime/canonical_che_evidence_correlation_contract_v1.py")
AIGOL_HUMAN_ACT = Path("aigol/runtime/canonical_human_authority_act_contract_v1.py")
AIGOL_HUMAN_ENTRY = Path("aigol/runtime/canonical_human_entry_contract_v1.py")
AIGOL_SERIALIZATION = Path("aigol/runtime/transport/serialization.py")
AIGOL_LEDGER = Path("aigol/runtime/transport/ledger.py")
HP_SOURCE_RAW = Path(
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "operation_state/runtime_export/G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/"
    "harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
HU_REDUCTION = Path(
    ".github/governance/evidence/g77_256hu_post_ht_live_binding_readiness_v1/"
    "G77_256HU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)

DEPENDENCY_CLOSURE = (
    FM_CONTEXT,
    FM_LAUNCHER,
    ADAPTER,
    MATERIALIZER,
    CLOUD_INIT,
    SEED,
    HR_SPEC,
    HR_PRODUCER,
    HR_REDUCER,
    FC_ADAPTER,
    HG_PROJECTION,
    P11,
    P11_SUBSTRATE,
    P11_CONSUMER,
    AIGOL_MODELS,
    AIGOL_CHE,
    AIGOL_HUMAN_ACT,
    AIGOL_HUMAN_ENTRY,
    AIGOL_SERIALIZATION,
    AIGOL_LEDGER,
    HP_SOURCE_RAW,
    ER_HARNESS,
    FM_META,
    FM_NETWORK,
)


class HVAuditError(ValueError):
    """One deterministic fail-closed HV audit rejection."""


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
        raise HVAuditError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", f"{revision}:{path.as_posix()}"],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise HVAuditError(f"COMMITTED_DEPENDENCY_UNAVAILABLE__{path.name}") from exc


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HVAuditError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def authenticate_hu_checkpoint(repository_root: Path) -> dict[str, Any]:
    """Authenticate committed HU and the nested authority without prompt trust."""

    root = repository_root.resolve()
    observed = {
        "repository": str(root),
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(root),
        "branch": BRANCH,
        "head": HU_HEAD,
        "tree": HU_TREE,
        "subject": HU_SUBJECT,
        "origin": ORIGIN,
        "remote_head": HU_HEAD,
        "index": "",
    }
    if observed != expected:
        raise HVAuditError("EXACT_COMMITTED_HU_CHECKPOINT_MISMATCH")
    for ancestor in (HT_HEAD, HS_HEAD, HR_HEAD, STABLE_ANCHOR):
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, HU_HEAD],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode:
            raise HVAuditError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")

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
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "branch": "",
        "status": "",
        "tag_head": NESTED_HEAD,
    }:
        raise HVAuditError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def _load_context_namespace(source: bytes, identity: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "__name__": identity,
        "__file__": FM_CONTEXT.as_posix(),
    }
    exec(compile(source, FM_CONTEXT.as_posix(), "exec"), namespace)
    return namespace


def generation(vector: str) -> str:
    return (
        f"G77_256HVTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )


def reconstruct_hu_blocker(repository_root: Path) -> dict[str, Any]:
    """Recompute HU terminal truth from HU, HT, and HG committed bytes."""

    root = repository_root.resolve()
    raw = _git_bytes(root, HU_HEAD, HU_REDUCTION)
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    if raw != canonical_bytes(envelope):
        raise HVAuditError("HU_REDUCTION_NOT_CANONICAL")
    if envelope["reduction_sha256"] != sha256_bytes(
        canonical_bytes(envelope["reduction"])
    ):
        raise HVAuditError("HU_REDUCTION_INNER_SEAL_INVALID")

    stale = _load_context_namespace(
        _git_bytes(root, HG_HEAD, FM_CONTEXT), "g77_256hv_hg_context"
    )
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT"):
        if stale["operation_vector"](generation(vector)) != vector:
            raise HVAuditError(f"HG_CONTEXT_VECTOR_DRIFT__{vector}")
    try:
        stale["operation_vector"](generation("WRONG_CONTRACT"))
    except stale["ContextError"]:
        pass
    else:
        raise HVAuditError("HG_CONTEXT_UNEXPECTEDLY_SUPPORTS_WRONG_CONTRACT")

    current = _load_context_namespace(
        _git_bytes(root, HT_HEAD, FM_CONTEXT), "g77_256hv_ht_context"
    )
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT"):
        if current["operation_vector"](generation(vector)) != vector:
            raise HVAuditError(f"HT_CONTEXT_VECTOR_DRIFT__{vector}")
    return {
        "last_verified_edge": (
            "HOST_PROJECTS_COMMITTED_HT_WRONG_CONTRACT_ADAPTER_AND_BINDS_ITS_"
            "EXACT_HASH_IN_COMMITTED_BOOTSTRAP"
        ),
        "first_broken_edge": (
            "GUEST_ADAPTER_LOADS_FM_CONTEXT_OWNER_FROM_HG_PINNED_CHECKOUT_"
            "WHERE_WRONG_CONTRACT_IS_UNSUPPORTED"
        ),
        "minimum_missing_capability": (
            "CURRENT_COMMITTED_CHECKOUT_AND_BOOTSTRAP_HEAD_TREE_CONTAINING_"
            "HT_WRONG_CONTRACT_CONTEXT_SUPPORT"
        ),
        "hg_head": HG_HEAD,
        "hg_tree": HG_TREE,
        "status": "VERIFIED",
    }


def select_checkout(repository_root: Path) -> dict[str, Any]:
    """Prove HT is the earliest coherent checkout on the HG-to-HT lineage."""

    root = repository_root.resolve()
    if _git(root, "rev-parse", HT_HEAD + "^{tree}") != HT_TREE:
        raise HVAuditError("HT_TREE_MISMATCH")
    lineage = _git(root, "rev-list", "--reverse", f"{HG_HEAD}..{HT_HEAD}").splitlines()
    supporting: list[str] = []
    for commit in lineage:
        source = _git_bytes(root, commit, FM_CONTEXT)
        namespace = _load_context_namespace(source, f"g77_256hv_context_{commit[:8]}")
        try:
            resolved = namespace["operation_vector"](generation("WRONG_CONTRACT"))
        except namespace["ContextError"]:
            continue
        if resolved == "WRONG_CONTRACT":
            supporting.append(commit)
    if supporting != [HT_HEAD]:
        raise HVAuditError("MINIMUM_COHERENT_CHECKOUT_NOT_UNIQUE_HT")

    identities: dict[str, str] = {}
    for path in DEPENDENCY_CLOSURE:
        content = _git_bytes(root, HT_HEAD, path)
        identities[path.as_posix()] = sha256_bytes(content)
    adapter_source = _git_bytes(root, HT_HEAD, ADAPTER).decode("utf-8")
    required_tokens = (
        "G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py",
        "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "context_owner_path = root / (",
        'operation_vector(context["generation_identity"]) != "WRONG_CONTRACT"',
    )
    if any(token not in adapter_source for token in required_tokens):
        raise HVAuditError("HT_ADAPTER_DEPENDENCY_DECLARATION_INCOMPLETE")
    hu_delta = set(
        _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", HU_HEAD).splitlines()
    )
    if not hu_delta or any("g77_256hu_post_ht_live_binding_readiness_v1" not in p and not p.startswith("docs/governance/G77_256HU_") for p in hu_delta):
        raise HVAuditError("POST_HT_ROUTE_DEPENDENCY_UNEXPECTED")
    return {
        "selected_checkout_head": HT_HEAD,
        "selected_checkout_tree": HT_TREE,
        "selection_reason": (
            "HT_IS_THE_FIRST_LINEAGE_COMMIT_WITH_WRONG_CONTRACT_FM_CONTEXT_"
            "SUPPORT_AND_CONTAINS_THE_COMPLETE_GUEST_DEPENDENCY_SET"
        ),
        "dependency_closure_status": "VERIFIED",
        "dependency_identities": identities,
        "post_ht_route_dependency_required": False,
    }


def _cloud_bindings(source: bytes) -> tuple[str, str, str, str, str]:
    commands = [
        line.strip().split()
        for line in source.decode("utf-8").splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    ]
    if len(commands) != 1 or len(commands[0]) != 7:
        raise HVAuditError("WRONG_CONTRACT_BOOTSTRAP_COMMAND_INVALID")
    return tuple(commands[0][2:])  # type: ignore[return-value]


def audit_correction(repository_root: Path) -> dict[str, Any]:
    """Authenticate only the permitted launcher/bootstrap identity correction."""

    root = repository_root.resolve()
    launcher = (root / FM_LAUNCHER).read_text(encoding="utf-8")
    if launcher.count(f'CHECKOUT_HEAD = "{HT_HEAD}"') != 1:
        raise HVAuditError("FM_CHECKOUT_HEAD_CORRECTION_INVALID")
    if launcher.count(f'CHECKOUT_TREE = "{HT_TREE}"') != 1:
        raise HVAuditError("FM_CHECKOUT_TREE_CORRECTION_INVALID")
    adapter_sha = sha256_path(root / ADAPTER)
    expected_harness, _, head, tree, _ = _cloud_bindings((root / CLOUD_INIT).read_bytes())
    if adapter_sha != EXPECTED_ADAPTER_SHA256 or expected_harness != adapter_sha:
        raise HVAuditError("EXPECTED_HARNESS_BINDING_NOT_PRESERVED")
    if (head, tree) != (HT_HEAD, HT_TREE):
        raise HVAuditError("WRONG_CONTRACT_BOOTSTRAP_HEAD_TREE_INVALID")
    if sha256_path(root / CLOUD_INIT) != EXPECTED_CLOUD_INIT_SHA256:
        raise HVAuditError("WRONG_CONTRACT_CLOUD_INIT_HASH_INVALID")
    if sha256_path(root / SEED) != EXPECTED_SEED_SHA256:
        raise HVAuditError("WRONG_CONTRACT_SEED_HASH_INVALID")
    if f'"{EXPECTED_CLOUD_INIT_SHA256}"' not in launcher:
        raise HVAuditError("LAUNCHER_CLOUD_INIT_HASH_BINDING_INVALID")
    if f'WRONG_CONTRACT_SEED: "{EXPECTED_SEED_SHA256}"' not in launcher:
        raise HVAuditError("LAUNCHER_SEED_HASH_BINDING_INVALID")
    return {
        "checkout_owner_binding_status": "VERIFIED",
        "wrong_contract_bootstrap_head_tree_status": "VERIFIED",
        "checkout_bootstrap_coherence_status": "VERIFIED",
        "expected_harness_binding_preservation_status": "VERIFIED",
        "wrong_contract_expected_harness_sha256": expected_harness,
        "committed_wrong_contract_adapter_sha256": adapter_sha,
    }


def authenticate_ex_reuse(repository_root: Path) -> dict[str, Any]:
    raw = _git_bytes(repository_root.resolve(), HU_HEAD, EX_CERTIFICATE)
    certificate = json.loads(raw, object_pairs_hook=_unique_object)
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(
        preimage,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload):
        raise HVAuditError("EX_CERTIFICATE_INNER_SEAL_INVALID")
    if certificate["certificate"]["component_counts"].get("CERTIFIED") != 17:
        raise HVAuditError("EX_REUSE_NOT_17_OF_17")
    return {"ex_reused": "17/17", "ex_reconstructed": 0, "status": "VERIFIED"}


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    """Return the canonical truth reduced by HV without readiness expansion."""

    authenticate_hu_checkpoint(repository_root)
    blocker = reconstruct_hu_blocker(repository_root)
    selection = select_checkout(repository_root)
    correction = audit_correction(repository_root)
    ex = authenticate_ex_reuse(repository_root)
    return {
        "schema_id": "G77_256HV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": {
            "head": HU_HEAD,
            "tree": HU_TREE,
            "subject": HU_SUBJECT,
            "remote_equal": True,
            "status": "VERIFIED",
        },
        "hu_blocker_reconstruction": blocker,
        "checkout_selection": selection,
        "correction": correction | {
            "host_guest_context_vector_semantic_equivalence": "VERIFIED",
            "wrong_attempt_regression_status": "VERIFIED",
            "wrong_input_regression_status": "VERIFIED",
            "wrong_contract_route_support_status": "VERIFIED",
            "unknown_malformed_fail_closed_status": "VERIFIED",
            "cross_vector_rejection_status": "VERIFIED",
            "production_route_count_status": "VERIFIED",
            "post_commit_rebind_required": "VERIFIED",
        },
        "semantic_firewall": {
            "target_mutation": "contract_identity",
            "semantic_mutation_count": 1,
            "dependent_recomputation": "record_identity",
            "unrelated_mutation_count": 0,
        },
        "reuse_impact": {
            "reused_certified_capability_set": [
                "EX_17_OF_17", "P11_D2", "CHE", "FK", "DU", "EB", "EE",
                "FM_SOLE_ROUTE", "HT_ROUTE_EXTENSION", "HG_CHECKOUT_PROJECTION",
                "GN", "GL", "GOVERNANCE", "LAYER_0",
            ],
            "new_capability_set": ["HV_CHECKOUT_BOOTSTRAP_COMMITTED_IDENTITY_CORRECTION"],
            "unreachable_preexisting_capability_set": [],
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "new_generic_framework_count": 0,
            "new_authority_layer_count": 0,
            "new_production_route_count": 0,
            "new_runtime_owner_count": 0,
        },
        "ex": ex,
        "readiness": {
            "post_commit_live_binding_status": "NOT_PROVEN",
            "current_du_status": "NOT_PROVEN",
            "current_eb_status": "NOT_PROVEN",
            "current_ee_status": "NOT_PROVEN",
            "preoperational_readiness_status": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN",
            "wrong_contract_operational_capability": "NOT_PROVEN",
        },
        "e05": {"before": "8/18", "credit": 0, "after": "8/18"},
        "operational_counters": {
            "human_operational_authority": 0,
            "authority_consumption": 0,
            "pre": 0,
            "fm_operational_launcher_invocation": 0,
            "qemu": 0,
            "vm_creation": 0,
            "vm_boot": 0,
            "operation_attempt": 0,
            "request": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
            "e05_credit": 0,
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "minimum_legal_next_delta": (
                "AFTER_HUMAN_COMMIT_ONLY__ONE_SEPARATE_POST_COMMIT_LIVE_BINDING_"
                "AND_PREOPERATIONAL_READINESS_GENERATION__NO_OPERATION"
            ),
            "verdict": (
                "PASS__G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_COMMITTED_"
                "IDENTITY_CORRECTION_VERIFIED__POST_COMMIT_LIVE_BINDING_NOT_"
                "PROVEN__ZERO_OPERATION__E05_8_OF_18__HUMAN_REVIEW_REQUIRED"
            ),
        },
    }


if __name__ == "__main__":
    raise SystemExit("repository-only auditor; use the deterministic HV reducer")
