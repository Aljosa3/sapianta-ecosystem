#!/usr/bin/env python3
"""Authenticate and assess the exact post-HG repository binding; never operate."""

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

EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
EXPECTED_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
EXPECTED_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
EXPECTED_SUBJECT = "G77-256HG correct guest projection validation"
STABLE_ANCESTRY_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1

FM_ROOT = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher"
)
FM_LAUNCHER = FM_ROOT / "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_LAUNCHER_SHA256 = "32ff60d38373c6f536e6bacfa47b3f66afb4106a18e782ef45d21490e6c3a3d7"
FM_CONTEXT_OWNER = FM_ROOT / "sapianta_fresh_operation_context_v1.py"
FM_CONTEXT_OWNER_SHA256 = "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
HG_FIXTURE = Path(
    ".github/governance/evidence/g77_256hg_guest_projection_validation_v1/"
    "static/G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py"
)
HG_TEST = Path(
    ".github/governance/evidence/g77_256hg_guest_projection_validation_v1/"
    "tests/test_g77_256hg_guest_projection_validation_v1.py"
)
HG_REPORT = Path(
    "docs/governance/G77_256HG_PROJECTION_AWARE_GUEST_VALIDATION_CORRECTION_V1.md"
)
HG_MATERIAL_SHA256 = {
    FM_LAUNCHER: FM_LAUNCHER_SHA256,
    FM_CONTEXT_OWNER: FM_CONTEXT_OWNER_SHA256,
    HG_FIXTURE: "d6e2366481ae01910b281775e5437506b6baef719a57e53a1e109e7d1ea0d141",
    HG_TEST: "e55f287708c13a5ae2da18ea30660b6b5ba62bfb1d3e7dfa7922e33a4c05ce20",
    HG_REPORT: "ce242e62ae05a1d207572c7271f5ada88381be9a58b10e4604d464b43b44e333",
}

HE_REFERENCE = Path(
    ".github/governance/evidence/g77_256he_post_hd_live_binding_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HE_REFERENCE_SHA256 = "71d49b7216af9c306cfd0e4f5da9837af4f37136e69137ef3a732b066d95096b"
GY_PRODUCER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
GY_PRODUCER_SHA256 = "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
GY_BINDER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/"
    "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
)
GY_BINDER_SHA256 = "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00"
GY_REDUCER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/"
    "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)
DU = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
EB = Path(
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EE = Path(
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
REUSED_OWNER_SHA256 = {
    HE_REFERENCE: HE_REFERENCE_SHA256,
    GY_PRODUCER: GY_PRODUCER_SHA256,
    GY_BINDER: GY_BINDER_SHA256,
    DU: "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    EB: "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    EE: "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
}


class PostHGBindingError(ValueError):
    """Deterministic fail-closed post-HG binding rejection."""


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
        raise PostHGBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, object_path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", object_path], cwd=root, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        raise PostHGBindingError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHGBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PostHGBindingError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHGBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_committed_hg(repository_root: Path) -> dict[str, Any]:
    """Authenticate exact HG identity and changed owners from committed bytes."""

    root = repository_root.resolve()
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "log", "-1", "--format=%s"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
    }
    expected = {
        "branch": EXPECTED_BRANCH,
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "subject": EXPECTED_SUBJECT,
        "remote_tracking_head": EXPECTED_HEAD,
    }
    if observed != expected:
        raise PostHGBindingError("EXACT_COMMITTED_HG_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", STABLE_ANCESTRY_ANCHOR, "HEAD"],
        cwd=root,
        check=False,
    ).returncode != 0:
        raise PostHGBindingError("STABLE_ANCESTRY_MISSING")
    for path, expected_sha256 in {**HG_MATERIAL_SHA256, **REUSED_OWNER_SHA256}.items():
        absolute = root / path
        if absolute.is_symlink() or not absolute.is_file():
            raise PostHGBindingError(f"MATERIAL_PATH_INVALID__{path.name}")
        if sha256_path(absolute) != expected_sha256:
            raise PostHGBindingError(f"MATERIAL_HASH_MISMATCH__{path.name}")
        if _git(root, "rev-parse", f"HEAD:{path.as_posix()}") != _git(
            root, "hash-object", path.as_posix()
        ):
            raise PostHGBindingError(f"MATERIAL_NOT_COMMITTED_EXACTLY__{path.name}")
    return observed | {"material_count": len(HG_MATERIAL_SHA256) + len(REUSED_OWNER_SHA256)}


def _leaf_differences(
    left: Any, right: Any, path: tuple[Any, ...] = ()
) -> dict[tuple[Any, ...], tuple[Any, Any]]:
    if type(left) is not type(right):
        return {path: (left, right)}
    if isinstance(left, dict):
        differences: dict[tuple[Any, ...], tuple[Any, Any]] = {}
        for key in set(left) | set(right):
            if key not in left or key not in right:
                differences[path + (key,)] = (left.get(key), right.get(key))
            else:
                differences.update(
                    _leaf_differences(left[key], right[key], path + (key,))
                )
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return {path: (left, right)}
        differences = {}
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            differences.update(
                _leaf_differences(left_item, right_item, path + (index,))
            )
        return differences
    return {} if left == right else {path: (left, right)}


def validate_exact_hg_rebind(
    reference: dict[str, Any], candidate: dict[str, Any]
) -> None:
    """Allow only HG HEAD/tree, committed launcher identity, and derived seal."""

    for envelope in (reference, candidate):
        if envelope.get("manifest_sha256") != sha256_bytes(
            canonical_bytes(envelope["manifest"])
        ):
            raise PostHGBindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
    expected = {
        ("manifest", "required_head"): (
            reference["manifest"]["required_head"],
            EXPECTED_HEAD,
        ),
        ("manifest", "source_tree"): (
            reference["manifest"]["source_tree"],
            EXPECTED_TREE,
        ),
        ("manifest", "extension_bindings", 5, "sha256"): (
            reference["manifest"]["extension_bindings"][5]["sha256"],
            FM_LAUNCHER_SHA256,
        ),
        ("manifest_sha256",): (
            reference["manifest_sha256"],
            candidate["manifest_sha256"],
        ),
    }
    if _leaf_differences(reference, candidate) != expected:
        raise PostHGBindingError("CANDIDATE_CHANGED_OUTSIDE_EXACT_HG_REBIND")
    if candidate["manifest"].get("selected_case") != {
        "case_class": CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise PostHGBindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")


def build_hg_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_committed_hg(root)
    producer = _load_module(root / GY_PRODUCER, "g77_256hh_gy_producer")
    candidate = producer.build_candidate(root)
    validate_exact_hg_rebind(load_canonical(root / HE_REFERENCE), candidate)
    return candidate


def _harness_bytes() -> bytes:
    return (
        "from pathlib import Path\n\n"
        'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
        'RAW_ROOT = Path("/mnt/g77-evidence")\n'
        'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"\n'
    ).encode("utf-8")


def instantiate_hg_repository_evidence(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Reissue current DU/EB/EE evidence, then stop at the stale checkout edge."""

    root = repository_root.resolve()
    output = output_root.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise PostHGBindingError("OUTPUT_OUTSIDE_REPOSITORY") from exc
    if output.exists() or output.is_symlink():
        raise PostHGBindingError("OUTPUT_COLLISION")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise PostHGBindingError("OUTPUT_PARENT_INVALID")

    candidate_value = build_hg_candidate(root)
    candidate_bytes = canonical_bytes(candidate_value)
    candidate = output / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    runtime = output / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    bindings = output / "bindings"
    harness = bindings / "G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_receipt = bindings / "G77_256GY_EB_RECEIPT_V1.json"
    ee_receipt = bindings / "G77_256GY_EE_RECEIPT_V1.json"
    for parent in (candidate.parent, runtime.parent, bindings):
        parent.mkdir(parents=True, exist_ok=False)
    candidate.write_bytes(candidate_bytes)
    runtime.write_bytes(candidate_bytes)
    harness.write_bytes(_harness_bytes())

    du = _load_module(root / DU, "g77_256hh_du")
    eb = _load_module(root / EB, "g77_256hh_eb")
    ee = _load_module(root / EE, "g77_256hh_ee")
    du_result = du.validate_file(candidate, root, expected_head=EXPECTED_HEAD)
    eb_value = eb.validate_candidate(
        root, candidate, required_head=EXPECTED_HEAD, required_tree=EXPECTED_TREE
    )
    eb_receipt.write_bytes(eb.canonical_bytes(eb_value))
    eb_result = eb.verify_receipt_file(root, eb_receipt)
    ee_value = ee.validate_binding(
        root,
        candidate,
        eb_receipt,
        harness,
        runtime.parent,
        "/mnt/g77-evidence",
        required_head=EXPECTED_HEAD,
        required_tree=EXPECTED_TREE,
    )
    ee_receipt.write_bytes(ee.canonical_bytes(ee_value))
    ee_result = ee.verify_receipt_file(root, ee_receipt)
    if set(du_result.values()) != {"PASS"}:
        raise PostHGBindingError("CURRENT_HG_DU_NOT_PASS")
    if eb_result.get("overall_result") != "PASS":
        raise PostHGBindingError("CURRENT_HG_EB_NOT_PASS")
    if ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise PostHGBindingError("CURRENT_HG_EE_NOT_PASS")

    launcher = _load_module(root / FM_LAUNCHER, "g77_256hh_fm_launcher")
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=EXPECTED_HEAD,
        repository_tree=EXPECTED_TREE,
        generation_identity=(
            "G77_256HH_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HH_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HH",
        operation_evidence_root=Path("/tmp/g77_256hh/operation_state"),
        transient_root=Path("/tmp/g77_256hh/transient"),
        candidate_source_path=candidate.relative_to(root),
    )
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate.relative_to(root)
    )
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))

    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    checkout_owner = _git_bytes(
        root, f"{checkout['head']}:{FM_CONTEXT_OWNER.as_posix()}"
    )
    checkout_owner_sha256 = sha256_bytes(checkout_owner)
    if checkout["tree"] != _git(root, "rev-parse", f"{checkout['head']}^{{tree}}"):
        raise PostHGBindingError("CHECKOUT_HEAD_TREE_INTERNAL_MISMATCH")
    stale_checkout = (
        checkout["head"] != EXPECTED_HEAD
        or checkout["tree"] != EXPECTED_TREE
        or checkout_owner_sha256 != FM_CONTEXT_OWNER_SHA256
    )
    if not stale_checkout:
        raise PostHGBindingError("EXPECTED_HG_STALE_CHECKOUT_EDGE_NOT_REPRODUCED")

    result = {
        "schema_id": "G77_256HH_POST_HG_REPOSITORY_EVIDENCE_RESULT_V1",
        "artifact_class": "REPOSITORY_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "repository_head": EXPECTED_HEAD,
        "repository_tree": EXPECTED_TREE,
        "candidate_sha256": sha256_path(candidate),
        "candidate_inner_sha256": candidate_value["manifest_sha256"],
        "candidate_runtime_byte_identity": candidate.read_bytes() == runtime.read_bytes(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "fm_launcher_sha256": FM_LAUNCHER_SHA256,
        "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
        "checkout_head": checkout["head"],
        "checkout_tree": checkout["tree"],
        "checkout_owner_sha256": checkout_owner_sha256,
        "exact_permitted_candidate_rebindings": [
            "HG_HEAD",
            "HG_TREE",
            "FM_COMMITTED_LAUNCHER_SHA256",
            "DERIVED_MANIFEST_SHA256",
        ],
        "candidate_semantics_changed": False,
        "du_status": "PASS",
        "eb_status": "PASS",
        "ee_status": "PASS",
        "fm_context_owner_binding_status": "NOT_PROVEN__STALE_CHECKOUT_OWNER_BYTES",
        "post_commit_live_binding_status": "NOT_PROVEN",
        "preoperational_readiness_status": "NOT_PROVEN",
        "next_operational_generation_eligible": "NOT_PROVEN",
        "last_verified_edge": "CURRENT_HG_CANDIDATE_DU_EB_EE_AND_CONTEXT_SEAL",
        "first_broken_edge": "FM_CHECKOUT_HEAD_TREE_REMAINS_PRE_HG_AND_PROJECTS_OLD_CONTEXT_OWNER",
        "minimum_missing_capability": "CURRENT_HG_CHECKOUT_BINDING_WITHOUT_LAUNCHER_HASH_SELF_REFERENCE",
        "human_operational_authority_count": 0,
        "authority_consumption_count": 0,
        "pre_count": 0,
        "fm_operational_launcher_invocation_count": 0,
        "qemu_count": 0,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_and_continue_count": 0,
        "operational_replay_count": 0,
        "e05_credit": 0,
    }
    return result


def write_terminal_reduction(
    *, repository_root: Path, live_root: Path, output_path: Path
) -> dict[str, Any]:
    result = instantiate_hg_repository_evidence(
        repository_root=repository_root, output_root=live_root
    )
    reduction = {
        "schema_id": "G77_256HH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HH",
        "terminal_branch": "BRANCH_B__READINESS_NOT_PROVEN",
        "result": result,
        "stale_binding_set": [
            "PRE_HG_FM_CHECKOUT_HEAD_TREE",
            "PRE_HG_CHECKOUT_CONTEXT_OWNER_BYTES",
            "PRE_HG_FULL_PREOPERATIONAL_READINESS",
        ],
        "required_rebind_set": [
            "CURRENT_HG_FM_CHECKOUT_HEAD_TREE",
            "CURRENT_HG_CHECKOUT_CONTEXT_OWNER_BYTES",
        ],
        "unchanged_binding_set": [
            "GY_WRONG_INPUT_SEMANTICS",
            "HA_GUEST_ADAPTER",
            "DU_EB_EE_VALIDATORS",
            "P11_CHE_FK",
            "HF_TERMINAL_HISTORY",
            "EX_COMMON_SUBSTRATE",
        ],
        "reused_binder_set": [
            "GY_PRODUCER",
            "DU_VALIDATOR",
            "EB_VALIDATOR",
            "EE_VALIDATOR",
            "FM_CONTEXT_BUILDER",
        ],
        "capability_boundary": {
            "candidate_capability": "VERIFIED",
            "projection_aware_validation_candidate_capability": "VERIFIED",
            "projection_aware_validation_repository_capability": "VERIFIED",
            "projection_aware_validation_operational_capability": "NOT_PROVEN",
            "wrong_input_candidate_capability": "VERIFIED",
            "wrong_input_repository_capability": "VERIFIED",
            "wrong_input_operational_capability": "NOT_PROVEN",
        },
        "e05": {"before": "7/18", "after": "7/18", "credit": 0},
        "auto_continuable": False,
        "human_review_required": True,
        "minimum_legal_next_development_delta": (
            "ONE_BOUNDED_REPOSITORY_ONLY_CHECKOUT_BINDING_CORRECTION_THAT_"
            "RESOLVES_THE_LAUNCHER_HASH_SELF_REFERENCE__NO_OPERATION"
        ),
    }
    envelope = {
        "schema_id": "G77_256HH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise PostHGBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only evidence owner; no operational CLI entry point")
