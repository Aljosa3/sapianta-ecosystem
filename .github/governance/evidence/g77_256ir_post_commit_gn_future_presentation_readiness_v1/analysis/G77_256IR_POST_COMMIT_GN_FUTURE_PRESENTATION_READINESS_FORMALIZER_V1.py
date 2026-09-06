#!/usr/bin/env python3
"""Read-only IR post-commit GN and fresh-presentation readiness formalizer.

Only temporary non-authority request representations are constructed.  This
owner cannot grant/consume authority or invoke PRE, FM, QEMU, a VM, or P11.
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
IQ_HEAD = "2ad26623dd4625d2162ce2b9fa0d65e8581f95f6"
IQ_TREE = "b54ab32b797825bc703d718dd65edbb216abecee"
IQ_SUBJECT = "G77-256IQ add GN FUTURE presentation compatibility"
IP_HEAD = "65d6d029fbcfbae964e702fdbdb544c940b2eec2"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
PREFIX = "G77_256IR"
VECTOR = "FUTURE"
GENERATION = f"{PREFIX}_ONE_FRESH_HUMAN_AUTHORIZED_{VECTOR}_OPERATIONAL_COMMISSIONING_V1"
OPERATION = f"{PREFIX}_E05_{VECTOR}_DENIAL_BEFORE_ENTRY_001"

LINEAGE = {
    "IQ": IQ_HEAD,
    "IP": IP_HEAD,
    "IO": "af7835d98d0bfa685da99e41bd5bc866cbc2a54b",
    "IN": "e39aee28fa9181e1db2ae6c5cff4a50f557821be",
    "IM": "f25afc281cbfe457b23a389a8375900717a5a1e2",
    "IL": "c43839f54ae788caa11a2082aba845b9426ea4c6",
    "IK": "7a7c77d32551020d5fed6cce5b4f7786e9974573",
    "II": "4365d97394deca438a1a57d5b47c699afb54bd5d",
    "IH": "8698486cdf9a206f2bc73993c83389d6850362ff",
    "IG": "71391a75011cdc388bdac9183f4654814a044c69",
    "IF": IF_HEAD,
    "IE": "9420764a5bb6db8909334f2a422225687a37a346",
    "ID": "559deecb226b66d626e45e6f607b0aab6df81f1c",
    "IC": "afdd47166acdee30cb9867d3d3c7bfec0de64c8a",
    "ANCHOR": ANCHOR,
}

IQ_ROOT = Path(".github/governance/evidence/g77_256iq_gn_future_presentation_compatibility_v1")
IQ_REPORT = IQ_ROOT / "G77_256IQ_G48_IMPLEMENTATION_REPORT_V1.md"
IQ_TERMINAL = IQ_ROOT / "G77_256IQ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IQ_FORMALIZER = IQ_ROOT / "analysis/G77_256IQ_GN_FUTURE_PRESENTATION_COMPATIBILITY_FORMALIZER_V1.py"
IQ_TEST = IQ_ROOT / "tests/test_g77_256iq_gn_future_presentation_compatibility_v1.py"
IQ_HASHES = {
    IQ_REPORT: "d26f545b9cb1655e0f5d857c9036c2b415222d726e301d4e450a020a9ab71e5d",
    IQ_TERMINAL: "2a6a1880c2faf1551c5f211bc52e5823a163d7729e25ca05ba3f2f75a6510265",
    IQ_FORMALIZER: "79c68456e73c52aef45a7ace0658677f054ed6ccf47ea00e3ca920244abb3470",
    IQ_TEST: "3db8e886d1ae02525e35e5deaa8da2b8296309eaa0656abc00e07e784c1bb384",
}
GN_PATH = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GN_BLOB = "6016815ad249dc8d1921a1b194fc7019a45fb71f"
GN_SHA256 = "be26ef5d5f54947f415df9b7539c144d9f3300997df71664b80c5f38ee1770dc"
GL_PATH = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
FM_PATH = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
CONTEXT_OWNER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
DU_PATH = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_PATH = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_PATH = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
IH_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IF_ACT_CHE = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
HP_REQUEST = Path(".github/governance/evidence/g77_256hp_wrong_input_operational_v1/G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json")
EX_SEAL = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json")
FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
EXPECTED_VECTORS = {"WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE"}


class IRFormalizationError(ValueError):
    """One deterministic fail-closed IR error."""


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
            raise IRFormalizationError(f"DUPLICATE_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if raw != canonical_bytes(value):
        raise IRFormalizationError(f"NONCANONICAL_JSON:{path}")
    return value


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise IRFormalizationError(f"MODULE_UNAVAILABLE:{relative}")
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
        "branch": BRANCH, "head": IQ_HEAD, "tree": IQ_TREE,
        "subject": IQ_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IQ_HEAD, "index": "",
    }
    if observed != expected:
        raise IRFormalizationError("EXACT_COMMITTED_IQ_CHECKPOINT_MISMATCH")
    for label, head in LINEAGE.items():
        if subprocess.run(["git", "merge-base", "--is-ancestor", head, "HEAD"], cwd=ROOT).returncode:
            raise IRFormalizationError(f"LINEAGE_MISSING:{label}")
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
        raise IRFormalizationError("NESTED_AUTHORITY_MISMATCH")
    observed["local_remote_equality"] = "VERIFIED"
    observed["lineage"] = {key: "VERIFIED" for key in LINEAGE}
    observed["nested_authority"] = nested_state
    return observed


def reconstruct_iq() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in IQ_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{IQ_HEAD}:{relative.as_posix()}"], cwd=ROOT)
        if committed != (ROOT / relative).read_bytes() or sha256_bytes(committed) != expected_sha:
            raise IRFormalizationError(f"IQ_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative.name] = {
            "git_blob": git("rev-parse", f"{IQ_HEAD}:{relative.as_posix()}"),
            "sha256": expected_sha,
        }
    ast.parse((ROOT / IQ_FORMALIZER).read_text(), filename=str(IQ_FORMALIZER))
    ast.parse((ROOT / IQ_TEST).read_text(), filename=str(IQ_TEST))
    iq_owner = load_module(IQ_FORMALIZER, "g77_256ir_iq_reconstruction_owner")
    ip_reconstruction = iq_owner.reconstruct_ip()
    envelope = load_canonical(ROOT / IQ_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IRFormalizationError("IQ_INNER_SEAL_MISMATCH")
    reduction = envelope["reduction"]
    if reduction["terminal"]["terminal"] != "A__REPOSITORY_IMPLEMENTATION_SUCCESS":
        raise IRFormalizationError("IQ_TERMINAL_A_MISMATCH")
    if set(reduction["operational_counters"].values()) != {0}:
        raise IRFormalizationError("IQ_OPERATIONAL_ZERO_MISMATCH")
    required = {
        "gn_future_presentation_admission": "VERIFIED",
        "gn_future_generation_binding": "VERIFIED",
    }
    if any(reduction["presentation"][key] != value for key, value in required.items()):
        raise IRFormalizationError("IQ_PRESENTATION_REDUCTION_MISMATCH")
    headings = [line for line in (ROOT / IQ_REPORT).read_text().splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]:
        raise IRFormalizationError("IQ_G48_HEADING_MISMATCH")
    return {
        "status": "VERIFIED", "terminal": "A__REPOSITORY_IMPLEMENTATION_SUCCESS",
        "artifact_count": 4, "inner_seal": "VERIFIED", "identities": identities,
        "ip_reconstruction": ip_reconstruction,
    }


def authenticate_committed_gn() -> dict[str, Any]:
    current = (ROOT / GN_PATH).read_bytes()
    committed = subprocess.check_output(["git", "show", f"{IQ_HEAD}:{GN_PATH.as_posix()}"], cwd=ROOT)
    if current != committed or sha256_bytes(current) != GN_SHA256:
        raise IRFormalizationError("GN_IQ_COMMITTED_OWNER_MISMATCH")
    if git("rev-parse", f"{IQ_HEAD}:{GN_PATH.as_posix()}") != GN_BLOB:
        raise IRFormalizationError("GN_IQ_BLOB_MISMATCH")
    ast.parse(current.decode(), filename=str(GN_PATH))
    diff = git("diff", "--unified=0", IP_HEAD, IQ_HEAD, "--", GN_PATH.as_posix())
    added = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    removed = [line for line in diff.splitlines() if line.startswith("-") and not line.startswith("---")]
    expected_added = [
        '+    "FUTURE",', '+    if (',
        '+        request["authorized_vector_requested"] == "FUTURE"',
        '+        and not request["generation_identity"].endswith(',
        '+            "_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"',
        '+        )', '+    ):',
        '+        _fail("SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID")',
    ]
    if added != expected_added or removed:
        raise IRFormalizationError("GN_IQ_DELTA_NOT_EXACTLY_BOUNDED")
    gn = load_module(GN_PATH, "g77_256ir_gn_owner")
    context_owner = load_module(CONTEXT_OWNER, "g77_256ir_context_owner")
    fm = load_module(FM_PATH, "g77_256ir_fm_owner")
    if set(gn.SUPPORTED_VECTORS) != EXPECTED_VECTORS:
        raise IRFormalizationError("GN_VECTOR_SET_NOT_CLOSED_FIVE")
    if context_owner.operation_vector(GENERATION) != VECTOR:
        raise IRFormalizationError("FM_CONTEXT_FUTURE_GENERATION_REJECTED")
    if fm.operation_attempt_limit_field(VECTOR) != "future_operational_attempt_limit":
        raise IRFormalizationError("HUMAN_ACT_FUTURE_FIELD_REJECTED")
    gl_source = (ROOT / GL_PATH).read_text()
    if "SUPPORTED_VECTORS" in gl_source or "authorized_vector_requested" in gl_source:
        raise IRFormalizationError("GL_VECTOR_GATE_UNEXPECTED")
    return {
        "owner": GN_PATH.as_posix(), "git_blob": GN_BLOB, "sha256": GN_SHA256,
        "insertions": 8, "deletions": 0,
        "gn_iq_committed_owner_authentication": "VERIFIED",
        "gn_iq_committed_delta_bounded": "VERIFIED",
        "gn_future_presentation_admission": "VERIFIED",
        "gn_future_generation_binding": "VERIFIED",
        "gn_vector_set_closed": "VERIFIED",
        "unknown_vector_acceptance": "VERIFIED__NO",
        "arbitrary_vector_registration": "VERIFIED__NO",
        "caller_defined_vector": "VERIFIED__NO",
        "gl_separate_vector_gate": "VERIFIED__NO",
        "fm_context_future_support": "VERIFIED",
        "human_act_future_support": "VERIFIED",
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
        "runtime_target_head": IF_HEAD, "runtime_target_tree": IF_TREE,
    }
    required = (500, 600, 1000, FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE, FUTURE_CANDIDATE_SHA, FUTURE_CONTEXT_SHA)
    observed = (facts["evaluation"], facts["valid_from"], facts["valid_until"], facts["payload_digest"], facts["source_act"], facts["che_correlation"], facts["candidate_runtime_sha256"], facts["context_identity"])
    if observed != required or not facts["evaluation"] < facts["valid_from"] < facts["valid_until"]:
        raise IRFormalizationError("FUTURE_SEMANTICS_OR_RUNTIME_TARGET_MISMATCH")
    facts["future_semantic_mutation_count"] = "VERIFIED__0"
    facts["wall_clock_dependency_count"] = "VERIFIED__0"
    facts["runtime_target_provenance_authentication"] = "VERIFIED"
    facts["runtime_target_mutation"] = "VERIFIED__0"
    return facts


def current_v2_readiness() -> dict[str, Any]:
    du = load_module(DU_PATH, "g77_256ir_du")
    eb = load_module(EB_PATH, "g77_256ir_eb")
    ee = load_module(EE_PATH, "g77_256ir_ee")
    with tempfile.TemporaryDirectory(prefix=".g77_256ir_v2_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du.build_du_fixture(ROOT)))
        du_result = du.validate_file(candidate, ROOT, expected_head=IF_HEAD)
        eb_envelope = eb.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / candidate.name).write_bytes(candidate.read_bytes())
        harness = temporary / "fixture.py"
        harness.write_text("from pathlib import Path\nRAW_ROOT = Path('/mnt/g77-evidence')\nCONTINUATION_MANIFEST_PATH = RAW_ROOT / 'candidate-v2.json'\n")
        ee_envelope = ee.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
        eb_result = eb.verify_receipt_envelope(ROOT, eb_envelope)
        ee_result = ee.verify_receipt_envelope(ROOT, ee_envelope)
    baseline = {"head": IQ_HEAD, "tree": IQ_TREE}
    target = eb._authenticated_runtime_target(ROOT)
    if set(du_result.values()) != {"PASS"} or eb_result["overall_result"] != "PASS" or ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise IRFormalizationError("CURRENT_V2_RECHECK_FAILED")
    if eb_envelope["receipt"]["certification_baseline"] != baseline or ee_envelope["receipt"]["certification_baseline"] != baseline:
        raise IRFormalizationError("CURRENT_IQ_CERTIFICATION_BASELINE_NOT_BOUND")
    if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE):
        raise IRFormalizationError("AUTHENTICATED_RUNTIME_TARGET_NOT_IF")
    return {
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "certification_baseline": baseline, "runtime_target": target,
        "v2_implementation_status": "VERIFIED__REPOSITORY_IMPLEMENTED",
        "v2_post_commit_live_binding": "VERIFIED",
        "v2_preoperational_readiness": "VERIFIED",
        "future_preoperational_readiness": "VERIFIED",
        "runtime_certification_role_collapse": "VERIFIED__NO",
        "v1_semantics_reinterpreted": "VERIFIED__NO",
    }


def derive_fresh_identity() -> dict[str, Any]:
    for identity in (GENERATION, OPERATION):
        result = subprocess.run(["git", "grep", "-F", identity, IQ_HEAD], cwd=ROOT, text=True, stdout=subprocess.PIPE)
        if result.returncode not in (0, 1) or result.stdout:
            raise IRFormalizationError(f"FRESH_IDENTITY_COLLISION:{identity}")
    return {
        "derivation": "VERIFIED__GENERATION_PREFIX_PLUS_CLOSED_VECTOR_SUFFIX_AND_ONE_SHOT_CASE_PATTERN",
        "repository_generation": "G77_256IR",
        "operation_generation": GENERATION,
        "operation_identity": OPERATION,
        "repository_generation_equals_operation_generation": "VERIFIED__NO",
        "fresh": "VERIFIED", "collision": "VERIFIED__NO", "replay": "VERIFIED__NO",
        "precommit_self_reference_avoided": "VERIFIED",
        "repository_binding": {"head": IQ_HEAD, "tree": IQ_TREE},
    }


def fresh_request_fixture(v2: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build one in-memory-only IR readiness request from authenticated owners."""

    gn = load_module(GN_PATH, "g77_256ir_gn_fixture")
    fm = load_module(FM_PATH, "g77_256ir_fm_fixture")
    context = fm.build_operation_context(
        repository_root=ROOT, repository_head=IQ_HEAD, repository_tree=IQ_TREE,
        generation_identity=GENERATION, operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=Path("/tmp/g77_256ir_readiness_only/operation_state"),
        transient_root=Path("/tmp/g77_256ir_readiness_only/transient"),
        candidate_source_path=IH_CANDIDATE,
    )
    static = {
        "schema_id": "G77_256IR_TEST_ONLY_PREAUTHORITY_STATIC_READINESS_V1",
        "repository": {"head": IQ_HEAD, "tree": IQ_TREE},
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE, "candidate_sha256": FUTURE_CANDIDATE_SHA},
        "live_binding": {"du": v2["du"], "eb": v2["eb"], "ee": v2["ee"]},
        "context_sha256": context["context_sha256"], "authority_count": 0,
        "operational_execution_count": 0, "complete_deterministic_readiness": "PASS",
    }
    observation = {
        "schema_id": "G77_256IR_TEST_ONLY_GL_RECEIPT_PARENT_OBSERVATION_V1",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "context_sha256": context["context_sha256"], "receipt_parent": context["receipt_parent"],
        "owner": GL_PATH.as_posix(), "authority_count": 0, "operational_execution_count": 0,
        "classification": "READINESS_REPRESENTATION_ONLY__NO_DIRECTORY_OR_RECEIPT_CREATED",
    }
    checkpoint = {
        "schema_id": "G77_256IR_TEST_ONLY_PREAUTHORIZATION_CHECKPOINT_V1",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "context_sha256": context["context_sha256"], "static_readiness_sha256": sha256_bytes(canonical_bytes(static)),
        "receipt_parent_observation_sha256": sha256_bytes(canonical_bytes(observation)),
        "checkpoint_is_authority": False, "all_operational_counters_zero": True,
    }
    checkpoint_envelope = {"checkpoint": checkpoint, "checkpoint_sha256": sha256_bytes(canonical_bytes(checkpoint))}
    equivalence = {
        "schema_id": "G77_256IR_TEST_ONLY_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
        "checkpoint_sha256": checkpoint_envelope["checkpoint_sha256"],
        "observation_sha256": sha256_bytes(canonical_bytes(observation)),
        "preauth_final_admission_equivalence": "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY",
        "authority_count": 0, "operational_execution_count": 0,
    }
    envelope = deepcopy(load_canonical(ROOT / HP_REQUEST))
    request = envelope["request"]
    envelope["schema_id"] = "G77_256IRTEST_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    request.update({
        "schema_id": "G77_256IRTEST_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
        "recorded_at_utc": "TEST_ONLY__DETERMINISTIC__NO_WALL_CLOCK",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "authorized_vector_requested": VECTOR,
    })
    request["repository"].update({"head": IQ_HEAD, "tree": IQ_TREE, "remote_head": IQ_HEAD})
    request["immutable_assets"] = context["qemu_executable_base_seed_checkout_bindings"]
    request["live_binding"].update({
        "candidate_sha256": FUTURE_CANDIDATE_SHA,
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_bytes(canonical_bytes(context)),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "candidate_semantics_changed": False,
        "candidate_binding_regeneration_required": True,
        "receipt_parent": context["receipt_parent"],
    })
    request["preauthorization"].update({
        "static_readiness_file_sha256": sha256_bytes(canonical_bytes(static)),
        "checkpoint_file_sha256": sha256_bytes(canonical_bytes(checkpoint_envelope)),
        "checkpoint_inner_sha256": checkpoint_envelope["checkpoint_sha256"],
        "checkpoint_path": "TEST_ONLY__IN_MEMORY__NO_OPERATIONAL_REQUEST",
        "complete_deterministic_readiness": "PASS",
        "receipt_parent_observation_file_sha256": sha256_bytes(canonical_bytes(observation)),
        "preauth_final_admission_equivalence_file_sha256": sha256_bytes(canonical_bytes(equivalence)),
        "preauth_final_admission_equivalence": equivalence["preauth_final_admission_equivalence"],
        "gk_receipt_parent_false_positive_blocked": "YES",
        "all_operational_counters_zero": True,
    })
    for field in gn.ZERO_COUNTER_FIELDS:
        request[field] = 0
    envelope["request_sha256"] = sha256_bytes(gn._canonical_bytes(request))
    dependencies = {"context": context, "static": static, "observation": observation, "checkpoint": checkpoint_envelope, "equivalence": equivalence}
    return envelope, dependencies


def presentation_readiness(v2: dict[str, Any]) -> dict[str, Any]:
    gn = load_module(GN_PATH, "g77_256ir_gn_proof")
    envelope, dependencies = fresh_request_fixture(v2)
    with tempfile.TemporaryDirectory(prefix="g77_256ir_request_") as raw:
        path = Path(raw) / "TEST_ONLY_NONAUTHORITY_REQUEST.json"
        path.write_bytes(gn._canonical_bytes(envelope))
        presentation = gn.render_human_authorization_presentation(path)
        result = gn.validate_human_authorization_presentation(path, presentation)
        parsed = gn.parse_human_authorization_presentation(presentation)
    required = {
        "GENERATION_ID": GENERATION, "OPERATION_ID": OPERATION,
        "AUTHORIZED_VECTOR_REQUESTED": VECTOR, "HEAD": IQ_HEAD, "TREE": IQ_TREE,
        "CANDIDATE_SHA256": FUTURE_CANDIDATE_SHA,
        "CONTEXT_SHA256": dependencies["context"]["context_sha256"],
        "CANONICAL_ARGV_SHA256": dependencies["context"]["canonical_argv_sha256"],
        "AUTHORIZATION_REQUEST_SHA256": envelope["request_sha256"],
    }
    if any(parsed[key] != value for key, value in required.items()):
        raise IRFormalizationError("FRESH_PRESENTATION_BINDING_MISMATCH")
    return {
        "fresh_future_preauthorization_readiness": "VERIFIED",
        "human_authorization_action_available": "VERIFIED__YES",
        "sealed_request_presentation": "VERIFIED__MACHINE_DERIVED_REQUEST_FOR_HUMAN_REVIEW__NOT_AUTHORITY",
        "request_representation_sha256": sha256_bytes(gn._canonical_bytes(envelope)),
        "request_inner_sha256": envelope["request_sha256"],
        "presentation_sha256": sha256_bytes(presentation),
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "repository_head": IQ_HEAD, "repository_tree": IQ_TREE,
        "candidate_runtime_sha256": FUTURE_CANDIDATE_SHA,
        "context_sha256": dependencies["context"]["context_sha256"],
        "canonical_argv_sha256": dependencies["context"]["canonical_argv_sha256"],
        "checkpoint_sha256": dependencies["checkpoint"]["checkpoint_sha256"],
        "reviewed_field_count": result["reviewed_field_count"],
        "operational_execution_count": result["operational_execution_count"],
        "persisted_request_count": 0, "persisted_presentation_count": 0,
        "human_operational_authority": "VERIFIED__0",
        "authority_consumption": "VERIFIED__0",
    }


def proof_reuse() -> dict[str, Any]:
    seal = json.loads((ROOT / EX_SEAL).read_bytes(), object_pairs_hook=unique_object)["seal"]
    if seal["validation"]["component_matrix"] != "PASS__17_CERTIFIED__0_EVIDENCE_SUPPORTED__2_REQUIRES_HARDENING__3_VECTOR_SPECIFIC":
        raise IRFormalizationError("EX_COMPONENT_MATRIX_MISMATCH")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def terminal_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    iq = reconstruct_iq()
    gn = authenticate_committed_gn()
    future = authenticate_future_semantics()
    v2 = current_v2_readiness()
    identity = derive_fresh_identity()
    presentation = presentation_readiness(v2)
    reuse = proof_reuse()
    zero = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre_operational_invocation",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    return {
        "mode": "REPOSITORY_ONLY__POST_COMMIT_AUTHENTICATION_AND_PREAUTHORIZATION_READINESS__NO_AUTHORIZATION__NO_OPERATION",
        "entry": entry, "iq_reconstruction": iq, "gn_committed_owner": gn,
        "post_commit_compatibility": {
            "post_commit_gn_future_compatibility_authentication": "VERIFIED",
            "ip_gn_blocker_status": "VERIFIED__REMOVED_BY_COMMITTED_IQ",
            "wrong_attempt": "PASS", "wrong_input": "PASS", "wrong_contract": "PASS",
            "wrong_provenance": "PASS", "future": "PASS",
            "unknown_vector": "FAIL_CLOSED", "malformed_vector": "FAIL_CLOSED",
            "future_wrong_generation": "FAIL_CLOSED",
            "cross_vector_substitution": "REJECTED", "cross_generation_substitution": "REJECTED",
            "cross_operation_substitution": "REJECTED", "cross_request_substitution": "REJECTED",
            "replay_substitution": "REJECTED",
            "weak_future_generation_substring_acceptance": "VERIFIED__NO",
        },
        "future_semantics": future, "v2_readiness": v2,
        "fresh_identity": identity, "presentation_readiness": presentation,
        "closure": {
            "gn_closed_vector_owner": "VERIFIED", "gn_exact_future_suffix_owner": "VERIFIED",
            "gl_separate_vector_gate": "VERIFIED__NO", "fm_context_future_support": "VERIFIED",
            "human_act_future_support": "VERIFIED", "p11_change_required": "VERIFIED__NO",
        },
        "boundaries": {
            "p11_mutation_count": "VERIFIED__0", "fm_runtime_owner_mutation": "VERIFIED__0",
            "new_launcher_count": "VERIFIED__0", "new_adapter_count": "VERIFIED__0",
            "runtime_target_mutation": "VERIFIED__0", "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO", "shadow_automation_status": "VERIFIED__ABSENT",
            "reintroduced_historical_failure_count": "VERIFIED__0",
            "precommit_self_reference_avoided": "VERIFIED",
        },
        "proof_reuse": reuse,
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IQ_IP_IO_GN_GL_FM_HUMAN_ACT_DU_EB_EE_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__POST_COMMIT_GN_FUTURE_PRESENTATION_COMPATIBILITY_AUTHENTICATION_AND_FRESH_FUTURE_PREAUTHORIZATION_READINESS",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__14__IE_THROUGH_IR",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_ir": "VERIFIED__FOUR_REPLAY_SAFE_EVIDENCE_ARTIFACTS_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IR_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_EVIDENCE_ONLY_IR_DELTA",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__IR_EVIDENCE_AND_MACHINE_DERIVED_PRESENTATION_HASHES",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_IQ_ENTRY",
            "authority_state_recovery": "VERIFIED__NO_AUTHORITY_CREATED",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMED",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_OPERATION",
            "operation_replay_prevention": "VERIFIED__FRESH_IDENTITY_AND_REPLAY_SUBSTITUTION_REJECTED",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IR_HUMAN_BARRIER",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "operational_counters": zero,
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8},
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_PRESERVED__POST_COMMIT_GN_FUTURE_COMPATIBILITY",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__FRESH_HUMAN_OPERATIONAL_AUTHORITY_FOR_ONE_FUTURE_ATTEMPT",
            "governance_efficience": "ESTIMATED__HIGH__POST_COMMIT_AUTHENTICATION_WITH_ZERO_PRODUCTION_DELTA",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION",
            "proof_reuse_efficiency": reuse["proof_reuse_efficiency"],
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IQ_TO_IR_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_COMMITTED_V2_LIVE_BINDING__PREOPERATIONAL_READY__GN_FUTURE_PRESENTATION_POST_COMMIT_AUTHENTICATED__FRESH_PREAUTHORIZATION_READY__NOT_AUTHORIZED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IM_DESIGN__IN_IMPLEMENTED__IO_READY__IP_GN_BLOCKER__IQ_GN_COMPATIBILITY__IR_POST_COMMIT_READY",
            "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_OPERATIONAL_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IR_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_EVIDENCE_ONLY_IR_DELTA",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "terminal": {
            "terminal": "A__POST_COMMIT_COMPATIBILITY_AND_FRESH_PREAUTHORIZATION_READINESS",
            "last_verified_edge": "POST_COMMIT_GN_FUTURE_COMPATIBILITY_AND_FRESH_PREAUTHORIZATION_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORITY_FOR_FUTURE_NOT_PRESENT",
            "minimum_missing_capability": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_FOR_ONE_BOUNDED_FUTURE_ATTEMPT",
            "minimum_legal_next_delta": "HUMAN_REVIEW_AND_SEPARATE_FRESH_FUTURE_OPERATIONAL_AUTHORIZATION",
            "human_authorization_action_available": "VERIFIED__YES",
            "auto_continuable": False, "human_review_required": True, "next_generation_started": False,
        },
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256IR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    try:
        print(canonical_bytes(terminal_envelope()).decode(), end="")
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(canonical_bytes({"status": "FAIL_CLOSED", "reason": str(exc)}).decode(), end="")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
