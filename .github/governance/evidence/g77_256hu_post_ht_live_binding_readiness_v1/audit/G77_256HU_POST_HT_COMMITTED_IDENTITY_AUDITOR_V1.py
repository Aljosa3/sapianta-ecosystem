#!/usr/bin/env python3
"""Authenticate committed HT and fail closed before any operational boundary.

HU is a repository-only audit.  This owner never creates a request, authority,
candidate, runtime projection, operation context, receipt, VM, or P11 entry.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
import re
import subprocess
from typing import Any


EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
EXPECTED_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
EXPECTED_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
EXPECTED_SUBJECT = "G77-256HT extend existing route for WRONG_CONTRACT"
EXPECTED_PARENT = "247d6b089b91c20364b5d0ce43017c07bae803b7"
EXPECTED_ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
REQUIRED_ANCESTORS = (
    "247d6b089b91c20364b5d0ce43017c07bae803b7",
    "cbd457d9281e787a10980583921abb0a6021be74",
    "fc7c4ad58722ac280fd3a6bed6bd7f41856c4ffb",
    "5c972e9960987ab27420395b54ace693df097e7b",
)
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
VECTOR = "WRONG_CONTRACT"
GENERATION = (
    "G77_256HU_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_"
    "OPERATIONAL_COMMISSIONING_V1"
)

HT = Path(".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1")
HT_TERMINAL = HT / "G77_256HT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HT_REPORT = HT / "G77_256HT_G48_IMPLEMENTATION_REPORT_V1.md"
ADAPTER = HT / "adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
MATERIALIZER = HT / "orchestration/G77_256HT_WRONG_CONTRACT_PREAUTHORIZATION_MATERIALIZER_V1.py"
CLOUD_INIT = HT / "static/G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = HT / "static/SAPIANTA_WRONG_CONTRACT_NOCLOUD_SEED_TEMPLATE_V1.img"
FM_CONTEXT = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_OWNER = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
HR = Path(".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1")
HR_SPEC = HR / "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
HR_PRODUCER = HR / "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
HR_REDUCER = HR / "reducer/G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_REDUCER_V1.py"
HG_PROJECTION = Path(
    ".github/governance/evidence/g77_256hg_guest_projection_validation_v1/static/"
    "G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py"
)
P11_OWNER = Path("tests/p11_da_custody_process_v1.py")
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

IDENTITY_PATHS = {
    "HT_TERMINAL_REDUCTION": (HT_TERMINAL, "committed HT terminal claims"),
    "HT_G48_REPORT": (HT_REPORT, "committed HT G48 report"),
    "FM_CONTEXT_OWNER": (FM_CONTEXT, "host and guest context semantics"),
    "FM_LAUNCHER": (FM_LAUNCHER, "sole production route and checkout owner"),
    "GN_PRESENTATION_OWNER": (GN_OWNER, "presentation binding owner"),
    "WRONG_CONTRACT_ADAPTER": (ADAPTER, "projected vector adapter"),
    "WRONG_CONTRACT_MATERIALIZER": (MATERIALIZER, "repository-only coherence validator"),
    "WRONG_CONTRACT_CLOUD_INIT": (CLOUD_INIT, "bootstrap command template"),
    "WRONG_CONTRACT_NOCLOUD_SEED": (SEED, "bootstrap source projection"),
    "HG_PROJECTION_OWNER": (HG_PROJECTION, "checkout/projection mechanism"),
    "P11_OWNER": (P11_OWNER, "bounded custody consumer"),
    "DU_OWNER": (DU_OWNER, "continuation manifest validator"),
    "EB_OWNER": (EB_OWNER, "candidate-bound receipt validator"),
    "EE_OWNER": (EE_OWNER, "runtime-consumer receipt validator"),
    "HR_FORMAL_SPECIFICATION": (HR_SPEC, "WRONG_CONTRACT semantics"),
    "HR_PRODUCER": (HR_PRODUCER, "WRONG_CONTRACT vector producer"),
    "HR_REDUCER": (HR_REDUCER, "WRONG_CONTRACT repository reducer"),
    "EX_CERTIFICATE": (EX_CERTIFICATE, "common certified proof substrate"),
}


class HUAuditError(ValueError):
    """Deterministic fail-closed HU audit rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise HUAuditError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision_path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", revision_path], cwd=root, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        raise HUAuditError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise HUAuditError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _committed_json(root: Path, path: Path) -> dict[str, Any]:
    value = json.loads(
        _git_bytes(root, f"{EXPECTED_HEAD}:{path.as_posix()}"),
        object_pairs_hook=_unique_object,
    )
    if not isinstance(value, dict):
        raise HUAuditError(f"COMMITTED_JSON_NOT_OBJECT__{path.name}")
    return value


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    """Authenticate the exact committed checkpoint without trusting the prompt."""

    root = repository_root.resolve()
    observed = {
        "repository": str(root),
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "log", "-1", "--format=%s"),
        "parent": _git(root, "rev-parse", "HEAD^"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
        "tracked_status": _git(root, "status", "--porcelain", "--untracked-files=no"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(root),
        "branch": EXPECTED_BRANCH,
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "subject": EXPECTED_SUBJECT,
        "parent": EXPECTED_PARENT,
        "origin": EXPECTED_ORIGIN,
        "remote_tracking_head": EXPECTED_HEAD,
        "tracked_status": "",
        "index": "",
    }
    if observed != expected:
        raise HUAuditError("EXACT_COMMITTED_HT_CHECKPOINT_MISMATCH")
    for ancestor in REQUIRED_ANCESTORS:
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, EXPECTED_HEAD],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode:
            raise HUAuditError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")

    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-list", "-n", "1", f"refs/tags/{NESTED_TAG}"),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "branch": "",
        "status": "",
        "tag_head": NESTED_HEAD,
    }:
        raise HUAuditError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def committed_identity(repository_root: Path, path: Path, role: str) -> dict[str, str]:
    root = repository_root.resolve()
    relative = path.as_posix()
    committed = _git_bytes(root, f"{EXPECTED_HEAD}:{relative}")
    current = root / path
    if current.is_symlink() or not current.is_file() or current.read_bytes() != committed:
        raise HUAuditError(f"COMMITTED_WORKTREE_IDENTITY_DRIFT__{path.name}")
    return {
        "path": relative,
        "git_blob_id": _git(root, "rev-parse", f"{EXPECTED_HEAD}:{relative}"),
        "sha256": sha256_bytes(committed),
        "role": role,
        "committed_identity_status": "VERIFIED",
    }


def committed_identity_map(repository_root: Path) -> dict[str, dict[str, str]]:
    return {
        identity: committed_identity(repository_root, path, role)
        for identity, (path, role) in IDENTITY_PATHS.items()
    }


def authenticate_ht_and_hr(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    terminal = _committed_json(root, HT_TERMINAL)
    if terminal.get("reduction_sha256") != sha256_bytes(canonical_bytes(terminal.get("reduction"))):
        raise HUAuditError("HT_TERMINAL_INNER_SEAL_INVALID")
    reduction = terminal["reduction"]
    expected = {
        "wrong_contract_route_support_status": "VERIFIED",
        "fm_context_wrong_contract_support": "VERIFIED",
        "fm_bootstrap_selector_wrong_contract_support": "VERIFIED",
        "fm_authorization_selector_wrong_contract_support": "VERIFIED",
        "gn_wrong_contract_support": "VERIFIED",
        "preauthorization_materialization_support": "VERIFIED",
        "wrong_contract_adapter_status": "VERIFIED",
        "wrong_contract_bootstrap_template_status": "VERIFIED",
        "expected_harness_binding_design_status": "VERIFIED",
        "wrong_attempt_regression_status": "VERIFIED",
        "wrong_input_regression_status": "VERIFIED",
        "unknown_vector_fail_closed_status": "VERIFIED",
        "production_route_count_status": "VERIFIED",
        "post_commit_rebind_required": "VERIFIED",
    }
    if any(reduction["readiness_reduction"].get(key) != value for key, value in expected.items()):
        raise HUAuditError("HT_TERMINAL_CLAIM_RECONSTRUCTION_FAILED")
    if reduction.get("e05") != {"after": "8/18", "before": "8/18", "credit": 0}:
        raise HUAuditError("HT_E05_RECONSTRUCTION_FAILED")
    if reduction["reuse_impact"] != reduction["reuse_impact"] | {
        "production_route_before": 1,
        "production_route_after": 1,
        "production_route_delta": 0,
        "new_generic_framework_count": 0,
        "new_authority_layer_count": 0,
        "new_production_route_count": 0,
        "new_runtime_owner_count": 0,
    }:
        raise HUAuditError("HT_ROUTE_COUNT_RECONSTRUCTION_FAILED")

    specification = _committed_json(root, HR_SPEC)
    if specification.get("specification_sha256") != sha256_bytes(
        canonical_bytes(specification.get("specification"))
    ):
        raise HUAuditError("HR_SPECIFICATION_INNER_SEAL_INVALID")
    semantics = specification["specification"]
    if (
        semantics["selected_vector"] != "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT"
        or semantics["mutation_rule"]["target_field"] != "contract_identity"
        or semantics["mutation_rule"]["semantic_mutation_count"] != 1
        or semantics["mutation_rule"]["dependent_recomputation"] != "record_identity"
        or semantics["mutation_rule"]["allowed_differing_record_fields"]
        != ["contract_identity", "record_identity"]
        or semantics["expected_denial"]["contract_specific_comparison_reached"] is not False
        or semantics["expected_denial"]["error_reason"]
        != "operational Human act input_record_identity binding is invalid"
    ):
        raise HUAuditError("HR_SEMANTIC_RECONSTRUCTION_FAILED")
    return {"ht": reduction, "hr": semantics}


def authenticate_ex_reuse(repository_root: Path) -> dict[str, Any]:
    certificate = _committed_json(repository_root.resolve(), EX_CERTIFICATE)
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    ex_canonical = json.dumps(
        preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if certificate.get("certificate_sha256") != sha256_bytes(ex_canonical):
        raise HUAuditError("EX_CERTIFICATE_INNER_SEAL_INVALID")
    counts = certificate["certificate"]["component_counts"]
    if counts.get("CERTIFIED") != 17:
        raise HUAuditError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "17/17", "ex_reconstructed": 0}


def _cloud_command_bindings(cloud_text: str) -> tuple[str, str, str, str, str]:
    commands = [
        line.strip().split()
        for line in cloud_text.splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    ]
    if len(commands) != 1 or len(commands[0]) != 7:
        raise HUAuditError("WRONG_CONTRACT_BOOTSTRAP_COMMAND_INVALID")
    return tuple(commands[0][2:])  # type: ignore[return-value]


def audit_committed_route(repository_root: Path) -> dict[str, Any]:
    """Return the exact first broken edge; never materialize past that edge."""

    root = repository_root.resolve()
    authenticate_entry(root)
    identities = committed_identity_map(root)
    authenticate_ht_and_hr(root)
    authenticate_ex_reuse(root)

    adapter_sha = identities["WRONG_CONTRACT_ADAPTER"]["sha256"]
    cloud = _git_bytes(root, f"{EXPECTED_HEAD}:{CLOUD_INIT.as_posix()}").decode()
    expected_harness, _, checkout_head, checkout_tree, _ = _cloud_command_bindings(cloud)
    if expected_harness != adapter_sha:
        raise HUAuditError("EXPECTED_HARNESS_COMMITTED_IDENTITY_MISMATCH")
    if (checkout_head, checkout_tree) != (HG_HEAD, HG_TREE):
        raise HUAuditError("UNEXPECTED_BOOTSTRAP_CHECKOUT_IDENTITY")
    stale_context = _git_bytes(root, f"{HG_HEAD}:{FM_CONTEXT.as_posix()}").decode()
    if "WRONG_CONTRACT" in stale_context:
        raise HUAuditError("HG_CONTEXT_UNEXPECTEDLY_SUPPORTS_WRONG_CONTRACT")
    adapter = _git_bytes(root, f"{EXPECTED_HEAD}:{ADAPTER.as_posix()}").decode()
    required_dependency = 'context_owner_path = root / ('
    if required_dependency not in adapter or 'if context_owner.operation_vector(context["generation_identity"]) != "WRONG_CONTRACT"' not in adapter:
        raise HUAuditError("ADAPTER_GUEST_CONTEXT_DEPENDENCY_NOT_AUTHENTICATED")
    launcher = _git_bytes(root, f"{EXPECTED_HEAD}:{FM_LAUNCHER.as_posix()}").decode()
    if f'CHECKOUT_HEAD = "{HG_HEAD}"' not in launcher or f'CHECKOUT_TREE = "{HG_TREE}"' not in launcher:
        raise HUAuditError("FM_CHECKOUT_BINDING_NOT_AUTHENTICATED")
    return {
        "expected_harness_binding_status": "VERIFIED",
        "wrong_contract_expected_harness_sha256": expected_harness,
        "committed_wrong_contract_adapter_sha256": adapter_sha,
        "host_wrong_contract_selector_status": "VERIFIED",
        "checkout_head": checkout_head,
        "checkout_tree": checkout_tree,
        "checkout_contains_committed_ht": False,
        "guest_checkout_context_wrong_contract_support": "NOT_PROVEN",
        "last_verified_edge": "HOST_PROJECTS_COMMITTED_HT_WRONG_CONTRACT_ADAPTER_AND_BINDS_ITS_EXACT_HASH_IN_COMMITTED_BOOTSTRAP",
        "first_broken_edge": "GUEST_ADAPTER_LOADS_FM_CONTEXT_OWNER_FROM_HG_PINNED_CHECKOUT_WHERE_WRONG_CONTRACT_IS_UNSUPPORTED",
        "post_commit_live_binding_status": "NOT_PROVEN",
        "preoperational_readiness_status": "NOT_PROVEN",
        "current_du_status": "NOT_PROVEN",
        "current_eb_status": "NOT_PROVEN",
        "current_ee_status": "NOT_PROVEN",
    }


def require_exact_binding(observed: Any, expected: Any, case: str) -> None:
    """Small reusable negative-matrix gate for one exact binding edge."""

    if observed != expected:
        raise HUAuditError(f"PREAUTHORIZATION_BINDING_REJECTED__{case}")


def coherent_future_chain_fixture(repository_root: Path) -> dict[str, Any]:
    """Return non-authority test semantics for the negative matrix only."""

    identities = committed_identity_map(repository_root)
    candidate = "a" * 64
    context = "b" * 64
    return {
        "fixture_classification": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "ht_head": EXPECTED_HEAD,
        "ht_tree": EXPECTED_TREE,
        "hr_spec": identities["HR_FORMAL_SPECIFICATION"]["sha256"],
        "hr_producer": identities["HR_PRODUCER"]["sha256"],
        "hr_reducer": identities["HR_REDUCER"]["sha256"],
        "fm_context_owner": identities["FM_CONTEXT_OWNER"]["sha256"],
        "fm_launcher": identities["FM_LAUNCHER"]["sha256"],
        "gn_owner": identities["GN_PRESENTATION_OWNER"]["sha256"],
        "adapter": identities["WRONG_CONTRACT_ADAPTER"]["sha256"],
        "materializer": identities["WRONG_CONTRACT_MATERIALIZER"]["sha256"],
        "cloud_init": identities["WRONG_CONTRACT_CLOUD_INIT"]["sha256"],
        "nocloud_seed": identities["WRONG_CONTRACT_NOCLOUD_SEED"]["sha256"],
        "candidate": candidate,
        "runtime": candidate,
        "context_candidate": candidate,
        "context": context,
        "checkout_head": EXPECTED_HEAD,
        "checkout_tree": EXPECTED_TREE,
        "projection": identities["WRONG_CONTRACT_ADAPTER"]["sha256"],
        "expected_harness": identities["WRONG_CONTRACT_ADAPTER"]["sha256"],
        "vector": VECTOR,
        "presentation_vector": VECTOR,
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
    }


def validate_coherent_future_chain(repository_root: Path, chain: dict[str, Any]) -> None:
    """Fail closed on any stale/incoherent preauthorization binding."""

    expected = coherent_future_chain_fixture(repository_root)
    if set(chain) != set(expected):
        raise HUAuditError("PREAUTHORIZATION_CHAIN_FIELDS_MISSING_OR_UNKNOWN")
    for field, expected_value in expected.items():
        require_exact_binding(chain[field], expected_value, field.upper())
    require_exact_binding(chain["candidate"], chain["runtime"], "CANDIDATE_RUNTIME")
    require_exact_binding(chain["candidate"], chain["context_candidate"], "CANDIDATE_CONTEXT")
    require_exact_binding(chain["adapter"], chain["projection"], "ADAPTER_PROJECTION")
    require_exact_binding(chain["adapter"], chain["expected_harness"], "EXPECTED_HARNESS")
    require_exact_binding(chain["vector"], chain["presentation_vector"], "PRESENTATION_VECTOR")


if __name__ == "__main__":
    raise SystemExit("repository-only auditor; no operational CLI entry point")
