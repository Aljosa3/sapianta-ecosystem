#!/usr/bin/env python3
"""Materialize once, then replay-verify, the authority-free G77-256LM Phase A.

The materialization path reuses the existing FM operation-state owner and the
existing GL receipt-parent orchestration.  The default path is read-only and
has no operational entry point.  Neither path creates Human authority, writes
an execution receipt, invokes FM main/QEMU/P11, or performs a protected effect.
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
ENTRY_HEAD = "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
ENTRY_TREE = "607e9dae3a562d823d64b17888c11d3e4b881e2f"
ENTRY_SUBJECT = "G77-256LL record preconsumption admission failure"
ANCESTRY_ANCHOR = "584aa26914aa5a4547070bbf91bfedf2250d205c"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
LL_TREE = "f2bf3b067736ca4e60b25f97f09446d138308887"
RUNTIME_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
RUNTIME_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
GENERATION = "G77_256LM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
DECISION_ID = "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
OPERATION = "G77_256LM_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
ATTEMPT = "G77_256LM_E05_AUTHORIZED_ATTEMPT_001"
PREFIX = "G77_256LM"
TERMINAL = (
    "A__G77_256LM_WRONG_SCOPE_RECEIPT_PARENT_READINESS_RECONCILED__"
    "FRESH_PHASE_A_DECISION_OBJECT_SEALED__ZERO_AUTHORITY__ZERO_OPERATION__"
    "READY_FOR_HUMAN_DECISION"
)

LM_REL = Path(
    ".github/governance/evidence/"
    "g77_256lm_wrong_scope_receipt_parent_phase_a_v1"
)
LM = ROOT / LM_REL
LL_REL = Path(
    ".github/governance/evidence/"
    "g77_256ll_wrong_scope_operational_acceptance_v1"
)
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
SOURCE_HASHES = {
    FM_REL: "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247",
    GL_REL: "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    LG_REL: "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f",
    Path(".github/governance/evidence/g77_256le_wrong_scope_minimum_governed_delta_v1/G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"): "7710f40b8f2bb57229167c37fff527cf2e18c81769f82db096e029a3895c45dc",
    Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"): "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    Path("aigol/runtime/canonical_human_authority_act_contract_v1.py"): "905ce577c31c2c538033455d1633470a34e9f7a94edd6190d50932e97ba8ebc8",
    Path("tests/p11_da_operational_consumer_v1.py"): "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
    LL_REL / "G77_256LL_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json": "bf97489792e1affb50aa3ccdd0ccab1acc351977494304f6a88fa6c0bec9aa56",
}

CONTEXT = LM / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
OBSERVATION = LM / "G77_256LM_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
EQUIVALENCE = LM / "G77_256LM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
READINESS = LM / "G77_256LM_PREAUTHORITY_STATIC_READINESS_V1.json"
ROOT_CAUSE = LM / "G77_256LM_RECEIPT_PARENT_ROOT_CAUSE_V1.json"
DECISION = LM / "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_V1.json"
PRESENTATION = LM / "G77_256LM_HUMAN_DECISION_PRESENTATION_V1.txt"
REDUCTION = LM / "G77_256LM_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = LM / "G77_256LM_G48_IMPLEMENTATION_REPORT_V1.md"
TRANSIENT = Path("/tmp/g77_256lm_wrong_scope_receipt_parent_phase_a_v1")


class LMVerificationError(RuntimeError):
    """One deterministic fail-closed LM lifecycle error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise LMVerificationError(f"MODULE_UNAVAILABLE:{name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(ROOT / FM_REL, "g77_256lm_existing_fm_owner")
GL = load_module(ROOT / GL_REL, "g77_256lm_existing_gl_orchestration")
LG = load_module(ROOT / LG_REL, "g77_256lm_existing_wrong_scope_adapter")


def load_canonical(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LMVerificationError(f"DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LMVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(value)),
    }


def write_fresh(path: Path, value: dict[str, Any] | str) -> None:
    if path.exists() or path.is_symlink():
        raise LMVerificationError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_bytes(canonical_bytes(value))


def authenticate_repository() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("rev-parse", "--show-toplevel") != str(ROOT)
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(ANCESTRY_ANCHOR, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LMVerificationError("LL_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    unexpected = [
        line for line in subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT, text=True,
        ).splitlines()
        if not line[3:].startswith(LM_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LMVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    if git("rev-parse", f"{ENTRY_HEAD}:{LL_REL}") != LL_TREE:
        raise LMVerificationError("LL_TERMINAL_TREE_IDENTITY_MISMATCH")
    changed_ll = subprocess.run(
        ["git", "diff", "--quiet", ENTRY_HEAD, "--", str(LL_REL)], cwd=ROOT,
        check=False,
    ).returncode
    if changed_ll != 0:
        raise LMVerificationError("LL_TERMINAL_IMMUTABILITY_VIOLATION")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LMVerificationError("NESTED_AUTHORITY_CHECKPOINT_MISMATCH")
    return {"entry_head": ENTRY_HEAD, "entry_tree": ENTRY_TREE, "head": head,
            "remote": remote}


def authenticate_sources() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LMVerificationError(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != path.read_bytes():
            raise LMVerificationError(f"SOURCE_NOT_ENTRY_COMMITTED:{relative}")


def zero_counters() -> dict[str, int]:
    return {
        "HUMAN_AUTHORITY_SOURCE_COUNT": 0,
        "AUTHORITY_CREATION_COUNT": 0,
        "AUTHORITY_CONSUMPTION_COUNT": 0,
        "OPERATION_ATTEMPT_COUNT": 0,
        "QEMU_START_COUNT": 0,
        "VM_START_COUNT": 0,
        "RETRY_COUNT": 0,
        "OPERATIONAL_REPLAY_COUNT": 0,
        "REPAIR_RETRY_COUNT": 0,
        "P11_ENTRY_COUNT": 0,
        "PROTECTED_INVOCATION_COUNT": 0,
        "PROTECTED_EFFECT_COUNT": 0,
    }


def root_cause_fact() -> dict[str, Any]:
    return {
        "schema_id": "G77_256LM_RECEIPT_PARENT_ROOT_CAUSE_V1",
        "failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "novelty": "NEW_PRECONSUMPTION_MATERIALIZATION_DEFECT_WITHIN_LL_ATTEMPT",
        "classification": "B__EXISTING_DERIVED_AUTHORITY_FREE_PHASE_A_MATERIALIZATION_ARTIFACT",
        "affected_invariant": "ONE_SHOT_FINAL_ADMISSION_REQUIRES_DURABLE_UNUSED_RECEIPT_PARENT",
        "previous_closest_edge": "G77_256GL_EXISTING_RECEIPT_PARENT_PREAUTHORIZATION_EQUIVALENCE",
        "semantic_difference": "LL_MATERIALIZED_OPERATION_STATE_BUT_OMITTED_GL_FM_RECEIPT_PARENT_PREPARATION",
        "production_behavior_impact": "NONE__NO_OPERATIONAL_PROCESS_STARTED",
        "new_capability_required": "NO",
        "new_proof_required": "OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY__STILL_MISSING",
        "convergence_signal": "STRONG__ONE_EXISTING_MECHANISM_REUSED_BEFORE_NEW_HUMAN_DECISION",
        "repetition_pressure": "REDUCED__NO_EQUIVALENT_OPERATIONAL_ATTEMPT",
        "verification_amplification_risk": "LOW__ONE_PHASE_A_MATERIALIZATION_AND_READ_ONLY_REPLAY",
        "authenticated_owner": "EXISTING_GA_CERTIFIED_FM_PREPARE_RECEIPT_PARENT",
        "validation_owner": "EXISTING_FM_VALIDATE_RECEIPT_PARENT_READY",
        "lifecycle_stage": "EXPLICIT_AUTHORITY_FREE_PRELAUNCH_PHASE_A_AFTER_OPERATION_STATE_MATERIALIZATION_BEFORE_FINAL_ADMISSION",
        "creation_is_authority_free": True,
        "creation_is_operational_attempt": False,
        "creates_human_authority": False,
        "consumes_human_authority": False,
        "behavior_class": "PREPARATION_ORCHESTRATION__NOT_PRODUCTION_EXECUTION",
        "prior_authenticated_vector_mechanism": "G77_256GL_PREPARE_AND_OBSERVE_RECEIPT_PARENT__REUSED_BY_LATER_SATISFIED_VECTOR_PHASE_A_LIFECYCLES",
        "exact_mechanism_reusable_without_production_change": True,
        "production_owner_or_route_change_required": False,
        "ll_exact_cause": "MISSING_MATERIALIZATION__LL_PREPARE_CALLED_FM_MATERIALIZE_OPERATION_STATE_BUT_NOT_GL_PREPARE_AND_OBSERVE_RECEIPT_PARENT",
        "wrong_namespace": False,
        "successor_workspace_isolation_defect": False,
        "cleanup_ordering_defect": False,
        "path_ownership_defect": False,
        "symlink_defect": False,
        "readiness_provable_before_human_decision": True,
        "ll_authority_transfer": "NO",
        "ll_proof_transfer": "NO",
        "ll_e05_credit_transfer": "NO",
    }


def build_decision(context: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "GENERATION_ID": GENERATION,
        "VECTOR": "WRONG_SCOPE",
        "DECISION_OBJECT_ID": DECISION_ID,
        "CANONICAL_OPERATION_ID": OPERATION,
        "CURRENT_REPOSITORY_HEAD": ENTRY_HEAD,
        "CURRENT_REPOSITORY_TREE": ENTRY_TREE,
        "GOVERNED_RUNTIME_CHECKOUT_HEAD": RUNTIME_HEAD,
        "GOVERNED_RUNTIME_CHECKOUT_TREE": RUNTIME_TREE,
        "CALLER_BINDING": {
            "caller_identity": "P11_ORCHESTRATION_CALLER_PRINCIPAL:2",
            "caller_role": "P11_ORCHESTRATION_CALLER_PRINCIPAL",
            "caller_uid": 2, "caller_gid": 2, "caller_groups": [4],
        },
        "ATTEMPT_BINDING": {"attempt_identity": ATTEMPT, "operation_attempt_limit": 1},
        "INPUT_BINDING": {
            "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
            "schema_version": "1.0.0",
            "record_kind": "P11_BOUNDED_CONSUMER_INPUT",
            "input_identity": "G77_256LM_E05_WRONG_SCOPE_BASELINE_INPUT_001",
            "attempt_identity": ATTEMPT,
            "caller_identity_reference": "P11_ORCHESTRATION_CALLER_PRINCIPAL:2",
            "contract_identity": "G77_256LM_E05_WRONG_SCOPE_FAIL_CLOSED_CONTRACT_V1",
            "contract_version": "1.0.0",
            "contract_content_sha256": "sha256:12819a6cb1a4b7f94146169e3c1879f7142006bc0c83d83f8f46038764792405",
            "provenance_identity": "G77_256LM_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1",
            "authorization_reference_state": "UNMATERIALIZED__REQUIRES_LATER_EXPLICIT_HUMAN_DECISION",
            "comparator_outcome": "FAILED_CLOSED",
            "comparator_outcome_identity": "G77_256LM_E05_WRONG_SCOPE_DENIAL_OUTCOME_001",
        },
        "CONTRACT_BINDING": {
            "contract_identity": "G77_256LM_E05_WRONG_SCOPE_FAIL_CLOSED_CONTRACT_V1",
            "contract_version": "1.0.0",
            "contract_content_sha256": "sha256:12819a6cb1a4b7f94146169e3c1879f7142006bc0c83d83f8f46038764792405",
        },
        "PROVENANCE_BINDING": {
            "provenance_identity": "G77_256LM_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1",
            "fm_owner_sha256": SOURCE_HASHES[FM_REL],
            "gl_orchestration_sha256": SOURCE_HASHES[GL_REL],
            "lg_adapter_sha256": SOURCE_HASHES[LG_REL],
            "ex_certificate_sha256": SOURCE_HASHES[next(p for p in SOURCE_HASHES if "G77_256EX" in p.name)],
            "nested_authenticated_head": NESTED_HEAD,
            "nested_authenticated_tree": NESTED_TREE,
            "nested_authenticated_tag": NESTED_TAG,
            "ll_terminal_commit": ENTRY_HEAD,
            "ll_terminal_tree": LL_TREE,
            "ll_authority_reused": False,
        },
        "EXPECTED_SCOPE": EXPECTED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_SCOPE_MISMATCH": {
            "independent_semantic_mutation_count": 1,
            "independent_semantic_mutation_field": "authority_scope",
            "expected": EXPECTED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "dependent_recomputation_fields": [
                "canonical_Human_act_content_identity", "CHE_source_act_digest",
                "CHE_correlation_identity",
            ],
        },
        "RECEIPT_PARENT_READINESS_EVIDENCE": {
            "context_sha256": context["context_sha256"],
            "context_file_sha256": sha256_path(CONTEXT),
            "receipt_parent": context["receipt_parent"],
            "observation_path": OBSERVATION.relative_to(ROOT).as_posix(),
            "observation_file_sha256": sha256_path(OBSERVATION),
            "observation_inner_sha256": receipt["observation_sha256"],
            "preparation_owner": GL.PREPARATION_OWNER,
            "validation_owner": GL.VALIDATION_OWNER,
            "readiness": "PASS__DURABLE_REAL_DIRECTORY__UNUSED__WRITABLE__EXACT_NAMESPACE",
            "authority_count": 0,
            "operational_execution_count": 0,
        },
        "CANDIDATE_HUMAN_ACT_MATERIAL": {
            "artifact_class": "HUMAN_ACT_SHAPED_REVIEW_MATERIAL__NONAUTHORITY",
            "candidate_material_id": "G77_256LM_WRONG_SCOPE_HUMAN_ACT_SHAPED_REVIEW_MATERIAL_001",
            "is_authority": False,
            "human_authority_source_bytes_state": "ABSENT",
            "human_actor_identity_state": "ABSENT",
            "authority_act_identity_state": "UNMATERIALIZED__REQUIRES_LATER_EXPLICIT_HUMAN_DECISION",
            "payload_digest_state": "UNMATERIALIZED",
            "proposed_authority_scope": PRESENTED_SCOPE,
            "proposed_operation_attempt_limit": 1,
            "proposed_retry_limit": 0,
        },
        "ONE_SHOT_LIMIT": {
            "authority_consumption_maximum_if_later_authorized": 1,
            "operation_attempt_maximum_if_later_authorized": 1,
        },
        "RETRY_LIMIT": 0,
        "AUTHORITY_STATE": "NONE",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_ENTRY_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "NEXT_ALLOWED_TRANSITION": "EXPLICIT_HUMAN_DECISION",
        "SEALED_PHASE": "PHASE_A__PREHUMAN__NONOPERATIONAL",
        "NOTICES": [
            "THIS OBJECT IS NOT AUTHORIZED",
            "APPROVAL HAS NOT YET BEEN GIVEN",
            "NO OPERATION MAY START FROM THIS GENERATION",
            "LL AUTHORITY IS TERMINAL AND MUST NOT BE REUSED",
            "A FUTURE OPERATIONAL ATTEMPT REQUIRES A FRESH EXPLICIT HUMAN DECISION",
            "INTELLIGENCE != AUTHORITY",
        ],
        "STATE_COUNTERS": zero_counters(),
        "E05": {"BEFORE": "12/18", "LM_CREDIT": 0, "AFTER": "12/18",
                "WRONG_SCOPE": "UNSAT__PHASE_A_READY__HUMAN_DECISION_PENDING__OPERATIONAL_UNPROVEN"},
    }


def cross_vector() -> list[dict[str, str]]:
    bindings = [
        ("WRONG_SCOPE", "UNSAT__PHASE_A_READY__OPERATIONAL_UNPROVEN", "AUTHORITY_SCOPE", "LL_OMITTED_EXISTING_RECEIPT_PREPARATION"),
        ("WRONG_CALLER", "SATISFIED__OPERATIONAL", "CALLER", "NONE"),
        ("WRONG_ATTEMPT", "SATISFIED__OPERATIONAL", "ATTEMPT", "NONE"),
        ("WRONG_INPUT", "SATISFIED__OPERATIONAL", "INPUT", "NONE"),
        ("WRONG_CONTRACT", "SATISFIED__OPERATIONAL", "CONTRACT", "NONE"),
        ("WRONG_PROVENANCE", "SATISFIED__OPERATIONAL", "PROVENANCE", "NONE"),
        ("FUTURE", "SATISFIED__OPERATIONAL", "TEMPORAL_FUTURE", "NONE"),
        ("EXPIRED", "SATISFIED__OPERATIONAL", "TEMPORAL_EXPIRED", "NONE"),
    ]
    return [{
        "VECTOR": vector, "E05_STATUS": status,
        "COMMON_INFRA_REUSABLE": "YES__DISCOVERY_AND_COMMON_MECHANISM_ONLY",
        "RECEIPT_PARENT_READINESS_MECHANISM": "GL_TO_EXISTING_FM_PREPARE_AND_VALIDATE_RECEIPT_PARENT",
        "VECTOR_SPECIFIC_BINDING": binding, "KNOWN_DEFECT": defect,
        "AUTHORITY_TRANSFER": "NO", "PROOF_TRANSFER": "NO",
        "E05_CREDIT_TRANSFER": "NO",
    } for vector, status, binding, defect in bindings]


def materialize(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    if repository["head"] != ENTRY_HEAD or remote_head != ENTRY_HEAD:
        raise LMVerificationError("LM_MATERIALIZATION_REQUIRES_EXACT_LL_ENTRY")
    if nested_remote_tag != NESTED_HEAD:
        raise LMVerificationError("NESTED_REMOTE_TAG_MISMATCH")
    targets = (CONTEXT, OBSERVATION, EQUIVALENCE, READINESS, ROOT_CAUSE,
               DECISION, PRESENTATION, REDUCTION)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise LMVerificationError("LM_ONE_SHOT_ARTIFACT_NAMESPACE_NOT_FRESH")
    if (LM / "operation_state").exists() or TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise LMVerificationError("LM_DERIVED_MATERIALIZATION_NAMESPACE_NOT_FRESH")

    context = FM.build_operation_context(
        repository_root=ROOT, repository_head=ENTRY_HEAD, repository_tree=ENTRY_TREE,
        generation_identity=GENERATION, operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX, operation_evidence_root=LM / "operation_state",
        transient_root=TRANSIENT, candidate_source_path=CANDIDATE_REL,
    )
    write_fresh(CONTEXT, context)
    materialization = FM.materialize_operation_state(
        repository_root=ROOT, context=context, context_source_path=CONTEXT,
        candidate_source_path=CANDIDATE_REL,
    )
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    static = FM.authority_free_static_readiness(
        repository_root=ROOT, context=context, observed_head=ENTRY_HEAD,
        observed_tree=ENTRY_TREE, repository_clean=True,
        observed_asset_sha256=observations, candidate_source_path=CANDIDATE_REL,
    )
    receipt = GL.prepare_and_observe_receipt_parent(ROOT, context)
    write_fresh(OBSERVATION, receipt)
    checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, receipt)
    equivalence = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, receipt, checkpoint
    )
    write_fresh(EQUIVALENCE, sealed(
        "G77_256LM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1", "proof",
        {"schema_id": "G77_256LM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
         "generation_identity": GENERATION, "operation_identity": OPERATION,
         **equivalence},
    ))
    readiness = sealed(
        "G77_256LM_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1", "checkpoint",
        {
            "schema_id": "G77_256LM_PREAUTHORITY_STATIC_READINESS_V1",
            "artifact_class": "SEALED_PHASE_A_READINESS__NONAUTHORITY__NONOPERATIONAL",
            "entry": {"head": ENTRY_HEAD, "tree": ENTRY_TREE,
                      "remote_head": remote_head, "branch": BRANCH},
            "generation_identity": GENERATION, "operation_identity": OPERATION,
            "context_sha256": context["context_sha256"],
            "context_file_sha256": sha256_path(CONTEXT),
            "materialization": materialization, "static_readiness": static,
            "receipt_parent_observation_sha256": receipt["observation_sha256"],
            "receipt_parent_equivalence": equivalence["preauth_final_admission_equivalence"],
            "authority_state": "NONE", "human_decision_state": "PENDING",
            "operational_counters": zero_counters(),
        },
    )
    write_fresh(READINESS, readiness)
    root_cause = sealed(
        "G77_256LM_RECEIPT_PARENT_ROOT_CAUSE_ENVELOPE_V1", "analysis",
        root_cause_fact(),
    )
    write_fresh(ROOT_CAUSE, root_cause)
    decision = build_decision(context, receipt)
    decision_envelope = sealed(
        "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_ENVELOPE_V1",
        "decision_object", decision,
    )
    write_fresh(DECISION, decision_envelope)
    presentation = (
        "G77-256LM WRONG_SCOPE PHASE-A HUMAN REVIEW PRESENTATION\n\n"
        "THIS OBJECT IS NOT AUTHORIZED.\n"
        "APPROVAL HAS NOT YET BEEN GIVEN.\n"
        "NO OPERATION MAY START FROM THIS GENERATION.\n"
        "LL AUTHORITY IS TERMINAL AND MUST NOT BE REUSED.\n"
        "A FUTURE OPERATIONAL ATTEMPT REQUIRES A FRESH EXPLICIT HUMAN DECISION.\n\n"
        f"DECISION_OBJECT_ID = {DECISION_ID}\n"
        f"CANONICAL_OPERATION_ID = {OPERATION}\n"
        f"DECISION_OBJECT_PATH = {DECISION.relative_to(ROOT).as_posix()}\n"
        f"DECISION_OBJECT_WHOLE_FILE_SHA256 = {sha256_path(DECISION)}\n"
        f"DECISION_OBJECT_CANONICAL_INNER_SHA256 = {decision_envelope['decision_object_sha256']}\n"
        f"EXPECTED_SCOPE = {EXPECTED_SCOPE}\n"
        f"PRESENTED_SCOPE = {PRESENTED_SCOPE}\n"
        "INDEPENDENT_SEMANTIC_MISMATCH = authority_scope only\n"
        f"RECEIPT_PARENT = {context['receipt_parent']}\n"
        f"RECEIPT_PARENT_OBSERVATION_SHA256 = {receipt['observation_sha256']}\n"
        "AUTHORITY_STATE = NONE\nOPERATION_STATE = NOT_STARTED\n"
        "HUMAN_DECISION_STATE = PENDING\nNEXT_ALLOWED_TRANSITION = EXPLICIT_HUMAN_DECISION\n"
        "READY_FOR_HUMAN_DECISION = YES\n"
    )
    write_fresh(PRESENTATION, presentation)
    reduction_inner = {
        "schema_id": "G77_256LM_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256LM", "vector": "WRONG_SCOPE", "terminal": TERMINAL,
        "entry": repository, "ll_terminal_immutable": True,
        "ll_authority": {"state": "GRANTED_UNCONSUMED__TERMINATED_BY_LL_STOP__REUSE_NOT_AUTHORIZED",
                         "reused": False, "transfer": "NO"},
        "root_cause": root_cause["analysis"],
        "decision_object": {"count": 1, "id": DECISION_ID,
            "whole_file_sha256": sha256_path(DECISION),
            "canonical_inner_sha256": decision_envelope["decision_object_sha256"]},
        "receipt_parent": {"path": context["receipt_parent"],
            "observation_file_sha256": sha256_path(OBSERVATION),
            "observation_inner_sha256": receipt["observation_sha256"],
            "equivalence_file_sha256": sha256_path(EQUIVALENCE),
            "owner": GL.PREPARATION_OWNER, "readiness": "PASS"},
        "frontier": {
            "LAST_VERIFIED_EDGE": "FRESH_EXACT_WRONG_SCOPE_PHASE_A_OBJECT_WITH_DURABLE_RECEIPT_PARENT_READINESS",
            "FIRST_BROKEN_EDGE": "NONE_WITHIN_LM_AUTHORITY_FREE_PHASE_A_SCOPE",
            "FIRST_UNVERIFIED_EDGE": "EXPLICIT_HUMAN_DECISION_THEN_ONE_WRONG_SCOPE_OPERATIONAL_DENIAL",
            "MINIMUM_MISSING_CAPABILITY": "NONE__EXISTING_RECEIPT_PARENT_MATERIALIZATION_MECHANISM_REUSED",
            "MINIMUM_MISSING_PROOF": "OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY",
            "MINIMUM_LEGAL_NEXT_DELTA": "STOP__AWAIT_ONE_FRESH_EXPLICIT_HUMAN_DECISION",
        },
        "architecture": {"PRODUCTION_MUTATION": 0, "P11_MUTATION": 0,
            "ER_MUTATION": 0, "EX_MUTATION": 0, "NEW_OWNER": 0,
            "NEW_ROUTE": 0, "NEW_REGISTRY": 0, "NEW_GENERIC_ABSTRACTION": 0,
            "NEW_CONSTITUTIONAL_CONCEPT": 0, "ROUTE_COUNT_BEFORE": 1,
            "ROUTE_COUNT_AFTER": 1},
        "cross_vector_reuse_assessment": cross_vector(),
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "FM_OPERATION_MATERIALIZATION__GL_FM_RECEIPT_PARENT_OWNER__LG_LE_WRONG_SCOPE__LJ_STABLE_CHECKOUT__EX_17_OF_17",
            "new_capabilities": "NONE__ONE_GENERATION_LOCAL_LIFECYCLE_INSTANCE",
            "existing_capability_unreachable": False, "parallel_flow": False,
            "production_route_effect": "UNCHANGED__1_TO_1",
        },
        "e05": {"BEFORE": "12/18", "LM_CREDIT": 0, "AFTER": "12/18",
                "WRONG_SCOPE": "UNSAT__OPERATIONAL_PROOF_NOT_PERFORMED"},
        "ex": {"REUSED": "VERIFIED__17_OF_17", "RECONSTRUCTED": "VERIFIED__0"},
        "operational_counters": zero_counters(),
        "phase_a": {"authority_state": "NONE", "operation_state": "NOT_STARTED",
                    "human_decision_state": "PENDING", "ready_for_human_decision": True,
                    "independent_semantic_mismatch_count": 1},
    }
    write_fresh(REDUCTION, sealed(
        "G77_256LM_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction",
        reduction_inner,
    ))
    return verify()


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    context = load_canonical(CONTEXT)
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    if (
        context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or context.get("identity_namespace_prefix") != PREFIX
        or context.get("repository_head") != ENTRY_HEAD
        or context.get("repository_tree") != ENTRY_TREE
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"].get("head") != RUNTIME_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"].get("tree") != RUNTIME_TREE
    ):
        raise LMVerificationError("CONTEXT_BINDING_MISMATCH")
    receipt = load_canonical(OBSERVATION)
    GL.validate_bound_observation(ROOT, context, receipt)
    checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, receipt)
    equivalence = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, receipt, checkpoint
    )
    if equivalence["preauth_final_admission_equivalence"] != GL.EQUIVALENCE_RESULT:
        raise LMVerificationError("RECEIPT_PARENT_EQUIVALENCE_MISMATCH")
    # Preserve the LJ separation: the sealed materialization base is historical
    # after an evidence commit, while repository authentication requires only an
    # advancing descendant.  Replaying FM.authority_free_static_readiness here
    # would incorrectly substitute current-admission identity for the sealed
    # base and recreate the rejected LI literal HEAD/TREE loop.
    readiness_envelope = load_canonical(READINESS)
    readiness = readiness_envelope.get("checkpoint")
    if (
        not isinstance(readiness, dict)
        or readiness_envelope.get("checkpoint_sha256")
        != sha256_bytes(canonical_bytes(readiness))
        or readiness.get("context_sha256") != context["context_sha256"]
        or readiness.get("context_file_sha256") != sha256_path(CONTEXT)
        or readiness.get("entry", {}).get("head") != ENTRY_HEAD
        or readiness.get("entry", {}).get("tree") != ENTRY_TREE
        or readiness.get("static_readiness", {}).get("result")
        != "STATIC_READINESS_PASS"
        or any(readiness.get("operational_counters", {}).values())
    ):
        raise LMVerificationError("SEALED_ENTRY_BASE_READINESS_MISMATCH")
    freshness = FM.fresh_context.validate_freshness(
        context, overlay_materialized=True
    )
    checkout = FM.validate_checkout_preboot_readiness(context)
    visibility = FM.validate_preboot_visibility(
        ROOT, context, context["canonical_argv"], context["canonical_argv_sha256"],
        candidate_source_path=CANDIDATE_REL,
    )
    adapter = FM.prove_guest_adapter_binding(ROOT, context)
    if (
        not freshness
        or checkout.get("checkout_head_tree") != "PASS"
        or visibility.get("result") != "PREBOOT_VISIBILITY_COMPOSITION_PASS"
        or not adapter
    ):
        raise LMVerificationError("STABLE_MATERIALIZATION_REPLAY_FAILED")
    root_cause = load_canonical(ROOT_CAUSE)
    if root_cause.get("analysis_sha256") != sha256_bytes(canonical_bytes(root_cause["analysis"])):
        raise LMVerificationError("ROOT_CAUSE_SEAL_MISMATCH")
    if root_cause["analysis"] != root_cause_fact():
        raise LMVerificationError("ROOT_CAUSE_FACT_MISMATCH")
    envelope = load_canonical(DECISION)
    decision = envelope.get("decision_object")
    if (
        not isinstance(decision, dict)
        or envelope.get("decision_object_sha256") != sha256_bytes(canonical_bytes(decision))
        or decision.get("DECISION_OBJECT_ID") != DECISION_ID
        or decision.get("CANONICAL_OPERATION_ID") != OPERATION
        or decision.get("EXPECTED_SCOPE") != EXPECTED_SCOPE
        or decision.get("PRESENTED_SCOPE") != PRESENTED_SCOPE
        or decision.get("AUTHORITY_STATE") != "NONE"
        or decision.get("OPERATION_STATE") != "NOT_STARTED"
        or decision.get("P11_ENTRY_STATE") != "NOT_ENTERED"
        or decision.get("PROTECTED_EFFECT_STATE") != "NONE"
        or decision.get("HUMAN_DECISION_STATE") != "PENDING"
        or decision.get("NEXT_ALLOWED_TRANSITION") != "EXPLICIT_HUMAN_DECISION"
        or any(decision.get("STATE_COUNTERS", {}).values())
    ):
        raise LMVerificationError("DECISION_OBJECT_BINDING_MISMATCH")
    mismatch = decision.get("ISOLATED_SCOPE_MISMATCH", {})
    if mismatch.get("independent_semantic_mutation_count") != 1 or mismatch.get(
        "independent_semantic_mutation_field"
    ) != "authority_scope":
        raise LMVerificationError("MULTIPLE_OR_WRONG_SEMANTIC_MISMATCH")
    receipt_binding = decision.get("RECEIPT_PARENT_READINESS_EVIDENCE", {})
    if (
        receipt_binding.get("observation_file_sha256") != sha256_path(OBSERVATION)
        or receipt_binding.get("observation_inner_sha256") != receipt["observation_sha256"]
        or receipt_binding.get("receipt_parent") != context["receipt_parent"]
    ):
        raise LMVerificationError("DECISION_RECEIPT_READINESS_BINDING_MISMATCH")
    historical = subprocess.run(
        ["git", "grep", "-F", DECISION_ID, ENTRY_HEAD], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if historical.returncode == 0 or len(list(LM.glob("*DECISION_OBJECT*.json"))) != 1:
        raise LMVerificationError("DECISION_FRESHNESS_OR_COUNT_MISMATCH")
    presentation = PRESENTATION.read_text(encoding="utf-8")
    required_notices = (
        "THIS OBJECT IS NOT AUTHORIZED.", "APPROVAL HAS NOT YET BEEN GIVEN.",
        "NO OPERATION MAY START FROM THIS GENERATION.",
        "LL AUTHORITY IS TERMINAL AND MUST NOT BE REUSED.",
        "A FUTURE OPERATIONAL ATTEMPT REQUIRES A FRESH EXPLICIT HUMAN DECISION.",
        sha256_path(DECISION), envelope["decision_object_sha256"],
        "READY_FOR_HUMAN_DECISION = YES",
    )
    if not all(value in presentation for value in required_notices):
        raise LMVerificationError("HUMAN_PRESENTATION_INCOMPLETE")
    reduction = load_canonical(REDUCTION)
    inner = reduction.get("reduction")
    if (
        not isinstance(inner, dict)
        or reduction.get("reduction_sha256") != sha256_bytes(canonical_bytes(inner))
        or inner.get("terminal") != TERMINAL
        or any(inner.get("operational_counters", {}).values())
        or inner.get("decision_object", {}).get("count") != 1
        or not inner.get("phase_a", {}).get("ready_for_human_decision")
    ):
        raise LMVerificationError("TERMINAL_REDUCTION_MISMATCH")
    return {
        "terminal": TERMINAL, "repository": repository,
        "decision_object_whole_file_sha256": sha256_path(DECISION),
        "decision_object_canonical_inner_sha256": envelope["decision_object_sha256"],
        "receipt_parent": context["receipt_parent"],
        "receipt_parent_ready": True, "authority_creation_count": 0,
        "authority_consumption_count": 0, "operation_attempt_count": 0,
        "p11_entry_count": 0, "protected_effect_count": 0,
        "ready_for_human_decision": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    parser.add_argument("--remote-head")
    parser.add_argument("--nested-remote-tag")
    args = parser.parse_args()
    if args.materialize:
        if not args.remote_head or not args.nested_remote_tag:
            raise LMVerificationError("DIRECT_REMOTE_IDENTITIES_REQUIRED")
        result = materialize(args.remote_head, args.nested_remote_tag)
    else:
        result = verify()
    print(result["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
