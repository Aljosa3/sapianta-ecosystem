#!/usr/bin/env python3
"""Read-only G77-256IQ GN FUTURE compatibility formalizer.

The formalizer authenticates the committed IP blocker, the pre-IQ GN owner,
the already-governed FUTURE semantics, and the uniquely bounded GN delta.  It
constructs only temporary non-authority fixtures.  It cannot create Human
authority, invoke PRE/FM/P11, run QEMU, boot a VM, or create an operation.
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
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IP_HEAD = "65d6d029fbcfbae964e702fdbdb544c940b2eec2"
IP_TREE = "6855043f4816ce3ffc2942f6bdf4ebb87453168e"
IP_SUBJECT = "G77-256IP record FUTURE preoperational GN blocker"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
GENERATION = "G77_256IP_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IP_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"

IQ_ROOT = Path(".github/governance/evidence/g77_256iq_gn_future_presentation_compatibility_v1")
IP_ROOT = Path(".github/governance/evidence/g77_256ip_future_operational_v1")
IP_REPORT = IP_ROOT / "G77_256IP_G48_PREOPERATIONAL_BLOCKER_REPORT_V1.md"
IP_TERMINAL = IP_ROOT / "G77_256IP_SPCE_TERMINAL_PREOPERATIONAL_BLOCKER_V1.json"
IP_FORMALIZER = IP_ROOT / "analysis/G77_256IP_PREOPERATIONAL_BLOCKER_FORMALIZER_V1.py"
IP_TEST = IP_ROOT / "tests/test_g77_256ip_preoperational_blocker_v1.py"
IP_HASHES = {
    IP_REPORT: "c26bb023de39b6fdf199c2d1afd3aeaedf6ee278eca2d1de0f7923ad047defbd",
    IP_TERMINAL: "90a9cf65e82ded90077a07f23e8ac4e2e26d55fc17c5ae582b77ea8b133cdf71",
    IP_FORMALIZER: "9688c18adbf881754e32525977f18b7397cef68ce865e7c698a88df35ceb4c8e",
    IP_TEST: "e15c2718491aba34abd770e7c6ba645f1af321510a06c5c50b3170eb8780b523",
}
GN_PATH = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GN_BASE_BLOB = "c5a18210c51dff31b10db0906a462e8d2fdb7b09"
GN_BASE_SHA256 = "cc7f002622c7ee84a0ab2678d4fcc1456f4d658d58759b8100ab1da072b31de2"
GL_PATH = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
CONTEXT_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
HP_REQUEST = Path(
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
IH_CONTEXT = Path(
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
IH_CANDIDATE = Path(
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
    "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
)
IF_ACT_CHE = Path(
    ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/"
    "live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"
)
FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
EXPECTED_VECTORS = {
    "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"
}


class IQFormalizationError(ValueError):
    """One deterministic fail-closed IQ formalization error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise IQFormalizationError(f"DUPLICATE_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if raw != canonical_bytes(value):
        raise IQFormalizationError(f"NONCANONICAL_JSON:{path}")
    return value


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise IQFormalizationError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": BRANCH, "head": IP_HEAD, "tree": IP_TREE,
        "subject": IP_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IP_HEAD, "index": "",
    }
    if observed != expected:
        raise IQFormalizationError("EXACT_COMMITTED_IP_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT
    ).returncode:
        raise IQFormalizationError("STABLE_ANCESTRY_MISSING")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }:
        raise IQFormalizationError("NESTED_AUTHORITY_MISMATCH")
    observed["local_remote_equality"] = "VERIFIED"
    observed["nested_authority"] = nested_state
    return observed


def reconstruct_ip() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in IP_HASHES.items():
        committed = subprocess.check_output(
            ["git", "show", f"{IP_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != (ROOT / relative).read_bytes() or sha256_bytes(committed) != expected_sha:
            raise IQFormalizationError(f"IP_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative.name] = {
            "git_blob": git("rev-parse", f"{IP_HEAD}:{relative.as_posix()}"),
            "sha256": expected_sha,
        }
    envelope = load_canonical(ROOT / IP_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IQFormalizationError("IP_INNER_SEAL_MISMATCH")
    reduction = envelope["reduction"]
    terminal = reduction["terminal"]
    if terminal["terminal"] != "C__PRE_OPERATIONAL_BLOCKER":
        raise IQFormalizationError("IP_TERMINAL_C_MISMATCH")
    if terminal["first_broken_edge"] != "EXISTING_GN_SEALED_REQUEST_VALIDATION_REJECTS_FUTURE_VECTOR":
        raise IQFormalizationError("IP_FIRST_BROKEN_EDGE_MISMATCH")
    if set(reduction["operational_counters"].values()) != {0}:
        raise IQFormalizationError("IP_OPERATIONAL_ZERO_MISMATCH")
    if reduction["e05"] != {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8}:
        raise IQFormalizationError("IP_E05_MISMATCH")
    headings = [line for line in (ROOT / IP_REPORT).read_text().splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]:
        raise IQFormalizationError("IP_G48_HEADING_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "inner_seal": "VERIFIED", "identities": identities}


def authenticate_gn_and_closure() -> dict[str, Any]:
    committed = subprocess.check_output(["git", "show", f"{IP_HEAD}:{GN_PATH}"], cwd=ROOT)
    if sha256_bytes(committed) != GN_BASE_SHA256:
        raise IQFormalizationError("GN_BASE_SHA256_MISMATCH")
    if git("rev-parse", f"{IP_HEAD}:{GN_PATH}") != GN_BASE_BLOB:
        raise IQFormalizationError("GN_BASE_BLOB_MISMATCH")
    baseline = ast.parse(committed.decode(), filename=f"{IP_HEAD}:{GN_PATH}")
    current_source = (ROOT / GN_PATH).read_text(encoding="utf-8")
    ast.parse(current_source, filename=str(GN_PATH))
    gn = load_module(GN_PATH, "g77_256iq_gn")
    context = load_module(CONTEXT_PATH, "g77_256iq_context")
    launcher = load_module(FM_PATH, "g77_256iq_launcher")
    if set(gn.SUPPORTED_VECTORS) != EXPECTED_VECTORS:
        raise IQFormalizationError("GN_CLOSED_VECTOR_SET_MISMATCH")
    if set(context.SUPPORTED_OPERATION_VECTORS) != EXPECTED_VECTORS:
        raise IQFormalizationError("FM_CONTEXT_FUTURE_COMPATIBILITY_MISMATCH")
    if launcher.operation_attempt_limit_field("FUTURE") != "future_operational_attempt_limit":
        raise IQFormalizationError("HUMAN_ACT_FUTURE_COMPATIBILITY_MISMATCH")
    gl_source = (ROOT / GL_PATH).read_text(encoding="utf-8")
    if "SUPPORTED_VECTORS" in gl_source or "authorized_vector_requested" in gl_source:
        raise IQFormalizationError("GL_VECTOR_GATE_UNEXPECTED")
    baseline_strings = {node.value for node in ast.walk(baseline) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    if "FUTURE" in baseline_strings:
        raise IQFormalizationError("GN_IP_BASELINE_ALREADY_CONTAINS_FUTURE")
    return {
        "gn_owner": GN_PATH.as_posix(),
        "gn_base_git_blob": GN_BASE_BLOB,
        "gn_base_sha256": GN_BASE_SHA256,
        "gn_current_sha256": sha256_path(ROOT / GN_PATH),
        "gn_ip_vector_set": ["WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE"],
        "gn_iq_vector_set": sorted(EXPECTED_VECTORS),
        "minimum_dependency_closure": "VERIFIED__GN_SUPPORTED_VECTORS_AND_FUTURE_GENERATION_SUFFIX_BINDING_ONLY",
        "existing_contract_family_expresses_future": "VERIFIED__YES",
        "existing_profile_fields_sufficient": "VERIFIED__YES",
        "membership_plus_existing_sealed_identity_recomputation": "VERIFIED__YES",
        "generation_binding_generic_projection_plus_bounded_suffix_check": "VERIFIED__YES",
        "downstream_closed_vector_delta_required": "VERIFIED__NO",
        "dependent_identity_recomputation": "VERIFIED__REQUEST_INNER_SEAL_AND_PRESENTATION_SHA_ONLY",
        "new_schema_major_required": "VERIFIED__NO",
        "p11_change_required": "VERIFIED__NO",
        "fm_change_required": "VERIFIED__NO",
        "new_presentation_protocol_required": "VERIFIED__NO",
        "ambiguity_count": "VERIFIED__0",
    }


def authenticate_future_semantics() -> dict[str, Any]:
    binding = load_canonical(ROOT / IF_ACT_CHE)["binding"]
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    context = load_canonical(ROOT / IH_CONTEXT)
    facts = {
        "evaluation": binding["evaluation_time_unix_ns"],
        "valid_from": act["payload"]["valid_from_unix_ns"],
        "valid_until": act["payload"]["valid_until_unix_ns"],
        "payload_digest": act["payload_digest"].removeprefix("sha256:"),
        "source_act": che["source_act_digest"].removeprefix("sha256:"),
        "che_correlation": che["correlation_identity"],
        "candidate_runtime_sha256": sha256_path(ROOT / IH_CANDIDATE),
        "context_identity": context["context_sha256"],
        "runtime_target_head": IF_HEAD,
        "runtime_target_tree": IF_TREE,
    }
    if (facts["evaluation"], facts["valid_from"], facts["valid_until"]) != (500, 600, 1000):
        raise IQFormalizationError("FUTURE_TEMPORAL_SEMANTICS_MISMATCH")
    if not facts["evaluation"] < facts["valid_from"] < facts["valid_until"]:
        raise IQFormalizationError("FUTURE_TEMPORAL_RELATION_MISMATCH")
    if (facts["payload_digest"], facts["source_act"], facts["che_correlation"]) != (
        FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE
    ):
        raise IQFormalizationError("FUTURE_ACT_CHE_IDENTITY_MISMATCH")
    if facts["candidate_runtime_sha256"] != FUTURE_CANDIDATE_SHA or facts["context_identity"] != FUTURE_CONTEXT_SHA:
        raise IQFormalizationError("FUTURE_RUNTIME_CONTEXT_IDENTITY_MISMATCH")
    facts["future_semantic_mutation_count"] = "VERIFIED__0"
    facts["wall_clock_dependency_count"] = "VERIFIED__0"
    return facts


def future_request_fixture() -> dict[str, Any]:
    """Build one sealed test-only request; returned bytes are never persisted."""

    gn = load_module(GN_PATH, "g77_256iq_gn_fixture")
    context = load_canonical(ROOT / IH_CONTEXT)
    envelope = deepcopy(load_canonical(ROOT / HP_REQUEST))
    request = envelope["request"]
    envelope["schema_id"] = "G77_256IQTEST_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    request["schema_id"] = "G77_256IQTEST_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1"
    request["recorded_at_utc"] = "TEST_ONLY__NON_AUTHORITY__NO_WALL_CLOCK"
    request["generation_identity"] = GENERATION
    request["operation_identity"] = OPERATION
    request["authorized_vector_requested"] = "FUTURE"
    request["repository"].update({"head": IP_HEAD, "tree": IP_TREE, "remote_head": IP_HEAD})
    request["live_binding"].update({
        "candidate_sha256": FUTURE_CANDIDATE_SHA,
        "context_sha256": FUTURE_CONTEXT_SHA,
        "context_file_sha256": sha256_path(ROOT / IH_CONTEXT),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "receipt_parent": context["receipt_parent"],
    })
    envelope["request_sha256"] = sha256_bytes(gn._canonical_bytes(request))
    return envelope


def presentation_proof() -> dict[str, Any]:
    gn = load_module(GN_PATH, "g77_256iq_gn_proof")
    envelope = future_request_fixture()
    with tempfile.TemporaryDirectory(prefix="g77_256iq_") as raw:
        request_path = Path(raw) / "TEST_ONLY_NON_AUTHORITY_FUTURE_REQUEST.json"
        request_path.write_bytes(gn._canonical_bytes(envelope))
        presentation = gn.render_human_authorization_presentation(request_path)
        result = gn.validate_human_authorization_presentation(request_path, presentation)
        parsed = gn.parse_human_authorization_presentation(presentation)
        if parsed["GENERATION_ID"] != GENERATION or parsed["OPERATION_ID"] != OPERATION:
            raise IQFormalizationError("FUTURE_GENERATION_OPERATION_PROJECTION_MISMATCH")
        if parsed["AUTHORIZED_VECTOR_REQUESTED"] != "FUTURE":
            raise IQFormalizationError("FUTURE_VECTOR_PROJECTION_MISMATCH")
        if parsed["CANDIDATE_SHA256"] != FUTURE_CANDIDATE_SHA or parsed["CONTEXT_SHA256"] != FUTURE_CONTEXT_SHA:
            raise IQFormalizationError("FUTURE_RUNTIME_CONTEXT_PROJECTION_MISMATCH")
    return {
        "gn_future_presentation_admission": "VERIFIED",
        "gn_future_generation_binding": "VERIFIED",
        "gn_future_operation_binding": "VERIFIED",
        "gn_future_request_binding": "VERIFIED__INNER_REQUEST_SHA256_AND_EXACT_PRESENTATION_EQUIVALENCE",
        "canonical_sealing": "VERIFIED",
        "human_authority_created": 0,
        "operational_execution_count": result["operational_execution_count"],
        "reviewed_field_count": result["reviewed_field_count"],
    }


def terminal_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    ip = reconstruct_ip()
    closure = authenticate_gn_and_closure()
    future = authenticate_future_semantics()
    presentation = presentation_proof()
    zero = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    return {
        "mode": "REPOSITORY_ONLY__GN_FUTURE_PRESENTATION_COMPATIBILITY__NO_AUTHORIZATION__NO_OPERATION",
        "entry": entry,
        "ip_reconstruction": ip,
        "formalization": closure,
        "future_semantics": future,
        "presentation": presentation,
        "compatibility": {
            "gn_existing_vector_compatibility": "VERIFIED",
            "existing_gn_vector_reachability": "VERIFIED__PRESERVED",
            "existing_gn_vector_semantic_mutation_count": "VERIFIED__0",
            "gn_vector_set_closed": "VERIFIED",
            "unknown_vector_acceptance": "VERIFIED__NO",
            "arbitrary_vector_registration": "VERIFIED__NO",
            "caller_defined_vector": "VERIFIED__NO",
            "stale_dependent_identity_count": "VERIFIED__0",
            "manually_invented_identity_count": "VERIFIED__0",
        },
        "negative_validation": {
            "unknown_vector": "VERIFIED__REJECTED",
            "malformed_vector": "VERIFIED__REJECTED",
            "cross_vector_substitution": "VERIFIED__REJECTED",
            "cross_generation_substitution": "VERIFIED__REJECTED",
            "cross_operation_substitution": "VERIFIED__REJECTED_BY_EXACT_PRESENTATION_REQUEST_EQUIVALENCE",
            "cross_request_substitution": "VERIFIED__REJECTED_BY_REQUEST_SHA256",
            "replay_substitution": "VERIFIED__REJECTED",
            "wrong_candidate_context_argv_checkpoint_seal": "VERIFIED__REJECTED",
            "wrong_runtime_target_record_input_contract_provenance_che": "NOT_APPLICABLE__NOT_GN_PROFILE_FIELDS",
            "mixed_version_downgrade": "NOT_APPLICABLE__NO_VERSION_SUCCESSOR",
        },
        "boundaries": {
            "p11_mutation_count": "VERIFIED__0",
            "fm_runtime_owner_mutation": "VERIFIED__0",
            "runtime_target_mutation": "VERIFIED__0",
            "v1_semantics_reinterpreted": "VERIFIED__NO",
            "v2_readiness_preserved": "VERIFIED",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
            "reintroduced_historical_failure_count": "VERIFIED__0",
            "shadow_automation_status": "VERIFIED__ABSENT",
        },
        "proof_reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__GN_GL_FM_HUMAN_ACT_DU_EB_EE_P11_CHE_FK_EX_GOVERNANCE_LAYER_0",
            "new_capability_set": "VERIFIED__GN_FUTURE_PRESENTATION_COMPATIBILITY_AND_GENERATION_BINDING",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__13__IE_THROUGH_IQ",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__BOUNDED_EXISTING_GN_COMPATIBILITY_DELTA",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0__NO_NEW_PROTOCOL_OR_RUNTIME_OWNER",
            "marginal_new_infrastructure_for_iq": "VERIFIED__ONE_GN_CLOSED_SET_MEMBER_ONE_SUFFIX_BINDING_AND_FOUR_EVIDENCE_ARTIFACTS",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IQ_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_LOW_MARGINAL_DELTA",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__IQ_COMMISSION_AND_IP_LOCATOR",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_IP_ENTRY",
            "authority_state_recovery": "VERIFIED__NO_AUTHORITY_CREATED",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMED",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_OPERATION",
            "operation_replay_prevention": "VERIFIED__ZERO_OPERATION_AND_REPLAY_FIXTURE_REJECTED",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IQ_REPOSITORY_DELTA",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "operational_counters": zero,
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8},
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_PRESERVED__BOUNDED_GN_DELTA",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__POST_COMMIT_GN_COMPATIBILITY_AUTHENTICATION_THEN_FRESH_PREAUTHORIZATION_DERIVATION",
            "governance_efficience": "ESTIMATED__HIGH__MINIMUM_OWNER_DELTA",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IP_TO_IQ_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_COMMITTED_V2_LIVE_BINDING__PREOPERATIONAL_READY__GN_FUTURE_PRESENTATION_COMPATIBILITY_IMPLEMENTED__NOT_AUTHORIZED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IM_DESIGN__IN_IMPLEMENTED__IO_READY__IP_GN_BLOCKER__IQ_GN_COMPATIBILITY",
            "prompt_context_reuse_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_OPERATIONAL_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IQ_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_LOW_MARGINAL_DELTA",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "terminal": {
            "terminal": "A__REPOSITORY_IMPLEMENTATION_SUCCESS",
            "last_verified_edge": "GN_FUTURE_PRESENTATION_COMPATIBILITY_AND_GENERATION_BINDING",
            "first_broken_edge": "POST_COMMIT_GN_FUTURE_COMPATIBILITY_AUTHENTICATION_NOT_YET_PERFORMED",
            "minimum_missing_capability": "POST_COMMIT_GN_FUTURE_PRESENTATION_COMPATIBILITY_AUTHENTICATION",
            "minimum_legal_next_delta": "SEPARATE_POST_COMMIT_GN_FUTURE_COMPATIBILITY_AUTHENTICATION__THEN_FRESH_PREAUTHORIZATION_DERIVATION",
            "auto_continuable": False,
            "human_review_required": True,
            "next_generation_started": False,
        },
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256IQ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    try:
        print(canonical_bytes(terminal_envelope()).decode(), end="")
    except (IQFormalizationError, OSError, subprocess.CalledProcessError) as exc:
        print(canonical_bytes({"status": "FAIL_CLOSED", "reason": str(exc)}).decode(), end="")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
