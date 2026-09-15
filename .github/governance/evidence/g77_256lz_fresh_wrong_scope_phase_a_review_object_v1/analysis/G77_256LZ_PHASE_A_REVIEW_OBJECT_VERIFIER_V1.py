#!/usr/bin/env python3
"""Materialize once, then verify, the authority-free G77-256LZ Phase A.

The materialization path reuses the authenticated FM/GL/LG/LP mechanisms.
It never creates or consumes authority and never invokes FM operationally,
QEMU, a VM, P11, or a protected effect.  The default invocation is read-only
verification.
"""

from __future__ import annotations

import argparse
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
ENTRY_HEAD = "0158178c45d66a81f675ba431fb8ae261c4b3bd9"
ENTRY_TREE = "0ac5500055df6ba75dce76a2107604dae1be8608"
ENTRY_SUBJECT = "G77-256LY enforce LT parent preauthority readiness"
LT_HEAD = "f22fae2529de35eaf8093776c04a6a8e05a097f6"
LR_HEAD = "b738b0795b9d50b60819bbbf31e49fab6b47ed5d"
LV_HEAD = "e86ada76834b7af95b86dce57dda0927a96e4eb7"
LW_HEAD = "cbe60ce7aa5d586f70fe211a9807873c8bb9d63e"
LX_HEAD = "913e4deb93f1d9366b3e7fd218b9ac89469b0bbc"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
RUNTIME_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
RUNTIME_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"

AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
LIFECYCLE_ID = "G77_256LZ_WRONG_SCOPE_PHASE_A_LIFECYCLE_001"
OBJECT_ID = "G77_256LZ_WRONG_SCOPE_PHASE_A_OBJECT_001"
REVIEW_ID = "G77_256LZ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
CONTEXT_ID = "G77_256LZ_WRONG_SCOPE_CANONICAL_CONTEXT_001"
PRESENTATION_ID = "G77_256LZ_WRONG_SCOPE_HUMAN_REVIEW_PRESENTATION_001"
GENERATION_ID = "G77_256LZ_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION_ID = "G77_256LZ_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
ATTEMPT_ID = "G77_256LZ_E05_FUTURE_AUTHORIZED_ATTEMPT_001"
PREFIX = "G77_256LZ"
TERMINAL = (
    "A__G77_256LZ_WRONG_SCOPE_FRESH_PHASE_A_REVIEW_OBJECT_SEALED__"
    "LY_READINESS_DEPENDENCY_BOUND__CURRENT_ADMISSION_BOUND__"
    "ZERO_AUTHORITY__ZERO_OPERATION__"
    "READY_FOR_HUMAN_DECISION"
)

LZ_REL = Path(
    ".github/governance/evidence/"
    "g77_256lz_fresh_wrong_scope_phase_a_review_object_v1"
)
LZ = ROOT / LZ_REL
FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GL_REL = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
LG_REL = Path(
    ".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/"
    "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
CANDIDATE_REL = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
LP_REL = Path(
    ".github/governance/evidence/g77_256lp_committed_review_transition_v1/"
    "G77_256LP_SPCE_TERMINAL_REDUCTION_V1.json"
)
LQ_REVIEW_REL = Path(
    ".github/governance/evidence/g77_256lq_wrong_scope_fresh_phase_a_review_object_v1/"
    "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
)
LR_REL = Path(
    ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1/"
    "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json"
)
LV_REVIEW_REL = Path(
    ".github/governance/evidence/g77_256lv_fresh_wrong_scope_phase_a_review_object_v1/"
    "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
)
LW_REDUCTION_REL = Path(
    ".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1/"
    "G77_256LW_OPERATIONAL_EVIDENCE_REDUCTION_V1.json"
)
LW_DECISION_REL = Path(
    ".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1/"
    "G77_256LW_TERMINAL_DECISION_V1.json"
)
LX_DECISION_REL = Path(
    ".github/governance/evidence/g77_256lx_lt_state_parent_blocker_classification_v1/"
    "G77_256LX_TERMINAL_DECISION_V1.json"
)
LY_IMPLEMENTATION_REL = Path(
    ".github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/"
    "orchestration/G77_256LY_LT_PARENT_PREAUTHORITY_READINESS_V1.py"
)
LY_DECISION_REL = Path(
    ".github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/"
    "G77_256LY_TERMINAL_DECISION_V1.json"
)
LT_REL = Path(
    ".github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/"
    "G77_256LT_TERMINAL_DECISION_V1.json"
)
LU_DECISION_REL = Path(
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_TERMINAL_DECISION_V1.json"
)
LU_RELATION_REL = Path(
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_V1.json"
)
EX_REL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
P11_REL = Path("tests/p11_da_operational_consumer_v1.py")
SOURCE_HASHES = {
    FM_REL: "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8",
    GL_REL: "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    LG_REL: "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f",
    LP_REL: "fee1e1bdf2bf8de547135b05be09cf8b987ba2786a34642524a291a74470918b",
    LQ_REVIEW_REL: "035e406848463173bd68b6cf1ec810cdfa7ab846ce02b26cf376c7d81a77eecb",
    LR_REL: "429123ec1ddef737060de182e712cb1a6091318a69345ca720764f91977b126b",
    LV_REVIEW_REL: "333c95c19351f237e5e8bd000894e6bbabadc7c5851b33e624d2c256378c4f5e",
    LW_REDUCTION_REL: "f3a396fdc127b57bc7b955efd2d9eb46058140931a4563e4f269194bd250de00",
    LW_DECISION_REL: "2370f169667e6d0ae34058c7fd7cf6dea16a343e67ecf1a2b14c65c3ce8de8bb",
    LX_DECISION_REL: "6a708ab6af89ea38e4cea14bc0439907234df2ab30653e58cad56e74a50cb86d",
    LY_IMPLEMENTATION_REL: "920e84f5be5fcb17f29dc7850c3f0862609ea847bde7fd72483c2d4e18f5e49d",
    LY_DECISION_REL: "fbf54d57a506adcf81ea830007300a87ad87d5bf78f987864e985ecce4567c47",
    LT_REL: "f0a6acfc31c72b1b1e890cf2e3c587b4f5ccf179ecf2da9c6e2ad724a27aae9f",
    LU_DECISION_REL: "77cf5cd0c71875bca1d57f17a06605c79101dab9217f3f1782be7a1767141cf7",
    LU_RELATION_REL: "b17bcf19cc11142b0a4a603138c0311dcce0cfb34510c76dff156fbfcce9e80c",
    EX_REL: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    P11_REL: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}

CONTEXT = LZ / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
READINESS = LZ / "G77_256LZ_PREAUTHORITY_STATIC_READINESS_V1.json"
REVIEW = LZ / "G77_256LZ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
PRESENTATION = LZ / "G77_256LZ_HUMAN_DECISION_PRESENTATION_V1.txt"
REDUCTION = LZ / "G77_256LZ_SPCE_TERMINAL_REDUCTION_V1.json"
DECISION = LZ / "G77_256LZ_TERMINAL_DECISION_V1.json"
REPORT = LZ / "G77_256LZ_G48_IMPLEMENTATION_REPORT_V1.md"
TRANSIENT = Path("/tmp/g77_256lz_fresh_wrong_scope_phase_a_review_object_v1")


class LZVerificationError(RuntimeError):
    """One deterministic fail-closed LZ verification failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise LZVerificationError(f"MODULE_LOAD_FAILED:{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(ROOT / FM_REL, "g77_256lz_existing_fm_owner")
GL = load_module(ROOT / GL_REL, "g77_256lz_existing_gl_owner")
LG = load_module(ROOT / LG_REL, "g77_256lz_existing_wrong_scope_semantics")


def load_canonical(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LZVerificationError(f"DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LZVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        field: value,
        f"{field}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_fresh(path: Path, value: dict[str, Any] | str) -> None:
    if path.exists() or path.is_symlink():
        raise LZVerificationError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_bytes(canonical_bytes(value))


def zero_counters() -> dict[str, int]:
    return {
        "HUMAN_AUTHORITY_SOURCE_COUNT": 0,
        "AUTHORITY_CREATION_COUNT": 0,
        "AUTHORITY_CONSUMPTION_COUNT": 0,
        "OPERATION_ATTEMPT_COUNT": 0,
        "LT_RESERVATION_COUNT": 0,
        "LT_CHILD_COUNT": 0,
        "FM_OPERATION_COUNT": 0,
        "QEMU_START_COUNT": 0,
        "VM_START_COUNT": 0,
        "P11_ENTRY_COUNT": 0,
        "PROTECTED_INVOCATION_COUNT": 0,
        "PROTECTED_EFFECT_COUNT": 0,
        "RETRY_COUNT": 0,
        "OPERATIONAL_REPLAY_COUNT": 0,
        "REPAIR_RETRY_COUNT": 0,
    }


def ly_readiness_dependency() -> dict[str, Any]:
    """Return the exact authenticated LY contract required by a future lifecycle."""

    envelope = json.loads((ROOT / LY_DECISION_REL).read_text(encoding="utf-8"))
    return {
        "required_for_future_execution": True,
        "authenticated_head": ENTRY_HEAD,
        "authenticated_tree": ENTRY_TREE,
        "implementation_path": LY_IMPLEMENTATION_REL.as_posix(),
        "implementation_sha256": sha256_path(ROOT / LY_IMPLEMENTATION_REL),
        "terminal_path": LY_DECISION_REL.as_posix(),
        "terminal_whole_file_sha256": sha256_path(ROOT / LY_DECISION_REL),
        "terminal_decision_sha256": envelope["decision_sha256"],
        "identity_continuity_proof": envelope["decision"]["IDENTITY_CONTINUITY_PROOF"],
        "authority_waste_prevention_static_proof": envelope["decision"][
            "AUTHORITY_WASTE_PREVENTION_STATIC_PROOF"
        ],
        "future_execution_order": [
            "DERIVE_EXACT_LT_LIFECYCLE_LEAF",
            "DERIVE_EXACT_IMMEDIATE_PARENT",
            "AUTHENTICATE_PERMITTED_GENERATION_LOCAL_ROOT",
            "MATERIALIZE_AND_VALIDATE_PARENT",
            "PROVE_LEAF_ABSENT",
            "SEAL_READINESS_OBSERVATION",
            "ONLY_THEN_FUTURE_AUTHORITY_CREATION_MAY_BECOME_ELIGIBLE",
            "FINAL_ADMISSION_REVALIDATION",
            "IMMEDIATELY_BEFORE_CONSUMPTION_READ_ONLY_LY_REOBSERVATION_OF_SAME_PARENT_AND_ABSENT_LEAF",
            "FAIL_CLOSED_ON_IDENTITY_OR_READINESS_DRIFT",
            "ONLY_THEN_AUTHORITY_CONSUMPTION",
            "LT_ATOMIC_EXCLUSIVE_LIFECYCLE_LEAF_RESERVATION",
            "AT_MOST_ONE_EXACT_FM_CHILD",
        ],
        "future_controller_integration_state": "SEPARATE_FUTURE_COMPOSITION_REQUIRED_AFTER_HUMAN_APPROVAL",
        "lz_execution_state": "DEPENDENCY_BOUND_ONLY__NOT_EXECUTED_OPERATIONALLY",
        "static_proof_is_operational_proof": False,
        "authority_or_permission_transferred": False,
        "acceptance_credit_transferred": False,
    }


def validate_replay_safe_receipt_claim(
    context: dict[str, Any], claim: dict[str, Any]
) -> dict[str, Any]:
    """Authenticate the sealed GL claim and replay its semantic state.

    GL's original observation also seals ctime/inode device metadata.  Those
    values authenticate materialization-time freshness but are not a Git
    replay identity.  LZ therefore preserves that exact sealed observation
    while reusing the same GL/FM owner to compare every semantic state field.
    """

    owner = GL._load_existing_owner(ROOT)
    if set(claim) != {"schema_id", "observation", "observation_sha256"}:
        raise LZVerificationError("RECEIPT_CLAIM_ENVELOPE_INVALID")
    observation = claim.get("observation")
    if (
        claim.get("schema_id") != GL.CLAIM_SCHEMA
        or not isinstance(observation, dict)
        or claim.get("observation_sha256") != GL._sealed_hash(owner, observation)
    ):
        raise LZVerificationError("RECEIPT_CLAIM_SEAL_INVALID")
    current = GL._observed_state(
        owner,
        context,
        owner.validate_receipt_parent_ready(ROOT, context),
    )
    replay_fields = set(observation) - {"directory_identity"}
    if (
        replay_fields != set(current) - {"directory_identity"}
        or any(current[field] != observation[field] for field in replay_fields)
        or observation.get("authority_count") != 0
        or observation.get("operational_execution_count") != 0
        or observation.get("receipt_namespace_unused") is not True
    ):
        raise LZVerificationError("RECEIPT_PARENT_SEMANTIC_STATE_CHANGED")
    return current


def authenticate_repository() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(LT_HEAD, ENTRY_HEAD)
        or not is_ancestor(LR_HEAD, ENTRY_HEAD)
        or not is_ancestor(LV_HEAD, ENTRY_HEAD)
        or not is_ancestor(LW_HEAD, ENTRY_HEAD)
        or not is_ancestor(LX_HEAD, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LZVerificationError("LY_ENTRY_OR_ANCESTRY_AUTHENTICATION_FAILED")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty if not line[3:].startswith(LZ_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LZVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    changed = set(filter(None, git("diff", "--name-only", ENTRY_HEAD, "HEAD").splitlines()))
    if any(not path.startswith(LZ_REL.as_posix() + "/") for path in changed):
        raise LZVerificationError("PRODUCTION_OR_UNRELATED_MUTATION")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
    ):
        raise LZVerificationError("NESTED_AUTHORITY_MISMATCH")
    return {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "current_head": head,
        "current_tree": git("rev-parse", "HEAD^{tree}"),
        "remote_head": remote,
    }


def authenticate_sources_and_predecessors() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LZVerificationError(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != path.read_bytes():
            raise LZVerificationError(f"SOURCE_NOT_LY_COMMITTED:{relative}")

    lr = load_canonical(ROOT / LR_REL)["reconstruction"]
    if (
        lr["cardinality"] != {
            "authority_consumed_count": 1,
            "authority_created_count": 1,
            "constitutional_cardinality_conflict": False,
            "human_decision_count": 1,
            "operation_attempt_count": 1,
            "retry_count": 0,
        }
        or lr["authority"]["reusable"] is not False
        or lr["operation"]["result"]
        != "INCOMPLETE__NO_POST_RECEIPT_NO_CONTROLLER_RESULT_NO_GUEST_TERMINAL"
        or lr["operation"]["denial_class"] != "UNKNOWN"
        or lr["human_decision"]["object_id"]
        != "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
    ):
        raise LZVerificationError("LR_TERMINAL_NONREUSE_FACTS_INVALID")

    lw = json.loads((ROOT / LW_DECISION_REL).read_text(encoding="utf-8"))["decision"]
    lw_reduction = load_canonical(ROOT / LW_REDUCTION_REL)["reduction"]
    if (
        lw["AUTHORITY_CREATED_COUNT"] != 1
        or lw["AUTHORITY_CONSUMED_COUNT"] != 1
        or lw["AUTHORITY_REUSABLE"] != "NO"
        or lw["OPERATIONAL_RETRY_AUTHORIZED"] != "NO"
        or lw["LT_RESERVATION_COUNT"] != 0
        or lw["LT_CHILD_LAUNCH_COUNT"] != 0
        or lw["FM_OPERATION_ATTEMPT_COUNT"] != 0
        or lw["QEMU_START_COUNT"] != 0
        or lw["VM_START_COUNT"] != 0
        or any(
            lw[field] != "UNKNOWN"
            for field in (
                "DENIAL_CLASS",
                "P11_ENTRY_COUNT",
                "PROTECTED_INVOCATION_COUNT",
                "PROTECTED_EFFECT_COUNT",
            )
        )
        or lw["operational_reduction_sha256"] != sha256_path(ROOT / LW_REDUCTION_REL)
        or any(
            lw_reduction[field] != "UNKNOWN"
            for field in (
                "DENIAL_CLASS",
                "P11_ENTRY_COUNT",
                "PROTECTED_INVOCATION_COUNT",
                "PROTECTED_EFFECT_COUNT",
            )
        )
    ):
        raise LZVerificationError("LW_SPENT_AUTHORITY_OR_UNKNOWN_FACTS_INVALID")

    # LT/LU terminal evidence predates the compact canonical-envelope pattern.
    # Exact file hashes and LU commit-byte equality above authenticate the source;
    # JSON parsing here reads its deliberately human-oriented presentation form.
    lt = json.loads((ROOT / LT_REL).read_text(encoding="utf-8"))["decision"]
    lu = json.loads((ROOT / LU_DECISION_REL).read_text(encoding="utf-8"))["decision"]
    relation = json.loads((ROOT / LU_RELATION_REL).read_text(encoding="utf-8"))["relation"]
    if (
        lt["CAPABILITY_IMPLEMENTED"] != "YES__GENERATION_LOCAL_HARNESS_ONLY"
        or lt["AUTHORITY_EFFECT"] != "NONE"
        or lt["CONSUMABILITY"] != "NONAUTHORITY"
        or not lt["DUPLICATE_LAUNCH_PREVENTION"].startswith("PROVEN__")
        or not lt["SESSION_INDEPENDENCE_PROVEN"].startswith("YES__")
        or not lt["UNKNOWN_FAIL_CLOSED_PROVEN"].startswith("YES__")
        or lu["INTEGRATION_READINESS"] != "PROVEN"
        or lu["NEW_CAPABILITY_REQUIRED"] != "NO"
        or lu["PRODUCTION_BEHAVIOR_IMPACT"] != "NONE"
        or lu["MINIMUM_LEGAL_NEXT_DELTA"] != "FRESH_PHASE_A_WRONG_SCOPE_REVIEW_OBJECT"
        or relation["new_capability_required"] != "NO"
        or relation["production_route_count"] != "1 -> 1"
    ):
        raise LZVerificationError("LT_LU_READINESS_FACTS_INVALID")

    lx = json.loads((ROOT / LX_DECISION_REL).read_text(encoding="utf-8"))["decision"]
    ly_envelope = json.loads((ROOT / LY_DECISION_REL).read_text(encoding="utf-8"))
    ly = ly_envelope["decision"]
    if (
        lx["FAILURE_CLASS"] != "DUPLICATE_OR_EQUIVALENT_EDGE"
        or lx["NEW_CAPABILITY_REQUIRED"] != "NO"
        or ly_envelope["decision_sha256"]
        != hashlib.sha256(canonical_bytes(ly)).hexdigest()
        or ly["FAILURE_CLASS"] != "DUPLICATE_OR_EQUIVALENT_EDGE"
        or ly["PRODUCTION_BEHAVIOR_IMPACT"] != "NONE"
        or ly["NEW_CAPABILITY_REQUIRED"] != "NO"
        or ly["MINIMUM_MISSING_CAPABILITY"] != "NONE"
        or ly["MINIMUM_MISSING_PROOF"]
        != "NONE_FOR_GENERATION_LOCAL_LT_PARENT_PREAUTHORITY_READINESS_COMPOSITION"
        or not ly["IDENTITY_CONTINUITY_PROOF"].startswith("PROVEN__")
        or not ly["AUTHORITY_WASTE_PREVENTION_STATIC_PROOF"].startswith("PROVEN__")
        or ly["E05_AFTER"] != "12/18"
        or ly["WRONG_SCOPE_STATUS"] != "UNSAT"
        or ly_envelope["evidence"]["ly_counters"]
        != {
            "authority_created": 0,
            "authority_consumed": 0,
            "operation_attempts": 0,
            "lt_operational_reservations": 0,
            "lt_child_launches": 0,
            "fm_operation_attempts": 0,
            "qemu_starts": 0,
            "vm_starts": 0,
            "retries": 0,
        }
    ):
        raise LZVerificationError("LX_LY_TERMINAL_OR_READINESS_CONTRACT_INVALID")

    lv_review = load_canonical(ROOT / LV_REVIEW_REL)["review_object"]
    if (
        lv_review["REVIEW_OBJECT_ID"]
        != "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
        or lv_review["AUTHORIZED_SCOPE"] != AUTHORIZED_SCOPE
        or lv_review["PRESENTED_SCOPE"] != PRESENTED_SCOPE
    ):
        raise LZVerificationError("LV_STRUCTURAL_PRECEDENT_INVALID")
    for identity in (LIFECYCLE_ID, OBJECT_ID, REVIEW_ID, CONTEXT_ID, PRESENTATION_ID):
        found = subprocess.run(
            ["git", "grep", "-F", identity, ENTRY_HEAD],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        if found:
            raise LZVerificationError(f"FRESH_IDENTITY_COLLISION:{identity}")


def build_review(context: dict[str, Any], readiness_sha256: str) -> dict[str, Any]:
    return {
        "GENERATION": "G77-256LZ",
        "GENERATION_ID": GENERATION_ID,
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "OBJECT_ID": OBJECT_ID,
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CONTEXT_ID": CONTEXT_ID,
        "PRESENTATION_ID": PRESENTATION_ID,
        "VECTOR": "WRONG_SCOPE",
        "PHASE": "A",
        "SEALED_PHASE": "PHASE_A__PREHUMAN__NONOPERATIONAL",
        "ARTIFACT_CLASS": "HUMAN_REVIEW_OBJECT__NONAUTHORITY__NONCONSUMABLE__NONOPERATIONAL",
        "CANONICAL_OPERATION_ID": OPERATION_ID,
        "FUTURE_OPERATIONAL_CONTEXT_TEMPLATE_STATE": "NAME_COMPATIBILITY_ONLY__NOT_AUTHORIZED__NOT_EXECUTABLE_FROM_PHASE_A",
        "ATTEMPT_BINDING": {
            "attempt_identity": ATTEMPT_ID,
            "operation_attempt_limit_if_later_authorized": 1,
        },
        "CANONICAL_CONTEXT_BINDING": {
            "context_id": CONTEXT_ID,
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": ENTRY_HEAD,
            "repository_tree": ENTRY_TREE,
            "preauthority_static_readiness_file_sha256": readiness_sha256,
        },
        "LP_TRANSITION_BINDING": {
            "schema_id": FM.COMMITTED_REVIEW_TRANSITION_SCHEMA,
            "review_identity_R": "DERIVE_FROM_UNIQUE_COMMIT_INTRODUCING_CANONICAL_CONTEXT",
            "current_admission_identity_C": "MUST_EQUAL_FUTURE_OBSERVED_HEAD_TREE",
            "transition_relation_T": "MUST_EQUAL_FM_DETERMINISTIC_EXACT_PAIR_AND_FULL_DELTA",
            "ancestry_sufficient": False,
            "branch_name_sufficient": False,
            "coherent_copy_sufficient": False,
            "transition_is_authority": False,
            "transition_consumable": False,
            "fresh_human_decision_required": True,
        },
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_MISMATCH": {
            "field": "authority_scope",
            "expected": AUTHORIZED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "independent_semantic_mutation_count": 1,
            "preserved_dimensions": [
                "authority_kind",
                "authority_lifecycle_state",
                "attempt_identity",
                "input_identity",
                "contract_identity",
                "provenance_identity",
                "validity_interval_and_currentness",
                "target_owner_and_revision",
                "caller_identity",
            ],
        },
        "CANDIDATE_HUMAN_ACT_MATERIAL": {
            "artifact_class": "HUMAN_REVIEW_MATERIAL__NONAUTHORITY",
            "is_authority": False,
            "human_actor_identity_state": "ABSENT",
            "human_authority_source_bytes_state": "ABSENT",
            "authority_act_identity_state": "UNMATERIALIZED",
            "payload_digest_state": "UNMATERIALIZED",
            "proposed_authority_scope": AUTHORIZED_SCOPE,
            "intentionally_different_future_runtime_presented_scope": PRESENTED_SCOPE,
            "human_authorizes_presented_scope": False,
            "proposed_operation_attempt_limit": 1,
            "proposed_retry_limit": 0,
        },
        "PREDECESSOR_READINESS": {
            "LT_CAPABILITY": "IMPLEMENTED__READINESS_ONLY__NONAUTHORITY",
            "LU_INTEGRATION": "PROVEN__STATIC_ONLY__NONOPERATIONAL",
            "LY_PARENT_PREAUTHORITY_READINESS": "PROVEN__STATIC_ONLY__REQUIRED_FUTURE_DEPENDENCY",
            "authority_or_permission_transferred": False,
            "acceptance_credit_transferred": False,
        },
        "LY_PREAUTHORITY_READINESS_DEPENDENCY": ly_readiness_dependency(),
        "PREVIOUS_LIFECYCLE": {
            "LQ_OBJECT_ID": "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001",
            "LQ_APPROVAL_REUSED": False,
            "LR_AUTHORITY_ID": "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001",
            "LR_AUTHORITY_REUSED": False,
            "LR_INVOCATION_REUSED": False,
            "LR_RECEIPT_NAMESPACE_REUSED": False,
            "LR_OPERATION_IDENTITY_REUSED": False,
            "LR_OUTCOME": "UNKNOWN__PRESERVED_WITHOUT_ZERO_ENCODING",
            "LV_OBJECT_ID": "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001",
            "LV_APPROVAL_REUSED": False,
            "LW_AUTHORITY_ID": "G77_256LW_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001",
            "LW_AUTHORITY_REUSED": False,
            "LW_DENIAL_CLASS": "UNKNOWN",
            "LW_P11_ENTRY_COUNT": "UNKNOWN",
            "LW_PROTECTED_INVOCATION_COUNT": "UNKNOWN",
            "LW_PROTECTED_EFFECT_COUNT": "UNKNOWN",
            "state": "HISTORICAL_ONLY__TERMINAL__NONTRANSFERABLE",
        },
        "GOVERNED_RUNTIME_CHECKOUT": {
            "head": RUNTIME_HEAD,
            "tree": RUNTIME_TREE,
            "separate_from_review_and_admission_identity": True,
        },
        "RECEIPT_PARENT_BINDING": {
            "path": context["receipt_parent"],
            "readiness": "PASS__EXISTING_FM_GL_OWNER",
            "receipt_namespace_unused": True,
            "lr_namespace_reused": False,
        },
        "ONE_SHOT_LIMIT": 1,
        "RETRY_LIMIT": 0,
        "AUTHORITY_STATE": "NONE",
        "AUTHORITY_CREATED": "NO",
        "AUTHORITY_CONSUMED": "NO",
        "HUMAN_DECISION_STATE": "PENDING",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LZ",
        "STATE_COUNTERS": zero_counters(),
        "NOTICES": [
            "THIS OBJECT IS NOT AUTHORIZED",
            "APPROVAL HAS NOT YET BEEN GIVEN",
            "NO OPERATION MAY START FROM THIS GENERATION",
            "LQ AND LV APPROVALS ARE HISTORICAL AND MUST NOT BE REUSED",
            "LR AND LW AUTHORITIES ARE TERMINAL AND MUST NOT BE REUSED",
            "A FUTURE HUMAN DECISION MUST BIND THIS EXACT LZ OBJECT",
            "HUMAN AUTHORIZATION APPLIES ONLY TO THE AUTHORIZED SCOPE A",
            "THE DIFFERENT PRESENTED SCOPE B IS ONLY A FUTURE FAIL_CLOSED TEST INPUT",
            "LT LU AND LY ARE READINESS EVIDENCE ONLY",
            "INTELLIGENCE != AUTHORITY",
        ],
        "NEXT_ALLOWED_TRANSITION": "INDEPENDENT_HUMAN_REVIEW_AND_DECISION",
        "READINESS": "READY_FOR_HUMAN_DECISION",
    }


def render_presentation(context: dict[str, Any], review: dict[str, Any]) -> str:
    return (
        "G77-256LZ WRONG_SCOPE PHASE-A HUMAN REVIEW PRESENTATION\n\n"
        f"PRESENTATION_ID = {PRESENTATION_ID}\n"
        f"LIFECYCLE_ID = {LIFECYCLE_ID}\n"
        f"OBJECT_ID = {OBJECT_ID}\n"
        f"REVIEW_OBJECT_ID = {REVIEW_ID}\n"
        "THIS OBJECT IS NOT AUTHORIZED.\n"
        "APPROVAL HAS NOT YET BEEN GIVEN.\n"
        "NO OPERATION MAY START FROM THIS GENERATION.\n"
        "THE CONTEXT GENERATION ID USES THE EXISTING FM VECTOR-COMPATIBILITY NAME; IT DOES NOT RECORD APPROVAL.\n"
        "LQ/LV APPROVALS AND LR/LW AUTHORITIES ARE TERMINAL AND NONREUSABLE.\n"
        "LT/LU/LY READINESS IS NOT AUTHORITY OR OPERATIONAL PROOF.\n"
        "A FUTURE CONTROLLER MUST COMPOSE THE AUTHENTICATED LY DEPENDENCY.\n"
        "HUMAN APPROVAL, IF GRANTED, AUTHORIZES ONLY SCOPE A.\n"
        "SCOPE B IS ONLY THE DELIBERATELY MISMATCHING FUTURE RUNTIME PRESENTATION.\n"
        "A FUTURE HUMAN DECISION MUST BIND THIS EXACT LZ OBJECT.\n\n"
        f"REVIEW_OBJECT_PATH = {REVIEW.relative_to(ROOT).as_posix()}\n"
        f"REVIEW_OBJECT_WHOLE_FILE_SHA256 = {sha256_path(REVIEW)}\n"
        f"REVIEW_OBJECT_CANONICAL_INNER_SHA256 = {review['review_object_sha256']}\n"
        f"CANONICAL_CONTEXT_ID = {CONTEXT_ID}\n"
        f"CANONICAL_CONTEXT_PATH = {CONTEXT.relative_to(ROOT).as_posix()}\n"
        f"CANONICAL_CONTEXT_WHOLE_FILE_SHA256 = {sha256_path(CONTEXT)}\n"
        f"CANONICAL_CONTEXT_INNER_SHA256 = {context['context_sha256']}\n"
        f"CURRENT_ADMISSION_HEAD = {ENTRY_HEAD}\n"
        f"CURRENT_ADMISSION_TREE = {ENTRY_TREE}\n"
        f"LY_READINESS_IMPLEMENTATION_SHA256 = {sha256_path(ROOT / LY_IMPLEMENTATION_REL)}\n"
        f"LY_TERMINAL_WHOLE_FILE_SHA256 = {sha256_path(ROOT / LY_DECISION_REL)}\n"
        f"LY_TERMINAL_DECISION_SHA256 = {json.loads((ROOT / LY_DECISION_REL).read_text(encoding='utf-8'))['decision_sha256']}\n"
        "LP_TRANSITION_PROOF = DERIVE_DETERMINISTIC_EXACT_R_TO_C_AFTER_COMMITTED_REVIEW_SUCCESSOR\n"
        "LP_TRANSITION_IS_AUTHORITY = NO\n"
        "LP_TRANSITION_CONSUMABLE = NO\n"
        f"AUTHORIZED_SCOPE = {AUTHORIZED_SCOPE}\n"
        f"PRESENTED_SCOPE = {PRESENTED_SCOPE}\n"
        "ISOLATED_MISMATCH = authority_scope\n"
        "AUTHORITY_STATE = NONE\n"
        "HUMAN_DECISION_STATE = PENDING\n"
        "OPERATION_STATE = NOT_STARTED\n"
        "RETRY_STATE = 0\n"
        "P11_STATE = NOT_ENTERED\n"
        "PROTECTED_EFFECT_STATE = NONE_IN_LZ\n"
        "APPROVAL_TRANSFER_TO_ANOTHER_OBJECT_SCOPE_RETRY_SUCCESSOR_OR_HISTORICAL_LIFECYCLE = PROHIBITED\n"
        "READINESS = READY_FOR_HUMAN_DECISION\n"
    )


def cross_vector() -> dict[str, str]:
    return {
        "GK": "SEMANTICALLY_EQUIVALENT__PREAUTHORITY_PARENT_READINESS_PRECEDENT",
        "GL": "SEMANTICALLY_EQUIVALENT__FM_OWNED_PREPARATION_AND_IDENTITY_OBSERVATION",
        "LG": "VECTOR_SPECIFIC__EXACT_WRONG_SCOPE_PAIR_AND_SINGLE_MISMATCH",
        "LP": "EXACT_REUSE_POSSIBLE__FM_OWNED_COMMITTED_REVIEW_R_TO_CURRENT_ADMISSION_C",
        "LQ": "PARTIAL_REUSE__PHASE_A_STRUCTURE_ONLY__NO_IDENTITY_DECISION_OR_AUTHORITY_TRANSFER",
        "LR": "NOT_APPLICABLE__HISTORICAL_TERMINAL_OPERATION_ONLY",
        "LS": "PARTIAL_REUSE__FAILURE_LOCALIZATION_ONLY",
        "LT": "EXACT_REUSE_POSSIBLE__FUTURE_LEAF_RESERVATION_AND_SUPERVISION__NO_LZ_OPERATION",
        "LU": "EXACT_REUSE_POSSIBLE__AUTHENTICATED_LT_TO_FM_SCOPE__NO_LZ_OPERATION",
        "LV": "PARTIAL_REUSE__STRUCTURAL_PHASE_A_PRECEDENT_ONLY__NO_OBJECT_OR_DECISION_TRANSFER",
        "LW": "VECTOR_SPECIFIC__SPENT_AUTHORITY_AND_OPERATIONAL_UNKNOWNS_ONLY",
        "LX": "SEMANTICALLY_EQUIVALENT__DUPLICATE_EDGE_CLASSIFICATION_REUSED",
        "LY": "EXACT_REUSE_POSSIBLE__REQUIRED_FUTURE_PARENT_READINESS_AND_REOBSERVATION_CONTRACT",
        "WRONG_ATTEMPT": "PARTIAL_REUSE__PHASE_A_CONTEXT_AND_ONE_SHOT_STRUCTURE",
        "WRONG_INPUT": "SEMANTICALLY_EQUIVALENT__EXACT_BINDING_STRUCTURE",
        "WRONG_CONTRACT": "SEMANTICALLY_EQUIVALENT__EXACT_BINDING_STRUCTURE",
        "WRONG_PROVENANCE": "PARTIAL_REUSE__EXACT_BINDING_STRUCTURE_ONLY",
        "WRONG_CALLER": "PARTIAL_REUSE__PRE_ENTRY_FAIL_CLOSED_STRUCTURE",
        "FUTURE": "PARTIAL_REUSE__PRESENTATION_AND_FRESHNESS_STRUCTURE",
        "EXPIRED": "PARTIAL_REUSE__FRESH_LIFECYCLE_STRUCTURE",
        "WRONG_SCOPE": "VECTOR_SPECIFIC__EXACT_SCOPE_PAIR_AND_ISOLATED_MISMATCH",
    }


def build_reduction(context: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LZ_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256LZ",
        "terminal": TERMINAL,
        "failure_novelty_and_convergence": {
            "FAILURE_CLASS": "DUPLICATE_OR_EQUIVALENT_EDGE",
            "NOVELTY": "FRESH_LIFECYCLE_IDENTITY_REQUIRED__NO_CAPABILITY_NOVELTY",
            "AFFECTED_INVARIANT": "FRESH_HUMAN_DECISION_MUST_PRECEDE_ANY_NEW_OPERATION_AFTER_CONSUMED_AUTHORITY",
            "PREVIOUS_CLOSEST_EDGE": "LV_REVIEW_TO_LW_SPENT_ONE_SHOT_LIFECYCLE__LY_STATIC_PARENT_READINESS_CLOSURE",
            "SEMANTIC_DIFFERENCE": "FRESH_LZ_IDENTITY_BINDS_AUTHENTICATED_LY_DEPENDENCY__NO_NEW_PRODUCTION_SEMANTIC",
            "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
            "NEW_CAPABILITY_REQUIRED": "NO",
            "NEW_PROOF_REQUIRED": "NONE_FOR_PHASE_A_SEALING__FUTURE_OPERATIONAL_WRONG_SCOPE_PROOF_REMAINS_UNSAT",
            "CONVERGENCE_SIGNAL": "LY_STATIC_BLOCKER_CLOSED_AND_EXISTING_PHASE_A_LP_MECHANISMS_SUFFICIENT",
            "REPETITION_PRESSURE": "HIGH__MULTIPLE_FRESH_PHASE_A_LIFECYCLES_WITH_ZERO_E05_MOVEMENT__FRESHNESS_STILL_MANDATORY",
            "VERIFICATION_AMPLIFICATION_RISK": "ELEVATED__REUSE_ONLY_AND_NO_SCOPE_WIDENING_REQUIRED",
        },
        "duplicate_assessment": {
            "valid_reusable_historical_object_exists": False,
            "basis": "LV_DECISION_HISTORICAL__LW_AUTHORITY_SPENT__LZ_IDENTITIES_ABSENT_AT_LY",
            "historical_lq_lv": "TERMINAL__DECISIONS_NONTRANSFERABLE",
            "historical_lr_lw": "AUTHORITIES_CONSUMED__NONREUSABLE",
        },
        "spce": {
            "state": "LY_INDEPENDENTLY_HUMAN_AUTHENTICATED__STATIC_LT_PARENT_READINESS_COMPOSITION_CLOSED__E05_12_OF_18__WRONG_SCOPE_UNSAT__NO_REUSABLE_HUMAN_AUTHORITY",
            "problem": "NEXT_OPERATIONAL_ACCEPTANCE_CANNOT_REUSE_LV_DECISION_OR_LW_SPENT_AUTHORITY__FRESH_EXACT_PHASE_A_OBJECT_REQUIRED",
            "constraints": "PHASE_A_ONLY__ZERO_AUTHORITY_OPERATION_QEMU_VM_P11_RETRY",
            "capability_hypothesis": "AUTHENTICATED_TRUE__EXISTING_PHASE_A_LIFECYCLE_AND_LP_TRANSITION_MECHANISMS_SUFFICIENT__NO_NEW_CAPABILITY",
            "execution": "ONE_FRESH_SEALED_REVIEW_OBJECT__EXACT_SCOPE_PAIR__LY_DEPENDENCY__LP_CURRENT_ADMISSION__STOP_AT_HUMAN_DECISION",
        },
        "context": {
            "id": CONTEXT_ID,
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": ENTRY_HEAD,
            "repository_tree": ENTRY_TREE,
        },
        "review_object": {
            "count": 1,
            "lifecycle_id": LIFECYCLE_ID,
            "object_id": OBJECT_ID,
            "review_object_id": REVIEW_ID,
            "presentation_id": PRESENTATION_ID,
            "path": REVIEW.relative_to(ROOT).as_posix(),
            "whole_file_sha256": sha256_path(REVIEW),
            "canonical_inner_sha256": load_canonical(REVIEW)["review_object_sha256"],
        },
        "readiness": {
            "file_sha256": sha256_path(READINESS),
            "checkpoint_sha256": readiness["checkpoint_sha256"],
            "receipt_parent_ready": True,
            "lp_transition": "NONAUTHORITY__NONCONSUMABLE__DETERMINISTIC_CURRENT_ADMISSION_RECONSTRUCTION",
            "lt": "REFERENCED_AS_READINESS_ONLY",
            "lu": "REFERENCED_AS_STATIC_INTEGRATION_ONLY",
            "ly_dependency": ly_readiness_dependency(),
        },
        "scope": {
            "authorized": AUTHORIZED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "isolated_mismatch": "authority_scope",
            "independent_semantic_mutation_count": 1,
        },
        "cross_vector_reuse_assessment": cross_vector(),
        "forward_compatibility": {
            "AMBIGUOUS": "STRONGER",
            "STALE": "STRONGER",
            "REVOKED": "UNCHANGED",
            "SUPERSEDED": "UNCHANGED",
            "WRONG_SCOPE": "STRONGER__FRESH_EXACT_PHASE_A_BINDING__OPERATIONAL_UNSAT",
            "COHERENT_COPY": "STRONGER__LP_CANONICAL_COMMIT_IDENTITY_REQUIRED",
        },
        "architecture": {
            "PRODUCTION_FILES_CHANGED": 0,
            "FM_PRODUCTION_FILES_CHANGED": 0,
            "GN_PRODUCTION_FILES_CHANGED": 0,
            "ER_PRODUCTION_FILES_CHANGED": 0,
            "P11_PRODUCTION_FILES_CHANGED": 0,
            "EX_PRODUCTION_FILES_CHANGED": 0,
            "OWNER_DELTA": 0,
            "ROUTE_COUNT_BEFORE": 1,
            "ROUTE_COUNT_AFTER": 1,
            "REGISTRY_DELTA": 0,
            "CONSTITUTIONAL_CONCEPT_DELTA": 0,
        },
        "e05": {
            "E05_BEFORE": "12/18",
            "LZ_E05_CREDIT": 0,
            "E05_AFTER": "12/18",
            "WRONG_SCOPE_STATUS": "UNSAT",
        },
        "ex": {"EX_REUSED": "VERIFIED__17_OF_17", "EX_RECONSTRUCTED": "VERIFIED__0"},
        "operational_counters": zero_counters(),
        "human_boundary": {
            "authority": "NONE",
            "decision": "PENDING",
            "operation": "NOT_STARTED",
            "next": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_LZ__THEN_HUMAN_DECISION_OVER_EXACT_SEALED_LZ_OBJECT",
        },
    }


def build_decision(context: dict[str, Any]) -> dict[str, Any]:
    review = load_canonical(REVIEW)
    return {
        "FAILURE_CLASS": "DUPLICATE_OR_EQUIVALENT_EDGE",
        "NOVELTY": "FRESH_LIFECYCLE_IDENTITY_REQUIRED__NO_CAPABILITY_NOVELTY",
        "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
        "NEW_CAPABILITY_REQUIRED": "NO",
        "FRESH_LIFECYCLE_CREATED": "YES",
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "FRESH_OBJECT_ID": OBJECT_ID,
        "FRESH_REVIEW_OBJECT_ID": REVIEW_ID,
        "FRESH_OBJECT_WHOLE_SHA256": sha256_path(REVIEW),
        "CANONICAL_INNER_SHA256": review["review_object_sha256"],
        "CONTEXT_SHA256": context["context_sha256"],
        "CONTEXT_WHOLE_SHA256": sha256_path(CONTEXT),
        "PRESENTATION_ID": PRESENTATION_ID,
        "PRESENTATION_SHA256": sha256_path(PRESENTATION),
        "REVIEW_CONTEXT_BASELINE_BINDING": f"{ENTRY_HEAD}/{ENTRY_TREE}",
        "CURRENT_ADMISSION_BINDING": "LP_EXACT_COMMITTED_REVIEW_R_TO_CURRENT_ADMISSION_C_REQUIRED_AFTER_COMMIT_R",
        "LY_READINESS_DEPENDENCY": ly_readiness_dependency(),
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_MISMATCH": "authority_scope",
        "HUMAN_DECISION_STATE": "PENDING",
        "AUTHORITY_STATE": "NONE",
        "LQ_APPROVAL_REUSED": "NO",
        "LR_AUTHORITY_REUSED": "NO",
        "LV_APPROVAL_REUSED": "NO",
        "LW_AUTHORITY_REUSED": "NO",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LZ",
        "LAST_VERIFIED_EDGE": "LW_FINAL_ADMISSION_REVALIDATED__FRESH_AUTHORITY_CONSUMPTION_DURABLY_RECORDED_EXACTLY_ONCE__AUTHORITY_NONREUSABLE",
        "FIRST_BROKEN_EDGE": "LW_CALLER_OWNED_LT_STATE_PARENT_PRECONDITION_TO_LT_RESERVE_ONCE__PARENT_WAS_NOT_MATERIALIZED_OR_VALIDATED_BEFORE_AUTHORITY_CONSUMPTION",
        "FIRST_UNVERIFIED_EDGE": "LT_ATOMIC_EXCLUSIVE_LIFECYCLE_LEAF_RESERVATION_AND_DURABLE_NOT_STARTED_EVENT",
        "CURRENT_LIFECYCLE_LAST_VERIFIED_EDGE": "FRESH_EXACT_WRONG_SCOPE_REVIEW_OBJECT_SEALED__LY_DEPENDENCY_BOUND__LP_TRANSITION_REQUIRED",
        "CURRENT_LIFECYCLE_FIRST_BROKEN_EDGE": "NONE__READY_FOR_INDEPENDENT_HUMAN_AUTHENTICATION",
        "CURRENT_LIFECYCLE_FIRST_UNVERIFIED_EDGE": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_EXACT_SEALED_LZ_OBJECT",
        "MINIMUM_MISSING_CAPABILITY": "NONE",
        "MINIMUM_MISSING_PROOF": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_LZ__THEN_HUMAN_DECISION__OPERATIONAL_WRONG_SCOPE_PROOF_REMAINS_FUTURE",
        "MINIMUM_LEGAL_NEXT_DELTA": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_LZ",
        "OPERATIONAL_RETRY_AUTHORIZED": "NO",
        "TERMINAL": TERMINAL,
    }


def materialize() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources_and_predecessors()
    if repository["current_head"] != ENTRY_HEAD or repository["remote_head"] != ENTRY_HEAD:
        raise LZVerificationError("MATERIALIZATION_REQUIRES_EXACT_LY_ENTRY")
    targets = (CONTEXT, READINESS, REVIEW, PRESENTATION, REDUCTION, DECISION)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise LZVerificationError("LZ_ONE_SHOT_NAMESPACE_NOT_FRESH")
    if (LZ / "operation_state").exists() or TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise LZVerificationError("LZ_MATERIALIZATION_NAMESPACE_NOT_FRESH")

    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=GENERATION_ID,
        operation_identity=OPERATION_ID,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=LZ / "operation_state",
        transient_root=TRANSIENT,
        candidate_source_path=CANDIDATE_REL,
    )
    write_fresh(CONTEXT, context)
    materialization = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=CONTEXT,
        candidate_source_path=CANDIDATE_REL,
    )
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    static = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=ENTRY_HEAD,
        observed_tree=ENTRY_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE_REL,
    )
    receipt_claim = GL.prepare_and_observe_receipt_parent(ROOT, context)
    receipt_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, receipt_claim)
    readiness_inner = {
        "schema_id": "G77_256LZ_PREAUTHORITY_STATIC_READINESS_V1",
        "artifact_class": "AUTHORITY_FREE_STATIC_OBSERVATION__NONOPERATIONAL",
        "lifecycle_id": LIFECYCLE_ID,
        "generation_identity": GENERATION_ID,
        "operation_identity": OPERATION_ID,
        "context_id": CONTEXT_ID,
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(CONTEXT),
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "materialization": materialization,
        "static_readiness": static,
        "receipt_parent_claim": receipt_claim,
        "receipt_parent_checkpoint": receipt_checkpoint,
        "lt_readiness": "REFERENCED__NONAUTHORITY__NONOPERATIONAL",
        "lu_readiness": "REFERENCED__STATIC_PROOF_ONLY__NO_PERMISSION",
        "ly_readiness_dependency": ly_readiness_dependency(),
        "authority_state": "NONE",
        "human_decision_state": "PENDING",
        "operation_state": "NOT_STARTED",
        "operational_counters": zero_counters(),
    }
    readiness = sealed(
        "G77_256LZ_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "checkpoint",
        readiness_inner,
    )
    write_fresh(READINESS, readiness)
    review = sealed(
        "G77_256LZ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1",
        "review_object",
        build_review(context, sha256_path(READINESS)),
    )
    write_fresh(REVIEW, review)
    write_fresh(PRESENTATION, render_presentation(context, review))
    write_fresh(
        REDUCTION,
        sealed(
            "G77_256LZ_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1",
            "reduction",
            build_reduction(context, readiness),
        ),
    )
    write_fresh(
        DECISION,
        sealed(
            "G77_256LZ_TERMINAL_DECISION_ENVELOPE_V1",
            "decision",
            build_decision(context),
        ),
    )
    return verify()


def authenticate_transition(context: dict[str, Any], repository: dict[str, str]) -> dict[str, Any]:
    relative_context = CONTEXT.relative_to(ROOT).as_posix()
    if FM._committed_review_context_path(ROOT, context) != relative_context:
        raise LZVerificationError("LP_CANONICAL_REVIEW_PATH_MISMATCH")
    current_head = repository["current_head"]
    current_tree = repository["current_tree"]
    committed = subprocess.run(
        ["git", "cat-file", "-e", f"{current_head}:{relative_context}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    if not committed:
        relation = FM.authenticate_review_to_current_admission(
            repository_root=ROOT,
            context=context,
            observed_head=current_head,
            observed_tree=current_tree,
        )
        if current_head != ENTRY_HEAD or relation["repository_identity_relation"] != "EXACT_SAME_HEAD_TREE":
            raise LZVerificationError("UNCOMMITTED_REVIEW_STATE_INVALID")
        return {
            "state": "PENDING_IMMUTABLE_COMMIT_R",
            "review_identity_R": "PENDING_COMMIT",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED",
            "transition_is_authority": False,
            "transition_consumable": False,
        }
    introductions = git(
        "log", "--format=%H", "--diff-filter=A", current_head, "--", relative_context
    ).splitlines()
    if len(introductions) != 1:
        raise LZVerificationError("LZ_REVIEW_INTRODUCTION_MISSING_OR_AMBIGUOUS")
    review_head = introductions[0]
    review_tree = git("rev-parse", f"{review_head}^{{tree}}")
    if (
        not is_ancestor(ENTRY_HEAD, review_head)
        or not is_ancestor(review_head, current_head)
        or subprocess.check_output(
            ["git", "show", f"{review_head}:{relative_context}"], cwd=ROOT
        ) != CONTEXT.read_bytes()
    ):
        raise LZVerificationError("LZ_COMMITTED_REVIEW_IDENTITY_INVALID")
    if review_head == current_head:
        return {
            "state": "IMMUTABLE_REVIEW_IDENTITY_R_COMMITTED__SUCCESSOR_C_REQUIRED",
            "review_identity_R": f"{review_head}/{review_tree}",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED__NO_SUCCESSOR_DELTA",
            "transition_is_authority": False,
            "transition_consumable": False,
        }
    proof = FM.build_committed_review_transition(
        repository_root=ROOT,
        context=context,
        current_admission_head=current_head,
        current_admission_tree=current_tree,
    )
    relation = FM.authenticate_review_to_current_admission(
        repository_root=ROOT,
        context=context,
        observed_head=current_head,
        observed_tree=current_tree,
        committed_review_transitions=[proof],
    )
    if (
        proof["review_object_head"] != review_head
        or proof["transition_is_authority"] is not False
        or proof["transition_consumable"] is not False
        or relation["repository_identity_relation"]
        != "EXACT_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION"
    ):
        raise LZVerificationError("LP_TRANSITION_AUTHENTICATION_FAILED")
    return {
        "state": "LP_EXACT_TRANSITION_VERIFIED",
        "review_identity_R": f"{review_head}/{review_tree}",
        "current_admission_identity_C": f"{current_head}/{current_tree}",
        "transition_proof_state": "DERIVED_IN_MEMORY__NONAUTHORITY__NONCONSUMABLE",
        "transition_sha256": proof["transition_sha256"],
        "transition_is_authority": False,
        "transition_consumable": False,
    }


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources_and_predecessors()
    context = load_canonical(CONTEXT)
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    if (
        context["generation_identity"] != GENERATION_ID
        or context["operation_identity"] != OPERATION_ID
        or context["repository_head"] != ENTRY_HEAD
        or context["repository_tree"] != ENTRY_TREE
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] != RUNTIME_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] != RUNTIME_TREE
    ):
        raise LZVerificationError("CANONICAL_CONTEXT_BINDING_MISMATCH")
    readiness = load_canonical(READINESS)
    checkpoint = readiness.get("checkpoint")
    if (
        not isinstance(checkpoint, dict)
        or readiness.get("checkpoint_sha256") != hashlib.sha256(canonical_bytes(checkpoint)).hexdigest()
        or checkpoint.get("authority_state") != "NONE"
        or checkpoint.get("human_decision_state") != "PENDING"
        or checkpoint.get("operation_state") != "NOT_STARTED"
        or any(checkpoint.get("operational_counters", {}).values())
    ):
        raise LZVerificationError("STATIC_READINESS_SEAL_OR_BOUNDARY_INVALID")
    validate_replay_safe_receipt_claim(context, checkpoint["receipt_parent_claim"])

    review_envelope = load_canonical(REVIEW)
    review = review_envelope.get("review_object")
    if (
        review_envelope.get("schema_id")
        != "G77_256LZ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1"
        or not isinstance(review, dict)
        or review_envelope.get("review_object_sha256")
        != hashlib.sha256(canonical_bytes(review)).hexdigest()
        or len(list(LZ.glob("*PHASE_A_REVIEW_OBJECT*.json"))) != 1
    ):
        raise LZVerificationError("REVIEW_OBJECT_CARDINALITY_OR_SEAL_INVALID")
    required = {
        "GENERATION": "G77-256LZ",
        "GENERATION_ID": GENERATION_ID,
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "OBJECT_ID": OBJECT_ID,
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CONTEXT_ID": CONTEXT_ID,
        "PRESENTATION_ID": PRESENTATION_ID,
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "AUTHORITY_STATE": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LZ",
        "RETRY_LIMIT": 0,
        "READINESS": "READY_FOR_HUMAN_DECISION",
    }
    if any(review.get(key) != expected for key, expected in required.items()):
        raise LZVerificationError("REVIEW_OBJECT_REQUIRED_FIELD_MISMATCH")
    binding = review.get("CANONICAL_CONTEXT_BINDING", {})
    if binding != {
        "context_id": CONTEXT_ID,
        "path": CONTEXT.relative_to(ROOT).as_posix(),
        "context_sha256": context["context_sha256"],
        "whole_file_sha256": sha256_path(CONTEXT),
        "repository_head": ENTRY_HEAD,
        "repository_tree": ENTRY_TREE,
        "preauthority_static_readiness_file_sha256": sha256_path(READINESS),
    }:
        raise LZVerificationError("REVIEW_TO_CONTEXT_BINDING_MISMATCH")
    mismatch = review.get("ISOLATED_MISMATCH", {})
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if (
        mismatch.get("field") != "authority_scope"
        or mismatch.get("expected") != AUTHORIZED_SCOPE
        or mismatch.get("presented") != PRESENTED_SCOPE
        or mismatch.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_count") != 1
        or model["baseline"]["authority_scope"] != AUTHORIZED_SCOPE
        or model["presented"]["authority_scope"] != PRESENTED_SCOPE
    ):
        raise LZVerificationError("WRONG_SCOPE_NOT_EXACTLY_ONE_MISMATCH")
    candidate = review.get("CANDIDATE_HUMAN_ACT_MATERIAL", {})
    previous = review.get("PREVIOUS_LIFECYCLE", {})
    if (
        candidate.get("is_authority") is not False
        or candidate.get("human_actor_identity_state") != "ABSENT"
        or candidate.get("human_authority_source_bytes_state") != "ABSENT"
        or candidate.get("proposed_authority_scope") != AUTHORIZED_SCOPE
        or candidate.get("intentionally_different_future_runtime_presented_scope")
        != PRESENTED_SCOPE
        or candidate.get("human_authorizes_presented_scope") is not False
        or previous.get("LQ_APPROVAL_REUSED") is not False
        or previous.get("LR_AUTHORITY_REUSED") is not False
        or previous.get("LR_INVOCATION_REUSED") is not False
        or previous.get("LR_RECEIPT_NAMESPACE_REUSED") is not False
        or previous.get("LR_OPERATION_IDENTITY_REUSED") is not False
        or previous.get("LV_APPROVAL_REUSED") is not False
        or previous.get("LW_AUTHORITY_REUSED") is not False
        or any(
            previous.get(field) != "UNKNOWN"
            for field in (
                "LW_DENIAL_CLASS",
                "LW_P11_ENTRY_COUNT",
                "LW_PROTECTED_INVOCATION_COUNT",
                "LW_PROTECTED_EFFECT_COUNT",
            )
        )
        or review.get("LY_PREAUTHORITY_READINESS_DEPENDENCY")
        != ly_readiness_dependency()
        or not review.get("STATE_COUNTERS")
        or any(review["STATE_COUNTERS"].values())
    ):
        raise LZVerificationError("AUTHORITY_OPERATION_OR_PREDECESSOR_BOUNDARY_INVALID")
    if PRESENTATION.read_text(encoding="utf-8") != render_presentation(context, review_envelope):
        raise LZVerificationError("HUMAN_PRESENTATION_BINDING_MISMATCH")

    forbidden = (
        "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
        "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
        "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
        "*OPERATIONAL_INVOCATION_ATTEMPT*",
        "*SERIAL_CONSOLE*",
        "*POST_EXECUTED_QEMU_ARGV_RECEIPT*",
    )
    if any(list(LZ.rglob(pattern)) for pattern in forbidden):
        raise LZVerificationError("AUTHORITY_OR_OPERATION_ARTIFACT_PRESENT")
    reduction = load_canonical(REDUCTION)
    if (
        reduction.get("reduction_sha256")
        != hashlib.sha256(canonical_bytes(reduction.get("reduction"))).hexdigest()
        or reduction.get("reduction") != build_reduction(context, readiness)
    ):
        raise LZVerificationError("SPCE_REDUCTION_INVALID")
    decision = load_canonical(DECISION)
    if (
        decision.get("decision_sha256")
        != hashlib.sha256(canonical_bytes(decision.get("decision"))).hexdigest()
        or decision.get("decision") != build_decision(context)
    ):
        raise LZVerificationError("TERMINAL_DECISION_INVALID")
    transition = authenticate_transition(context, repository)
    return {
        "terminal": TERMINAL,
        "repository": repository,
        "lifecycle_id": LIFECYCLE_ID,
        "object_id": OBJECT_ID,
        "review_object_id": REVIEW_ID,
        "review_object_whole_sha256": sha256_path(REVIEW),
        "canonical_inner_sha256": review_envelope["review_object_sha256"],
        "context_sha256": context["context_sha256"],
        "context_whole_sha256": sha256_path(CONTEXT),
        "presentation_sha256": sha256_path(PRESENTATION),
        "transition": transition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    arguments = parser.parse_args()
    result = materialize() if arguments.materialize else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
