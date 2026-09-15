#!/usr/bin/env python3
"""One Human-authorized LW authority and one LT-supervised existing FM child."""

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
LW_REL = Path(".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1")
LW = ROOT / LW_REL
LV_REL = Path(".github/governance/evidence/g77_256lv_fresh_wrong_scope_phase_a_review_object_v1")
LV = ROOT / LV_REL
CONTEXT = LV / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REVIEW = LV / "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
PRESENTATION = LV / "G77_256LV_HUMAN_DECISION_PRESENTATION_V1.txt"
READINESS = LV / "G77_256LV_PREAUTHORITY_STATIC_READINESS_V1.json"
SOURCE = LW / "G77_256LW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
TRANSITION = LW / "G77_256LW_LP_COMMITTED_REVIEW_TRANSITION_V1.json"
PREAUTH = LW / "G77_256LW_PREAUTHORITY_READINESS_CHECKPOINT_V1.json"
HANDOFF = LW / "G77_256LW_FRESH_HUMAN_OPERATIONAL_AUTHORITY_V1.json"
FM_BINDING = LW / "G77_256LW_FM_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
LT_BINDING = LW / "G77_256LW_LT_SEALED_SUPERVISOR_INPUT_V1.json"
PRECONSUMPTION = LW / "G77_256LW_FINAL_PRECONSUMPTION_CHECKPOINT_V1.json"
CONSUMPTION = LW / "G77_256LW_AUTHORITY_CONSUMPTION_CHECKPOINT_V1.json"
LAUNCH_HANDOFF = LW / "G77_256LW_LT_LAUNCH_HANDOFF_V1.json"
LT_STATE = LW / "operation_state/lt_supervision/G77_256LW_WRONG_SCOPE_OPERATION_001"
CANDIDATE_REL = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
CANDIDATE = ROOT / CANDIDATE_REL
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LG_PATH = ROOT / (
    ".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/"
    "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
LT_PATH = ROOT / (
    ".github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/"
    "harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py"
)
LT_DECISION = ROOT / (
    ".github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/"
    "G77_256LT_TERMINAL_DECISION_V1.json"
)
LU_RELATION = ROOT / (
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_V1.json"
)
LU_DECISION = ROOT / (
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_TERMINAL_DECISION_V1.json"
)

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
C_HEAD = "e86ada76834b7af95b86dce57dda0927a96e4eb7"
C_TREE = "c5bdac3e664c41c1e0cda6b382f3865d2dd44257"
C_SUBJECT = "G77-256LV record fresh Human decision readiness"
R_HEAD = "342822c1bb51328d9d67155810f3f62513249773"
R_TREE = "f1b4c919b46da766297dd8c0d1a98dbed9b1073a"
R_SUBJECT = "G77-256LV seal fresh WRONG_SCOPE Phase-A review object"
LU_HEAD = "3f6055f85c8bff0a3de89eda27421c92e0742904"
LT_HEAD = "f22fae2529de35eaf8093776c04a6a8e05a097f6"
LT_TREE = "921382a2b0f852150037db4c7eff4d9884693211"
LU_TREE = "2e99987b75cfdc891338870281a12fe21e018ec6"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
OBJECT_ID = "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
LIFECYCLE_ID = "G77_256LV_WRONG_SCOPE_PHASE_A_LIFECYCLE_001"
OBJECT_WHOLE_SHA256 = "333c95c19351f237e5e8bd000894e6bbabadc7c5851b33e624d2c256378c4f5e"
OBJECT_INNER_SHA256 = "07b12ee47da2b363f3818a8efbda6b33cf31084c42935679377c690f0f1a15c4"
CONTEXT_SHA256 = "d83f24de26ebcdedc5ddb280b842c515f848773c9a56b42111a6afdfe9862d33"
CONTEXT_WHOLE_SHA256 = "6e2bb18c36e9b6ded9a2c47ff6ba5d027f6a9cebb6d8a14b170f0dc6092200f4"
PRESENTATION_SHA256 = "9e70696fbed8d08700c05af4c77ab6cdc0f169cfd10d82647977991951acf21b"
READINESS_SHA256 = "52f75742d41e156f97a7044e3cc734f899fff751847df8f330f636cc15e2463e"
TRANSITION_SHA256 = "923a168080421db554eb1899c98fd7ae17ad0cab9e0dc61774425cd8449e0019"
FM_SHA256 = "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8"
LG_SHA256 = "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f"
LT_SHA256 = "5d1e54acd3e37390e3c0077c1f480b6008f849e569ced8889e6aacc04fbccf6f"
LT_DECISION_SHA256 = "f0a6acfc31c72b1b1e890cf2e3c587b4f5ccf179ecf2da9c6e2ad724a27aae9f"
LU_RELATION_SHA256 = "b17bcf19cc11142b0a4a603138c0311dcce0cfb34510c76dff156fbfcce9e80c"
LU_DECISION_SHA256 = "77cf5cd0c71875bca1d57f17a06605c79101dab9217f3f1782be7a1767141cf7"
AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
GENERATION = "G77_256LV_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LV_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
AUTHORITY_ID = "G77_256LW_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001"
LT_LIFECYCLE_ID = "G77_256LW_WRONG_SCOPE_OPERATIONAL_LIFECYCLE_001"
LT_INVOCATION_ID = "G77_256LW_EXACT_FM_INVOCATION_001"
CAPABILITY_ID = "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_DURABLE_TERMINAL_HANDOFF_V1"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_module(path: Path, name: str, expected: str) -> ModuleType:
    if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
        raise RuntimeError(f"AUTHENTICATED_OWNER_MISMATCH:{name}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"OWNER_IMPORT_FAILED:{name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256lw_existing_fm_owner", FM_SHA256)
LG = load_module(LG_PATH, "g77_256lw_existing_lg_semantics", LG_SHA256)
LT = load_module(LT_PATH, "g77_256lw_existing_lt_supervisor", LT_SHA256)


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def seal(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, field: value, f"{field}_sha256": digest(value)}


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"NONCANONICAL_JSON:{path.name}")
    return value


def inner(path: Path, field: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(field)
    if not isinstance(value, dict) or envelope.get(f"{field}_sha256") != digest(value):
        raise RuntimeError(f"SEAL_MISMATCH:{path.name}")
    return value


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"ONE_SHOT_ARTIFACT_COLLISION:{path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return FM.write_atomic(path, value)


def allowed_worktree() -> None:
    allowed_lv = {Path("operation_state/receipts/G77_256LV_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"), Path("operation_state/receipts/G77_256LV_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")}
    allowed_lv |= {Path("operation_state/runtime_export") / name for name in (
        "G77_256LV_RAW_EXECUTION_EVIDENCE_V1.jsonl", "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl", "G77_256DN_SPCE_EXECUTION_SEAL_V1.json", "G77_256LV_PRE_ACT_CHECKPOINT_V1.json", "G77_256LV_AUTHORITY_CHECKPOINT_V1.json", "G77_256LV_GUEST_EXECUTION_SEAL_V1.json", "G77_256LV_GUEST_TEARDOWN_SEAL_V1.json", "G77_256LV_CONTINUATION_MANIFEST_TERMINAL_V1.json")}
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??":
            raise RuntimeError(f"TRACKED_OR_STAGED_MUTATION:{line}")
        path = line[3:]
        if path.startswith(LW_REL.as_posix() + "/"):
            continue
        if path.startswith(LV_REL.as_posix() + "/") and Path(path[len(LV_REL.as_posix()) + 1:]) in allowed_lv:
            continue
        raise RuntimeError(f"UNRELATED_UNTRACKED_MUTATION:{line}")


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    if (ROOT != Path("/home/pisarna/work/sapianta-fl") or git("branch", "--show-current") != BRANCH or git("rev-parse", "HEAD") != C_HEAD or git("rev-parse", "HEAD^{tree}") != C_TREE or git("show", "-s", "--format=%s", "HEAD") != C_SUBJECT or remote_head != C_HEAD or git("rev-parse", f"{R_HEAD}^{{tree}}") != R_TREE or git("show", "-s", "--format=%s", R_HEAD) != R_SUBJECT or not is_ancestor(LU_HEAD, R_HEAD) or not is_ancestor(R_HEAD, C_HEAD) or git("status", "--porcelain=v1", "--untracked-files=no")):
        raise RuntimeError("LW_ENTRY_AUTHENTICATION_CONFLICT")
    allowed_worktree()
    nested = ROOT / "sapianta_system"
    if (git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested) or git("branch", "--show-current", cwd=nested) or git("rev-parse", f"{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD or nested_remote_tag != NESTED_HEAD):
        raise RuntimeError("NESTED_AUTHORITY_CONFLICT")


def authenticate_readiness_chain() -> None:
    if (git("rev-parse", f"{LT_HEAD}^{{tree}}") != LT_TREE or git("rev-parse", f"{LU_HEAD}^{{tree}}") != LU_TREE or not is_ancestor(LT_HEAD, LU_HEAD) or any(sha256_path(p) != h for p, h in ((LT_PATH, LT_SHA256), (LT_DECISION, LT_DECISION_SHA256), (LU_RELATION, LU_RELATION_SHA256), (LU_DECISION, LU_DECISION_SHA256)))):
        raise RuntimeError("LT_LU_IDENTITY_CONFLICT")
    lt = json.loads(LT_DECISION.read_bytes())["decision"]
    lu = json.loads(LU_DECISION.read_bytes())["decision"]
    relation = json.loads(LU_RELATION.read_bytes())["relation"]
    if (lt.get("CAPABILITY_ID") != CAPABILITY_ID or lt.get("OPERATIONAL_RETRY_AUTHORIZED") != "NO" or lu.get("INTEGRATION_READINESS") != "PROVEN" or lu.get("NEW_CAPABILITY_REQUIRED") != "NO" or relation.get("integration_readiness") != "PROVEN" or relation.get("exact_existing_fm_invocation", {}).get("launcher") != FM_PATH.relative_to(ROOT).as_posix()):
        raise RuntimeError("LT_LU_SEMANTIC_CONFLICT")


def authenticate_lv() -> tuple[dict[str, Any], dict[str, Any]]:
    expected = ((REVIEW, OBJECT_WHOLE_SHA256), (CONTEXT, CONTEXT_WHOLE_SHA256), (PRESENTATION, PRESENTATION_SHA256), (READINESS, READINESS_SHA256))
    if any(p.is_symlink() or not p.is_file() or sha256_path(p) != h for p, h in expected):
        raise RuntimeError("LV_OBJECT_CONTEXT_PRESENTATION_READINESS_CONFLICT")
    envelope = load_canonical(REVIEW)
    review = envelope.get("review_object")
    if (not isinstance(review, dict) or envelope.get("review_object_sha256") != OBJECT_INNER_SHA256 or digest(review) != OBJECT_INNER_SHA256 or review.get("LIFECYCLE_ID") != LIFECYCLE_ID or review.get("REVIEW_OBJECT_ID") != OBJECT_ID or review.get("VECTOR") != "WRONG_SCOPE" or review.get("PHASE") != "A" or review.get("AUTHORIZED_SCOPE") != AUTHORIZED_SCOPE or review.get("PRESENTED_SCOPE") != PRESENTED_SCOPE or review.get("ONE_SHOT_LIMIT") != 1 or review.get("RETRY_LIMIT") != 0 or review.get("AUTHORITY_CREATED") != "NO" or review.get("AUTHORITY_CONSUMED") != "NO" or review.get("OPERATION_STATE") != "NOT_STARTED" or any(review.get("STATE_COUNTERS", {}).values())):
        raise RuntimeError("LV_REVIEW_OBJECT_BINDING_CONFLICT")
    mismatch = review.get("ISOLATED_MISMATCH", {})
    if (mismatch.get("field") != "authority_scope" or mismatch.get("expected") != AUTHORIZED_SCOPE or mismatch.get("presented") != PRESENTED_SCOPE or mismatch.get("independent_semantic_mutation_count") != 1):
        raise RuntimeError("LV_ISOLATED_MISMATCH_CONFLICT")
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    if (context.get("context_sha256") != CONTEXT_SHA256 or context.get("generation_identity") != GENERATION or context.get("operation_identity") != OPERATION or context.get("repository_head") != LU_HEAD or FM.context_vector(context) != "WRONG_SCOPE"):
        raise RuntimeError("LV_CANONICAL_CONTEXT_CONFLICT")
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if model.get("independent_semantic_mutation_set") != [f"authority_scope:{AUTHORIZED_SCOPE}->{PRESENTED_SCOPE}"]:
        raise RuntimeError("WRONG_SCOPE_SEMANTICS_CONFLICT")
    return review, context


def authenticate_human_source() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    required = (OBJECT_ID, OBJECT_WHOLE_SHA256, AUTHORIZED_SCOPE, PRESENTED_SCOPE, "natanko en enkratni", "ne prenaša")
    if SOURCE.is_symlink() or any(value not in text for value in required) or text.count(OBJECT_ID) != 1 or text.count(OBJECT_WHOLE_SHA256) != 1:
        raise RuntimeError("HUMAN_DECISION_SOURCE_CONFLICT")
    return sha256_path(SOURCE)


def derive_transition(context: dict[str, Any]) -> dict[str, Any]:
    proof = FM.build_committed_review_transition(repository_root=ROOT, context=context, current_admission_head=C_HEAD, current_admission_tree=C_TREE)
    if (proof.get("transition_sha256") != TRANSITION_SHA256 or proof.get("review_object_head") != R_HEAD or proof.get("review_object_tree") != R_TREE or proof.get("current_admission_head") != C_HEAD or proof.get("current_admission_tree") != C_TREE or proof.get("transition_is_authority") is not False or proof.get("transition_consumable") is not False):
        raise RuntimeError("LP_TRANSITION_BINDING_CONFLICT")
    relation = FM.authenticate_review_to_current_admission(repository_root=ROOT, context=context, observed_head=C_HEAD, observed_tree=C_TREE, committed_review_transitions=[proof])
    if relation.get("committed_review_transition_sha256") != TRANSITION_SHA256:
        raise RuntimeError("LP_TRANSITION_AUTHENTICATION_FAILED")
    return proof


def validate_admission(context: dict[str, Any], handoff: dict[str, Any], authority_sha: str, proof: dict[str, Any]) -> dict[str, str]:
    observed = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    argv = context["canonical_argv"]
    return FM.validate_final_admission(repository_root=ROOT, context=context, authority=handoff, authority_file_sha256=authority_sha, supplied_authority_sha256=authority_sha, observed_head=C_HEAD, observed_tree=C_TREE, anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT), repository_clean=git("status", "--porcelain=v1", "--untracked-files=no") == "", observed_asset_sha256=observed, argv=argv, canonical_argv_sha256=FM.load_canonicalizer(ROOT).argv_sha256(argv), receipt_namespace_consumed=any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)), candidate_source_path=CANDIDATE_REL, committed_review_transitions=[proof])


def authority(context: dict[str, Any], source_sha: str) -> dict[str, Any]:
    return {"schema_id": FM.AUTHORIZATION_SCHEMA, "authorization_present": True, "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION", "authorization_source_sha256": source_sha, "authorized_context_sha256": CONTEXT_SHA256, "authorized_operation_identity": OPERATION, "authorized_generation_identity": GENERATION, "authorized_vector": "WRONG_SCOPE", "authorized_repository_head": C_HEAD, "authorized_repository_tree": C_TREE, "authorized_constitutional_anchor_head": ANCHOR, "authorized_candidate_sha256": context["candidate_manifest_sha256"], "authorized_canonical_argv_sha256": context["canonical_argv_sha256"], "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"], "authorized_fk_adapter_sha256": FM.FK_ADAPTER_SHA256, "vm_boot_limit": 1, "qemu_system_execution_limit": 1, "wrong_scope_operational_attempt_limit": 1, "retry_limit": 0, "repair_limit": 0, "replay_limit": 0, "receipt_namespace_must_be_unconsumed": True, "network_authorized": False, "provider_authorized": False, "trusted_access_authorized": False, "authorization_reusable": False, "auto_continuable": False}


def combined_fm_binding(transition_file_sha: str) -> tuple[dict[str, Any], list[str]]:
    fm_envelope = FM.build_preconsumption_invocation_binding(repository_root=ROOT, operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF)
    base = FM.validate_preconsumption_invocation_binding(repository_root=ROOT, operation_context=CONTEXT, live_candidate_binding=CANDIDATE, execution_authority=HANDOFF, envelope=fm_envelope)
    argv = [*base["final_fm_argv"], "--committed-review-transition", TRANSITION.relative_to(ROOT).as_posix(), "--committed-review-transition-sha256", transition_file_sha]
    value = {"schema_id": "G77_256LW_FM_PRECONSUMPTION_INVOCATION_BINDING_V1", "binding_phase": "BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION", "fm_owned_base_binding": fm_envelope, "lp_transition_path": TRANSITION.relative_to(ROOT).as_posix(), "lp_transition_file_sha256": transition_file_sha, "lp_transition_inner_sha256": TRANSITION_SHA256, "lp_transition_is_authority": False, "lp_transition_consumable": False, "final_fm_argv": argv, "final_fm_argv_sha256": digest(argv), "caller_digest_input_count": 0, "process_started": False, "authority_consumption_count": 0, "fm_operational_invocation_count": 0}
    return seal("G77_256LW_FM_PRECONSUMPTION_INVOCATION_BINDING_ENVELOPE_V1", "binding", value), argv


def preflight(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    authenticate_readiness_chain()
    review, context = authenticate_lv()
    source_sha = authenticate_human_source()
    dynamic = (TRANSITION, PREAUTH, HANDOFF, FM_BINDING, LT_BINDING, PRECONSUMPTION, CONSUMPTION, LAUNCH_HANDOFF, LT_STATE)
    if any(path.exists() or path.is_symlink() for path in dynamic):
        raise RuntimeError("LW_PREAUTHORITY_NAMESPACE_NOT_FRESH")
    proof = derive_transition(context)
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    static = FM.authority_free_static_readiness(repository_root=ROOT, context=context, observed_head=C_HEAD, observed_tree=C_TREE, repository_clean=True, observed_asset_sha256=observations, candidate_source_path=CANDIDATE_REL, committed_review_transitions=[proof])
    if any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)) or Path(context["serial_path"]).exists():
        raise RuntimeError("LW_OPERATION_NAMESPACE_NOT_FRESH")
    transition_file_sha = persist(TRANSITION, proof)
    checkpoint = {"schema_id": "G77_256LW_PREAUTHORITY_READINESS_CHECKPOINT_V1", "recorded_at_utc": now(), "generation": "G77-256LW", "repository": {"branch": BRANCH, "review_head": R_HEAD, "review_tree": R_TREE, "current_head": C_HEAD, "current_tree": C_TREE, "remote_head": args.remote_head}, "lv": {"lifecycle_id": LIFECYCLE_ID, "review_object_id": OBJECT_ID, "review_object_sha256": OBJECT_WHOLE_SHA256, "canonical_inner_sha256": OBJECT_INNER_SHA256, "context_sha256": CONTEXT_SHA256, "context_whole_sha256": CONTEXT_WHOLE_SHA256, "presentation_sha256": PRESENTATION_SHA256}, "human_decision": {"source": "EXPLICIT_CURRENT_HUMAN_DECISION_OVER_INDEPENDENTLY_AUTHENTICATED_LV_OBJECT", "source_sha256": source_sha, "count": 1, "authorized_scope": AUTHORIZED_SCOPE, "presented_scope": PRESENTED_SCOPE, "authorized_operation_count": 1, "authorized_retry_count": 0}, "failure_class": "PROOF_GAP", "novelty": "FRESH_HUMAN_AUTHORIZED_OPERATIONAL_WRONG_SCOPE_PROOF_USING_EXISTING_LT_LU_READINESS", "new_capability_required": "NO", "new_proof_required": "YES__AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11", "isolated_mismatch": "authority_scope", "isolated_mismatch_count": 1, "lp_transition_sha256": TRANSITION_SHA256, "lp_transition_file_sha256": transition_file_sha, "lt_capability_id": CAPABILITY_ID, "lt_head": LT_HEAD, "lu_head": LU_HEAD, "lu_integration_readiness": "PROVEN", "fm_static_readiness_sha256": static["readiness_sha256"], "receipt_namespace_unused": True, "lt_namespace_fresh": True, "lr_authority_reused": False, "lq_approval_reused": False, "authority_created_count": 0, "authority_consumed_count": 0, "operation_attempt_count": 0, "retry_count": 0, "ready_for_authority_creation": True}
    persist(PREAUTH, seal("G77_256LW_PREAUTHORITY_READINESS_CHECKPOINT_ENVELOPE_V1", "checkpoint", checkpoint))
    print("A__G77_256LW_PREAUTHORITY_READY__ZERO_AUTHORITY__ZERO_OPERATION")


def prepare_authority(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    authenticate_readiness_chain()
    _, context = authenticate_lv()
    source_sha = authenticate_human_source()
    proof = derive_transition(context)
    if FM.load_committed_review_transition(TRANSITION, sha256_path(TRANSITION)) != proof:
        raise RuntimeError("DURABLE_LP_TRANSITION_DRIFT")
    checkpoint = inner(PREAUTH, "checkpoint")
    if not checkpoint.get("ready_for_authority_creation") or checkpoint.get("authority_created_count") != 0 or checkpoint.get("human_decision", {}).get("source_sha256") != source_sha:
        raise RuntimeError("PREAUTHORITY_CHECKPOINT_CONFLICT")
    if any(path.exists() or path.is_symlink() for path in (HANDOFF, FM_BINDING, LT_BINDING, PRECONSUMPTION, CONSUMPTION, LAUNCH_HANDOFF, LT_STATE)):
        raise RuntimeError("LW_AUTHORITY_NAMESPACE_NOT_FRESH")
    result = FM.write_authority_handoff(HANDOFF, authority(context, source_sha))
    handoff, authority_sha = FM.load_authority(HANDOFF)
    if result["authority_file_sha256"] != authority_sha:
        raise RuntimeError("AUTHORITY_PERSISTENCE_MISMATCH")
    admission = validate_admission(context, handoff, authority_sha, proof)
    fm_envelope, argv = combined_fm_binding(sha256_path(TRANSITION))
    fm_file_sha = persist(FM_BINDING, fm_envelope)
    fm_binding_sha = fm_envelope["binding_sha256"]
    lt_envelope = LT.build_binding(lifecycle_id=LT_LIFECYCLE_ID, invocation_id=LT_INVOCATION_ID, invocation_binding_identity="FM_BINDING_SHA256:" + fm_binding_sha, fm_input_identity="CONTEXT_FILE_SHA256:" + CONTEXT_WHOLE_SHA256, admission_identity=f"HEAD:{C_HEAD}__TREE:{C_TREE}", authority_binding_sha256=authority_sha, execution_class="FUTURE_SEPARATELY_AUTHORIZED_FM_INVOCATION", working_directory=ROOT, argv=argv)
    LT.write_binding_once(LT_BINDING, lt_envelope)
    lt_file_sha = sha256_path(LT_BINDING)
    LT.load_binding(LT_BINDING)
    final = {"schema_id": "G77_256LW_FINAL_PRECONSUMPTION_CHECKPOINT_V1", "recorded_at_utc": now(), "generation": "G77-256LW", "authority_id": AUTHORITY_ID, "authority_path": HANDOFF.relative_to(ROOT).as_posix(), "authority_file_sha256": authority_sha, "authority_inner_sha256": handoff["authorization_sha256"], "authority_source_sha256": source_sha, "authority_state": "GRANTED_UNCONSUMED", "authority_valid": True, "authority_unconsumed": True, "object_id": OBJECT_ID, "object_whole_sha256": OBJECT_WHOLE_SHA256, "authorized_scope": AUTHORIZED_SCOPE, "presented_scope": PRESENTED_SCOPE, "isolated_mismatch": "authority_scope", "context_sha256": CONTEXT_SHA256, "current_admission_identity": f"{C_HEAD}/{C_TREE}", "final_admission_validation": "PASS", "admission_result": admission["result"], "fm_binding_file_sha256": fm_file_sha, "fm_invocation_binding_sha256": fm_binding_sha, "final_fm_argv_sha256": digest(argv), "lt_capability_id": CAPABILITY_ID, "lt_lifecycle_id": LT_LIFECYCLE_ID, "lt_invocation_id": LT_INVOCATION_ID, "lt_input_file_sha256": lt_file_sha, "lt_input_inner_sha256": lt_envelope["binding_sha256"], "attempt_limit": 1, "retry_limit": 0, "lt_namespace_fresh": True, "lt_reservation_count": 0, "lt_child_launch_count": 0, "fm_operation_attempt_count": 0, "qemu_start_count": 0, "vm_start_count": 0, "authority_created_count": 1, "authority_consumed_count": 0}
    persist(PRECONSUMPTION, seal("G77_256LW_FINAL_PRECONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", final))
    print(json.dumps({"terminal": "A__G77_256LW_ONE_AUTHORITY_CREATED__FINAL_PRECONSUMPTION_READY__ZERO_OPERATION", "authority_id": AUTHORITY_ID, "authority_sha256": authority_sha, "lt_input_sha256": lt_file_sha}, sort_keys=True))


def consume_and_launch(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    _, context = authenticate_lv()
    source_sha = authenticate_human_source()
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, LAUNCH_HANDOFF, LT_STATE)):
        raise RuntimeError("LW_AUTHORITY_CONSUMED_OR_LT_RESERVED__NO_RELAUNCH")
    proof = derive_transition(context)
    if FM.load_committed_review_transition(TRANSITION, sha256_path(TRANSITION)) != proof:
        raise RuntimeError("DURABLE_LP_TRANSITION_DRIFT")
    handoff, authority_sha = FM.load_authority(HANDOFF)
    fm_expected, argv = combined_fm_binding(sha256_path(TRANSITION))
    if load_canonical(FM_BINDING) != fm_expected:
        raise RuntimeError("FM_INVOCATION_BINDING_DRIFT")
    expected_lt = LT.build_binding(lifecycle_id=LT_LIFECYCLE_ID, invocation_id=LT_INVOCATION_ID, invocation_binding_identity="FM_BINDING_SHA256:" + fm_expected["binding_sha256"], fm_input_identity="CONTEXT_FILE_SHA256:" + CONTEXT_WHOLE_SHA256, admission_identity=f"HEAD:{C_HEAD}__TREE:{C_TREE}", authority_binding_sha256=authority_sha, execution_class="FUTURE_SEPARATELY_AUTHORIZED_FM_INVOCATION", working_directory=ROOT, argv=argv)
    if load_canonical(LT_BINDING) != expected_lt:
        raise RuntimeError("LT_SEALED_INPUT_DRIFT")
    checkpoint = inner(PRECONSUMPTION, "checkpoint")
    if checkpoint.get("authority_state") != "GRANTED_UNCONSUMED" or checkpoint.get("authority_file_sha256") != authority_sha or checkpoint.get("lt_reservation_count") != 0 or checkpoint.get("retry_limit") != 0:
        raise RuntimeError("FINAL_PRECONSUMPTION_CHECKPOINT_DRIFT")
    validate_admission(context, handoff, authority_sha, proof)
    consumed = {"schema_id": "G77_256LW_AUTHORITY_CONSUMPTION_CHECKPOINT_V1", "recorded_at_utc": now(), "generation": "G77-256LW", "authority_id": AUTHORITY_ID, "authority_file_sha256": authority_sha, "authority_source_sha256": source_sha, "authority_state_before": "GRANTED_UNCONSUMED", "authority_state_after": "CONSUMED__NONREUSABLE", "authority_created_count": 1, "authority_consumed_count": 1, "authority_reusable": False, "operation_attempt_count_at_consumption": 0, "retry_count": 0, "lt_reservation_count_at_consumption": 0, "fm_operation_attempt_count_at_consumption": 0}
    persist(CONSUMPTION, seal("G77_256LW_AUTHORITY_CONSUMPTION_CHECKPOINT_ENVELOPE_V1", "checkpoint", consumed))
    handoff_result = LT.launch_detached(LT_STATE, LT_BINDING)
    launch = {"schema_id": "G77_256LW_LT_LAUNCH_HANDOFF_V1", "recorded_at_utc": now(), "generation": "G77-256LW", "authority_id": AUTHORITY_ID, "authority_state": "CONSUMED__NONREUSABLE", "lt_lifecycle_id": LT_LIFECYCLE_ID, "lt_invocation_id": LT_INVOCATION_ID, "lt_input_file_sha256": sha256_path(LT_BINDING), "lt_reservation_count": 1, "lt_child_launch_count_maximum": 1, "fm_operation_attempt_count_maximum": 1, "retry_count": 0, "handoff": handoff_result}
    persist(LAUNCH_HANDOFF, seal("G77_256LW_LT_LAUNCH_HANDOFF_ENVELOPE_V1", "handoff", launch))
    print(json.dumps(handoff_result, sort_keys=True))


def status() -> None:
    latest = LT.latest_state(LT_STATE)
    print(canonical_bytes(latest).decode("utf-8"), end="")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("preflight", "prepare-authority", "consume-and-launch", "status"))
    parser.add_argument("--remote-head", default=C_HEAD)
    parser.add_argument("--nested-remote-tag", default=NESTED_HEAD)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.phase == "preflight":
        preflight(arguments)
    elif arguments.phase == "prepare-authority":
        prepare_authority(arguments)
    elif arguments.phase == "consume-and-launch":
        consume_and_launch(arguments)
    else:
        status()
